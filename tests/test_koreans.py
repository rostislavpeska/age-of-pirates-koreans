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
                                                  'zpSeungbyeongIndustrial', 'zpSeungbyeongImperial', 'zpDisciplinedJochong',
                                                  'zpHonoredJochong', 'zpExaltedJochong', 'zpJochongPostIndustrial', 'zpJochongMeiji',
                                                  'zpDisciplinedJangchang', 'zpHonoredJangchang', 'zpExaltedJangchang',
                                                  'zpJochongPostImperial', 'zpDisciplinedGakgung', 'zpHonoredGakgung',
                                                  'zpExaltedGakgung', 'zpGakgungPostIndustrial', 'zpGakgungPostImperial']
    active = [e.text for e in techs[1].iter('effect') if e.get('type') == 'TechStatus' and e.get('status') == 'active']
    assert active == ['YPAge0Japanese', 'zpKoreanVisuals', 'zpKoreanBuildings', 'zpKoreanUnits', 'zpKoreanEconomy']
    assert all(60000 <= int(t.findtext('dbid')) < 61000 for t in techs)


def test_strings_flags_personality_and_sounds():
    ids = re.findall(r'_locid="(\d+)"', (K / 'data/strings/english/stringmods.xml').read_text(encoding='utf-8'))
    assert ids == [str(600000 + i) for i in range(83)]          # 600022-600027: zzTEST House benches A/B/C; 600048-49: zzTEST castle;
                                                                # 600077-600078: zzTEST Dock
                                                                # 600079-600080: zzTEST Consulate
                                                                # 600081-600082: zzTEST Monastery
                                                                # 600028-600037: the monks' random names
                                                                # 600038-600043: zzTEST TC/Barracks/Stable names
                                                                # 600044-600047: the Seungbyeong
                                                                # 600050-600058: the Jochong Musketeer
                                                                # 600059-600067: the Jangchang Spearman
                                                                # 600068-600076: the Gakgung Archer
    civ = xml(K / 'data/civmods.xml').find('civ')
    for field in ('homecityflagiconwpf', 'homecityflagbuttonwpf', 'postgameflagiconwpf'):
        assert (K / 'data/wpfg' / civ.findtext(field).replace(BS, '/')).is_file(), field
    assert (K / 'art/objects/flags/zpkoreans.ddt').stat().st_size == 174856        # vanilla flag profile
    pers = xml(K / 'game/ai/personalities/zpmyeongseong.personality')
    assert pers.findtext('forcedciv') == 'zpKoreans' and pers.findtext('nameID') == '600004'
    assert 'zpMyeongseong' in [p.text for p in xml(K / 'game/ai/personalities.xml').findall('Personality')]
    for s in xml(K / 'tools/korean_soundsets.xml').iter('sound'):
        assert (K / 'sound' / s.get('filename').replace(BS, '/')).is_file(), s.get('filename')


