# SaberDock

**为 Apple Vision Pro 安装和管理 Beat Saber 自定义曲库的 Mac 应用。**

复用你本机 **AVP Play 已下载的 Beat Saber 1.40.8**，以你自己的 Apple 开发签名生成独立应用。把谱面拖进文件夹，每个文件夹就是一个曲包，再一键更新到头显。

> 首个公开预览版。当前仅支持 Beat Saber **1.40.8 / versionCode 1716**，不支持 1.45。运行库独立构建、首次签名和安装流程仍需要更多不同账户、工具链和设备的实测。

## 功能

- 自动识别 AVP Play 的本地下载与外置硬盘位置，也可手动选择。
- 核对 APK 与资源版本；当前 AVP Play 构建属于其他版本时，在独立目录重新准备 1.40.8。
- 首次安装／修复独立头显应用，使用你自己的 Apple 开发团队；不替换 AVP Play 安装的原版游戏。
- ZIP 与已解压谱面导入；文件夹生成曲包；封面、作者方块配色和 Standard 双剑难度保留。
- 应用内删除、恢复和排序；按歌名、歌手或谱师排序。
- 首次建立处理缓存，之后只重新转换新增／修改的歌曲。曲库不变时跳过重复同步。
- 防破音处理；歌曲相关错误包含歌名和谱师；更新前备份成绩。

曲库有变化时，仍需向头显传输完整 OBB 资源文件；缓存优化的是歌曲转换、校验和无变化时的同步。

## 使用前准备

- Apple Silicon Mac，macOS 14 或更新版本。
- [AVP Play](https://github.com/myMartek/avp-play)，以及你通过自己账户下载的 Beat Saber **1.40.8（1716）APK + OBB**。已有 1.45 下载不会自动替代 1.40.8。
- 已登录自己的 Apple 开发账户的 Xcode，已安装 visionOS SDK。请使用与你的 AVP Play 工具链兼容的 Xcode。
- Vision Pro 已与 Xcode 配对、开启开发者模式、解锁，并与 Mac 在同一网络。
- 本机 AVP Play 已准备好 Klepton 工具链。首次独立准备可能需要数 GB 空间和数分钟构建时间。

**不需要 Quest 头显。SaberDock 不登录 Meta，也不下载、分享或解锁游戏及付费曲包。**

## 安装与首次使用

1. 从 [Releases](https://github.com/Arch1xxxxx/SaberDock/releases) 下载 `SaberDock-…-macOS-arm64.zip`，解压后拖到“应用程序”。公开预览包使用本地签名，尚未取得 Apple Developer ID 公证；首次打开时按 macOS 的“隐私与安全性”提示允许即可。
2. 打开“安装设置”。应用会检查 AVP Play 应用、数据、下载目录和最近使用的开发团队 ID；确认它们属于你自己的账户。
3. 选择曲库目录。默认是 `音乐/Beat Saber 曲库`。每个子文件夹对应一个曲包，放入 ZIP 或解压谱面即可。
4. 保持头显解锁，选择设备，点击“首次安装／修复”。谱面转换、资源校验和签名完成后才开始安装与传输。
5. 在头显手动打开独立的自定义歌曲应用。以后只需点击“一键更新头显”；改名可用“仅改名称”。

如果只检测到 1.45，请回到 AVP Play，确认自己的本地曲库中确实有 1.40.8 下载。SaberDock 不会从其他来源获取游戏。

```text
音乐/Beat Saber 曲库/
├── Vol.1 - K-pop/
│   ├── song-one.zip
│   └── song-two/
└── Vol.2 - Japan/
    └── song-three.zip
```

## 歌曲管理

- 歌曲旁的文件夹按钮打开源谱面；ZIP 会打开所在目录并选中原文件。
- 垃圾桶按钮只从当前曲包移除。顶部恢复按钮可连续恢复最近删除。
- 单独的谱面目录／单曲 ZIP 移到曲库中隐藏的 `.曲库回收站`；多曲 ZIP 保留原文件，只排除选中歌曲。
- 上下箭头、拖动或“排序”菜单保存当前顺序，新增歌曲追加在末尾。头显游戏请选择曲包的默认顺序。
- 删除和排序在下一次同步时应用到头显。连同 `.beatsaber-library.json` 备份整个曲库即可保存管理记录。

## 兼容范围

| 项目 | 当前状态 |
| --- | --- |
| Beat Saber 1.40.8 / 1716 | 支持的资源版本 |
| Beat Saber 1.45 等其他版本 | 拒绝混用，需要单独适配 |
| 标准双剑谱面 | 支持多个 Standard 难度；转换后校验 |
| Chroma、Noodle Extensions、Mapping Extensions 等必需插件 | 不支持，报出歌名并阻止同步 |
| 原谱面封面、方块配色 | 保留 |
| 音频偏移、Shuffle、各难度不同变速时间轴 | 暂不支持，会显示具体歌曲错误 |
| 删空曲库 | 可生成不含歌曲的自定义曲包；头显体验待更多实测 |
| Apple 开发签名 | 使用本机账户生成；有效期与能力取决于你的 Apple 开发账户 |

## 本地数据

SaberDock 只读取 AVP Play 的相关下载、安装记录和工具链，不读取其 Meta 登录凭据。临时 APK 解包、翻译代码、曲库资源、签名资料、处理缓存和成绩备份仅存于本机：

```text
~/Library/Application Support/SaberDock/
```

应用包和 GitHub 仓库不包含游戏 APK/OBB、游戏译码库、歌曲、封面、Apple 证书或描述文件。请勿把本机 Application Support 或生成的头显应用提交到仓库。

## 从源码构建

需要 Apple Silicon Mac、Xcode，以及可启动构建脚本的 Python 3。脚本会下载固定版本且核对 SHA-256 的便携 Python 和 Node，安装锁定依赖，构建独立 Mac 应用；成品不依赖开发机路径，也不需要用户另装 Python／Node。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_app.py
open dist/
```

结果在 `dist/`，包括 ZIP 和 SHA256SUMS；解压 ZIP 后打开应用。`scripts/audit_release.py` 检查游戏资源、个人描述文件等是否误入发布包。

GitHub Actions 会验证源码、构建 Mac 包并提供构建产物。推送到 main 后生成与该提交绑定的私测预览 Release，推送 `v…` 标签生成相应版本的预发布 Release；CI 不需要也不接收游戏文件或 Apple 签名凭据。仓库保持私有时，下载仅对有权限的协作者开放。

## 致谢与许可

感谢 [AVP Play](https://github.com/myMartek/avp-play)、[Klepton](https://github.com/shinyquagsire23/Klepton)、UnityPy 和 bsmap。SaberDock 是独立社区工具，与 Meta、Beat Games、Apple 及上述项目没有隶属关系。

SaberDock 源码采用 [MIT License](LICENSE)。依赖及其许可见 [THIRD-PARTY.md](THIRD-PARTY.md)。不会分发 FMOD SDK／运行库，音频使用自行生成并校验的未压缩 PCM。

English overview: [docs/README.en.md](docs/README.en.md).
