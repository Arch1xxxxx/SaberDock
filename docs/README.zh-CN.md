[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

用于在 Mac 上管理 Beat Saber 自定义谱面，并借助本机 AVP Play 为 Apple Vision Pro 安装和更新独立自定义内容应用。

**SaberDock 不包含、也不分发任何游戏、APK、OBB、付费曲包或由游戏生成的运行文件。本软件只是辅助工具，让你在已有的设备上游玩已拥有游戏的自定义内容。你需要通过自己的 AVP Play 安装提供自己拥有的游戏文件。**

**安装或更新前，必须准备至少两个歌单（曲包），且每个歌单至少包含一份受支持的谱面。目前仅有一个歌单时，头显应用无法进入主菜单；空文件夹不计入歌单数量。整理或删除歌曲后，也请保留至少两个非空歌单。**

## 可以做什么

- 拖入谱面 ZIP 或已解压的谱面文件夹，直接导入歌曲。
- 用 Mac 上的文件夹整理歌曲，每个文件夹对应头显中的一个曲包。
- 浏览歌曲封面、歌手、谱师与可用难度，在头显中保留受支持谱面的封面和配色。
- 删除、恢复和手动排列歌曲，也可按歌名、歌手或谱师排序。
- 为 Vision Pro 安装独立的自定义内容应用，一键更新头显曲库。
- 自定义头显应用名称，并在英文与简体中文界面间切换。

## 使用前准备

- Apple Silicon Mac，macOS 14 或更新版本。
- [AVP Play](https://github.com/myMartek/avp-play)、本机工具链，以及通过自己账户完整下载的 **Beat Saber 1.40.8 / versionCode 1716**（APK 与 OBB）。不支持 1.45 等其他版本。
- 已登录自己 Apple 开发账户的 Xcode，及与 AVP Play 工具链兼容的 visionOS SDK。请先通过 AVP Play 完成一次安装。
- 你自己的 Apple Vision Pro，已与 Xcode 配对并开启开发者模式，保持解锁，与 Mac 连接同一网络。
- 足够的本机空间，用于歌曲处理与生成曲库。

不需要 Quest 头显。SaberDock 不登录 Meta、不下载游戏、不解锁付费内容，也不从其他来源获取游戏文件。

## 在 Mac 上安装

1. 从 [Releases](https://github.com/Arch1xxxxx/SaberDock/releases) 下载 Apple Silicon 版 `.dmg`。
2. 打开后，将 **SaberDock** 拖到旁边的 **Applications（应用程序）** 快捷方式。
3. 从“应用程序”打开 SaberDock，然后推出磁盘映像。以后可在 macOS 应用库或 Spotlight 搜索 **SaberDock**。

应用使用本地签名，尚未经过 Apple 公证。如果 macOS 阻止首次启动，可在“系统设置 → 隐私与安全性”中使用针对此应用的“仍要打开”。也提供 ZIP 下载。

## 设置并安装到头显

1. 打开 **Installation Settings（安装设置）**，核对自动检测的 AVP Play 应用、数据目录、下载目录和你自己的 Apple 团队 ID，也可手动选择。团队 ID 还可在 Xcode → Settings → Accounts 中查看。
2. 创建至少两个歌单文件夹，每个文件夹放入至少一份受支持的谱面。默认曲库位置为 `~/Music/SaberDock Library`，默认头显应用名称为 **SaberDock Custom Songs**。无论界面选择哪种语言，这两个默认值都使用英文。可自行选择其他曲库位置和应用名称。
3. 保持头显解锁，选择你的 Vision Pro，点击 **Install（安装）**。SaberDock 在本机准备并签名独立应用，再安装应用并传输必要数据。
4. 在头显打开 **SaberDock Custom Songs**，或你自行设置的名称。

SaberDock 使用你的本地游戏文件和自己的签名账户，与 AVP Play 原版游戏安装相互独立。签名有效期及设备能力取决于你的 Apple 开发账户。

## 管理曲库

```text
~/Music/SaberDock Library/
├── Vol.1 - K-pop/
│   ├── song-one.zip
│   └── song-two/
└── Vol.2 - Japan/
    └── song-three.zip
```

曲库根目录下的每个直接子文件夹对应一个曲包。可以在访达中将谱面放入曲包文件夹、直接拖入应用，或使用 **Import Maps（导入谱面）**。拖入整份分类文件夹会建立同名曲包；使用 **New Playlist（新建曲包）** 可添加文件夹。

- 歌曲旁的文件夹按钮打开源谱面；ZIP 会在所在文件夹中被选中。
- 垃圾桶按钮从当前曲包移除歌曲，恢复按钮撤销最近一次删除；其他曲包中的副本会保留。
- 已删除的单曲源文件保存在隐藏的 `.library-trash` 文件夹。多曲 ZIP 保留原文件，只从当前曲包排除选中的歌曲。
- 使用上下箭头、拖动或 **Sort（排序）** 菜单排列歌曲。头显内请使用曲包默认顺序。
- 点击 **Update Headset（一键更新头显）** 应用新增、删除和排序；**Rename Only（仅改名称）** 无需传输曲库即可更改头显应用名。
- **Build Library Only（仅生成曲库）** 只在 Mac 上生成并校验曲库。

歌曲错误会标出对应歌名。请先处理或移除不兼容谱面再更新。备份整个曲库及其中的 `.beatsaber-library.json`，即可保留曲包和管理记录。

## 谱面兼容范围

支持 Standard 标准双剑谱面。不支持必须依赖 Chroma、Noodle Extensions、Mapping Extensions 等 Quest 插件的谱面；可选插件效果不会导入。不支持音频偏移、Shuffle 或各难度采用不同 BPM 时间轴的谱面。应用会在传输前检查并提示不兼容的歌曲。

## 本地数据与隐私

谱面保留在你选择的曲库位置。处理缓存、本机生成的头显应用、签名资料和成绩备份保存在：

```text
~/Library/Application Support/SaberDock/
```

SaberDock 读取 AVP Play 相关的本地下载、安装记录和工具链，不读取 Meta 登录凭据。请勿将生成的头显应用、游戏文件、签名凭据或 Application Support 文件夹上传到本仓库。

## 从源码构建

在已安装 Xcode 与 Python 3 的 Apple Silicon Mac 上运行：

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_app.py
```

构建会下载固定版本并核对校验和的便携 Python、Node 和锁定依赖。生成的 Mac 应用无需另装 Python 或 Node。DMG、ZIP 和 SHA-256 校验文件位于 `dist/`；发布包检查会排除游戏内容和个人签名资料。

## 创建者

由 [Arch1xxxxx](https://github.com/Arch1xxxxx) 与 Codex（AI 编程助手）共同创建。

## 所有权、商标与许可

感谢 [AVP Play](https://github.com/myMartek/avp-play)、[Klepton](https://github.com/shinyquagsire23/Klepton)、UnityPy 和 bsmap。

SaberDock 是独立社区工具，与 Meta、Beat Games、Apple、AVP Play、Klepton 没有隶属、认可或赞助关系。**文中提及的所有商标、产品名称、标志及其他标识均属于其各自的原所有人。** 使用这些名称仅为说明兼容产品和依赖，不主张拥有相关商标。

源码采用 [MIT License](../LICENSE)。依赖许可见 [第三方说明](../THIRD-PARTY.md)。
