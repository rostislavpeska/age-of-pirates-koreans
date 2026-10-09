"""Texture-set coherence of the Korean models (moved here from AoP on 2026-10-09 with the models).

The rules are AoP's scripts/havok/texture_sets.py (generic tests there); this file pins the Korean data: the shared
generic atlas korean_shared_matc_r65 is the ONE generic atlas of every Korean building, its retired predecessors
(TC v1 512, military v2 512) are gone and never bound, every own Korean texture is registered (tools/texture_sets.json),
every model bound to the atlas sits inside its regions with the atlas's tangent convention, and a path swap without
UV remap / new tangents (the S18k TC on the r65 material) is caught. Canonical atlas record: korean-buildings-blender
patterns/korean/shared_atlas_r65.json.

    python -m pytest tests -q          (needs ../age-of-pirates or AOP_ROOT; skips without it)
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

K = Path(__file__).resolve().parents[1]
ART = K / "art"
AOP = Path(os.environ.get("AOP_ROOT") or K.parent / "age-of-pirates")
if not (AOP / "scripts" / "havok" / "texture_sets.py").is_file():
    pytest.skip("AoP checkout not found (../age-of-pirates or AOP_ROOT)", allow_module_level=True)
sys.path.insert(0, str(AOP / "scripts" / "havok"))
sys.dont_write_bytecode = True
import texture_sets as TS  # noqa: E402
from gr2_lint import read_raw  # noqa: E402

REGISTRY = K / "tools" / "texture_sets.json"
REG = TS.load_registry(REGISTRY)
KOREAN_TEXTURE_DIRS = ("buildings/korean_tc/textures", "buildings/korean_shared/textures",
                       "zbench_korean_military/barracks/textures", "zbench_korean_military/stable/textures")
KOREAN_MODELS = [("buildings/korean_tc/korean_tc.gr2", "buildings/korean_tc/korean_tc.material"),
                 ("buildings/korean_tc/korean_tc_damaged.gr2", "buildings/korean_tc/korean_tc_damaged.material"),
                 ("buildings/korean_tc/korean_tc_con.gr2", "buildings/korean_tc/korean_tc_con.material"),
                 ("zbench_korean_military/barracks/korean_barracks_physics.gr2", "zbench_korean_military/barracks/korean_barracks_physics.material"),
                 ("zbench_korean_military/barracks/korean_barracks_physics_damaged.gr2", "zbench_korean_military/barracks/korean_barracks_physics_damaged.material"),
                 ("zbench_korean_military/stable/korean_stable_physics.gr2", "zbench_korean_military/stable/korean_stable_physics.material"),
                 ("zbench_korean_military/stable/korean_stable_physics_damaged.gr2", "zbench_korean_military/stable/korean_stable_physics_damaged.material")]


def test_the_models_find_this_registry():
    assert TS.registry_for(ART / KOREAN_MODELS[0][1]) == REGISTRY


def test_registry_current_sets_match_the_installed_files():
    for s in REG["sets"]:
        if s["status"] != "current":
            continue
        for ch, row in s["channels"].items():
            p = ART / (row["path"] + ".ddt")
            assert p.exists(), (s["id"], ch, p)
            assert TS.sha256(p) == row["sha256"], f"{s['id']} {ch}: the registry pins another revision of {p.name}"


def test_one_generic_atlas_copy_and_the_retired_pages_unbound():
    retired = [r["path"] for s in REG["sets"] if s["status"] == "retired" for r in s["channels"].values()]
    assert retired
    for rel in retired:
        assert not (ART / (rel + ".ddt")).exists(), f"one atlas copy only: {rel} is retired"
        assert not (AOP / "art" / (rel + ".ddt")).exists(), f"one atlas copy only: {rel} is back in AoP"
    assert not (AOP / "art" / "buildings" / "korean_shared").exists(), "the shared atlas lives here only (AGENTS.md 15)"
    refs = {TS.norm_ref(r) for r in retired}
    for m in ART.rglob("*.material"):
        for _, _, b in TS.parse_material(m.read_text(encoding="utf-8", errors="replace")):
            assert not refs & {TS.norm_ref(r) for r in b.values()}, m


def test_every_korean_own_texture_is_registered():
    known = set(REG["_by_ref"])
    for d in KOREAN_TEXTURE_DIRS:
        for p in (ART / d).glob("*.ddt"):
            ref = TS.norm_ref(p.relative_to(ART).with_suffix("").as_posix())
            assert ref in known, f"register {p.relative_to(ART)} in tools/texture_sets.json"


def test_no_material_mixes_texture_sets():
    bad = {}
    for m in ART.rglob("*.material"):
        errs = TS.material_findings(m, REG, ART)["errors"]
        if errs:
            bad[str(m.relative_to(K))] = errs
    assert not bad, bad


@pytest.mark.parametrize("gr2,mat", KOREAN_MODELS)
def test_models_sit_inside_the_atlas_regions_with_its_tangents(gr2, mat):
    info = read_raw(ART / gr2)
    checked, outside, sets = TS.region_findings(info, ART / mat, REG)
    assert checked and outside == 0 and sets == ["korean_shared_matc_r65"], (checked, outside, sets)
    rows = [r for r in TS.tangent_findings(info, ART / mat, REG) if r[3] >= 50]
    assert rows and all(share >= 0.9 for _, _, share, _ in rows), rows


def test_a_path_swap_without_uv_remap_and_tangents_is_caught(tmp_path):
    """the shipped S18k damaged TC (backing on the old 512 page, TC tangents; AoP history ba233e90) bound to today's
    r65 material: the faces cross region borders and carry the opposite tangent convention."""
    r = subprocess.run(["git", "-C", str(AOP), "show", "ba233e90:art/buildings/korean_tc/korean_tc_damaged.gr2"],
                       capture_output=True, timeout=120)
    if r.returncode or not r.stdout:
        pytest.skip("the S18k specimen is not in the AoP clone")
    (tmp_path / "s18k.gr2").write_bytes(r.stdout)
    info = read_raw(tmp_path / "s18k.gr2")
    mat = ART / "buildings/korean_tc/korean_tc_damaged.material"
    checked, outside, _ = TS.region_findings(info, mat, REG)
    assert checked and outside / checked > 0.2, (checked, outside)          # measured 7,836 / 20,357 cross a border
    r65 = [x for x in TS.tangent_findings(info, mat, REG) if x[0] == "korean_shared_matc_r65"]
    assert r65 and r65[0][2] < 0.1, r65


def test_review_scene_images_resolve_and_the_2026_10_08_mix_is_caught():
    assert TS.set_of_image(REG, "shared_r65_BaseColor.png")[0] == "korean_shared_matc_r65"
    assert TS.set_of_image(REG, "26f76a47d69a_26f76a47d69a_MATC_V2_Masks.png")[0] == "korean_shared_matc_v2"
    assert TS.set_of_image(REG, "MATC_BaseColor.png")[0] == "korean_tc_matc_v1"
    bound = {"basecolor": "korean_shared_matc_r65", "normals": TS.set_of_image(REG, "MATC_V2_Normal.png")[0],
             "masks": TS.set_of_image(REG, "MATC_V2_Masks.png")[0]}
    assert any("2 different texture sets" in e for e in TS.binding_findings(bound, REG, "barracks | r60-library-v3"))
