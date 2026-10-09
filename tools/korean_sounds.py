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

    python tools/korean_sounds.py        # summary
"""
import os
import re
import subprocess
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


def korean_sets():
    text = open(os.path.join(HERE, 'korean_soundsets.xml'), 'rb').read().decode('utf-8-sig')
    return set(re.findall(r'<soundset name="([^"]+)"', text))


def base_text(name):
    own = os.path.join(korean_visuals.AOP, 'sound', name)
    if os.path.isfile(own):
        return open(own, 'rb').read().decode('utf-8-sig').replace('\r\n', '\n'), 'AoP override'
    out = subprocess.run([sys.executable, korean_visuals.BARTOOL, 'cat', 'Sound/%s.XMB' % name],
                         capture_output=True, check=True)
    return out.stdout.decode('utf-8-sig').replace('\r\n', '\n'), 'vanilla'


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
    return out


def main():
    for path, data in build().items():
        print('%-40s %6d bytes, %d Korean choices' % (path, len(data), data.count(b'name="%s"' % CIV.encode())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
