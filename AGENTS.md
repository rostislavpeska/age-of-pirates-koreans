# Koreans add-on: agent instructions

This repository is the Koreans civilization add-on for Age of Pirates (AoP) and its **single source of truth**
(owner, 2026-10-08: "One source of truth!!! NEVER TWO!!!").

1. **Edit Korean content only here.** Never create a copy, mirror, source folder or export of it in AoP or anywhere
   else, unless the owner explicitly requests a merge and confirms it. AoP's guard test
   `scripts/tools/tests/test_no_korean_civ_in_aop.py` fails on Korean civ records in AoP.
2. **Skills live in AoP**, never here: every skill, even one created while working in this repo, goes into AoP's
   `.claude/skills/` (the canonical library) and holds the generic method only. **Korean-specific documentation
   stays in the Korean repositories** (this repo: README, AUDIT; korean-buildings-blender: plan and research), never
   in AoP. Read the relevant skills in AoP (`aoe-xml`, `aoe3de-soundsets`, `bar-extract` ...) before editing.
   Record lessons in AoP's shared journal (`workflow-journal` skill).
3. **AoP's AGENTS.md rules apply here too** (CRLF runtime XML, XMB twins, never copy vanilla assets, owner approval
   for deletions, screen control announced, incidents reported). Read `../age-of-pirates/AGENTS.md`.
4. **Workflow:** edit `art/ data/ game/ sound/` (soundset definitions in `tools/korean_soundsets.xml`), then
   `python tools/build.py`, `python -m pytest tests -q`, game test, commit. Never hand-edit the files
   `tools/build.py` generates (listed at its top).
5. **Text is English only**; the build copies it to every language. Only rewrites of original-game strings are
   translated.
6. Ids: protos 22000-22999, tech dbids 60000-60999, strings 600000+. Open work and debts: [AUDIT.md](AUDIT.md).
   Design plan: korean-buildings-blender `research/Koreans_Civ_18/PLAN.md`.
