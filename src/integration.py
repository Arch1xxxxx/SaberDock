from i18n import tr
"""Reuse user-selected local AVP Play files without filtering game versions."""
import hashlib,json,plistlib,re,shutil,subprocess,zipfile
from pathlib import Path

def read(path,default=None):
 try:return json.loads(Path(path).read_text())
 except FileNotFoundError:return default

def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.new');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)

def version_info(tree):
 path=Path(tree)/'apktool.yml'
 if not path.is_file():return {'name':'','code':None}
 text=path.read_text()
 name=re.search(r"""versionName:\s*['"]?([^\s'"]+)""",text)
 code=re.search(r"""versionCode:\s*['"]?(\d+)""",text)
 return {'name':name[1] if name else '', 'code':int(code[1]) if code else None}

def component(name):
 return isinstance(name,str) and bool(name) and name not in ('.','..') and Path(name).name==name and '/' not in name and '\\' not in name

def resource_name(environment):
 name=environment.get('obbName','')
 if not component(name):raise ValueError(tr('请选择本地 OBB 资源文件。'))
 return name

def app_info(app):
 try:
  path=Path(app);info=plistlib.loads((path/'Info.plist').read_bytes())
  executable=info.get('CFBundleExecutable','')
  if not component(executable) or not (path/executable).is_file():return None
  if not component(info.get('KLTree','')):return None
  if not component(info.get('KLApkName','')):info['KLApkName']='game.apk'
  return info
 except (OSError,ValueError,TypeError):return None

def reusable_build(matched):
 return bool(matched and app_info(matched.get('app','/nonexistent')))

def data_tree(path):
 path=Path(path)
 return (path/'assets').is_dir() and (path/'AndroidManifest.xml').is_file()

def infer_tree(app,info):
 for parent in Path(app).resolve().parents:
  candidate=parent/info['KLTree']
  if data_tree(candidate):return candidate
 return None

