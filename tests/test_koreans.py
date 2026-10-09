"""The Koreans add-on: its wiring and the freshness of its generated files.

    python -m pytest tests -q

Repo-only checks run everywhere; checks that read AoP (../age-of-pirates or AOP_ROOT) or the installed game skip
when those are missing. AoP's own guard (no Korean record in AoP) lives in AoP:
scripts/tools/tests/test_no_korean_civ_in_aop.py.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

K = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(K / 'tools'))
import korean_visuals  # noqa: E402

AOP = Path(korean_visuals.AOP)
BS = chr(92)
needs_aop = pytest.mark.skipif(not (AOP / 'data' / 'techtreemods.xml').is_file(), reason='AoP checkout not found')


def xml(path):
    return ET.fromstring(path.read_bytes().decode('utf-8-sig'))


def test_one_playable_civ_on_the_korean_age0_tech():
    civs = xml(K / 'data/civmods.xml').findall('civ')
    assert [c.findtext('name') for c in civs] == ['zpKoreans']
    civ = civs[0]
    assert civ.findtext('main') == '1' and civ.find('visible') is None
    ages = {a.findtext('age'): a.findtext('tech') for a in civ.findall('agetech')}
    assert ages['Age0'] == 'zpAge0Korean' and ages['Age1'] == 'YPColonializeJapanese'
    assert civ.findtext('culture') == 'Japanese'
    assert (K / 'data' / civ.findtext('homecityfilename')).is_file()


def test_techs_activate_japan_and_the_visual_marker():
    techs = xml(K / 'data/techtreemods.xml').findall('tech')
    assert [t.get('name') for t in techs] == ['zpKoreanVisuals', 'zpAge0Korean', 'zpKoreanBuildings', 'zpKoreanHouseArrows',
                                                  'zpKoreanUnits', 'zpKoreanEconomy', 'zpMonasteryHyangyak', 'zpMonasteryDure',
                                                  'zpMonasteryPyeonjeon', 'zpMonasterySeungbyeong', 'zpSeungbyeongColonial', 'zpSeungbyeongFortress',
                                                  'zpSeungbyeongIndustrial', 'zpSeungbyeongImperial']
    active = [e.text for e in techs[1].iter('effect') if e.get('type') == 'TechStatus' and e.get('status') == 'active']
    assert active == ['YPAge0Japanese', 'zpKoreanVisuals', 'zpKoreanBuildings', 'zpKoreanUnits', 'zpKoreanEconomy']
    assert all(60000 <= int(t.findtext('dbid')) < 61000 for t in techs)


def test_strings_flags_personality_and_sounds():
    ids = re.findall(r'_locid="(\d+)"', (K / 'data/strings/english/stringmods.xml').read_text(encoding='utf-8'))
    assert ids == [str(600000 + i) for i in range(48)]          # 600022-600027: zzTEST House benches A/B/C
                                                                # 600028-600037: the monks' random names
                                                                # 600038-600043: zzTEST TC/Barracks/Stable names
                                                                # 600044-600047: the Seungbyeong
    civ = xml(K / 'data/civmods.xml').find('civ')
    for field in ('homecityflagiconwpf', 'homecityflagbuttonwpf', 'postgameflagiconwpf'):
        assert (K / 'data/wpfg' / civ.findtext(field).replace(BS, '/')).is_file(), field
    assert (K / 'art/objects/flags/zpkoreans.ddt').stat().st_size == 174856        # vanilla flag profile
    pers = xml(K / 'game/ai/personalities/zpmyeongseong.personality')
    assert pers.findtext('forcedciv') == 'zpKoreans' and pers.findtext('nameID') == '600004'
    assert 'zpMyeongseong' in [p.text for p in xml(K / 'game/ai/personalities.xml').findall('Personality')]
    for s in xml(K / 'tools/korean_soundsets.xml').iter('sound'):
        assert (K / 'sound' / s.get('filename').replace(BS, '/')).is_file(), s.get('filename')


def test_korean_house_replaces_the_shrine_as_a_refuge():
    """Owner decisions 2026-10-08: standard-house values, refuge for 3 villagers or infantry (5 was too strong, 2026-10-09), arrows only while
    occupied (Chinese Village tactics) from the Colonial Age, Shrine model as placeholder, every villager builds it
    in the Shrine's slot."""
    units = xml(K / 'data/protomods.xml').findall('unit')
    assert units[0].get('name') == 'zpHouseKorean'
    house = units[0]
    assert all(22000 <= int(u.findtext('dbid')) == int(u.get('id')) < 23000 for u in units)
    assert (house.findtext('populationcapaddition'), house.findtext('buildlimit'), house.findtext('maxcontained')) == ('10', '20', '3')
    assert float(house.findtext('maxhitpoints')) == 1200 and float(house.find('cost').text) == 100
    types = [e.text for e in house.findall('unittype')]
    assert 'AbstractHouse' in types and 'AbstractShrine' not in types
    assert [e.text for e in house.findall('contain')] == ['AbstractVillager', 'AbstractInfantry']
    assert 'AllowAutoGarrison' in [e.text for e in house.findall('flag')]
    tactics = xml(K / 'data/tactics' / house.findtext('tactics'))
    attack = [a for a in tactics.findall('action') if a.findtext('name') == 'RangedAttack'][0]
    assert attack.findtext('activeifcontainsunits') == '1' and attack.findtext('scalebycontainedunits') == '1'
    assert attack.findtext('damagefactorcap') == house.findtext('maxcontained') and attack.findtext('active') == '0'
    snds = xml(K / 'sound' / ('%s_snds.xml' % house.get('name').lower()))
    assert snds.find('protounit').get('name') == house.get('name')
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = [(e.get('type'), e.get('subtype') or e.get('status'), e.get('amount'), e.get('proto'), e.get('page'),
            e.get('column'), e.findtext('target') or (e.text or '').strip()) for e in techs['zpKoreanBuildings'].iter('effect')]
    assert eff == [('Data', 'Enable', '1.00', None, None, None, 'zpHouseKorean'),
                   ('CommandAdd', None, None, 'zpHouseKorean', '6', '0', 'AbstractVillager'),   # the Shrine's slot
                   ('Data', 'Enable', '0.00', None, None, None, 'ypShrineJapanese'),
                   # an UNOBTAINABLE shadow tech fires on its prereqs only once armed (owner's test 2026-10-09)
                   ('TechStatus', 'obtainable', None, None, None, None, 'zpKoreanHouseArrows')]
    arrows = techs['zpKoreanHouseArrows']
    assert [p.text for p in arrows.iter('techstatus')] == ['Colonialize', 'zpKoreanVisuals']
    assert [(e.get('action'), e.findtext('target')) for e in arrows.iter('effect')] == [('RangedAttack', 'zpHouseKorean')]


