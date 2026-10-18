# korean_consulate - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed GR2s (sha256 prefix):
  - `art/buildings/korean_consulate/korean_consulate.gr2` d2e082f8bb57
  - `_con.gr2` 5df0f1cb4b2c
  - `_damaged.gr2` d133087e11fa
  - UVs c4r9i, add-on commit 6947ef8.
- Installed mata (r7b, 18 Oct 2026, committed 18 Oct with the Colonial roof commit; owner game test pending): BaseColor f486c9db, Normals 759d71ba, Masks 635eadb0.
  - Rollback: `C:/work/consulate-density-r7/rollback-installed-before`.
- Port: `C:/work/consulate-density-r7/port-installed/korean_consulate_INSTALLED_port_r1.blend`, sha 0b24e7c1, 18 Oct 2026, PASS, UV error 0.
  - Its `textures/` predate r7b.
  - Command: `--building korean_consulate --origin-x -6.4`; runtime→authoring is (-x - 6.4, -z, y).
- Authoring source: `C:/work/korean-civic-pair-claude/work/uv_c4r9i/Korean_Consulate_Monastery_UV_c4r9i.blend`. It holds the Monastery too (one source chain for two buildings).

## Pages and intended shares

- `korean_consulate_mata` (own): roofs, plaster, coping; protected valley-trim rectangle [220,1520,64,288].
- `korean_shared_matc_r65` and `korean_shared_props_r6` (matd): shared by every Korean building.

## Owner decisions

- 17–18 Oct 2026: roof on the reusable module, density .3365 m (9 rolls per the 3.028 m Main share), texture only (owner: "I only wanted to edit texture, no UV map, no new model").
- Back-slope faces 245/263/299/317 re-pointed to their owners (c4r9g rule). The eave strip under the cut-outs has its own UVs (c4r9i).

## Frozen

Geometry, UVs, GR2, Havok, the shared pages, the valley-trim rectangle.

## Known false positives

- Disc-to-tube phase:
  - Reading: the Main W north piece (`Main.Eave.-1.1`) reads INCONCLUSIVE (0.29 m, 0.85 periods, one disc).
  - Why expected: the piece is too short to measure a rhythm (gate fix 5bec0be).
  - Evidence: `consulate/seam-r2/final-r7b/DISC_TUBE_PHASE_*.json`.
- INC-432 per-face normal gate:
  - The thresholds were calibrated on this building.
  - The Consulate textures installed before 18 Oct (r6) FAIL it on the Main W fronts. That is a real defect, fixed in r7b, not a false positive.

## Open

- `texel_provenance_gate` FAILs on 3 hidden-share readers that were already present in r6 (ConnectedFields:63 share 7, Main.Eave.1.0:5 inner fascia). Owner decision pending; not yet known whether intended.
- The flag mast reads one 2-texel row at the edge of a shared wood-beam strip carrying edge-dust streaks, so the pole shows bands. Fix by a mast UV move (GR2 + damaged + Havok) or by cleaning the beam-edge texels: owner decision.