def _discover_files(base=None,app=None,store=None,*,runtime_app=None,apk=None,obb=None,tree=None):
 base=Path(base or Path.home()/'Library/Application Support/AVPPlay').expanduser().resolve()
 candidates=[Path(app).expanduser()] if app else [Path('/Applications/AVP Play.app'),Path.home()/'Applications/AVP Play.app']
 avp_app=next((p for p in candidates if p.is_dir()),None)
 settings=read(base/'settings.json',{})
 store=Path(store or settings.get('store') or base/'store').expanduser().resolve()
 jobs=[]
 for path in (base/'jobs').glob('beatsaber*.json'):
  try:jobs.append(read(path,{}))
  except (ValueError,OSError):continue
 jobs.sort(key=lambda j:j.get('updated',''),reverse=True)
 toolchains=[];team=''
 for job in jobs:
  request=job.get('request',{});chain=Path(request.get('toolchain','/nonexistent'))
  if request.get('team') and not team:team=request['team']
  if chain.is_dir() and str(chain) not in toolchains:toolchains.append(str(chain))
 for chain in sorted((base/'toolchains').glob('*'),key=lambda p:p.stat().st_mtime,reverse=True):
  if chain.is_dir() and str(chain) not in toolchains:toolchains.append(str(chain))
 builds=[Path(runtime_app).expanduser()] if runtime_app else [built for chain in toolchains for built in Path(chain).glob('visionos/build/dd-device-beatsaber*/Build/Products/*-xros/*.app')]
 selected_app=builds[0] if builds else None;info=app_info(selected_app) if selected_app else None
 selected_tree=Path(tree).expanduser() if tree else None
 selected_apk=Path(apk).expanduser() if apk else None
 selected_obb=Path(obb).expanduser() if obb else None
 for built in builds:
  current=app_info(built)
  if not current:continue
  current_tree=selected_tree or infer_tree(built,current)
  metadata=version_info(current_tree) if current_tree else {'name':'','code':None}
  folders=[]
  if selected_apk:folders.append(selected_apk.parent)
  if selected_obb:folders.append(selected_obb.parent)
  if metadata['code'] is not None:folders.append(store/('beatsaber140-'+str(metadata['code'])))
  folders += [store]+sorted(store.glob('beatsaber*'),key=lambda p:p.stat().st_mtime,reverse=True)
  candidate_apk=selected_apk;candidate_obb=selected_obb
  for folder in folders:
   if not folder.is_dir():continue
   apks=[folder/current.get('KLApkName','beat-saber.apk'),folder/'beat-saber.apk']+list(folder.glob('*.apk'))
   obbs=[folder/current['KLObbFile']] if component(current.get('KLObbFile','')) else []
   a=candidate_apk or next((p for p in apks if p.is_file()),None)
   o=candidate_obb or next((p for p in obbs if p.is_file()),None)
   if a and o:candidate_apk=a;candidate_obb=o;break
  if runtime_app or (current_tree and candidate_apk and candidate_obb):
   selected_app=built;info=current;selected_tree=current_tree;selected_apk=candidate_apk;selected_obb=candidate_obb;break
 if selected_app and info and not selected_tree:selected_tree=infer_tree(selected_app,info)
 issues=[]
 if not info:issues.append(tr('请选择 AVP Play 已生成的游戏 visionOS 应用（.app），不是 Mac 上的 AVP Play.app。'))
 if not selected_apk or not selected_apk.is_file():issues.append(tr('请选择本地 APK 游戏文件。'))
 if not selected_obb or not selected_obb.is_file():issues.append(tr('请选择本地 OBB 资源文件。'))
 if not selected_tree or not data_tree(selected_tree):issues.append(tr('请选择游戏数据文件夹，其中须包含 assets 和 AndroidManifest.xml。'))
 metadata=version_info(selected_tree) if selected_tree else {'name':'','code':None}
 matched={'app':str(selected_app),'tree':str(selected_tree)} if info and selected_tree else None
 return {'avpRoot':str(base),'avpApp':str(avp_app) if avp_app else '', 'store':str(store),
         'runtimeApp':str(selected_app) if selected_app else '', 'gameTree':str(selected_tree) if selected_tree else '',
         'apk':str(selected_apk) if selected_apk else '', 'sourceObb':str(selected_obb) if selected_obb else '',
         'treeName':info['KLTree'] if info else 'beatsaber', 'apkName':info.get('KLApkName') or (selected_apk.name if selected_apk else 'game.apk') if info else 'game.apk',
         'obbName':selected_obb.name if selected_obb else '', 'toolchains':toolchains,'matched':matched,'team':team,
         'ready':not issues,'issues':issues,'version':metadata['name'],'versionName':metadata['name'],'versionCode':metadata['code']}

