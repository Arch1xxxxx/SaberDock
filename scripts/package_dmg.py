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
        run('/usr/bin/ditto', '--norsrc', '--noextattr', app, staging / app.name)
        run('/usr/bin/xattr', '-cr', staging / app.name)
        run('/usr/bin/codesign', '--verify', '--deep', '--strict', staging / app.name)
        (staging / 'Applications').symlink_to('/Applications')
        (staging / 'Install - 安装说明.txt').write_text(
            'Drag SaberDock into Applications, then launch it from Applications once.\n'
            'Search for SaberDock in the macOS app library or Spotlight. Eject this image after installation.\n'
            'The interface defaults to English. Choose English or 简体中文 in the toolbar.\n\n'
            '将 SaberDock 拖到 Applications（应用程序）文件夹，再从应用程序打开一次。\n'
            '之后可在 macOS 应用库及 Spotlight 搜索 SaberDock，安装后可推出此磁盘映像。\n'
            '默认使用英文界面，可在工具栏切换为简体中文。\n', encoding='utf-8')
        run('/usr/bin/hdiutil', 'create', '-ov', '-volname', 'SaberDock', '-srcfolder', staging,
            '-format', 'UDZO', '-fs', 'APFS', image)
    run('/usr/bin/hdiutil', 'verify', image)
    with tempfile.TemporaryDirectory(prefix='saberdock-dmg-verify-') as mount:
        run('/usr/bin/hdiutil', 'attach', image, '-readonly', '-nobrowse', '-mountpoint', mount)
        try:
            run('/usr/bin/codesign', '--verify', '--deep', '--strict', Path(mount) / app.name)
            assert (Path(mount) / 'Applications').resolve() == Path('/Applications')
        finally:
            run('/usr/bin/hdiutil', 'detach', mount)
    print('Built:', image)

if __name__ == '__main__':
    main()
