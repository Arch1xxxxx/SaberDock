from i18n import tr
#!/usr/bin/env python3
import uuid
import integration
import argparse,contextlib,datetime,hashlib,json,os,plistlib,re,shutil,subprocess,sys,tempfile,time,traceback,zipfile,fcntl
from pathlib import Path
RES=Path(__file__).resolve().parent
SUPPORT=Path(os.environ.get('SABER_LIBRARY_SUPPORT',str(Path.home()/'Library/Application Support/SaberDock')))
BUNDLE='io.saberdock.beatsaber140'
ENVIRONMENT={};TEAM='';DEVICE=''
SOURCE=Path('/nonexistent')
PRIORITY=['ostvol1','ostvol2','ostvol3','ostvol4','ostvol5','ostvol6','ostvol7','extras','camellia']
def emit(event,**data):print(json.dumps({'event':event,**data},ensure_ascii=False),flush=True)
def note(s):emit('progress',message=s)
def atomic(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);p=path.with_name(path.name+'.new');p.write_text(json.dumps(data,ensure_ascii=False,indent=2));p.replace(path)
def read_json(p,default=None):
 try:return json.loads(Path(p).read_text(encoding='utf-8-sig'))
 except FileNotFoundError:return default

def local(folder,name):
 p=(folder/name).resolve()
 if not p.is_relative_to(folder.resolve()):raise ValueError(tr('谱面引用了文件夹之外的文件'))
 return p

def info_files(folder):
 return sorted((p for p in folder.rglob('*') if p.is_file() and p.name.lower()=='info.dat' and not any(v.startswith('.') or v=='__MACOSX' for v in p.relative_to(folder).parts)),key=str)
def unzip_safe(file,target):
 with zipfile.ZipFile(file) as z:
  if len(z.infolist())>10000 or sum(i.file_size for i in z.infolist())>5*1024**3:raise ValueError(tr('谱面 ZIP 太大或文件数量过多'))
  for i in z.infolist():
   p=(target/i.filename).resolve()
   if not p.is_relative_to(target.resolve()) or ((i.external_attr>>16)&0o170000)==0o120000:raise ValueError(tr('ZIP 含有不安全的路径或符号链接'))
  z.extractall(target)

def fingerprint(folder,info,raw,cache):
 if '_songFilename' in info:
  names=[info['_songFilename'],info.get('_coverImageFilename','')]+[m['_beatmapFilename'] for s in info.get('_difficultyBeatmapSets',[]) for m in s.get('_difficultyBeatmaps',[])]
 else:
  names=[info.get('coverImageFilename',''),info['audio']['songFilename'],info['audio'].get('audioDataFilename','')]+[m.get('beatmapDataFilename','') for m in info.get('difficultyBeatmaps',[])]+[m.get('lightshowDataFilename','') for m in info.get('difficultyBeatmaps',[])]
 h=hashlib.sha256(raw)
 for name in sorted(set(filter(None,names))):
  p=local(folder,name);st=p.stat();key=str(p);stamp=[st.st_size,st.st_mtime_ns];entry=cache.get(key)
  if entry and entry['stamp']==stamp:digest=entry['hash']
  else:digest=hashlib.sha256(p.read_bytes()).hexdigest();cache[key]={'stamp':stamp,'hash':digest}
  h.update(name.encode());h.update(digest.encode())
 return h.hexdigest()

