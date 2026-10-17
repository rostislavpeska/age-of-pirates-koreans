#!/usr/bin/env python
"""Korean cavalry as separate units on the original vanilla textures (audit 2026-10-13-cursor-06).

Geomsabok (zpKoreanLancer, 22023) is the Naginata Rider on the Yabusame horse: the community
concept's armored hand cavalry, here with a woldo.
Gungdo Cavalry (zpKoreanHorseArcher, 22024) is the Yabusame on the Naginata horse: WoL's horse archer.
Pyeongon Cavalry (zpKoreanIronFlail, 22025) is the Chinese Iron Flail rider on the Yabusame horse.
Pyeongon (편곤) is the Joseon cavalry flail. The rider mesh is the vanilla one. A Korean rider is not modeled (technical debt).

Each unit has its own GR2 clones and its own animfiles. Geometry, UVs and vertex data are the
vanilla bytes. Every texture path in the materials is still the vanilla archive path, so a later
retexture only replaces those paths (the infantry route, tools/infantry_texture/, not a hue shift).
Animation clips stay the vanilla library. The horse MESH is the other unit's horse:

  Lancer horse ages:       Yabusame horse 0 (Colonial and Disciplined; the Yabusame has no middle
                           horse), Yabusame horse 2 (Honored). Clips are the Naginata horse set.
  Horse archer horse ages: Naginata horse (Colonial), Naginata horse 2 (Honored). The four posed
                           Yabusame bow-shot meshes have no Naginata equivalent, so those slots use
                           the cloned Naginata horse. Clips are the Yabusame horse set.

The Naginata horse GR2 is oodle-compressed. The game reads it. The repo's GR2 tools do not.

    python tools/korean_cavalry.py     # write the GR2 clones and the proto / tech / string records
                                       # animfiles and materials are written by tools/build.py
"""
import copy
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import korean_visuals  # noqa: E402

BS = chr(92)
BARTOOL = korean_visuals.BARTOOL

# dest basename -> source basename (archive file name, any case). The source folder is on the unit.
LANCER_BODY = {
    'korean_lancer_rider_0': 'naginata_rider_0',
    'korean_lancer_rider_0_lp': 'naginata_rider_0_lp',
    'korean_lancer_rider_1': 'naginata_rider_1',
    'korean_lancer_rider_1_lp': 'naginata_rider_1_lp',
    'korean_lancer_rider_2': 'naginata_rider_2',
    'korean_lancer_rider_2_lp': 'naginata_rider_2_lp',
    'korean_lancer_lance': 'naginata_lance',
}
LANCER_HORSE = {
    'korean_lancer_horse_0': 'yabusameHorse_0',
    'korean_lancer_horse_0_lp': 'yabusameHorse_0_lp',
    'korean_lancer_horse_2': 'yabusameHorse_2',
    'korean_lancer_horse_2_lp': 'yabusameHorse_2_lp',
}
ARCHER_BODY = {
    'korean_horse_archer_rider_0': 'yabusameRider_0',
    'korean_horse_archer_rider_0_lp': 'yabusameRider_0_lp',
    'korean_horse_archer_rider_2': 'yabusameRider_2',
    'korean_horse_archer_rider_2_lp': 'yabusameRider_2_lp',
    'korean_horse_archer_bow': 'yabusameRider_bow',
    'korean_horse_archer_sword': 'steppe_rider_sword',
}
ARCHER_HORSE = {
    'korean_horse_archer_horse_0': 'naginata_horse',
    'korean_horse_archer_horse_2': 'naginata_horse_2',
}
# The flail is skinned into the rider GR2. Horse ages are the light Yabusame horse: Colonial uses horse 0,
# Honored uses horse 2. iron_flail_horse_walk00 / iron_flail_rider_walk00 are the Walk ANIMATIONS, not posed meshes:
# they stay the vanilla archive paths (FLAIL_ANIMS; d631c26 2026-10-15 fixed the horse walk, which had pointed at the
# static horse_0 mesh).
FLAIL_BODY = {
    'korean_iron_flail_rider_0': 'iron_rider_0',
    'korean_iron_flail_rider_0_lp': 'iron_rider_0_lp',
    'korean_iron_flail_rider_2': 'iron_rider_2',
    'korean_iron_flail_rider_2_lp': 'iron_rider_2_lp',
}
FLAIL_ANIMS = ('units\\asians\\chinese\\iron_flail\\iron_flail_horse_walk00',
               'units\\asians\\chinese\\iron_flail\\iron_flail_rider_walk00')
