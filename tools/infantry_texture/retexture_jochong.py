"""Jochong Musketeer: Joseon retexture of one vanilla Chinese Arquebusier age, colours only, following the model's own
garments (owner 2026-10-09: "full retextures", "if [a] more advanced model basically doesn't fit the history, resolve
the upgrade only by reskin", "for belts etc - edit also normals and masks maps"). Islands, body parts and texel heights
come from texmap.py; vanilla shading is kept (luminance remap).
  age 1 (base)       : jeonbok vest = player colour, white hemp sleeves, white baji, indigo haengjeon leg wraps
  age 2 (Disciplined): + white beoseon socks, cream ties on the wraps, darker leather bandoliers, indigo jeondae belt
  age 3 (Honored)    : red dongdari sleeves, black jeondae; the painted Chinese breast mirror is erased along the
                       slant of the front placket (the coat halves and the placket run on through it) - texture only,
                       the model has no disc geometry
  the jeondae is a real band: a height profile (bevelled edges, two creases) -> Normals (DirectX), Masks (AO at the
  edges, contact shadow, silk roughness); never red (a red belt vanishes on a red player)
    python retexture_jochong.py DIR AGE
DIR holds the vanilla maps decoded to ageN_{BaseColor,Details,Normals,Masks}.png and texmap.py's ageN_texmap.npz;
writes DIR/jochong_ageN_{BaseColor,Details,Normals,Masks}.png and _blue/_red previews (player colour multiplied)."""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

D, AGE = sys.argv[1], int(sys.argv[2])
WHITE = (226, 221, 207)            # hemp
BAJI = (220, 216, 204)
INDIGO = (54, 60, 86)
CREAM = (206, 196, 168)
LEATHER = (74, 52, 36)
CRIMSON = (148, 34, 32)
NAVY = (38, 44, 74)
SLEEVE = {1: WHITE, 2: WHITE, 3: CRIMSON}[AGE]
BELT = {1: None, 2: INDIGO, 3: (34, 34, 40)}[AGE]      # never red: a red belt vanishes on a red player

rgba = np.asarray(Image.open(os.path.join(D, 'age%d_BaseColor.png' % AGE)).convert('RGBA'), np.float64)
rgb = rgba[..., :3] / 255
det = np.asarray(Image.open(os.path.join(D, 'age%d_Details.png' % AGE)).convert('RGBA'), np.float64) / 255
nrm = np.asarray(Image.open(os.path.join(D, 'age%d_Normals.png' % AGE)).convert('RGBA'), np.float64) / 255
tm = np.load(os.path.join(D, 'age%d_texmap.npz' % AGE))
pos, part, isl = tm['pos'], tm['part'], tm['island']
cov = ~np.isnan(pos[..., 0])
X, Y, Z = pos[..., 0], pos[..., 1], pos[..., 2]
H, W = rgb.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]

lum = rgb @ np.array([0.299, 0.587, 0.114])
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
msk = np.asarray(Image.open(os.path.join(D, 'age%d_Masks.png' % AGE)).convert('RGBA'), np.float64) / 255