def test_fishing_boats_do_not_build_the_korean_house():
    """Owner's test 2026-10-09: "fishing boats can for some reason build houses". The House goes to every
    AbstractVillager, and every fishing boat (vanilla and AoP) is one: zpKoreanBuildings takes it off
    AbstractFishingBoat right after."""
    eff = [(e.get('type'), e.get('proto'), e.findtext('target'))
           for e in {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}['zpKoreanBuildings'].iter('effect')]
    add = eff.index(('CommandAdd', 'zpHouseKorean', 'AbstractVillager'))
    assert eff.index(('CommandRemove', 'zpHouseKorean', 'AbstractFishingBoat')) > add


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
                   ('CommandRemove', None, None, 'zpHouseKorean', None, None, 'AbstractFishingBoat'),   # not on boats
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
    files.append(K / 'sound/ypmilitaryrickshaw_snds.xml')         # the Asian wagon: builds Barracks and Stable
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
    assert {n for n in units if not n.startswith('zzTEST')} == {'zpHouseKorean', 'zpMonkKorean', 'zpMonkKorean2', 'zpSeungbyeong',
                                                               'zpJochong', 'zpJangchang', 'zpGakgung'}
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
    for rel in ('art/units/korean_monk/korean_monk_horse.xml', 'art/units/korean_monk/korean_monk_rider.xml'):
        anims = set(re.findall(r'^  <anim>(\w+)<', (K / rel).read_text(encoding='utf-8'), re.M))
        # owner's test 2026-10-09: Knockout aliased to Idle kept the knocked-out monk on the horse; vanilla mounted
        # heroes (Hetman, Ras, Emir) have none of these and fall with the death animation
        assert not anims & {'Knockout', 'KnockoutIdle', 'Recover'}, rel
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
    retexture; a special unit: only the Seungjang trains it, in the field, after zpMonasterySeungbyeong."""
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
    # owner 2026-10-09: "This one is special unit - not trainable from barracks" - only the Seungjang trains it
    assert [e.findtext('target') for e in eff if e.get('type') == 'CommandAdd' and e.get('proto') == 'zpSeungbyeong'] == []
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
    for name in ('zpMonkKorean', 'zpMonkKorean2', 'zpSeungbyeong', 'zpJochong', 'zpJangchang', 'zpGakgung'):   # coats
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
    removed = [(e.text or '').strip() for e in eff if e.get('status') == 'unobtainable'
               and not any(u in (e.text or '') for u in ('Ashigaru', 'Yumi', 'Samurai'))]   # infantry: own tests
    assert removed == ['ypMonasteryJapaneseHealing', 'ypMonasteryJapaneseCombat', 'ypMonasteryKillingBlowUpgrade',
                       'ypMonasteryRangedSplash']
    slots = [(e.get('tech'), e.get('column')) for e in eff
             if e.get('type') == 'CommandAdd' and e.findtext('target') == 'ypMonastery']
    assert slots == [('zpMonasteryHyangyak', '1'), ('zpMonasteryDure', '2'), ('zpMonasteryPyeonjeon', '3'),
                     ('zpMonasterySeungbyeong', '4')]
    armed = [(e.text or '').strip() for e in eff if e.get('status') == 'obtainable'
             and not (e.text or '').strip().startswith('zpSeungbyeong')      # the age-up techs: their own test
             and not any(u in (e.text or '') for u in ('Jochong', 'Jangchang', 'Gakgung'))]   # infantry: own tests
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
    # the castle switches on its OWN first upgrade (owner 2026-10-10: "as castle 1st upgrade Korean variant"): vanilla
    # Japanese castle before ypFrontierCastle, the Korean castle from it on
    root = ET.fromstring(files['art/buildings/asian_civs/castle/castle.xml'].decode('utf-8'))
    tech = next(lg.find('japanese/logic') for lg in root.iter('logic') if lg.find('japanese/logic') is not None)
    branch = tech.find('zpkoreanvisuals/logic')
    assert [c.tag for c in tech][-1] == 'zpkoreanvisuals'
    assert [c.tag for c in branch] == ['none', 'ypfrontiercastle'], [c.tag for c in branch]
    refs = [r.get('ref') for r in branch.find('ypfrontiercastle').iter('submodelref')]
    assert refs[-1] == 'korean_castle_built' and all(r.startswith('korean_castle') for r in refs), refs
    langs = [d for d in os.listdir(K / 'data/strings') if (K / 'data/strings' / d).is_dir()]
    assert len(langs) == 15
    for lang in langs:
        assert 'data/strings/%s/stringmods.xml.xmb' % lang in files
    for path in ('data/civmods.xml.xmb', 'data/techtreemods.xml.xmb', 'data/homecityzpkoreans.xml.xmb',
                 'data/protomods.xml.xmb'):
        assert files[path][:4] == b'alz4', path


# ---------------------------------------------------------------- the Korean infantry (Jochong Musketeer, Jangchang Spearman)
# owner 2026-10-09: "Jochong can stay Jochong", "the upgrades are must have ... vanilla always upgrades skins", "full
# retextures"; the Jangchang Spearman added as anti-cavalry (roster proposal accepted, "good, next one")
OWN_FIELDS = {'displaynameid', 'editornameid', 'animfile', 'icon', 'portraiticon', 'rollovertextid',
              'shortrollovertextid', 'dbid'}
INFANTRY = {
    # unit: (vanilla proto it copies, id, name, folder, vanilla animfile, ages, skin techs, {vanilla upgrade: own})
    'zpJochong': ('ypAshigaru', '22012', 'Jochong Musketeer', 'korean_jochong',
                  'art/units/asians/chinese/arquebusier/arquebusier.xml.xmb', (1, 2, 3),
                  ['none', 'zpdisciplinedjochong', 'zphonoredjochong'],
                  {'YPDisciplinedAshigaru': 'zpDisciplinedJochong', 'YPHonoredAshigaru': 'zpHonoredJochong',
                   'YPExaltedAshigaru': 'zpExaltedJochong'}),
    'zpJangchang': ('ypQiangPikeman', '22013', 'Jangchang Spearman', 'korean_jangchang',
                    'art/units/asians/chinese/qiang_pikeman/qiang_pikeman.xml.xmb', (1, 2, 2),   # fur cap unused
                    ['none', 'zpdisciplinedjangchang', 'zphonoredjangchang'],
                    {'YPDisciplinedQiangPikeman': 'zpDisciplinedJangchang', 'YPHonoredQiangPikeman': 'zpHonoredJangchang',
                     'YPExaltedQiangPikeman': 'zpExaltedJangchang'}),
    'zpGakgung': ('ypYumi', '22014', 'Gakgung Archer', 'korean_gakgung',
                  'art/units/asians/japanese/yumi/yumi.xml.xmb', (0, 1, 2),
                  ['none', 'zpdisciplinedgakgung', 'zphonoredgakgung'],
                  {'YPDisciplinedYumi': 'zpDisciplinedGakgung', 'YPHonoredYumi': 'zpHonoredGakgung',
                   'YPExaltedYumi': 'zpExaltedGakgung'}),
}
REPLACING = ('zpJochong', 'zpGakgung')          # in the place of the Ashigaru and the Yumi; the Jangchang is added
# skins that are a material variant of a body (owner 2026-10-10: "split industrial - one with red sleeves - industrial
# and one with white sleeves - fortress"): {unit: {tech branch: materialvariant index}}
VARIANTS = {'zpJangchang': {'zphonoredjangchang': '1'}}


def _game():
    try:
        import korean_sounds
        return korean_sounds.bartool()
    except BaseException:
        pytest.skip('game archives not readable here')


def _vanilla(path):
    bt, index = _game()
    return bt.decode(bt.read_entry(index[path]), True, 'lf')[0].decode('utf-8-sig')


def _canon(e):
    return (e.tag, sorted(e.attrib.items()), (e.text or '').strip(), [_canon(c) for c in e])


@pytest.mark.parametrize('unit', sorted(INFANTRY))
def test_infantry_is_its_vanilla_unit_with_its_own_look(unit):
    """Every field of the live vanilla unit it stands for except its identity, its strings and its art: the Jochong
    is the Ashigaru, the Jangchang the Qiang Pikeman."""
    van_name, uid, name, folder = INFANTRY[unit][:4]
    van = next(u for u in ET.fromstring(_vanilla('data/protoy.xml.xmb')).findall('unit') if u.get('name') == van_name)
    ours = {u.get('name'): u for u in xml(K / 'data/protomods.xml').findall('unit')}[unit]
    assert [_canon(c) for c in ours if c.tag not in OWN_FIELDS] == [_canon(c) for c in van if c.tag not in OWN_FIELDS]
    assert ours.get('id') == ours.findtext('dbid') == uid
    assert ours.findtext('animfile') == BS.join(['units', folder, folder + '.xml'])
    strings = dict(re.findall(r'_locid="(\d+)">([^<]*)<', (K / 'data/strings/english/stringmods.xml').read_text(encoding='utf-8')))
    assert strings[ours.findtext('displaynameid')] == name
    snds = xml(K / 'sound' / ('%s_snds.xml' % unit.lower()))
    assert snds.find('protounit').get('name') == unit
    assert {s.get('name') for s in snds.iter('soundset')} >= {'Korean_Soldier_Select', 'Korean_Soldier_Attack'}


@needs_aop
def test_infantry_replaces_its_vanilla_unit_wherever_it_is_trained():
    """Every vanilla and AoP building or unit that trains the Ashigaru (the Yumi) trains the Jochong (the Gakgung) for
    Korea, in the same slot (vanilla campaign protos ypSPC* aside); the replaced units are switched off for Korea. The
    Jangchang, an added unit, sits in the free Barracks column 4."""
    units = (ET.fromstring(_vanilla('data/protoy.xml.xmb')).findall('unit') + xml(AOP / 'data/protomods.xml').findall('unit'))
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = list(techs['zpKoreanUnits'].iter('effect'))
    adds = lambda proto: {(e.findtext('target'), e.get('page'), e.get('column')) for e in eff
                          if e.get('type') == 'CommandAdd' and e.get('proto') == proto}
    enable = {e.findtext('target'): e.get('amount') for e in eff if e.get('subtype') == 'Enable'}
    for unit in REPLACING:
        van = INFANTRY[unit][0]
        want = set()
        for u in units:
            if not u.get('name', '').startswith('ypSPC'):
                want |= {(u.get('name'), t.get('page'), t.get('column')) for t in u.findall('train') if t.text == van}
        assert want and adds(unit) == want, unit
        assert enable[unit] == '1.00' and enable[van] == '0.00', unit
    assert adds('zpJangchang') == {('ypBarracksJapanese', '0', '4')} and enable['zpJangchang'] == '1.00'
    columns = [e.get('column') for e in eff if e.get('type') == 'CommandAdd' and e.findtext('target') == 'ypBarracksJapanese'
               and e.get('page') == '0']
    assert sorted(columns) == ['0', '1', '4']                      # Gakgung, Jochong, Jangchang (no Seungbyeong)


def test_samurai_is_off_for_korea_only():
    """Owner 2026-10-09: "strip Samurai from korean barracks", "We must NOT touch Japan at all": the Korean-only
    zpKoreanUnits switches the Samurai (ypKensei) and its three Barracks upgrades off; no record of this add-on
    touches a Japanese unit, tech or building otherwise."""
    techs = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    eff = list(techs['zpKoreanUnits'].iter('effect'))
    assert [e.get('amount') for e in eff if e.get('subtype') == 'Enable' and e.findtext('target') == 'ypKensei'] == ['0.00']
    status = {e.text: e.get('status') for e in eff if e.get('type') == 'TechStatus'}
    for up in ('YPDisciplinedSamurai', 'YPHonoredSamurai', 'YPExaltedSamurai'):
        assert status[up] == 'unobtainable', up
    assert 'ypKensei' not in [e.get('proto') for e in eff if e.get('type') == 'CommandAdd']
    others = [t.get('name') for t in techs.values() if t.get('name') != 'zpKoreanUnits'
              and ('ypKensei' in ET.tostring(t, encoding='unicode') or 'Samurai<' in ET.tostring(t, encoding='unicode'))]
    assert others == []


@pytest.mark.parametrize('unit', sorted(INFANTRY))
def test_infantry_upgrades_are_the_vanilla_upgrades(unit):
    """Owner 2026-10-09: "the upgrades are must have". The vanilla unit's three upgrades field for field on the Korean
    unit (ages, costs, effects), in the Barracks; for the Jochong the Japanese Ashigaru ones are off for Korea and the
    two vanilla techs that grant them (post-industrial start, Meiji Restoration) grant the Jochong's."""
    van_name, mapping = INFANTRY[unit][0], dict(INFANTRY[unit][7], **{INFANTRY[unit][0]: unit})
    van = {t.get('name'): t for t in ET.fromstring(_vanilla('data/techtreey.xml.xmb')).findall('tech')}
    ours = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    ren = lambda s: mapping.get(s, s)
    eff = lambda t: sorted((e.get('type'), e.get('subtype'), e.get('amount'), e.get('relativity'), e.get('allactions'),
                            e.get('action'), ren(e.findtext('target') or e.get('proto') or e.get('unittype') or ''))
                           for e in t.iter('effect'))
    k = list(ours['zpKoreanUnits'].iter('effect'))
    status = {(e.text or '').strip(): e.get('status') for e in k if e.get('type') == 'TechStatus'}
    column = [e.get('column') for e in k if e.get('proto') == unit][0]       # its Barracks column (listed first)
    for a, j in INFANTRY[unit][7].items():
        v, o = van[a], ours[j]
        for f in ('researchpoints', 'status'):
            assert o.findtext(f) == v.findtext(f), (j, f)
        # the Japanese Barracks look (owner's test 2026-10-09: "weird upgrade icon"): the hand-infantry medallion for
        # the spearman, never the Chinese War Academy layout flag (it moved the upgrade one column off)
        assert o.findtext('icon') == v.findtext('icon').replace('_pikeman.png', '_infantry.png'), j
        assert [(c.get('resourcetype'), c.text) for c in o.findall('cost')] == [(c.get('resourcetype'), c.text) for c in v.findall('cost')]
        assert [f.text for f in o.findall('flag')] == [f.text for f in v.findall('flag') if f.text != 'YPGridShiftRowRightOne']
        assert [p.text for p in o.iter('techstatus')] == [ren(p.text) for p in v.iter('techstatus')]
        assert eff(o) == eff(v), j
        assert status[j] == 'obtainable'
        assert (j, '1', column, 'ypBarracksJapanese') in [(e.get('tech'), e.get('page'), e.get('column'), e.findtext('target')) for e in k]
    if unit not in REPLACING:
        return
    for a in INFANTRY[unit][7]:
        assert status[a] == 'unobtainable'
    # every vanilla tech that grants the replaced unit's upgrades grants the Korean ones through an armed shadow
    shadows = {}
    for name, tt in ours.items():
        pre = [p.text for p in tt.iter('techstatus')]
        if 'Shadow' in [f.text for f in tt.findall('flag')] and len(pre) == 1:
            shadows.setdefault(pre[0], []).append((name, [(e.text or '').strip() for e in tt.iter('effect')]))
    granting = 0
    for vname, vt in van.items():
        granted = [x for x in INFANTRY[unit][7] if x in {(e.text or '').strip() for e in vt.iter('effect') if e.get('status') == 'active'}]
        if not granted or vname in INFANTRY[unit][7]:
            continue
        granting += 1
        want = [INFANTRY[unit][7][x] for x in granted]
        hits = [n for n, e in shadows.get(vname, []) if e == want]
        assert len(hits) == 1 and status[hits[0]] == 'obtainable', (unit, vname, want)
    assert granting >= 2, unit


