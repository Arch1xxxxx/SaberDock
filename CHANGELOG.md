# Changelog

## 0.1.2

- Publish a read-only DMG with the SaberDock app and an Applications shortcut for drag-to-install. Keep the ZIP alternative and include both checksums.
- Document installation in Applications and first launch so macOS can register the app for app-library and Spotlight searches.

## 0.1.1

- Fix the independently built visionOS application exiting before its launch screen appears. Xcode Debug builds can place `Klepton.debug.dylib` and `__preview.dylib` beside the main executable; these libraries need their own development signature.
- Sign every embedded Mach-O before signing the outer application, and verify loose libraries explicitly. A successful outer `codesign --verify --deep` alone is insufficient for this layout.
- Add regression checks covering debug/preview dylibs, framework signing order and failed embedded-code verification.

Already affected installations can update the Mac tool and use “仅改名称” with the existing name to replace just the signed app. This keeps the installed library in place. “首次安装 / 修复” also applies the fix but retransfers first-run assets.

## 0.1.0

Initial private preview: AVP Play 1.40.8 local-file discovery, isolated runtime preparation, own-account signing, custom playlist building, library management and incremental processing.
