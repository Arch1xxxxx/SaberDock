# Contributing

Run `python3 -m unittest discover -s tests -v` before submitting changes. Unit fixtures generate their own silent WAV audio, small PNG image and minimal beatmap; they do not use commercial game resources.

For a Mac build, use `python3 scripts/build_app.py`. Only the builder's portable runtimes and dependencies are downloaded. Never commit or upload your game downloads, translated frameworks, device logs containing identifiers, local library, Apple signing material, or Application Support directory.

Compatibility changes should document the resource layouts they handle. Do not gate installation on game version names, internal version codes, or automatic discovery results. Explicit local file selections take priority. Validate required files and resource structures, and never silently switch to different selected files or rebuild the game executable. Keep all conversion and signing failures ahead of device mutations, preserve stable song IDs, and make source deletion reversible.

A useful bug report includes SaberDock, macOS, Xcode and AVP Play versions, the Beat Saber versionCode, and the displayed error. Remove local usernames, team/device identifiers and account data. Custom map reproduction files should be shared only when you have the right to distribute them.

Third-party export patch: the builder defers UnityPy's unused `fmod_toolkit` import to its AudioClip export path. SaberDock never invokes that exporter; it writes and validates uncompressed FSB PCM itself. Keep this patch explicit and preserve upstream license files.
