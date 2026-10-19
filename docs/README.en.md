# SaberDock

A native Apple Silicon Mac library manager and custom Beat Saber installer for Apple Vision Pro, using files already downloaded by the user's own AVP Play installation.

The initial preview targets **Beat Saber 1.40.8, version code 1716 only**. It does not support 1.45 and will not combine game files from different versions. No Quest headset is required.

Features include folder-based playlists, ZIP import, per-map covers and colors, reversible deletion, persistent ordering, incremental conversion caches, named song errors, score backups, and an initial install/repair flow. A changed library still requires transferring a complete OBB.

Users need their own AVP Play downloads, Xcode with a compatible visionOS SDK, an Apple development account and a paired Vision Pro with Developer Mode enabled. The installer uses the user's own signing team. If AVP Play currently holds a different-version build, SaberDock prepares 1.40.8 in a separate local workspace without modifying AVP Play's copy.

No APK, OBB, translated game code, songs, covers, credentials, provisioning profiles, or FMOD runtime are included. The Mac download is ad-hoc signed and not Apple-notarized. First-install behavior across different Apple accounts and AVP Play toolchain revisions is experimental and needs broader device testing.

Download the Mac ZIP from Releases, drag SaberDock into Applications, open Installation Settings, confirm the detected paths/team, add maps to the library, and choose Initial Install/Repair. Launch the installed headset app manually. Use Update Headset thereafter.

Build from source:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_app.py
```

The script downloads checksum-pinned portable Python and Node distributions. Dependencies and legal notices accompany the app. It builds the Mac tool only; game-derived builds are produced on the end user's Mac from their local AVP Play library.

SaberDock source: MIT. See [third-party notices](../THIRD-PARTY.md) and the [Chinese guide](../README.md).