def test_upgrade_buttons_are_visible_from_the_start():
    """Owner 2026-10-10: "These techs should be visible permanently", "That's off pattern!!!! Check other civs. tests
    should cover that". A building shows an upgrade button only once the tech's prereqs other than its age are met: a
    button tech chained to a shadow that an age-up fires stays hidden until then (the Honored Jangchang until Fortress).
    Vanilla: every unit with a free Disciplined shadow (Chinese, Indian, Japanese) has an Honored that needs only
    Industrialize. So every Korean button tech needs only ages and the button before it in its own slot."""
    ages = {'Colonialize', 'Fortressize', 'Industrialize', 'Imperialize'}
    van = {t.get('name'): t for t in ET.fromstring(_vanilla('data/techtreey.xml.xmb')).findall('tech')}
    low = {n.lower(): n for n in van}
    pattern = []
    for n in van:
        m = re.fullmatch(r'ypDisciplined(\w+)Shadow', n, re.I)
        honored = low.get(('ypHonored' + m.group(1)).lower()) if m else None
        if honored:
            assert [p.text for p in van[honored].iter('techstatus')] == ['Industrialize'], honored
            pattern.append(honored)
    assert len(pattern) >= 7                                   # Arquebusier, Changdao, Iron Flail, Yabusame, Howdah ...
    ours = {t.get('name'): t for t in xml(K / 'data/techtreemods.xml').findall('tech')}
    buttons = {}
    for t in ours.values():
        for e in t.iter('effect'):
            if e.get('type') == 'CommandAdd' and e.get('tech'):
                buttons[e.get('tech')] = (e.findtext('target'), e.get('page'), e.get('column'))
    own = [b for b in buttons if b in ours]
    assert len(own) >= 12
    armed = {(e.text or '').strip() for t in ours.values() for e in t.iter('effect')
             if e.get('type') == 'TechStatus' and e.get('status') in ('obtainable', 'active')}
    for name in own:
        for p in ours[name].iter('techstatus'):
            assert p.text in ages or buttons.get(p.text) == buttons[name], (name, p.text)
        # an UNOBTAINABLE tech nobody arms never shows at all
        assert ours[name].findtext('status') != 'UNOBTAINABLE' or name in armed, name


