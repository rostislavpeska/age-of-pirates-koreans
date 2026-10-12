"""Every Korean building ships with its test bed unit (owner 2026-10-11: "test bed must always be part of the package").

A zzTEST bench in data/protomods.xml loads the building's Korean animfile directly (no civ / age logic), so the model,
its construction stages and its destruction can be placed and tested in the editor or from zzTESTKoreanBuilderWagon.

    python -m pytest tests -q
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

K = Path(__file__).resolve().parents[1]
ART = K / "art"
sys.path.insert(0, str(K / "tools"))
import korean_visuals  # noqa: E402

PROTO = ET.fromstring((K / "data" / "protomods.xml").read_text(encoding="utf-8"))
BENCHES = {u.get("name"): u for u in PROTO.iter("unit") if (u.get("name") or "").startswith("zzTEST")}
WAGON = BENCHES.pop("zzTESTKoreanBuilderWagon")
HOUSE_BENCHES = ("zzTESTKoreanHouseA", "zzTESTKoreanHouseB", "zzTESTKoreanHouseC")    # zpHouseKorean: one per variant


def norm(path):
    return path.replace("\\", "/").lower().removeprefix("art/")


def test_every_korean_building_has_a_test_bed():
    by_anim = {norm(u.findtext("animfile")): n for n, u in BENCHES.items()}
    missing = [src for src in korean_visuals.source_animfiles() if norm(src) not in by_anim]
    assert not missing, f"no zzTEST bench loads these Korean animfiles: {missing} (add one to the zzTEST block of data/protomods.xml)"
    assert all(h in BENCHES for h in HOUSE_BENCHES)


def test_every_test_bed_resolves_and_is_buildable():
    trains = {t.text for t in WAGON.iter("train")}
    for name, u in BENCHES.items():
        anim = ART / norm(u.findtext("animfile"))
        assert anim.is_file(), f"{name}: animfile {anim} missing"
        assert name in trains, f"{name} is not on zzTESTKoreanBuilderWagon"
        assert u.findtext("dbid") == u.get("id"), name
        text = anim.read_text(encoding="utf-8", errors="replace")
        for ref in set(re.findall(r"<file>((?:buildings\\korean_|zbench_)[^<]+)</file>", text)):
            assert (ART / (norm(ref) + ".gr2")).is_file(), f"{name}: {ref}.gr2 missing"


def test_dock_bench_places_like_a_dock():
    d = BENCHES["zzTESTKoreanDock"]
    assert d.findtext("placementfile") == "dock.xml" and d.findtext("physicsinfo") == "dock"
    assert {"TieToWaterSurface", "SnapPlacement"} <= {f.text for f in d.iter("flag")}
