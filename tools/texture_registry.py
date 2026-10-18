#!/usr/bin/env python
"""Texture-set registry upkeep: every current channel in tools/texture_sets.json pins the installed DDT (INC-400).

AoP scripts/havok/texture_sets.py reads the registry (sets by revision; a binding takes its channels from ONE set). An
install that replaces a registered DDT re-pins that channel in the same change. Between 13 and 14 Oct 2026 nine installs
did not (41 channels in 15 sets), and tests/test_texture_sets.py reported only the first stale set.

    python tools/texture_registry.py check                    # every current channel against art/; exit 1 on drift
    python tools/texture_registry.py check --staged           # pre-commit: staged DDTs against the staged registry
    python tools/texture_registry.py pin --record "2026-10-17 <package> (<what>; <commit>)" \
        --issue rostislavpeska/korean-buildings-blender#8 [--lint-json LINT.json] art/.../x_Masks.ddt ...

pin takes the sha256 from the installed bytes and appends " + <record>" once to each set it changed; a file already
pinned is left alone. Unregistered files are an error unless --only-registered (then reported and skipped); a retired
set is never re-pinned. --registry / --art point pin and check at a staged copy (stage/tools, stage/art).
A pin into this add-on's own registry is an install into the game (blendify-2#13): it names the building's issue with
--issue, and Blendify's board.py posts which version went in (the record and the pinned hashes) on the building's
card and keeps or moves the card to "Game review" (its checks: this install record, and a gr2_lint --json of the
installed model with every check PASS, --lint-json). Only the owner moves a card back or to Accepted. A re-pin that is
not an install (registry drift) says why with --not-an-install; a staged copy needs neither. board.py is found in
BLENDIFY_REPO, else through AoP's skill link. Exit 5: pinned, but the note was not posted (rerun the same command).
Callers: korean-buildings-blender research/Colonial_Roof_Rollout_22/recipes/zen_finish_release.py and
consulate_finish_delivery.py (install), consulate_valley_export.py (stage). Hook: tools/hooks/pre-commit.
Journal 2026-10-17-claude-opus-5.5-42, task KTC-442; install note: journal 2026-10-18-claude-opus-5.5-133.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

K = Path(__file__).resolve().parents[1]
REGISTRY = K / "tools" / "texture_sets.json"
REGISTRY_REL = "tools/texture_sets.json"
BOARD = Path(".claude") / "skills" / "blender-architecture-texturing" / "scripts" / "board.py"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path=REGISTRY):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(reg, path=REGISTRY):
    """the registry's own layout (indent 1, LF, final newline): a re-pin diff touches only the changed lines."""
    Path(path).write_bytes((json.dumps(reg, indent=1) + "\n").encode("utf-8"))


def ref(path, art_root):
    """art-relative channel path as the registry writes it: forward slashes, no .ddt, compared case-folded."""
    p = Path(path)
    if p.is_absolute():
        p = p.resolve().relative_to(Path(art_root).resolve())
    s = p.as_posix()
    s = s[4:] if s.lower().startswith("art/") else s
    return s[:-4] if s.lower().endswith(".ddt") else s


def channels(reg):
    """case-folded path -> (set, channel name, channel row)"""
    return {row["path"].lower(): (s, ch, row) for s in reg["sets"] for ch, row in s["channels"].items()}


def drift(reg, art_root, sha_of=None):
    """every channel of a current set whose installed DDT is missing or not the pinned revision"""
    sha_of = sha_of or (lambda rel: sha256(Path(art_root) / (rel + ".ddt")) if (Path(art_root) / (rel + ".ddt")).is_file() else None)
    out = []
    for s in reg["sets"]:
        if s["status"] != "current":
            continue
        for ch, row in s["channels"].items():
            got = sha_of(row["path"])
            if got != row["sha256"]:
                out.append(dict(set=s["id"], channel=ch, path=row["path"], pinned=row["sha256"], installed=got))
    return out


