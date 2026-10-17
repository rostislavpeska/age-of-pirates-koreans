#!/usr/bin/env python
"""Korean Home City docks01 (art/homecity/korean/docks01): the pier, its collision mesh and the right junk where the owner
put them in the Blender scene, as IN-PLACE edits of vanilla homecity/china/docks01, under the VANILLA Idle animation.
Audit: Blendify journal 2026-10-17-claude-opus-5.5-01..12.

    python tools/homecity_docks01.py --blend <korean_homecity_test.blend> [--deploy] [--keep DIR]

Owner, after three game tests (2026-10-17): "I think we drift to overengineering! ... Left junk was animated correctly,
so it's ok. Right was exaggerated, and jumping, because was animated from wrong bone. So left can stay as was, right can
be static with no anim. And that's it." That snapshot was the previous agent's first build (vanilla skeleton + vanilla
anim, vertices moved); every later build with a converter-made Idle misplaced the junks and/or the dock in game.

 1. background Blender exports world vertices, loop triangles and UVs (docks01_M0Shape must be absent: deleted);
    frame GR2 = (-2.54 x, 2.54 z, -2.54 y), winding reversed, UV (u, 1 - v);
 2. vanilla docks01.gr2 / docks01_anim.gr2 from the installed game (bartool, temp folder only);
 3. MOVED meshes = vanilla + one measured rigid move: the pier (kept vanilla triangles + the owner's duplicated post via
    gr2_droptris "dup") and the collision mesh by their object translation, the right junk by a Procrustes fit
    (residual < 1e-4); docks01_M0Shape loses every triangle; the LEFT junk keeps its vanilla bytes - the vanilla Idle
    places and rocks it (the owner: correct);
 4. gr2_droptris then gr2_rotate_verts (both refresh the bone boxes); skeleton untouched;
 5. Idle = the vanilla anim with the right junk's track renamed (gr2_rename.py track, same length, same sort slot, no
    bone has the name): it drives nothing, so the right junk stays static at its Blender spot - no converter involved;
 6. proof: every Blender triangle of a moved mesh is one GR2 triangle (corners < 1e-3, reversed winding, UVs), M0 0
    triangles, left junk byte-identical to vanilla, gr2_bounds clean, anim == vanilla except that one name - else
    nothing is deployed.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
import korean_visuals  # noqa: E402  (AOP, BARTOOL)
AOP = Path(korean_visuals.AOP); HAVOK = AOP / 'scripts' / 'havok'
sys.path.insert(0, str(HAVOK))
import gr2_bounds, gr2_droptris, gr2_lint, gr2_rotate_verts  # noqa: E402,E401
from gr2_rest_anim import tracks_of  # noqa: E402

OUT = REPO / 'art' / 'homecity' / 'korean' / 'docks01'
VANILLA = ('homecity/china/docks01/docks01.gr2', 'homecity/china/docks01/docks01_anim.gr2')
MOVED = ['docks01Shape', 'docks01_M1Shape', 'docks01_wokou_junkShape']
KEPT_VANILLA = ['docks01_wokou_junk1Shape']                     # the left junk: the vanilla Idle places and rocks it
DELETED = ['docks01_M0Shape']
STATIC_TRACKS = {'bone_hc_wokou_junk': 'bone_hc_wokou_jun_'}    # the right junk's pivot: no anim (owner)
EPS = 1e-4

BPY = r'''
import bpy, json, sys, numpy as np
names, out = json.loads(sys.argv[-2]), sys.argv[-1]
dg = bpy.context.evaluated_depsgraph_get(); arrs = {}
meta = {'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty, 'docks_objects': sorted(o.name for o in bpy.data.objects if 'docks01' in o.name)}
for n in names:
    ob = bpy.data.objects.get(n)
    if ob is None: continue
    M = np.array(ob.matrix_world); me = ob.evaluated_get(dg).to_mesh(); me.calc_loop_triangles()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    tv = np.empty(len(me.loop_triangles) * 3, np.int64); me.loop_triangles.foreach_get('vertices', tv)
    tl = np.empty(len(me.loop_triangles) * 3, np.int64); me.loop_triangles.foreach_get('loops', tl)
    uv = np.empty(len(me.loops) * 2); me.uv_layers.active.data.foreach_get('uv', uv)
    arrs[n + '__world'] = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]; arrs[n + '__mw'] = M
    arrs[n + '__tv'] = tv.reshape(-1, 3); arrs[n + '__tl'] = tl.reshape(-1, 3); arrs[n + '__uv'] = uv.reshape(-1, 2)
    ob.evaluated_get(dg).to_mesh_clear()
np.savez(out, **arrs); json.dump(meta, open(out + '.json', 'w'))
'''


def b2g(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.column_stack([-2.54 * P[:, 0], 2.54 * P[:, 2], -2.54 * P[:, 1]])


def blender_export(exe, blend, work):
    script, out = work / 'export_docks.py', work / 'blender_docks.npz'
    script.write_text(BPY, encoding='utf-8')
    r = subprocess.run([exe, '-b', str(blend), '--python', str(script), '--', json.dumps(MOVED + KEPT_VANILLA + DELETED), str(out)],
                       capture_output=True, text=True, timeout=600)
    assert out.exists(), f'Blender export failed (rc {r.returncode}):\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}'
    z = np.load(out); meta = json.loads(Path(str(out) + '.json').read_text())
    return {k: z[k] for k in z.files}, meta


def vanilla(work):
    for rel in VANILLA:
        if not (work / Path(rel).name).exists():
            subprocess.run([sys.executable, korean_visuals.BARTOOL, 'extract', rel, '-o', str(work), '--flat'], check=True,
                           capture_output=True, timeout=600)
    return work / 'docks01.gr2', work / 'docks01_anim.gr2'


def procrustes(A, B):
    """B ~ A @ R.T + t (proper rotation)"""
    ca, cb = A.mean(0), B.mean(0); U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))]); R = Vt.T @ D @ U.T
    return R, cb - R @ ca, float(np.linalg.norm(A @ R.T + cb - R @ ca - B, axis=1).max())


def plan_mesh(name, bl, m):
    """-> (drop tri ids, dup ops, transform op, facts) reproducing the Blender mesh from the vanilla one"""
    W = b2g(bl[name + '__world']); BT = bl[name + '__tv']; vp, vt = m['pos'], m['tris']
    if len(W) == m['nv']:
        R, t, res = procrustes(vp, W)
        assert res < EPS, f'{name}: same vertex count but no rigid fit (residual {res:.5f})'
        op = {'translate': t.tolist(), 'meshes': {name: 'all'}}
        if np.abs(R - np.eye(3)).max() > 1e-6:
            op['matrix'] = R.tolist()
        deg = float(np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))))
        return [], [], op, dict(kind='rigid fit', residual=res, degrees=round(deg, 4), translate=np.round(t, 5).tolist())
    M = bl[name + '__mw']
    assert np.abs(M[:3, :3] - np.eye(3)).max() < 1e-6, f'{name}: trimmed mesh with a rotated/scaled object'
    t = b2g(M[:3, 3])[0]; G = W - t
    dc, ti = cKDTree(vp[vt].mean(1)).query(G[BT].mean(1))
    kept = set()
    for k in np.where(dc < EPS)[0]:
        if np.abs(np.sort(vp[vt[ti[k]]], 0) - np.sort(G[BT[k]], 0)).max() < EPS:
            kept.add(int(ti[k]))
    rest = [k for k in range(len(BT)) if not (dc[k] < EPS and int(ti[k]) in kept)]
    dups = []
    if rest:
        UV = np.column_stack([bl[name + '__uv'][:, 0], 1 - bl[name + '__uv'][:, 1]]); TL = bl[name + '__tl']
        kp, ku = cKDTree(vp), cKDTree(m['uv'])
        corners = [(int(BT[k][c]), int(TL[k][c])) for k in rest for c in range(3)]
        best = None
        for j in ku.query_ball_point(UV[corners[0][1]], EPS):          # candidate offsets from the first corner's UV twins
            off = G[corners[0][0]] - vp[j]; donors = []
            for v, l in corners:
                cand = [x for x in kp.query_ball_point(G[v] - off, EPS) if np.abs(m['uv'][x] - UV[l]).max() < EPS]
                if not cand: break
                donors.append(cand[0])
            else:
                best = (off, donors); break
        assert best, f'{name}: {len(rest)} Blender triangles are neither vanilla nor a translated copy of vanilla ones'
        off, donors = best; byset = {frozenset(t_.tolist()): i for i, t_ in enumerate(vt)}
        src = [byset.get(frozenset(donors[3 * i:3 * i + 3])) for i in range(len(rest))]
        assert None not in src, f'{name}: copied corners do not form vanilla triangles'
        dups = [{'tris': src, 'translate': off.tolist()}]
    drop = sorted(set(range(len(vt))) - kept)
    return drop, dups, {'translate': t.tolist(), 'meshes': {name: 'all'}}, dict(
        kind='object translation + drop/dup', translate=np.round(t, 5).tolist(), kept=len(kept), dropped=len(drop),
        duplicated=len(rest), dup_offset=None if not dups else np.round(dups[0]['translate'], 5).tolist())


def verify(path, van, bl, anim, van_anim):
    """moved meshes == Blender (corners, reversed winding, UVs); M0 empty; left junk == vanilla; boxes clean; anim ==
    vanilla except the renamed track(s)"""
    info = gr2_lint.read_raw(path); meshes = {m['name']: m for m in info['meshes']}; rep = {}
    for name in MOVED:
        m = meshes[name]; W = b2g(bl[name + '__world']); BT = bl[name + '__tv']; TL = bl[name + '__tl']
        UV = np.column_stack([bl[name + '__uv'][:, 0], 1 - bl[name + '__uv'][:, 1]])
        T = m['tris']; assert len(T) == len(BT), f'{name}: {len(T)} GR2 vs {len(BT)} Blender triangles'
        _, gi = cKDTree(m['pos'][T].mean(1)).query(W[BT].mean(1)); assert len(set(gi.tolist())) == len(BT), f'{name}: not 1:1'
        perr = uerr = 0.0; wind = 0
        for k, g in enumerate(gi):
            gt = T[g]; perm = [int(np.argmin(np.linalg.norm(m['pos'][gt] - W[v], axis=1))) for v in BT[k]]
            assert sorted(perm) == [0, 1, 2], f'{name}: triangle {k} corners do not correspond'
            perr = max(perr, float(np.abs(m['pos'][gt[perm]] - W[BT[k]]).max()))
            uerr = max(uerr, float(np.abs(m['uv'][gt[perm]] - UV[TL[k]]).max()))
            wind += (perm[1] - perm[0]) % 3 == 2                           # reversed cyclic order
        rep[name] = dict(tris=len(T), max_corner_err=round(perr, 6), max_uv_err=round(uerr, 5), reversed=wind)
        assert perr < 1e-3 and wind == len(BT) and uerr < 2e-3, (name, rep[name])
    for name in DELETED:
        assert len(meshes[name]['tris']) == 0, f'{name}: deleted in Blender but still drawn'
        rep[name] = dict(tris=0)
    vm = {m['name']: m for m in gr2_lint.read_raw(van)['meshes']}
    for name in KEPT_VANILLA:
        same = np.array_equal(meshes[name]['pos'], vm[name]['pos']) and np.array_equal(meshes[name]['tris'], vm[name]['tris'])
        assert same, f'{name}: must stay vanilla (the vanilla Idle places it)'
        rep[name] = 'vanilla bytes'
    bad = [b for b in gr2_bounds.bindings(path) if b.get('outside')]
    assert not bad, f'stale bone boxes: {[(b["mesh"], b["excess"]) for b in bad]}'
    va, vb = Path(van_anim).read_bytes(), Path(anim).read_bytes()
    assert len(va) == len(vb) and [STATIC_TRACKS.get(t, t) for t in tracks_of(van_anim)] == tracks_of(anim), 'anim tracks'
    rep['anim_bytes_changed'] = int(sum(x != y for x, y in zip(va, vb)))
    rep['tracks_renamed'] = STATIC_TRACKS
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--blend', required=True, help="the owner's Blender scene (source of truth)")
    ap.add_argument('--blender', default=os.environ.get('BLENDER_EXE') or shutil.which('blender')
                    or r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
    ap.add_argument('--keep', help='work folder to keep (plans, intermediates); default a temp folder')
    ap.add_argument('--deploy', action='store_true', help=f'copy the verified model and anim into {OUT}')
    a = ap.parse_args(argv)
    work = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix='kdocks_')); work.mkdir(parents=True, exist_ok=True)
    bl, meta = blender_export(a.blender, a.blend, work)
    assert not set(DELETED) & set(meta['docks_objects']), f'{DELETED} still in the scene: {meta["docks_objects"]}'
    assert all(n + '__world' in bl for n in MOVED), f'missing objects: {[n for n in MOVED if n + "__world" not in bl]}'
    van, van_anim = vanilla(work)
    vm = {m['name']: m for m in gr2_lint.read_raw(van)['meshes']}
    drop = {n: list(range(len(vm[n]['tris']))) for n in DELETED}; dup = {}; ops = []; facts = {}
    for n in MOVED:
        d_, u_, op, facts[n] = plan_mesh(n, bl, vm[n])
        if d_: drop[n] = d_
        if u_: dup[n] = u_
        ops.append(op)
    plan = dict(droptris={'meshes': drop, 'dup': dup}, transforms={'ops': ops}, static_tracks=STATIC_TRACKS, facts=facts,
                blend=dict(path=str(a.blend), sha256=hashlib.sha256(Path(a.blend).read_bytes()).hexdigest()))
    (work / 'plan.json').write_text(json.dumps(plan, indent=1), encoding='utf-8')
    step1, model, anim = work / 'step1_droptris.gr2', work / 'korean_docks01.gr2', work / 'korean_docks01_anim.gr2'
    gr2_droptris.drop(van, plan['droptris'], step1)
    gr2_rotate_verts.rotate(step1, plan['transforms'], model)
    ren = [x for old, new in STATIC_TRACKS.items() for x in ('track', old, new)]
    r = subprocess.run([sys.executable, str(HAVOK / 'gr2_rename.py'), str(van_anim), str(anim), *ren], capture_output=True,
                       text=True, timeout=300, cwd=str(HAVOK))
    assert r.returncode == 0 and anim.exists(), f'track rename failed: {r.stdout}{r.stderr}'
    rep = verify(model, van, bl, anim, van_anim)
    print('PLAN', json.dumps(facts)); print('VERIFIED', json.dumps(rep))
    if a.deploy:
        shutil.copyfile(model, OUT / model.name); shutil.copyfile(anim, OUT / anim.name)
        print('DEPLOYED', OUT / model.name, OUT / anim.name)
    print('WORK', work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
