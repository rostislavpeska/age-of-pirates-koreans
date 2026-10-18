"""tools/texture_registry.py: installs re-pin tools/texture_sets.json, and a commit that does not is refused (INC-400).

Between 13 and 14 Oct 2026 nine texture installs replaced registered DDTs without re-pinning them; 40 channels in 14 sets
went stale and the registry test reported only the first set. These fixtures use a two-set registry in tmp_path, so they
run without AoP.

    python -m pytest tests -q
"""
import importlib.util
import json
import os
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


# ---- the install note on the building's card (blendify-2#13) -------------------------------------------------------
REPO = "rostislavpeska/korean-buildings-blender"


def own_tool(mod):
    """the tool copied into the fixture mod, so the fixture registry is 'this add-on's own registry'"""
    (mod / "tools" / "texture_registry.py").write_bytes((K / "tools" / "texture_registry.py").read_bytes())
    spec = importlib.util.spec_from_file_location("tr_own", mod / "tools" / "texture_registry.py")
    tr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tr)
    return tr


class FakeBoard:
    """the surface of Blendify board.py the install uses; records the post instead of reaching GitHub"""
    BoardError = RuntimeError

    def __init__(self, fail=None):
        self.posts, self.fail = [], fail

    def post(self, issue, note, title, evidence, stage, checks=None):
        if self.fail:
            raise self.BoardError(self.fail)
        self.posts.append(dict(issue=issue, note=note, title=title, evidence=evidence, stage=stage, checks=checks))
        return {"comment": "https://github.com/x/y/issues/4#issuecomment-1"}

    def report(self, res):
        print("NOTE POSTED", res["comment"])

    @staticmethod
    def receipt_verdict(path):
        return all(r["status"] == "PASS" for r in json.loads(Path(path).read_text())["results"]), "read"


def test_an_install_into_this_registry_must_name_its_issue(mod, capsys):
    tr = own_tool(mod)
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    before = (mod / "tools" / "texture_sets.json").read_bytes()
    with pytest.raises(SystemExit) as e:
        tr.main(["pin", "--record", "2026-10-18 pkg-r2", str(tex / "x_mata_BaseColor.ddt")])
    assert e.value.code == 2 and "--issue owner/repo#N" in capsys.readouterr().err
    assert (mod / "tools" / "texture_sets.json").read_bytes() == before


def test_the_install_note_names_the_version_and_asks_for_game_review(mod, monkeypatch, capsys):
    tr, board = own_tool(mod), FakeBoard()
    monkeypatch.setattr(tr, "board_module", lambda: board)
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    files = [str(tex / "x_mata_BaseColor.ddt"), str(tex / "x_mata_Normals.ddt")]
    assert tr.main(["pin", "--record", "2026-10-18 pkg-r2 (roof)", "--issue", f"{REPO}#8", *files]) == 0
    (p,) = board.posts
    assert p["issue"] == f"{REPO}#8" and p["stage"] == "Game review" and p["checks"]["installed_from"][0] is True
    assert "Installed in the game: 2026-10-18 pkg-r2 (roof). 2 texture file(s)" in p["note"]
    assert "1 of them changed by this install" in p["note"] and "gr2_lint" not in p["checks"]
    assert any(sha(b"colour r2")[:12] in e and e.endswith(" new") for e in p["evidence"])
    assert "NOTE POSTED" in capsys.readouterr().out


def test_a_lint_report_counts_only_for_this_add_on_and_only_all_pass(mod, tmp_path):
    lint = tmp_path / "LINT.json"
    gr2 = mod / "art" / "buildings" / "x" / "x.gr2"
    rows = [{"check": "crc", "status": "PASS"}]
    lint.write_text(json.dumps({"files": {"intact": str(gr2), "hkt": None}, "results": rows}))
    assert TR.lint_check(lint, mod / "art", FakeBoard())[0] is True
    lint.write_text(json.dumps({"files": {"intact": str(gr2)}, "results": rows + [{"check": "dll_read", "status": "SKIP"}]}))
    assert TR.lint_check(lint, mod / "art", FakeBoard())[0] is False
    lint.write_text(json.dumps({"files": {"intact": str(tmp_path / "elsewhere.gr2")}, "results": rows}))
    ok, why = TR.lint_check(lint, mod / "art", FakeBoard())
    assert ok is False and "outside" in why


