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
    nothing is deployed;
 7. the HARBOUR junk is its own model on its own ground bone (owner: "add a new bone on a city layout so you can then
    place the junk there ... then the junk can be animated separately"; "structure which will be transparent so you
    don't get lost in dependencies"): ONE Blender object = ONE bone, and no Blender pivot matters. korean_harbour_junk
    is vanilla docks01 with every other mesh emptied - the junk's mesh, skeleton, pivot and Idle (the vanilla anim, by
    archive path) are byte-vanilla, so it rocks about its own pivot as in vanilla. bone_harbour_junk on
    korean_hc_ground carries the ONE measured rigid move from the vanilla junk to the Blender junk (gr2_addbones; moved
    there by gr2_bones on a re-run). To reposition the junk: move/rotate its object in Blender, save, rerun. Proof:
    ground bone x model == the Blender junk (< 1e-3), junk byte-vanilla, other meshes empty, existing ground bones
    unmoved, no orphan fixups. (Renaming the anim's BONE_MAIN track was refused: the string is the track group's name.)
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
import gr2_bones, gr2_bounds, gr2_droptris, gr2_lint, gr2_rotate_verts  # noqa: E402,E401
from gr2_rest_anim import tracks_of  # noqa: E402
sys.path.insert(0, str(AOP / 'scripts' / 'tools'))
import local_env  # noqa: E402
BLENDIFY = Path(os.environ.get('BLENDIFY_REPO') or local_env.value('BLENDIFY_REPO'))
sys.path.insert(0, str(BLENDIFY / '.claude' / 'skills' / 'blender-complex-scene' / 'scripts'))
import edit_match  # noqa: E402  (the generic measure/prove method: Blendify blender-complex-scene)

