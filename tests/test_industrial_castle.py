"""Both Korean castle upgrades retain their own complete state machines and player colour."""
import sys
import xml.etree.ElementTree as E
from pathlib import Path

K = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(K / 'tools'))
import korean_visuals as V


def test_castle_upgrade_states_and_other_cultures_are_preserved():
    rel = 'art/buildings/asian_civs/castle/castle.xml'
    text = V.read(rel)
    root = E.fromstring(text)
    tech = root.find('component/logic/japanese/logic')
    assert tech is not None
    inner = tech.find('zpkoreanvisuals/logic')
    for tier, stem in [('ypfrontiercastle', 'korean_castle'),
                       ('ypfortifiedcastle', 'korean_castle_industrial')]:
        completion = inner.find(tier + '/logic')
        assert completion.get('type') == 'BuildingCompletion'
        assert [c.tag for c in completion] == ['p0', 'p33', 'p66', 'p100']
        assert [c.find('submodelref').get('ref') for c in completion] == [
            stem + '_construction_stage_01', stem + '_construction_stage_02',
            stem + '_construction_stage_03', stem + '_built']
    assert V.canon(inner.find('none')) == V.canon(tech.find('none'))
    own = V.read('art/buildings/korean_castle/korean_castle.xml', str(K))
    upgraded = V.read(V.UPGRADES[rel][0][1], str(K))
    stripped = V.strip(V.strip(text, own), upgraded)
    merged = V.merge(stripped, own, 'japanese', False, 'ypfrontiercastle',
                     [('ypfortifiedcastle', upgraded, False)])
    assert merged == text, 'generator must be idempotent and preserve unrelated bytes'
    base = E.fromstring(stripped)
    for culture in ('chinese', 'indian'):
        assert V.canon(root.find('component/logic/' + culture)) == V.canon(base.find('component/logic/' + culture))


def test_industrial_player_colour_is_bound_in_intact_and_damaged():
    folder = K / 'art/buildings/korean_castle_industrial'
    for suffix in ('', '_damaged'):
        m = E.parse(folder / ('korean_castle_industrial' + suffix + '.material'))
        for slot in ('mata', 'matb'):
            textures = m.find("submaterial[@name='%s']/parameters" % slot)
            path = textures.find("texture[@name='Details']").get('override')
            assert path == 'buildings\\korean_castle_industrial\\textures\\korean_castle_industrial_' + slot + '_Details'
            assert (K / 'art' / (path.replace('\\', '/') + '.ddt')).is_file()
    root = E.parse(folder / 'korean_castle_industrial.xml')
    models = [m.text for m in root.findall('.//simskeleton/model')]
    assert models and set(models) == {'buildings\\korean_castle_industrial\\korean_castle_industrial_damaged'}
    banner = root.find(".//attachment[include='buildings\\korean_castle\\banner\\korean_castle_banner.xml']")
    assert banner is not None and (banner.text or '').strip() == 'korean_castle_banner'
    # Each live action uses the same existing left/right Korean banners.
    live_anims = [a for a in root.findall('.//anim') if a.findtext('component') == 'LIVE']
    assert len(live_anims) == 3
    for anim in live_anims:
        banners = anim.findall("attach[@a='korean_castle_banner']")
        assert {b.get('tobone') for b in banners} == {'bone_banner_l', 'bone_banner_r'}
        assert all(b.get('frombone') == 'bone_main' for b in banners)
    for anim in root.findall('.//anim'):
        if anim.findtext('component') != 'LIVE':
            assert not anim.findall("attach[@a='korean_castle_banner']")