def pin(paths, record, registry=REGISTRY, art_root=K / "art", only_registered=False):
    """re-pin the named installed DDTs; returns (changed rows, skipped unregistered refs). Writes only on a change."""
    if not record or not record.strip():
        raise ValueError("pin needs --record: which install / package / commit produced these files")
    reg = load(registry)
    index = channels(reg)
    changed, skipped, touched = [], [], []
    for p in paths:
        r = ref(p, art_root)
        hit = index.get(r.lower())
        if hit is None:
            if only_registered:
                skipped.append(r)
                continue
            raise KeyError(f"{r} is not registered in {registry}: add its set first")
        s, ch, row = hit
        if s["status"] != "current":
            raise ValueError(f"{r} belongs to the {s['status']} set {s['id']}: a retired page is never re-pinned")
        f = Path(art_root) / (row["path"] + ".ddt")
        new = sha256(f)
        if new == row["sha256"]:
            continue
        changed.append(dict(set=s["id"], channel=ch, path=row["path"], before=row["sha256"], after=new))
        row["sha256"] = new
        if s["id"] not in touched:
            touched.append(s["id"])
    for i, s in enumerate(reg["sets"]):
        if s["id"] not in touched:
            continue
        if "record" not in s:      # placed after status, like the sets that have one
            s = reg["sets"][i] = {k: v for k, v in [("id", s["id"]), ("status", s["status"]), ("record", "")] + list(s.items())}
        s["record"] = (s["record"] + " + " if s["record"] else "") + record.strip()
    if changed:
        dump(reg, registry)
    return changed, skipped


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def staged_findings(repo=K):
    """pre-commit: each staged DDT of a current set equals the staged registry's pin, and each pin the commit changes
    names the staged bytes. Only the commit's own files are hashed, so drift elsewhere never blocks it."""
    try:
        reg = json.loads(git(repo, "show", ":" + REGISTRY_REL).decode("utf-8"))
    except subprocess.CalledProcessError:
        return []
    names = git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode("utf-8").split("\0")
    staged = {n[4:-4].lower() for n in names if n.lower().startswith("art/") and n.lower().endswith(".ddt")}
    if REGISTRY_REL in names:
        try:
            old = channels(json.loads(git(repo, "show", "HEAD:" + REGISTRY_REL).decode("utf-8")))
        except subprocess.CalledProcessError:
            old = {}
        staged |= {k for k, (_, _, row) in channels(reg).items() if old.get(k, (0, 0, {}))[2].get("sha256") != row["sha256"]}
    out = []
    for k, (s, ch, row) in channels(reg).items():
        if k not in staged:
            continue
        try:
            got = hashlib.sha256(git(repo, "cat-file", "blob", ":art/" + row["path"] + ".ddt")).hexdigest()
        except subprocess.CalledProcessError:
            got = None
        if s["status"] != "current":
            if got is not None:
                out.append(f"{row['path']}.ddt: the {s['id']} set is {s['status']}; its pages stay out of art/")
        elif got != row["sha256"]:
            out.append(f"{row['path']}.ddt ({s['id']} {ch}): staged {got and got[:12]}, registry pins {row['sha256'][:12]}")
    return out


