[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

SaberDock is a Mac companion for organizing custom Beat Saber maps and syncing your playlists to Apple Vision Pro. It is intended for playing custom content for a game you have purchased, on a headset you own.

Start with [AVP Play](https://github.com/myMartek/avp-play): install it, connect the Meta account that owns Beat Saber, and prepare your purchased game for Vision Pro. According to AVP Play's [published account and ownership guidance](https://github.com/myMartek/avp-play#your-accounts-and-your-data), it verifies purchases with Meta using your own account and downloads only the game files confirmed for that account. See AVP Play's documentation for its download workflow and conditions.

SaberDock then works with that existing local installation to organize maps and prepare a separate custom-content app. It does not sign in to Meta or download games. SaberDock includes no game content and provides no access to games or paid packs you have not purchased. It is independently maintained and is not an official AVP Play project.

**Before installing or updating, add at least two playlists, each containing at least one supported map. The headset app currently cannot reach the main menu with only one playlist; empty folders do not count. Keep at least two nonempty playlists when reorganizing or deleting songs.**

## Before you begin: game license and platform terms

SaberDock modifies local Beat Saber game assets and uses a third-party toolchain to prepare an app for Apple Vision Pro. **Section 4.2.5 of the [Beat Saber End User License Agreement](https://www.meta.com/legal/quest/beat-saber-end-user-license-agreement)** restricts editing, merging, distributing, translating, reverse engineering, decompiling, and disassembling the game, except as specifically permitted by the agreement, prior consent, or mandatory applicable law. **Section 6.1** permits termination of the game license for a material breach.

Using SaberDock may conflict with these restrictions or other applicable store and developer-service terms. Purchasing the game does not itself authorize these activities. This project does not guarantee official permission or protection from account or service restrictions. Review the current terms applicable to your account and location before proceeding.

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

## Support

For problems with SaberDock installation, playlists, or syncing, open an issue in the [SaberDock issue tracker](https://github.com/Arch1xxxxx/SaberDock/issues). This integration is maintained by SaberDock; AVP Play and Klepton maintainers are not responsible for supporting it. If a problem also occurs when using AVP Play on its own, follow its contribution and issue-reporting guidance.

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

SaberDock's source code is available under the [MIT License](../LICENSE), including its warranty disclaimer. Dependency licenses and notices are listed in [THIRD-PARTY.md](../THIRD-PARTY.md). This license covers the project code, not the game or content you provide.