FLAIL_HORSE = {
    'korean_iron_flail_horse_0': 'yabusameHorse_0',
    'korean_iron_flail_horse_1': 'yabusameHorse_2',
}

UNITS = {
    'korean_lancer': dict(
        proto='zpKoreanLancer', vanilla='ypNaginataRider', uid='22023',
        display='Geomsabok', editor='CAV Geomsabok',
        rollover='Armored cavalry with a woldo. Good against infantry.',
        short='Polearm cavalry, good against infantry',
        strings=(600095, 600096, 600097, 600098),
        horse_src='Art/units/asians/japanese/naginata_rider/naginata_rider_horse.xml.XMB',
        rider_src='Art/units/asians/japanese/naginata_rider/naginata_rider.xml.XMB',
        body=LANCER_BODY, horse=LANCER_HORSE,
        body_dir='units/asians/japanese/naginata_rider/',
        horse_dir='units/asians/japanese/yabusame/',
        sword_dir=None,
        # longest paths first. The Disciplined age has no Yabusame horse of its own, so it keeps horse 0.
        replace=(
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider.xml',
             'units\\korean_lancer\\korean_lancer_rider.xml'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_2_lp',
             'units\\korean_lancer\\korean_lancer_rider_2_lp'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_1_lp',
             'units\\korean_lancer\\korean_lancer_rider_1_lp'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_0_lp',
             'units\\korean_lancer\\korean_lancer_rider_0_lp'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_2',
             'units\\korean_lancer\\korean_lancer_rider_2'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_1',
             'units\\korean_lancer\\korean_lancer_rider_1'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_rider_0',
             'units\\korean_lancer\\korean_lancer_rider_0'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_lance',
             'units\\korean_lancer\\korean_lancer_lance'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_horse_2',
             'units\\korean_lancer\\korean_lancer_horse_2'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_horse_1',
             'units\\korean_lancer\\korean_lancer_horse_0'),
            ('units\\asians\\japanese\\naginata_rider\\naginata_horse',
             'units\\korean_lancer\\korean_lancer_horse_0'),
        ),
        techs=(('ypdisciplinednaginatarider', 'zpdisciplinedkoreanlancer'),
               ('yphonorednaginatarider', 'zphonoredkoreanlancer')),
        lp_pairs=True,
    ),
    'korean_horse_archer': dict(
        proto='zpKoreanHorseArcher', vanilla='ypYabusame', uid='22024',
        display='Gungdo Cavalry', editor='CAV Gungdo Cavalry',
        rollover='Horse archers. Good against artillery.',
        short='Mounted archer',
        strings=(600104, 600105, 600106, 600107),
        horse_src='Art/units/asians/japanese/yabusame/yabusamehorse.xml.XMB',
        rider_src='Art/units/asians/japanese/yabusame/yabusamerider.xml.XMB',
        body=ARCHER_BODY, horse=ARCHER_HORSE,
        body_dir='units/asians/japanese/yabusame/',
        horse_dir='units/asians/japanese/naginata_rider/',
        sword_dir='units/asians/chinese/steppe_rider/',
        replace=(
            ('units\\asians\\japanese\\yabusame\\yabusameRider.xml',
             'units\\korean_horse_archer\\korean_horse_archer_rider.xml'),
            ('units\\asians\\japanese\\yabusame\\yabusameRider_2_lp',
             'units\\korean_horse_archer\\korean_horse_archer_rider_2_lp'),
            ('units\\asians\\japanese\\yabusame\\yabusameRider_0_lp',
             'units\\korean_horse_archer\\korean_horse_archer_rider_0_lp'),
            ('units\\asians\\japanese\\yabusame\\yabusameRider_2',
             'units\\korean_horse_archer\\korean_horse_archer_rider_2'),
            ('units\\asians\\japanese\\yabusame\\yabusameRider_0',
             'units\\korean_horse_archer\\korean_horse_archer_rider_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameRider_bow',
             'units\\korean_horse_archer\\korean_horse_archer_bow'),
            ('units\\asians\\chinese\\steppe_rider\\steppe_rider_sword',
             'units\\korean_horse_archer\\korean_horse_archer_sword'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_attackRanged03',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_attackRanged02',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_attackRanged01',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_attackRanged00',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_2_lp',
             'units\\korean_horse_archer\\korean_horse_archer_horse_2'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_0_lp',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_2',
             'units\\korean_horse_archer\\korean_horse_archer_horse_2'),
            ('units\\asians\\japanese\\yabusame\\yabusameHorse_0',
             'units\\korean_horse_archer\\korean_horse_archer_horse_0'),
        ),
        techs=(('yphonoredyabusame', 'zphonoredkoreanhorsearcher'),),
        lp_pairs=False,
    ),
    'korean_iron_flail': dict(
        proto='zpKoreanIronFlail', vanilla='ypIronFlail', uid='22025',
        display='Pyeongon Cavalry', editor='CAV Pyeongon Cavalry',
        rollover='Scout cavalry with a flail. Good against archers and artillery.',
        short='Scout cavalry, good against archers',
        strings=(600112, 600113, 600114, 600115),
        horse_src='Art/units/asians/chinese/iron_flail/iron_flail.xml.XMB',
        rider_src='Art/units/asians/chinese/iron_flail/iron_flail_rider.xml.XMB',
        body=FLAIL_BODY, horse=FLAIL_HORSE,
        body_dir='units/asians/chinese/iron_flail/',
        horse_dir='units/asians/japanese/yabusame/',
        sword_dir=None,
        # An extra Stable unit, not a replacement: China keeps its Iron Flail. Column 2 is free
        # (Geomsabok is 0, Gungdo Cavalry is 1). The icon stays the vanilla Iron Flail icon.
        extra=True, column='2', keep_icons=True,
        note=('  <!-- zpKoreanIronFlail, displayed as Pyeongon Cavalry (Joseon cavalry flail). Vanilla ypIronFlail '
              'rider, flail skinned in, on the Yabusame horse. Own GR2 clones and animfiles '
              '(tools/korean_cavalry.py). A Korean rider mesh is technical debt. Textures are still '
              'the vanilla archive paths. -->\n'),
        replace=(
            ('units\\asians\\chinese\\iron_flail\\iron_flail_whip.xml',
             'units\\korean_iron_flail\\korean_iron_flail_whip.xml'),
            ('units\\asians\\chinese\\iron_flail\\iron_flail_rider.xml',
             'units\\korean_iron_flail\\korean_iron_flail_rider.xml'),
            ('units\\asians\\chinese\\iron_flail\\iron_rider_2_lp',
             'units\\korean_iron_flail\\korean_iron_flail_rider_2_lp'),
            ('units\\asians\\chinese\\iron_flail\\iron_rider_0_lp',
             'units\\korean_iron_flail\\korean_iron_flail_rider_0_lp'),
            ('units\\asians\\chinese\\iron_flail\\iron_rider_2',
             'units\\korean_iron_flail\\korean_iron_flail_rider_2'),
            ('units\\asians\\chinese\\iron_flail\\iron_rider_0',
             'units\\korean_iron_flail\\korean_iron_flail_rider_0'),
            ('units\\asians\\chinese\\iron_flail\\iron_flail_horse_1',
             'units\\korean_iron_flail\\korean_iron_flail_horse_1'),
            ('units\\asians\\chinese\\iron_flail\\iron_flail_horse_0',
             'units\\korean_iron_flail\\korean_iron_flail_horse_0'),
        ),
        techs=(('yphonoredironflail', 'zphonoredkoreanironflail'),),
        lp_pairs=False,
        # The whip include is declared and never attached. It stays, pointed at our copy, and that
        # copy still uses the vanilla oprichnik whip meshes (archive paths, not clones).
        extras=(('Art/units/asians/chinese/iron_flail/iron_flail_whip.xml.XMB',
                 'art/units/korean_iron_flail/korean_iron_flail_whip.xml'),),
        vanilla_anims=FLAIL_ANIMS,
    ),
}

