"""tools/texture_registry.py: installs re-pin tools/texture_sets.json, and a commit that does not is refused (INC-400).

Between 13 and 14 Oct 2026 nine texture installs replaced registered DDTs without re-pinning them; 40 channels in 14 sets
went stale and the registry test reported only the first set. These fixtures use a two-set registry in tmp_path, so they
run without AoP.

    python -m pytest tests -q
"""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

K = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("texture_registry", K / "tools" / "texture_registry.py")
TR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(TR)


def sha(data):
    import hashlib
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def mod(tmp_path):
    """a mod root: art/ with one current page (two channels) and one retired page, and its registry"""
    tex = tmp_path / "art" / "buildings" / "x" / "textures"
    tex.mkdir(parents=True)
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r1")
    (tex / "x_mata_Normals.ddt").write_bytes(b"normals r1")
    (tex / "x_old_BaseColor.ddt").write_bytes(b"old")
    reg = {"schema": 1, "sets": [
        {"id": "x_mata", "status": "current", "channels": {
            "BaseColor": {"path": "buildings/x/textures/x_mata_BaseColor", "sha256": sha(b"colour r1")},
            "Normals": {"path": "buildings/x/textures/x_mata_Normals", "sha256": sha(b"normals r1")}}, "tangent": "uv"},
        {"id": "x_old", "status": "retired", "record": "first page", "channels": {
            "BaseColor": {"path": "buildings/x/textures/x_old_BaseColor", "sha256": sha(b"old")}}}]}
    (tmp_path / "tools").mkdir()
    TR.dump(reg, tmp_path / "tools" / "texture_sets.json")
    return tmp_path


def test_drift_lists_every_stale_channel_not_only_the_first(mod):
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    (tex / "x_mata_Normals.ddt").unlink()
    stale = TR.drift(TR.load(mod / "tools" / "texture_sets.json"), mod / "art")
    assert [(d["channel"], d["installed"]) for d in stale] == [("BaseColor", sha(b"colour r2")), ("Normals", None)]


def test_pin_takes_the_installed_bytes_and_records_the_install_once(mod):
    reg_path, art = mod / "tools" / "texture_sets.json", mod / "art"
    tex = art / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    (tex / "x_mata_Normals.ddt").write_bytes(b"normals r2")
    changed, skipped = TR.pin([tex / "x_mata_BaseColor.ddt", "art/buildings/x/textures/x_mata_Normals.ddt"],
                              "2026-10-17 pkg-r1 (roof; abc1234)", reg_path, art)
    assert [d["after"] for d in changed] == [sha(b"colour r2"), sha(b"normals r2")] and skipped == []
    reg = TR.load(reg_path)
    s = reg["sets"][0]
    assert list(s)[:3] == ["id", "status", "record"] and s["record"] == "2026-10-17 pkg-r1 (roof; abc1234)"
    assert TR.drift(reg, art) == []
    assert reg_path.read_bytes() == (json.dumps(reg, indent=1) + "\n").encode()
    # already pinned: no change, no second record
    assert TR.pin([tex / "x_mata_BaseColor.ddt"], "2026-10-18 again", reg_path, art) == ([], [])
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r3")
    TR.pin([tex / "x_mata_BaseColor.ddt"], "2026-10-18 pkg-r2", reg_path, art)
    assert TR.load(reg_path)["sets"][0]["record"] == "2026-10-17 pkg-r1 (roof; abc1234) + 2026-10-18 pkg-r2"


def test_pin_refuses_unregistered_and_retired_pages_and_an_empty_record(mod):
    reg_path, art = mod / "tools" / "texture_sets.json", mod / "art"
    tex = art / "buildings" / "x" / "textures"
    (tex / "x_new_BaseColor.ddt").write_bytes(b"new")
    before = reg_path.read_bytes()
    with pytest.raises(KeyError):
        TR.pin([tex / "x_new_BaseColor.ddt"], "2026-10-17 pkg", reg_path, art)
    with pytest.raises(ValueError):
        TR.pin([tex / "x_old_BaseColor.ddt"], "2026-10-17 pkg", reg_path, art)
    with pytest.raises(ValueError):
        TR.pin([tex / "x_mata_BaseColor.ddt"], " ", reg_path, art)
    assert TR.pin([tex / "x_new_BaseColor.ddt"], "2026-10-17 pkg", reg_path, art, only_registered=True) == \
        ([], ["buildings/x/textures/x_new_BaseColor"])
    assert reg_path.read_bytes() == before


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=", *args], check=True, capture_output=True)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")
def test_the_staged_check_refuses_an_install_without_a_repin(mod):
    (mod / "tools" / "texture_registry.py").write_bytes((K / "tools" / "texture_registry.py").read_bytes())
    spec = importlib.util.spec_from_file_location("tr_copy", mod / "tools" / "texture_registry.py")
    tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tr)
    git(mod, "init", "-q")
    git(mod, "add", "-A")
    git(mod, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    tex = mod / "art" / "buildings" / "x" / "textures"
    assert tr.staged_findings(mod) == []
    (tex / "x_mata_Normals.ddt").write_bytes(b"normals r2")          # the install, registry untouched
    git(mod, "add", "art")
    bad = tr.staged_findings(mod)
    assert len(bad) == 1 and "x_mata_Normals" in bad[0], bad
    tr.pin([tex / "x_mata_Normals.ddt"], "2026-10-17 pkg", mod / "tools" / "texture_sets.json", mod / "art")
    git(mod, "add", "tools/texture_sets.json")
    assert tr.staged_findings(mod) == []
    # a pin that names other bytes than the staged file, and a retired page brought back
    reg = tr.load(mod / "tools" / "texture_sets.json")
    reg["sets"][0]["channels"]["BaseColor"]["sha256"] = "0" * 64
    tr.dump(reg, mod / "tools" / "texture_sets.json")
    (tex / "x_old_BaseColor.ddt").write_bytes(b"old again")
    git(mod, "add", "-A")
    bad = tr.staged_findings(mod)
    assert any("x_mata_BaseColor" in b for b in bad) and any("retired" in b for b in bad), bad


def test_the_hook_runs_the_staged_check():
    hook = (K / "tools" / "hooks" / "pre-commit").read_text()
    assert hook.startswith("#!/bin/sh") and "texture_registry.py\" check --staged" in hook
