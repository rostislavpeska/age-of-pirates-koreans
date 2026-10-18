"""Every protounit in data/protomods.xml has its own id, dbid and name.

The range check in test_koreans.py looks at each unit on its own, so it let zzTESTKoreanCastleIndustrial (2026-10-12)
and zpKoreanLancer (2026-10-13) both ship as 22023 until 2026-10-18. A new unit takes the next free id in
22000-22999, with dbid = id.

    python -m pytest tests -q
"""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

K = Path(__file__).resolve().parents[1]
UNITS = ET.fromstring((K / 'data/protomods.xml').read_bytes().decode('utf-8-sig')).findall('unit')
KEYS = {'id': lambda u: u.get('id'), 'dbid': lambda u: (u.findtext('dbid') or '').strip(), 'name': lambda u: u.get('name')}


def shared(units, key):
    """{value: [unit names]} for every value of `key` that more than one unit carries."""
    seen = {}
    for u in units:
        if key(u):
            seen.setdefault(key(u), []).append(u.get('name'))
    return {v: names for v, names in seen.items() if len(names) > 1}


@pytest.mark.parametrize('field', KEYS)
def test_protomods_units_do_not_share(field):
    clash = shared(UNITS, KEYS[field])
    assert not clash, f'data/protomods.xml: units share a {field}: {clash}'