# vanilla upgrade -> (own tech, dbid, display string, rollover string, newname string)
# newname is what the unit is called after the upgrade. Disciplined and Honored share a rollover;
# Exalted has its own, as the other Korean units do.
UPGRADES = {
    'ypNaginataRider': (
        ('YPDisciplinedNaginataRider', 'zpDisciplinedKoreanLancer', 60028, 600099, 600102, 600099),
        ('YPHonoredNaginataRider', 'zpHonoredKoreanLancer', 60029, 600100, 600102, 600100),
        ('YPExaltedNaginataRider', 'zpExaltedKoreanLancer', 60030, 600101, 600103, 600101),
    ),
    'ypYabusame': (
        ('YPHonoredYabusame', 'zpHonoredKoreanHorseArcher', 60033, 600108, 600110, 600108),
        ('YPExaltedYabusame', 'zpExaltedKoreanHorseArcher', 60034, 600109, 600111, 600109),
    ),
    'ypIronFlail': (
        ('YPHonoredIronFlail', 'zpHonoredKoreanIronFlail', 60037, 600116, 600118, 600116),
        ('YPExaltedIronFlail', 'zpExaltedKoreanIronFlail', 60038, 600117, 600119, 600117),
    ),
}
SHADOWS = (
    ('zpKoreanLancerPostIndustrial', 60031, 'ypPostIndustrialJapanese',
     ('zpDisciplinedKoreanLancer', 'zpHonoredKoreanLancer')),
    ('zpKoreanLancerPostImperial', 60032, 'ypPostImperialJapanese',
     ('zpExaltedKoreanLancer',)),
    ('zpKoreanHorseArcherPostIndustrial', 60035, 'ypPostIndustrialJapanese',
     ('zpHonoredKoreanHorseArcher',)),
    ('zpKoreanHorseArcherPostImperial', 60036, 'ypPostImperialJapanese',
     ('zpExaltedKoreanHorseArcher',)),
    ('zpKoreanIronFlailPostIndustrial', 60039, 'ypPostIndustrialJapanese',
     ('zpHonoredKoreanIronFlail',)),
    ('zpKoreanIronFlailPostImperial', 60040, 'ypPostImperialJapanese',
     ('zpExaltedKoreanIronFlail',)),
)