@pytest.mark.parametrize('unit', sorted(INFANTRY))
def test_infantry_animfile_switches_skins(unit):
    """Owner 2026-10-09: "vanilla always upgrades skins" - the vanilla animfile: the same animations, the unit's own
    bodies switched by its own upgrades (Exalted keeps the Honored skin), the Jochong's crafted jeollip on every age;
    every file it names exists in the repo or in the game."""
    folder, src, ages, tags = INFANTRY[unit][3:7]
    bt, index = _game()
    ours = (K / 'art/units' / folder / (folder + '.xml')).read_text(encoding='utf-8')
    assert set(_top_anims(ours)) == set(_top_anims(_vanilla(src)))
    logic = ET.fromstring(ours).find('component/logic')
    assert logic.get('type') == 'Tech' and [c.tag for c in logic] == tags
    for branch, age in zip(logic, ages):
        for state in ('normal', 'lowpoly'):
            s = branch.find('logic/' + state)
            assert [f.text for f in s.iter('file')] == [BS.join(['units', folder, '%s_age%d' % (folder, age)])]
            want = VARIANTS.get(unit, {}).get(branch.tag)
            assert [[c.tag for c in r] for r in s.iter('assetreference')] == [['file'] + (['materialvariant'] if want else [])]
            assert [m.get('index') for m in s.iter('materialvariant')] == ([want] if want else []), (unit, branch.tag)
            attach = {(a.get('a'), a.get('tobone')) for a in s.findall('attach')}
            if unit == 'zpJochong':
                assert attach == {('gun_age%d' % age, 'BIP01 PROP1'), ('hats', 'HEAD')}
            elif unit == 'zpJangchang':
                assert attach == {('pikes', 'Pikeman Prop1')}
            else:
                assert attach == set()                             # the Yumi attaches bow and quiver for all ages
    if unit == 'zpGakgung':
        comp = ET.fromstring(ours).find('component')
        assert {(a.get('a'), a.get('tobone')) for a in comp.findall('attach')} == {('quivers', 'SPINE1'), ('bows', 'Bip01 Prop1')}
        assert BS.join(['units', 'infantry', 'azap', 'azap_bow']) in ours and 'longbow_bows' not in ours
    if unit == 'zpJochong':
        assert BS.join(['units', folder, 'korean_jochong_hat']) in ours and 'arquebusier_age3_hat' not in ours
    for f in set(re.findall(r'<file>([^<]+)</file>', ours)):
        p = 'art/' + f.replace(BS, '/').lower()
        if f.startswith(BS.join(['units', folder, ''])):
            assert (K / (p + '.gr2')).is_file() and (K / (p + '.material')).is_file(), f
        else:
            assert any(p + ext in index for ext in ('.gr2', '.xmb', '')), f