def local_versions(base=None,store=None):
 base=Path(base or Path.home()/'Library/Application Support/AVPPlay').expanduser().resolve()
 settings=read(base/'settings.json',{})
 store=Path(store or settings.get('store') or base/'store').expanduser().resolve()
 jobs=[]
 for path in (base/'jobs').glob('beatsaber*.json'):
  try:jobs.append(read(path,{}))
  except (ValueError,OSError):continue
 jobs.sort(key=lambda j:j.get('updated',''),reverse=True)
 chains=[];names={};team=''
 for job in jobs:
  request=job.get('request',{});recipe=job.get('recipe',{})
  if not team:team=request.get('team','')
  chain=Path(request.get('toolchain','/nonexistent')).expanduser().resolve()
  if chain.is_dir() and chain not in chains:chains.append(chain)
  code=recipe.get('versionCode')
  if code is not None and recipe.get('versionName'):names.setdefault(str(code),recipe['versionName'])
 for chain in sorted((base/'toolchains').glob('*'),key=lambda p:p.stat().st_mtime,reverse=True):
  if chain.is_dir() and chain not in chains:chains.append(chain)
 builds={}
 for chain in chains:
  builds[str(chain)]=[]
  for built in sorted(chain.glob('visionos/build/dd-device-beatsaber*/Build/Products/*-xros/*.app'),key=lambda p:p.stat().st_mtime,reverse=True):
   info=app_info(built)
   if not info:continue
   tree=infer_tree(built,info)
   metadata=version_info(tree) if tree else {'name':'','code':None}
   builds[str(chain)].append((built,info,tree,metadata))
   if metadata['code'] is not None and metadata['name']:names.setdefault(str(metadata['code']),metadata['name'])
 folders=sorted((p for p in store.glob('beatsaber*') if p.is_dir()),key=lambda p:p.stat().st_mtime,reverse=True)
 if store.is_dir() and any(store.glob('*.apk')):folders.insert(0,store)
 games=[]
 for folder in folders:
  apks=sorted(folder.glob('*.apk'));obbs=sorted(folder.glob('*.obb'))
  if not apks and not obbs:continue
  code=next((m[1] for p in obbs if (m:=re.match(r'main\.(\d+)\.',p.name))),None)
  if code is None:
   match=re.search(r'-(\d+)$',folder.name);code=match[1] if match else None
  name=names.get(code,'')
  games.append({'id':str(folder),'label':(name+' · '+code if name and code else folder.name),'code':code,
                'apk':str(next((p for p in apks if p.name=='beat-saber.apk'),apks[0] if apks else '')),
                'obbs':[str(p) for p in obbs],'name':name})
 return base,store,games,[{'id':str(c),'label':c.name} for c in chains],builds,team

def discover(base=None,app=None,store=None,*,game_version=None,toolchain_version=None,**files):
 if any(files.values()):return _discover_files(base,app,store,**files)
 base,store,games,chains,builds,team=local_versions(base,store)
 if game_version:game_version=str(Path(game_version).expanduser().resolve())
 if toolchain_version:toolchain_version=str(Path(toolchain_version).expanduser().resolve())
 def compatible(game,record):
  built,info,tree,metadata=record
  return bool(tree and any(Path(o).name==info.get('KLObbFile') for o in game['obbs'])
              and (metadata['code'] is None or game['code'] is None or str(metadata['code'])==game['code']))
 chain=next((c for c in chains if c['id']==toolchain_version),None) if toolchain_version else next(iter(chains),None)
 game=next((g for g in games if g['id']==game_version),None) if game_version else None
 records=builds.get(chain['id'],[]) if chain else []
 if game is None and not game_version:
  game=next((g for g in games if any(compatible(g,r) for r in records)),next(iter(games),None))
 record=next((r for r in records if game and compatible(game,r)),None)
 if record:
  built,info,tree,metadata=record
  obb=next(o for o in game['obbs'] if Path(o).name==info.get('KLObbFile'))
  env=_discover_files(base,app,store,runtime_app=built,apk=game['apk'] or '/nonexistent',obb=obb,tree=tree)
 else:
  candidates=[Path(app).expanduser()] if app else [Path('/Applications/AVP Play.app'),Path.home()/'Applications/AVP Play.app']
  avp_app=next((p for p in candidates if p.is_dir()),None)
  env={'avpRoot':str(base),'avpApp':str(avp_app) if avp_app else '', 'store':str(store),
       'runtimeApp':'','gameTree':'','apk':game['apk'] if game else '',
       'sourceObb':game['obbs'][0] if game and game['obbs'] else '', 'treeName':'beatsaber','apkName':'game.apk',
       'obbName':Path(game['obbs'][0]).name if game and game['obbs'] else '', 'matched':None,
       'version':game['name'] if game else '', 'versionName':game['name'] if game else '',
       'versionCode':int(game['code']) if game and game['code'] else None, 'ready':False,'issues':[]}
  if not game:env['issues'].append(tr('未找到所选游戏版本，请先在 AVP Play 下载游戏，然后刷新列表。'))
  if not chain:env['issues'].append(tr('未找到所选 Toolchain，请先在 AVP Play 下载工具链，然后刷新列表。'))
  if game and chain:env['issues'].append(tr('所选组合缺少对应的游戏程序或数据，请先在 AVP Play 使用此 Toolchain 完成该游戏版本的安装，然后刷新列表。'))
 env.update(gameVersions=[{'id':g['id'],'label':g['label']} for g in games],toolchainVersions=chains,
            selectedGame=game['id'] if game else '',selectedToolchain=chain['id'] if chain else '',
            toolchains=[c['id'] for c in chains],team=team)
 return env