_GR2 = {}
_MAT = {}


def vanilla(path):
    out = subprocess.run([sys.executable, BARTOOL, 'cat', path], capture_output=True, check=True)
    return out.stdout.decode('utf-8-sig').replace('\r\n', '\n')


def _extract(pattern):
    tmp = tempfile.mkdtemp(prefix='aop-cav-')
    subprocess.run([sys.executable, BARTOOL, 'extract', pattern, '-o', tmp],
                   capture_output=True, check=True)
    found = {}
    for root, _, files in os.walk(tmp):
        for name in files:
            if name.lower().endswith('.gr2'):
                found[name.lower()] = open(os.path.join(root, name), 'rb').read()
    return found


def gr2_bytes():
    """Every cloned model, keyed by its vanilla file name in lower case."""
    if not _GR2:
        for pattern in ('art/units/asians/japanese/naginata_rider/*.gr2',
                        'art/units/asians/japanese/yabusame/*.gr2',
                        'art/units/asians/chinese/steppe_rider/steppe_rider_sword.gr2',
                        'art/units/asians/chinese/iron_flail/*.gr2'):
            _GR2.update(_extract(pattern))
    return _GR2


def material_text(folder, source_name):
    key = (folder + source_name).lower()
    if key not in _MAT:
        _MAT[key] = vanilla('Art/' + folder + source_name + '.material.XMB')
    text = _MAT[key]
    assert '<materialdef name="' in text, source_name
    assert 'asians' in text, source_name
    return text


def _rewrite(unit):
    """Horse and rider animfiles. A path lives in only one of them; every listed path must occur."""
    texts = {kind: vanilla(unit[kind + '_src']) for kind in ('horse', 'rider')}
    anims = {kind: set(re.findall(r'<file>(animation_library[^<]*)</file>', text)) for kind, text in texts.items()}
    for old, new in unit['replace']:
        assert sum(text.count(old) for text in texts.values()) >= 1, old
        texts = {kind: text.replace(old, new) for kind, text in texts.items()}
    for path in unit.get('vanilla_anims', ()):
        assert sum(text.count('<file>%s</file>' % path) for text in texts.values()) == 1, path
    for kind in texts:
        for old, new in unit['techs']:
            texts[kind], n = re.subn(r'(</?)%s>' % old, r'\1%s>' % new, texts[kind])
            assert n == 2, (unit['proto'], kind, old, n)
        assert 'asians\\' not in own_paths(unit, texts[kind]) and 'steppe_rider' not in texts[kind], (unit['proto'], kind)
        assert set(re.findall(r'<file>(animation_library[^<]*)</file>', texts[kind])) == anims[kind]
    if unit['lp_pairs']:
        # The Naginata horse lists the same mesh for normal and low poly. The Yabusame horse has a real low poly,
        # and it sits in the <lowpoly> block, not on the next line.
        texts['horse'], n = re.subn(
            r'(<lowpoly>\s*<assetreference type="GrannyModel">\s*<file>units\\korean_lancer\\korean_lancer_horse_)([02])(</file>)',
            r'\1\2_lp\3', texts['horse'])
        assert n == 3, n
    return texts


