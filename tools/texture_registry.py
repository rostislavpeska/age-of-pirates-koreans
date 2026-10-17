#!/usr/bin/env python
"""Texture-set registry upkeep: every current channel in tools/texture_sets.json pins the installed DDT (INC-400).

AoP scripts/havok/texture_sets.py reads the registry (sets by revision; a binding takes its channels from ONE set). An
install that replaces a registered DDT re-pins that channel in the same change. Between 13 and 14 Oct 2026 nine installs
did not (41 channels in 15 sets), and tests/test_texture_sets.py reported only the first stale set.

    python tools/texture_registry.py check                    # every current channel against art/; exit 1 on drift
    python tools/texture_registry.py check --staged           # pre-commit: staged DDTs against the staged registry
    python tools/texture_registry.py pin --record "2026-10-17 <package> (<what>; <commit>)" art/.../x_Masks.ddt ...

pin takes the sha256 from the installed bytes and appends " + <record>" once to each set it changed; a file already
pinned is left alone. Unregistered files are an error unless --only-registered (then reported and skipped); a retired
set is never re-pinned. --registry / --art point pin and check at a staged copy (stage/tools, stage/art).
Callers: korean-buildings-blender research/Colonial_Roof_Rollout_22/recipes/zen_finish_release.py and
consulate_finish_delivery.py (install), consulate_valley_export.py (stage). Hook: tools/hooks/pre-commit.
Journal 2026-10-17-claude-opus-5.5-42, task KTC-442.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

K = Path(__file__).resolve().parents[1]
REGISTRY = K / "tools" / "texture_sets.json"
REGISTRY_REL = "tools/texture_sets.json"


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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="list every current channel whose installed DDT is not the pinned revision")
    c.add_argument("--staged", action="store_true", help="the commit being made (pre-commit hook)")
    p = sub.add_parser("pin", help="re-pin installed DDTs and record the install")
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--record", required=True, help='"<date> <package> (<what>; <commit>)", appended to each set record')
    p.add_argument("--only-registered", action="store_true", help="skip (and list) DDTs no set registers")
    for q in (c, p):
        q.add_argument("--registry", type=Path, default=REGISTRY)
        q.add_argument("--art", type=Path, default=K / "art")
    a = ap.parse_args(argv)
    if a.cmd == "check" and a.staged:
        bad = staged_findings()
        for line in bad:
            print("STALE", line)
        if bad:
            print("re-pin the installed files in the same commit:\n"
                  '  python tools/texture_registry.py pin --record "<date> <package> (<what>)" <ddt> ...')
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