def test_not_an_install_and_a_staged_copy_post_nothing(mod, monkeypatch, capsys):
    tr, board = own_tool(mod), FakeBoard()
    monkeypatch.setattr(tr, "board_module", lambda: board)
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    assert tr.main(["pin", "--record", "2026-10-18 re-pin", "--not-an-install", "registry drift (INC-400)",
                    str(tex / "x_mata_BaseColor.ddt")]) == 0
    assert "NO NOTE: registry drift (INC-400)" in capsys.readouterr().out
    (tex / "x_mata_Normals.ddt").write_bytes(b"normals r2")      # the real tool on a staged copy: not the game
    assert TR.main(["pin", "--record", "stage", "--registry", str(mod / "tools" / "texture_sets.json"),
                    "--art", str(mod / "art"), str(tex / "x_mata_Normals.ddt")]) == 0
    assert "NO NOTE: a staged copy" in capsys.readouterr().out and board.posts == []


def test_a_note_that_fails_keeps_the_pin_and_says_rerun(mod, monkeypatch, capsys):
    tr = own_tool(mod)
    monkeypatch.setattr(tr, "board_module", lambda: FakeBoard(fail="gh: error connecting to api.github.com"))
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    assert tr.main(["pin", "--record", "2026-10-18 pkg-r2", "--issue", f"{REPO}#8",
                    str(tex / "x_mata_BaseColor.ddt")]) == 5
    out = capsys.readouterr().out
    assert "THE INSTALL NOTE WAS NOT POSTED" in out and "rerun the same command" in out
    assert tr.drift(tr.load(mod / "tools" / "texture_sets.json"), mod / "art") == []


def blendify_board():
    root = os.environ.get("BLENDIFY_REPO")
    path = Path(root) / TR.BOARD if root else K.parent / "age-of-pirates" / TR.BOARD
    return path if path.is_file() and (path.parent / "fake_gh.py").is_file() else None


@pytest.mark.skipif(blendify_board() is None, reason="Blendify board.py with fake_gh.py not found (BLENDIFY_REPO)")
def test_the_install_reaches_the_building_card_through_blendify(mod, monkeypatch, capsys):
    """end to end offline: the real board.py and Blendify's fake gh; the task #8 note lands on the Market card #4"""
    state = mod / "gh_state.json"
    item = lambda i, n, stage=None: {"id": i, "content": {"number": n, "repository": REPO, "title": f"#{n}"},
                                     **({"stage": stage} if stage else {})}
    state.write_text(json.dumps({"items": [item("PVTI_4", 4, "Game review"), item("PVTI_8", 8)],
                                 "fields": [], "parents": {f"{REPO}#8": 4}}))
    monkeypatch.setenv("BLENDIFY_GH", str(blendify_board().parent / "fake_gh.py"))
    monkeypatch.setenv("FAKE_GH_STATE", str(state))
    monkeypatch.setenv("BLENDIFY_REPO", str(blendify_board().parents[4]))
    tr = own_tool(mod)
    tex = mod / "art" / "buildings" / "x" / "textures"
    (tex / "x_mata_BaseColor.ddt").write_bytes(b"colour r2")
    assert tr.main(["pin", "--record", "2026-10-18 pkg-r2", "--issue", f"{REPO}#8", str(tex / "x_mata_BaseColor.ddt")]) == 0
    s = json.loads(state.read_text())
    (c,) = s["comments"]
    assert c["issue"] == 4 and "(task #8)" in c["body"] and "2026-10-18 pkg-r2" in c["body"]
    assert "stays at **Game review**" in c["body"] and not s.get("edits")
    assert "STAGE KEPT Game review -> Game review" in capsys.readouterr().out
