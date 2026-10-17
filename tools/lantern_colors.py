#!/usr/bin/env python
"""Korean HC Cheongsachorong lantern colours (art/homecity/korean/lanterns/textures): 17th-century dyed silk lit by a
candle instead of primary red and blue neon. Owner 2026-10-17: "too pinky - possibly the emit + the basecolor together
look like blue++red = pink ... more like 17 century lanterns and less like Disneyland in Seoul".
Audit: Blendify journal 2026-10-17-claude-opus-5.5-39.

    python tools/lantern_colors.py [--preview OUT.png]

Sources are the committed textures of SOURCE (git show), so a rerun regrades the originals, never its own output.
 BaseColor: the silk panel (SILK, the atlas rectangle of the lantern body) takes the dye colours - safflower red above,
   indigo below - with each texel's own shading (its luminance over the median of its colour band); rope, wood and caps
   outside the panel stay byte-identical.
 Emissive: candlelight through that silk: the emissive luminance x the tint of the silk under it (red -> warm orange,
   indigo -> a dim cold glow), mixed by the same red/blue weight, so the purple band at the seam is gone.
 Material: EmissiveIntensity 2.5 -> EMISSIVE (vanilla China round lanterns: 2.12); EmissiveColor stays white.
Writes the PNGs and their 512 DXT1 DDTs (AoP scripts/havok/ddt_dxt1.py; 174,872 B as tools/homecity_lanterns.py expects).
"""
import argparse, re, subprocess, sys
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
import korean_visuals  # noqa: E402  (AOP)
DDT = Path(korean_visuals.AOP) / 'scripts' / 'havok' / 'ddt_dxt1.py'
TEX = REPO / 'art' / 'homecity' / 'korean' / 'lanterns' / 'textures'
MATERIAL = REPO / 'art' / 'homecity' / 'korean' / 'lanterns' / 'korean_lantern_upgrade.material'
SOURCE = '792417b'                                   # the Cheongsachorong textures as first deployed
SILK = (0, 138, 425, 505)                            # x0, y0, x1, y1 (exclusive) of the silk panel in the 512 atlas
                                                     # (measured: saturated rows 138-504, columns 0-424; tan border below)
DYE_RED = np.array([150, 40, 30], float)             # safflower-dyed silk, aged
DYE_BLUE = np.array([36, 60, 94], float)             # indigo silk (cheongsa)
GLOW_RED = np.array([1.00, 0.46, 0.20])              # candle through red silk
GLOW_BLUE = np.array([0.20, 0.22, 0.28])             # little light through indigo
EMISSIVE = 2.0


def source(name):
    rel = f'art/homecity/korean/lanterns/textures/{name}'
    raw = subprocess.run(['git', 'show', f'{SOURCE}:{rel}'], cwd=REPO, capture_output=True, check=True).stdout
    return np.asarray(Image.open(BytesIO(raw)).convert('RGB'), float)


def lum(a):
    return a @ np.array([0.2126, 0.7152, 0.0722])


def grade(base, emis):
    x0, y0, x1, y1 = SILK
    b, e = base.copy(), emis.copy()
    pb, pe = base[y0:y1, x0:x1], emis[y0:y1, x0:x1]
    w = np.clip((pb[..., 0] - pb[..., 2]) / (pb[..., 0] + pb[..., 2] + 1e-6) * 0.5 + 0.5, 0, 1)[..., None]   # 1 = red
    L = lum(pb)[..., None]
    med_r, med_b = np.median(L[w[..., 0] > 0.8]), np.median(L[w[..., 0] < 0.2])
    shade = L / (w * med_r + (1 - w) * med_b)
    b[y0:y1, x0:x1] = np.clip((w * DYE_RED + (1 - w) * DYE_BLUE) * shade, 0, 255)
    peak = lum(pe).max()
    e[y0:y1, x0:x1] = np.clip(lum(pe)[..., None] / peak * 255 * (w * GLOW_RED + (1 - w) * GLOW_BLUE), 0, 255)
    return b.round().astype(np.uint8), e.round().astype(np.uint8)


def write(name, arr):
    png = TEX / f'{name}.png'
    Image.fromarray(arr).save(png)
    subprocess.run([sys.executable, str(DDT), str(png), str(TEX / f'{name}.ddt'), '--size', '512'], check=True,
                   capture_output=True)
    assert (TEX / f'{name}.ddt').stat().st_size == 174872, name


def material():
    raw = MATERIAL.read_bytes()
    new = re.sub(rb'(<float name="EmissiveIntensity" override=")[0-9.]+(")', rb'\g<1>%.4f\g<2>' % EMISSIVE, raw)
    assert new.count(b'EmissiveIntensity') == 2 and b'\n' not in new.replace(b'\r\n', b'')
    MATERIAL.write_bytes(new)


def preview(path, before, after):
    """before/after strips of the silk panel: BaseColor, Emissive, and a glow composite (base x 0.35 + emissive x 0.45 x
    intensity) - a swatch, not the game's shader"""
    x0, y0, x1, y1 = SILK
    rows = []
    for (b, e), k in ((before, 2.5), (after, EMISSIVE)):
        cb, ce = b[y0:y1, x0:x1].astype(float), e[y0:y1, x0:x1].astype(float)
        glow = np.clip(cb * 0.35 + ce * 0.45 * k / 2.5 * 1.6, 0, 255)
        rows.append(np.concatenate([cb, np.full((y1 - y0, 8, 3), 255.0), ce, np.full((y1 - y0, 8, 3), 255.0), glow], 1))
    sheet = np.concatenate([rows[0], np.full((8, rows[0].shape[1], 3), 255.0), rows[1]], 0).astype(np.uint8)
    Image.fromarray(sheet).save(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--preview', help='write a before/after swatch here (outside the repo)')
    a = ap.parse_args(argv)
    base, emis = source('korean_lanterns_mata_basecolor.png'), source('korean_lanterns_mata_emissive.png')
    nb, ne = grade(base, emis)
    x0, y0, x1, y1 = SILK
    outside = np.ones(base.shape[:2], bool); outside[y0:y1, x0:x1] = False
    assert np.array_equal(nb[outside], base[outside].astype(np.uint8)), 'texels outside the silk panel changed'
    write('korean_lanterns_mata_basecolor', nb); write('korean_lanterns_mata_emissive', ne); material()
    if a.preview:
        preview(a.preview, (base.astype(np.uint8), emis.astype(np.uint8)), (nb, ne))
    print('GRADED', dict(red=DYE_RED.tolist(), blue=DYE_BLUE.tolist(), emissive=EMISSIVE, preview=a.preview))
    return 0


if __name__ == '__main__':
    sys.exit(main())