def test_koreans_use_the_asian_villager_with_korean_voices():
    """Owner decision 2026-10-08: the Asian (Chinese) villager, which hunts, speaking Korean (as WoL Koreans)."""
    civ = xml(K / 'data/civmods.xml').find('civ')
    assert 'ypSettlerJapanese' not in (K / 'data/civmods.xml').read_text(encoding='utf-8')
    assert civ.findtext('settlerprotoname') == 'ypSettlerAsian'
    assert [u.text for u in civ.findall('townstartingunit')].count('ypSettlerAsian') == 6
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    assert [(e.get('amount'), e.findtext('target')) for e in techs['zpKoreanUnits'].iter('effect')][:2] == [
        ('1.00', 'ypSettlerAsian'), ('0.00', 'ypSettlerJapanese')]
    snds = (K / 'sound/ypsettlerasian_snds.xml').read_text(encoding='utf-8')
    root = ET.fromstring(snds)
    korean = [c.find('soundset').get('name') for c in root.iter('choice') if c.get('name') == 'zpKoreans']
    chinese = [s.get('name') for s in root.iter('soundset') if s.get('name').startswith('ChineseVillager')]
    assert len(korean) == len(chinese) == 20      # every Chinese villager voice has a Korean twin
    defined = set(re.findall(r'<soundset name="([^"]+)"', (K / 'sound/soundsetsde.mods.xml').read_text(encoding='utf-8')))
    assert set(korean) <= defined, sorted(set(korean) - defined)


