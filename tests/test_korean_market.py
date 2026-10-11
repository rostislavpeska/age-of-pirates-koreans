"""The Korean Market (Discovery Age): the merged Asian trade_market animfile routes Korean players to the Korean Market from
age 1 while Japanese and Chinese players keep their vanilla markets, every file it names is installed, the alpha page is a
cutout, player colour is bound on both own pages, and the runtime XML is CRLF.

    python -m pytest tests -q
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

K = Path(__file__).resolve().parents[1]
ART = K / "art"
MARKET = ART / "buildings" / "korean_market"
MERGED = ART / "buildings" / "asian_civs" / "trade_market" / "trade_market.xml"


def test_korean_market_runtime_files_are_crlf():
    for name in ("korean_market.xml", "korean_market.material", "korean_market_con.material", "korean_market_damaged.material"):
        data = (MARKET / name).read_bytes()
        assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b""), f"{name}: CRLF only"
    data = MERGED.read_bytes()
    assert b"\n" not in data.replace(b"\r\n", b""), "merged trade_market.xml: CRLF only"


def test_every_model_and_texture_the_market_names_is_installed():
    text = (MARKET / "korean_market.xml").read_text(encoding="utf-8")
    for ref in set(re.findall(r"buildings\\korean_market\\(\w+)", text)):
        assert (MARKET / f"{ref}.gr2").is_file(), ref
    assert (MARKET / "korean_market_damaged.hkt").is_file()
    for m in MARKET.glob("*.material"):
        for path in re.findall(r'override="([^"]+)"', m.read_text(encoding="utf-8")):
            if path.startswith("buildings\\korean_"):
                assert (ART / (path.replace("\\", "/") + ".ddt")).is_file(), (m.name, path)


def test_player_colour_and_cutout_on_the_market_pages():
    text = (MARKET / "korean_market.material").read_text(encoding="utf-8")
    for mat in ("mata", "matb"):
        assert f'override="buildings\\korean_market\\textures\\korean_market_{mat}_Details"' in text, mat
    sub = re.search(r'<submaterial name="matb">\s*<materialdef name="([^"]+)"', text).group(1)
    assert sub == "default_cutout", sub                             # the 1024 carries the alpha surfaces (single-sided)


def test_korean_players_get_the_korean_market_from_age_1():
    root = ET.fromstring(MERGED.read_text(encoding="utf-8"))
    names = {(s.text or "").strip() for s in root.iter("submodel")}
    culture = next(lg for c in root.findall("component") for lg in c.findall("logic") if lg.find("japanese") is not None)
    tech = culture.find("japanese").find("logic")
    kids = [c.tag for c in tech]
    assert kids[-1] == "zpkoreanvisuals", kids                      # last child: wins while zpKoreanVisuals is active
    inner = tech.find("zpkoreanvisuals").find("logic")
    assert [c.tag for c in inner] == ["none"]                       # Korean from the Discovery Age, no vanilla branch
    refs = [r.get("ref") for r in inner.iter("submodelref")]
    assert refs == ["korean_market_construction_stage_01", "korean_market_construction_stage_02",
                    "korean_market_construction_stage_03", "korean_market_built"]
    assert set(refs) <= names
    vanilla_none = tech.find("none")                                # Japanese players keep the vanilla markets
    assert [r.get("ref") for r in vanilla_none.iter("submodelref")][-1] == "japanese_market_age_01"
    chinese = culture.find("chinese").find("logic")
    assert "zpkoreanvisuals" not in [c.tag for c in chinese]        # the Chinese branch is untouched
