"""Gakgung Archer: Joseon retexture of one vanilla Chinese Changdao age (0/1/2), colours only, following the model's
own garments; the same palette and rules as retexture_jochong.py and retexture_jangchang.py (owner 2026-10-09; the
Changdao body chosen for the archer in the history check: Ming-style coats and conical helmets fit Joseon).
  age 0 (base)       : coat in player colour, the Ming cloud-collar trims as black edging, the round chest mirror
                       painted out (fabric, Normals and Masks follow the coat), white sleeves and baji, indigo leg wraps;
                       the steel helmet with mail hood kept
  age 1 (Disciplined): + the red plume (kept); the red armour lacing as an indigo jeondae; brass skirt studs
  age 2 (Honored)    : the armour kept (cuirass, lamellar bracers and skirt), skirt studs brass; the card of the gold
                       Ming phoenix-wing ornament above the helmet carries a jangmok instead (owner 2026-10-09: "replace
                       the symbol with something genuinely Korean"): a bundle of barred pheasant tail feathers on a red
                       tuft, as on Joseon helmets and command-flag poles - cut out by the BaseColor alpha (DXT5)
    python retexture_gakgung.py DIR AGE
DIR holds the vanilla maps decoded to ageN_{BaseColor,Details,Normals,Masks}.png and texmap.py's ageN_texmap.npz;
writes DIR/gakgung_ageN_{BaseColor,Details,Normals,Masks}.png (BaseColor with its alpha: DXT5) and _blue/_red previews."""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

D, AGE = sys.argv[1], int(sys.argv[2])
WHITE = (214, 209, 194)
BAJI = (220, 216, 204)
INDIGO = (54, 60, 86)
EDGE = (36, 36, 42)
BRASS = (184, 146, 70)

ld = lambda n: np.asarray(Image.open(os.path.join(D, 'age%d_%s.png' % (AGE, n))).convert('RGBA'), np.float64) / 255
base, det, nrm, msk = ld('BaseColor'), ld('Details'), ld('Normals'), ld('Masks')
tm = np.load(os.path.join(D, 'age%d_texmap.npz' % AGE))
pos, part, isl = tm['pos'], tm['part'], tm['island']
cov = ~np.isnan(pos[..., 0])
Z = np.where(cov, pos[..., 2], np.nan)
rgb = base[..., :3].copy()
alpha = base[..., 3].copy()


def colour_stats(img):
    lum = img @ np.array([0.299, 0.587, 0.114])
    mx, mn = img.max(-1), img.min(-1)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
    return lum, sat, hue


lum, sat, hue = colour_stats(rgb)
pcw = det[..., 0]


def islands_where(test, minimum=2000):
    ids = []
    for i in range(1, isl.max() + 1):
        m = isl == i
        n = m.sum()
        if n < minimum:
            continue
        cnt = np.bincount(part[m], minlength=8) / n
        if test(cnt, pcw[m].mean(), n, np.nanmin(Z[m]), np.nanmax(Z[m])):
            ids.append(i)
    return np.isin(isl, ids)


torso = islands_where(lambda c, pc, n, z0, z1: c[7] > 0.8 and n > 100000)
skirt = islands_where(lambda c, pc, n, z0, z1: c[5] + c[6] > 0.9 and n > 100000 and z1 < 0.42)
coat = torso | skirt
arms = islands_where(lambda c, pc, n, z0, z1: c[3] > 0.8)
legs = islands_where(lambda c, pc, n, z0, z1: c[4] + c[5] + c[6] > 0.9 and z0 < 0.02)
ornament = islands_where(lambda c, pc, n, z0, z1: c[1] > 0.95 and z0 > 0.9, minimum=500)
skin = ((hue < 45) | (hue > 340)) & (sat > 0.22) & (lum > 0.3)
hand = (part == 2) | skin
light = (lum > 0.45) & (sat < 0.25) & (pcw < 0.5)

# 1. the round chest mirror: the neutral grey disc on the coat top (the trims are beige) - paint it out
grey = torso & (pcw < 0.5) & (sat < 0.1) & (lum > 0.4) & (lum < 0.85)
lab, n = ndimage.label(ndimage.binary_opening(grey, iterations=2))
sizes = np.bincount(lab.ravel())
mirror = np.zeros_like(torso)
cand = [k for k in range(1, n + 1) if 800 < sizes[k] < 9000]
if cand:
    k = max(cand, key=lambda c: sizes[c])
    mirror = ndimage.binary_dilation(lab == k, iterations=3) & torso & (pcw < 0.5)
