#!/usr/bin/env python3
"""Fail packaging if local game content or signing materials enter a public app."""
from pathlib import Path
import json,plistlib,re,sys

def audit(app):
 app=Path(app);resources=app/'Contents/Resources';allowed={'runtime','python-libs','node_modules','licenses','LICENSE','THIRD-PARTY.md','DEPENDENCIES.json','AppIcon.icns','backend.py','integration.py','build.py','convert.cjs','i18n.py','i18n.cjs','messages.json','SigningProject.pbxproj'}
 unexpected={p.name for p in resources.iterdir()}-allowed
 if unexpected:raise ValueError('Unexpected release resources: '+', '.join(sorted(unexpected)))
 for path in app.rglob('*'):
  if path.suffix.lower() in {'.apk','.obb','.mobileprovision','.p12','.cer'}:raise ValueError('Private/game file in release: '+str(path.relative_to(app)))
  if 'fmod' in path.name.lower():raise ValueError('Proprietary FMOD dependency in release: '+str(path.relative_to(app)))
  if path.is_file() and path.suffix in {'.py','.swift','.json','.pbxproj','.plist'} and path.stat().st_size<2_000_000:
   text=path.read_text(errors='replace')
   if re.search(r'/Users/[^/]+/(?:Documents/Codex|\.codex)/',text):raise ValueError('Personal development path in release: '+str(path.relative_to(app)))
 info=plistlib.loads((app/'Contents/Info.plist').read_bytes())
 assert info['CFBundleIdentifier']=='io.saberdock.mac'
 print('Release audit passed: no game content, personal profiles, or private development paths.')
if __name__=='__main__':audit(sys.argv[1])
