[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

SaberDock is a Mac companion for organizing custom Beat Saber maps and syncing playlists to Apple Vision Pro. It is intended for playing custom content for a game you have purchased, on a headset you own.

Prepare your game through [AVP Play](https://github.com/myMartek/avp-play) first. SaberDock reuses its locally generated game app; it does not sign in to Meta, download or distribute games, or provide access to unpurchased games or paid packs. It is independently maintained and is not an official AVP Play project.

**Before installing or updating, prepare at least two nonempty playlists, each containing at least one supported map. The headset app currently cannot reach the main menu with only one playlist; empty folders do not count.**

## Before you begin: game license and platform terms

SaberDock modifies local Beat Saber game assets and reuses the visionOS app already built by AVP Play. **Section 4.2.5 of the [Beat Saber End User License Agreement](https://www.meta.com/legal/quest/beat-saber-end-user-license-agreement)** sets restrictions on editing, merging, distributing, translating, reverse engineering, decompiling, and disassembling the game. Refer to the agreement for the full scope of these restrictions. **Section 6.1** permits termination of the game license for a material breach.

Using SaberDock may conflict with these restrictions or other applicable store and developer-service terms. Purchasing the game does not itself authorize these activities. This project does not guarantee official permission or protection from account or service restrictions. Review the current terms applicable to your account and location before proceeding.

## What you can do

- Import map ZIP files or extracted map folders by dragging them into the app.
- Create playlists using folders on your Mac, with each playlist becoming a pack on the headset.
- Browse song covers, artists, mappers, and available difficulties, with supported map covers and colors preserved on the headset.
- Delete and restore songs, arrange them manually, or sort by title, artist, or mapper.
- Install a separate custom-content app on Vision Pro and update its library with one button.
- Choose your headset app name and switch between English and Simplified Chinese.

## Requirements

- An Apple Silicon Mac running macOS 14 or later.
- Xcode with a visionOS SDK compatible with your AVP Play toolchain, signed in to your own Apple development account.
- Your own Apple Vision Pro, paired with Xcode and with Developer Mode enabled. Keep it unlocked and on the same network as your Mac during installation or syncing.
- Enough free space on your Mac to process songs, generate the library, and store app files.

A Quest headset is not required. Follow the next section to prepare your game files.

## Install AVP Play first

**Install and configure AVP Play before using SaberDock to install the headset app.** SaberDock needs the visionOS game app, APK, OBB, and game data folder already prepared by AVP Play. It does not translate or rebuild the game executable.

1. Install [AVP Play](https://github.com/myMartek/avp-play) on your Mac and follow its setup guide.
2. Connect the Meta account that owns **Beat Saber**. Follow AVP Play’s guide to verify your purchase and download the game version you choose.
3. **Complete at least one build of that game version with your chosen toolchain**, then install it on Vision Pro through AVP Play and confirm that it launches.
4. Keep the generated app and associated game files locally for SaberDock to read automatically. Downloading the APK and OBB alone is not enough for the subsequent headset app installation.

SaberDock lets you choose game versions and toolchains already present in AVP Play’s local folders, without requiring a particular game version. In principle, you can also try the latest version available through AVP Play. Newer versions are not all tested: successful installation and gameplay depend on AVP Play’s build support and game resource compatibility. If a newer version does not work, choose **Beat Saber 1.40.8**, which has been tested by the SaberDock developer. Whichever version you choose, complete the build steps above first.

According to AVP Play’s [published account and ownership guidance](https://github.com/myMartek/avp-play#your-accounts-and-your-data), it verifies purchases with Meta using your own account and downloads only the game files confirmed for that account. Refer to AVP Play’s documentation for its download workflow and conditions.

## Install SaberDock on your Mac

1. Download the Apple Silicon `.dmg` from [Releases](https://github.com/Arch1xxxxx/SaberDock/releases).
2. Open it and drag **SaberDock** to the **Applications** shortcut.
3. Open SaberDock from Applications, then eject the disk image. Search for **SaberDock** in the macOS app library or Spotlight to open it later.

The app is locally signed and is not notarized by Apple. If macOS blocks the first launch, use the app-specific Open Anyway option in System Settings → Privacy & Security. A ZIP download is also available.

## Prepare your library

The default library location is `~/Music/SaberDock Library`. Each immediate subfolder becomes a playlist, for example:

```text
~/Music/SaberDock Library/
├── Vol.1 - K-pop/
│   ├── song-one.zip
│   └── song-two/
└── Vol.2 - Japan/
    └── song-three.zip
```

Use **New Playlist** to create a playlist, then drag maps into it or click **Import Maps**. You can also place maps in the corresponding playlist folder in Finder. Dropping a category folder creates a playlist with that folder’s name. Prepare at least two playlists, each with at least one supported map, and keep at least two nonempty playlists when reorganizing or deleting songs.

### Supported maps

Standard two-saber maps are supported. Required Quest mods such as Chroma, Noodle Extensions, and Mapping Extensions are not supported; optional mod effects are omitted. Audio offsets, Shuffle, and different BPM timelines between difficulties are not supported.

The app checks maps before transfer and identifies the affected song in error messages. Resolve or remove incompatible maps before installing or updating.

## Set up and install on your headset

1. Open **Installation Settings**, choose **Game Version** and **Toolchain Version**, then click **Save and Check**. SaberDock locates the corresponding files and reads signing settings from AVP Play automatically.
2. If a version is missing from the list or its build is unavailable, return to AVP Play to download and build that version, then click **Refresh List**.
3. Confirm that your library is ready and choose a headset app name. The default is **SaberDock Custom Songs**. This name and the default library path stay in English regardless of interface language; you can change both.
4. Keep the headset unlocked, select your Vision Pro, and click **Install**. SaberDock prepares and signs the separate app locally, then transfers the app and library to the headset.
5. Open **SaberDock Custom Songs**, or the name you chose, on the headset.

The custom-content app is separate from the original AVP Play game installation. Signing validity and device access depend on your Apple development account.

If the game files lack the resource structure needed for library processing, the operation stops before changing the headset. Changing the selected game or toolchain causes the next update to sync the complete selected program and library.

## Manage and sync your library

- **Find source files:** Click the folder button beside a song to open its source in Finder. ZIP files are selected in their containing folder.
- **Delete and restore:** The trash button removes a song from the current playlist; the restore button undoes the most recent deletion. Copies in other playlists are kept.
- **Arrange songs:** Use the arrows, drag to reorder, or choose a **Sort** option. Use the playlist’s default order in the headset game.
- **Sync changes:** Click **Update Headset** to apply additions, deletions, and ordering.
- **Change the app name:** Use **Rename Only** without transferring the library again.
- **Build locally:** Use **Build Library Only** to prepare and verify the library without syncing to the headset.

Back up your entire library, including `.beatsaber-library.json`, to retain playlists and management records.

## Local data and privacy

Maps remain in your chosen library location. Removed single-map sources are stored in its hidden `.library-trash` folder. Multi-map ZIPs stay intact; the selected song is excluded from the current playlist.

Processing caches, locally generated headset apps, provisioning data, and score backups are stored on your Mac in:

```text
~/Library/Application Support/SaberDock/
```

SaberDock reads AVP Play’s relevant local downloads, installation records, and toolchain; it does not read Meta login credentials. Do not upload or share generated headset apps, game files, signing credentials, or your Application Support folder with any third party.

## Build from source

On an Apple Silicon Mac with Xcode and Python 3:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_app.py
```

The build downloads checksum-pinned portable Python and Node runtimes and locked dependencies. The resulting Mac app does not require a separate Python or Node installation. DMG, ZIP, and SHA-256 checksums are written to `dist/`. The package audit excludes game content and personal signing materials.

## Support

For problems with SaberDock installation, playlists, or syncing, open an issue in the [SaberDock issue tracker](https://github.com/Arch1xxxxx/SaberDock/issues). This integration is maintained by SaberDock; AVP Play and Klepton maintainers are not responsible for supporting it. If a problem also occurs when using AVP Play on its own, follow its contribution and issue-reporting guidance.

## Creators

Created by [Arch1xxxxx](https://github.com/Arch1xxxxx) and Codex.

## Acknowledgments

Thank you to [AVP Play](https://github.com/myMartek/avp-play) and its contributors for the installation workflow on which SaberDock relies, and to Max Thomas for [Klepton](https://github.com/shinyquagsire23/Klepton), the foundation of the game translation toolchain.

Thank you to UnityPy and bsmap for the tools used to read game resource formats and work with beatmaps. For the contributors and projects behind AVP Play's toolchain, see its own [acknowledgments](https://github.com/myMartek/avp-play#thanks). These credits recognize upstream work; they do not imply endorsement of SaberDock. AVP Play's own scope and conditions are set out in its [legal notice](https://github.com/myMartek/avp-play#legal).

## Use, ownership, and legal notice

SaberDock is for managing custom content for a copy of Beat Saber you have purchased, on hardware you own. It supplies no game APKs, OBBs, paid music packs, game-derived runtimes, or commercial songs. It does not provide game cracks, purchase-check bypasses, or a way to unlock unpurchased content. Purchase verification and access to your game files remain part of the Meta and AVP Play workflow described above; SaberDock does not perform its own Meta account verification.

Buying a game does not grant permission to redistribute its files. Game code, music, maps, artwork, and other content remain subject to their owners' rights. Import custom maps and other content only when you have permission to use them. SaberDock's source-code license does not grant rights to any game or third-party content.

You are responsible for checking whether your intended use complies with applicable law and the terms of the relevant games, stores, and developer services. This project does not promise that every use of a purchased game on another device is permitted by those terms.

SaberDock is an independent community project. It is not affiliated with, endorsed by, or sponsored by Apple, Meta, Beat Games, AVP Play, or Klepton. Apple Vision Pro, Meta Quest, Beat Saber, and all other product names, logos, and trademarks mentioned belong to their respective owners. They are used only to identify compatible products and acknowledge dependencies.

## License

SaberDock's source code is available under the [MIT License](../LICENSE), including its warranty disclaimer. Dependency licenses and notices are listed in [THIRD-PARTY.md](../THIRD-PARTY.md). This license covers the project code, not the game or content you provide.