if mirror.any():
    # fill with real coat fabric (folds included) copied from just below the disc, then feather the border
    ys, xs = np.nonzero(mirror)
    dy = int(ys.max() - ys.min()) + 8
    if AGE == 2:                                   # on the iron cuirass: fill with the cuirass, no player colour
        fabric = torso & (pcw < 0.5) & (lum < 0.4) & ~mirror
    else:
        fabric = torso & (pcw >= 0.5)
    src_y = np.clip(ys + dy, 0, mirror.shape[0] - 1)
    ok = fabric[src_y, xs]
    near = ndimage.distance_transform_edt(~fabric, return_distances=False, return_indices=True)
    sy = np.where(ok, src_y, near[0][ys, xs])
    sx = np.where(ok, xs, near[1][ys, xs])
    for arr in (rgb, det, nrm, msk):
        arr[ys, xs] = arr[sy, sx]
    ring = ndimage.binary_dilation(mirror, iterations=3) & ~ndimage.binary_erosion(mirror, iterations=3) & torso
    for arr in (rgb, nrm, msk):
        blur = np.stack([ndimage.gaussian_filter(arr[..., c], 1.5) for c in range(arr.shape[-1])], -1)
        arr[ring] = blur[ring]
    det[mirror, 0] = 0.0 if AGE == 2 else 1.0
    pcw = det[..., 0]
    lum, sat, hue = colour_stats(rgb)
    light = (lum > 0.45) & (sat < 0.25) & (pcw < 0.5)

out = rgb.copy()


def recolor(mask, target, contrast=1.0):
    if not mask.any():
        return
    t = np.array(target, float) / 255
    tl = t @ np.array([0.299, 0.587, 0.114])
    m = lum[mask].mean()
    lp = np.clip(tl + contrast * (lum[mask] - m) * (tl / max(m, 0.05)) ** 0.5, 0.02, 0.98)
    out[mask] = np.clip(t[None, :] * (lp / tl)[:, None], 0, 1)


pc_out = pcw.copy()
red = ((hue < 15) | (hue > 340)) & (sat > 0.45) & (lum > 0.12) & (pcw < 0.5)
lab, n = ndimage.label(skirt & light)                         # the studded skirt (ages 1 and 2): brass studs
sizes = np.bincount(lab.ravel())
studs = np.isin(lab, [i for i in range(1, n + 1) if 30 < sizes[i] < 900]) if AGE > 0 else np.zeros_like(coat)
recolor(studs, BRASS, 0.9)
if AGE == 2:
    edging = torso & light                                    # the armour itself (dark cuirass, lamellae) stays
else:
    edging = coat & light & ~studs
recolor(edging & ~studs, EDGE, 0.7)
pc_out[edging | studs] = 0
jeondae = coat & red
recolor(jeondae, INDIGO, 0.6)
pc_out[jeondae] = 0
if AGE < 2:                                                   # sleeves (the age 2 bracers stay armour)
    arm_light = arms & light & ~hand
    sleeve = arms & (pcw < 0.5) & ~hand & ~arm_light
    recolor(sleeve, WHITE, 0.45)
    recolor(arm_light, EDGE, 0.7)
    pc_out[arm_light] = 0