def erase_disc():
    """age 3: fill the breast mirror column by column from the fabric above and below it (folds run vertically)."""
    big = max(range(1, isl.max() + 1), key=lambda i: ((isl == i) & (det[..., 0] > 0.5)).sum())
    coat0 = isl == big
    strap0 = coat0 & (hue > 8) & (hue < 42) & (sat > 0.3) & (lum > 0.08) & (lum < 0.6) & (det[..., 0] < 0.5)
    lab0, n0 = ndimage.label(strap0)
    keep = [i for i, c in enumerate(np.bincount(lab0.ravel())) if i and c > 3000]
    strap0 = ndimage.binary_dilation(np.isin(lab0, keep), iterations=1)   # the real straps only, no specks
    gold0 = coat0 & (hue > 38) & (hue < 62) & (sat > 0.35) & (lum > 0.4)
    cy, cx = yy[gold0].mean(), xx[gold0].mean()
    rr = np.hypot(yy - cy, xx - cx)
    rg = rr[gold0].max()
    fabric = (lum > 0.5) & (sat < 0.15) & ~strap0
    edge = rg
    for rad in np.arange(rg, rg * 1.8, 1.0):                  # disc edge = where fabric takes over the ring
        ring = coat0 & ~strap0 & (np.abs(rr - rad) < 1.0)
        if ring.sum() and fabric[ring].mean() > 0.7:
            edge = rad
            break
    disc = coat0 & (rr <= edge + 6)
    fill = disc & ~strap0
    # the front placket runs on a slant in UV: fit its centre line above and below the disc and fill along that slant,
    # so the placket and the folds beside it continue straight through (column fill broke the junction)
    trim0 = coat0 & (lum > 0.6) & (sat < 0.1) & (det[..., 0] < 0.5) & ~disc
    ys_d = np.nonzero(disc.any(1))[0]
    pts = []
    for y in list(range(ys_d.min() - 60, ys_d.min() - 3)) + list(range(ys_d.max() + 3, ys_d.max() + 50)):
        xs = np.nonzero(trim0[y, int(cx - edge):int(cx + edge)])[0] + int(cx - edge)
        if len(xs) < 8:
            continue
        runs = np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1)
        run = min(runs, key=lambda r: abs(r.mean() - cx))
        if 8 <= len(run) <= 22:
            pts.append((y, run.mean()))
    pts = np.array(pts)
    slope, icpt = np.polyfit(pts[:, 0], pts[:, 1], 1)
    maps = [rgb, det, nrm, msk]
    anchor_ok = coat0 & ~disc & ~ndimage.binary_dilation(strap0, iterations=5) & (lum > 0.42)  # no strap shadows
    for y, x in zip(*np.nonzero(fill)):
        up = dn = None
        for k in range(1, 400):
            yu, xu = y - k, int(round(x - slope * k))
            if yu < 0 or not (0 <= xu < W):
                break
            if anchor_ok[yu, xu]:
                up = (yu, xu, k)
                break
        for k in range(1, 400):
            yd, xd = y + k, int(round(x + slope * k))
            if yd >= H or not (0 <= xd < W):
                break
            if anchor_ok[yd, xd]:
                dn = (yd, xd, k)
                break
        if up is None and dn is None:
            continue
        if up is None or dn is None:
            src = up or dn
            for m in maps:
                m[y, x] = m[src[0], src[1]]
            continue
        w = up[2] / (up[2] + dn[2])
        for m in maps:
            m[y, x] = (1 - w) * m[up[0], up[1]] + w * m[dn[0], dn[1]]
    print('placket line x = %.1f + %.3f y from %d rows' % (icpt, slope, len(pts)))
    return 'disc erased centre (%.0f, %.0f) gold r %.0f edge %.0f, %d texels' % (cx, cy, rg, edge, fill.sum())


disc_info = ''
if AGE == 3:
    disc_info = ' ' + erase_disc()
    lum = rgb @ np.array([0.299, 0.587, 0.114])
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
pcw = det[..., 0]
out = rgb.copy()


def islands_where(test):
    ids = []
    for i in range(1, isl.max() + 1):
        m = isl == i
        n = m.sum()
        if n < 2000:
            continue
        cnt = np.bincount(part[m], minlength=8) / n
        if test(cnt, pcw[m].mean(), n):
            ids.append(i)
    return np.isin(isl, ids)


def recolor(mask, target, contrast=1.0):
    if not mask.any():
        return
    t = np.array(target, float) / 255
    tl = t @ np.array([0.299, 0.587, 0.114])
    m = lum[mask].mean()
    lp = np.clip(tl + contrast * (lum[mask] - m) * (tl / max(m, 0.05)) ** 0.5, 0.02, 0.98)
    out[mask] = np.clip(t[None, :] * (lp / tl)[:, None], 0, 1)


coat = islands_where(lambda c, pc, n: pc > 0.5 and n > 100000)
arms = islands_where(lambda c, pc, n: c[3] > 0.8)
legs = islands_where(lambda c, pc, n: c[4] + c[5] > 0.6)
skin = ((hue < 45) | (hue > 340)) & (sat > 0.22) & (lum > 0.22)
hand = (part == 2) | skin
brown = (hue > 8) & (hue < 42) & (sat > 0.3) & (lum > 0.08) & (lum < 0.6)
whiteish = (lum > 0.55) & (sat < 0.14)
gold = (hue > 38) & (hue < 62) & (sat > 0.35) & (lum > 0.4)

# arms: the coat's short sleeve and the forearm become one sleeve (age 1/2 white hemp, age 3 red dongdari sleeve)
sleeve_pc = arms & (pcw > 0.5)
cuff = arms & ~sleeve_pc & whiteish
fore = arms & ~sleeve_pc & ~cuff & ~hand
ties = fore & brown
recolor(sleeve_pc, SLEEVE, 0.9)
recolor(fore, SLEEVE if AGE == 3 else (214, 209, 194), 0.35)
recolor(cuff, WHITE, 0.8)
pc_out = pcw.copy()
pc_out[arms] = 0

