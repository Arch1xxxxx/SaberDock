# Contributing

Run `python3 -m unittest discover -s tests -v` before submitting changes. Unit fixtures generate their own silent WAV audio, small PNG image and minimal beatmap; they do not use commercial game resources.

For a Mac build, use `python3 scripts/build_app.py`. Only the builder's portable runtimes and dependencies are downloaded. Never commit or upload your game downloads, translated frameworks, device logs containing identifiers, local library, Apple signing material, or Application Support directory.

Compatibility changes should identify a supported APK/versionCode and OBB layout explicitly. Do not silently fall back to a different game version. Keep all conversion and signing failures ahead of device mutations, preserve stable song IDs, and make source deletion reversible.

A useful bug report includes SaberDock, macOS, Xcode and AVP Play versions, the Beat Saber versionCode, and the displayed error. Remove local usernames, team/device identifiers and account data. Custom map reproduction files should be shared only when you have the right to distribute them.

Third-party export patch: the builder defers UnityPy's unused `fmod_toolkit` import to its AudioClip export path. SaberDock never invokes that exporter; it writes and validates uncompressed FSB PCM itself. Keep this patch explicit and preserve upstream license files.
