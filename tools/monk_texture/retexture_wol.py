"""Korean monk on the Shaolin Disciple, after the WoL Jeobju: light grey-white hanbok cloth, dark charcoal collar band
and belt, mid-grey trousers, white leg wraps and socks, a red tie cord with teal beads at the collar crossing.
Fabric = fold shading (low frequency) + weave (high frequency) re-graded separately; cool shadows, warm highlights.
    python retexture_wol.py <dret dir>"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

D = sys.argv[1]
src = np.array(Image.open(os.path.join(D, 'base.png')).convert('RGBA')).astype(float)
rgb, alpha = src[..., :3] / 255, src[..., 3]
d = np.load(os.path.join(D, 'texmap.npz'))
pos, cov = d['pos'] * 1000, ~np.isnan(d['pos'][..., 0])
lab = np.load(os.path.join(D, 'islands.npy'))
Z = pos[..., 2]
lum = rgb @ np.array([0.299, 0.587, 0.114])
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
out = rgb.copy()
isl = lambda *ids: np.isin(lab, ids)

# luminance split: folds (sigma 5) and weave (what remains above sigma 1.2)
low = ndimage.gaussian_filter(lum, 5)
mid = ndimage.gaussian_filter(lum, 1.2)
weave = mid - low
COOL, WARM = np.array([0.92, 0.95, 1.00]), np.array([1.00, 0.99, 0.95])


def cloth(mask, target, fold=1.0, weave_k=0.45, grade=True):
    """target mean colour; fold shading and weave re-scaled; shadows cool, highlights warm."""
    if not mask.any():
        return
    t = np.array(target, float) / 255
    tl = t @ np.array([0.299, 0.587, 0.114])
    lo = low[mask] - low[mask].mean()
    span = max(np.percentile(np.abs(lo), 95), 1e-3)
    shade = np.clip(lo / span, -1, 1) * 0.15 * fold            # folds: +-15%: matte cloth
    L = tl * (1 + shade) + weave_k * weave[mask] * tl / max(low[mask].mean(), 0.05)
    c = t[None, :] * (L / tl)[:, None]
    if grade:
        w = np.clip(shade / 0.15 * 0.5 + 0.5, 0, 1)[:, None]   # 0 = deepest fold, 1 = brightest
        c = c * (COOL[None, :] * (1 - w) + WARM[None, :] * w)
    out[mask] = np.clip(c, 0, 1)


brown = (hue < 40) & (sat > 0.18)
skin = isl(4, 5, 10) & (lum > 0.45) & (sat > 0.2)
white = (lum > 0.55) & (sat < 0.18)
dark = (lum < 0.22)

cloth(isl(1, 2, 3, 12) & brown & ~skin, (210, 209, 205), weave_k=0.25)   # sleeves: whitest
cloth(isl(9, 13) & brown, (192, 192, 189), weave_k=0.25)            # jacket/robe body
cloth(isl(8, 11) & brown, (124, 124, 126), fold=1.3, weave_k=0.35)  # trousers: mid grey (WoL)
# collar band + sash carry the PLAYER COLOUR (vanilla Details.R): keep them light so the team colour shows
cloth((isl(9) | isl(5)) & white, (238, 236, 232), fold=1.2, weave_k=0.15, grade=False)
legs = isl(6, 7)
lz = Z[legs]
shoe = legs & dark & (Z < 0.42)                                      # the 94%-dark feet band
cloth(shoe, (206, 204, 199), weave_k=0.2)                            # white-grey socks/shoes (beoseon)
cloth(legs & white, (226, 224, 218), weave_k=0.3)                    # leg wraps stay white
cloth(legs & (lum >= 0.22) & ~white & ~shoe & (sat < 0.2), (150, 150, 152), weave_k=0.3)   # grey under-wraps
cloth(legs & dark & ~shoe, (118, 116, 113), fold=0.6, weave_k=0.1, grade=False)            # tie cords: soft grey

# the red tie cord (goreum) with teal beads at the collar crossing, drawn at 4x and scaled down
S = 4
x0, y0, x1, y1 = 300, 560, 450, 745
W, H = (x1 - x0) * S, (y1 - y0) * S
layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
shadow = Image.new('L', (W, H), 0)
dl, ds = ImageDraw.Draw(layer), ImageDraw.Draw(shadow)
P = lambda x, y: ((x - x0) * S, (y - y0) * S)
knot = (352, 600)
strands = [[(352, 600), (358, 622), (364, 645), (369, 668), (372, 691), (374, 714)],
           [(352, 600), (345, 624), (342, 648), (343, 671), (347, 694)]]
for s in strands:
    ds.line([P(x + 2, y + 2) for x, y in s], fill=150, width=7 * S, joint='curve')
for s in strands:
    pts = [P(x, y) for x, y in s]
    dl.line(pts, fill=(95, 14, 18, 255), width=7 * S, joint='curve')           # outline
    dl.line(pts, fill=(176, 28, 34, 255), width=5 * S, joint='curve')          # cord
    dl.line([(px - 1 * S, py) for px, py in pts], fill=(226, 92, 88, 255), width=1 * S)   # highlight
kx, ky = P(*knot)
ds.ellipse([kx - 8 * S + 2 * S, ky - 6 * S + 2 * S, kx + 8 * S + 2 * S, ky + 6 * S + 2 * S], fill=150)
dl.ellipse([kx - 8 * S, ky - 6 * S, kx + 8 * S, ky + 6 * S], fill=(95, 14, 18, 255))
dl.ellipse([kx - 6 * S, ky - 4 * S, kx + 6 * S, ky + 4 * S], fill=(176, 28, 34, 255))
dl.arc([kx - 5 * S, ky - 3 * S, kx + 3 * S, ky + 2 * S], 190, 300, fill=(226, 92, 88, 255), width=S)
for s, picks in ((strands[0], (1, 3, 5)), (strands[1], (2, 4))):
    for i in picks:
        bx, by = P(*s[i])
        rr = 3.4 * S
        ds.ellipse([bx - rr + 2 * S, by - rr + 2 * S, bx + rr + 2 * S, by + rr + 2 * S], fill=170)
        dl.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=(18, 92, 88, 255))
        dl.ellipse([bx - rr + S, by - rr + S, bx + rr - S, by + rr - S], fill=(44, 170, 158, 255))
        dl.ellipse([bx - 1.6 * S, by - 2.2 * S, bx - 0.2 * S, by - 0.8 * S], fill=(190, 245, 236, 255))
layer = layer.resize((x1 - x0, y1 - y0), Image.LANCZOS)
shadow = shadow.filter(ImageFilter.GaussianBlur(3 * S)).resize((x1 - x0, y1 - y0), Image.LANCZOS)
la = np.array(layer).astype(float) / 255
sh = np.array(shadow).astype(float) / 255 * 0.45
reg = out[y0:y1, x0:x1]
reg *= (1 - sh)[..., None]
reg[:] = reg * (1 - la[..., 3:4]) + la[..., :3] * la[..., 3:4]

cord = np.zeros(rgb.shape[:2]); cord[y0:y1, x0:x1] = np.maximum(la[..., 3], sh / 0.45 * 0.6)
idx = ndimage.distance_transform_edt(~cov, return_distances=False, return_indices=True)
out[~cov] = out[idx[0][~cov], idx[1][~cov]]
res = np.dstack([np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8), alpha.astype(np.uint8)])
Image.fromarray(res).save(os.path.join(D, 'korean_disciple_wol.png'))

# Details: vanilla player-colour weight, cleared under the cord so it stays red in every team colour
det = np.array(Image.open(os.path.join(D, 'van_Details.png')).convert('RGB')).astype(float)
det[..., 0] *= np.clip(1 - ndimage.gaussian_filter(cord, 1.0) * 1.3, 0, 1)
Image.fromarray(np.clip(det + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(D, 'korean_disciple_wol_Details.png'))

# Normals (DirectX, linear): soften the coarse weave on the cloth, keep folds, skin, wraps and seams untouched
nm = np.array(Image.open(os.path.join(D, 'van_Normals.png')).convert('RGB')).astype(float) / 255 * 2 - 1
clothm = isl(1, 2, 3, 8, 9, 11, 12, 13) & ~skin
soft = np.stack([ndimage.gaussian_filter(nm[..., k], 1.3) for k in range(2)], -1)
k = ndimage.gaussian_filter(clothm.astype(float), 1.5)[..., None]
xy = nm[..., :2] * (1 - k) + soft * k
z = np.sqrt(np.clip(1 - (xy ** 2).sum(-1), 0, 1))
nn = np.dstack([xy, z])
Image.fromarray(np.clip((nn + 1) / 2 * 255 + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(D, 'korean_disciple_wol_Normals.png'))
print('wrote Details and Normals; cord cleared texels', int((cord > 0.05).sum()))
print('wrote korean_disciple_wol.png; shoes px', int(shoe.sum()))
