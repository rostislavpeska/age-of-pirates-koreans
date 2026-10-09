"""Texture-space maps of a model from its triangles (dump_uv3d.py output):
per texel the 3D rest position, normal, mesh and triangle. Saved as texmap.npz next to this file."""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
N = 1024


def build(tris):
    pos = np.full((N, N, 3), np.nan, np.float32)
    nrm = np.zeros((N, N, 3), np.float32)
    obj = np.full((N, N), -1, np.int16)
    tid = np.full((N, N), -1, np.int32)
    names = sorted({t['o'] for t in tris})
    for k, t in enumerate(tris):
        uv = np.array(t['uv'], np.float64) % 1.0 if False else np.array(t['uv'], np.float64)
        px = uv[:, 0] * N - 0.5
        py = (1.0 - uv[:, 1]) * N - 0.5
        x0, x1 = int(np.floor(px.min())), int(np.ceil(px.max()))
        y0, y1 = int(np.floor(py.min())), int(np.ceil(py.max()))
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, N - 1), min(y1, N - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        (ax, bx, cx), (ay, by, cy) = px, py
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -0.02) & (w1 >= -0.02) & (w2 >= -0.02)    # small dilation against seams
        if not inside.any():
            continue
        p = np.array(t['p'], np.float64)
        P = w0[..., None] * p[0] + w1[..., None] * p[1] + w2[..., None] * p[2]
        yy, xx = ys[inside], xs[inside]
        pos[yy, xx] = P[inside]
        nrm[yy, xx] = t['n']
        obj[yy, xx] = names.index(t['o'])
        tid[yy, xx] = k
    return pos, nrm, obj, tid, names


if __name__ == '__main__':
    # python texmap.py <tris.json> <work dir>  ->  <work dir>/texmap.npz and islands.npy (texture-space maps + islands)
    from scipy import ndimage
    tris = json.load(open(sys.argv[1]))
    pos, nrm, obj, tid, names = build(tris)
    np.savez_compressed(os.path.join(sys.argv[2], 'texmap.npz'), pos=pos, nrm=nrm, obj=obj, tid=tid, names=np.array(names))
    np.save(os.path.join(sys.argv[2], 'islands.npy'), ndimage.label(~np.isnan(pos[..., 0]))[0])
    print('coverage %.1f%%' % (100 * (~np.isnan(pos[..., 0])).mean()))