def test_korean_wagons_and_fishing_boats_speak_like_the_japanese_ones():
    """Owner 2026-10-09: fishing boats with the male villager voice, every wagon as the Japanese one, no new
    soundsets. Each Japanese choice has a zpKoreans twin right after it: Japanese voices renamed to their Korean
    twins (existing soundsets), every other voice kept."""
    defined = set(re.findall(r'<soundset name="([^"]+)"', (K / 'sound/soundsetsde.mods.xml').read_text(encoding='utf-8')))
    files = sorted(p for p in (K / 'sound').glob('*_snds.xml') if 'wagon' in p.name and not p.name.startswith('zztest'))
    assert len(files) == 49 and (K / 'sound/ypfishingboatasian_snds.xml').is_file()
    korean_voices = set()
    for p in files + [K / 'sound/ypfishingboatasian_snds.xml']:
        assert b'\r\n' in p.read_bytes() and b'\n' not in p.read_bytes().replace(b'\r\n', b''), p.name   # CRLF
        root = ET.fromstring(p.read_text(encoding='utf-8'))
        pairs = 0
        for parent in root.iter():
            kids = list(parent)
            for k, c in enumerate(kids):
                if c.get('name') == 'Japanese':
                    twin = kids[k + 1]
                    assert twin.get('name') == 'zpKoreans', p.name
                    jp = [s.get('name') for s in c.iter('soundset')]
                    ko = [s.get('name') for s in twin.iter('soundset')]
                    assert ko == [n.replace('JapaneseVillagerM_', 'zpKoreanVillagerM_')
                                  .replace('JapaneseFishingBoat', 'zpKoreanFishingBoat') for n in jp], p.name
                    korean_voices |= {n for n in ko if n.startswith('zpKorean')}
                    pairs += 1
        assert pairs == 2, (p.name, pairs)                                   # Select and Acknowledge
    assert korean_voices == {'zpKoreanVillagerM_Select', 'zpKoreanVillagerM_Acknowledge',
                             'zpKoreanFishingBoatSelect', 'zpKoreanFishingBoatAcknowledge'}
    assert korean_voices <= defined


def test_monks_have_the_japanese_monk_abilities_and_korean_names():
    """Owner's test 2026-10-09: the Abilities grid was empty and the monk was called "Korean Monk". Abilities and
    random names bind by proto name in their own files (data/abilities/abilitymods.xml, data/randomnamemods.xml), so
    a new proto has neither until it is listed there."""
    strings = dict(re.findall(r'_locid="(\d+)">([^<]*)<', (K / 'data/strings/english/stringmods.xml').read_text(encoding='utf-8')))
    units = {u.get('name'): u for u in xml(K / 'data/protomods.xml').findall('unit')}
    abilities = xml(K / 'data/abilities/abilitymods.xml')
    names = {p.text.strip(): [t.text for t in p.iter('title')] for p in xml(K / 'data/randomnamemods.xml').findall('protounit')}
    tactics = {a.findtext('name') for a in xml(K / 'data/tactics/zpmonkkorean.tactics').iter('action')}
    for name in ('zpMonkKorean', 'zpMonkKorean2'):
        u = units[name]
        assert 'Abilities' in [c.text for c in u.findall('command')] and 'HeroName2' in [f.text for f in u.findall('flag')]
        powers = [a.text for a in abilities.find(name.lower()).findall('ability')]
        assert powers == ['ypPowerGuardianStun', 'ypPowerSmokeBomb', 'ypPowerDivineBlow', 'ypPowerDodge',
                          'ypUnitScareAura', 'deUnitHealthRegen']       # the Japanese monk's, without ypPowerSabotage
        assert {'Stun', 'SmokeBomb'} <= tactics                          # the actions those powers fire
        assert names[name] == [str(i) for i in range(600028, 600038)] and all(strings[i] for i in names[name])
        assert strings[u.findtext('displaynameid')] == 'Seungjang'
    assert (K / 'data/abilities/abilitymods.xml.xmb').is_file() and (K / 'data/randomnamemods.xml.xmb').is_file()


def test_hanok_uses_the_generic_house_icons():
    house = xml(K / 'data/protomods.xml').find('unit')
    assert house.findtext('icon').endswith('house_icon.png') and house.findtext('portraiticon').endswith('house_portrait.png')