def state_file(root):return Path(root)/'.beatsaber-library.json'
def library_state(root):return read_json(state_file(root),{'orders':{},'deleted':{},'history':[]})
def manage(root,category,action,ids):
 root=Path(root).expanduser().resolve();library=scan(root);state=library_state(root)
 group=next((g for g in library['playlists'] if g['name']==category),None)
 if not group and action!='restore':raise ValueError(tr('找不到所选曲包，请刷新后重试'))
 songs=group['songs'] if group else [];lookup={s['id']:s for s in songs}
 if action=='order':
  if len(ids)!=len(set(ids)) or set(ids)!=set(lookup):raise ValueError(tr('曲库刚刚发生变化，请刷新后重新排序'))
  state.setdefault('orders',{})[category]=ids
 elif action=='delete':
  if len(ids)!=1 or ids[0] not in lookup:raise ValueError(tr('所选歌曲已发生变化，请刷新后重试'))
  song=lookup[ids[0]];source=Path(song['sourcePath']);group_path=Path(group['path']).resolve()
  if not source.resolve().is_relative_to(group_path):raise ValueError(tr('不能删除曲库以外的源文件'))
  moved=False;target=None
  # A ZIP containing several maps stays intact; only this map is excluded.
  movable=(source.suffix.lower()=='.zip' and len(info_files(Path(song['archiveRoot'])))==1) if song.get('archiveRoot') else (source!=group_path and len(info_files(source))==1 and not any(p.suffix.lower()=='.zip' for p in source.rglob('*')))
  record={'category':category,'id':song['id'],'title':song['title'],'source':str(source),'moved':False}
  if movable:
   target=root/'.library-trash'/uuid.uuid4().hex/source.name;target.parent.mkdir(parents=True);shutil.move(str(source),target);record.update(moved=True,trash=str(target))
  state.setdefault('deleted',{}).setdefault(category,[]).append(song['id']);state.setdefault('history',[]).append(record)
  try:atomic(state_file(root),state)
  except Exception:
   if target:shutil.move(str(target),source)
   raise
  return scan(root)
 elif action=='restore':
  history=state.setdefault('history',[])
  if not history:raise ValueError(tr('没有可以恢复的歌曲'))
  record=history[-1]
  if record['moved']:
   source=Path(record['source']);target=Path(record['trash'])
   if not source.is_relative_to(root) or not any(target.is_relative_to(root/name) for name in ['.library-trash','.曲库回收站']):raise ValueError(tr('回收站记录路径无效'))
   if source.exists():raise ValueError(tr('原位置已有同名文件，请先在访达中改名后再恢复'))
   source.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(target),source)
  history.pop();deleted=state.setdefault('deleted',{}).setdefault(record['category'],[])
  if record['id'] in deleted:deleted.remove(record['id'])
 else:raise ValueError(tr('未知的管理操作'))
 atomic(state_file(root),state);return scan(root)

def folder_stamp(folder):
 return [[str(p.relative_to(folder)),p.stat().st_size,p.stat().st_mtime_ns] for p in sorted(folder.rglob('*')) if p.is_file() and not any(v.startswith('.') for v in p.relative_to(folder).parts)]

