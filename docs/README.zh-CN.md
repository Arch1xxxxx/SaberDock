[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

SaberDock 是一款 Mac 曲库管理工具，用于整理 Beat Saber 自定义谱面，并将歌单同步到 Apple Vision Pro。它面向已购买游戏、希望在自己拥有的头显上游玩自定义内容的用户。

使用前需先通过 [AVP Play](https://github.com/myMartek/avp-play) 准备游戏。SaberDock 复用其本机生成的游戏应用，不登录 Meta、不下载或分发游戏，也不提供未购买游戏或付费曲包的访问权限。本项目独立维护，并非 AVP Play 官方项目。

**安装或更新前，请准备至少两个非空歌单，每个歌单至少包含一份受支持的谱面。目前只有一个歌单时，头显应用无法进入主菜单；空文件夹不计入歌单数量。**

## 使用前须知：游戏许可与平台条款

SaberDock 会修改本地 Beat Saber 游戏资源，并复用 AVP Play 已经生成的 visionOS 应用。**[Beat Saber 最终用户许可协议](https://www.meta.com/legal/quest/beat-saber-end-user-license-agreement)第 4.2.5 条**对编辑、合并、分发、转译、逆向工程、反编译和反汇编游戏设有限制，具体范围以原协议为准。**第 6.1 条**规定，重大违约可能导致游戏使用许可被终止。

使用 SaberDock 可能与上述限制或相关商店、开发者服务条款冲突。购买游戏本身不代表获得上述用途的授权。本项目不保证这些用途获得官方许可，也不保证相关账户或服务不受限制。使用前请阅读适用于你的账户与所在地的现行条款。

## 可以做什么

- 拖入谱面 ZIP 或已解压的谱面文件夹，导入歌曲。
- 按 Mac 上的文件夹创建歌单，每个歌单对应头显中的一个曲包。
- 浏览歌曲封面、歌手、谱师与可用难度，在头显中保留受支持谱面的封面和配色。
- 删除、恢复和手动排列歌曲，也可按歌名、歌手或谱师排序。
- 为 Vision Pro 安装独立的自定义内容应用，一键更新曲库。
- 自定义头显应用名称，并在英文与简体中文界面间切换。

## 使用前准备

- 运行 macOS 14 或更新版本的 Apple Silicon Mac。
- 已安装 visionOS SDK 的 Xcode，并登录你自己的 Apple 开发账户；SDK 需与所用的 AVP Play 工具链兼容。
- 你自己的 Apple Vision Pro，已与 Xcode 配对并开启开发者模式。安装或同步时，请保持头显解锁，并与 Mac 连接同一网络。
- 足够的本机可用空间，用于处理歌曲、生成曲库和保存应用文件。

不需要 Quest 头显。游戏文件的准备步骤见下文。

## 先安装 AVP Play

**请先安装并配置 AVP Play，再使用 SaberDock 安装头显应用。** SaberDock 需要读取 AVP Play 已生成的 visionOS 游戏应用、APK、OBB 和游戏数据文件夹，不自行转译或重新构建游戏可执行程序。

1. 在 Mac 上安装 [AVP Play](https://github.com/myMartek/avp-play)，按其使用指引完成设置。
2. 连接拥有 **Beat Saber** 的 Meta 账户，按 AVP Play 的指引验证购买记录，并下载所选版本的游戏文件。
3. **使用所选 Toolchain，对该游戏版本至少完成一次构建**，再通过 AVP Play 安装到 Vision Pro，确认游戏能够正常启动。
4. 在本机保留生成的应用及对应游戏文件，供 SaberDock 自动读取。仅下载 APK 和 OBB，不足以完成后续的头显应用安装。

SaberDock 可以选择 AVP Play 本地文件夹中已有的游戏版本和 Toolchain，不强制限定游戏版本。理论上也可以尝试通过 AVP Play 获取的最新版本，但较新版本尚未全部验证，能否安装和游玩取决于 AVP Play 的构建支持及游戏资源兼容性。若较新版本不适用，可以选择经过 SaberDock 开发者测试的 **Beat Saber 1.40.8**。无论选择哪个版本，都需先完成上述构建步骤。

根据 AVP Play 公开的[账户与购买说明](https://github.com/myMartek/avp-play#your-accounts-and-your-data)，它使用用户自己的账户向 Meta 核实购买记录，并仅下载该账户已确认拥有的游戏文件。具体下载流程与使用条件请以 AVP Play 的文档为准。

## 在 Mac 上安装 SaberDock

1. 从 [Releases](https://github.com/Arch1xxxxx/SaberDock/releases) 下载 Apple Silicon 版 `.dmg`。
2. 打开后，将 **SaberDock** 拖到 **Applications（应用程序）** 快捷方式。
3. 从“应用程序”打开 SaberDock，然后推出磁盘映像。以后可在 macOS 应用库或 Spotlight 搜索 **SaberDock**。

应用使用本地签名，尚未经过 Apple 公证。如果 macOS 阻止首次启动，可在“系统设置 → 隐私与安全性”中使用针对此应用的“仍要打开”。也提供 ZIP 下载。

## 准备曲库

默认曲库位置为 `~/Music/SaberDock Library`。根目录下的每个直接子文件夹对应一个歌单，例如：

```text
~/Music/SaberDock Library/
├── Vol.1 - K-pop/
│   ├── song-one.zip
│   └── song-two/
└── Vol.2 - Japan/
    └── song-three.zip
```

使用 **New Playlist（新建曲包）** 创建歌单，再拖入谱面或点击 **Import Maps（导入谱面）**。也可在访达中将谱面放入对应的歌单文件夹；拖入整份分类文件夹会建立同名歌单。请确保至少两个歌单各有一份受支持的谱面，整理或删除歌曲后也要保留至少两个非空歌单。

### 谱面兼容范围

支持 Standard 标准双剑谱面。不支持必须依赖 Chroma、Noodle Extensions、Mapping Extensions 等 Quest 插件的谱面；可选插件效果不会导入。不支持音频偏移、Shuffle 或各难度采用不同 BPM 时间轴的谱面。

应用会在传输前检查谱面，并在报错中标出对应歌名。请先处理或移除不兼容的谱面，再安装或更新。

## 设置并安装到头显

1. 打开 **Installation Settings（安装设置）**，选择 **Game Version（游戏版本）** 和 **Toolchain Version（Toolchain 版本）**，再点击 **Save and Check（保存并检查）**。应用会自动定位对应文件，并读取 AVP Play 的签名设置。
2. 若列表中缺少版本，或提示缺少对应构建，请先回到 AVP Play 下载并完成该版本的构建，再点击 **Refresh List（刷新列表）**。
3. 确认曲库已准备好，并设置头显应用名称。默认名称为 **SaberDock Custom Songs**；该名称与默认曲库路径均使用英文，不随界面语言变化，也可以自行更改。
4. 保持头显解锁，选择你的 Vision Pro，点击 **Install（安装）**。SaberDock 会在本机准备并签名独立应用，再将应用与曲库传到头显。
5. 在头显打开 **SaberDock Custom Songs**，或你自行设置的名称。

SaberDock 的自定义内容应用与 AVP Play 原版游戏安装相互独立。签名有效期及设备访问权限取决于你的 Apple 开发账户。

若游戏文件缺少曲库处理所需的资源结构，操作会在修改头显前停止。更换所选游戏或 Toolchain 后，下次更新会完整同步所选程序和曲库。

## 日常管理与同步

- **查看源文件：** 点击歌曲旁的文件夹按钮，在访达中打开源谱面；ZIP 会在所在文件夹中被选中。
- **删除与恢复：** 垃圾桶按钮从当前歌单移除歌曲，恢复按钮撤销最近一次删除；其他歌单中的副本会保留。
- **调整顺序：** 使用上下箭头、拖动或 **Sort（排序）** 菜单排列歌曲，头显内使用曲包默认顺序即可。
- **同步曲库：** 点击 **Update Headset（一键更新头显）**，应用新增、删除和排序。
- **更改应用名：** 使用 **Rename Only（仅改名称）**，无需重新传输曲库。
- **仅在本机生成：** 使用 **Build Library Only（仅生成曲库）**，准备并校验曲库，不同步到头显。

备份整个曲库及其中的 `.beatsaber-library.json`，即可保留歌单和管理记录。

## 本地数据与隐私

谱面保留在你选择的曲库位置。已删除的单曲源文件存放在曲库内隐藏的 `.library-trash` 文件夹；多曲 ZIP 保留原文件，只从当前歌单排除选中的歌曲。

处理缓存、本机生成的头显应用、签名资料和成绩备份保存在：

```text
~/Library/Application Support/SaberDock/
```

SaberDock 读取 AVP Play 相关的本地下载、安装记录和工具链，不读取 Meta 登录凭据。请勿将生成的头显应用、游戏文件、签名凭据或 Application Support 文件夹上传或分享给任何第三方。

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

由 [Arch1xxxxx](https://github.com/Arch1xxxxx) 与 Codex 共同创建。

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