def test_korean_monks_replace_the_japanese_monks():
    """Owner 2026-10-09: a mounted monk-explorer (WoL principle) on the Manchu horse archer model as placeholder."""
    units = {u.get('name'): u for u in xml(K / 'data/protomods.xml').findall('unit')}
    # zzTEST* = the 3D test benches in their own marked block (owner 2026-10-09, strip before release)
    assert {n for n in units if not n.startswith('zzTEST')} == {'zpHouseKorean', 'zpMonkKorean', 'zpMonkKorean2', 'zpSeungbyeong'}
    civ = xml(K / 'data/civmods.xml').find('civ')
    assert [u.text for u in civ.findall('startingunit')][:2] == ['zpMonkKorean', 'zpMonkKorean2']
    assert 'ypMonkJapanese' not in (K / 'data/civmods.xml').read_text(encoding='utf-8')
    assert 'ypMonkJapanese' not in (K / 'data/homecityzpkoreans.xml').read_text(encoding='utf-8')
    for name in ('zpMonkKorean', 'zpMonkKorean2'):
        u = units[name]
        types = {e.text for e in u.findall('unittype')}
        assert {'Hero', 'AbstractMonk', 'AbstractCavalry'} <= types
        assert not types & {'AbstractInfantry', 'AbstractJapaneseMonk', 'LogicalTypeStealthUnit'}
        assert 'KnockoutDeath' in [f.text for f in u.findall('flag')]
        trains = [e.text for e in u.findall('train')]
        assert 'zpHouseKorean' in trains and 'ypShrineJapanese' not in trains
        assert 'ypMonkDisciple' not in trains and 'zpSeungbyeong' not in trains   # the tech adds the Seungbyeong
        assert 'ToggleStealth' not in [c.text for c in u.findall('command')]
        assert 'SabotageAttack' not in [a.findtext('name') for a in u.findall('protoaction')]
        assert (K / 'data/tactics' / u.findtext('tactics')).is_file()
        assert (K / 'art' / u.findtext('animfile').replace(BS, '/')).is_file()
        snds = xml(K / 'sound' / ('%s_snds.xml' % name.lower()))
        assert snds.find('protounit').get('name') == name
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = list(techs['zpKoreanUnits'].iter('effect'))
    tc = [(e.get('proto'), e.get('page'), e.get('column')) for e in eff
          if e.get('type') == 'CommandAdd' and e.findtext('target') == 'TownCenter']
    assert tc == [('zpMonkKorean', '0', '5'), ('zpMonkKorean2', '0', '6')]      # the Japanese monks' retrain slots
    off = [e.findtext('target') for e in eff if e.get('subtype') == 'Enable' and e.get('amount') == '0.00']
    assert {'ypMonkJapanese', 'ypMonkJapanese2'} <= set(off)


def test_seungbyeong_is_a_zero_pop_monk_soldier_with_a_glaive():
    """Owner 2026-10-09: "extra unit like disciple", "no pop costs but lower stats", "distinct from Disciple", the white
    monk "as footman". The native Sohei's glaive and pikeman.tactics on the Disciple body with the monk's white
    retexture; trained in the Barracks (Korea only) and, after zpMonasterySeungbyeong, by the Seungjang in the field."""
    units = {u.get('name'): u for u in xml(K / 'data/protomods.xml').findall('unit')}
    u = units['zpSeungbyeong']
    assert u.findtext('populationcount') is None and u.findtext('buildlimit') == '10' and u.findtext('allowedage') == '1'
    assert {c.get('resourcetype'): float(c.text) for c in u.findall('cost')} == {'Food': 50.0, 'Wood': 30.0}
    assert float(u.findtext('maxhitpoints')) == 100 and u.findtext('tactics') == 'pikeman.tactics'
    types = {e.text for e in u.findall('unittype')}
    assert {'AbstractPikeman', 'AbstractHandInfantry', 'AbstractInfantry'} <= types and 'AbstractNativeWarrior' not in types
    melee = [a for a in u.findall('protoaction') if a.findtext('name') == 'MeleeHandAttack'][0]
    assert float(melee.findtext('damage')) == 9
    assert {b.get('type'): float(b.text) for b in melee.findall('damagebonus')} == {'AbstractCavalry': 3.0,
                                                                                   'AbstractLightInfantry': 2.0}
    anim = (K / 'art' / u.findtext('animfile').replace(BS, '/')).read_text(encoding='utf-8')
    model = BS.join(['units', 'korean_monk', 'korean_seungbyeong'])
    assert anim.count('<file>%s</file>' % model) == 2 and 'sohei_age2' not in anim
    assert '_pikeman</file>' not in anim and anim.count('tobone="Bip01 Prop1"') == 2     # Bip01 twins, glaive in hand
    assert BS.join(['sohei', 'sohei_sword']) in anim                                  # the vanilla glaive, by path
    mat = lambda n: (K / 'art/units/korean_monk' / n).read_text(encoding='utf-8')
    assert mat('korean_seungbyeong.material') == mat('korean_monk_rider.material')    # the monk's white retexture
    assert (K / 'art/units/korean_monk/korean_seungbyeong.gr2').is_file()
    snds = xml(K / 'sound/zpseungbyeong_snds.xml')
    assert snds.find('protounit').get('name') == 'zpSeungbyeong'
    assert {s.get('name') for s in snds.iter('soundset')} >= {'Korean_Soldier_Select', 'Korean_Soldier_Attack'}
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = list(techs['zpKoreanUnits'].iter('effect'))
    assert ('zpSeungbyeong', '0', '3', 'ypBarracksJapanese') in [
        (e.get('proto'), e.get('page'), e.get('column'), e.findtext('target')) for e in eff if e.get('type') == 'CommandAdd']
    assert 'zpSeungbyeong' in [e.findtext('target') for e in eff if e.get('subtype') == 'Enable' and e.get('amount') == '1.00']
    sb = [(e.get('type'), e.get('subtype'), e.get('amount'), e.get('proto'), e.get('page'), e.get('column'),
           e.findtext('target')) for e in techs['zpMonasterySeungbyeong'].iter('effect')]
    assert sb == [('CommandAdd', None, None, 'zpSeungbyeong', '6', '7', 'zpMonkKorean'),
                  ('CommandAdd', None, None, 'zpSeungbyeong', '6', '7', 'zpMonkKorean2'),
                  ('Data', 'BuildLimit', '15.00', None, None, None, 'zpSeungbyeong')]
    strings = dict(re.findall(r'_locid="(\d+)">([^<]*)<', (K / 'data/strings/english/stringmods.xml').read_text(encoding='utf-8')))
    assert strings[u.findtext('displaynameid')] == 'Seungbyeong'


