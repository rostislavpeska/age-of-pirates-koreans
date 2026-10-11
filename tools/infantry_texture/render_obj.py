"""EEVEE turnaround of rest-pose OBJs, each with its own BaseColor (player colour already multiplied in) and an
optional DirectX normal map. Writes one strip PNG per call.
blender -b --factory-startup --python render_obj.py -- <out.png> <obj> <base.png> <normals.png|-> [<obj> <base> <nrm>]...
"""
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
out, rest = args[0], args[1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
meshes = []
for i in range(0, len(rest), 3):
    obj, base, normals = rest[i:i + 3]
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=obj, up_axis='Z', forward_axis='Y')
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    m = bpy.data.materials.new('m%d' % i)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Specular IOR Level'].default_value = 0.2
    tb = nt.nodes.new('ShaderNodeTexImage')
    tb.image = bpy.data.images.load(base)
    nt.links.new(tb.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tb.outputs['Alpha'], bsdf.inputs['Alpha'])        # cut-out cards (plumes) as in game
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'DITHERED'
    if normals != '-':
        tn = nt.nodes.new('ShaderNodeTexImage')
        tn.image = bpy.data.images.load(normals)
        tn.image.colorspace_settings.name = 'Non-Color'
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        inv = nt.nodes.new('ShaderNodeMath')
        inv.operation = 'SUBTRACT'
        inv.inputs[0].default_value = 1.0
        comb = nt.nodes.new('ShaderNodeCombineColor')
        nt.links.new(tn.outputs['Color'], sep.inputs['Color'])
        nt.links.new(sep.outputs['Red'], comb.inputs['Red'])
        nt.links.new(sep.outputs['Green'], inv.inputs[1])            # DirectX green -> OpenGL
        nt.links.new(inv.outputs['Value'], comb.inputs['Green'])
        nt.links.new(sep.outputs['Blue'], comb.inputs['Blue'])
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = 0.8
        nt.links.new(comb.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    for o in new:
        o.data.materials.clear()
        o.data.materials.append(m)
    meshes += new
pts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
c, size = (lo + hi) / 2, max(hi - lo)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
sc.render.resolution_x, sc.render.resolution_y = 384, 512
sc.render.film_transparent = False
w = bpy.data.worlds.new('w')
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.25, 0.25, 0.27, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2
sc.world = w
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(45), 0, math.radians(-30))
sc.collection.objects.link(sun)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = 'ORTHO'
cam.data.clip_start, cam.data.clip_end = size * 0.01, size * 100
shots = []
for label, az, zoom in (('a', 0, 1.0), ('b', 60, 1.0), ('c', 120, 1.0), ('d', 180, 1.0), ('e', 270, 1.0),
                        ('f', 30, 0.38)):
    t = Vector((c.x, c.y, hi.z - size * 0.17)) if zoom < 1 else c
    cam.data.ortho_scale = size * 1.05 * zoom
    r = math.radians(az)
    cam.location = t + Vector((math.sin(r), -math.cos(r), 0.12)).normalized() * size * 3
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z', 'Y').to_euler()
    p = out[:-4] + '_%s.png' % label
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    shots.append(p)
strip = bpy.data.images.new('strip', 384 * len(shots), 512)
px = [0.0] * (384 * len(shots) * 512 * 4)
for k, p in enumerate(shots):
    im = bpy.data.images.load(p)
    src = list(im.pixels)
    for y in range(512):
        row = src[y * 384 * 4:(y + 1) * 384 * 4]
        o = (y * 384 * len(shots) + k * 384) * 4
        px[o:o + 384 * 4] = row
    os.remove(p)
strip.pixels = px
strip.filepath_raw = out
strip.file_format = 'PNG'
strip.save()
print('DONE', out)