@pytest.mark.parametrize('unit', sorted(INFANTRY))
def test_infantry_materials_resolve_within_the_texture_budget(unit):
    """Owner 2026-10-09: "unit textures 1024 only", "hats only 512px". Every texture a unit's materials name is a repo
    DDT of that size or a vanilla map by archive path (maps the retexture did not change); the jeollip has no Details
    (no player colour, as 41 of 198 vanilla hats)."""
    import struct
    folder, ages = INFANTRY[unit][3], INFANTRY[unit][5]
    bt, index = _game()
    mats = sorted((K / 'art/units' / folder).glob('*.material'))
    want = ['%s_age%d.material' % (folder, a) for a in sorted(set(ages))] + (['korean_jochong_hat.material'] if unit == 'zpJochong' else [])
    assert [m.name for m in mats] == want
    import korean_infantry as ki
    spec = ki.UNITS[folder]
    own = set()
    for m in mats:
        blocks = list(xml(m).iter('parameters'))
        # a skin variant (VARIANTS) has its own <parameters variant="N"> block, every other material one block
        variants = sorted(set(VARIANTS.get(unit, {}).values())) if m.stem in [s for s, v in spec['materials'].items() if len(v) > 3] else []
        assert [b.get('variant') for b in blocks] == [None] + variants, m.name
        # the vanilla model's own materialdef, per model (owner's test 2026-10-09: the Gakgung's cards drew as solid
        # squares under default_doublesided; vanilla changdao_1/2 are default_doublesided_cutout, changdao_0 is not)
        van = spec['materials'][m.stem][1]
        want = 'default'                                             # the crafted jeollip
        if van:
            src = 'art/' + (spec.get('tex', spec['van']) + van).replace(BS, '/').lower() + '.material.xmb'
            want = re.search(r'<materialdef name="([^"]+)"', _vanilla(src)).group(1)
        assert xml(m).find('submaterial/materialdef').get('name') == want, m.name
        hat = 'hat' in m.name
        for b in blocks:
            tex = {t.get('name'): t.get('override') for t in b.iter('texture')}
            assert set(tex) == ({'BaseColor', 'Normals', 'Masks'} | (set() if hat else {'Details'}))
            for ch, path in tex.items():
                p = path.replace(BS, '/')
                if p.startswith('units/%s/' % folder):
                    ddt = (K / 'art' / (p + '.ddt')).read_bytes()
                    assert ddt[:4] == b'RTS3' and struct.unpack_from('<II', ddt, 8) == ((512, 512) if hat else (1024, 1024)), p
                    if unit == 'zpGakgung' and ch == 'BaseColor':
                        assert ddt[5:7] == bytes([4, 9]), p            # DXT5: the Changdao's cut-out cards
                    own.add(p.lower())
                else:
                    assert 'art/%s.ddt' % p.lower() in index, p
    assert len(list((K / 'art/units' / folder / 'textures').glob('*.ddt'))) == len(own)


