"""Joseon jeollip (military felt hat) for the Jochong Musketeer, modelled for the mod (owner 2026-10-09: "if you need
hats, these can be created separately and easily attached", "Hats are the easiest thing to craft"), in the vanilla
bandido hat's brim frame so it sits where that hat sits (<attach a="hats" frombone="bone_hat" tobone="HEAD">):
black felt dome crown clear of the head, wide flat brim (slight droop), brass jeongja knob on the apex, red sangmo
horsehair falling over the upper crown (two layers of strands, uneven tips). No player colour (historical).

Writes OUT/jeollip.obj (preview, GXO space), OUT/jeollip_{BaseColor,Normals,Masks}.png (512) and PARTS (default:
jeollip_parts.json next to this script): the geometry in the raw engine frame of the vanilla bandido hat
(engine = 2.54 * mirror(GXO), measured on bandido_hat.gr2 to 1.6e-8; the mirror reverses the winding), UVs in the
Blender convention, for tools/korean_infantry_model.py (AoP multimaterial_gr2.replace).

    python jeollip_model.py <AoP>/.claude/skills/aoe3de-unit-animation/scripts BANDIDO_HAT.gxo OUT [PARTS]
BANDIDO_HAT.gxo: the vanilla art/units/spc/outlaws/bandido_hat.gr2 converted with AoP gxo-convert (scratch only).
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, sys.argv[1])
import pose_sim as ps  # noqa: E402

GXO, OUT = sys.argv[2], sys.argv[3]
PARTS = sys.argv[4] if len(sys.argv) > 4 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jeollip_parts.json')
MIRROR = np.array([[-1, 0, 0], [0, 0, 1], [0, -1, 0]], float)   # AoP gr2_addbones MAPS['mirror']: GXO -> engine
_, meshes = ps.parse_model(GXO)
V0 = np.array(meshes[0]['v'], float)

# ---- frame of the vanilla brim: plane fit of the outer brim vertices
rad0 = np.hypot(V0[:, 1] - 0.015, V0[:, 2] - 0.0035)
brim = V0[rad0 > 0.085]
C = brim.mean(0)
_, _, vt = np.linalg.svd(brim - C)
UP = vt[2] if vt[2][0] > 0 else -vt[2]                       # crown side = +x in the hat's model space
E1 = np.cross(UP, [0, 0, 1.0]); E1 /= np.linalg.norm(E1)
E2 = np.cross(UP, E1)
O = C - 0.003 * E1 - 0.002 * E2           # measured head centre in this frame (head r 0.045 at the brim, top +0.037)
print('brim centre', O.round(4), 'up', UP.round(3))


def P(r, a, h):
    """local cylindrical (radius, angle, height above the brim plane) -> hat model space"""
    return O + r * (math.cos(a) * E1 + math.sin(a) * E2) + h * UP


def N(nr, a, nh):
    v = nr * (math.cos(a) * E1 + math.sin(a) * E2) + nh * UP
    return v / np.linalg.norm(v)


RC, HC, RB = 0.052, 0.058, 0.115           # crown base radius, crown height, brim radius (clear of the head)
TH = 0.004                                 # brim thickness
verts, tris = [], []                       # verts: (pos, normal, uv)


def vert(p, n, uv):
    verts.append((np.asarray(p, float), np.asarray(n, float), (float(uv[0]), float(uv[1]))))
    return len(verts) - 1


def quad(a, b, c, d):                      # a b c d counter-clockwise seen from the front
    tris.extend([(a, b, c), (a, c, d)])


def polar_uv(cx, cy, rr, a):
    return (cx + rr * math.cos(a), cy + rr * math.sin(a))


SEG = 16
# ---- crown dome: rings from the base (slightly below the brim top) to the apex
RINGS = 5
crown_rows = []
for i in range(RINGS + 1):
    t = i / RINGS
    th = t * math.pi / 2
    r = RC * math.cos(th) ** 0.6
    h = -0.002 + (HC + 0.002) * math.sin(th)
    nr, nh = math.cos(th) * HC, math.sin(th) * RC          # ellipsoid-ish normal
    row = []
    for j in range(SEG + 1):
        a = 2 * math.pi * j / SEG
        uvr = 0.235 * (1 - t)                               # apex at the centre of the crown region
        row.append(vert(P(r, a, h), N(nr, a, nh), polar_uv(0.25, 0.25, uvr, a)))
    crown_rows.append(row)
for i in range(RINGS):
    for j in range(SEG):
        a, b = crown_rows[i][j], crown_rows[i][j + 1]
        c, d = crown_rows[i + 1][j + 1], crown_rows[i + 1][j]
        quad(a, b, c, d)

# ---- brim: top annulus, outer rim, bottom disc
BSEG = 20
def droop(r):
    return -0.007 * max(0.0, (r - RC) / (RB - RC)) ** 2
top_in, top_out, bot_out, rim_t, rim_b = [], [], [], [], []
for j in range(BSEG + 1):
    a = 2 * math.pi * j / BSEG
    top_in.append(vert(P(RC - 0.002, a, droop(RC)), UP, polar_uv(0.75, 0.25, 0.085, a)))
    top_out.append(vert(P(RB, a, droop(RB)), UP, polar_uv(0.75, 0.25, 0.235, a)))
    rim_t.append(vert(P(RB + 0.001, a, droop(RB)), N(1, a, 0), (0.5 + 0.5 * j / BSEG, 0.505)))
    rim_b.append(vert(P(RB + 0.001, a, droop(RB) - TH), N(1, a, 0), (0.5 + 0.5 * j / BSEG, 0.545)))
    bot_out.append(vert(P(RB, a, droop(RB) - TH), -UP, polar_uv(0.25, 0.75, 0.235, a)))
for j in range(BSEG):
    quad(top_in[j], top_out[j], top_out[j + 1], top_in[j + 1])
    quad(rim_t[j], rim_b[j], rim_b[j + 1], rim_t[j + 1])
bc = vert(P(0, 0, -TH - 0.001), -UP, (0.25, 0.75))
for j in range(BSEG):
    tris.append((bc, bot_out[j + 1], bot_out[j]))

# ---- jeongja: a short brass cylinder + cap on the apex
KS, KR, KH = 8, 0.0075, 0.009
k_lo, k_hi = [], []
for j in range(KS + 1):
    a = 2 * math.pi * j / KS
    k_lo.append(vert(P(KR, a, HC - 0.002), N(1, a, 0.2), (0.52 + 0.08 * j / KS, 0.93)))
    k_hi.append(vert(P(KR * 0.8, a, HC + KH), N(1, a, 0.6), (0.52 + 0.08 * j / KS, 0.97)))
for j in range(KS):
    quad(k_lo[j], k_lo[j + 1], k_hi[j + 1], k_hi[j])
kc = vert(P(0, 0, HC + KH + 0.002), UP, (0.66, 0.95))
for j in range(KS):
    tris.append((k_hi[j], k_hi[j + 1], kc))

# ---- sangmo: red horsehair spreading from under the knob over the upper crown; two layers, uneven tips
def dome_h(r):
    r = min(r, RC * 0.999)
    th = math.acos((r / RC) ** (1 / 0.6))
    return -0.002 + (HC + 0.002) * math.sin(th)


TS = 16
rng = np.random.default_rng(7)
for layer, (lift, reach, half) in enumerate(((0.0030, 1.0, 0.34), (0.0060, 0.97, 0.28))):
    for s in range(TS):
        a = 2 * math.pi * (s + 0.5 * layer + 0.15 * rng.standard_normal()) / TS
        rt = RC * reach * (0.93 + 0.07 * rng.random())          # tip radius (lower = longer down the crown)
        rm = 0.62 * rt
        w_root, w_mid = half * 0.35, half                       # angular half-widths: bundle spreads, then tapers
        r0 = KR * 0.85
        h0 = HC + 0.002 + lift * 0.5                             # under the knob top: the brass shows
        v_root = [vert(P(r0, a + d, h0), N(0.2, a, 1), (0.5 + 0.25 * (1 + d / w_root), 0.60)) for d in (-w_root, w_root)]
        v_mid = [vert(P(rm, a + d, dome_h(rm) + lift + 0.004), N(0.7, a, 1), (0.5 + 0.25 * (1 + d / w_mid), 0.75))
                 for d in (-w_mid, w_mid)]
        v_tip = vert(P(rt, a, dome_h(rt) + lift * 0.7), N(1, a, 0.6), (0.75, 0.90))
        quad(v_root[0], v_mid[0], v_mid[1], v_root[1])
        tris.append((v_mid[0], v_tip, v_mid[1]))

pos = np.array([v[0] for v in verts])
nrm = np.array([v[1] for v in verts])
uv = np.array([v[2] for v in verts])
T = np.array(tris)
T = T[np.linalg.norm(np.cross(pos[T[:, 1]] - pos[T[:, 0]], pos[T[:, 2]] - pos[T[:, 0]]), axis=1) > 1e-10]   # apex ring
# winding: make every face normal agree with its vertex normals (outward)
fn = np.cross(pos[T[:, 1]] - pos[T[:, 0]], pos[T[:, 2]] - pos[T[:, 0]])
flip = (fn * nrm[T].mean(1)).sum(1) < 0
T[flip] = T[flip][:, [0, 2, 1]]
print('verts %d tris %d (flipped %d)' % (len(pos), len(T), flip.sum()))

# ---- obj preview (v flipped back to OBJ convention: our uv is image space, top = 0)
with open(os.path.join(OUT, 'jeollip.obj'), 'w') as f:
    f.write('o jeollip\n')
    for p in pos:
        f.write('v %.6f %.6f %.6f\n' % tuple(p))
    for t in uv:
        f.write('vt %.6f %.6f\n' % (t[0], 1 - t[1]))
    for n in nrm:
        f.write('vn %.5f %.5f %.5f\n' % tuple(n))
    for a, b, c in T + 1:
        f.write('f %d/%d/%d %d/%d/%d %d/%d/%d\n' % (a, a, a, b, b, b, c, c, c))

# ---- the parts file: engine frame, winding reversed by the mirror, Blender UVs (v up)
P6 = [(2.54 * MIRROR @ p.round(6)).round(6).tolist() for p in pos]
N5 = [(MIRROR @ n.round(5)).round(5).tolist() for n in nrm]
doc = {'_doc': ['Korean jeollip (Jochong hat) geometry, the frozen output of jeollip_model.py: one part in the',
                'raw engine frame of the vanilla bandido hat (engine = 2.54 * mirror(GXO), winding outward), UVs in the',
                'Blender convention (v up) as multimaterial_gr2.replace expects. tools/korean_infantry_model.py builds',
                'art/units/korean_jochong/korean_jochong_hat.gr2 from it on the vanilla bandido_hat.gr2 skeleton.'],
       'material': {'runtime_name': 'matA', 'resource_class': 'own'},
       'bone': 'outlaw_shotgun_hat',                      # the bone the vanilla hat mesh is bound to
       'vertices': [{'p': p, 'n': n, 'uv': [round(float(t[0]), 6), round(1.0 - float(t[1]), 6)]} for p, n, t in zip(P6, N5, uv)],
       'faces': [[int(a), int(c), int(b)] for a, b, c in T]}
open(PARTS, 'w', newline='\n').write(json.dumps(doc, separators=(',', ':')) + '\n')
print('wrote', PARTS)

# ---- textures (512): felt, horsehair, brass; Normals (DirectX) from height; Masks R=AO G=rough B=metal
S = 512
yy, xx = np.mgrid[0:S, 0:S] / S
noise = ndimage.gaussian_filter(rng.random((S, S)), 1.2)
noise = (noise - noise.mean()) / noise.std()
coarse = ndimage.gaussian_filter(rng.random((S, S)), 6)
coarse = (coarse - coarse.mean()) / coarse.std()
col = np.zeros((S, S, 3))
hgt = 0.12 * noise + 0.5 * coarse                 # felt: soft, no specks
rough = np.full((S, S), 0.92)
metal = np.zeros((S, S))
ao = np.ones((S, S))
felt = np.array([30, 28, 30]) / 255
col[:] = felt * (1 + 0.05 * noise[..., None] + 0.06 * coarse[..., None])
# crown: darker toward the base (where it meets the brim), sheen toward the apex
rc_ = np.hypot(xx - 0.25, yy - 0.25)
crown = (xx < 0.5) & (yy < 0.5)
ao[crown] *= np.clip(0.78 + 0.22 * (1 - rc_[crown] / 0.235), 0.7, 1)
# brim top: darker next to the crown
rb_ = np.hypot(xx - 0.75, yy - 0.25)
btop = (xx >= 0.5) & (yy < 0.5)
ao[btop] *= np.clip(0.72 + 0.28 * (rb_[btop] - 0.085) / 0.05, 0.72, 1)
bbot = (xx < 0.5) & (yy >= 0.5)
ao[bbot] *= 0.8
# horsehair strip
hair = (xx >= 0.5) & (yy >= 0.585) & (yy < 0.915)
strands = ndimage.gaussian_filter1d(rng.random(S), 0.8)[None, :].repeat(S, 0)
strands = (strands - strands.mean()) / strands.std()
along = np.clip((yy - 0.60) / 0.30, 0, 1)
red = np.array([168, 30, 28]) / 255
col[hair] = red * np.clip(1 + 0.22 * strands[hair] - 0.25 * (1 - along[hair]) ** 3, 0.4, 1.4)[..., None]
hgt[hair] = 1.2 * strands[hair]
rough[hair] = 0.78
ao[hair] *= np.clip(0.6 + 0.4 * along[hair], 0.6, 1)
# brass knob
knob = (xx >= 0.5) & (xx < 0.7) & (yy >= 0.915)
col[knob] = np.array([186, 146, 66]) / 255 * (1 + 0.08 * noise[knob])[..., None]
hgt[knob] = 0.2 * noise[knob]
rough[knob] = 0.45
metal[knob] = 1.0
# normals from height (DirectX: green = -dh/dy in image space)
gy, gx = np.gradient(ndimage.gaussian_filter(hgt, 0.6) * 0.9)
nn = np.dstack([-gx, -gy, np.ones_like(gx)])
nn /= np.linalg.norm(nn, axis=-1, keepdims=True)
save = lambda a, n: Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)).save(
    os.path.join(OUT, 'jeollip_%s.png' % n))
save(np.clip(col, 0, 1), 'BaseColor')
save(nn * 0.5 + 0.5, 'Normals')
save(np.dstack([ao, rough, metal]), 'Masks')
print('textures written')
