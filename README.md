[English](#saberdock) · [简体中文](#saberdock-1)

# SaberDock

SaberDock is a Mac companion for organizing custom Beat Saber maps and syncing your playlists to Apple Vision Pro. It is intended for playing custom content for a game you have purchased, on a headset you own.

Start with [AVP Play](https://github.com/myMartek/avp-play): install it, connect the Meta account that owns Beat Saber, and prepare your purchased game for Vision Pro. AVP Play's [account and ownership guidance](https://github.com/myMartek/avp-play#your-accounts-and-your-data) explains that it checks purchases with Meta and obtains only the game files confirmed for that account. Those files come from Meta, not from SaberDock or AVP Play's project repository.

SaberDock then works with that existing local installation to organize maps and prepare a separate custom-content app. It does not sign in to Meta or download games. Neither SaberDock nor AVP Play distributes game copies or provides access to games or paid packs you have not purchased.

**Before installing or updating, add at least two playlists, each containing at least one supported map. The headset app currently cannot reach the main menu with only one playlist; empty folders do not count. Keep at least two nonempty playlists when reorganizing or deleting songs.**

## What you can do

- Import map ZIP files or extracted map folders by dragging them into the app.
- Organize songs into playlists using folders on your Mac.
- Browse song covers, artists, mappers, and available difficulties, with supported map covers and colors preserved on the headset.
- Delete and restore songs, arrange them manually, or sort by title, artist, or mapper.
- Install a separate custom-content app on Vision Pro and update its library with one button.
- Choose your headset app name and switch between English and Simplified Chinese.

## Requirements

- An Apple Silicon Mac running macOS 14 or later.
- **Install and configure [AVP Play](https://github.com/myMartek/avp-play) first.** Use the Meta account that owns Beat Saber to prepare **Beat Saber 1.40.8 / version code 1716** and its local toolchain through AVP Play. Other versions, including 1.45, are not supported.
- Xcode with a visionOS SDK compatible with your AVP Play toolchain, signed in to your own Apple development account. Complete an AVP Play installation first.
- Your Apple Vision Pro paired with Xcode, with Developer Mode enabled, unlocked, and connected to the same network as the Mac.
- Free space for local processing and the generated library.

A Quest headset is not required. SaberDock does not sign in to Meta, download games, unlock purchases, or obtain game files from third-party sources.

## Install AVP Play first

**AVP Play must be installed and set up before you use SaberDock.**

1. Install [AVP Play](https://github.com/myMartek/avp-play) on your Mac and follow its setup guide.
2. In AVP Play, connect the Meta account that owns **Beat Saber 1.40.8 (1716)**. Follow AVP Play's guide to verify your purchase and prepare the game files supplied by Meta.
3. Complete a game installation with AVP Play and confirm it can launch on your Vision Pro. Then install SaberDock below.

## Install SaberDock on your Mac

1. Download the Apple Silicon `.dmg` from [Releases](https://github.com/Arch1xxxxx/SaberDock/releases).
2. Open it and drag **SaberDock** to the **Applications** shortcut.
3. Open SaberDock from Applications, then eject the disk image. Search for **SaberDock** in the macOS app library or Spotlight to open it later.

The app is locally signed and is not notarized by Apple. If macOS blocks the first launch, use the app-specific Open Anyway option in System Settings → Privacy & Security. A ZIP download is also available.

## Set up and install on your headset

1. Open **Installation Settings**. Check the detected AVP Play app, data folder, downloads folder, and your Apple Team ID. You can choose paths manually. The team ID is also available in Xcode → Settings → Accounts.
2. Create at least two playlist folders and add at least one supported map to each. The default location is `~/Music/SaberDock Library`; the default headset app name is **SaberDock Custom Songs**. These defaults stay in English regardless of interface language. You can choose a different library location and app name.
3. Keep the headset unlocked, select your Vision Pro, and click **Install**. SaberDock prepares and signs the separate app locally, then installs the app and required data on your headset.
4. Open **SaberDock Custom Songs**, or the name you chose, on the headset.

SaberDock uses the game files downloaded from Meta through AVP Play and your own signing account. The original AVP Play game installation remains separate. Signing validity and device access depend on your Apple development account.

## Organize your library

```text
~/Music/SaberDock Library/
├── Vol.1 - K-pop/
│   ├── song-one.zip
│   └── song-two/
└── Vol.2 - Japan/
    └── song-three.zip
```

Each immediate subfolder is a playlist. Drop maps into a playlist folder in Finder, drag them into the app, or use **Import Maps**. Dropping a category folder creates a playlist with that folder's name. Use **New Playlist** to create another folder.

- The folder button beside a song opens its source in Finder; ZIP files are selected in their containing folder.
- The trash button removes a song from the selected playlist. The restore button undoes the most recent deletion. Copies in other playlists are kept.
- Removed single-map sources are stored in the hidden `.library-trash` folder. Multi-map ZIPs stay intact; the selected song is excluded from that playlist.
- Use the arrows, drag to reorder, or choose a **Sort** option. Select the playlist's default order in the headset game.
- Click **Update Headset** to apply additions, deletions, and ordering. Use **Rename Only** to change the headset app name without transferring the library.
- **Build Library Only** prepares and verifies the library on the Mac without syncing.

Map errors identify the affected song. Resolve or remove unsupported maps before updating. Back up your whole library, including `.beatsaber-library.json`, to retain playlists and management records.

## Supported maps

Standard two-saber maps are supported. Required Quest mods such as Chroma, Noodle Extensions, and Mapping Extensions are not supported. Optional mod effects are omitted. Audio offsets, Shuffle, and different BPM timelines between difficulties are not supported. The app checks maps before transfer and reports incompatible songs.

## Local data and privacy

Library files remain where you choose. Processing caches, locally generated headset apps, provisioning data, and score backups are stored on your Mac in:

```text
~/Library/Application Support/SaberDock/
```

SaberDock reads AVP Play's relevant local downloads, installation records, and toolchain; it does not read Meta login credentials. Do not upload generated headset apps, game files, signing credentials, or your Application Support folder to this repository.

## Build from source

On an Apple Silicon Mac with Xcode and Python 3:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_app.py
```

The build downloads checksum-pinned portable Python and Node runtimes and locked dependencies. The resulting Mac app does not require a separate Python or Node installation. DMG, ZIP, and SHA-256 checksums are written to `dist/`. The package audit excludes game content and personal signing materials.

## Creators

Created by [Arch1xxxxx](https://github.com/Arch1xxxxx) and Codex (AI coding assistant).

## Acknowledgments

Thank you to [AVP Play](https://github.com/myMartek/avp-play) and its contributors for the installation workflow on which SaberDock relies, and to Max Thomas for [Klepton](https://github.com/shinyquagsire23/Klepton), the foundation of the game translation toolchain.

Thank you to UnityPy and bsmap for the tools used to read game resource formats and work with beatmaps. For the contributors and projects behind AVP Play's toolchain, see its own [acknowledgments](https://github.com/myMartek/avp-play#thanks). These credits recognize upstream work; they do not imply endorsement of SaberDock. AVP Play's own scope and conditions are set out in its [legal notice](https://github.com/myMartek/avp-play#legal).

## Use, ownership, and legal notice

SaberDock is for managing custom content for a copy of Beat Saber you have purchased, on hardware you own. It supplies no game APKs, OBBs, paid music packs, game-derived runtimes, or commercial songs. It does not provide game cracks, purchase-check bypasses, or a way to unlock unpurchased content. Purchase verification and access to your game files remain part of the Meta and AVP Play workflow described above; SaberDock does not perform its own Meta account verification.

Buying a game does not grant permission to redistribute its files. Game code, music, maps, artwork, and other content remain subject to their owners' rights. Import custom maps and other content only when you have permission to use them. SaberDock's source-code license does not grant rights to any game or third-party content.

You are responsible for checking whether your intended use complies with applicable law and the terms of the relevant games, stores, and developer services. This project does not promise that every use of a purchased game on another device is permitted by those terms.

SaberDock is an independent community project. It is not affiliated with, endorsed by, or sponsored by Apple, Meta, Beat Games, AVP Play, or Klepton. Apple Vision Pro, Meta Quest, Beat Saber, and all other product names, logos, and trademarks mentioned belong to their respective owners. They are used only to identify compatible products and acknowledge dependencies.

## License

SaberDock's source code is available under the [MIT License](LICENSE), including its warranty disclaimer. Dependency licenses and notices are listed in [THIRD-PARTY.md](THIRD-PARTY.md). This license covers the project code, not the game or content you provide.

---

# SaberDock

SaberDock 是一款 Mac 曲库管理工具，用于整理 Beat Saber 自定义谱面，并将歌单同步到 Apple Vision Pro。它面向已经购买游戏、希望在自己头显上游玩自定义内容的用户。

使用前，请先安装 [AVP Play](https://github.com/myMartek/avp-play)，连接拥有 Beat Saber 的 Meta 账户，并完成已购游戏在 Vision Pro 上的安装。AVP Play 的[账户与购买说明](https://github.com/myMartek/avp-play#your-accounts-and-your-data)明确：它会向 Meta 核实账户的购买记录，仅获取该账户已确认拥有的游戏文件。游戏文件来自 Meta，而非 SaberDock 或 AVP Play 的项目仓库。

SaberDock 在现有本地安装的基础上管理谱面，并准备独立的自定义内容应用；它不登录 Meta，也不下载游戏。SaberDock 与 AVP Play 均不分发游戏副本，不提供未购买游戏或付费曲包的访问权限。

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
- **先安装并配置 [AVP Play](https://github.com/myMartek/avp-play)**，使用拥有 Beat Saber 的 Meta 账户，按 AVP Play 的指引准备已购 **Beat Saber 1.40.8 / versionCode 1716** 与本机工具链。不支持 1.45 等其他版本。
- 已登录自己 Apple 开发账户的 Xcode，及与 AVP Play 工具链兼容的 visionOS SDK。请先通过 AVP Play 完成一次安装。
- 你自己的 Apple Vision Pro，已与 Xcode 配对并开启开发者模式，保持解锁，与 Mac 连接同一网络。
- 足够的本机空间，用于歌曲处理与生成曲库。

不需要 Quest 头显。SaberDock 不登录 Meta、不下载游戏、不解锁付费内容，也不从其他来源获取游戏文件。

## 先安装 AVP Play

**使用 SaberDock 前，必须先安装并完成 AVP Play 的设置。**

1. 在 Mac 上安装 [AVP Play](https://github.com/myMartek/avp-play)，按其使用指引完成设置。
2. 在 AVP Play 中连接拥有 **Beat Saber 1.40.8（1716）** 的 Meta 账户，按其指引完成购买验证，并准备由 Meta 提供的游戏文件。
3. 先通过 AVP Play 完成一次游戏安装，确认游戏能在 Vision Pro 上启动，再按下文安装 SaberDock。

## 在 Mac 上安装 SaberDock

1. 从 [Releases](https://github.com/Arch1xxxxx/SaberDock/releases) 下载 Apple Silicon 版 `.dmg`。
2. 打开后，将 **SaberDock** 拖到旁边的 **Applications（应用程序）** 快捷方式。
3. 从“应用程序”打开 SaberDock，然后推出磁盘映像。以后可在 macOS 应用库或 Spotlight 搜索 **SaberDock**。

应用使用本地签名，尚未经过 Apple 公证。如果 macOS 阻止首次启动，可在“系统设置 → 隐私与安全性”中使用针对此应用的“仍要打开”。也提供 ZIP 下载。

## 设置并安装到头显

1. 打开 **Installation Settings（安装设置）**，核对自动检测的 AVP Play 应用、数据目录、下载目录和你自己的 Apple 团队 ID，也可手动选择。团队 ID 还可在 Xcode → Settings → Accounts 中查看。
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

## 致谢

感谢 [AVP Play](https://github.com/myMartek/avp-play) 及其贡献者提供 SaberDock 所依赖的游戏安装流程；感谢 Max Thomas 创建的 [Klepton](https://github.com/shinyquagsire23/Klepton)，为游戏转译工具链奠定基础。

感谢 UnityPy 与 bsmap 提供游戏资源格式读取和谱面处理工具。AVP Play 工具链涉及的其他贡献者与上游项目，请参阅其[致谢](https://github.com/myMartek/avp-play#thanks)。这些署名用于说明项目依赖和贡献来源，不表示上游项目认可或担保 SaberDock。AVP Play 的项目定位和使用条件请以其[法律声明](https://github.com/myMartek/avp-play#legal)为准。

## 使用范围、内容权利与法律声明

SaberDock 仅用于管理已购 Beat Saber 的自定义内容，并在用户自己拥有的设备上使用。项目不提供游戏 APK、OBB、付费曲包、由游戏生成的运行文件或商业歌曲，也不提供游戏破解、绕过购买验证或解锁未购内容的功能。游戏购买验证和文件获取仍由前述 Meta 与 AVP Play 流程处理，SaberDock 不自行执行 Meta 账户验证。

购买游戏不等于获得分发其文件的权利。游戏代码、音乐、谱面、图片等内容的权利仍归各自权利人所有。请仅导入你有权使用的自定义谱面和其他内容；SaberDock 的源码许可不授予任何游戏或第三方内容的使用、复制或分发权。

用户需自行确认使用方式是否符合适用法律，以及相关游戏、商店和开发者服务的条款。本项目不承诺将已购游戏用于其他设备的所有方式都获得相关条款允许。

SaberDock 是独立社区项目，与 Apple、Meta、Beat Games、AVP Play、Klepton 没有隶属、认可或赞助关系。Apple Vision Pro、Meta Quest、Beat Saber，以及文中其他产品名称、标志和商标，均属于其各自所有人。使用这些名称仅为说明兼容产品与致谢上游依赖。

## 许可

SaberDock 源码采用 [MIT License](LICENSE)，包括其中的不提供担保条款。依赖许可和声明见 [THIRD-PARTY.md](THIRD-PARTY.md)。该许可适用于本项目代码，不包含用户提供的游戏或其他内容。
