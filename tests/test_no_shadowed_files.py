"""No file of this add-on is shadowed by AoP (owner 2026-10-11: "Consulate still original Japanese ... follow pattern").

AoE3DE resolves a path that two enabled mods ship by mod priority: the mod with the lower `Priority` in
<profile>/mods/age3-mod-status.json wins, and AoP has priority 1, this add-on 2. Only the additive `*mods.xml` data
files (and their XMB twins) are merged across mods. Every other file this add-on ships at a path AoP also ships never
reaches the game: the Korean consulate showed as the Japanese one because AoP's consulate.xml won. The fix is the castle
pattern: AoP hosts the Korean branch in its own file (tools/korean_visuals.py AOP_HOSTED), and this add-on ships no copy.

    python -m pytest tests -q
"""
import os
from pathlib import Path

import pytest

K = Path(__file__).resolve().parents[1]
AOP = Path(os.environ.get("AOP_ROOT") or K.parent / "age-of-pirates")
GAME_DIRS = ("art", "data", "game", "sound")
# Known shadowed files, waiting for the owner's decision (AUDIT.md): the add-on's Korean wagon voices
# (tools/korean_sounds.py) are built on AoP's copies, but AoP's own files win, so these two wagons stay Japanese-voiced.
# strict: once fixed, the xfail turns into a failure and the entry must go.
KNOWN = {"sound/factorywagon_snds.xml", "sound/fortwagon_snds.xml"}


def game_files(root):
    out = {}
    for top in GAME_DIRS:
        for p in (root / top).rglob("*"):
            if p.is_file():
                out[p.relative_to(root).as_posix().lower()] = p.relative_to(root).as_posix()
    return out


def additive(rel):
    return rel.removesuffix(".xmb").endswith("mods.xml")


def shadowed():
    if not AOP.is_dir():
        pytest.skip(f"AoP checkout not found at {AOP} (set AOP_ROOT): shadowing NOT checked")
    mine, aop = game_files(K), game_files(AOP)
    return sorted(mine[r] for r in set(mine) & set(aop) if not additive(r))


def test_no_add_on_file_is_shadowed_by_aop():
    bad = [p for p in shadowed() if p.lower() not in KNOWN]
    assert not bad, ("AoP (priority 1) ships these paths too, so the game never reads this add-on's copy: %s. "
                     "Host the Korean branch in AoP's file (korean_visuals.AOP_HOSTED) and delete the copy here." % bad)


@pytest.mark.xfail(strict=True, reason="owner decision pending: AoP's wagon sound files shadow the Korean wagon voices")
@pytest.mark.parametrize("rel", sorted(KNOWN))
def test_known_shadowed_file_is_fixed(rel):
    assert rel not in {p.lower() for p in shadowed()}


def test_aop_hosted_files_live_only_in_aop():
    import sys
    sys.path.insert(0, str(K / "tools"))
    import korean_visuals
    for rel in korean_visuals.AOP_HOSTED:
        assert (AOP / rel).is_file(), f"AoP must host {rel}"
        assert not (K / rel).exists(), f"{rel} is hosted by AoP: this add-on ships no copy"
        assert "zpkoreanvisuals" in (AOP / rel).read_text(encoding="utf-8"), f"AoP's {rel} lacks the Korean branch"
