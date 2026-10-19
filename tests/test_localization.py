import ast
import os
import re
import string
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import backend
from i18n import MESSAGES, tr
from test_library import make_map

SOURCE = Path(__file__).resolve().parents[1] / 'src'

class LocalizationTests(unittest.TestCase):
    def test_every_application_message_has_an_english_translation(self):
        for filename in ['backend.py', 'integration.py', 'build.py']:
            for node in ast.walk(ast.parse((SOURCE / filename).read_text())):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'tr':
                    message = ast.literal_eval(node.args[0])
                    self.assertIn(message, MESSAGES, (filename, message))
        converter = (SOURCE / 'convert.cjs').read_text()
        for message in re.findall(r"tr\('([^']*)'\)", converter):
            self.assertIn(message, MESSAGES)
        for original, english in MESSAGES.items():
            self.assertIsNone(re.search(r'[\u4e00-\u9fff]', english), original)
            fields = lambda text: [(field, spec, conv) for _, field, spec, conv in string.Formatter().parse(text) if field is not None]
            self.assertEqual(fields(original), fields(english), original)

    def test_english_default_and_chinese_selection(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(tr('缺少封面图片'), 'Cover image missing')
        with patch.dict(os.environ, {'SABERDOCK_LANGUAGE': 'zh-Hans'}):
            self.assertEqual(tr('缺少封面图片'), '缺少封面图片')

    def test_song_errors_keep_user_titles_in_both_languages(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / 'Library'
            song = make_map(root / 'Pop' / 'Map', '用户歌名 Japanese 日本語')
            (song / 'cover.png').unlink()
            with patch.object(backend, 'SUPPORT', Path(folder) / 'support'):
                for language, expected in [('en', 'Cover image missing'), ('zh-Hans', '缺少封面图片')]:
                    with patch.dict(os.environ, {'SABERDOCK_LANGUAGE': language}):
                        error = backend.scan(root)['errors'][0]
                        self.assertIn('用户歌名 Japanese 日本語', error)
                        self.assertIn(expected, error)

    def test_legacy_deleted_song_can_be_restored_after_update(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / 'Library'
            with patch.object(backend, 'SUPPORT', Path(folder) / 'support'):
                make_map(root / 'Pop' / 'Map')
                song = backend.scan(root)['playlists'][0]['songs'][0]
                backend.manage(root, 'Pop', 'delete', [song['id']])
                state = backend.library_state(root)
                record = state['history'][-1]
                target = Path(record['trash'])
                self.assertIn('.library-trash', target.parts)
                legacy = root / '.曲库回收站' / 'legacy' / target.name
                legacy.parent.mkdir(parents=True)
                target.rename(legacy)
                record['trash'] = str(legacy)
                backend.atomic(backend.state_file(root), state)
                backend.manage(root, 'Pop', 'restore', [])
                self.assertTrue((root / 'Pop' / 'Map' / 'Info.dat').exists())
