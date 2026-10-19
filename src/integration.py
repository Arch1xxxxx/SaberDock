from i18n import tr
"""Read AVP Play's local library and prepare an isolated, version-matched runtime."""
import hashlib,json,plistlib,re,shutil,subprocess,zipfile
from pathlib import Path
VERSION_CODE=1716
OBB_NAME='main.1716.com.beatgames.beatsaber.obb'

def read(path,default=None):
 try:return json.loads(Path(path).read_text())
 except FileNotFoundError:return default

def save(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.new');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)

def version_of_tree(tree):
 path=Path(tree)/'apktool.yml'
 if not path.is_file():return None
 match=re.search(r'versionCode:\s*[\'\"]?(\d+)',path.read_text())
 return int(match[1]) if match else None

def reusable_build(matched):
 if not matched or version_of_tree(matched.get('tree','/nonexistent'))!=VERSION_CODE:return False
 try:
  app=Path(matched['app']);info=plistlib.loads((app/'Info.plist').read_bytes())
  executable=info.get('CFBundleExecutable','')
  return bool(executable and Path(executable).name==executable and (app/executable).is_file() and info.get('KLObbFile')==OBB_NAME and info.get('KLTree')=='beatsaber140')
 except (OSError,ValueError,KeyError,TypeError):return False

def discover(base=None,app=None,store=None):
 base=Path(base or Path.home()/'Library/Application Support/AVPPlay').expanduser().resolve()
 candidates=[Path(app)] if app else [Path('/Applications/AVP Play.app'),Path.home()/'Applications/AVP Play.app']
 app=next((p for p in candidates if (p/'Contents/Helpers/avpplay').is_file()),None)
 settings=read(base/'settings.json',{})
 store=Path(store or settings.get('store') or base/'store').expanduser().resolve()
 folder=store/'beatsaber140-1716';apk=folder/'beat-saber.apk';obb=folder/OBB_NAME
 jobs=[]
 for path in (base/'jobs').glob('beatsaber140-*.json'):
  try:jobs.append(read(path,{}))
  except (ValueError,OSError):continue
 jobs.sort(key=lambda j:j.get('updated',''),reverse=True)
 toolchains=[];team=''
 for job in jobs:
  request=job.get('request',{});path=Path(request.get('toolchain','/nonexistent'))
  if request.get('team') and not team:team=request['team']
  if (path/'visionos/gen_xcodeproj.py').is_file() and str(path) not in toolchains:toolchains.append(str(path))
 for path in sorted((base/'toolchains').glob('*'),key=lambda p:p.stat().st_mtime,reverse=True):
  if (path/'visionos/gen_xcodeproj.py').is_file() and str(path) not in toolchains:toolchains.append(str(path))
 matched=None
 for raw in toolchains:
  chain=Path(raw)
  if version_of_tree(chain/'beatsaber140')!=VERSION_CODE:continue
  for built in chain.glob('visionos/build/dd-device-beatsaber140*/Build/Products/Debug-xros/*.app'):
   try:
    candidate={'app':str(built),'tree':str(chain/'beatsaber140'),'toolchain':str(chain)}
    if reusable_build(candidate):matched=candidate;break
   except (OSError,ValueError):continue
  if matched:break
 issues=[]
 if not app:issues.append(tr('找不到 AVP Play.app，请先安装 AVP Play 或手动选择其应用文件。'))
 if not apk.is_file() or not obb.is_file():issues.append(tr('未找到 Beat Saber 1.40.8（1716）的完整下载。请先在 AVP Play 下载该版本；当前通用版暂不支持 1.45。'))
 if not toolchains:issues.append(tr('找不到 AVP Play 工具链，请先用 AVP Play 完成一次游戏安装。'))
 if not matched:issues.append(tr('未找到 AVP Play 已生成的 Beat Saber 1.40.8（1716）应用。请先在 AVP Play 下载该版本并完成安装，确认能在 Vision Pro 启动后，再返回 SaberDock。'))
 return {'avpRoot':str(base),'avpApp':str(app) if app else '', 'store':str(store),'apk':str(apk),'sourceObb':str(obb),'toolchains':toolchains,'matched':matched,'team':team,'ready':not issues,'issues':issues,'version':'1.40.8 (1716)'}

def validate_source(environment):
 if not environment['ready']:raise ValueError('\n'.join(environment['issues']))
 with zipfile.ZipFile(environment['apk']) as z:
  if 'AndroidManifest.xml' not in z.namelist() or 'lib/arm64-v8a/libil2cpp.so' not in z.namelist():raise ValueError(tr('AVP Play 中的 APK 不完整或不是 ARM64 Beat Saber。'))
 with zipfile.ZipFile(environment['sourceObb']) as z:
  required=['assets/BeatmapLevelsData/fitbeat','assets/aa/catalog.json']
  if any(p not in z.namelist() for p in required):raise ValueError(tr('下载资源缺少 1.40.8 曲库模板，请在 AVP Play 中修复该版本下载。'))

def command(argv,*,cwd=None,env=None,timeout=900):
 result=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 if result.returncode:raise RuntimeError(result.stdout.strip()[-4000:] or tr('操作失败'))
 return result.stdout

def prepare(environment,support,resources,team,bundle,note,*,build_app=True):
 validate_source(environment)
 matched=environment.get('matched')
 if not reusable_build(matched):raise ValueError(tr('未找到 AVP Play 已生成的 Beat Saber 1.40.8（1716）应用。请先在 AVP Play 下载该版本并完成安装，确认能在 Vision Pro 启动后，再返回 SaberDock。'))
 support=Path(support)
 source=Path(matched['app']).resolve()
 info=plistlib.loads((source/'Info.plist').read_bytes())
 stamp=(source/info['CFBundleExecutable']).stat()
 source_stamp=[str(source),stamp.st_size,stamp.st_mtime_ns]
 identity=hashlib.sha256(('avp-reuse-v1'+str(environment['apk'])+hashlib.sha256(Path(environment['apk']).read_bytes()).hexdigest()+json.dumps(source_stamp)+bundle).encode()).hexdigest()[:24]
 destination=support/'runtime-prepared'/identity
 manifest=read(destination/'runtime.json',{})
 if manifest.get('sourceBuild')==source_stamp and reusable_build(manifest):return manifest
 destination.mkdir(parents=True,exist_ok=True)
 # AVP Play's CLI verifies the APK package and version after decoding it. No fetch/login operation is called.
 recipe={'schema':1,'id':'beatsaber140','title':'Beat Saber','package':'com.beatgames.beatsaber','versionName':'1.40.8','versionCode':1716,'store':{},'toolchain':{'target':'beatsaber140','minCommit':''},'files':[{'name':'beat-saber.apk','role':'apk','id':'0','required':True}], 'status':{'playability':'local','download':'local'}}
 recipes=destination/'recipes';recipes.mkdir(exist_ok=True);save(recipes/'beatsaber140.json',recipe)
 unpacked=destination/'beatsaber140'
 note(tr('正在读取 AVP Play 已下载的 1.40.8 文件…'))
 if unpacked.exists():shutil.rmtree(unpacked)
 command([Path(environment['avpApp'])/'Contents/Helpers/avpplay','unpack','beatsaber140','--recipes',recipes,'--store',environment['store'],'--to',unpacked],timeout=180)
 if version_of_tree(unpacked)!=1716:raise ValueError(tr('APK 版本不匹配，需要 1.40.8（1716）。'))
 if not build_app:return {'tree':str(unpacked),'versionCode':1716}
 target=destination/'Klepton.app';shutil.rmtree(target,ignore_errors=True)
 command(['/usr/bin/ditto',source,target]);note(tr('已复用 AVP Play 的 1.40.8 应用构建。'))
 if not reusable_build({'app':str(target),'tree':str(unpacked)}):raise ValueError(tr('未找到 AVP Play 已生成的 Beat Saber 1.40.8（1716）应用。请先在 AVP Play 下载该版本并完成安装，确认能在 Vision Pro 启动后，再返回 SaberDock。'))
 result={'app':str(target),'tree':str(unpacked),'apk':environment['apk'],'versionCode':1716,'sourceBuild':source_stamp}
 save(destination/'runtime.json',result);return result


def provisioning(resources,support,team,bundle,device,note):
 if not re.fullmatch(r'[A-Z0-9]{10}',team):raise ValueError(tr('请输入自己的 10 位 Apple 开发团队 ID，或先在 AVP Play 完成签名设置。'))
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
