#!/usr/bin/env python
"""Korean Home City lanterns (art/homecity/korean/lanterns): the Cheongsachorong lanterns where the owner's Blender scene
has them, as IN-PLACE edits of vanilla homecity/china/lantern_upgrade - vanilla skeleton, no whole-model converter.
Audit: Blendify journal 2026-10-17-claude-opus-5.5-18 (diagnosis), -20 (reuse decision).

    python tools/homecity_lanterns.py --blend <korean_homecity_test.blend> [--deploy] [--keep DIR]
    python tools/homecity_lanterns.py --check          # the installed files (no Blender)

Why (2026-10-17): the previous model was a whole-model converter rebuild of an FBX from another session's scene - a cm
skeleton (bone scale 100) under the vanilla metre Idle, the drawbridge strings moved 47 m in the GR2 only, a mesh the
scene no longer has - and the owner saw the lanterns "100% flawed and displaced". aoe3de-complex-scene-export rule 1.

 1. background Blender exports the 6 Korean_Lanterns meshes (world vertices, loop triangles, UVs, corner normals, slot
    materials); the owner's scene has no building_lanterns_GEOShape (its lanterns are the NL_* building objects);
 2. vanilla lantern_upgrade.gr2 from the installed game (bartool, work folder only); frame GR2 = (-2.54 x, 2.54 z,
    -2.54 y), winding reversed, UV (u, 1 - v);
 3. per mesh: Blender triangles that coincide with a vanilla triangle (sorted corners < EPS) keep their VANILLA bytes;
    every other vanilla triangle is dropped (the Chinese bodies, building_lanterns entirely); every other Blender
    triangle is NEW geometry: one rigid mesh per (scene mesh, material) on BONE_MAIN, bound to the vanilla material
    record (Korean bodies -> mata, which korean_lantern_upgrade.material maps to the Korean textures; new ropes -> mate);
 4. gr2_droptris then gr2_editmesh (new meshes from Blender vertices; tangents from the UVs; it registers the native
    marshalling records of the new vertex arrays and scrubs orphan fixups); skeleton untouched;
 5. STATIC: the owner's lantern meshes have no vertex weights (nothing sways in Blender) and the new bodies are rigid,
    while the vanilla Idle swings the kept ropes of Wall_Move (12.8 deg) and bridge_move_R (9.0 deg) with blended
    weights - so korean_lanterns.xml plays no anim and the model stays at the skeleton rest = the Blender scene;
 6. proof: every Blender triangle is exactly one GR2 triangle (corners < 1e-3, reversed winding, UVs), kept ropes keep
    their vanilla vertex bytes, building_lanterns 0 triangles, skeleton == vanilla, bone boxes clean, no orphan fixups,
    the game's Granny DLL reads the file - else nothing is deployed.
To change a lantern: edit it in Blender, save, rerun with --deploy.
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
import gr2_bounds, gr2_droptris, gr2_lint  # noqa: E402,E401
from gr2_fixups import orphan_fixups  # noqa: E402
sys.path.insert(0, str(AOP / 'scripts' / 'tools'))
import local_env  # noqa: E402
BLENDIFY = Path(os.environ.get('BLENDIFY_REPO') or local_env.value('BLENDIFY_REPO'))
sys.path.insert(0, str(BLENDIFY / '.claude' / 'skills' / 'blender-complex-scene' / 'scripts'))
import edit_match  # noqa: E402  (the generic measure/prove method: Blendify blender-complex-scene)

OUT = REPO / 'art' / 'homecity' / 'korean' / 'lanterns'
MODEL = OUT / 'korean_lantern_upgrade.gr2'
ANIMFILE = OUT / 'korean_lanterns.xml'
MATERIAL = OUT / 'korean_lantern_upgrade.material'
TEXTURES = ['korean_lanterns_mata_basecolor.ddt', 'korean_lanterns_mata_emissive.ddt', 'korean_lanterns_mata_normals.ddt',
            'korean_lanterns_mata_masks.ddt']
VANILLA = 'homecity/china/lantern_upgrade/lantern_upgrade.gr2'
MESHES = ['Wall_Move_lanterns_GEO3Shape', 'bridge_BG_lanterns_GEOShape', 'bridge_move_lanterns_L_GEOShape',
          'bridge_move_lanterns_R_GEOShape', 'enrty_lanterns_GEOShape', 'stall_lanterns_GEOShape']
DELETED = ['building_lanterns_GEOShape']                        # not in the owner's scene
SLOT_MATERIAL = {'mate': 'mate', 'Korean_Cheongsachorong_Lantern_Mat': 'mata'}   # Blender slot -> vanilla GR2 material
TEMPLATE = 'enrty_lanterns_GEOShape'                           # rigid 24-byte source mesh for gr2_editmesh
EPS = 1e-4

BPY = r'''
import bpy, json, sys, numpy as np
names, out = json.loads(sys.argv[-2]), sys.argv[-1]
dg = bpy.context.evaluated_depsgraph_get(); arrs = {}
meta = {'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty, 'slots': {}, 'groups': {},
        'lantern_objects': sorted(o.name for o in bpy.data.objects if 'lanterns_GEO' in o.name)}
for n in names:
    ob = bpy.data.objects.get(n)
    if ob is None: continue
    M = np.array(ob.matrix_world); me = ob.evaluated_get(dg).to_mesh(); me.calc_loop_triangles()
    nt, nl = len(me.loop_triangles), len(me.loops)
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    tv = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get('vertices', tv)
    tl = np.empty(nt * 3, np.int64); me.loop_triangles.foreach_get('loops', tl)
    tm = np.empty(nt, np.int64); me.loop_triangles.foreach_get('material_index', tm)
    uv = np.empty(nl * 2); me.uv_layers.active.data.foreach_get('uv', uv)
    cn = np.empty(nl * 3); me.corner_normals.foreach_get('vector', cn)
    arrs[n + '__world'] = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]; arrs[n + '__mw'] = M
    arrs[n + '__tv'] = tv.reshape(-1, 3); arrs[n + '__tl'] = tl.reshape(-1, 3); arrs[n + '__tm'] = tm
    arrs[n + '__uv'] = uv.reshape(-1, 2)
    N = cn.reshape(-1, 3) @ np.linalg.inv(M[:3, :3]); arrs[n + '__cn'] = N / np.linalg.norm(N, axis=1)[:, None]
    meta['slots'][n] = [s.material.name if s.material else None for s in ob.material_slots]
    meta['groups'][n] = [g.name for g in ob.vertex_groups]
    ob.evaluated_get(dg).to_mesh_clear()
np.savez(out, **arrs); json.dump(meta, open(out + '.json', 'w'))
'''


def b2g(P):
    P = np.asarray(P, float).reshape(-1, 3)
    return np.column_stack([-2.54 * P[:, 0], 2.54 * P[:, 2], -2.54 * P[:, 1]])


def blender_export(exe, blend, work):
    script, out = work / 'export_lanterns.py', work / 'blender_lanterns.npz'
    script.write_text(BPY, encoding='utf-8')
    r = subprocess.run([exe, '-b', str(blend), '--python', str(script), '--', json.dumps(MESHES + DELETED), str(out)],
                       capture_output=True, text=True, timeout=900)
    assert out.exists(), f'Blender export failed (rc {r.returncode}):\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}'
    z = np.load(out); meta = json.loads(Path(str(out) + '.json').read_text())
    return {k: z[k] for k in z.files}, meta


def vanilla(work):
    p = work / Path(VANILLA).name
    if not p.exists():
        subprocess.run([sys.executable, korean_visuals.BARTOOL, 'extract', VANILLA, '-o', str(work), '--flat'], check=True,
                       capture_output=True, timeout=600)
    return p


def edited(name, bl, tris=None):
    """the Blender object in the GR2 frame for edit_match: world positions, triangles, corner UVs (u, 1 - v)"""
    UV = np.column_stack([bl[name + '__uv'][:, 0], 1 - bl[name + '__uv'][:, 1]])
    tv, tl = bl[name + '__tv'], bl[name + '__tl']
    if tris is not None:
        tv, tl = tv[tris], tl[tris]
    return dict(pos=b2g(bl[name + '__world']), tris=tv, corner_uv=UV[tl])


def split(name, bl, m):
    """-> (kept vanilla triangle ids, new Blender triangle ids): a Blender triangle whose sorted corners equal a vanilla
    triangle's keeps the vanilla bytes; the object transform must be identity (the lantern objects sit on the armature)"""
    assert np.abs(bl[name + '__mw'] - np.eye(4)).max() < 1e-6, f'{name}: object transform is not identity'
    vp, vt = np.asarray(m['pos'], float), m['tris']
    G, BT = b2g(bl[name + '__world']), bl[name + '__tv']
    dc, ti = cKDTree(vp[vt].mean(1)).query(G[BT].mean(1))
    kept, kept_dst = set(), set()
    for k in np.where(dc < EPS)[0]:
        if int(ti[k]) not in kept and np.abs(np.sort(vp[vt[ti[k]]], 0) - np.sort(G[BT[k]], 0)).max() < EPS:
            kept.add(int(ti[k])); kept_dst.add(int(k))
    return sorted(kept), [k for k in range(len(BT)) if k not in kept_dst]


