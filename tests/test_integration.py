import argparse,hashlib,json,os,plistlib,shutil,sys,tempfile,unittest,zipfile
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
 def add_build(self,name,code):
  tree=self.chain/'beatsaber140';tree.mkdir(exist_ok=True);(tree/'assets').mkdir(exist_ok=True);(tree/'AndroidManifest.xml').write_text('<manifest/>');(tree/'apktool.yml').write_text(f"versionInfo:\n  versionName: '{name}'\n  versionCode: '{code}'\n")
  app=self.chain/'visionos/build/dd-device-beatsaber140/Build/Products/Debug-xros/Klepton.app';app.mkdir(parents=True,exist_ok=True)
  (app/'Info.plist').write_bytes(plistlib.dumps({'KLObbFile':f'main.{code}.com.beatgames.beatsaber.obb','KLTree':'beatsaber140','CFBundleExecutable':'Klepton'}));(app/'Klepton').write_bytes(b'fixture executable')
  return app
 def test_external_store_and_newer_game_not_mixed(self):
  self.add_download(3237);self.add_build('1.45.3_30054',3237)
  env=self.discover();self.assertTrue(env['ready'],env['issues']);self.assertEqual(env['store'],str(self.store.resolve()));self.assertEqual(env['version'],'1.45.3_30054')
 def test_accepts_different_versions_codes_and_build_suffixes(self):
  for name,code in [('1.40.8',1716),('1.40.8_99999',2789),('1.45.3_30054',4321),('9.99.0',9999)]:
   with self.subTest(name=name,code=code):
    self.add_download(code);self.add_build(name,code);env=self.discover()
    self.assertTrue(env['ready'],env['issues']);self.assertEqual(env['version'],name)
    self.assertEqual(env['versionCode'],code);self.assertEqual(env['obbName'],f'main.{code}.com.beatgames.beatsaber.obb')
    self.assertEqual(Path(env['apk']).parent.name,f'beatsaber140-{code}')
 def test_any_version_name_or_missing_version_is_accepted(self):
  self.add_download(1716)
  for name in ['1.45.3_30054','1.40.80','1.40.8.1','']:
   self.add_build(name,1716);self.assertTrue(self.discover()['ready'])
 def test_missing_executable_or_matching_download_is_not_ready(self):
  self.add_download(1716);app=self.add_build('1.40.8_12345',2789)
  self.assertFalse(self.discover()['ready'])
  self.add_download(2789);self.assertTrue(self.discover()['ready'])
  (app/'Klepton').unlink();self.assertFalse(self.discover()['ready'])
 def test_team_from_local_job(self):
  i.save(self.base/'jobs/beatsaber140-fixture.json',{'updated':'2026-01-01','request':{'team':'ABCDE12345','toolchain':str(self.chain)}})
  self.assertEqual(self.discover()['team'],'ABCDE12345')
 def test_no_game_fetch_or_translation_command(self):
  source=Path(i.__file__).read_text()
  for forbidden in ["'fetch'","'install',",'mkguest.sh','mkangle.sh','mkmvk.sh','Klepton.xcodeproj']:
   self.assertNotIn(forbidden,source)

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
    events.append('build');(job/'main.2789.com.beatgames.beatsaber.obb').write_bytes(b'custom');return {'resourceBytes':6,'resourceSha256':'fixture'}
   def sign(name,job):events.append('sign');return base/'Klepton.app'
   def device(args,*unused):
    events.append(list(args))
    if 'apps' in args:return {'result':{'apps':[]}}
    return {'result':{'files':[{'name':'main.2789.com.beatgames.beatsaber.obb','metadata':{'size':6}}]}}
   with patch.multiple(b,SUPPORT=base/'support',TEAM='ABCDE12345',BUNDLE=bundle,SOURCE=source,ENVIRONMENT={'apk':str(apk),'obbName':'main.2789.com.beatgames.beatsaber.obb'}),patch.object(b,'build',side_effect=build),patch.object(b,'sign_app',side_effect=sign),patch.object(b,'devicectl',side_effect=device),patch.object(b,'run',side_effect=lambda args,**kw:events.append([str(a) for a in args])),patch.object(b,'send_resource',side_effect=lambda *a:events.append('send')),patch.object(b,'scan',return_value={'playlists':[]}),patch.object(i,'prepare',return_value={'tree':str(tree)}):
    result=b.install(folder,'SaberDock','fixture-device')
    self.assertTrue(result['installed']);self.assertEqual(events[:2],['build','sign']);self.assertIn('send',events)
    mutations=[e for e in events if isinstance(e,list) and ('copy' in e or 'install' in e)]
    self.assertEqual(len(mutations),5)
    for event in mutations:
     if 'copy' in event:self.assertIn(bundle,event)
    self.assertEqual(i.read(base/'support/latest-success.json')['bundle'],bundle)

