#!/usr/bin/env python
"""The Korean monk's rider model: the vanilla Shaolin Disciple mesh on the vanilla yabusame rider skeleton, so the
cavalry animations drive a bald monk (owner 2026-10-09: "we need to use some other model with bald head", "infantry
and rig it with cavalry bones"). Built with AoP's scripts/havok/gr2_reskeleton.py: the Disciple's mesh, vertex and
index bytes stay vanilla; only its skeleton becomes the rider's (identical joints, rider hierarchy and names).

    python tools/korean_monk_model.py           # rebuild art/units/korean_monk/korean_monk_rider.gr2
    python tools/korean_monk_model.py --check   # exit 1 if the file in the repo differs from a fresh build

Needs the installed game (AoP's bartool) and the AoP checkout; exits 2 when either is missing. Shape untouched: the
AGENTS.md rule-2 exception (retexture clone of a vanilla unit), here with the skeleton of another vanilla unit.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import korean_visuals  # noqa: E402  (AOP, BARTOOL)

DONOR = 'Art/units/asians/japanese/yabusame/yabusamerider_0.gr2'          # skeleton
TARGET = 'Art/units/asians/chinese/shaolin_disciple/shaolin_disciple_01.gr2'   # mesh
OUT = os.path.join(REPO, 'art', 'units', 'korean_monk', 'korean_monk_rider.gr2')


def build():
    """bytes of a fresh build (the vanilla files are extracted into a temporary folder, never into the repo)."""
    tool = os.path.join(korean_visuals.AOP, 'scripts', 'havok', 'gr2_reskeleton.py')
    if not os.path.isfile(tool) or not os.path.isfile(korean_visuals.BARTOOL):
        print('MISSING: AoP checkout with scripts/havok/gr2_reskeleton.py and bartool (%s)' % korean_visuals.AOP)
        sys.exit(2)
    with tempfile.TemporaryDirectory(prefix='korean_monk_model_') as tmp:
        for src in (DONOR, TARGET):
            r = subprocess.run([sys.executable, korean_visuals.BARTOOL, 'extract', src, '-o', tmp, '--flat'],
                               capture_output=True, text=True)
            if r.returncode:
                print('MISSING game file %s: %s' % (src, r.stderr.strip()[-300:]))
                sys.exit(2)
        donor, target = (os.path.join(tmp, os.path.basename(p).lower()) for p in (DONOR, TARGET))
        out = os.path.join(tmp, 'korean_monk_rider.gr2')
        r = subprocess.run([sys.executable, tool, donor, target, out], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode:
            print(r.stderr.strip()[-1500:])
            sys.exit(1)
        return open(out, 'rb').read()


def main():
    data = build()
    current = open(OUT, 'rb').read() if os.path.isfile(OUT) else None
    if '--check' in sys.argv:
        print('korean_monk_rider.gr2', 'up to date' if current == data else 'STALE')
        return 0 if current == data else 1
    if current != data:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        open(OUT, 'wb').write(data)
        print('wrote', os.path.relpath(OUT, REPO), len(data), 'bytes')
    else:
        print('korean_monk_rider.gr2 up to date')
    return 0


if __name__ == '__main__':
    sys.exit(main())
