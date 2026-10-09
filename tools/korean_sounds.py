#!/usr/bin/env python
"""Korean voices on shared protos: sound/<proto>_snds.xml = AoP's copy of that file if AoP has one, else vanilla,
with every leaf voice that has a Korean counterpart wrapped in

    <civlogic>
      <choice name="none"> the original soundset </choice>      every other civ keeps its voice
      <choice name="zpKoreans"> the Korean soundset </choice>
    </civlogic>

(the aoe3de-soundsets skill, "Give a new civ its own voices on a shared proto"). The Korean soundsets in
tools/korean_soundsets.xml mirror the vanilla family name by name (ChineseVillagerM_Select ->
zpKoreanVillagerM_Select), so the mapping is mechanical. tools/build.py writes the result; never edit it by hand.
A full copy shadows vanilla, so re-run the build after a DE patch or an AoP change to these files.

Wagons and the Asian fishing boat (owner 2026-10-09: "fishing boats same as male settler and all wagons that
Korea uses - basically same as Japanese wagons", "no new soundsets, only reuse"): every wagon sound file (vanilla
or AoP) and ypfishingboatasian_snds.xml that has a <choice name="Japanese"> gets, right after it, the same block as
<choice name="zpKoreans"> with each Japanese voice replaced by its Korean twin (JapaneseVillagerM_* ->
zpKoreanVillagerM_*, JapaneseFishingBoat* -> zpKoreanFishingBoat*). Voices that are not Japanese stay: where the
game gives a Japanese player's wagon a Dutch or Russian voice (consulate and DLC wagons), the Korean player hears
the same. Without the choice the Korean civ is unlisted and the wagon is silent.

    python tools/korean_sounds.py        # summary
"""
import importlib.util
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import korean_visuals  # noqa: E402  (AOP and BARTOOL)

CIV = 'zpKoreans'
# (proto sound file, vanilla soundset family prefix, Korean family prefix)
FILES = [
    ('ypsettlerasian_snds.xml', 'ChineseVillager', 'zpKoreanVillager'),
]
# Japanese voice family -> its Korean twin, for the files that get a zpKoreans choice next to the Japanese one
KOREAN_FAMILIES = (('JapaneseVillagerM_', 'zpKoreanVillagerM_'), ('JapaneseFishingBoat', 'zpKoreanFishingBoat'))
BOAT = 'ypfishingboatasian_snds.xml'
_BARTOOL = []


def korean_sets():
    text = open(os.path.join(HERE, 'korean_soundsets.xml'), 'rb').read().decode('utf-8-sig')
    return set(re.findall(r'<soundset name="([^"]+)"', text))


def bartool():
    """AoP's bartool module and the game's archive index, loaded once (one process for every file)."""
    if not _BARTOOL:
        spec = importlib.util.spec_from_file_location('bartool', korean_visuals.BARTOOL)
        bt = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bt)
        _BARTOOL.extend([bt, bt.build_index(bt.find_game_dir())])
    return _BARTOOL


def aop_sound_files():
    """lower-case name -> AoP's file name, for AoP's own sound files."""
    d = os.path.join(korean_visuals.AOP, 'sound')
    return {f.lower(): f for f in os.listdir(d) if f.lower().endswith('_snds.xml')}


def base_text(name):
    own = aop_sound_files().get(name.lower())
    if own:
        path = os.path.join(korean_visuals.AOP, 'sound', own)
        return open(path, 'rb').read().decode('utf-8-sig').replace('\r\n', '\n'), 'AoP override'
    bt, index = bartool()
    entry = index['sound/%s.xmb' % name.lower()]
    data, _ = bt.decode(bt.read_entry(entry), True, 'lf')
    return data.decode('utf-8-sig').replace('\r\n', '\n'), 'vanilla'


def wagon_files():
    """Every wagon sound file the game or AoP ships (lower case), sorted."""
    _, index = bartool()
    names = {p[len('sound/'):-len('.xmb')] for p in index if p.startswith('sound/') and p.count('/') == 1
             and p.endswith('_snds.xml.xmb')}
    names |= set(aop_sound_files())
    return sorted(n for n in names if 'wagon' in n)