class SigningTests(unittest.TestCase):
 def fixture(self,root):
  app=root/'App.app';app.mkdir();(app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'App'}))
  (app/'App').write_bytes(b'\xcf\xfa\xed\xfeMAIN')
  (app/'App.debug.dylib').write_bytes(b'\xcf\xfa\xed\xfeDEBUG')
  (app/'__preview.dylib').write_bytes(b'\xca\xfe\xba\xbePREVIEW')
  framework=app/'Frameworks/Guest.framework';framework.mkdir(parents=True);(framework/'Guest').write_bytes(b'\xcf\xfa\xed\xfeGUEST')
  (app/'resource.txt').write_text('fixture');return app,framework
 def test_debug_preview_and_framework_are_signed_and_explicitly_verified(self):
  with tempfile.TemporaryDirectory() as folder:
   app,framework=self.fixture(Path(folder));calls=[]
   i.sign_application(app,'IDENTITY',Path(folder)/'sign.entitlements',lambda args:calls.append([str(v) for v in args]))
   signed=[Path(c[-1]) for c in calls if '--force' in c];verified=[Path(c[-1]) for c in calls if '--verify' in c]
   for name in ['App.debug.dylib','__preview.dylib']:
    self.assertIn(app/name,signed);self.assertIn(app/name,verified);self.assertLess(signed.index(app/name),signed.index(app))
   self.assertIn(framework/'Guest',signed);self.assertLess(signed.index(framework/'Guest'),signed.index(framework));self.assertEqual(signed[-1],app)
   self.assertNotIn(app/'resource.txt',signed)
 def test_embedded_library_verification_failure_aborts_signing(self):
  with tempfile.TemporaryDirectory() as folder:
   app,_=self.fixture(Path(folder))
   def run(args):
    if '--verify' in args and Path(args[-1]).name=='App.debug.dylib':raise RuntimeError('missing code signature')
   with self.assertRaisesRegex(RuntimeError,'missing code signature'):i.sign_application(app,'IDENTITY',Path(folder)/'sign.entitlements',run)


class RuntimeReuseTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
  self.tree=self.base/'AVPPlay/beatsaber140';self.tree.mkdir(parents=True);(self.tree/'apktool.yml').write_text('versionCode: 2789\nversionName: 1.40.8_12345\n');(self.tree/'assets').mkdir();(self.tree/'AndroidManifest.xml').write_text('<manifest/>')
  self.app=self.base/'AVPPlay/Klepton.app';self.app.mkdir()
  (self.app/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'Klepton','KLObbFile':'main.2789.com.beatgames.beatsaber.obb','KLTree':'beatsaber140'}))
  (self.app/'Klepton').write_bytes(b'fixture translated executable')
  self.apk=self.base/'game.apk';self.obb=self.base/'game.obb'
  for path,entries in [(self.apk,['AndroidManifest.xml','lib/arm64-v8a/libil2cpp.so']),(self.obb,['assets/BeatmapLevelsData/fitbeat','assets/aa/catalog.json'])]:
   with zipfile.ZipFile(path,'w') as archive:
    for name in entries:archive.writestr(name,b'fixture')
  self.support=self.base/'support'
  self.env={'ready':True,'issues':[],'apk':str(self.apk),'sourceObb':str(self.obb),'obbName':'main.2789.com.beatgames.beatsaber.obb','avpApp':str(self.base/'AVP Play.app'),'store':str(self.base),'toolchains':[str(self.tree.parent)],'matched':{'app':str(self.app),'tree':str(self.tree)}}
  self.calls=[]
 def tearDown(self):self.temp.cleanup()
 def command(self,args,**kwargs):
  args=[str(a) for a in args];self.calls.append(args)
  if args[0]=='/usr/bin/ditto':shutil.copytree(args[1],args[2])
  else:raise AssertionError('Unexpected external operation: '+repr(args))
 def prepare(self):
  return i.prepare(self.env,self.support,self.base/'resources','ABCDE12345','io.fixture',lambda message:None)
 def test_only_existing_app_is_copied_and_cached(self):
  with patch.object(i,'command',side_effect=self.command):
   result=self.prepare()
   self.assertEqual((Path(result['app'])/'Klepton').read_bytes(),(self.app/'Klepton').read_bytes())
   self.assertEqual(len(self.calls),1);self.assertEqual(self.calls[-1][0],'/usr/bin/ditto')
   self.assertEqual(self.prepare(),result);self.assertEqual(len(self.calls),1)
 def test_missing_match_stops_before_commands_even_with_legacy_cache(self):
  legacy_id=hashlib.sha256((str(self.apk)+hashlib.sha256(self.apk.read_bytes()).hexdigest()+str(self.env['toolchains'])+'io.fixture').encode()).hexdigest()[:24]
  i.save(self.support/'runtime-prepared'/legacy_id/'runtime.json',{'app':str(self.app),'tree':str(self.tree),'versionCode':1716})
  self.env['matched']=None
  for language,phrase in [('en','Select the game visionOS app'),('zh-Hans','请选择 AVP Play 已生成')]:
   with patch.dict(os.environ,{'SABERDOCK_LANGUAGE':language}),patch.object(i,'command') as command:
    with self.assertRaisesRegex(ValueError,phrase):self.prepare()
    command.assert_not_called()
 def test_source_deleted_after_discovery_cannot_be_replaced_by_cache(self):
  with patch.object(i,'command',side_effect=self.command):
   self.prepare();self.calls.clear();(self.app/'Klepton').unlink()
   with self.assertRaisesRegex(ValueError,'AVP Play'):self.prepare()
   self.assertEqual(self.calls,[])
 def test_cache_without_reuse_provenance_is_not_trusted(self):
  with patch.object(i,'command',side_effect=self.command):
   result=self.prepare();manifest=Path(result['app']).parent/'runtime.json'
   data=i.read(manifest);data.pop('sourceBuild');i.save(manifest,data)
   (Path(result['app'])/'Klepton').write_bytes(b'old fallback executable')
   self.calls.clear();result=self.prepare()
   self.assertEqual((Path(result['app'])/'Klepton').read_bytes(),(self.app/'Klepton').read_bytes())
   self.assertEqual(len(self.calls),1)


 def test_missing_or_newer_version_metadata_does_not_block_reuse(self):
  with patch.object(i,'command',side_effect=self.command):
   (self.tree/'apktool.yml').write_text('versionName: 1.45.3_30054\nversionCode: 3237\n')
   self.assertEqual(self.prepare()['versionName'],'1.45.3_30054')
   (self.tree/'apktool.yml').unlink()
   self.assertTrue(self.prepare()['app'])