def validate_source(environment):
 if not environment['ready']:raise ValueError('\n'.join(environment['issues']))
 if not reusable_build(environment.get('matched')):raise ValueError(tr('请选择 AVP Play 已生成的游戏 visionOS 应用（.app），不是 Mac 上的 AVP Play.app。'))
 if not data_tree(environment['matched']['tree']):raise ValueError(tr('请选择游戏数据文件夹，其中须包含 assets 和 AndroidManifest.xml。'))
 resource_name(environment)
 try:
  with zipfile.ZipFile(environment['apk']) as z:
   if 'AndroidManifest.xml' not in z.namelist() or 'lib/arm64-v8a/libil2cpp.so' not in z.namelist():raise ValueError(tr('所选 APK 缺少游戏程序文件，请重新选择完整的本地 APK。'))
  with zipfile.ZipFile(environment['sourceObb']) as z:
   required=['assets/BeatmapLevelsData/fitbeat','assets/aa/catalog.json']
   if any(p not in z.namelist() for p in required):raise ValueError(tr('所选 OBB 缺少曲库处理所需的资源结构。已取消操作，头显尚未修改。'))
 except zipfile.BadZipFile:raise ValueError(tr('所选 APK 或 OBB 不是完整的资源包，请重新选择文件。'))

def command(argv,*,cwd=None,env=None,timeout=900):
 result=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 if result.returncode:raise RuntimeError(result.stdout.strip()[-4000:] or tr('操作失败'))
 return result.stdout

def prepare(environment,support,resources,team,bundle,note,*,build_app=True):
 validate_source(environment)
 matched=environment['matched'];tree=Path(matched['tree']);version=version_info(tree);obb_name=resource_name(environment)
 source=Path(matched['app']).resolve();info=app_info(source);stamp=(source/info['CFBundleExecutable']).stat()
 source_stamp=[str(source),stamp.st_size,stamp.st_mtime_ns]
 identity=hashlib.sha256(('local-files-v1'+hashlib.sha256(Path(environment['apk']).read_bytes()).hexdigest()+json.dumps(source_stamp)+str(tree)+obb_name+bundle).encode()).hexdigest()[:24]
 destination=Path(support)/'runtime-prepared'/identity
 manifest=read(destination/'runtime.json',{})
 if manifest.get('sourceBuild')==source_stamp and reusable_build(manifest):return manifest
 if not build_app:return {'tree':str(tree),'versionCode':version['code'],'versionName':version['name'],'obbName':obb_name}
 destination.mkdir(parents=True,exist_ok=True)
 target=destination/'Klepton.app';shutil.rmtree(target,ignore_errors=True)
 command(['/usr/bin/ditto',source,target]);note(tr('已复用所选本地游戏应用。'))
 if not reusable_build({'app':str(target)}):raise ValueError(tr('所选游戏应用复制后不完整，请重新选择本地构建。'))
 result={'app':str(target),'tree':str(tree),'apk':environment['apk'],'versionCode':version['code'],'versionName':version['name'],'obbName':obb_name,'sourceBuild':source_stamp}
 save(destination/'runtime.json',result);return result


