# Third-party software

SaberDock's own source is MIT-licensed. Dependencies retain their respective licenses:

- [AVP Play](https://github.com/myMartek/avp-play), MIT: called on the user's Mac to unpack the user's local APK. Its application, toolchains and content library are not redistributed.
- [Klepton](https://github.com/shinyquagsire23/Klepton), MIT and its third-party notices: the user's AVP Play toolchain is used locally to prepare the visionOS runtime. No Klepton build or translated game code is included in SaberDock releases.
- [Python](https://www.python.org/), PSF and bundled-library notices; portable distribution from [python-build-standalone](https://github.com/astral-sh/python-build-standalone). Runtime notices are preserved in the release.
- [Node.js](https://nodejs.org/), MIT and bundled-library notices. `Contents/Resources/licenses/Node-LICENSE` preserves its full notice.
- [UnityPy](https://github.com/K0lb3/UnityPy), MIT.
- [bsmap](https://github.com/KivalEvan/BeatSaber-JSMap), MIT.
- NumPy, BSD-3-Clause; Pillow, HPND; SoundFile, BSD-3-Clause; libsndfile, LGPL-2.1-or-later.
- Transitive dependencies retain their package license files. Python wheel `*.dist-info` license directories and npm package license files are included unchanged. A generated dependency inventory accompanies releases.

No FMOD SDK or proprietary FMOD runtime is distributed. SaberDock generates uncompressed FSB PCM and checks the serialized PCM payload directly.

No Beat Saber APK/OBB, official audio, custom songs, covers, paid song packs, translated game libraries, Apple signing profile, certificate or account credential is included in the source or release. Game-derived files are created only on the user's Mac from their own AVP Play downloads, in Application Support/SaberDock.

Beat Saber is a trademark of its respective owners. SaberDock is an independent community tool and is not affiliated with Meta, Beat Games, Apple, AVP Play or Klepton.