def test_seungbyeong_plays_the_vanilla_sohei_animations():
    """The footman's animfile keeps the vanilla Sohei's animation set (the one pikeman.tactics plays on the Sohei),
    and every file it names exists in the game: the animation library's Bip01 twins, the glaive, the effects."""
    try:
        import korean_sounds
        bt, index = korean_sounds.bartool()
    except BaseException:
        pytest.skip('game archives not readable here')
    vanilla = bt.decode(bt.read_entry(index['art/units/asians/japanese/sohei/sohei.xml.xmb']), True, 'lf')[0]
    ours = (K / 'art/units/korean_monk/korean_seungbyeong.xml').read_text(encoding='utf-8')
    assert set(_top_anims(ours)) == set(_top_anims(vanilla.decode('utf-8-sig')))
    model = BS.join(['units', 'korean_monk', 'korean_seungbyeong'])
    for f in set(re.findall(r'<file>([^<]+)</file>', ours)) - {model}:
        p = 'art/' + f.replace(BS, '/').lower()
        assert any(p + ext in index for ext in ('.gr2', '.xmb', '')), f


def test_monk_portraits_and_icons_carry_the_player_colour():
    """Owner 2026-10-09: own portraits for the Seungjang and the Seungbyeong on the vanilla portrait backdrop; the
    kasaya is transparent and stores a light grey shading: the game multiplies the player colour into the RGB under
    it (owner's test 2026-10-09: stored black showed a near-black sash), as the vanilla monk sashes."""
    from PIL import Image
    units = {u.get('name'): u for u in xml(K / 'data/protomods.xml').findall('unit')}
    for name in ('zpMonkKorean', 'zpMonkKorean2', 'zpSeungbyeong'):
        u = units[name]
        for field, size in (('portraiticon', 512), ('icon', 128)):
            im = Image.open(K / 'data/wpfg' / u.findtext(field).replace(BS, '/')).convert('RGBA')
            assert im.size == (size, size), (name, field, im.size)
            hole = sum(1 for a in im.getchannel('A').getdata() if a == 0) / size / size
            assert hole > 0.02, (name, field, hole)                       # the player-colour kasaya
            under = [sum(px[:3]) / 3 for px in im.getdata() if px[3] == 0]
            assert sorted(under)[len(under) // 2] > 100, (name, field)     # the game MULTIPLIES the player colour
                                                                          # into this RGB: black = black sash
        assert 'sohei' not in u.findtext('icon') and 'sohei' not in u.findtext('portraiticon')


def test_seungbyeong_scales_with_the_ages_like_the_disciple():
    """Owner 2026-10-09: "verify how disciples are impacted by age up ... your new unit must work the same way". The
    Disciple's only age scaling: the Chinese age techs (hit points and damage x1.20/1.30/1.40/1.50, +0.5 speed at
    Colonial). Korea's Japanese age-ups activate the generic age techs, on which four armed shadow techs fire."""
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    armed = [(e.text or '').strip() for e in techs['zpKoreanUnits'].iter('effect') if e.get('status') == 'obtainable']
    for name, age, amt in (('zpSeungbyeongColonial', 'Colonialize', '1.20'), ('zpSeungbyeongFortress', 'Fortressize', '1.30'),
                           ('zpSeungbyeongIndustrial', 'Industrialize', '1.40'), ('zpSeungbyeongImperial', 'Imperialize', '1.50')):
        t = techs[name]
        assert name in armed and t.findtext('status') == 'UNOBTAINABLE' and 'Shadow' in [f.text for f in t.findall('flag')]
        assert [p.text for p in t.iter('techstatus')] == [age, 'zpKoreanVisuals']
        got = {(e.get('subtype'), e.get('amount'), e.get('relativity'), e.get('allactions')) for e in t.iter('effect')}
        want = {('Hitpoints', amt, 'BasePercent', None), ('Damage', amt, 'BasePercent', '1')}
        if age == 'Colonialize':
            want.add(('MaximumVelocity', '0.50', 'Absolute', None))
        assert got == want, (name, got)
        assert {e.findtext('target') for e in t.iter('effect')} == {'zpSeungbyeong'}


def _top_anims(text):
    """{lower anim name: [GrannyAnim files]} of the top-level anims (anims inside attachments are skipped)."""
    blocks = re.findall(r'^  <anim>(\w+)<(.*?)^  </anim>', text, re.S | re.M)
    return {n.lower(): re.findall(r'<file>([^<]+)</file>', b) for n, b in blocks}


def _anim_scopes(text):
    """[(scope, anims, defined attachments, used attachments)] of one animfile. A unit: its top-level anims and
    attachments. A building whose anims all sit inside submodels (the vanilla shrine.xml pattern, the Korean House):
    one scope per finished submodel - it has a Death anim; construction stages hold Idle only and play no action -
    with the attachments defined at the top level or inside that submodel."""
    top = _top_anims(text)
    defined_top = set(re.findall(r'^  <attachment>(\w+)', text, re.M))
    if top:
        return [('', top, defined_top, set(re.findall(r'<attach a="(\w+)"', text)))]
    scopes = []
    for s in ET.fromstring(text.lstrip('\ufeff')).findall('submodel'):
        anims = {(a.text or '').strip().lower(): [(f.text or '').strip() for f in a.iter('file')]
                 for a in s.findall('anim')}
        if 'death' in anims:
            scopes.append(((s.text or '').strip(), anims,
                           defined_top | {(a.text or '').strip() for a in s.findall('attachment')},
                           {e.get('a') for e in s.iter('attach')}))
    return scopes


def test_final_monk_is_the_retextured_disciple_on_the_yabusame_horse():
    """Owner 2026-10-09: the bald Disciple on the rider skeleton rides (game test "Works!"), retextured after the WoL
    Jeobju; hero cavalry selection like the Elmeti; heal from the Lakota war chief; own BaseColor/Normals/Details."""
    horse = (K / 'art/units/korean_monk/korean_monk_horse.xml').read_text(encoding='utf-8')
    rider = (K / 'art/units/korean_monk/korean_monk_rider.xml').read_text(encoding='utf-8')
    dec = re.search(r'<decal>(.*?)</decal>', horse, re.S).group(1)
    assert 'shadows_selections' + BS + 'shadow_hero_64x64' in dec and 'selection_hero_64x64' in dec
    assert '<width>1.50</width>' in dec and '<height>3.00</height>' in dec
    model = BS.join(['units', 'korean_monk', 'korean_monk_rider'])
    assert rider.count('<file>%s</file>' % model) == 4 and not re.search(r'yabusameRider_[02]', rider, re.I)
    assert (K / 'art/units/korean_monk/korean_monk_rider.gr2').is_file()
    heal = lambda text: re.search(r'^  <anim>Heal<(.*?)^  </anim>', text, re.S | re.M).group(1)
    assert 'horse_heal' in heal(horse) and 'warchief_lakota' + BS + 'heal' in heal(rider)
    assert 'spear' not in heal(rider)
    mat = (K / 'art/units/korean_monk/korean_monk_rider.material').read_text(encoding='utf-8')
    tex = dict(re.findall(r'<texture name="(\w+)" override="([^"]+)"', mat))
    for kind in ('BaseColor', 'Normals', 'Details'):
        assert (K / 'art' / (tex[kind] + '.ddt')).is_file(), kind
    assert tex['Masks'].startswith('units/asians/chinese/shaolin_disciple/')     # vanilla masks by path


def test_monk_arrows_leave_with_the_bow_release():
    """Owner's game test 2026-10-09 (bench): "the shooting anim is not well synced with the arrow". The rider draws
    with the generic cavalry bow_attack_A-D; the arrow leaves at the HORSE animation's Attack tag. Only the generic
    horse_1-5_attack_A-D carry tags tuned to that release (0.62 / 0.43 / 0.43 / 0.43, the Manchu archer pair); the
    yabusame's own horse attacks fire at 0.28. Every monk horse animfile uses the tuned pair for each shot."""
    tuned = [('horse_1-5_attack_A', ['0.62']), ('horse_1-5_attack_B', ['0.43']),
             ('horse_1-5_attack_C', ['0.43']), ('horse_1-5_attack_D', ['0.43'])]
    for rel in ('art/units/korean_monk/korean_monk_horse.xml',):
        anims = dict(re.findall(r'^  <anim>(\w+)<(.*?)^  </anim>', (K / rel).read_text(encoding='utf-8'), re.S | re.M))
        for shot in ('Attack_ranged', 'Volley_standing_attack', 'stun_attack'):
            refs = re.findall(r'<file>([^<]+)</file>(.*?)</assetreference>', anims[shot], re.S)
            got = [(f.split(BS)[-1], re.findall(r'type="Attack">([^<]+)<', b)) for f, b in refs]
            assert got == tuned, (rel, shot, got)


def test_every_tactics_animation_exists_and_moves():
    """Owner 2026-10-09: the Korean monk stood still while building and picking up treasure (its Build and Pickup
    were copies of Idle). For every proto with a repo animfile and repo tactics: each animation an action names
    exists in the animfile and in every repo animfile it includes (horse and rider), builders carry the Build
    variants the engine picks per building, no action plays only the idle pose, and every attachment an animation
    attaches is defined in its file."""
    checked = 0
    for u in xml(K / 'data/protomods.xml').findall('unit'):
        anim, tac = u.findtext('animfile'), u.findtext('tactics')
        if not anim or not tac:
            continue
        anim_path, tac_path = K / 'art' / anim.replace(BS, '/'), K / 'data/tactics' / tac
        if not (anim_path.is_file() and tac_path.is_file()):
            continue                                   # vanilla animfile or vanilla tactics: the game's own business
        tactics = tac_path.read_text(encoding='utf-8')
        needed = {a.lower() for a in re.findall(r'<anim>(\w+)</anim>', tactics)}
        if re.search(r'<type>Build</type>', tactics):
            needed |= {'build', 'buildlifting', 'buildsaw', 'buildstaking'}
        texts = [anim_path.read_text(encoding='utf-8')]
        for inc in re.findall(r'<include>([^<]+)</include>', texts[0]):
            p = K / 'art' / inc.strip().replace(BS, '/')
            if p.is_file():
                texts.append(p.read_text(encoding='utf-8'))
        scopes = [sc for t in texts for sc in _anim_scopes(t)]
        assert scopes, '%s: %s has no top-level anims and no finished submodel' % (u.get('name'), anim)
        for scope, anims, defined, used in scopes:
            missing = needed - set(anims)
            assert not missing, '%s: %s %s lacks %s' % (u.get('name'), anim, scope, sorted(missing))
            assert used <= defined, '%s: undefined attachments %s' % (u.get('name'), sorted(used - defined))
        unit = [a for s, a, _, _ in scopes if not s]  # a unit: its files together (horse and rider); a building:
        for group in ([unit] if unit else [[a] for _, a, _, _ in scopes]):   # each finished state on its own
            idle = {f for a in group for f in a['idle']}
            for name in sorted(needed):
                played = {f for a in group for f in a[name]}
                assert not played <= idle, '%s: %s plays only the idle pose' % (u.get('name'), name)
        checked += 1
    assert checked >= 3                                # zpMonkKorean, zpMonkKorean2, zpHouseKorean


def test_korean_monastery_replaces_the_japanese_monk_techs():
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = list(techs['zpKoreanUnits'].iter('effect'))
    removed = [(e.text or '').strip() for e in eff if e.get('status') == 'unobtainable']
    assert removed == ['ypMonasteryJapaneseHealing', 'ypMonasteryJapaneseCombat', 'ypMonasteryKillingBlowUpgrade',
                       'ypMonasteryRangedSplash']
    slots = [(e.get('tech'), e.get('column')) for e in eff
             if e.get('type') == 'CommandAdd' and e.findtext('target') == 'ypMonastery']
    assert slots == [('zpMonasteryHyangyak', '1'), ('zpMonasteryDure', '2'), ('zpMonasteryPyeonjeon', '3'),
                     ('zpMonasterySeungbyeong', '4')]
    armed = [(e.text or '').strip() for e in eff if e.get('status') == 'obtainable'
             and not (e.text or '').strip().startswith('zpSeungbyeong')]     # the age-up techs: their own test
    assert armed == [s[0] for s in slots]
    for name, _ in slots:
        t = techs[name]
        assert t.findtext('status') == 'UNOBTAINABLE' and 'YPMonasteryTech' in [f.text for f in t.findall('flag')]
    targets = {e.findtext('target') for e in techs['zpMonasteryPyeonjeon'].iter('effect')}
    assert targets == {'zpMonkKorean', 'zpMonkKorean2'}
    assert all(e.get('relativity') == 'BasePercent' for e in techs['zpMonasteryPyeonjeon'].iter('effect')
               if e.get('subtype') == 'Damage')
    tactics = (K / 'data/tactics/zpmonkkorean.tactics').read_text(encoding='utf-8')
    assert '>Dure</name>' in tactics and '<modifytype>GatherRate</modifytype>' in tactics
    assert [(e.get('action'), e.findtext('target')) for e in techs['zpMonasteryDure'].iter('effect')] == [
        ('Dure', 'zpMonkKorean'), ('Dure', 'zpMonkKorean2')]


def test_market_offers_the_hunting_pair():
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    st = [(e.get('status'), (e.text or '').strip()) for e in techs['zpKoreanEconomy'].iter('effect')]
    assert st == [('obtainable', 'ypMarketHuntingDogs'), ('obtainable', 'ypMarketSteelTraps'),
                  ('unobtainable', 'ypMarketBerryDogs'), ('unobtainable', 'ypMarketBerryTraps')]


@needs_aop
def test_korean_house_carries_every_action_aop_adds_to_houses():
    """AoP techs ActionAdd actions to every AbstractHouse (Western cowboys, Christmas trees); a house without the
    action in its tactics silently misses the feature."""
    added = set(re.findall(r'action="(\w+)"[^>]*subtype="ActionAdd"[^>]*unittype="AbstractHouse"',
                           (AOP / 'data/techtreemods.xml').read_text(encoding='utf-8')))
    assert added, 'pattern no longer matches AoP techtreemods'
    house = xml(K / 'data/protomods.xml').find('unit')
    have = {a.findtext('name') for a in xml(K / 'data/tactics' / house.findtext('tactics')).findall('action')}
    assert added <= have, sorted(added - have)


@needs_aop
def test_generated_files_are_current_and_buildings_switch_at_the_first_upgrade():
    import build
    try:
        files = build.build()
    except Exception as e:   # no installed game / archive index on this machine
        pytest.skip('build needs the installed game: %s' % e)
    assert build.stale(files) == [], 'run python tools/build.py'
    for path in ('art/buildings/town_center/town_center.xml', 'art/buildings/asian_civs/bansho/bansho.xml',
                 'art/buildings/asian_civs/stable/stable.xml'):
        root = ET.fromstring(files[path].decode('utf-8'))
        tech = root.find('component/logic/japanese/logic')
        branch = tech.find('zpkoreanvisuals/logic')
        assert [c.tag for c in tech][-1] == 'zpkoreanvisuals' and [c.tag for c in branch][-1] == 'colonialize'
    langs = [d for d in os.listdir(K / 'data/strings') if (K / 'data/strings' / d).is_dir()]
    assert len(langs) == 15
    for lang in langs:
        assert 'data/strings/%s/stringmods.xml.xmb' % lang in files
    for path in ('data/civmods.xml.xmb', 'data/techtreemods.xml.xmb', 'data/homecityzpkoreans.xml.xmb',
                 'data/protomods.xml.xmb'):
        assert files[path][:4] == b'alz4', path
