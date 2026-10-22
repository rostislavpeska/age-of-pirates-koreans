# Koreans add-on: agent instructions

This repository is the Koreans civilization add-on for Age of Pirates (AoP) and its **single source of truth**
(owner, 2026-10-08: "One source of truth!!! NEVER TWO!!!").

1. **Edit Korean content only here.** Never create a copy, mirror, source folder or export of it in AoP or anywhere
   else, unless the owner explicitly requests a merge and confirms it. AoP's guard test
   `scripts/tools/tests/test_no_korean_civ_in_aop.py` fails on Korean civ records in AoP.
2. **Skills live in their canonical owners**, never here (Blendify `docs/skill-system.md`, split of 13 October):
   generic 3D skills in Blendify, AoE3 integration and mod policy in AoP's `.claude/skills/`. A skill holds the
   generic method only. **Korean-specific documentation
   stays in the Korean repositories** (this repo: README, AUDIT; korean-buildings-blender: plan and research), never
   in AoP. Read the relevant skills in AoP (`aoe-xml`, `aoe3de-soundsets`, `bar-extract` ...) before editing.
   Record lessons in the shared diary (`workflow-journal` skill; Blendify `.local/JOURNAL.jsonl`).
3. **AoP's AGENTS.md rules apply here too** (CRLF runtime XML, XMB twins, never copy vanilla assets - except rule 2's
   retexture clone of a vanilla unit, shape untouched -, owner approval
   for deletions, screen control announced, incidents reported). Read `../age-of-pirates/AGENTS.md`.
4. **Workflow:** edit `art/ data/ game/ sound/` (soundset definitions in `tools/korean_soundsets.xml`), then
   `python tools/build.py`, `python -m pytest tests -q`, game test, commit. Never hand-edit the files
   `tools/build.py` generates (listed at its top).
5. **Text is English only**; the build copies it to every language. Only rewrites of original-game strings are
   translated.
6. Ids: protos 22000-22999, tech dbids 60000-60999, strings 600000+. Open work and debts: [AUDIT.md](AUDIT.md).
   Design plan: korean-buildings-blender `research/Koreans_Civ_18/PLAN.md`.
7. **Every Korean building ships with its test bed unit** (owner 2026-10-11: "test bed must always be part of the
   package"). In the same change that installs or changes a building model, add or update its `zzTEST<Name>` bench in
   the marked zzTEST block of `data/protomods.xml`: it loads the building's own Korean animfile directly (no civ/age
   logic), copies the vanilla unit's values (placement, physics, flags), sits on `zzTESTKoreanBuilderWagon`, and has
   its two strings. `tests/test_korean_test_beds.py` fails when a building in `tools/korean_visuals.py` has no bench,
   or a bench points at a missing animfile or model.
8. **Read the model's brief first** (owner 2026-10-18: "model must be refreshed from game", "Each model should have
   agent brief informing about decisions and possible false positives during tests"):
   - Briefs are in `docs/model-briefs/<model>.md`.
   - Work from a port of the installed game files, not an older source file. Refresh it after every install.
   - Treat the owner decisions quoted in the brief as settled.
   - Report a gate reading listed under the brief's known false positives as `KNOWN`, not as a new defect.