def new_mesh(name, bl, tris, material, src_vertex=0):
    """gr2_editmesh "new" entry for Blender triangles `tris`: one vertex per (vertex, UV, normal) corner, GR2 frame,
    reversed winding (the frame map is a reflection)"""
    W = b2g(bl[name + '__world']); tv, tl = bl[name + '__tv'][tris], bl[name + '__tl'][tris]
    UV, CN = bl[name + '__uv'], bl[name + '__cn']
    index, verts, out = {}, [], []
    for t in range(len(tv)):
        c = []
        for v, l in zip(tv[t], tl[t]):
            u = (float(UV[l, 0]), float(1 - UV[l, 1])); n = (-CN[l, 0], CN[l, 2], -CN[l, 1])
            key = (int(v), round(u[0], 6), round(u[1], 6), round(n[0], 4), round(n[1], 4), round(n[2], 4))
            if key not in index:
                index[key] = len(verts)
                verts.append(dict(src=src_vertex, pos=[float(x) for x in W[v]], uv=list(u), nrm=[float(x) for x in n]))
            c.append(index[key])
        out.append([c[0], c[2], c[1]])
    return dict(name=f'{name}_KR_{material}', bone='BONE_MAIN', use_material=material, extra_verts=verts,
                extra_tris=out)


def verify(path, van, bl, plan):
    """every Blender triangle == one GR2 triangle of its mesh + its new meshes; kept ropes vanilla bytes; deleted meshes
    empty; skeleton == vanilla; boxes clean; no orphan fixups"""
    info = gr2_lint.read_raw(path); meshes = {m['name']: m for m in info['meshes']}; rep = {}
    vm = {m['name']: m for m in gr2_lint.read_raw(van)['meshes']}
    for name in MESHES:
        parts = [meshes[name]] + [meshes[n['name']] for n in plan['new'] if n['name'].startswith(name + '_KR_')]
        pos, tris, uv, off = [], [], [], 0
        for p in parts:
            pos.append(p['pos']); uv.append(p['uv']); tris.append(p['tris'] + off); off += len(p['pos'])
        out = dict(pos=np.concatenate(pos), tris=np.concatenate(tris), uv=np.concatenate(uv))
        r = edit_match.verify(edited(name, bl), out, reversed_winding=True)
        assert np.array_equal(meshes[name]['comps']['Position'], vm[name]['comps']['Position']), f'{name}: vanilla vertices changed'
        rep[name] = dict(tris=r['tris'], kept_vanilla=len(meshes[name]['tris']), new=r['tris'] - len(meshes[name]['tris']),
                         max_corner_err=round(r['max_corner_err'], 6), max_uv_err=round(r['max_uv_err'], 5))
    for name in DELETED:
        assert len(meshes[name]['tris']) == 0, f'{name}: not in the scene, still drawn'
        rep[name] = dict(tris=0)
    vb = {b['name']: b for b in gr2_lint.read_raw(van)['bones']}; ob = {b['name']: b for b in info['bones']}
    assert list(vb) == list(ob) and all(np.allclose(vb[n]['world'], ob[n]['world'], atol=1e-6) and vb[n]['rest'] == ob[n]['rest']
                                        for n in vb), 'skeleton differs from vanilla'
    bad = [b for b in gr2_bounds.bindings(str(path)) if b.get('outside')]
    assert not bad, f'stale bone boxes: {[(b["mesh"], b["excess"]) for b in bad]}'
    assert not orphan_fixups(str(path))['orphans'], 'orphan pointer fixups'
    rep['skeleton'] = 'vanilla'
    return rep