def provisioning(resources,support,team,bundle,device,note):
 if not re.fullmatch(r'[A-Z0-9]{10}',team):raise ValueError(tr('未找到 Apple 开发签名设置，请先在 AVP Play 使用自己的 Apple 账户完成一次游戏安装。'))
 support=Path(support);resources=Path(resources);folder=support/'signing'/bundle;project=folder/'LibrarySign.xcodeproj';project.mkdir(parents=True,exist_ok=True)
 path=folder/'Derived/Build/Products/Debug-xros/LibrarySign.app/embedded.mobileprovision'
 def parse():
  profile=plistlib.loads(subprocess.check_output(['/usr/bin/security','cms','-D','-i',str(path)],stderr=subprocess.DEVNULL))
  import datetime
  if profile['ExpirationDate']<datetime.datetime.now()+datetime.timedelta(hours=12):raise ValueError(tr('签名已过期'))
  if profile['TeamIdentifier'][0]!=team or profile['Entitlements']['application-identifier'].split('.',1)[1]!=bundle:raise ValueError(tr('签名标识不匹配'))
  if device and device not in profile.get('ProvisionedDevices',[]):raise ValueError(tr('签名尚未包含该头显'))
  identities=command(['/usr/bin/security','find-identity','-v','-p','codesigning'])
  identity=next((hashlib.sha1(c).hexdigest().upper() for c in profile['DeveloperCertificates'] if hashlib.sha1(c).hexdigest().upper() in identities),None)
  if not identity:raise ValueError(tr('找不到签名证书的私钥'))
  return profile,identity,path
 try:return parse()
 except (OSError,ValueError,KeyError,StopIteration,subprocess.SubprocessError):pass
 note(tr('正在通过本机 Xcode 账户生成你的开发签名…'))
 (folder/'Main.swift').write_text('import SwiftUI\n@main struct SigningApp: App { var body: some Scene { WindowGroup { Text("SaberDock") } } }')
 entitlements={'com.apple.developer.kernel.extended-virtual-addressing':True,'com.apple.developer.kernel.increased-memory-limit':True,'com.apple.developer.low-latency-streaming':True}
 (folder/'Headset.entitlements').write_bytes(plistlib.dumps(entitlements))
 template=(resources/'SigningProject.pbxproj').read_text().replace('TEAM_PLACEHOLDER',team).replace('BUNDLE_PLACEHOLDER',bundle)
 template=template.replace('CODE_SIGN_STYLE = Automatic;','CODE_SIGN_STYLE = Automatic; CODE_SIGN_ENTITLEMENTS = Headset.entitlements;')
 (project/'project.pbxproj').write_text(template)
 command(['/usr/bin/xcrun','xcodebuild','-project',project,'-scheme','LibrarySign','-configuration','Debug','-sdk','xros','-destination','id='+device if device else 'generic/platform=visionOS','-derivedDataPath',folder/'Derived','-allowProvisioningUpdates','-allowProvisioningDeviceRegistration','build'],timeout=600)
 return parse()


def sign_application(app,identity,entitlements,run=command):
 """Sign every embedded Mach-O, including Xcode's root-level debug dylib.

 A top-level `codesign --verify --deep` does not reliably check loose dylibs
 beside the executable. Validate those explicitly before the app is installed.
 """
 app=Path(app);info=plistlib.loads((app/'Info.plist').read_bytes());main=(app/info['CFBundleExecutable']).resolve()
 magic={b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xce',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca',b'\xca\xfe\xba\xbf',b'\xbf\xba\xfe\xca'}
 binaries=[]
 for path in app.rglob('*'):
  if not path.is_file() or path.is_symlink() or path.resolve()==main:continue
  with path.open('rb') as stream:header=stream.read(4)
  if header in magic:binaries.append(path)
 binaries.sort(key=lambda p:(-len(p.parts),str(p)))
 for path in binaries:run(['/usr/bin/codesign','--force','--sign',identity,'--timestamp=none',path])
 for framework in sorted(app.rglob('*.framework'),key=lambda p:len(p.parts),reverse=True):run(['/usr/bin/codesign','--force','--sign',identity,'--timestamp=none',framework])
 run(['/usr/bin/codesign','--force','--sign',identity,'--entitlements',entitlements,'--timestamp=none','--generate-entitlement-der',app])
 for path in binaries:run(['/usr/bin/codesign','--verify','--strict',path])
 run(['/usr/bin/codesign','--verify','--deep','--strict',app])
 return app
