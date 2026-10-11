"""Jangchang Spearman: Joseon retexture of one vanilla Chinese Qiang pikeman age (0/1/2), colours only, following the
model's own garments; the same palette and rules as retexture_jochong.py (owner 2026-10-09).
  age 0 (base)       : coat in player colour with black edging, white hemp sleeves, white baji, indigo haengjeon,
                       indigo jeondae; the Manchu fur cap (part of the head mesh) repainted as a black felt beonggeoji
  age 1 (Disciplined): the steel tugu helmet with red plume and mail (kept); the round Qing badge on the back painted
                       out (fabric, Normals and Masks follow the coat around it)
  age 2 (Honored)    : the studded dujeong-gap (kept, studs repainted brass), red dongdari sleeves, black jeondae
                       (the front opening keeps the vanilla dark inner robe: the leg recolour of ages 0/1 split it
                       into white baji and indigo wraps at the knee, ragged white patches on the coat)
  2  (Honored)       : + gilt studs and helmet fittings, the rim band of the bowl and the cup under the red tassel
                       (owner 2026-10-10: "more fancy, maybe some gilded parts?", "if realistic?", "on the armor
                       studs", "partially gilded helmet too": gilt-brass studs and fittings on officers' armour),
                       metallic and smoother in its own Masks
  2w (Disciplined)   : the age 2 body with white sleeves and brass studs, no gilding (owner 2026-10-10: "split
                       industrial - one with red sleeves - industrial and one with white sleeves - fortress"); only its
                       BaseColor is its own: the base parameters of the age 2 material, age 2 itself its variant 1
    python retexture_jangchang.py DIR AGE          # AGE = 0, 1, 2 or 2w
DIR holds the vanilla maps decoded to ageN_{BaseColor,Details,Normals,Masks}.png and texmap.py's ageN_texmap.npz;
writes DIR/jangchang_age<AGE>_{BaseColor,Details,Normals,Masks}.png and _blue/_red previews."""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

D, TAG = sys.argv[1], sys.argv[2]
AGE = int(TAG[0])
WHITE = (226, 221, 207)
BAJI = (220, 216, 204)
INDIGO = (54, 60, 86)
EDGE = (36, 36, 42)
CRIMSON = (148, 34, 32)
FELT = (34, 31, 31)
BRASS = (184, 146, 70)
GILT = (222, 178, 74)
GILDED = TAG == '2'
SLEEVE = {0: (214, 209, 194), 1: (214, 209, 194), 2: CRIMSON}[AGE]
if TAG == '2w':
    SLEEVE = (214, 209, 194)                    # the white sleeves of ages 0/1 on the studded armour
BELT = {0: INDIGO, 1: INDIGO, 2: (34, 34, 40)}[AGE]

ld = lambda n: np.asarray(Image.open(os.path.join(D, 'age%d_%s.png' % (AGE, n))).convert('RGBA'), np.float64) / 255
base, det, nrm, msk = ld('BaseColor'), ld('Details'), ld('Normals'), ld('Masks')
tm = np.load(os.path.join(D, 'age%d_texmap.npz' % AGE))
pos, part, isl = tm['pos'], tm['part'], tm['island']
cov = ~np.isnan(pos[..., 0])
Z = np.where(cov, pos[..., 2], np.nan)
rgb = base[..., :3].copy()


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


coat = islands_where(lambda c, pc, n, z0, z1: pc > 0.5 and n > 100000)
brown = (hue > 8) & (hue < 45) & (sat > 0.25) & (lum > 0.08) & (lum < 0.6)

# 1. age 1: paint out the round badge on the back (brown, inside the coat, not player colour) - fill from the coat
badge_info = ''
if AGE == 1:
    badge = coat & brown & (pcw < 0.5)
    lab, n = ndimage.label(ndimage.binary_dilation(badge, iterations=2))
    keep = [i for i, s in enumerate(np.bincount(lab.ravel())) if i and s > 400]
    badge = ndimage.binary_dilation(np.isin(lab, keep), iterations=3) & coat
    fabric = coat & ~badge
    for arr in (rgb, det, nrm, msk):
        flat = arr.reshape(-1, arr.shape[-1]) if arr.ndim == 3 else arr
        idx = ndimage.distance_transform_edt(~fabric, return_distances=False, return_indices=True)
        src = arr[idx[0], idx[1]]
        blur = np.stack([ndimage.gaussian_filter(src[..., c], 3) for c in range(src.shape[-1])], -1)
        arr[badge] = blur[badge]
    nrm[badge, :3] = nrm[badge, :3] * 0.5 + np.array([0.5, 0.5, 1.0]) * 0.5      # the badge's relief flattened
    pcw = det[..., 0]
    lum, sat, hue = colour_stats(rgb)
    badge_info = ' badge painted out %d px' % badge.sum()

out = rgb.copy()


def recolor(mask, target, contrast=1.0):
    if not mask.any():
        return
    t = np.array(target, float) / 255
    tl = t @ np.array([0.299, 0.587, 0.114])
    m = lum[mask].mean()
    lp = np.clip(tl + contrast * (lum[mask] - m) * (tl / max(m, 0.05)) ** 0.5, 0.02, 0.98)
    out[mask] = np.clip(t[None, :] * (lp / tl)[:, None], 0, 1)