def scan(root):
 root=Path(root).expanduser().resolve();root.mkdir(parents=True,exist_ok=True);cache=read_json(SUPPORT/'scan-cache.json',{});registry=read_json(SUPPORT/'song-ids.json',{});groups=[];errors=[];state=library_state(root)
 for group in sorted((p for p in root.iterdir() if p.is_dir() and not p.name.startswith('.')),key=lambda p:p.name.casefold()):
  songs=[];sources=[(p,p.parent,None) for p in info_files(group)]
  for file in sorted(p for p in group.rglob('*') if p.is_file() and p.suffix.lower()=='.zip'):
   if any(v.startswith('.') or v=='__MACOSX' for v in file.relative_to(group).parts):continue
   st=file.stat();key=str(file);entry=cache.get(key);stamp=[st.st_size,st.st_mtime_ns]
   if entry and entry['stamp']==stamp:dig=entry['hash']
   else:dig=hashlib.sha256(file.read_bytes()).hexdigest();cache[key]={'stamp':stamp,'hash':dig}
   target=SUPPORT/'imports'/dig
   try:
    if not (target/'.complete').exists():
     tmp=target.with_name(dig+'.extracting');shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir(parents=True);unzip_safe(file,tmp);(tmp/'.complete').touch();target.parent.mkdir(parents=True,exist_ok=True);shutil.rmtree(target,ignore_errors=True);tmp.replace(target)
    sources.extend((p,file,target) for p in info_files(target))
   except Exception as e:errors.append(f'{group.name}/{file.name}：{e}')
  seen=set()
  for p,source,archive_root in sources:
   title=p.parent.name
   try:
    record_key='song:'+os.environ.get('SABERDOCK_LANGUAGE','en')+':'+str(p);stamp=folder_stamp(p.parent);record=cache.get(record_key)
    if record and record.get('stamp')==stamp:
     song=dict(record['song']);song.update(sourcePath=str(source),archiveRoot=str(archive_root) if archive_root else None)
     if song['id'] not in seen and song['id'] not in state.get('deleted',{}).get(group.name,[]):songs.append(song);seen.add(song['id'])
     continue
    raw=p.read_bytes();info=json.loads(raw.decode('utf-8-sig'));folder=p.parent
    if '_songName' in info:
     title=info['_songName'];artist=info.get('_songAuthorName','');mapper=info.get('_levelAuthorName','');cover=info.get('_coverImageFilename','');std=next((s['_difficultyBeatmaps'] for s in info['_difficultyBeatmapSets'] if s['_beatmapCharacteristicName']=='Standard'),[]);diffs=[d['_difficulty'] for d in std];req=[r for d in std for r in d.get('_customData',{}).get('_requirements',[])];suggestions=[r for d in std for r in d.get('_customData',{}).get('_suggestions',[])]
    else:
     title=info['song']['title'];artist=info['song'].get('author','');cover=info['coverImageFilename'];std=[s for s in info.get('difficultyBeatmaps',[]) if s.get('characteristic')=='Standard'];diffs=[s['difficulty'] for s in std];mapper=', '.join(sorted({v for s in std for v in s.get('beatmapAuthors',{}).get('mappers',[])}));req=[r for s in std for r in s.get('customData',{}).get('requirements',[])];suggestions=[]
    if not std:raise ValueError(tr('没有 Standard 标准双剑难度'))
    if req:raise ValueError(tr('需要 Quest 插件：')+', '.join(sorted(set(req))))
    coverpath=local(folder,cover)
    if not coverpath.is_file():raise ValueError(tr('缺少封面图片'))
    legacy_info=dict(info)
    if '_songName' in info:legacy_info['_coverImageFilename']=''
    else:legacy_info['coverImageFilename']=''
    ident=fingerprint(folder,legacy_info,raw,cache);content=fingerprint(folder,info,raw,cache)
    if ident in seen or ident in state.get('deleted',{}).get(group.name,[]):continue
    seen.add(ident)
    level=registry.get(ident) or 'SaberCustom'+ident[:20];registry[ident]=level
    songs.append({'id':ident,'contentKey':content,'levelId':level,'title':title,'artist':artist,'mapper':mapper,'difficulties':diffs,'folder':str(folder),'infoPath':str(p),'cover':str(coverpath),'sourcePath':str(source),'archiveRoot':str(archive_root) if archive_root else None,'warnings':[tr('可选插件效果不会导入：')+', '.join(sorted(set(suggestions)))] if suggestions else []});cache[record_key]={'stamp':stamp,'song':songs[-1]}
   except Exception as e:errors.append(f'{group.name} / {title}：{e}')
  order=state.get('orders',{}).get(group.name,[]);positions={v:i for i,v in enumerate(order)}
  songs.sort(key=lambda s:(positions.get(s['id'],len(order)),s['title'].casefold(),s['mapper'].casefold()));groups.append({'name':group.name,'path':str(group),'songs':songs,'count':len(songs)})
 atomic(SUPPORT/'scan-cache.json',cache);atomic(SUPPORT/'song-ids.json',registry)
 return {'root':str(root),'playlists':groups,'songCount':sum(len(g['songs']) for g in groups),'uniqueSongs':len({s['id'] for g in groups for s in g['songs']}),'errors':errors,'canRestore':bool(state.get('history'))}

def safe_name(s):
 name=s.strip()
 if not name or name in ['.','..'] or '/' in name or '\0' in name:raise ValueError(tr('请输入有效的文件夹名称'))
 return name

def init(root):
 root=Path(root).expanduser();root.mkdir(parents=True,exist_ok=True)
 if not any(root.iterdir()):
  for name in ['Vol.1','Vol.2']:(root/name).mkdir(exist_ok=True)
 return scan(root)

def import_paths(root,category,paths):
 root=Path(root).expanduser();root.mkdir(parents=True,exist_ok=True)
 for raw in paths:
  src=Path(raw).resolve()
  if src.is_relative_to(root.resolve()):continue
  if src.is_dir() and not info_files(src) and not any(p.suffix.lower()=='.zip' for p in src.rglob('*')):raise ValueError(tr('该文件夹内没有找到谱面或 ZIP'))
  if src.is_dir() and not any(p.name.lower()=='info.dat' for p in src.iterdir()):
   dst=root/safe_name(src.name)
  else:
   if not category:raise ValueError(tr('请先选择一个曲包，或先创建新曲包'))
   target=root/safe_name(category);target.mkdir(exist_ok=True);dst=target/src.name
  if dst.exists():
   idx=2
   while dst.with_name(src.stem+f' ({idx})'+src.suffix).exists():idx+=1
   dst=dst.with_name(src.stem+f' ({idx})'+src.suffix)
  if src.is_dir():
   if any(p.is_symlink() for p in src.rglob('*')):raise ValueError(tr('谱面文件夹不能包含符号链接'))
   shutil.copytree(src,dst)
  elif src.suffix.lower()=='.zip':shutil.copy2(src,dst)
  else:raise ValueError(tr('请拖入谱面 ZIP 或已解压的文件夹'))
 return scan(root)