# legs: shoes stay; beoseon socks white; haengjeon wraps indigo below the knee; baji white above
shoe_top = 0.045 if AGE == 1 else 0.018
knee = 0.185
leg = legs & cov & ~hand & ~((Z < 0.07) & (lum < 0.12))      # shoes and soles stay
socks = leg & (Z >= shoe_top) & (Z < 0.085) & (lum > 0.25) if AGE > 1 else np.zeros_like(leg)
wraps = leg & (Z >= shoe_top) & (Z < knee) & ~socks
baji = leg & (Z >= knee)
legties = wraps & brown if AGE > 1 else np.zeros_like(wraps)
recolor(socks, WHITE, 0.7)
recolor(wraps & ~legties, INDIGO, 0.3 if AGE == 1 else 0.6)
recolor(legties, CREAM, 0.8)
recolor(baji, BAJI, 0.5)

# coat: leather bandoliers darker; jeondae belt at the waist (under the straps)
straps = coat & brown & (pcw < 0.5)
recolor(straps, LEATHER, 1.0)
belt = np.zeros_like(coat)
if BELT:
    # a real band: height profile across the belt (bevelled edges + two lengthwise creases) -> Normals (DirectX),
    # Masks (R = AO darker at the edges and a contact shadow on the coat, G = roughness of a silk sash), shading
    WAIST, HALF = 0.47, 0.016
    tt = np.where(cov, (Z - WAIST) / HALF, 9.0)
    free = coat & cov & ~straps
    belt = free & (np.abs(tt) < 1.0)
    belt = ndimage.binary_opening(belt, iterations=1)
    plateau = np.clip((1 - np.abs(tt)) / 0.3, 0, 1)
    plateau = plateau * plateau * (3 - 2 * plateau)
    crease = 0.22 * np.cos(np.pi * tt * 2.6) * (0.6 + 0.4 * np.sin(xx / 21.0 + yy / 37.0))
    hgt = np.where(belt, 2.6 * (plateau + crease * plateau), 0.0)
    hgt = ndimage.gaussian_filter(hgt, 0.7)
    gy, gx = np.gradient(hgt)
    base = nrm[..., :3] * 2 - 1
    nb = np.dstack([0.3 * base[..., 0] - gx, 0.3 * base[..., 1] - gy, np.ones_like(gx)])
    nb /= np.linalg.norm(nb, axis=-1, keepdims=True)
    inside = belt | (ndimage.binary_dilation(belt, iterations=1) & free)
    nrm[inside, :3] = nb[inside] * 0.5 + 0.5
    recolor(belt, BELT, 0.35)
    light = np.array([-0.35, -0.55, 0.76])                     # from the top-left in image space
    shade = 0.8 + 0.2 * plateau + 0.35 * ((nb @ light) - light[2])
    out[belt] = np.clip(out[belt] * shade[belt, None], 0, 1)
    ao = msk[..., 0]
    ao[belt] = np.minimum(ao[belt], 0.68 + 0.27 * plateau[belt])
    rim = free & ~belt & (np.abs(tt) < 1.3)                     # contact shadow on the coat just beside the band
    ao[rim] = ao[rim] * (0.82 + 0.18 * np.clip((np.abs(tt[rim]) - 1) / 0.3, 0, 1))
    msk[belt, 1] = 185 / 255
    msk[belt, 2] = 0
    pc_out[belt] = 0

idx = ndimage.distance_transform_edt(~cov, return_distances=False, return_indices=True)
out[~cov] = out[idx[0][~cov], idx[1][~cov]]                 # padding follows its island
pc_out[~cov] = pc_out[idx[0][~cov], idx[1][~cov]]
det_out = det.copy()
det_out[..., 0] = pc_out
save = lambda a, name: Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)).save(
    os.path.join(D, 'jochong_age%d_%s.png' % (AGE, name)))
save(np.dstack([out, rgba[..., 3] / 255]), 'BaseColor')
save(det_out, 'Details')
save(nrm, 'Normals')
save(msk, 'Masks')
for nm, pc in (('blue', (0.18, 0.36, 0.9)), ('red', (0.86, 0.16, 0.16))):
    save(out * (1 - pc_out[..., None] + pc_out[..., None] * np.array(pc)), nm)
print('age', AGE, 'coat %d arms %d legs %d straps %d belt %d socks %d%s' % (
    coat.sum(), arms.sum(), legs.sum(), straps.sum(), belt.sum(), socks.sum(), disc_info))
