[English](README.en.md) · [简体中文](README.zh-CN.md)

# SaberDock

A Mac app for organizing custom Beat Saber maps and updating a separate custom-content app on Apple Vision Pro using your local AVP Play installation.

**SaberDock does not include or distribute any game, APK, OBB, paid music pack, or game-derived runtime. It is a companion tool for playing custom content for games you already own on devices you already own. You must provide your own game files through your own AVP Play installation.**

## What you can do

- Import map ZIP files or extracted map folders by dragging them into the app.
- Organize songs into playlists using folders on your Mac.
- Browse song covers, artists, mappers, and available difficulties, with supported map covers and colors preserved on the headset.
- Delete and restore songs, arrange them manually, or sort by title, artist, or mapper.
- Install a separate custom-content app on Vision Pro and update its library with one button.
- Choose your headset app name and switch between English and Simplified Chinese.

## Requirements

- An Apple Silicon Mac running macOS 14 or later.
- [AVP Play](https://github.com/myMartek/avp-play), its local toolchain, and your own complete **Beat Saber 1.40.8 / version code 1716** download (APK and OBB). Other versions, including 1.45, are not supported.
- Xcode with a visionOS SDK compatible with your AVP Play toolchain, signed in to your own Apple development account. Complete an AVP Play installation first.
- Your Apple Vision Pro paired with Xcode, with Developer Mode enabled, unlocked, and connected to the same network as the Mac.
- Free space for local processing and the generated library.

A Quest headset is not required. SaberDock does not sign in to Meta, download games, unlock purchases, or obtain game files from third-party sources.

## Install on your Mac

1. Download the Apple Silicon `.dmg` from [Releases](https://github.com/Arch1xxxxx/SaberDock/releases).
2. Open it and drag **SaberDock** to the **Applications** shortcut.
3. Open SaberDock from Applications, then eject the disk image. Search for **SaberDock** in the macOS app library or Spotlight to open it later.

The app is locally signed and is not notarized by Apple. If macOS blocks the first launch, use the app-specific Open Anyway option in System Settings → Privacy & Security. A ZIP download is also available.

## Set up and install on your headset

1. Open **Installation Settings**. Check the detected AVP Play app, data folder, downloads folder, and your Apple Team ID. You can choose paths manually. The team ID is also available in Xcode → Settings → Accounts.
2. Add maps to your library. The default location is `~/Music/SaberDock Library`; the default headset app name is **SaberDock Custom Songs**. These defaults stay in English regardless of interface language. Existing library locations and custom names are retained.
3. Keep the headset unlocked, select your Vision Pro, and click **Install / Repair**. SaberDock prepares and signs the separate app locally, then installs the app and required data on your headset.
4. Open **SaberDock Custom Songs**, or the name you chose, on the headset.

SaberDock uses your local game files and your own signing account. The original AVP Play game installation remains separate. Signing validity and device access depend on your Apple development account.

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

## Ownership, trademarks, and license

Thanks to [AVP Play](https://github.com/myMartek/avp-play), [Klepton](https://github.com/shinyquagsire23/Klepton), UnityPy, and bsmap.

SaberDock is an independent community tool and is not affiliated with, endorsed by, or sponsored by Meta, Beat Games, Apple, AVP Play, or Klepton. **All trademarks, product names, logos, and other marks mentioned belong to their respective owners.** The names identify compatible products and dependencies; no ownership of those marks is claimed.

The source is licensed under the [MIT License](../LICENSE). See [third-party notices](../THIRD-PARTY.md) for dependency licenses.
