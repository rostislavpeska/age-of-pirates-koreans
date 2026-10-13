"""INC358: native release authority must retain exact pinned Unicode text."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoofProfileAuthority(unittest.TestCase):
    def test_house_and_castle_shared_authority_is_exact(self):
        profiles = json.loads((ROOT / 'tools/gr2_lint/profiles.json').read_bytes())['profiles']
        names = ['korean_house_' + h + suffix for h in 'abc' for suffix in ['', '_con']]
        names += ['korean_castle' + age + suffix for age in ['', '_industrial'] for suffix in ['', '_con']]
        for name in names:
            for dependency in profiles[name].get('texture_budget', {}).get('shared_mod_dependencies', []):
                authority = dependency.get('authorization', {})
                if authority.get('kind') != 'recorded_owner_chat':
                    continue
                with self.subTest(profile=name, source=dependency['source_names']):
                    raw = (ROOT / authority['path']).read_bytes()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), authority['sha256'])
                    evidence = json.loads(raw)
                    self.assertEqual(authority['owner_quote'], evidence['owner_quote'])
                    self.assertIn(profiles[name]['model'], evidence['models'])
                    self.assertTrue(set(dependency['source_names']) <= set(evidence['source_names']))


if __name__ == '__main__':
    unittest.main()