def own_paths(unit, text):
    """The animfile without the vanilla animations it keeps by archive path; each must be a GrannyAnim reference."""
    for path in unit.get('vanilla_anims', ()):
        text, n = re.subn(r'(<assetreference type="GrannyAnim">\s*)<file>%s</file>' % re.escape(path), r'\1', text)
        assert n <= 1, path
    return text


def _models(unit):
    """(dest basename, source folder, source basename) for every GR2 this unit ships."""
    rows = []
    for dest, src in unit['body'].items():
        folder = unit['sword_dir'] if src == 'steppe_rider_sword' else unit['body_dir']
        rows.append((dest, folder, src))
    for dest, src in unit['horse'].items():
        rows.append((dest, unit['horse_dir'], src))
    return rows


def build():
    """Animfiles and materials. GR2 clones are written by main(); they are vanilla bytes, not derived."""
    out = {}
    for folder, unit in UNITS.items():
        for kind, text in _rewrite(unit).items():
            out['art/units/%s/%s_%s.xml' % (folder, folder, kind)] = text.replace('\n', '\r\n').encode('utf-8')
        for src, dest in unit.get('extras', ()):
            out[dest] = vanilla(src).replace('\n', '\r\n').encode('utf-8')
        for dest, folder_src, src in _models(unit):
            # A low-poly mesh has no material of its own; it uses the full model's vanilla material.
            src_mat = unit.get('material_alias', {}).get(src, src)
            out['art/units/%s/%s.material' % (folder, dest)] = material_text(
                folder_src, src_mat[:-3] if src_mat.endswith('_lp') else src_mat).replace('\n', '\r\n').encode('utf-8')
    return out


def write_models():
    blobs = gr2_bytes()
    written = []
    for folder, unit in UNITS.items():
        for dest, _folder_src, src in _models(unit):
            data = blobs.get(src.lower() + '.gr2')
            if data is None:
                raise SystemExit('no archived GR2 named %s.gr2 (have %s)' % (src, sorted(blobs)))
            path = os.path.join(REPO, 'art', 'units', folder, dest + '.gr2')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'wb').write(data)
            written.append(path)
    return written


def _strip(el):
    if el.text is not None:
        el.text = el.text.strip() or None
    el.tail = None
    for child in el:
        _strip(child)


def _xml(el, indent='  '):
    _strip(el)
    ET.indent(el, space='  ')
    return '\n'.join(indent + line if line else line for line in ET.tostring(el, encoding='unicode').splitlines())


def _set(el, tag, value):
    node = el.find(tag)
    assert node is not None and node.text is not None, tag
    node.text = value


def _unit_xml(proto_root, unit):
    src = next(u for u in proto_root.findall('unit') if u.get('name') == unit['vanilla'])
    own = copy.deepcopy(src)
    own.set('id', unit['uid'])
    own.set('name', unit['proto'])
    display, editor, rollover, short = (str(n) for n in unit['strings'])
    _set(own, 'dbid', unit['uid'])
    _set(own, 'displaynameid', display)
    _set(own, 'editornameid', editor)
    _set(own, 'animfile', BS.join(['units', unit_folder(unit), unit_folder(unit) + '_horse.xml']))
    if not unit.get('keep_icons'):
        _set(own, 'icon', BS.join(['resources', 'art', 'units', unit_folder(unit), unit_folder(unit) + '_icon.png']))
        _set(own, 'portraiticon', BS.join(['resources', 'art', 'units', unit_folder(unit),
                                           unit_folder(unit) + '_portrait.png']))
    _set(own, 'rollovertextid', rollover)
    _set(own, 'shortrollovertextid', short)
    note = unit.get('note') or (
        '  <!-- %s, displayed as %s. Vanilla %s field for field, on its own GR2 clones and animfiles '
        '(tools/korean_cavalry.py). Textures are still the vanilla archive paths. -->\n'
        % (unit['proto'], unit['display'], unit['vanilla']))
    return note + _xml(own) + '\n'


