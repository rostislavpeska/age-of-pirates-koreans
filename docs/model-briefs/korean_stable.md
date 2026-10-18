# korean_stable - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed GR2s (sha256 prefix):
  - `art/zbench_korean_military/stable/korean_stable_physics.gr2` 166c495eaa19
  - `_con.gr2` 815eaa8fb364
  - `_damaged.gr2` 42197c151dcc
- Installed mata (18 Oct 2026, committed 18 Oct with the Colonial roof commit; owner game test pending): BaseColor b2f4c68f, Normals a891a981, Masks 7d2b2a78.
  - Rollback: `C:/work/colonial-density-overnight-r1/rollback-installed-before/stable`.
- Port: `C:/work/colonial-density-overnight-r1/stable/port-installed/korean_stable_physics_INSTALLED_port_r1.blend`, sha 474acf0a, PASS, error 0.
  - Command: `--building korean_stable_physics --art-dir zbench_korean_military/stable`.
- The old pilot geometry is STALE (door and gable repairs). The adapter builds from the installed census and maps the pilot roof rows onto it by exact corners. Never use the pilot as the edit base.

## Pages and intended shares

- `korean_stable_mata` (own): every roof tile.
- `korean_shared_matc_r65`: the sloped faces read only plaster and wood swatch cells that every Korean building shares. Intended; no tiles.

## Owner decisions

- 18 Oct 2026 "Looks clean install ...": roofs at about .35 m (RearHall .3581 / hip .3443, StallWing .3519 / hip end .3586), module END on the eave fronts, texture only.

## Frozen

Geometry, UVs, GR2, Havok, r65.

## Known false positives

- `measure_tile_density.py`:
  - Reading: INCONCLUSIVE at .226 on the module page.
  - Why expected: a tool artifact. The INC-435 rhythm tool (branch `fix/inc-435-density-normal-rhythm`, not merged) measures 7/7 roofs at .3441–.3587.
- Disc-to-tube phase on the candidate PNG: one side INCONCLUSIVE (ratio 1.031); the decoded DDTs pass 7/7.
- INC-432 face-normal gate: `0001_end` INCONCLUSIVE (too few bins).
- Alpha reader gate: 278 cut-out texels are held at the installed alpha where damaged fragments contradict intact ones. Expected.

## Open (owner choices from the overnight report)

- END depth fitted to the lips (discs about 14 % squeezed) vs .16 m.
- Edge-dust cross-roof marks (6 blobs; `C:/work/colonial-density-overnight-r1/stable/review/sheets/zoom_0462_cand_mark.png`).
