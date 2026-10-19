import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import backend
from test_library import make_map

class RootMigrationTests(unittest.TestCase):
    def test_moves_legacy_library_preserving_order_and_deleted_song_recovery(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder).resolve()
            root = home / 'Music/Beat Saber 曲库'
            with patch.object(Path, 'home', return_value=home), patch.object(backend, 'SUPPORT', home / 'support'):
                make_map(root / 'Vol.1/A', 'A')
                make_map(root / 'Vol.1/B', 'B')
                songs = backend.scan(root)['playlists'][0]['songs']
                backend.manage(root, 'Vol.1', 'order', [s['id'] for s in songs[::-1]])
                backend.manage(root, 'Vol.1', 'delete', [songs[0]['id']])
                result = backend.init(root)
                destination = home / 'Music/SaberDock Library'
                self.assertEqual(result['root'], str(destination))
                self.assertFalse(root.exists())
                state = backend.library_state(destination)
                self.assertEqual(state['orders']['Vol.1'], [s['id'] for s in songs[::-1]])
                self.assertTrue(state['history'][0]['source'].startswith(str(destination)))
                result = backend.manage(destination, 'Vol.1', 'restore', [])
                self.assertEqual([s['title'] for s in result['playlists'][0]['songs']], ['B', 'A'])

    def test_existing_english_library_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder).resolve()
            root = home / 'Music/Beat Saber 曲库'
            root.mkdir(parents=True)
            (root / 'keep.txt').write_text('legacy')
            destination = home / 'Music/SaberDock Library'
            destination.mkdir()
            (destination / 'keep.txt').write_text('existing')
            with patch.object(Path, 'home', return_value=home):
                migrated = backend.migrate_legacy_root(root)
            self.assertEqual(migrated.name, 'SaberDock Library (2)')
            self.assertEqual((migrated / 'keep.txt').read_text(), 'legacy')
            self.assertEqual((destination / 'keep.txt').read_text(), 'existing')

    def test_custom_library_locations_are_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / 'My Music'
            root.mkdir()
            self.assertEqual(backend.migrate_legacy_root(root), root)