def korean_name(name):
    for jp, ko in KOREAN_FAMILIES:
        if name.startswith(jp):
            return ko + name[len(jp):]
    return name


def add_korean_choices(text):
    """After every <choice name="Japanese"> block (same indentation closes it), the block again as the zpKoreans
    choice with its Japanese voices renamed to the Korean twins. Returns (text, number of choices added)."""
    lines, out, i, n = text.split('\n'), [], 0, 0
    while i < len(lines):
        m = re.match(r'^( *)<choice name="Japanese"\s*(/?)>\s*$', lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        ind, j = m.group(1), i
        if not m.group(2):
            j = next(k for k in range(i + 1, len(lines)) if lines[k].rstrip() == ind + '</choice>')
        block = '\n'.join(lines[i:j + 1])
        twin = block.replace('<choice name="Japanese"', '<choice name="%s"' % CIV, 1)
        twin = re.sub(r'<soundset name="([^"]+)"', lambda s: '<soundset name="%s"' % korean_name(s.group(1)), twin)
        out.extend((block + '\n' + twin).split('\n'))
        n += 1
        i = j + 1
    return '\n'.join(out), n


def check_korean_choices(text, sets):
    """Every Japanese choice is followed by its zpKoreans twin: the same voices with each Japanese family renamed
    to an existing Korean soundset, nothing Japanese left. Returns the number of twins."""
    root = ET.fromstring(text)
    twins = 0
    for parent in root.iter():
        kids = list(parent)
        for k, c in enumerate(kids):
            if c.tag != 'choice' or c.get('name') != 'Japanese':
                continue
            twin = kids[k + 1]
            assert twin.get('name') == CIV, 'no %s choice after a Japanese one' % CIV
            names = [s.get('name') for s in twin.iter('soundset')]
            assert names == [korean_name(s.get('name')) for s in c.iter('soundset')]
            assert not [s for s in names if s.startswith('Japanese')], names
            assert not [s for s in names if s.startswith('zpKorean') and s not in sets], names
            twins += 1
    return twins


def wrap(text, vanilla_prefix, korean_prefix, sets):
    count = [0]

    def sub(m):
        ind, name = m.group(1), m.group(2)
        korean = korean_prefix + name[len(vanilla_prefix):]
        if korean not in sets:
            return m.group(0)
        count[0] += 1
        return ('%s<civlogic>\n%s  <choice name="none">\n%s    <soundset name="%s" />\n%s  </choice>\n'
                '%s  <choice name="%s">\n%s    <soundset name="%s" />\n%s  </choice>\n%s</civlogic>'
                % (ind, ind, ind, name, ind, ind, CIV, ind, korean, ind, ind))

    out = re.sub(r'^( *)<soundset name="(%s[^"]*)" />' % re.escape(vanilla_prefix), sub, text, flags=re.M)
    return out, count[0]


def build():
    """{repo-relative path: CRLF bytes} of every Korean-wired proto sound file."""
    sets, out = korean_sets(), {}
    for name, vprefix, kprefix in FILES:
        text, _ = base_text(name)
        merged, n = wrap(text, vprefix, kprefix, sets)
        leaves = len(re.findall(r'<soundset name="%s' % re.escape(vprefix), text))
        assert n and n == leaves, '%s: wrapped %d of %d %s voices' % (name, n, leaves, vprefix)
        ET.fromstring(merged)
        out['sound/' + name] = merged.replace('\n', '\r\n').encode('utf-8')
    for name in wagon_files() + [BOAT]:
        text, _ = base_text(name)
        if '<choice name="Japanese"' not in text:
            continue                                    # the Japanese player has no voice here: neither does Korea
        assert '<choice name="%s"' % CIV not in text, name
        merged, n = add_korean_choices(text)
        assert n == text.count('<choice name="Japanese"') == check_korean_choices(merged, sets), name
        out['sound/' + name] = merged.replace('\n', '\r\n').encode('utf-8')
    return out


def main():
    for path, data in build().items():
        print('%-48s %6d bytes, %d Korean choices' % (path, len(data), data.count(b'name="%s"' % CIV.encode())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