def board_module():
    """Blendify's board.py, the one helper that talks to GitHub (blendify-2#13): BLENDIFY_REPO, else AoP's skill link"""
    root = os.environ.get("BLENDIFY_REPO")
    path = Path(root) / BOARD if root else Path(os.environ.get("AOP_ROOT") or K.parent / "age-of-pirates") / BOARD
    if not path.is_file():
        raise FileNotFoundError(f"board helper not found at {path}: set BLENDIFY_REPO to a Blendify checkout")
    spec = importlib.util.spec_from_file_location("blendify_board", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def installed_rows(paths, registry, art_root):
    """(art-relative ref, set id, channel, pinned sha256) of each named file the registry holds"""
    index = channels(load(registry))
    hits = [index.get(ref(p, art_root).lower()) for p in paths]
    return [(row["path"], s["id"], ch, row["sha256"]) for s, ch, row in filter(None, hits)]


def uncommitted(rels, art_root):
    """the HEAD commit of the add-on that holds art_root, and the installed files it does not hold at HEAD yet"""
    try:
        repo = Path(git(art_root, "rev-parse", "--show-toplevel").decode().strip())
        files = [str((Path(art_root) / (r + ".ddt")).resolve().relative_to(repo.resolve())) for r in rels]
        head = git(repo, "rev-parse", "--short", "HEAD").decode().strip()
        dirty = git(repo, "status", "--porcelain", "--", *files).decode().splitlines() if files else []
    except (ValueError, subprocess.CalledProcessError):        # art outside this repository: nothing to compare
        return None, None
    return head, [line[3:] for line in dirty]


def lint_check(report, art_root, BD):
    """(passed, why): gr2_lint --json of the installed model, every check PASS, and the linted files in this art/"""
    try:
        files = [f for f in (json.loads(Path(report).read_text(encoding="utf-8")).get("files") or {}).values() if f]
    except (OSError, ValueError, AttributeError) as e:
        return False, f"{report}: not a gr2_lint --json report ({type(e).__name__})"
    art = Path(art_root).resolve()
    where = [Path(f) if Path(f).is_absolute() else art.parent / f for f in files]    # gr2_lint run from the add-on root
    if not files or not all(p.resolve().is_relative_to(art) for p in where):
        return False, f"{Path(report).name} linted files outside {art}: lint the installed model"
    ok, why = BD.receipt_verdict(report)
    return ok, f"{why}; {report}"


def report_install(issue, record, paths, changed, registry, art_root, lint_json=None, BD=None):
    """the install note on the building's card: which version went in, card kept or moved to Game review"""
    BD = BD or board_module()
    rows = installed_rows(paths, registry, art_root)
    head, dirty = uncommitted([r[0] for r in rows], art_root)
    new = {d["path"].lower() for d in changed}
    state = ("Not committed yet." if dirty else f"Committed in the add-on ({head}).") if head else ""
    note = (f"Version now in the game: {record.strip()}. {len(rows)} texture file(s) of it are in the add-on "
            f"({len(new)} changed by this run). {state} "
            "Please play it at normal camera distance and say whether it looks right.")
    evidence = [f"{r}.ddt ({sid} {ch}) sha256 {sha[:12]}" + (" new" if r.lower() in new else "") for r, sid, ch, sha in rows]
    evidence.append(f"registry: {Path(registry).resolve()} ("
                    + ("record appended" if new else "already pinned, nothing appended") + f": {record.strip()})")
    if head:
        evidence.append(f"add-on commit {head}" + (f"; not committed: {', '.join(dirty)}" if dirty else ""))
    checks = {"installed_from": (bool(rows), f"{len(rows)} file(s) pinned in {Path(registry).name}: {record.strip()}")}
    if lint_json:
        checks["gr2_lint"] = lint_check(lint_json, art_root, BD)
    res = BD.post(issue, note, "Installed in the game", evidence, "Game review", checks=checks)
    BD.report(res)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="list every current channel whose installed DDT is not the pinned revision")
    c.add_argument("--staged", action="store_true", help="the commit being made (pre-commit hook)")
    p = sub.add_parser("pin", help="re-pin installed DDTs and record the install")
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--record", required=True, help='"<date> <package> (<what>; <commit>)", appended to each set record')
    p.add_argument("--only-registered", action="store_true", help="skip (and list) DDTs no set registers")
    p.add_argument("--issue", help="the building's issue, owner/repo#N: the install note goes on its card")
    p.add_argument("--lint-json", type=Path, help="gr2_lint --json of the installed model (a Game review check)")
    p.add_argument("--not-an-install", metavar="REASON", help="a re-pin of this registry that is not an install")
    for q in (c, p):
        q.add_argument("--registry", type=Path, default=REGISTRY)
        q.add_argument("--art", type=Path, default=K / "art")
    a = ap.parse_args(argv)
    own = a.cmd == "pin" and a.registry.resolve() == REGISTRY.resolve()
    if own and not (a.issue or a.not_an_install):
        ap.error("a pin into this registry is an install: name the building's issue with --issue owner/repo#N "
                 '(blendify-2#13), or say why it is not an install with --not-an-install "<reason>"')
    if a.cmd == "check" and a.staged:
        bad = staged_findings()
        for line in bad:
            print("STALE", line)
        if bad:
            print("re-pin the installed files in the same commit:\n"
                  '  python tools/texture_registry.py pin --record "<date> <package> (<what>)" --issue <owner/repo#N> '
                  '<ddt> ...')
        return 1 if bad else 0
    if a.cmd == "check":
        bad = drift(load(a.registry), a.art)
        for d in bad:
            print(f"STALE {d['set']} {d['channel']} {d['path']}: pinned {d['pinned'][:12]}, installed "
                  f"{(d['installed'] or 'missing')[:12]}")
        print(f"{len(bad)} stale channel(s)" if bad else "registry matches the installed files")
        return 1 if bad else 0
    changed, skipped = pin(a.paths, a.record, a.registry, a.art, a.only_registered)
    for d in changed:
        print(f"PINNED {d['set']} {d['channel']}: {d['before'][:12]} -> {d['after'][:12]}")
    for r in skipped:
        print(f"UNREGISTERED {r} (skipped)")
    print(f"{len(changed)} channel(s) re-pinned in {a.registry}")
    if not a.issue:
        print(f"NO NOTE: {a.not_an_install or 'a staged copy, not the game'}")
        return 0
    try:
        report_install(a.issue, a.record, a.paths, changed, a.registry, a.art, a.lint_json)
    except Exception as e:                                       # board.BoardError, a missing helper, gh missing
        print(f"PINNED, BUT THE INSTALL NOTE WAS NOT POSTED: {e}\n  rerun the same command (pinned files are left alone)")
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
