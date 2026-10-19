import base64,importlib,io,json,os,struct,sys,tempfile,unittest,wave,zipfile,zlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import backend as b

def make_map(folder,title='Synthetic fixture'):
 folder.mkdir(parents=True,exist_ok=True)
 info={'_version':'2.1.0','_songName':title,'_songSubName':'','_songAuthorName':'Fixture','_levelAuthorName':'Fixture','_beatsPerMinute':120,'_songFilename':'song.wav','_coverImageFilename':'cover.png','_previewStartTime':0,'_previewDuration':.2,'_environmentName':'DefaultEnvironment','_environmentNames':[],'_difficultyBeatmapSets':[{'_beatmapCharacteristicName':'Standard','_difficultyBeatmaps':[{'_difficulty':'Expert','_difficultyRank':7,'_beatmapFilename':'Expert.dat','_noteJumpMovementSpeed':10,'_noteJumpStartBeatOffset':0}]}]}
 (folder/'Info.dat').write_text(json.dumps(info));(folder/'Expert.dat').write_text(json.dumps({'_version':'2.0.0','_notes':[{'_time':.1,'_lineIndex':1,'_lineLayer':0,'_type':0,'_cutDirection':1}],'_obstacles':[],'_events':[]}))
 with wave.open(str(folder/'song.wav'),'wb') as audio:audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(44100);audio.writeframes(b'\0\0'*44100)
 def chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data))
 (folder/'cover.png').write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\x22\x88\xbb'))+chunk(b'IEND',b''))
 return folder

class LibraryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'library';self.group=self.root/'Pop';self.old=b.SUPPORT;b.SUPPORT=Path(self.temp.name)/'support';b.SUPPORT.mkdir()
 def tearDown(self):b.SUPPORT=self.old;self.temp.cleanup()
 def songs(self):return b.scan(self.root)['playlists'][0]['songs']
 def test_order_delete_restore_and_append(self):
  make_map(self.group/'A','A');make_map(self.group/'B','B');ids=[s['id'] for s in self.songs()]
  b.manage(self.root,'Pop','order',ids[::-1]);make_map(self.group/'C','C')
  self.assertEqual([s['title'] for s in self.songs()],['B','A','C'])
  b.manage(self.root,'Pop','delete',[ids[1]]);self.assertFalse((self.group/'B').exists());b.manage(self.root,'','restore',[])
  self.assertEqual([s['title'] for s in self.songs()],['B','A','C'])
 def test_delete_from_multi_map_zip(self):
  maps=Path(self.temp.name)/'maps';make_map(maps/'A','A');make_map(maps/'B','B');self.group.mkdir(parents=True)
  with zipfile.ZipFile(self.group/'maps.ZIP','w') as z:
   for p in maps.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(maps))
  songs=self.songs();b.manage(self.root,'Pop','delete',[songs[0]['id']]);self.assertTrue((self.group/'maps.ZIP').exists());self.assertEqual(len(self.songs()),1)
  b.manage(self.root,'','restore',[]);self.assertEqual(len(self.songs()),2)
 def test_single_zip_restore(self):
  folder=make_map(Path(self.temp.name)/'map');self.group.mkdir(parents=True)
  with zipfile.ZipFile(self.group/'one.zip','w') as z:
   for p in folder.iterdir():z.write(p,p.name)
  b.manage(self.root,'Pop','delete',[self.songs()[0]['id']]);self.assertFalse((self.group/'one.zip').exists());b.manage(self.root,'','restore',[]);self.assertEqual(len(self.songs()),1)
 def test_unchanged_scan_and_cover_only_edit(self):
  folder=make_map(self.group/'A','A');before=self.songs()[0]
  with patch.object(b,'fingerprint',side_effect=AssertionError('unchanged song should be cached')):self.assertEqual(self.songs()[0]['id'],before['id'])
  (folder/'cover.png').write_bytes((folder/'cover.png').read_bytes()+b'\0')
  after=self.songs()[0];self.assertEqual(after['id'],before['id']);self.assertNotEqual(after['contentKey'],before['contentKey'])
 def test_missing_audio_names_song(self):
  folder=make_map(self.group/'A','Named broken song');(folder/'song.wav').unlink();self.assertIn('Named broken song','\n'.join(b.scan(self.root)['errors']))
 def test_unsafe_zip(self):
  self.group.mkdir(parents=True)
  with zipfile.ZipFile(self.group/'bad.zip','w') as z:z.writestr('../outside','bad')
  self.assertTrue(b.scan(self.root)['errors']);self.assertFalse((Path(self.temp.name)/'outside').exists())
 def test_stale_sort_rejected(self):
  make_map(self.group/'A');
  with self.assertRaises(ValueError):b.manage(self.root,'Pop','order',[])

if __name__=='__main__':unittest.main()
