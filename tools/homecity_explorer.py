#!/usr/bin/env python
"""Korean Home City explorer spot: the explorer (the Korean monk on his horse, units/korean_monk/korean_monk_horse.xml)
stands at the ground bone bone_explorer_special - the bone every inspected home city animfile defines (India, Poland,
China); no attachment places it. The unit itself comes from data/homecityprotounits.xml (tools/korean_homecity_units.py):
moving the bone alone showed nothing in game (2026-10-17), because the Koreans had no entry there.
Owner 2026-10-17 (game screenshot): "Korean explorer is missing ... remove one tree next to the Customs House and left
from the customs house place the explorer on a horse". Audit: Blendify journal 2026-10-17-claude-opus-5.5-26.

    python tools/homecity_explorer.py [--deploy]

 1. the street tree on SPOT (bone_pathnode_07: the tree directly left of the Customs House, bone_boatbuilding, in the
    home-city camera) leaves korean_homecity.xml (its tree and falling_leaves attachments);
 2. bone_explorer_special moves onto SPOT's position + BACK and keeps its vanilla yaw (-24.1 deg): gr2_bones "move",
    every other bone and byte unchanged. Its vanilla China spot sits by the gate 0.7 m under the Korean walkway. BACK =
    2.5 m away from the railing: on SPOT itself the Cheongsachorong stall-lantern string (Korean_Lanterns, a prop at the
    Emperor's Treasury's bone_fx) hung 0.4-2.3 m in front of him at rider height, so hovering him showed "Emperor's
    Treasury" (owner 2026-10-17) - the home city names the building whose geometry is under the cursor;
 3. proof: only that bone moved, onto SPOT + BACK (< 1e-4); no orphan fixups; the game's Granny DLL reads the ground.
A re-run is a no-op (byte-identical files). To move the explorer elsewhere, change SPOT (a ground bone) and rerun.
"""
import argparse, json, re, shutil, sys, tempfile
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
import korean_visuals  # noqa: E402  (AOP)
HAVOK = Path(korean_visuals.AOP) / 'scripts' / 'havok'
sys.path.insert(0, str(HAVOK))
import gr2_bones, gr2_lint  # noqa: E402,E401
from gr2_fixups import orphan_fixups  # noqa: E402

GROUND = REPO / 'art' / 'homecity' / 'korean' / 'korean_hc_ground.gr2'
ANIMFILE = REPO / 'art' / 'homecity' / 'korean' / 'korean_homecity.xml'
EXPLORER = 'bone_explorer_special'
SPOT = 'bone_pathnode_07'
BACK = np.array([0.0, 0.0, -6.35])     # GR2 frame: 2.5 m Blender +Y (away from the railing and the home-city camera)
TREE_LINE = re.compile(rb'[ \t]*<attach a="(?:tree|falling_leaves)" frombone="ATTACHPOINT" tobone="' + SPOT.encode()
                       + rb'" syncanims="0" />\r\n')


def worlds(path):
    """bone -> 4x4 row-vector world (translation in row 3)"""
    return {b['name']: b['world'] for b in gr2_lint.read_raw(path)['bones']}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--deploy', action='store_true', help=f'write {GROUND.name} and {ANIMFILE.name}')
    a = ap.parse_args(argv)
    work = Path(tempfile.mkdtemp(prefix='kexplorer_'))
    W = worlds(GROUND); target = W[SPOT][3, :3] + BACK; t = target - W[EXPLORER][3, :3]
    ground = work / GROUND.name
    if np.abs(t).max() > 1e-6:
        gr2_bones.edit(GROUND, {'move': [{'bones': [EXPLORER], 'translate': t.tolist()}]}, ground)
    else:
        shutil.copyfile(GROUND, ground)
    N = worlds(ground)
    assert list(N) == list(W), 'bone list changed'
    err = float(np.abs(N[EXPLORER][3, :3] - target).max())
    assert err < 1e-4 and np.allclose(N[EXPLORER][:3, :3], W[EXPLORER][:3, :3], atol=1e-6), f'explorer off SPOT by {err}'
    drift = max(float(np.abs(N[n] - W[n]).max()) for n in W if n != EXPLORER)
    assert drift < 1e-6, f'another ground bone moved ({drift:.2e})'
    assert not orphan_fixups(str(ground))['orphans'], 'orphan pointer fixups'
    profiles = json.loads((HAVOK / 'gr2_lint_profiles.json').read_text(encoding='utf-8'))
    dll = gr2_lint.dll_read(ground, gr2_lint.find_tools(profiles), work)
    assert dll['status'] == 'PASS', f'Granny DLL read: {dll}'
    raw = ANIMFILE.read_bytes(); anim = TREE_LINE.sub(b'', raw)
    assert b'\n' not in anim.replace(b'\r\n', b'') and SPOT.encode() not in anim.split(b'<attach', 1)[1], \
        f'{SPOT}: an attachment is left, or the animfile is not CRLF'
    rep = dict(explorer_from=np.round(W[EXPLORER][3, :3], 3).tolist(), explorer_to=np.round(N[EXPLORER][3, :3], 3).tolist(),
               spot=SPOT, max_err=err, other_bone_drift=drift, tree_lines_removed=raw.count(b'tobone="' + SPOT.encode()),
               dll_read=dll['status'])
    print('VERIFIED', json.dumps(rep))
    if a.deploy:
        shutil.copyfile(ground, GROUND); ANIMFILE.write_bytes(anim)
        print('DEPLOYED', GROUND, ANIMFILE)
    print('WORK', work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
