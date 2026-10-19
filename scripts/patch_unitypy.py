"""Defer unused proprietary FSB export so UnityPy can load without an FMOD runtime.

UnityPy is MIT-licensed. This is the only downstream change; original copyright
and license files remain in the installed package. SaberDock writes PCM itself.
"""
from pathlib import Path
import sys
path=Path(sys.argv[1])/'UnityPy/export/AudioClipConverter.py'
text=path.read_text();assert text.count('import fmod_toolkit')==1
text=text.replace('import fmod_toolkit\n','').replace('    return fmod_toolkit.raw_to_wav(', '    import fmod_toolkit  # Optional export path; not used or bundled by SaberDock.\n    return fmod_toolkit.raw_to_wav(')
path.write_text(text)