class DeploymentFileNamesTests(unittest.TestCase):
 def test_resource_copy_uses_discovered_obb_name(self):
  name='main.4321.com.beatgames.beatsaber.obb'
  with patch.object(b,'run') as run,patch.object(b,'ENVIRONMENT',{'obbName':name}):
   b.send_resource('fixture-device',Path('/tmp')/name)
   self.assertIn('Documents/android-files/obb/'+name,run.call_args.args[0])
 def test_app_configuration_uses_discovered_obb_name(self):
  with tempfile.TemporaryDirectory() as folder:
   base=Path(folder);source=base/'Source.app';source.mkdir();(source/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'Klepton'}))
   profile=base/'profile';profile.write_bytes(b'fixture');job=base/'job';job.mkdir()
   def copy(args,**kw):
    if args[0]=='/usr/bin/ditto':shutil.copytree(args[1],args[2])
   with patch.object(b,'ENVIRONMENT',{'obbName':'main.4321.com.beatgames.beatsaber.obb'}),patch.object(i,'prepare',return_value={'app':str(source)}),patch.object(i,'provisioning',return_value=({'Entitlements':{}},'identity',profile)),patch.object(i,'sign_application',side_effect=lambda app,*args:app),patch.object(b,'run',side_effect=copy):
    result=b.sign_app('SaberDock',job)
   self.assertEqual(plistlib.loads((result/'Info.plist').read_bytes())['KLObbFile'],'main.4321.com.beatgames.beatsaber.obb')



class ManualSelectionTests(unittest.TestCase):
 setUp=RuntimeReuseTests.setUp
 tearDown=RuntimeReuseTests.tearDown
 def selected(self):
  return i.discover(self.base/'missing-data',store=self.base/'missing-store',
                    runtime_app=self.app,apk=self.apk,obb=self.obb,tree=self.tree)
 def test_files_outside_avp_play_are_accepted_without_metadata(self):
  (self.tree/'apktool.yml').unlink()
  env=self.selected()
  self.assertTrue(env['ready'],env['issues']);self.assertEqual(env['sourceObb'],str(self.obb))
  self.assertEqual(env['obbName'],'game.obb');self.assertEqual(env['version'],'')
  i.validate_source(env)
 def test_manual_selection_overrides_discovery_and_survives_configure(self):
  args=argparse.Namespace(action='configure',avp_root=str(self.base/'missing-data'),avp_app=None,store=str(self.base/'missing-store'),team='ABCDE12345',runtime_app=str(self.app),apk=str(self.apk),obb=str(self.obb),game_tree=str(self.tree))
  with patch.multiple(b,SUPPORT=self.support,ENVIRONMENT={},TEAM='',BUNDLE='',SOURCE=Path('/nonexistent')):
   env=b.configure(args);self.assertTrue(env['ready'],env['issues'])
   saved=i.read(self.support/'settings.json')
   self.assertEqual(saved['runtimeApp'],str(self.app));self.assertEqual(saved['sourceObb'],str(self.obb))
   for key in ['avp_root','avp_app','store','team','runtime_app','apk','obb','game_tree']:setattr(args,key,None)
   args.action='environment';again=b.configure(args)
   self.assertTrue(again['ready']);self.assertEqual(again['apk'],str(self.apk))
 def test_invalid_explicit_app_never_silently_uses_another_build(self):
  env=i.discover(self.base,runtime_app=self.base/'not-an-app',apk=self.apk,obb=self.obb,tree=self.tree)
  self.assertFalse(env['ready']);self.assertIn('Select the game visionOS app','\n'.join(env['issues']))
 def test_resource_format_error_does_not_install_anything(self):
  env=self.selected()
  with zipfile.ZipFile(self.obb,'w') as z:z.writestr('unrelated',b'fixture')
  with patch.multiple(b,SUPPORT=self.support,ENVIRONMENT=env,TEAM='ABCDE12345',SOURCE=self.obb),patch.object(b,'run') as run,patch.object(b,'devicectl') as dc:
   with self.assertRaisesRegex(ValueError,'resource structure'):b.install(self.base,'SaberDock','fixture-device')
   run.assert_not_called();dc.assert_not_called()

class SourceChangeTests(unittest.TestCase):
 def test_changed_file_selection_uses_complete_install(self):
  with tempfile.TemporaryDirectory() as folder,patch.multiple(b,SUPPORT=Path(folder),ENVIRONMENT={}),patch.object(b,'install',return_value={'installed':True}) as install,patch.object(b,'preflight') as preflight:
   self.assertTrue(b.update(folder,'SaberDock','fixture-device')['installed'])
   install.assert_called_once_with(folder,'SaberDock','fixture-device');preflight.assert_not_called()
