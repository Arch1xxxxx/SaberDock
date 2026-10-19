import json,plistlib,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import integration as i
import backend as b

class DiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)/'AVPPlay';self.app=Path(self.temp.name)/'AVP Play.app';helper=self.app/'Contents/Helpers/avpplay';helper.parent.mkdir(parents=True);helper.write_text('fixture');self.store=Path(self.temp.name)/'External Downloads';self.store.mkdir();i.save(self.base/'settings.json',{'store':str(self.store)})
  self.chain=self.base/'toolchains/arbitrary-revision';(self.chain/'visionos').mkdir(parents=True);(self.chain/'visionos/gen_xcodeproj.py').write_text('fixture')
 def tearDown(self):self.temp.cleanup()
 def discover(self):return i.discover(self.base,self.app)
 def add_download(self,code):
  folder=self.store/f'beatsaber140-{code}';folder.mkdir();(folder/'beat-saber.apk').write_bytes(b'fixture');(folder/f'main.{code}.com.beatgames.beatsaber.obb').write_bytes(b'fixture')
 def test_external_store_and_latest_version_not_mixed(self):
  self.add_download(3237);env=self.discover();self.assertFalse(env['ready']);self.assertEqual(env['store'],str(self.store.resolve()));self.assertIn('1.40.8','\n'.join(env['issues']))
  self.add_download(1716);self.assertTrue(self.discover()['ready'])
 def test_other_version_build_never_reused(self):
  self.add_download(1716);tree=self.chain/'beatsaber140';tree.mkdir();(tree/'apktool.yml').write_text('versionInfo:\n  versionCode: 3237\n')
  app=self.chain/'visionos/build/dd-device-beatsaber140/Build/Products/Debug-xros/Klepton.app';app.mkdir(parents=True);(app/'Info.plist').write_bytes(plistlib.dumps({'KLObbFile':i.OBB_NAME,'KLTree':'beatsaber140'}))
  self.assertIsNone(self.discover()['matched']);(tree/'apktool.yml').write_text('versionInfo:\n  versionCode: 1716\n');self.assertIsNotNone(self.discover()['matched'])
 def test_team_from_local_job(self):
  i.save(self.base/'jobs/beatsaber140-fixture.json',{'updated':'2026-01-01','request':{'team':'ABCDE12345','toolchain':str(self.chain)}})
  self.assertEqual(self.discover()['team'],'ABCDE12345')
 def test_no_game_fetch_command(self):
  source=Path(i.__file__).read_text();self.assertNotIn("'fetch'",source);self.assertNotIn("'install',",source)

class InstallTests(unittest.TestCase):
 def test_build_error_never_installs(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(b,'SUPPORT',Path(folder)),patch.object(b,'TEAM','ABCDE12345'),patch.object(b,'build',side_effect=ValueError('Named broken song')),patch.object(b,'run') as run,patch.object(b,'devicectl') as dc:
   with self.assertRaisesRegex(ValueError,'Named broken song'):b.install(folder,'SaberDock','fixture-device')
   run.assert_not_called();dc.assert_not_called()
 def test_signing_error_never_installs(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(b,'SUPPORT',Path(folder)),patch.object(b,'TEAM','ABCDE12345'),patch.object(b,'build',return_value={}),patch.object(b,'sign_app',side_effect=ValueError('Signing failed')),patch.object(b,'run') as run,patch.object(b,'devicectl') as dc:
   with self.assertRaisesRegex(ValueError,'Signing failed'):b.install(folder,'SaberDock','fixture-device')
   run.assert_not_called();dc.assert_not_called()

if __name__=='__main__':unittest.main()

class FreshInstallFlowTests(unittest.TestCase):
 def test_fresh_install_stages_only_custom_bundle_and_verifies_size(self):
  with tempfile.TemporaryDirectory() as folder:
   base=Path(folder);tree=base/'tree';(tree/'assets').mkdir(parents=True);(tree/'apktool.yml').write_text('versionCode: 1716');(tree/'AndroidManifest.xml').write_text('fixture');apk=base/'game.apk';apk.write_bytes(b'fixture')
   source=base/'source.obb';source.write_bytes(b'source');events=[];bundle='io.saberdock.abcde12345.beatsaber140'
   def build(root,job):
    events.append('build');(job/i.OBB_NAME).write_bytes(b'custom');return {'resourceBytes':6,'resourceSha256':'fixture'}
   def sign(name,job):events.append('sign');return base/'Klepton.app'
   def device(args,*unused):
    events.append(list(args))
    if 'apps' in args:return {'result':{'apps':[]}}
    return {'result':{'files':[{'name':i.OBB_NAME,'metadata':{'size':6}}]}}
   with patch.multiple(b,SUPPORT=base/'support',TEAM='ABCDE12345',BUNDLE=bundle,SOURCE=source,ENVIRONMENT={'apk':str(apk)}),patch.object(b,'build',side_effect=build),patch.object(b,'sign_app',side_effect=sign),patch.object(b,'devicectl',side_effect=device),patch.object(b,'run',side_effect=lambda args,**kw:events.append([str(a) for a in args])),patch.object(b,'send_resource',side_effect=lambda *a:events.append('send')),patch.object(b,'scan',return_value={'playlists':[]}),patch.object(i,'prepare',return_value={'tree':str(tree)}):
    result=b.install(folder,'SaberDock','fixture-device')
    self.assertTrue(result['installed']);self.assertEqual(events[:2],['build','sign']);self.assertIn('send',events)
    mutations=[e for e in events if isinstance(e,list) and ('copy' in e or 'install' in e)]
    self.assertEqual(len(mutations),5)
    for event in mutations:
     if 'copy' in event:self.assertIn(bundle,event)
    self.assertEqual(i.read(base/'support/latest-success.json')['bundle'],bundle)