def test_infantry_models_rebuild_identically():
    """The bodies are the vanilla Arquebusier, Qiang pikeman and Changdao GR2s byte for byte; the jeollip GR2 rebuilds from its
    frozen geometry (tools/infantry_texture/jeollip_parts.json) through AoP's INC-187-safe writer."""
    import korean_infantry_model
    try:
        files = korean_infantry_model.build()
    except SystemExit:
        pytest.skip('needs the installed game and the AoP checkout')
    assert len(files) == 9                                       # the Jangchang's fur-cap body 0 is unused
    for path, data in files.items():
        assert open(path, 'rb').read() == data, 'run python tools/korean_infantry_model.py: %s' % path


def _dxt5_mip(data, level):
    """RGBA array of one mip of an RTS3 DXT5 DDT, decoded by Pillow's own BC3 reader (independent of our writer)."""
    import io
    import struct
    import numpy as np
    from PIL import Image
    w, h = struct.unpack_from('<II', data, 8)
    off, size = struct.unpack_from('<II', data, 16 + 8 * level)
    w, h = w >> level, h >> level
    dds = struct.pack('<4sI', b'DDS ', 124) + struct.pack('<IIIIII', 0x1007 | 0x80000, h, w, size, 0, 1) + bytes(44)
    dds += struct.pack('<II4sIIIII', 32, 4, b'DXT5', 0, 0, 0, 0, 0) + struct.pack('<IIII', 0x1000, 0, 0, 0) + bytes(4)
    return np.asarray(Image.open(io.BytesIO(dds + data[off:off + size])).convert('RGBA')).astype(int)