leg = legs & cov & ~hand & (pcw < 0.5) & (part != 1) & (Z < 0.5) & ~light & (Z > 0.07)
knee = 0.2
recolor(leg & (Z >= knee), BAJI, 0.5)
recolor(leg & (Z < knee), INDIGO, 0.5)
if AGE == 2:
    # the Ming ornament card -> a jangmok: its island plus the rim texels the rasterised island misses (never another
    # island's), up = image up (z 1.06 at the top row, 0.93 at the bottom); five barred pheasant tail feathers fan out
    # from a red tuft at the bottom centre, everything else on the card cut out
    ids = [int(i) for i in np.unique(isl[ornament]) if i]
    card = ndimage.binary_dilation(ornament, iterations=8) & np.isin(isl, [0] + ids)
    ys, xs = np.nonzero(ornament)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    W, Hc = x1 - x0, y1 - y0
    bx, by = (x0 + x1) / 2.0, y1 - 0.04 * Hc                          # base of the bundle
    gy, gx = np.mgrid[0:alpha.shape[0], 0:alpha.shape[1]].astype(float)
    feather = np.zeros(alpha.shape, bool)
    shade = np.ones(alpha.shape)
    bars = np.zeros(alpha.shape, bool)
    shaft = np.zeros(alpha.shape, bool)
    for ang, length in ((-26, 0.82), (-13, 0.92), (0, 0.98), (13, 0.92), (26, 0.82)):
        t = np.radians(ang)
        ux, uy = np.sin(t), -np.cos(t)                                # along the feather (image up = -y)
        dx, dy = gx - bx, gy - by
        s = (dx * ux + dy * uy) / (length * Hc)                       # 0 at the base, 1 at the tip
        d = dx * uy - dy * ux                                         # across
        half = W * 0.055 * np.clip(np.sin(np.clip(s, 0, 1) * np.pi) ** 0.6 + 0.25 * (s < 0.5), 0, 1.2)
        inside = (s > 0) & (s < 1) & (np.abs(d) < half)
        feather |= inside
        bars |= inside & (np.sin(s * 2 * np.pi * 9) > 0.55)           # the dark cross bars of a pheasant tail
        shaft |= inside & (np.abs(d) < 0.9)
        shade[inside] = np.minimum(shade[inside], 0.8 + 0.2 * (1 - np.abs(d[inside]) / np.maximum(half[inside], 1e-3)))
    tuft = np.hypot(gx - bx, (gy - by) * 1.3) < W * 0.075
    shape = (feather | tuft) & card
    buff, bar, quill, red = (np.array(c, float) / 255 for c in ((196, 158, 98), (62, 42, 26), (226, 214, 186), (168, 30, 28)))
    col = np.where(bars[..., None], bar, buff) * shade[..., None]
    col = np.where(shaft[..., None], quill, col)
    col = np.where(tuft[..., None], red * (0.8 + 0.2 * shade[..., None]), col)
    out[card] = col[card]
    near = ndimage.distance_transform_edt(~shape, return_distances=False, return_indices=True)
    rim = card & ~shape                                               # cut-out texels keep the feather colour (no
    out[rim] = out[near[0][rim], near[1][rim]]                        # dark fringe in the smaller mips)
    alpha[card] = np.where(shape[card], 1.0, 0.0)
    pc_out[card] = 0
    hgt = ndimage.gaussian_filter(np.where(shape, 1.0 + 0.6 * shaft - 0.3 * bars, 0.0), 1.0)
    ny, nx = np.gradient(hgt)
    nb = np.dstack([-nx, -ny, np.ones_like(nx)])
    nb /= np.linalg.norm(nb, axis=-1, keepdims=True)
    nrm[card, :3] = nb[card] * 0.5 + 0.5
    msk[card, 0] = np.where(tuft[card], 0.75, 0.95)                   # AO: darker in the tuft
    msk[card, 1] = 0.82                                               # matte feathers
    msk[card, 2] = 0.0

idx = ndimage.distance_transform_edt(~cov, return_distances=False, return_indices=True)
out[~cov] = out[idx[0][~cov], idx[1][~cov]]
pc_out[~cov] = pc_out[idx[0][~cov], idx[1][~cov]]
det_out = det.copy()
det_out[..., 0] = pc_out
save = lambda a, name: Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)).save(
    os.path.join(D, 'gakgung_age%d_%s.png' % (AGE, name)))
save(np.dstack([out, alpha]), 'BaseColor')
save(det_out, 'Details')
save(nrm, 'Normals')
save(msk, 'Masks')
for nm, pc in (('blue', (0.18, 0.36, 0.9)), ('red', (0.86, 0.16, 0.16))):
    save(np.dstack([out * (1 - pc_out[..., None] + pc_out[..., None] * np.array(pc)), alpha]), nm)
print('age', AGE, 'torso %d skirt %d arms %d legs %d mirror %d edging %d jeondae %d studs %d ornament %d' % (
    torso.sum(), skirt.sum(), arms.sum(), legs.sum(), mirror.sum(), edging.sum(), jeondae.sum(), studs.sum(),
    ornament.sum()))
