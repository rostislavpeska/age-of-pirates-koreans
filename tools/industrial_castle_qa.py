"""Strict Industrial castle gate, including donor hulls that the generic profile does not check.

Run from this add-on: python tools/industrial_castle_qa.py --out <scratch directory>.
The source fracture keeps a jagged stone ruin up to its authored course at 2.48 m.
The Japanese donor frame is HKT = 1.024 * GR2[z,y,x]; use the measured donor envelope.
This is offline evidence, not a Havok gameplay test.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

K = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(K / 'tools'))
from korean_visuals import AOP
A = Path(AOP)
sys.path.insert(0, str(A / 'scripts/havok'))
import gr2_lint as L


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out).resolve()
    if out.is_relative_to(K) or out.is_relative_to(A):
        ap.error('QA output belongs in scratch, outside runtime repositories')
    out.mkdir(parents=True, exist_ok=True)
    folder = K / 'art/buildings/korean_castle_industrial'
    for profile in ('korean_castle_industrial', 'korean_castle_industrial_con'):
        subprocess.run([sys.executable, '-u', str(A / 'scripts/havok/gr2_lint.py'),
                        '--profiles', str(K / 'tools/gr2_lint/profiles.json'), '--profile', profile,
                        str(folder), '--json', str(out / (profile + '.json'))], check=True)
    damaged = folder / 'korean_castle_industrial_damaged.gr2'
    d = L.read_raw(damaged)
    profile = {'damaged': {'base_bone': 'base', 'base_max_height_m': 2.481,
               'hkt': {'axis_map': [2, 1, 0], 'scale': 1.024, 'scale_tol': .002,
                       'median_err_max_m': .02, 'containment_tol_m': .05,
                       'containment_max_share': .005, 'containment_max_out_m': .1}}}
    results = [L.check_base('damaged', d, profile),
               L.check_hkt('damaged', d, folder / 'korean_castle_industrial_damaged.hkt', profile)]
    (out / 'hkt.json').write_text(json.dumps({'profile': profile, 'results': results}, indent=2))
    for r in results:
        print(r['status'], r['check'], r['summary'], flush=True)
    if L.exit_code(results):
        return L.exit_code(results)
    skills = A / '.claude/skills'
    for suffix, material in (('_con', 'matd'), ('_damaged', 'mata')):
        subprocess.run([sys.executable, '-u', str(skills / 'aoe3de-building-states/scripts/state_frame_check.py'),
                        '--intact', str(folder / 'korean_castle_industrial.gr2'),
                        '--state', str(folder / ('korean_castle_industrial' + suffix + '.gr2')),
                        '--material', material, '--json', str(out / (suffix + '_frame.json'))], check=True)
    subprocess.run([sys.executable, '-u', str(skills / 'aoe3de-model-attachments/scripts/attachment_check.py'),
                    str(folder / 'korean_castle_industrial.xml'), '--art-root', str(K / 'art'),
                    '--json', str(out / 'attachments.json')], check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
