#!/usr/bin/env python
"""Korean Home City building night lanterns (art/homecity/korean/night_lanterns): the vanilla Japanese building lanterns
and their lights, moved from the Japanese city onto the same Japanese buildings where the Korean city places them.
Audit: AoP journal 2026-10-17-claude-opus-5.5-hc-lanterns-01..07; mechanism: AoP skill aoe3de-homecity-backdrop section 6.

    python tools/homecity_night_lanterns.py [--deploy] [--keep DIR]

Vanilla: prop Japanese_LightSetNight spawns homecity/japan/japan_night_lights.xml = model japan_props/japan_night_lights
(every lantern of the Japanese city, city frame) + PopcornFX lights on its fire_NN bones. Here:
 1. vanilla files from the installed game (bartool, temp folder only); japan_ground through the Granny DLL (bitknit);
 2. each lantern (connected triangles, 122 each) and each light bone belongs to the Japanese building it hangs on
    (distance to the building meshes placed at their japan_ground bones); street lanterns and street lights do not;
 3. ONE rigid move per building: Japanese building placement -> Korean building placement (korean_hc_ground bones),
    p' = R (p - t_J) + t_K with R = R_K^T R_J (column vectors);
 4. in place on the vanilla model: gr2_droptris (street lanterns out), gr2_rotate_verts (lanterns moved, normals and
    tangents turned, boxes refreshed), gr2_bones (their light bones moved by the same transforms);
 5. proof: every kept triangle = its vanilla triangle moved (< 1e-4), street triangles 0, every lantern within 1.3
    units of the building model the Korean city loads, every light bone moved, bounding boxes clean - else nothing
    is deployed;
 6. the animfile: vanilla attachments (fire = small_light, fire1 = hc_single_flicker_light) on the kept bones, each
    declared with <definebone>; the .material references the vanilla textures by archive path.
Wiring (data/asianhomecityprops.xml): prop Korean_Night_Lanterns at Emperor's Treasury bone_fx (= the city origin:
korean_court bone_fx = -bone_court, vanilla China's anchor), switched on by Korean_Light_BlueMountains <activateprops>
and off by the other Korean LightSets (vanilla Inca_LightSetNight -> Inca_Night_Lights pattern).
"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
import korean_visuals  # noqa: E402  (AOP, BARTOOL)
AOP = Path(korean_visuals.AOP); HAVOK = AOP / 'scripts' / 'havok'
sys.path.insert(0, str(HAVOK))
import gr2_bones, gr2_bounds, gr2_droptris, gr2_lint, gr2_rotate_verts  # noqa: E402,E401

OUT = REPO / 'art' / 'homecity' / 'korean' / 'night_lanterns'
ANIMFILE = REPO / 'art' / 'homecity' / 'korean' / 'korean_night_lanterns.xml'
MODEL = 'korean_night_lanterns'
GAME_PATH = 'homecity\\korean\\night_lanterns\\' + MODEL
GROUND = REPO / 'art' / 'homecity' / 'korean' / 'korean_hc_ground.gr2'
J = 'homecity/japan/'
VANILLA = [J + 'japan_props/japan_night_lights.gr2', J + 'japan_props/japan_night_lights.material',
           J + 'japan_night_lights.xml', J + 'japan_ground/japan_ground.gr2'] + \
          [f'{J}{m}/{m}.gr2' for m in ('court', 'tallbuilding', 'circlebuilding', 'waterbuilding', 'boatbuilding')]
# HC building -> (vanilla Japanese model, ground bone, the model the KOREAN city shows there)
BUILDINGS = {
    "Emperor's Treasury": ('court', 'bone_court', REPO / 'art/homecity/korean/court/korean_court.gr2'),
    'Fortress': ('tallbuilding', 'bone_tallbuilding', None),
    'Imperial Court': ('circlebuilding', 'bone_circlebuilding', None),
    'Merchants Guild': ('waterbuilding', 'bone_waterbuilding', None),
    'Customs House': ('boatbuilding', 'bone_boatbuilding', None),
}
LANTERN_MESH, STREET_MESH = 'japan_night_lights_M0Shape', 'japan_night_lightsShape'
C = np.diag([-1.0, 1.0, -1.0]); CM = 1.5625 / 100.0      # japan_ground: Maya cm, right +X, back -Z -> model frame
ON_BUILDING, LIGHT_ON_BUILDING, MARGIN = 1.6, 2.4, 2.5  # model units (1.5625 per m); measured gaps 1.24 / 1.93 vs 2.76+
EXPECT = {"Emperor's Treasury": (47, 46), 'Fortress': (32, 33), 'Imperial Court': (23, 23), 'Merchants Guild': (30, 30),
          'Customs House': (1, 3)}                       # (lanterns, lights) measured 2026-10-17


def vanilla(work):
    for rel in VANILLA:
        if not (work / Path(rel).name).exists():
            subprocess.run([sys.executable, korean_visuals.BARTOOL, 'extract', rel, '-o', str(work), '--flat'], check=True,
                           capture_output=True, timeout=600)
    return {Path(rel).name: work / Path(rel).name for rel in VANILLA}


def placements(files, work):
    """(R, t) per building in the model frame, row vectors (p_world = p_local @ R + t), Japanese and Korean grounds"""
    d = gr2_lint.dll_read(files['japan_ground.gr2'], gr2_lint.find_tools(gr2_lint.load_profiles()), work)
    assert d['status'] == 'PASS', f'japan_ground through the Granny DLL: {d}'
    jb = {b['name']: np.asarray(b['world']) for b in gr2_lint.read_flat(d['flat'])['bones']}
    kb = {b['name']: np.asarray(b['world']) for b in gr2_lint.read_raw(GROUND)['bones']}
    out = {}
    for hc, (_, bone, _) in BUILDINGS.items():
        W, K = jb[bone], kb[bone]
        out[hc] = dict(RJ=C @ W[:3, :3] @ C, tJ=CM * (W[3, :3] @ C), RK=K[:3, :3], tK=K[3, :3])
    return out


def building_points(files, place, korean):
    pts, own = [], []
    for hc, (model, _, kor_model) in BUILDINGS.items():
        src = kor_model if korean and kor_model else files[f'{model}.gr2']
        P = np.vstack([m['pos'][:, :3] for m in gr2_lint.read_raw(src)['meshes'] if m['name'] != 'court_M0Shape'])
        R, t = (place[hc]['RK'], place[hc]['tK']) if korean else (place[hc]['RJ'], place[hc]['tJ'])
        pts.append(P @ R + t); own += [hc] * len(P)          # court_M0Shape: a far-off light-shaft card, not the building
    return cKDTree(np.vstack(pts)), np.array(own)


def lanterns(mesh):
    """connected triangle sets; parts closer than 0.25 merged (lantern + hook)"""
    pos, tris = mesh['pos'][:, :3], mesh['tris']; nv = len(pos)
    e = np.vstack([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    n, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(nv, nv)), directed=False)
    pairs = cKDTree(pos).query_pairs(0.25, output_type='ndarray')
    if len(pairs):
        B = coo_matrix((np.ones(len(pairs) + n), (np.r_[lab[pairs[:, 0]], np.arange(n)], np.r_[lab[pairs[:, 1]], np.arange(n)])),
                       shape=(n, n))
        n, lab2 = connected_components(B, directed=False); lab = lab2[lab]
    return n, lab


def plan(files, place):
    info = gr2_lint.read_raw(files['japan_night_lights.gr2'])
    meshes = {m['name']: m for m in info['meshes']}
    tree, own = building_points(files, place, korean=False)
    m = meshes[LANTERN_MESH]; n, lab = lanterns(m); pos = m['pos'][:, :3]
    owner, gap = [], []
    for k in range(n):
        d, j = tree.query(pos[lab == k]); i = int(np.argmin(d)); gap.append(float(d[i]))
        owner.append(own[j[i]] if d[i] <= ON_BUILDING else None)
    assigned = [g for g, o in zip(gap, owner) if o]; street = [g for g, o in zip(gap, owner) if not o]
    assert max(assigned) < ON_BUILDING and min(street) > MARGIN, f'lantern split not clear: {max(assigned)} / {min(street)}'
    s = meshes[STREET_MESH]; sd, _ = tree.query(s['pos'][:, :3])
    assert sd.min() > MARGIN, f'a {STREET_MESH} vertex is {sd.min():.2f} from a building: not only street lanterns'
    tri_owner = np.array([owner[c] for c in lab[m['tris'][:, 0]]], dtype=object)
    anim = files['japan_night_lights.xml'].read_text(encoding='utf-8')
    kind = {b: a for a, b in re.findall(r'attach a="(\w+)" frombone="ATTACHPOINT" tobone="(fire_\d+)"', anim)}
    lights = {}
    for b in info['bones']:
        if b['name'] in kind:
            d, j = tree.query(np.asarray(b['world'])[3, :3])
            if d <= LIGHT_ON_BUILDING:
                lights[b['name']] = own[j]
            else:
                assert d > MARGIN * 1.1, f"{b['name']} {d:.2f} from a building: ambiguous"
    drop = {STREET_MESH: list(range(len(s['tris']))), LANTERN_MESH: [int(i) for i in np.where(tri_owner == None)[0]]}  # noqa: E711
    ops, moves, facts = [], [], {}
    for hc in BUILDINGS:
        p = place[hc]; Rc = p['RK'].T @ p['RJ']                  # column-vector rotation J -> K
        verts = sorted({int(v) for v in m['tris'][tri_owner == hc].ravel()})
        ops.append(dict(meshes={LANTERN_MESH: verts}, pivot=p['tJ'].tolist(), matrix=Rc.tolist(),
                        translate=(p['tK'] - p['tJ']).tolist()))
        bones = sorted(b for b, o in lights.items() if o == hc)
        moves.append(dict(bones=bones, matrix=Rc.tolist(), translate=(p['tK'] - Rc @ p['tJ']).tolist()))
        facts[hc] = dict(lanterns=sum(1 for o in owner if o == hc), lights=len(bones), tris=int((tri_owner == hc).sum()))
        assert (facts[hc]['lanterns'], facts[hc]['lights']) == EXPECT[hc], f'{hc}: {facts[hc]} != {EXPECT[hc]}'
    return dict(droptris={'meshes': drop}, transforms={'ops': ops}, bones={'move': moves}, lights=lights, kind=kind,
                facts=facts, street=dict(lanterns=len(street), stone_tris=len(s['tris']),
                                         lights=len(kind) - len(lights)))


def verify(model, files, place, pl):
    """every kept triangle = its vanilla triangle moved; lanterns on the Korean buildings; bones moved; boxes clean"""
    van = {m['name']: m for m in gr2_lint.read_raw(files['japan_night_lights.gr2'])['meshes']}
    out = gr2_lint.read_raw(model); new = {m['name']: m for m in out['meshes']}
    assert len(new[STREET_MESH]['tris']) == 0, 'street lanterns left'
    vm, nm = van[LANTERN_MESH], new[LANTERN_MESH]
    keep = np.setdiff1d(np.arange(len(vm['tris'])), pl['droptris']['meshes'][LANTERN_MESH])
    assert np.array_equal(vm['tris'][keep], nm['tris']), 'kept triangles changed order or corners'
    exp = vm['pos'][:, :3].copy()
    for op in pl['transforms']['ops']:
        v = op['meshes'][LANTERN_MESH]; R = np.asarray(op['matrix'])
        exp[v] = (exp[v] - op['pivot']) @ R.T + op['pivot'] + op['translate']
    used = np.unique(nm['tris'])
    err = float(np.abs(nm['pos'][used, :3] - exp[used]).max())
    assert err < 1e-4, f'moved positions off by {err}'
    assert np.array_equal(vm['uv'][used], nm['uv'][used]), 'UVs changed'
    tree, own = building_points(files, place, korean=True)
    n, lab = lanterns(dict(pos=nm['pos'][used], tris=np.searchsorted(used, nm['tris'])))
    gaps = {}
    for k in range(n):
        d, j = tree.query(nm['pos'][used[lab == k], :3]); i = int(np.argmin(d))
        gaps.setdefault(own[j[i]], []).append(float(d[i]))
    worst = max(max(g) for g in gaps.values())
    assert worst < 1.3, f'a lantern is {worst:.2f} from its Korean building'
    vb = {b['name']: np.asarray(b['world'])[3, :3] for b in gr2_lint.read_raw(files['japan_night_lights.gr2'])['bones']}
    nb = {b['name']: np.asarray(b['world'])[3, :3] for b in out['bones']}
    berr = 0.0
    for mv in pl['bones']['move']:
        R = np.asarray(mv['matrix'])
        for b in mv['bones']:
            berr = max(berr, float(np.abs(R @ vb[b] + mv['translate'] - nb[b]).max()))
    assert berr < 1e-3, f'light bones off by {berr}'
    stale = [(r['mesh'], r.get('error')) for r in gr2_bounds.bindings(str(model)) if r.get('outside') or r.get('error')]
    assert not stale, f'stale bone boxes: {stale}'
    return dict(position_err=err, bone_err=berr, lanterns=n, worst_gap=round(worst, 3),
                median_gap={k: round(float(np.median(v)), 3) for k, v in gaps.items()},
                per_building={k: len(v) for k, v in gaps.items()}, tris=int(len(nm['tris'])))


def animfile(pl, files):
    anim = files['japan_night_lights.xml'].read_text(encoding='utf-8')
    kinds = sorted(set(pl['kind'][b] for b in pl['lights']))
    att = {a: f for a, f in re.findall(r'<attachment>(\w+)<component>emiter<assetreference type="popcornfx">\s*<file>([^<]+)</file>', anim)}
    bones = sorted(pl['lights'], key=lambda b: int(b.split('_')[1]))
    L = ['<animfile>'] + [f'  <definebone>{b}</definebone>' for b in bones]
    for a in kinds:
        L += [f'  <attachment>{a}', '    <component>emiter', '      <assetreference type="popcornfx">',
              f'        <file>{att[a]}</file>', '      </assetreference>', '    </component>',
              '    <anim>idle', '      <component>emiter</component>', '    </anim>', '  </attachment>']
    L += ['  <component>korean_night_lanterns', '    <assetreference type="GrannyModel">', f'      <file>{GAME_PATH}</file>',
          '    </assetreference>']
    L += [f'    <attach a="{pl["kind"][b]}" frombone="ATTACHPOINT" tobone="{b}" syncanims="0" />' for b in bones]
    L += ['  </component>', '  <anim>Idle', '    <component>korean_night_lanterns</component>', '  </anim>', '</animfile>', '']
    return '\r\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--keep', help='work folder to keep (vanilla, plan, intermediates); default a temp folder')
    ap.add_argument('--deploy', action='store_true', help=f'write the verified model, material and animfile into {OUT}')
    a = ap.parse_args(argv)
    work = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix='knightl_')); work.mkdir(parents=True, exist_ok=True)
    files = vanilla(work)
    place = placements(files, work)
    pl = plan(files, place)
    (work / 'plan.json').write_text(json.dumps({k: v for k, v in pl.items()}, indent=1), encoding='utf-8')
    step1, step2, model = work / 'step1_droptris.gr2', work / 'step2_moved.gr2', work / f'{MODEL}.gr2'
    gr2_droptris.drop(files['japan_night_lights.gr2'], pl['droptris'], step1)
    gr2_rotate_verts.rotate(step1, pl['transforms'], step2)
    gr2_bones.edit(step2, pl['bones'], model)
    rep = verify(model, files, place, pl)
    material = files['japan_night_lights.material'].read_text(encoding='utf-8').replace('\r\n', '\n').replace('\n', '\r\n')
    (work / f'{MODEL}.material').write_bytes(material.encode('utf-8'))
    (work / ANIMFILE.name).write_bytes(animfile(pl, files).encode('utf-8'))
    print('PLAN', json.dumps(dict(facts=pl['facts'], street=pl['street'])))
    print('VERIFIED', json.dumps(rep))
    if a.deploy:
        OUT.mkdir(parents=True, exist_ok=True)
        for f in (model, work / f'{MODEL}.material'):
            shutil.copyfile(f, OUT / f.name)
        shutil.copyfile(work / ANIMFILE.name, ANIMFILE)
        print('DEPLOYED', OUT / model.name, OUT / f'{MODEL}.material', ANIMFILE)
    print('WORK', work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
