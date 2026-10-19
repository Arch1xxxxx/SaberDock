import base64
import struct
import unittest
from build import verify_pack_registry

def catalog(rows):
    name=b'PackDefinition'
    keys=b'\0'+struct.pack('<i',len(name))+name
    buckets=struct.pack('<iii',1,0,len(rows))+struct.pack(f'<{len(rows)}i',*rows)
    return {'m_KeyDataString':base64.b64encode(keys).decode(),
            'm_BucketDataString':base64.b64encode(buckets).decode()}

class PackRegistryTests(unittest.TestCase):
    def test_single_playlist_cannot_remove_other_game_registry_entries(self):
        original=catalog([12,25,38])
        with self.assertRaisesRegex(ValueError,'menu initialization'):
            verify_pack_registry(original,catalog([12]))

    def test_registry_keeps_all_original_indices(self):
        verify_pack_registry(catalog([12,25,38]),catalog([12,25,38]))
        with self.assertRaises(ValueError):
            verify_pack_registry(catalog([12,25,38]),catalog([12,25,40]))