@pytest.mark.parametrize('unit', sorted(INFANTRY))
def test_infantry_basecolor_keeps_the_vanilla_cut_out_alpha(unit):
    """Owner's test 2026-10-09: black squares over the Honored Gakgung helmets - "check the alpha channel ... test for
    missing alpha". A BaseColor whose vanilla source is a DXT5 with cut-out alpha (format 9, alpha flag 4: plumes and
    ornaments on cards) must stay one in the same profile (mips to 4x4), with colour - not black - under the cut-out
    texels in the smaller mips (an RGBA resize premultiplies: black cards in game)."""
    import struct
    import korean_infantry as ki
    bt, index = _game()
    folder = INFANTRY[unit][3]
    spec = ki.UNITS[folder]
    checked = 0
    for model, (sub, van, maps, *variants) in spec['materials'].items():
        if not maps.get('BaseColor') or van is None:
            continue
        vkey = 'art/' + (spec.get('tex', spec['van']) + 'textures' + BS + '%s_%s_BaseColor' % (van, sub)).replace(BS, '/').lower() + '.ddt'
        vhead = bt.read_entry(index[vkey])[:8]
        ours = (K / 'art/units' / folder / 'textures' / ('%s_matA_BaseColor.ddt' % model)).read_bytes()
        if vhead[6] != 9:
            continue                                            # no cut-out alpha in the vanilla source
        checked += 1
        assert list(ours[4:8]) == list(vhead[4:8]), (model, list(ours[4:8]), list(vhead[4:8]))
        assert struct.unpack_from('<II', ours, 16 + 8 * (ours[7] - 1))[1] == 16, model    # last mip = one 4x4 block
        for level in (2, 4):
            a = _dxt5_mip(ours, level)
            cut = a[..., 3] < 64
            assert cut.any() and a[cut][:, :3].mean() > 20, (model, level, 'black under the cut-out texels')
    assert checked == (3 if unit == 'zpGakgung' else 0), (unit, checked)


@needs_aop
def test_materials_keep_their_source_materialdef():
    """Owner's game tests 2026-10-09: the Gakgung Archer's cards drew solid (one default_doublesided for the unit, vanilla
    changdao_1/2 are default_doublesided_cutout). AoP's aoe-xml material_source.py on every material of the add-on: the
    def treats the BaseColor alpha (cut / ignore) as the vanilla material it retextures does, no finding at all."""
    import importlib.util
    _game()
    spec = importlib.util.spec_from_file_location('material_source', AOP / '.claude/skills/aoe-xml/scripts/material_source.py')
    ms = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ms)
    data = ms.load_index()
    mats = sorted((K / 'art').rglob('*.material'))
    found = [m for p in mats for part in ms.check_file(str(p), str(K), data) for m in part]
    assert len(mats) > 20 and found == []
