[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

SaberDock 是一款 Mac 曲库管理工具，用于整理 Beat Saber 自定义谱面，并将歌单同步到 Apple Vision Pro。它面向已经购买游戏、希望在自己头显上游玩自定义内容的用户。

使用前，请先安装 [AVP Play](https://github.com/myMartek/avp-play)，连接拥有 Beat Saber 的 Meta 账户，并完成已购游戏在 Vision Pro 上的安装。根据 AVP Play 公开的[账户与购买说明](https://github.com/myMartek/avp-play#your-accounts-and-your-data)，它使用用户自己的账户向 Meta 核实购买记录，并仅下载该账户已确认拥有的游戏文件。其下载流程与使用条件请以 AVP Play 的文档为准。

SaberDock 在现有本地安装的基础上管理谱面，并准备独立的自定义内容应用；它不登录 Meta，也不下载游戏。SaberDock 不包含游戏内容，也不提供未购买游戏或付费曲包的访问权限。本项目独立维护，并非 AVP Play 官方项目。

**安装或更新前，必须准备至少两个歌单（曲包），且每个歌单至少包含一份受支持的谱面。目前仅有一个歌单时，头显应用无法进入主菜单；空文件夹不计入歌单数量。整理或删除歌曲后，也请保留至少两个非空歌单。**

## 使用前须知：游戏许可与平台条款

SaberDock 会修改本地 Beat Saber 游戏资源，并复用 AVP Play 已经生成的 visionOS 应用。**[Beat Saber 最终用户许可协议](https://www.meta.com/legal/quest/beat-saber-end-user-license-agreement)第 4.2.5 条**对编辑、合并、分发、转译、逆向工程、反编译和反汇编游戏设有限制，具体范围以原协议为准。**第 6.1 条**规定，重大违约可能导致游戏使用许可被终止。

使用 SaberDock 可能与上述限制或相关商店、开发者服务条款冲突。购买游戏本身不代表获得上述用途的授权。本项目不保证这些用途获得官方许可，也不保证相关账户或服务不受限制。使用前请阅读适用于你的账户与所在地的现行条款。

## 可以做什么

- 拖入谱面 ZIP 或已解压的谱面文件夹，直接导入歌曲。
- 用 Mac 上的文件夹整理歌曲，每个文件夹对应头显中的一个曲包。
- 浏览歌曲封面、歌手、谱师与可用难度，在头显中保留受支持谱面的封面和配色。
- 删除、恢复和手动排列歌曲，也可按歌名、歌手或谱师排序。
- 为 Vision Pro 安装独立的自定义内容应用，一键更新头显曲库。
- 自定义头显应用名称，并在英文与简体中文界面间切换。

## 使用前准备

- Apple Silicon Mac，macOS 14 或更新版本。
- **先安装并配置 [AVP Play](https://github.com/myMartek/avp-play)**，准备你已购买的 Beat Saber 并完成一次 Vision Pro 安装。请在本机保留生成的 visionOS 应用、APK、OBB 和游戏数据文件夹。SaberDock 不按游戏版本筛选；自定义曲库处理仍需要兼容的资源结构。
- 已登录自己 Apple 开发账户的 Xcode，及与 AVP Play 工具链兼容的 visionOS SDK。请先通过 AVP Play 完成一次安装。
- 你自己的 Apple Vision Pro，已与 Xcode 配对并开启开发者模式，保持解锁，与 Mac 连接同一网络。
- 足够的本机空间，用于歌曲处理与生成曲库。

不需要 Quest 头显。SaberDock 不登录 Meta、不下载游戏、不解锁付费内容，也不从其他来源获取游戏文件。

## 先安装 AVP Play

**使用 SaberDock 前，必须先安装并完成 AVP Play 的设置。**

1. 在 Mac 上安装 [AVP Play](https://github.com/myMartek/avp-play)，按其使用指引完成设置。
2. 在 AVP Play 中连接拥有 **Beat Saber** 的 Meta 账户，按其指引完成购买验证，并准备由 Meta 提供的游戏文件。
3. 先通过 AVP Play 完成一次游戏安装，确认游戏能在 Vision Pro 上启动，并保留 AVP Play 本机生成的应用与已下载游戏文件。SaberDock 复用你选择的现有构建，不自行转译游戏或重新构建游戏可执行程序；若缺少应用，请先返回 AVP Play 完成安装，再按下文安装 SaberDock。

## 在 Mac 上安装 SaberDock

1. 从 [Releases](https://github.com/Arch1xxxxx/SaberDock/releases) 下载 Apple Silicon 版 `.dmg`。
2. 打开后，将 **SaberDock** 拖到旁边的 **Applications（应用程序）** 快捷方式。
3. 从“应用程序”打开 SaberDock，然后推出磁盘映像。以后可在 macOS 应用库或 Spotlight 搜索 **SaberDock**。

应用使用本地签名，尚未经过 Apple 公证。如果 macOS 阻止首次启动，可在“系统设置 → 隐私与安全性”中使用针对此应用的“仍要打开”。也提供 ZIP 下载。

## 设置并安装到头显

1. 打开 **Installation Settings（安装设置）**，选择本地的 **Vision Pro App（头显游戏应用 .app）**、**Game APK（游戏 APK）**、**Game OBB（游戏 OBB）** 和 **Game Data（游戏数据文件夹）**。应用应为给 Vision Pro 生成的游戏，不是 Mac 上的 AVP Play.app。游戏数据文件夹须包含 `assets` 和 `AndroidManifest.xml`，SaberDock 会尝试从所选应用旁自动定位。可选用自动查找，也可选择其他位置的文件。填写自己的 Apple 团队 ID，再点击 **Save and Check（保存并检查）**。团队 ID 可在 Xcode → Settings → Accounts 中查看。
2. 创建至少两个歌单文件夹，每个文件夹放入至少一份受支持的谱面。默认曲库位置为 `~/Music/SaberDock Library`，默认头显应用名称为 **SaberDock Custom Songs**。无论界面选择哪种语言，这两个默认值都使用英文。可自行选择其他曲库位置和应用名称。
3. 保持头显解锁，选择你的 Vision Pro，点击 **Install（安装）**。SaberDock 在本机准备并签名独立应用，再安装应用并传输必要数据。
4. 在头显打开 **SaberDock Custom Songs**，或你自行设置的名称。

SaberDock 使用通过 AVP Play 从 Meta 下载的游戏文件和你自己的签名账户，与 AVP Play 原版游戏安装相互独立。签名有效期及设备能力取决于你的 Apple 开发账户。

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

## 游戏文件与版本

游戏版本名和内部版本编号不会阻止安装。缺少文件时会给出具体错误，安装按钮不会因自动识别失败而一直禁用。请选择同一次本地游戏安装中的文件。不限制版本不代表所有版本都已验证：如果所选文件缺少转换器需要的资源结构，会在修改头显前停止处理。更换游戏应用或程序数据后，下次更新会完整同步所选程序和曲库。

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

## 问题反馈

SaberDock 的安装、曲库或同步问题，请提交到 [SaberDock 的问题反馈页面](https://github.com/Arch1xxxxx/SaberDock/issues)。本集成由 SaberDock 维护，不应要求 AVP Play 或 Klepton 的维护者为其提供支持。如果问题在单独使用 AVP Play 时也能复现，请遵循其贡献与问题反馈指引。

## 创建者

由 [Arch1xxxxx](https://github.com/Arch1xxxxx) 与 Codex（AI 编程助手）共同创建。

## 致谢

感谢 [AVP Play](https://github.com/myMartek/avp-play) 及其贡献者提供 SaberDock 所依赖的游戏安装流程；感谢 Max Thomas 创建的 [Klepton](https://github.com/shinyquagsire23/Klepton)，为游戏转译工具链奠定基础。

感谢 UnityPy 与 bsmap 提供游戏资源格式读取和谱面处理工具。AVP Play 工具链涉及的其他贡献者与上游项目，请参阅其[致谢](https://github.com/myMartek/avp-play#thanks)。这些署名用于说明项目依赖和贡献来源，不表示上游项目认可或担保 SaberDock。AVP Play 的项目定位和使用条件请以其[法律声明](https://github.com/myMartek/avp-play#legal)为准。

## 使用范围、内容权利与法律声明

SaberDock 仅用于管理已购 Beat Saber 的自定义内容，并在用户自己拥有的设备上使用。项目不提供游戏 APK、OBB、付费曲包、由游戏生成的运行文件或商业歌曲，也不提供游戏破解、绕过购买验证或解锁未购内容的功能。游戏购买验证和文件获取仍由前述 Meta 与 AVP Play 流程处理，SaberDock 不自行执行 Meta 账户验证。

购买游戏不等于获得分发其文件的权利。游戏代码、音乐、谱面、图片等内容的权利仍归各自权利人所有。请仅导入你有权使用的自定义谱面和其他内容；SaberDock 的源码许可不授予任何游戏或第三方内容的使用、复制或分发权。

用户需自行确认使用方式是否符合适用法律，以及相关游戏、商店和开发者服务的条款。本项目不承诺将已购游戏用于其他设备的所有方式都获得相关条款允许。

SaberDock 是独立社区项目，与 Apple、Meta、Beat Games、AVP Play、Klepton 没有隶属、认可或赞助关系。Apple Vision Pro、Meta Quest、Beat Saber，以及文中其他产品名称、标志和商标，均属于其各自所有人。使用这些名称仅为说明兼容产品与致谢上游依赖。

## 许可

SaberDock 源码采用 [MIT License](../LICENSE)，包括其中的不提供担保条款。依赖许可和声明见 [THIRD-PARTY.md](../THIRD-PARTY.md)。该许可适用于本项目代码，不包含用户提供的游戏或其他内容。