OUT = REPO / 'art' / 'homecity' / 'korean' / 'docks01'
GROUND = REPO / 'art' / 'homecity' / 'korean' / 'korean_hc_ground.gr2'
VANILLA = ('homecity/china/docks01/docks01.gr2', 'homecity/china/docks01/docks01_anim.gr2')
MOVED = ['docks01Shape', 'docks01_M1Shape']
KEPT_VANILLA = ['docks01_wokou_junk1Shape']                     # the left junk: the vanilla Idle places and rocks it
DELETED = ['docks01_M0Shape']
STATIC_TRACKS = {'bone_hc_wokou_junk': 'bone_hc_wokou_jun_'}    # docks01 no longer draws that junk; track stays unbound
# step 7 (owner 2026-10-17: "add a new bone on a city layout so you can then place the junk there ... then the junk can
# be animated separately"): the harbour junk is its own model on its own ground bone. One Blender object = one bone:
# the object's world transform IS bone_harbour_junk on korean_hc_ground, the model is the junk in the object's local
# frame, its Idle is the vanilla docks01 anim (the junk rocks about its own vanilla pivot) with the root track unbound
HARBOUR = 'docks01_wokou_junkShape'
HARBOUR_BONE = 'bone_harbour_junk'
HARBOUR_MODEL = 'korean_harbour_junk'                          # Idle: homecity\china\docks01\docks01_anim (vanilla path)
MIRROR = np.array([[-1, 0, 0], [0, 0, 1], [0, -1, 0]], float)  # GR2 = 2.54 * MIRROR . Blender
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
    r = subprocess.run([exe, '-b', str(blend), '--python', str(script), '--', json.dumps(MOVED + [HARBOUR] + KEPT_VANILLA + DELETED), str(out)],
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
    return edit_match.rigid_fit(A, B)


def edited(name, bl):
    """the Blender object in the GR2 frame for edit_match: world positions, triangles, corner UVs (u, 1 - v)"""
    UV = np.column_stack([bl[name + '__uv'][:, 0], 1 - bl[name + '__uv'][:, 1]])
    return dict(pos=b2g(bl[name + '__world']), tris=bl[name + '__tv'], corner_uv=UV[bl[name + '__tl']])


def plan_mesh(name, bl, m):
    """-> (drop tri ids, dup ops, transform op, facts) reproducing the Blender mesh from the vanilla one (edit_match)"""
    M = bl[name + '__mw']
    plan = edit_match.classify(dict(pos=m['pos'], tris=m['tris'], uv=m['uv']), edited(name, bl),
                               translate=b2g(M[:3, 3])[0], eps=EPS)
    if plan['kind'] == 'rigid':
        op = {'translate': plan['translate'], 'meshes': {name: 'all'}}
        if np.abs(np.array(plan['matrix']) - np.eye(3)).max() > 1e-6:
            op['matrix'] = plan['matrix']
        return [], [], op, dict(kind='rigid fit', residual=plan['residual'], degrees=round(plan['degrees'], 4),
                                translate=np.round(plan['translate'], 5).tolist())
    assert np.abs(M[:3, :3] - np.eye(3)).max() < 1e-6, f'{name}: trimmed mesh with a rotated/scaled object'
    assert plan['unexplained'] == 0, f"{name}: {plan['unexplained']} Blender triangles are neither vanilla nor a translated copy"
    dups = []                                                  # one op per offset (components sharing an offset merge)
    for d in plan['dup']:
        same = [x for x in dups if np.abs(np.subtract(x['translate'], d['translate'])).max() < EPS]
        if same:
            same[0]['tris'] += d['tris']
        else:
            dups.append(dict(tris=list(d['tris']), translate=d['translate']))
    t = plan['translate']
    return plan['dropped'], dups, {'translate': t, 'meshes': {name: 'all'}}, dict(
        kind='object translation + drop/dup', translate=np.round(t, 5).tolist(), kept=len(plan['kept']),
        dropped=len(plan['dropped']), duplicated=sum(len(d['tris']) for d in dups),
        dup_offset=None if not dups else np.round(dups[0]['translate'], 5).tolist())


def verify(path, van, bl, anim, van_anim):
    """moved meshes == Blender (corners, reversed winding, UVs); M0 empty; left junk == vanilla; boxes clean; anim ==
    vanilla except the renamed track(s)"""
    info = gr2_lint.read_raw(path); meshes = {m['name']: m for m in info['meshes']}; rep = {}
    for name in MOVED:                                         # GR2 winding = reversed Blender loop order (det -1 map)
        m = meshes[name]
        r = edit_match.verify(edited(name, bl), dict(pos=m['pos'], tris=m['tris'], uv=m['uv']), reversed_winding=True)
        rep[name] = dict(tris=r['tris'], max_corner_err=round(r['max_corner_err'], 6), max_uv_err=round(r['max_uv_err'], 5),
                         reversed=r['winding_ok'])
    for name in DELETED + [HARBOUR]:
        assert len(meshes[name]['tris']) == 0, f'{name}: deleted in Blender / split out, but still drawn by docks01'
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


def harbour(bl, van, work):
    """step 7: -> (model, ground, facts). The model is vanilla docks01 with every mesh but the harbour junk emptied -
    the junk's mesh, skeleton, pivot and (by archive path) Idle stay byte-vanilla, so it rocks about its own vanilla
    pivot. The ground bone carries the one measured rigid move F (vanilla junk -> the Blender junk): where the object's
    pivot sits in Blender does not matter."""
    vm = {m['name']: m for m in gr2_lint.read_raw(van)['meshes']}
    Rf, tf, res = procrustes(vm[HARBOUR]['pos'], b2g(bl[HARBOUR + '__world']))
    assert res < EPS, f'{HARBOUR}: no rigid fit to vanilla (residual {res:.5f})'
    Rog, tog = Rf, tf                                                          # the ground bone's world in GR2
    Ro = MIRROR.T @ Rf @ MIRROR; to = MIRROR.T @ tf / 2.54                     # the same transform in Blender
    Mo = np.eye(4); Mo[:3, :3] = Ro; Mo[:3, 3] = to
    h3 = work / (HARBOUR_MODEL + '.gr2')
    gr2_droptris.drop(van, {'meshes': {n: list(range(len(m['tris']))) for n, m in vm.items() if n != HARBOUR}}, h3)
    ground = work / GROUND.name
    shutil.copyfile(GROUND, ground)
    names = [b['name'] for b in gr2_lint.read_raw(ground)['bones']]
    if HARBOUR_BONE not in names:                                              # create it (gr2_addbones, GXO b-table)
        F = Ro.T                                                               # GXO rows = transposed column rotation
        table = work / 'harbour_bone.gxo'
        table.write_text('b "root" 0 1 0 0 0 1 0 0 0 1 0 0 0\n' + f'b "{HARBOUR_BONE}" 1 '
                         + ' '.join(f'{x:.9g}' for x in F.reshape(-1)) + ' ' + ' '.join(f'{x:.9g}' for x in Mo[:3, 3]) + '\n')
        r = subprocess.run([sys.executable, str(HAVOK / 'gr2_addbones.py'), str(GROUND), str(table), str(ground), '--inplace',
                            '--map', 'mirror', '--scale', '2.54', '--only', HARBOUR_BONE], capture_output=True, text=True,
                           timeout=300, cwd=str(HAVOK))
        assert r.returncode == 0, f'gr2_addbones failed: {r.stdout}{r.stderr}'
    else:                                                                      # reposition it: move by target . current^-1
        W = {b['name']: b['world'].T for b in gr2_lint.read_raw(ground)['bones']}[HARBOUR_BONE]
        D = np.eye(4); D[:3, :3] = Rog; D[:3, 3] = tog; D = D @ np.linalg.inv(W)
        if np.abs(D - np.eye(4)).max() > 1e-6:                                 # already there: leave the file byte-identical
            gr2_bones.edit(GROUND, {'move': [{'bones': [HARBOUR_BONE], 'matrix': D[:3, :3].tolist(), 'translate': D[:3, 3].tolist()}]}, ground)
    deg = float(np.degrees(np.arccos(np.clip((np.trace(Rf) - 1) / 2, -1, 1))))
    return h3, ground, dict(bone_world_gr2=np.round(tog, 5).tolist(), bone_world_blender=np.round(to, 5).tolist(),
                            fit_residual=res, fit_degrees=round(deg, 4))


def verify_harbour(model, van, ground, bl):
    """ground bone x model == the Blender junk; the junk byte-vanilla, other meshes empty; the ground keeps every other
    bone; no orphan fixups"""
    from gr2_fixups import orphan_fixups
    gb = {b['name']: b['world'] for b in gr2_lint.read_raw(ground)['bones']}
    W = gb[HARBOUR_BONE]                                                       # row-vector world
    info = gr2_lint.read_raw(model); m = {x['name']: x for x in info['meshes']}[HARBOUR]
    used = np.unique(m['tris']); P = (np.c_[m['pos'][used], np.ones(len(used))] @ W)[:, :3]
    Wb = b2g(bl[HARBOUR + '__world']); d, _ = cKDTree(Wb).query(P); err = float(d.max())
    assert err < 1e-3 and len(m['tris']) == len(bl[HARBOUR + '__tv']), f'harbour junk off the Blender spot by {err:.4f}'
    assert all(len(x['tris']) == 0 for x in info['meshes'] if x['name'] != HARBOUR), 'other meshes still drawn'
    v = {x['name']: x for x in gr2_lint.read_raw(van)['meshes']}[HARBOUR]
    assert np.array_equal(m['pos'], v['pos']) and np.array_equal(m['tris'], v['tris']), 'the harbour junk must stay vanilla'
    old = [b['name'] for b in gr2_lint.read_raw(GROUND)['bones']]; new = list(gb)
    assert new[:len(old)] == old and set(new) - set(old) <= {HARBOUR_BONE}, 'ground bones changed beyond the new one'
    ow = {b['name']: b['world'] for b in gr2_lint.read_raw(GROUND)['bones']}
    drift = max(float(np.abs(ow[n] - gb[n]).max()) for n in old if n != HARBOUR_BONE)
    assert drift < 1e-5, f'an existing ground bone moved ({drift:.2e})'
    assert not orphan_fixups(str(ground))['orphans'] and not orphan_fixups(str(model))['orphans'], 'orphan pointer fixups'
    return dict(max_vertex_err=round(err, 6), tris=len(m['tris']), bone_world_gr2=np.round(W[3, :3], 4).tolist(),
                ground_bones=f'{len(old)} -> {len(new)}', existing_bone_drift=drift)


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
    drop = {n: list(range(len(vm[n]['tris']))) for n in DELETED + [HARBOUR]}; dup = {}; ops = []; facts = {}
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
    h_model, ground, facts['harbour'] = harbour(bl, van, work)
    rep['harbour'] = verify_harbour(h_model, van, ground, bl)
    print('PLAN', json.dumps(facts)); print('VERIFIED', json.dumps(rep))
    if a.deploy:
        for f in (model, anim, h_model):
            shutil.copyfile(f, OUT / f.name)
        shutil.copyfile(OUT / 'korean_docks01.material', OUT / (HARBOUR_MODEL + '.material'))   # same vanilla textures
        shutil.copyfile(ground, GROUND)
        print('DEPLOYED', [str(OUT / f.name) for f in (model, anim, h_model)], GROUND)
    print('WORK', work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
