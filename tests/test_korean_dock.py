"""The Korean Dock (Discovery Age): the merged Asian dock animfile routes Korean players to the Korean Dock from age 1,
every file it names is installed, and the runtime XML is CRLF.

    python -m pytest tests -q
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

K = Path(__file__).resolve().parents[1]
ART = K / "art"
DOCK = ART / "buildings" / "korean_dock"
MERGED = ART / "buildings" / "asian_civs" / "dock" / "dock.xml"


def test_korean_dock_runtime_files_are_crlf():
    for name in ("korean_dock.xml", "korean_dock.material", "korean_dock_con.material", "korean_dock_damaged.material"):
        data = (DOCK / name).read_bytes()
        assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b""), f"{name}: CRLF only"
    data = MERGED.read_bytes()
    assert b"\n" not in data.replace(b"\r\n", b""), "merged dock.xml: CRLF only"


def test_every_model_and_texture_the_dock_names_is_installed():
    text = (DOCK / "korean_dock.xml").read_text(encoding="utf-8")
    for ref in set(re.findall(r"buildings\\korean_dock\\(\w+)", text)):
        assert (DOCK / f"{ref}.gr2").is_file(), ref
    assert (DOCK / "korean_dock_damaged.hkt").is_file()
    for m in DOCK.glob("*.material"):
        for path in re.findall(r'override="([^"]+)"', m.read_text(encoding="utf-8")):
            if path.startswith("buildings\\korean_"):
                assert (ART / (path.replace("\\", "/") + ".ddt")).is_file(), (m.name, path)


def test_player_colour_is_bound_on_the_dock_page():
    text = (DOCK / "korean_dock.material").read_text(encoding="utf-8")
    assert 'override="buildings\\korean_dock\\textures\\korean_dock_mata_Details"' in text


def test_korean_players_get_the_korean_dock_from_age_1():
    root = ET.fromstring(MERGED.read_text(encoding="utf-8"))
    names = {(s.text or "").strip() for s in root.iter("submodel")}
    culture = next(lg for c in root.findall("component") for lg in c.findall("logic") if lg.find("japanese") is not None)
    tech = culture.find("japanese").find("logic")
    kids = [c.tag for c in tech]
    assert kids[-1] == "zpkoreanvisuals", kids                      # last child: wins while zpKoreanVisuals is active
    inner = tech.find("zpkoreanvisuals").find("logic")
    assert [c.tag for c in inner] == ["none"]                       # Korean from the Discovery Age, no vanilla branch
    refs = [r.get("ref") for r in inner.iter("submodelref")]
    assert refs == ["korean_dock_construction_stage_01", "korean_dock_construction_stage_02",
                    "korean_dock_construction_stage_03", "korean_dock_built"]
    assert set(refs) <= names
    vanilla_none = tech.find("none")                                # Japanese players keep the vanilla age-1 dock
    assert [r.get("ref") for r in vanilla_none.iter("submodelref")][-1] == "japanese_dock_age1"