def unit_folder(unit):
    return next(folder for folder, spec in UNITS.items() if spec is unit)


def _trainers(proto_root, aop_root, vanilla_name):
    rows = []
    for root in (proto_root, aop_root):
        for unit in root.findall('unit'):
            name = unit.get('name') or ''
            if name.startswith('ypSPC'):
                continue
            for train in unit.findall('train'):
                if train.text == vanilla_name:
                    rows.append((name, train.get('page'), train.get('column')))
    return sorted(set(rows), key=lambda row: (row[0] != 'ypStableJapanese', row[0], row[1] or '', row[2] or ''))


def _effects(proto_root, aop_root, only=None):
    chosen = [(folder, unit) for folder, unit in UNITS.items() if only is None or unit['proto'] in only]
    lines = []
    if only is None:
        lines.append('''      <!-- Geomsabok (zpKoreanLancer) replaces the Naginata Rider and rides the Yabusame horse.
           Gungdo Cavalry (zpKoreanHorseArcher) replaces the Yabusame and rides the Naginata horse.
           Pyeongon Cavalry (zpKoreanIronFlail) is an extra Stable unit: the Chinese rider on the Yabusame horse.
           Own GR2s and animfiles, vanilla textures (tools/korean_cavalry.py). -->''')
    owned = set()
    for _folder, unit in chosen:
        if unit.get('extra'):
            lines.append('''      <effect type="Data" amount="1.00" subtype="Enable" relativity="Absolute">
        <target type="ProtoUnit">%s</target>
      </effect>
      <effect type="CommandAdd" proto="%s" page="0" column="%s">
        <target type="ProtoUnit">ypStableJapanese</target>
      </effect>''' % (unit['proto'], unit['proto'], unit['column']))
            column = unit['column']
        else:
            lines.append('''      <effect type="Data" amount="1.00" subtype="Enable" relativity="Absolute">
        <target type="ProtoUnit">%s</target>
      </effect>
      <effect type="Data" amount="0.00" subtype="Enable" relativity="Absolute">
        <target type="ProtoUnit">%s</target>
      </effect>''' % (unit['proto'], unit['vanilla']))
            for building, page, column in _trainers(proto_root, aop_root, unit['vanilla']):
                lines.append('''      <effect type="CommandAdd" proto="%s" page="%s" column="%s">
        <target type="ProtoUnit">%s</target>
      </effect>''' % (unit['proto'], page, column, building))
            column = _trainers(proto_root, aop_root, unit['vanilla'])[0][2]
            assert _trainers(proto_root, aop_root, unit['vanilla'])[0][0] == 'ypStableJapanese'
        for vanilla_tech, own, _dbid, _display, _rollover, _newname in UPGRADES[unit['vanilla']]:
            owned.add(own)
            if not unit.get('extra'):
                lines.append('      <effect type="TechStatus" status="unobtainable">%s</effect>' % vanilla_tech)
            lines.append('      <effect type="TechStatus" status="obtainable">%s</effect>' % own)
            lines.append('''      <effect type="CommandAdd" tech="%s" page="1" column="%s">
        <target type="ProtoUnit">ypStableJapanese</target>
      </effect>''' % (own, column))
    for name, _dbid, _prereq, grants in SHADOWS:
        if only is not None and not any(g in owned for g in grants):
            continue
        lines.append('      <effect type="TechStatus" status="obtainable">%s</effect>' % name)
    return '\n'.join(lines) + '\n'


