"""Dump the rider's triangles: UV (texture space) + 3D rest position + normal per corner.
blender -b --factory-startup --python dump_uv3d.py -- <rider.fbx> <out.json>"""
import json
import sys

import bpy

fbx, out = sys.argv[sys.argv.index('--') + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
dg = bpy.context.evaluated_depsgraph_get()
tris = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    mw = ev.matrix_world
    nm = mw.to_3x3()
    for t in me.loop_triangles:
        tris.append({'o': o.name,
                     'uv': [list(uv[li].uv) for li in t.loops],
                     'p': [list(mw @ me.vertices[vi].co) for vi in t.vertices],
                     'n': list((nm @ t.normal).normalized())})
    print('MESH', o.name, len(me.loop_triangles), 'uv layers', [l.name for l in me.uv_layers])
    ev.to_mesh_clear()
json.dump(tris, open(out, 'w'))
print('TRIS', len(tris))
