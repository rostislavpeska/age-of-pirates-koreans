"""UV texel -> rest-pose 3D position, normal and body part, rasterised from a converter GXO, plus UV islands.
    python texmap.py POSE_SIM_DIR MODEL.gxo BASECOLOR.png OUT_PREFIX
Writes OUT_PREFIX_texmap.npz (pos HxWx3 NaN outside, nrm, part, island) and OUT_PREFIX_islands.png (labelled)."""
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, sys.argv[1])
import pose_sim as ps  # noqa: E402

GROUPS = [('head', ('head', 'neck')), ('hand', ('hand', 'finger', 'prop')), ('arm', ('upperarm', 'forearm', 'clavicle')),
          ('foot', ('foot', 'toe')), ('calf', ('calf',)), ('thigh', ('thigh',)), ('torso', ('spine', 'pelvis', 'bip01'))]


def group_of(name):
    n = ps.norm(name).lower()
    for i, (_, keys) in enumerate(GROUPS, 1):
        if any(k in n for k in keys):
            return i
    return 7


def main():
    model, basep, out = sys.argv[2], sys.argv[3], sys.argv[4]
    base = Image.open(basep).convert('RGB')
    size = base.size[0]
    _, meshes = ps.parse_model(model)
    pos = np.full((size, size, 3), np.nan, np.float32)
    nrm = np.zeros((size, size, 3), np.float32)
    part = np.zeros((size, size), np.uint8)
    for m in meshes:
        if not m['vt']:
            continue
        vg = []
        for w in m['vw']:
            k = int(np.argmax(w[:4]))
            vg.append(group_of(m['mb'][int(w[4 + k]) - 1]))
        if not vg:                                   # rigid prop (hat): one group
            vg = [1] * len(m['v'])
        V = np.array(m['v'], np.float64)
        T = np.array(m['vt'], np.float64)
        for f in m['f']:
            ids = [i - 1 for i in f]
            gs = [vg[i] for i in ids]
            g = max(set(gs), key=gs.count)
            uv = T[ids] * size
            uv[:, 1] = size - uv[:, 1]
            x0, y0 = np.floor(uv.min(0)).astype(int) - 1
            x1, y1 = np.ceil(uv.max(0)).astype(int) + 1
            x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, size - 1), min(y1, size - 1)
            if x1 < x0 or y1 < y0:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, ay), (bx, by), (cx, cy) = uv
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-12:
                continue
            l1 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
            l2 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
            p = l1[..., None] * V[ids[0]] + l2[..., None] * V[ids[1]] + l3[..., None] * V[ids[2]]
            n = np.cross(V[ids[1]] - V[ids[0]], V[ids[2]] - V[ids[0]])
            n = n / (np.linalg.norm(n) + 1e-12)
            sl = (slice(y0, y1 + 1), slice(x0, x1 + 1))
            pos[sl][inside] = p[inside]
            nrm[sl][inside] = n
            part[sl][inside] = g
    cov = ~np.isnan(pos[..., 0])
    isl, n = ndimage.label(ndimage.binary_closing(cov, iterations=1) | cov)
    np.savez_compressed(out + '_texmap.npz', pos=pos, nrm=nrm, part=part, island=isl)
    im = Image.blend(base, Image.fromarray(((isl * 47) % 255).astype(np.uint8)).convert('RGB'), 0.25)
    d = ImageDraw.Draw(im)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(isl == i)
        if len(xs) < 150:
            continue
        z = pos[ys, xs, 2]
        d.text((int(np.median(xs)), int(np.median(ys))), '%d z%.2f-%.2f' % (i, np.nanmin(z), np.nanmax(z)),
               fill=(255, 0, 0))
    im.save(out + '_islands.png')
    print(out, 'islands', n, 'covered', int(cov.sum()))


if __name__ == '__main__':
    main()
