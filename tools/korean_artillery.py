#!/usr/bin/env python
"""Hongyipao as a Korean Castle cannon (2026-10-13).

The industrial heavy cannon. Stats, population and the Exalted upgrade are the Ottoman Great Bombard's
(population 7, Industrial Age, 1.50 hitpoints and damage for 1500 Wood and 1500 Coin). The animation and
the icon are the native Korean bombard's, referenced by path. Chongtong and the Hwacha need their own
models and are not records here.

    python tools/korean_artillery.py
"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import korean_cavalry as kc  # noqa: E402

BS = chr(92)
PROTO = 'zpKoreanHongyipao'
UID = '22026'
VANILLA = 'GreatBombard'
VANILLA_TECH = 'ImperialBombard'
TECH = 'zpExaltedKoreanHongyipao'
TECH_DBID = '60041'
# display, editor, rollover, short, exalted name, exalted rollover
STRINGS = (
    (600120, 'Hongyipao'),
    (600121, 'ART Hongyipao'),
    (600122, 'Super-heavy artillery. Moves and fires slowly, but does tremendous damage against infantry or buildings.'),
    (600123, 'Super-heavy artillery.'),
    (600124, 'Exalted Hongyipao'),
    (600125, 'Exalted upgrade for Hongyipao.'),
)
ANIM = BS.join(['units', 'revolution', 'cetbang', 'korean_bombard.xml'])
ICON = BS.join(['resources', 'art', 'units', 'natives', 'korean_bombard_icon.png'])
PORTRAIT = BS.join(['resources', 'art', 'units', 'natives', 'korean_bombard_portrait.png'])
MARKER = '<!-- BEGIN zzTEST Korean building benches'
ANCHOR = '      <effect type="TechStatus" status="obtainable">zpKoreanIronFlailPostImperial</effect>\n'


def _unit_xml(proto_root):
    src = next(u for u in proto_root.findall('unit') if u.get('name') == VANILLA)
    own = copy.deepcopy(src)
    own.set('id', UID)
    own.set('name', PROTO)
    kc._set(own, 'dbid', UID)
    kc._set(own, 'displaynameid', '600120')
    kc._set(own, 'editornameid', '600121')
    kc._set(own, 'rollovertextid', '600122')
    if own.find('shortrollovertextid') is not None:
        kc._set(own, 'shortrollovertextid', '600123')
    kc._set(own, 'animfile', ANIM)
    kc._set(own, 'icon', ICON)
    kc._set(own, 'portraiticon', PORTRAIT)
    assert float(own.findtext('populationcount')) == 7, own.findtext('populationcount')
    assert int(float(own.findtext('allowedage'))) == 3, own.findtext('allowedage')
    assert own.find('buildlimit') is None
    assert 'AbstractNativeWarrior' not in [(t.text or '').strip() for t in own.findall('unittype')]
    note = ('  <!-- Hongyipao, the industrial Castle cannon. Great Bombard field for field '
            '(population 7); the native Korean bombard animation and icon (tools/korean_artillery.py). -->\n')
    return note + kc._xml(own) + '\n'


def _effects():
    return '''      <effect type="Data" amount="1.00" subtype="Enable" relativity="Absolute">
        <target type="ProtoUnit">%s</target>
      </effect>
      <effect type="CommandAdd" proto="%s" page="0" column="2">
        <target type="ProtoUnit">ypCastle</target>
      </effect>
      <effect type="TechStatus" status="obtainable">%s</effect>
      <effect type="CommandAdd" tech="%s" page="1" column="2">
        <target type="ProtoUnit">ypCastle</target>
      </effect>
''' % (PROTO, PROTO, TECH, TECH)


def _tech_xml(tech_root):
    src = next(t for t in tech_root.findall('tech') if t.get('name') == VANILLA_TECH)
    tech = copy.deepcopy(src)
    tech.set('name', TECH)
    kc._set(tech, 'dbid', TECH_DBID)
    kc._set(tech, 'displaynameid', '600124')
    kc._set(tech, 'rollovertextid', '600125')
    for node in tech.iter():
        if node.text and node.text.strip() == VANILLA:
            node.text = PROTO
        for key, val in list(node.attrib.items()):
            if val == VANILLA:
                node.set(key, PROTO)
        if node.get('type') == 'SetName':
            node.set('proto', PROTO)
            node.set('newname', '600124')
    prereqs = [(p.text or '').strip() for p in tech.iter('techstatus')]
    assert prereqs == ['Imperialize'], prereqs
    costs = sorted((c.get('resourcetype'), (c.text or '').strip()) for c in tech.findall('cost'))
    assert costs == [('Gold', '1500.0000'), ('Wood', '1500.0000')], costs
    return kc._xml(tech) + '\n'


def _strings(existing):
    fresh = [pair for pair in STRINGS if '_locid="%d"' % pair[0] not in existing]
    assert [i for i, _text in STRINGS] == list(range(600120, 600126))
    return '\n'.join('      <string _locid="%d">%s</string>' % pair for pair in fresh) + '\n'


def apply_data():
    proto_path = os.path.join(REPO, 'data', 'protomods.xml')
    tech_path = os.path.join(REPO, 'data', 'techtreemods.xml')
    string_path = os.path.join(REPO, 'data', 'strings', 'english', 'stringmods.xml')
    proto_text = open(proto_path, encoding='utf-8').read()
    if PROTO in proto_text:
        print('data records already present')
        return
    assert UID not in proto_text and MARKER in proto_text
    vanilla_proto = ET.fromstring(kc.vanilla('data/protoy.xml.XMB'))
    proto_text = proto_text.replace(MARKER, _unit_xml(vanilla_proto) + MARKER, 1)

    tech_text = open(tech_path, encoding='utf-8').read()
    assert tech_text.count(ANCHOR) == 1 and TECH not in tech_text and TECH_DBID not in tech_text
    tech_text = tech_text.replace(ANCHOR, ANCHOR + _effects(), 1)
    tech_root = ET.fromstring(kc.vanilla('data/techtreey.xml.XMB'))
    assert tech_text.rstrip().endswith('</techtreemods>')
    tech_text = tech_text.rstrip()[:-len('</techtreemods>')] + _tech_xml(tech_root) + '</techtreemods>\n'

    string_text = open(string_path, encoding='utf-8').read()
    old = 'Pyeongon Cavalry and Yumi Archer.'
    new = 'Pyeongon Cavalry, Hongyipao and Yumi Archer.'
    assert string_text.count(old) == 1
    string_text = string_text.replace(old, new, 1)
    lang = '    </language>'
    assert string_text.count(lang) == 1
    string_text = string_text.replace(lang, _strings(string_text) + lang, 1)

    kc._crlf_write(proto_path, proto_text)
    kc._crlf_write(tech_path, tech_text)
    kc._crlf_write(string_path, string_text)
    snd = os.path.join(REPO, 'sound', PROTO.lower() + '_snds.xml')
    kc._crlf_write(snd, '''<protounitsounddef>
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
''' % PROTO)
    print('sound', snd)


def main():
    apply_data()
    return 0


if __name__ == '__main__':
    sys.exit(main())
