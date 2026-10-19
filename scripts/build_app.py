#!/usr/bin/env python3
"""Build a portable Apple Silicon app using pinned, verified open-source runtimes."""
import argparse,hashlib,json,os,plistlib,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BUILD=ROOT/'.build';DIST=ROOT/'dist';VERSION='1.0.0'
def run(args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
def download(item):
 target=BUILD/Path(item['url']).name
 if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:
  run(['/usr/bin/curl','--fail','--location','--retry','3',item['url'],'--output',target])
 if hashlib.sha256(target.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Runtime SHA-256 mismatch: '+target.name)
 return target

def main():
 p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');p.add_argument('--skip-dependencies',action='store_true');a=p.parse_args()
 if sys.platform!='darwin' or os.uname().machine!='arm64':raise SystemExit('Build on an Apple Silicon Mac with Xcode.')
 BUILD.mkdir(exist_ok=True);DIST.mkdir(exist_ok=True);lock=json.loads((ROOT/'scripts/runtime-lock.json').read_text())
 for kind,folder in [('python','python'),('node','node')]:
  marker=BUILD/(kind+'.sha256')
  if not marker.exists() or marker.read_text()!=lock[kind]['sha256']:
   tar=download(lock[kind]);destination=BUILD/(kind+'-extract');shutil.rmtree(destination,ignore_errors=True);destination.mkdir()
   run(['/usr/bin/tar','-xf',tar,'-C',destination]);source=next(destination.iterdir());target=BUILD/folder;shutil.rmtree(target,ignore_errors=True);source.rename(target);destination.rmdir();marker.write_text(lock[kind]['sha256'])
 python=BUILD/'python/bin/python3';node=BUILD/'node/bin/node';npm=BUILD/'node/lib/node_modules/npm/bin/npm-cli.js'
 env=dict(os.environ);env['PATH']=str(BUILD/'node/bin')+':'+str(BUILD/'python/bin')+':'+env.get('PATH','')
 if not (ROOT/'package-lock.json').exists():run([node,npm,'install','--package-lock-only','--ignore-scripts'],cwd=ROOT,env=env)
 if a.prepare_only:return
 staging=Path(tempfile.mkdtemp(prefix='saberdock-app-'));app=staging/'SaberDock.app';(BUILD/'staged-app.txt').write_text(str(app));res=app/'Contents/Resources';mac=app/'Contents/MacOS';res.mkdir(parents=True,exist_ok=True);mac.mkdir(parents=True,exist_ok=True)
 shutil.copytree(BUILD/'python',res/'runtime',symlinks=True);shutil.copy2(node,res/'runtime/bin/node')
 if not a.skip_dependencies or not (BUILD/'python-libs').exists():
  libs=BUILD/'python-libs';shutil.rmtree(libs,ignore_errors=True)
  run([python,'-m','pip','install','--no-deps','--target',libs,'-r',ROOT/'requirements.txt'],env=env)
  run([python,ROOT/'scripts/patch_unitypy.py',libs])
  run([node,npm,'ci','--ignore-scripts','--omit=dev'],cwd=ROOT,env=env)
 shutil.copytree(BUILD/'python-libs',res/'python-libs',symlinks=True);shutil.copytree(ROOT/'node_modules',res/'node_modules',symlinks=True)
 run([python,ROOT/'scripts/dependency_inventory.py',res/'python-libs',res/'DEPENDENCIES.json'])
 for name in ['backend.py','integration.py','build.py','convert.cjs','i18n.py','i18n.cjs','messages.json','SigningProject.pbxproj']:shutil.copy2(ROOT/'src'/name,res/name)
 shutil.copy2(ROOT/'LICENSE',res/'LICENSE');shutil.copy2(ROOT/'THIRD-PARTY.md',res/'THIRD-PARTY.md')
 notices=res/'licenses';notices.mkdir(exist_ok=True)
 for name in ['LICENSE','LICENSE.txt','LICENSE.rst','COPYING','COPYING.txt']:
  file=BUILD/'node'/name
  if file.exists():shutil.copy2(file,notices/('Node-'+name))
 info={'CFBundleIdentifier':'io.saberdock.mac','CFBundleName':'SaberDock','CFBundleDisplayName':'SaberDock','CFBundleExecutable':'SaberDock','CFBundlePackageType':'APPL','CFBundleShortVersionString':VERSION,'CFBundleVersion':'100','CFBundleDevelopmentRegion':'en','CFBundleLocalizations':['en','zh-Hans'],'LSApplicationCategoryType':'public.app-category.music','LSMinimumSystemVersion':'14.0','NSHighResolutionCapable':True,'CFBundleIconFile':'AppIcon'}
 (app/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
 run(['/usr/bin/xcrun','swiftc','-swift-version','5','-parse-as-library','-O','-target','arm64-apple-macosx14.0','-module-cache-path',BUILD/'swift-cache','src/App.swift','-o',mac/'SaberDock'],cwd=ROOT)
 run(['/usr/bin/xcrun','swift',ROOT/'scripts/icon.swift',res/'AppIcon.icns'])
 # Keep distribution notices from Python and all wheel dist-info directories.
 for path in res.rglob('__pycache__'):shutil.rmtree(path,ignore_errors=True)
 run(['/usr/bin/xattr','-cr',app])
 run(['/usr/bin/codesign','--force','--deep','--sign','-',app]);run(['/usr/bin/codesign','--verify','--deep','--strict',app])
 run([python,ROOT/'scripts/audit_release.py',app])
 archive=DIST/('SaberDock-'+VERSION+'-macOS-arm64.zip');run(['/usr/bin/ditto','-c','-k','--keepParent',app,archive])
 run([python,ROOT/'scripts/package_dmg.py',app,DIST,VERSION])
 artifacts=[archive,DIST/('SaberDock-'+VERSION+'-macOS-arm64.dmg')]
 (DIST/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(item.read_bytes()).hexdigest()+'  '+item.name+'\n' for item in artifacts))
 print('Built:',archive)
if __name__=='__main__':main()
