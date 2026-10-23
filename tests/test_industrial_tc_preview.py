"""The diagnostic must show the new intact TC without claiming old damage/con states."""
import copy
import xml.etree.ElementTree as E
from pathlib import Path

K = Path(__file__).resolve().parents[1]


def test_preview_uses_current_model_and_keeps_tc_garrison_gameplay():
    root = E.parse(K / 'data/protomods.xml').getroot()
    get = lambda name: next(u for u in root.findall('unit') if u.get('name') == name)
    source = copy.deepcopy(get('zzTESTKoreanTownCenter'))
    candidate = copy.deepcopy(get('zzTESTKoreanTownCenterIndustrialPreview'))
    assert candidate.findtext('animfile') == (
        'buildings\\korean_tc_industrial_preview\\korean_tc_industrial_preview.xml')
    for node in (source, candidate):
        node.attrib.clear()
        for name in ('dbid', 'displaynameid', 'editornameid', 'animfile'):
            node.remove(node.find(name))
    # Numeric/garrison/tactics values stay identical to the existing TC test unit.
    assert [(c.tag, c.attrib, (c.text or '').strip()) for c in source] == [
        (c.tag, c.attrib, (c.text or '').strip()) for c in candidate]
    anim = E.parse(K / 'art/buildings/korean_tc_industrial_preview/korean_tc_industrial_preview.xml')
    assert {d.text for d in anim.findall('definebone')} == {'bone_flag_civ', 'bone_garrisonflag'}
    assert not anim.findall('.//simskeleton') and not anim.findall('.//logic')
    models = [r.findtext('file') for r in anim.findall('.//assetreference') if r.get('type') == 'GrannyModel']
    assert models == ['buildings\\korean_tc_industrial_preview\\korean_tc_industrial_preview']
    assert {'Idle', 'RangedAttack', 'RangedAttackShip', 'Death'} == {(a.text or '').strip() for a in anim.findall('anim')}
    assert len(anim.findall('anim')) == 4
    assert all(a.findtext('component') == 'LIVE' for a in anim.findall('anim'))
