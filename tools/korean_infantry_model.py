#!/usr/bin/env python
"""The Korean infantry's models (owner 2026-10-09: "full retextures", "if you need hats, these can be created
separately and easily attached", "Hats are the easiest thing to craft"):

  art/units/korean_jochong/korean_jochong_age1/2/3.gr2      the vanilla Chinese Arquebusier bodies, unchanged
  art/units/korean_jangchang/korean_jangchang_age1/2.gr2    the vanilla Chinese Qiang pikeman bodies 1 and 2, unchanged
                                                            (the fur-cap body 0 is not used: the unit starts Disciplined)
  art/units/korean_gakgung/korean_gakgung_age0/1/2.gr2      the vanilla Chinese Changdao bodies, unchanged
  art/units/korean_jochong/korean_jochong_hat.gr2           the jeollip, modelled for the mod (tools/infantry_texture/,
                                                            frozen geometry jeollip_parts.json), written by AoP's
                                                            scripts/havok/multimaterial_gr2.py on the vanilla bandido hat
                                                            (its skeleton: bone_hat, attached to HEAD like every hat)

The bodies keep their vanilla bytes under the units' own names so that their .material files give them the Joseon
retextures (AGENTS.md rule-2 exception).

    python tools/korean_infantry_model.py           # rebuild
    python tools/korean_infantry_model.py --check   # exit 1 if a file in the repo differs from a fresh build

Needs the installed game (AoP's bartool) and the AoP checkout; exits 2 when either is missing. The vanilla files are
extracted into a temporary folder, never into this repo. The hat writer refuses orphan pointer fixups (INC-187); its
load in the game's Granny DLL is proven with AoP gr2_lint's dll_read (2026-10-09: PASS on the wsl and native routes,
one bound mesh of 364 triangles).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import korean_visuals  # noqa: E402  (AOP, BARTOOL)

ART = os.path.join(REPO, 'art', 'units')
BODIES = {}
for a in (1, 2, 3):
    BODIES['korean_jochong/korean_jochong_age%d.gr2' % a] = 'Art/units/asians/chinese/arquebusier/arquebusier_age%d.gr2' % a
for a in (1, 2):
    BODIES['korean_jangchang/korean_jangchang_age%d.gr2' % a] = \
        'Art/units/asians/chinese/qiang_pikeman/qiang_pikeman_age%d.gr2' % a
for a in (0, 1, 2):
    BODIES['korean_gakgung/korean_gakgung_age%d.gr2' % a] = 'Art/units/asians/chinese/changdao/changdao_%d.gr2' % a
HAT_DONOR = 'Art/units/spc/outlaws/bandido_hat.gr2'
HAT_PARTS = os.path.join(HERE, 'infantry_texture', 'jeollip_parts.json')
HAT = 'korean_jochong/korean_jochong_hat.gr2'


def extract(src, tmp):
    r = subprocess.run([sys.executable, korean_visuals.BARTOOL, 'extract', src, '-o', tmp, '--flat'],
                       capture_output=True, text=True)
    if r.returncode:
        print('MISSING game file %s: %s' % (src, r.stderr.strip()[-300:]))
        sys.exit(2)
    return os.path.join(tmp, os.path.basename(src).lower())


def build():
    """{path: bytes} of a fresh build."""
    havok = os.path.join(korean_visuals.AOP, 'scripts', 'havok')
    if not os.path.isfile(os.path.join(havok, 'multimaterial_gr2.py')) or not os.path.isfile(korean_visuals.BARTOOL):
        print('MISSING: AoP checkout with scripts/havok/multimaterial_gr2.py and bartool (%s)' % korean_visuals.AOP)
        sys.exit(2)
    sys.path.insert(0, havok)
    import multimaterial_gr2  # noqa: E402
    out = {}
    with tempfile.TemporaryDirectory(prefix='korean_infantry_model_') as tmp:
        for name, src in BODIES.items():
            out[os.path.join(ART, *name.split('/'))] = open(extract(src, tmp), 'rb').read()
        donor = extract(HAT_DONOR, tmp)
        spec = json.load(open(HAT_PARTS))
        parts = [{'material': 'hat', 'bone': spec['bone'], 'vertices': spec['vertices'], 'faces': spec['faces']}]
        hat = os.path.join(tmp, 'hat_out', os.path.basename(HAT))
        multimaterial_gr2.replace(donor, parts, hat, {'hat': spec['material']})
        out[os.path.join(ART, *HAT.split('/'))] = open(hat, 'rb').read()
    return out


def main():
    stale = 0
    for path, data in build().items():
        name = os.path.relpath(path, REPO).replace(os.sep, '/')
        current = open(path, 'rb').read() if os.path.isfile(path) else None
        if '--check' in sys.argv:
            print(name, 'up to date' if current == data else 'STALE')
            stale += current != data
        elif current != data:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'wb').write(data)
            print('wrote', name, len(data), 'bytes')
        else:
            print(name, 'up to date')
    return 1 if stale else 0


if __name__ == '__main__':
    sys.exit(main())
