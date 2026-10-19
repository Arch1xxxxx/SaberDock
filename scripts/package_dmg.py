#!/usr/bin/env python3
"""Package a signed app in a read-only drag-to-install disk image."""
import subprocess
import sys
import tempfile
from pathlib import Path

def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)

def main():
    app, destination, version = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
    run('/usr/bin/codesign', '--verify', '--deep', '--strict', app)
    destination.mkdir(parents=True, exist_ok=True)
    image = destination / f'SaberDock-{version}-macOS-arm64.dmg'
    with tempfile.TemporaryDirectory(prefix='saberdock-dmg-') as folder:
        staging = Path(folder)
        run('/usr/bin/ditto', app, staging / app.name)
        (staging / 'Applications').symlink_to('/Applications')
        (staging / '安装说明 - Install.txt').write_text(
            '将 SaberDock 拖到 Applications（应用程序）文件夹，然后从应用程序打开一次。\n'
            '之后可在 macOS 应用库及 Spotlight 搜索 SaberDock 或 SaberDock 曲库。\n'
            '安装完成后可推出此磁盘映像。不要在磁盘映像内长期运行应用。\n\n'
            'Drag SaberDock into Applications, then launch it from Applications once.\n'
            'You can then find it in the macOS app library and Spotlight. Eject this image after installation.\n',
            encoding='utf-8')
        run('/usr/bin/hdiutil', 'create', '-ov', '-volname', 'SaberDock', '-srcfolder', staging,
            '-format', 'UDZO', '-fs', 'HFS+', image)
    run('/usr/bin/hdiutil', 'verify', image)
    print('Built:', image)

if __name__ == '__main__':
    main()