arms = islands_where(lambda c, pc, n, z0, z1: c[3] > 0.9)
legs = islands_where(lambda c, pc, n, z0, z1: c[5] + c[6] > 0.6 and pc < 0.5)          # calf + thigh
feet = islands_where(lambda c, pc, n, z0, z1: c[4] > 0.6, minimum=500)
cap = islands_where(lambda c, pc, n, z0, z1: c[1] > 0.95 and z0 > 0.745, minimum=500)
skin = ((hue < 45) | (hue > 340)) & (sat > 0.22) & (lum > 0.3)
hand = (part == 2) | skin
light = (lum > 0.45) & (sat < 0.18) & (pcw < 0.5)

# 2. coat: the light Qing piping -> black edging; the waist band -> the jeondae; age 2 studs -> brass
studs = coat & light & (pcw < 0.5) & np.zeros_like(coat)
if AGE == 2:
    lab, n = ndimage.label(coat & light)
    sizes = np.bincount(lab.ravel())
    small = np.isin(lab, [i for i in range(1, n + 1) if 30 < sizes[i] < 900])     # round studs, not the long piping
    studs = small
band = coat & light & ~studs & (Z < 0.485)
if AGE < 2:                                     # ages 0/1: the painted hem band of the tunic (its non-player-colour texels)
    band = ndimage.binary_closing(coat & (part == 7) & (pcw < 0.5) & (Z < 0.5), iterations=2) & coat & (pcw < 0.5)
edging = coat & light & ~studs & ~band
recolor(edging, EDGE, 0.7)
recolor(band, BELT, 0.6)
recolor(studs, GILT if GILDED else BRASS, 0.9)
pc_out = pcw.copy()
pc_out[edging | band | studs] = 0

# 3. arms: sleeves (not the player-colour shoulder caps, their light borders and studs, not the hands)
arm_light = arms & light & ~hand
lab, n = ndimage.label(arm_light)
sizes = np.bincount(lab.ravel())
arm_studs = np.isin(lab, [i for i in range(1, n + 1) if 30 < sizes[i] < 900]) if AGE == 2 else np.zeros_like(arms)
sleeve = arms & (pcw < 0.5) & ~hand & ~arm_light
recolor(sleeve, SLEEVE, 0.45)
recolor(arm_light & ~arm_studs, EDGE, 0.7)
recolor(arm_studs, GILT if GILDED else BRASS, 0.9)
pc_out[arm_light] = 0
# 4. legs (ages 0/1, short coat): white baji above the knee, indigo haengjeon below, boots stay. Age 2's long coat
#    shows only the vanilla dark inner robe at its front opening: kept
if AGE < 2:
    leg = legs & ~feet & cov & ~hand & (pcw < 0.5) & (part != 1) & (Z < 0.55)   # the face can share an island
    knee = 0.2
    recolor(leg & (Z >= knee), BAJI, 0.5)
    recolor(leg & (Z < knee), INDIGO, 0.5)
# 5. age 0: the fur cap -> black felt beonggeoji
if AGE == 0:
    recolor(cap & cov, FELT, 0.6)
    msk[cap & cov, 1] = np.maximum(msk[cap & cov, 1], 0.86)          # felt: matte
# 6. Honored: gilt studs (above), the rim band of the steel bowl and the cup under the red tassel; gilt = metallic,
#    smoother (vanilla paints the studs silver but not metallic)
gilt_info = ''
if GILDED:
    bowl = cap & cov & (msk[..., 2] > 0.9)                           # the steel bowl halves
    plume = cap & cov & (msk[..., 2] < 0.1) & (sat > 0.6)              # the red tassel cone
    rim = bowl & (Z < np.nanmin(Z[bowl]) + 0.007)
    cup = plume & (Z < np.nanmin(Z[plume]) + 0.010)
    recolor(rim | cup, GILT, 0.9)
    gilt = studs | arm_studs | rim | cup
    msk[gilt, 2] = 1.0
    msk[gilt, 1] = 0.35
    gilt_info = ' gilt: studs %d rim %d cup %d' % ((studs | arm_studs).sum(), rim.sum(), cup.sum())

idx = ndimage.distance_transform_edt(~cov, return_distances=False, return_indices=True)
out[~cov] = out[idx[0][~cov], idx[1][~cov]]
pc_out[~cov] = pc_out[idx[0][~cov], idx[1][~cov]]
det_out = det.copy()
det_out[..., 0] = pc_out
save = lambda a, name: Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8)).save(
    os.path.join(D, 'jangchang_age%s_%s.png' % (TAG, name)))
save(np.dstack([out, base[..., 3]]), 'BaseColor')
save(det_out, 'Details')
save(nrm, 'Normals')
save(msk, 'Masks')
for nm, pc in (('blue', (0.18, 0.36, 0.9)), ('red', (0.86, 0.16, 0.16))):
    save(out * (1 - pc_out[..., None] + pc_out[..., None] * np.array(pc)), nm)
print('age', TAG, 'coat %d arms %d legs %d cap %d edging %d band %d studs %d sleeve %d%s%s' % (
    coat.sum(), arms.sum(), legs.sum(), cap.sum(), edging.sum(), band.sum(), studs.sum(), sleeve.sum(), badge_info,
    gilt_info))