def _tech_xml(tech_root, vanilla_names=None):
    by_name = {t.get('name'): t for t in tech_root.findall('tech')}
    chunks = []
    rename = {}
    upgrades = {k: v for k, v in UPGRADES.items() if vanilla_names is None or k in vanilla_names}
    for vanilla_name, rows in upgrades.items():
        for vanilla_tech, own, dbid, display, rollover, newname in rows:
            rename[vanilla_tech] = (own, str(dbid), str(display), str(rollover), str(newname))
    owned = {row[1] for rows in upgrades.values() for row in rows}
    for vanilla_name, rows in upgrades.items():
        proto = next(folder_unit['proto'] for folder_unit in UNITS.values() if folder_unit['vanilla'] == vanilla_name)
        for vanilla_tech, own, dbid, display, rollover, newname in rows:
            tech = copy.deepcopy(by_name[vanilla_tech])
            tech.set('name', own)
            _set(tech, 'dbid', str(dbid))
            _set(tech, 'displaynameid', str(display))
            _set(tech, 'rollovertextid', str(rollover))
            for node in tech.iter():
                if node.get('proto') == vanilla_name:
                    node.set('proto', proto)
                if node.get('unittype') == vanilla_name:
                    node.set('unittype', proto)
                if node.tag == 'techstatus' and node.text in rename:
                    node.text = rename[node.text][0]
                if node.get('type') == 'SetName':
                    node.set('proto', proto)
                    node.set('newname', str(newname))
                if node.tag == 'target' and node.text == vanilla_name:
                    node.text = proto
            chunks.append(_xml(tech))
    for name, dbid, prereq, grants in SHADOWS:
        if vanilla_names is not None and not any(g in owned for g in grants):
            continue
        effects = '\n'.join('      <effect type="TechStatus" status="active">%s</effect>' % g for g in grants)
        chunks.append('''  <tech name="%s" type="Normal">
    <dbid>%d</dbid>
    <researchpoints>0.0000</researchpoints>
    <status>UNOBTAINABLE</status>
    <flag>Shadow</flag>
    <prereqs>
      <techstatus status="Active">%s</techstatus>
    </prereqs>
    <effects>
%s
    </effects>
  </tech>''' % (name, dbid, prereq, effects))
    return '\n'.join(chunks) + '\n'


def _strings(existing=''):
    rows = []
    for unit in UNITS.values():
        display, editor, rollover, short = unit['strings']
        rows.append((display, unit['display']))
        rows.append((editor, unit['editor']))
        rows.append((rollover, unit['rollover']))
        rows.append((short, unit['short']))
    rows += [
        (600099, 'Disciplined Geomsabok'),
        (600100, 'Honored Geomsabok'),
        (600101, 'Exalted Geomsabok'),
        (600102, 'Geomsabok attack and hitpoints increased.'),
        (600103, 'Exalted upgrade for Geomsabok.'),
        (600108, 'Honored Gungdo Cavalry'),
        (600109, 'Exalted Gungdo Cavalry'),
        (600110, 'Gungdo Cavalry attack and hitpoints increased.'),
        (600111, 'Exalted upgrade for Gungdo Cavalry.'),
        (600116, 'Honored Pyeongon Cavalry'),
        (600117, 'Exalted Pyeongon Cavalry'),
        (600118, 'Pyeongon Cavalry attack and hitpoints increased.'),
        (600119, 'Exalted upgrade for Pyeongon Cavalry.'),
    ]
    rows.sort()
    assert [i for i, _text in rows] == list(range(600095, 600120)), rows
    fresh = [pair for pair in rows if '_locid="%d"' % pair[0] not in existing]
    return '\n'.join('      <string _locid="%d">%s</string>' % pair for pair in fresh) + '\n'


def _crlf_write(path, text):
    open(path, 'wb').write(text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))