def run(cmd,timeout=60,**kwargs):
 p=subprocess.run([str(c) for c in cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout,**kwargs)
 if p.returncode:raise RuntimeError(p.stdout.strip()[-2400:] or tr('操作失败'))
 return p.stdout

def devicectl(args,timeout=45):
 with tempfile.TemporaryDirectory(prefix='device-',dir=SUPPORT) as td:
  file=Path(td)/'result.json'
  run(['/usr/bin/xcrun','devicectl',*args,'--timeout',str(timeout),'--json-output',file],timeout=timeout+10)
  return read_json(file,{})

def devices():
 data=devicectl(['list','devices'],20);out=[]
 for d in data.get('result',{}).get('devices',[]):
  props=d.get('deviceProperties',{});hw=d.get('hardwareProperties',{});conn=d.get('connectionProperties',{})
  if 'Reality' not in str(hw.get('productType','')) and 'Vision' not in str(hw.get('marketingName','')):continue
  out.append({'id':hw.get('udid') or d.get('identifier'),'name':props.get('name','Vision Pro'),'state':conn.get('tunnelState','unknown'),'model':hw.get('marketingName','Apple Vision Pro')})
 return out

def preflight(device):
 if not device:
  ds=devices()
  if len(ds)!=1:raise ValueError(tr('请选择要更新的 Vision Pro'))
  device=ds[0]['id']
 try:
  data=devicectl(['device','info','files','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--subdirectory','Documents'],25)
 except Exception as e:raise RuntimeError(tr('无法连接现有自定义歌曲应用。请解锁头显并保持同一 Wi-Fi；确认此头显已安装之前配置的独立应用。\n')+str(e))
 names=[f['name'] for f in data.get('result',{}).get('files',[])]
 if 'beatsaber140' not in names or 'beatsaber-1.40.apk' not in names:raise ValueError(tr('头显缺少首次运行所需的 1.40.8 程序数据。请先完成已有独立应用的初次安装。'))
 return device

def pack_keys():
 import zipfile
 if not SOURCE.is_file():raise ValueError(tr('找不到 AVP Play 已下载的 Beat Saber 1.40.8 资源，请恢复该版本的本地下载。'))
 with zipfile.ZipFile(SOURCE) as z:keys=[Path(n).name.split('_pack_assets_all_')[0] for n in z.namelist() if '_pack_assets_all_' in n and '/debug_' not in n]
 return PRIORITY+[k for k in keys if k not in PRIORITY]

def stream(cmd):
 p=subprocess.Popen([str(v) for v in cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
 tail=[];failure=None
 for line in p.stdout:
  tail.append(line.rstrip());tail=tail[-30:]
  try:
   v=json.loads(line);event=v.pop('event')
   if event=='error':failure=v.get('message')
   else:emit(event,**v)
  except (ValueError,KeyError):
   if line.strip():note(line.strip())
 if p.wait():raise RuntimeError(failure or '\n'.join(tail[-5:]))

def check_build_space(groups,job):
 import soundfile as sf
 seen=set();pcm=0;previews=0
 for group in groups:
  for song in group['songs']:
   try:
    raw=read_json(song['infoPath']);name=raw.get('_songFilename') or raw['audio']['songFilename'];audio=sf.info(local(Path(song['folder']),name))
   except Exception as e:raise ValueError(song['title']+' ['+song['mapper']+']：'+str(e))
   if song['id'] not in seen:pcm+=audio.frames*audio.channels*2;seen.add(song['id'])
   preview=raw.get('_previewDuration',raw.get('audio',{}).get('previewDuration',12)) or 12
   previews+=min(audio.frames,max(1,int(preview*audio.samplerate)))*audio.channels*2
 with zipfile.ZipFile(SOURCE) as z:base=sum(i.file_size for i in z.infolist() if not i.filename.startswith('assets/BeatmapLevelsData/'))
 needed=base+2*pcm+2*previews+768*1024**2
 free=shutil.disk_usage(SUPPORT).free
 if free<needed:raise ValueError(tr('此次处理需要约 {0:.1f} GB 可用空间，目前剩余 {1:.1f} GB。请释放空间后重试；头显曲库尚未修改。').format(needed / 1024 ** 3, free / 1024 ** 3))

def prune_build_cache(current):
 previous=read_json(SUPPORT/'latest-success.json',{}).get('resource')
 protected={current.resolve()}
 if previous:protected.add(Path(previous).parent.resolve())
 latest=read_json(SUPPORT/'latest.json',{}).get('job')
 if latest:protected.add(Path(latest).resolve())
 folder=SUPPORT/'builds'
 if folder.exists():
  for p in folder.iterdir():
   if p.is_dir() and p.resolve() not in protected:shutil.rmtree(p,ignore_errors=True)

def library_signature(library):
 source=SOURCE.stat()
 groups=[g for g in library['playlists'] if g['songs']] or [{'name':library['playlists'][0]['name'] if library['playlists'] else 'Custom Songs','songs':[]}]
 data={'source':[source.st_size,source.st_mtime_ns],'groups':[[g['name'],[[s['contentKey'],s['levelId']] for s in g['songs']]] for g in groups],'scripts':[hashlib.sha256((RES/n).read_bytes()).hexdigest() for n in ['build.py','convert.cjs']]}
 return hashlib.sha256(json.dumps(data,ensure_ascii=False).encode()).hexdigest()

def build(root,job):
 library=scan(root)
 if library['errors']:raise ValueError(tr('请先处理以下谱面问题：\n')+'\n'.join(library['errors']))
 groups=[g for g in library['playlists'] if g['songs']]
 if not groups:groups=[{'name':library['playlists'][0]['name'] if library['playlists'] else 'Custom Songs','songs':[]}]
 keys=pack_keys();signature=library_signature(library);previous=read_json(SUPPORT/'latest.json',{})
 previous_job=Path(previous.get('job','/nonexistent'));previous_obb=previous_job/'main.1716.com.beatgames.beatsaber.obb'
 if previous.get('signature')==signature and previous_obb.is_file() and (previous_job/'verification.json').is_file():
  note(tr('曲库未改变，复用上次生成的曲库…'));job.mkdir(parents=True,exist_ok=True)
  if job.resolve()!=previous_job.resolve():
   run(['/bin/cp','-c',previous_obb,job/previous_obb.name]);shutil.copy2(previous_job/'verification.json',job/'verification.json')
  return read_json(job/'verification.json')
 prune_build_cache(job);check_build_space(groups,job)
 if len(groups)>len(keys):raise ValueError(tr('目前最多支持 {0} 个非空曲包文件夹').format(len(keys)))
 cfg=[]
 for key,group in zip(keys,groups):
  for song in group['songs']:cfg.append({'folder':song['folder'],'infoPath':song['infoPath'],'slot':song['levelId'].lower(),'levelId':song['levelId'],'pack':key,'playlistName':group['name'],'contentKey':song['contentKey'],'label':song['title']+' ['+song['mapper']+']'})
 job.mkdir(parents=True,exist_ok=True);atomic(job/'config.json',cfg);atomic(job/'job.json',{'sourceObb':str(SOURCE),'cache':str(SUPPORT/'song-cache-v2'),'sourceStamp':[SOURCE.stat().st_size,SOURCE.stat().st_mtime_ns],'playlists':[{'pack':k,'name':g['name']} for k,g in zip(keys,groups)]})
 note(tr('开始处理 ')+str(library['uniqueSongs'])+tr(' 份谱面、')+str(len(groups))+tr(' 个曲包'))
 node=RES/'runtime/bin/node';node=node if node.exists() else Path(shutil.which('node') or '/nonexistent')
 try:
  stream([node,RES/'convert.cjs',job]);stream([sys.executable,RES/'build.py',job])
 except Exception:
  shutil.rmtree(job/'payload',ignore_errors=True);(job/'main.1716.com.beatgames.beatsaber.obb').unlink(missing_ok=True);raise
 shutil.rmtree(job/'payload',ignore_errors=True);atomic(SUPPORT/'latest.json',{'job':str(job),'root':str(root),'builtAt':time.time(),'signature':signature});return read_json(job/'verification.json')

def send_resource(device,file):
 run(['/usr/bin/xcrun','devicectl','device','copy','to','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source',file,'--destination','Documents/android-files/obb/main.1716.com.beatgames.beatsaber.obb','--timeout','900'],timeout=910)

def sign_app(name,job):
 name=name.strip()
 if not name or len(name)>60:raise ValueError(tr('应用名称请使用 1–60 个字符'))
 runtime=integration.prepare(ENVIRONMENT,SUPPORT,RES,TEAM,BUNDLE,note)
 target=job/'Klepton.app';shutil.rmtree(target,ignore_errors=True)
 run(['/usr/bin/ditto',runtime['app'],target])
 info=target/'Info.plist';d=plistlib.loads(info.read_bytes())
 d.update(CFBundleIdentifier=BUNDLE,CFBundleDisplayName=name,CFBundleName=name,CFBundleVersion=str(int(time.time())),KLApkName='beatsaber-1.40.apk',KLTree='beatsaber140',KLObbFile=integration.OBB_NAME,KLStartScreen='1',KLTestBuild='0',KLAutoBootDefault='1',KLMetaApkID='',KLMetaObbID='')
 info.write_bytes(plistlib.dumps(d))
 profile,identity,profile_file=integration.provisioning(RES,SUPPORT,TEAM,BUNDLE,DEVICE,note)
 shutil.copy2(profile_file,target/'embedded.mobileprovision')
 entitlements=job/'signing.entitlements';entitlements.write_bytes(plistlib.dumps(profile['Entitlements']))
 run(['/usr/bin/xattr','-cr',target])
 return integration.sign_application(target,identity,entitlements,run)

def install(root,name,device):
 global DEVICE
 if not name.strip() or len(name.strip())>60:raise ValueError(tr('应用名称请使用 1–60 个字符'))
 if not device:
  ds=devices()
  if len(ds)!=1:raise ValueError(tr('请选择要安装的 Vision Pro'))
  device=ds[0]['id']
 DEVICE=device
 if not re.fullmatch(r'[A-Z0-9]{10}',TEAM):raise ValueError(tr('请在安装设置中填写自己的 Apple 开发团队 ID'))
 job=SUPPORT/'builds'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);job.mkdir(parents=True)
 # Build and sign completely before installing or staging any data.
 report=build(root,job);app=sign_app(name,job)
 runtime=integration.prepare(ENVIRONMENT,SUPPORT,RES,TEAM,BUNDLE,note)
 apps=devicectl(['device','info','apps','--device',device],30)
 installed=any(a.get('bundleIdentifier')==BUNDLE for a in apps.get('result',{}).get('apps',[]))
 backup=None
 if installed:
  try:
   listing=devicectl(['device','info','files','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--subdirectory','Documents/android-files/files'])
  except Exception as e:
   if not any(v in str(e).lower() for v in ['no such file','does not exist','couldn’t be found','not found']):raise
   listing={}
  if any(f.get('name')=='PlayerData.dat' for f in listing.get('result',{}).get('files',[])):
   backup=SUPPORT/'backups'/job.name;backup.mkdir(parents=True,exist_ok=True)
   run(['/usr/bin/xcrun','devicectl','device','copy','from','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source','Documents/android-files/files/PlayerData.dat','--destination',backup/'PlayerData.dat','--timeout','45'],timeout=55)
 note(tr('正在安装你自己的独立自定义歌曲应用…'))
 run(['/usr/bin/xcrun','devicectl','device','install','app','--device',device,'--timeout','90',app],timeout=100)
 tree=Path(runtime['tree'])
 files=[(tree/'assets','Documents/beatsaber140/assets'),(tree/'apktool.yml','Documents/beatsaber140/apktool.yml'),(tree/'AndroidManifest.xml','Documents/beatsaber140/AndroidManifest.xml'),(Path(ENVIRONMENT['apk']),'Documents/beatsaber-1.40.apk')]
 for source,destination in files:
  if not source.exists():raise ValueError(tr('缺少首次安装文件：')+str(source))
  note(tr('正在传输首次运行文件：')+source.name)
  run(['/usr/bin/xcrun','devicectl','device','copy','to','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source',source,'--destination',destination,'--timeout','900'],timeout=910)
 note(tr('正在传输自定义曲库…'));send_resource(device,job/integration.OBB_NAME)
 listing=devicectl(['device','info','files','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--subdirectory','Documents/android-files/obb'])
 remote=next(f for f in listing['result']['files'] if f['name']==integration.OBB_NAME)
 if remote['metadata']['size']!=report['resourceBytes']:raise RuntimeError(tr('头显曲库资源大小不匹配，请点击首次安装/修复重试'))
 atomic(SUPPORT/'latest-success.json',{'resource':str(job/integration.OBB_NAME),'bundle':BUNDLE,'name':name,'device':device,'signature':library_signature(scan(root)),'sha256':report['resourceSha256'],'resourceBytes':report['resourceBytes']})
 same=True
 if backup:
  run(['/usr/bin/xcrun','devicectl','device','copy','from','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source','Documents/android-files/files/PlayerData.dat','--destination',backup/'PlayerData-after.dat','--timeout','45'],timeout=55)
  same=(backup/'PlayerData.dat').read_bytes()==(backup/'PlayerData-after.dat').read_bytes()
 return {'installed':True,'name':name,'device':device,'backup':str(backup) if backup else None,'report':report,'scoresUnchanged':same,'launchSucceeded':False}

def update(root,name,device,rename_only=False):
 global DEVICE
 if not name.strip() or len(name.strip())>60:raise ValueError(tr('应用名称请使用 1–60 个字符'))
 note(tr('正在连接 Vision Pro，请保持头显解锁…'));device=preflight(device);DEVICE=device
 signature=None
 if not rename_only:
  library=scan(root)
  if library['errors']:raise ValueError(tr('请先处理以下谱面问题：\n')+'\n'.join(library['errors']))
  signature=library_signature(library);previous=read_json(SUPPORT/'latest-success.json',{})
  if previous.get('signature')==signature and previous.get('device')==device and previous.get('bundle')==BUNDLE:
   files=devicectl(['device','info','files','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--subdirectory','Documents/android-files/obb'])
   remote=next((f for f in files.get('result',{}).get('files',[]) if f['name']=='main.1716.com.beatgames.beatsaber.obb'),{})
   if remote.get('metadata',{}).get('size')==previous.get('resourceBytes'):
    if previous.get('name')==name:
     note(tr('头显曲库已经是最新，无需重新处理或传输。'));return {'noChanges':True,'scoresUnchanged':True,'launchSucceeded':True}
    rename_only=True;note(tr('曲库没有变化，仅更新应用名称…'))
 job=SUPPORT/'builds'/time.strftime('%Y%m%d-%H%M%S');job.mkdir(parents=True,exist_ok=True)
 backup=SUPPORT/'backups'/job.name;backup.mkdir(parents=True,exist_ok=True)
 note(tr('正在备份成绩…'))
 run(['/usr/bin/xcrun','devicectl','device','copy','from','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source','Documents/android-files/files/PlayerData.dat','--destination',backup/'PlayerData.dat','--timeout','45'],timeout=55)
 report=None
 if not rename_only:report=build(root,job)
 note(tr('正在准备应用名称和签名…'));app=sign_app(name,job)
 # All conversion and signature checks finish before any changes to the headset.
 note(tr('正在更新头显应用名称…'));run(['/usr/bin/xcrun','devicectl','device','install','app','--device',device,'--timeout','90',app],timeout=100)
 if not rename_only:
  note(tr('正在传输曲库，可能需要几分钟，请保持头显解锁…'))
  try:send_resource(device,job/'main.1716.com.beatgames.beatsaber.obb')
  except Exception as e:
   previous=read_json(SUPPORT/'latest-success.json',{})
   previous_file=Path(previous.get('resource','/nonexistent'))
   if previous.get('bundle')==BUNDLE and previous_file.is_file():
    try:
     note(tr('本次传输未完成，正在恢复上次曲库…'));send_resource(device,previous_file)
     raise RuntimeError(tr('本次更新未完成，已恢复上次曲库。请保持头显解锁后重试。\n')+str(e))
    except Exception as restore:
     if tr('已恢复上次曲库') in str(restore):raise
     raise RuntimeError(tr('连接中断，恢复暂未完成。请解锁头显后重新更新曲库；本地上次曲库和成绩备份仍在。\n')+str(e))
   raise
  files=devicectl(['device','info','files','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--subdirectory','Documents/android-files/obb'])
  remote=next(f for f in files['result']['files'] if f['name']=='main.1716.com.beatgames.beatsaber.obb');assert remote['metadata']['size']==report['resourceBytes'],tr('头显资源大小不匹配')
 run(['/usr/bin/xcrun','devicectl','device','copy','from','--device',device,'--domain-type','appDataContainer','--domain-identifier',BUNDLE,'--source','Documents/android-files/files/PlayerData.dat','--destination',backup/'PlayerData-after.dat','--timeout','40'],timeout=50)
 same=(backup/'PlayerData.dat').read_bytes()==(backup/'PlayerData-after.dat').read_bytes()
 launch_ok=True
 try:
  note(tr('正在重新打开应用…'));run(['/usr/bin/xcrun','devicectl','device','process','launch','--device',device,'--terminate-existing','--timeout','20',BUNDLE],timeout=30)
 except Exception:launch_ok=False
 result={'name':name,'device':device,'job':str(job),'backup':str(backup),'scoresUnchanged':same,'launchSucceeded':launch_ok,'report':report}
 atomic(job/'deployment.json',result)
 if not rename_only:atomic(SUPPORT/'latest-success.json',{'resource':str(job/'main.1716.com.beatgames.beatsaber.obb'),'bundle':BUNDLE,'name':name,'sha256':report['resourceSha256'],'signature':signature,'device':device,'resourceBytes':report['resourceBytes']})
 else:
  previous=read_json(SUPPORT/'latest-success.json',{})
  if previous and previous.get('device')==device and previous.get('bundle')==BUNDLE:previous['name']=name;atomic(SUPPORT/'latest-success.json',previous)
 # Keep the deployed resource and this operation; score backups stay separate.
 prune_build_cache(job)
 return result

def configure(arguments):
 global ENVIRONMENT,TEAM,BUNDLE,SOURCE
 settings=read_json(SUPPORT/'settings.json',{})
 for key,attr in [('avpRoot','avp_root'),('avpApp','avp_app'),('store','store'),('team','team')]:
  value=getattr(arguments,attr,None)
  if value is not None:settings[key]=value
 if arguments.action=='configure':atomic(SUPPORT/'settings.json',settings)
 ENVIRONMENT=integration.discover(settings.get('avpRoot') or None,settings.get('avpApp') or None,settings.get('store') or None)
 TEAM=settings.get('team') or ENVIRONMENT.get('team','')
 BUNDLE='io.saberdock.'+TEAM.lower()+'.beatsaber140' if TEAM else 'io.saberdock.beatsaber140'
 SOURCE=Path(ENVIRONMENT['sourceObb'])
 ENVIRONMENT.update(team=TEAM,bundle=BUNDLE)
 return ENVIRONMENT

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['environment','configure','prepare','install','order','delete','restore','init','scan','import','create','devices','build','update','rename','preflight']);p.add_argument('--root',default=str(Path.home()/'Music/SaberDock Library'));p.add_argument('--category',default='');p.add_argument('--name',default='SaberDock Custom Songs');p.add_argument('--device',default='');p.add_argument('--job');p.add_argument('--avp-root');p.add_argument('--avp-app');p.add_argument('--store');p.add_argument('--team');p.add_argument('paths',nargs='*');a=p.parse_intermixed_args();SUPPORT.mkdir(parents=True,exist_ok=True)
 lock=(SUPPORT/'job.lock').open('w')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise ValueError(tr('另一个曲库操作正在进行，请稍后重试'))
 environment=configure(a)
 if a.action in ['environment','configure']:result=environment
 elif a.action=='prepare':result=integration.prepare(environment,SUPPORT,RES,TEAM,BUNDLE,note)
 elif a.action=='install':result=install(a.root,a.name,a.device)
 elif a.action in ['order','delete','restore']:result=manage(a.root,a.category,a.action,a.paths)
 elif a.action=='init':result=init(a.root)
 elif a.action=='scan':result=scan(a.root)
 elif a.action=='import':result=import_paths(a.root,a.category,a.paths)
 elif a.action=='create':(Path(a.root)/safe_name(a.category)).mkdir(parents=True,exist_ok=True);result=scan(a.root)
 elif a.action=='devices':result=devices()
 elif a.action=='preflight':result={'device':preflight(a.device)}
 elif a.action=='build':result=build(a.root,Path(a.job) if a.job else SUPPORT/'builds'/time.strftime('%Y%m%d-%H%M%S'))
 else:result=update(a.root,a.name,a.device,a.action=='rename')
 emit('result',data=result)
if __name__=='__main__':
 try:main()
 except Exception as e:
  emit('error',message=str(e));sys.exit(1)
