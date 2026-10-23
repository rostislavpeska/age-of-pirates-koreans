"""The diagnostic shows the new TC with its own destruction (R58, China TC age 4 donor graph); it has no construction
stages and never uses the old Korean TC's damaged model."""
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
    intact = 'buildings\\korean_tc_industrial_preview\\korean_tc_industrial_preview'
    damaged = intact + '_damaged'
    models = {r.findtext('file') for r in anim.findall('.//assetreference') if r.get('type') == 'GrannyModel'}
    assert models == {intact, damaged}
    comps = {(c.text or '').strip(): c for c in anim.findall('component')}
    logic = comps['LIVE'].find('logic')
    assert logic.get('type') == 'Destruction'
    assert logic.findtext('p1/assetreference/file') == damaged and logic.findtext('p99/assetreference/file') == intact
    assert comps['DEAD'].findtext('assetreference/file') == damaged
    anims = {(a.text or '').strip(): a for a in anim.findall('anim')}
    assert set(anims) == {'Idle', 'RangedAttack', 'RangedAttackShip', 'Death'} and len(anim.findall('anim')) == 4
    for name in ('Idle', 'RangedAttack', 'RangedAttackShip'):
        assert anims[name].findtext('component') == 'LIVE' and anims[name].findtext('simskeleton/model') == damaged
    assert anims['Death'].findtext('component') == 'DEAD'
    folder = K / 'art/buildings/korean_tc_industrial_preview'
    for name in ('korean_tc_industrial_preview_damaged.gr2', 'korean_tc_industrial_preview_damaged.hkt',
                 'korean_tc_industrial_preview_damaged.material'):
        assert (folder / name).is_file(), name