def apply_data():
    """Insert the proto, tech, string and sound records. Re-running leaves an already-wired tree alone."""
    proto_path = os.path.join(REPO, 'data', 'protomods.xml')
    tech_path = os.path.join(REPO, 'data', 'techtreemods.xml')
    string_path = os.path.join(REPO, 'data', 'strings', 'english', 'stringmods.xml')
    proto_text = open(proto_path, encoding='utf-8').read()
    missing = [unit for unit in UNITS.values() if unit['proto'] not in proto_text]
    if not missing:
        print('data records already present')
        return
    vanilla_proto = ET.fromstring(vanilla('data/protoy.xml.XMB'))
    aop_proto = ET.parse(os.path.join(korean_visuals.AOP, 'data', 'protomods.xml')).getroot()
    marker = '<!-- BEGIN zzTEST Korean building benches'
    assert marker in proto_text
    block = ''.join(_unit_xml(vanilla_proto, unit) for unit in missing)
    proto_text = proto_text.replace(marker, block + marker, 1)

    tech_text = open(tech_path, encoding='utf-8').read()
    old_note = ('Gungdo Cavalry (zpKoreanHorseArcher) replaces the Yabusame and rides the Naginata horse.\n'
                '           Own GR2s and animfiles, vanilla textures (tools/korean_cavalry.py).')
    new_note = ('Gungdo Cavalry (zpKoreanHorseArcher) replaces the Yabusame and rides the Naginata horse.\n'
                '           Pyeongon Cavalry (zpKoreanIronFlail) is an extra Stable unit: the Chinese rider on the Yabusame horse.\n'
                '           Own GR2s and animfiles, vanilla textures (tools/korean_cavalry.py).')
    if old_note in tech_text:
        tech_text = tech_text.replace(old_note, new_note, 1)
    names = {unit['proto'] for unit in missing}
    vanillas = {unit['vanilla'] for unit in missing}
    effects = _effects(vanilla_proto, aop_proto, None if len(missing) == len(UNITS) else names)
    if 'zpKoreanLancer' in open(proto_path, encoding='utf-8').read() and len(missing) != len(UNITS):
        anchor = '      <effect type="TechStatus" status="obtainable">zpKoreanHorseArcherPostImperial</effect>\n'
        assert tech_text.count(anchor) == 1, 'cavalry effect anchor moved'
        tech_text = tech_text.replace(anchor, anchor + effects, 1)
    else:
        end = '      <effect type="TechStatus" status="obtainable">zpGakgungPostImperial</effect>\n    </effects>'
        assert tech_text.count(end) == 1
        tech_text = tech_text.replace(end, end.replace('    </effects>', effects + '    </effects>'), 1)
    tech_root = ET.fromstring(vanilla('data/techtreey.xml.XMB'))
    assert tech_text.rstrip().endswith('</techtreemods>')
    tech_text = tech_text.rstrip()[:-len('</techtreemods>')] + _tech_xml(tech_root, vanillas) + '</techtreemods>\n'

    string_text = open(string_path, encoding='utf-8').read()
    if 'Naginata Rider' in string_text:
        string_text = string_text.replace('Naginata Rider', 'Geomsabok', 1)
    if 'Yabusame Archer' in string_text:
        string_text = string_text.replace('Yabusame Archer', 'Gungdo Cavalry', 1)
    if 'Gungdo Cavalry and Yumi Archer' in string_text:
        string_text = string_text.replace('Gungdo Cavalry and Yumi Archer', 'Gungdo Cavalry, Pyeongon Cavalry and Yumi Archer', 1)
    lang = '    </language>'
    assert string_text.count(lang) == 1
    string_text = string_text.replace(lang, _strings(string_text) + lang, 1)

    _crlf_write(proto_path, proto_text)
    _crlf_write(tech_path, tech_text)
    _crlf_write(string_path, string_text)
    for unit in missing:
        snd = os.path.join(REPO, 'sound', unit['proto'].lower() + '_snds.xml')
        _crlf_write(snd, '''<protounitsounddef>
  <protounit name="%s">
    <soundtype name="Grunt">
      <soundset name="GenericMaleGrunt" />
    </soundtype>
    <soundtype name="Death">
      <soundset name="GenericMaleDeath" />
    </soundtype>
    <soundtype name="Select">
      <soundset name="Korean_Soldier_Select" />
    </soundtype>
    <soundtype name="Acknowledge">
      <targetlogic>
        <choice name="default">
          <soundset name="Korean_Soldier_Acknowledge" />
        </choice>
        <choice name="enemy">
          <soundset name="Korean_Soldier_Attack" />
        </choice>
        <choice name="build" />
        <choice name="Huntable" />
        <choice name="Tree" />
        <choice name="AbstractMine" />
        <choice name="AbstractFarm" />
        <choice name="AbstractResourceCrate" />
        <choice name="AbstractFruit" />
      </targetlogic>
    </soundtype>
    <soundtype name="Creation">
      <soundset name="MilitaryBirth" />
    </soundtype>
  </protounit>
</protounitsounddef>
''' % unit['proto'])
        print('sound', snd)


def main():
    written = write_models()
    apply_data()
    for path in written:
        print('gr2', os.path.relpath(path, REPO), os.path.getsize(path))
    print('animfiles and materials: python tools/build.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
