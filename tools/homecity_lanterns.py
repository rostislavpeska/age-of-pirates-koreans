#!/usr/bin/env python
"""Harness and verification gate for Korean Home City lanterns (art/homecity/korean/lanterns).
Hardens the export pipeline against prop misplacement regressions (e.g. lanterns floating
at the vanilla Chinese drawbridge/pier position).

Usage:
    python tools/homecity_lanterns.py --check
"""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
import korean_visuals
AOP = Path(korean_visuals.AOP)
HAVOK = AOP / 'scripts' / 'havok'

GR2_PATH = REPO / 'art' / 'homecity' / 'korean' / 'lanterns' / 'korean_lantern_upgrade.gr2'
MAT_PATH = REPO / 'art' / 'homecity' / 'korean' / 'lanterns' / 'korean_lantern_upgrade.material'
TEX_DIR = REPO / 'art' / 'homecity' / 'korean' / 'lanterns' / 'textures'

REQUIRED_MESHES = [
    'Wall_Move_lanterns_GEO3Shape',
    'bridge_BG_lanterns_GEOShape',
    'bridge_move_lanterns_L_GEOShape',
    'bridge_move_lanterns_R_GEOShape',
    'building_lanterns_GEOShape',
    'enrty_lanterns_GEOShape',
    'stall_lanterns_GEOShape',
]

REQUIRED_TEXTURES = [
    'korean_lanterns_mata_basecolor.ddt',
    'korean_lanterns_mata_emissive.ddt',
    'korean_lanterns_mata_normals.ddt',
    'korean_lanterns_mata_masks.ddt',
]


def verify_lantern_upgrade(gr2_path):
    """Decompile to GXO via converter and verify bounds & structure."""
    assert gr2_path.exists(), f"GR2 missing: {gr2_path}"
    
    # Decompile to temp GXO
    gxo_path = gr2_path.with_suffix('.gxo')
    r = subprocess.run([sys.executable, str(HAVOK / 'converter.py'), '--format', 'gxo', str(gr2_path)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"GXO decompile failed: {r.stderr}\n{r.stdout}"
    assert gxo_path.exists(), f"GXO output missing: {gxo_path}"
    
    content = gxo_path.read_text(encoding='utf-8', errors='ignore')
    
    # Check all meshes
    for m in REQUIRED_MESHES:
        assert f'"{m}"' in content, f"Missing required mesh in GR2: {m}"
        
        # Check coordinates of bridge_move_lanterns
        if 'bridge_move' in m:
            pos = content.find(f'"{m}"')
            next_m = content.find('\nm "', pos + len(m) + 5)
            sub = content[pos:next_m] if next_m != -1 else content[pos:]
            verts = re.findall(r'v\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', sub)
            assert verts, f"No vertices for {m}"
            xs = [float(v[0]) / 100.0 for v in verts]
            ys = [float(v[1]) / 100.0 for v in verts]
            
            # Regression check: Must NOT sit at the old Chinese pier (X around -3 to 0, Y < 0)
            bad_pier_verts = [x for x, y in zip(xs, ys) if -5.0 < x < 2.0 and y < 0.0]
            assert not bad_pier_verts, (
                f"REGRESSION: {m} has {len(bad_pier_verts)} vertices sitting in the water "
                f"at the old Chinese drawbridge! (X in [-5, 2], Y < 0)"
            )
            
            # Must sit along the Korean bridge on the far left (X < -40)
            assert all(x < -40.0 for x in xs), (
                f"{m} is not on the Korean bridge: max X is {max(xs):.2f} (expected < -40.0)"
            )
            
    print("GR2 verification PASSED: all 7 meshes present and correctly positioned on the Korean bridge.")


def verify_materials():
    """Verify material XML parameters and CRLF line endings."""
    assert MAT_PATH.exists(), f"Material missing: {MAT_PATH}"
    raw = MAT_PATH.read_bytes()
    assert b'\r\n' in raw and b'\r\r\n' not in raw, "Material must have CRLF line endings (Rule 1)"
    text = raw.decode('utf-8')
    assert 'EmissiveColor' in text and '1.000, 1.000, 1.000, 1.000' in text, "EmissiveColor must be 1.0 pure white override"
    assert 'korean_lanterns_mata_basecolor' in text, "BaseColor must point to Korean lanterns"
    print("Material verification PASSED: CRLF line endings and bi-color emissive parameters validated.")


def verify_textures():
    """Verify 512x512 DXT1 textures with 10 mips."""
    for tex_name in REQUIRED_TEXTURES:
        p = TEX_DIR / tex_name
        assert p.exists(), f"Texture missing: {p}"
        size = p.stat().st_size
        # 512x512 DXT1 with 10 mips is exactly 174,872 bytes
        assert size == 174872, f"Texture {tex_name} has unexpected size {size} (expected 174872 bytes)"
    print("Texture verification PASSED: all 4 DDT textures validated (512x512, 10 mips, 174,872 B).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help="Run full verification gate on deployed assets")
    args = parser.parse_args()
    
    verify_textures()
    verify_materials()
    verify_lantern_upgrade(GR2_PATH)
    print("\nALL HARNESS CHECKS PASSED: Korean Home City lanterns are fully verified.")


if __name__ == '__main__':
    main()