def check_installed():
    """the installed files: textures, CRLF material with the Korean maps, a static animfile, the model's structure"""
    for t in TEXTURES:
        assert (OUT / 'textures' / t).stat().st_size == 174872, f'{t}: not the 512x512 DXT1 texture (174,872 B)'
    raw = MATERIAL.read_bytes(); assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b''), 'material must be CRLF'
    assert b'korean_lanterns_mata_basecolor' in raw and b'name="mate"' in raw, 'material maps'
    a = ANIMFILE.read_bytes(); assert b'\n' not in a.replace(b'\r\n', b''), 'animfile must be CRLF'
    assert b'GrannyAnim' not in a, 'the lanterns are static (step 5): korean_lanterns.xml plays no anim'
    info = gr2_lint.read_raw(MODEL); meshes = {m['name']: m for m in info['meshes']}
    assert all(len(meshes[n]['tris']) == 0 for n in DELETED), 'deleted meshes drawn'
    kr = [n for n in meshes if '_KR_' in n]; assert kr and all(n.split('_KR_')[0] in MESHES for n in kr), kr
    assert [b['name'] for b in info['bones']] == ['BONE_MAIN', 'wall_rotate_JNT', 'bridge_rotate_JNT'], 'vanilla skeleton'
    assert not [b for b in gr2_bounds.bindings(str(MODEL)) if b.get('outside')], 'stale bone boxes'
    return dict(meshes={n: len(meshes[n]['tris']) for n in meshes}, textures='ok', material='ok', animfile='static')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--blend', help="the owner's Blender scene (source of truth)")
    ap.add_argument('--blender', default=os.environ.get('BLENDER_EXE') or shutil.which('blender')
                    or r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe')
    ap.add_argument('--keep', help='work folder to keep (plans, intermediates); default a temp folder')
    ap.add_argument('--deploy', action='store_true', help=f'copy the verified model to {MODEL}')
    ap.add_argument('--check', action='store_true', help='check the installed files only')
    a = ap.parse_args(argv)
    if a.check:
        print('CHECKED', json.dumps(check_installed())); return 0
    assert a.blend, '--blend is required unless --check'
    work = Path(a.keep) if a.keep else Path(tempfile.mkdtemp(prefix='klanterns_')); work.mkdir(parents=True, exist_ok=True)
    bl, meta = blender_export(a.blender, a.blend, work)
    assert not set(DELETED) & set(meta['lantern_objects']), f'{DELETED} is in the scene again: export it (recipe change)'
    missing = [n for n in MESHES if n + '__world' not in bl]; assert not missing, f'missing objects: {missing}'
    unknown = {s for n in MESHES for s in meta['slots'][n]} - set(SLOT_MATERIAL); assert not unknown, f'new material slots {unknown}'
    van = vanilla(work)
    vm = {m['name']: m for m in gr2_lint.read_raw(van)['meshes']}
    drop = {n: list(range(len(vm[n]['tris']))) for n in DELETED}; new = []; facts = {}
    for n in MESHES:
        kept, add = split(n, bl, vm[n])
        drop[n] = sorted(set(range(len(vm[n]['tris']))) - set(kept))
        slots = meta['slots'][n]; tm = bl[n + '__tm'][add]
        for si in sorted(set(tm.tolist())):
            new.append(new_mesh(n, bl, [k for k, s in zip(add, tm) if s == si], SLOT_MATERIAL[slots[si]]))
        facts[n] = dict(vanilla_kept=len(kept), vanilla_dropped=len(drop[n]), new=len(add),
                        new_by_material={SLOT_MATERIAL[slots[s]]: int((tm == s).sum()) for s in sorted(set(tm.tolist()))})
    plan = dict(droptris={'meshes': drop}, editmesh={'mesh': TEMPLATE, 'reset_root': False, 'new': new}, facts=facts,
                blend=dict(path=str(a.blend), sha256=hashlib.sha256(Path(a.blend).read_bytes()).hexdigest()))
    (work / 'plan.json').write_text(json.dumps(plan), encoding='utf-8')
    (work / 'editmesh.json').write_text(json.dumps(plan['editmesh']), encoding='utf-8')
    step1, model = work / 'step1_droptris.gr2', work / MODEL.name
    model.unlink(missing_ok=True)
    gr2_droptris.drop(van, plan['droptris'], step1)
    r = subprocess.run([sys.executable, str(HAVOK / 'gr2_editmesh.py'), str(step1), str(work / 'editmesh.json'), str(model)],
                       capture_output=True, text=True, timeout=900, cwd=str(HAVOK))
    assert r.returncode == 0 and model.exists(), f'gr2_editmesh failed: {r.stdout[-2000:]}{r.stderr[-2000:]}'
    rep = verify(model, van, bl, plan['editmesh'])
    profiles = json.loads((HAVOK / 'gr2_lint_profiles.json').read_text(encoding='utf-8'))
    dll = gr2_lint.dll_read(model, gr2_lint.find_tools(profiles), work)
    assert dll['status'] == 'PASS', f'Granny DLL read: {dll}'
    rep['dll_read'] = dll['status']
    print('PLAN', json.dumps(facts)); print('VERIFIED', json.dumps(rep))
    print('MODEL', model, model.stat().st_size, hashlib.sha256(model.read_bytes()).hexdigest())
    if a.deploy:
        shutil.copyfile(model, MODEL)
        print('DEPLOYED', MODEL, json.dumps(check_installed()))
    print('WORK', work)
    return 0


if __name__ == '__main__':
    sys.exit(main())
