# korean_barracks - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed GR2s (sha256 prefix):
  - `art/zbench_korean_military/barracks/korean_barracks_physics.gr2` e85dc88936bb
  - `_con.gr2` 4eaa561cfad9
  - `_damaged.gr2` 59cca27dd369
- Installed mata (18 Oct 2026, committed 18 Oct with the Colonial roof commit; owner game test pending): BaseColor c4c1826b, Normals e1bd2a1a, Masks 7a463091.
  - Rollback: `C:/work/colonial-density-overnight-r1/rollback-installed-before/barracks`.
- Port: `C:/work/colonial-density-overnight-r1/barracks/port-installed/korean_barracks_physics_INSTALLED_port_r1.blend`, sha 7c8fe427, PASS, error 0.
  - Command: `--building korean_barracks_physics --art-dir zbench_korean_military/barracks`; frame (-x, -z - 82.93268, y).
- The old pilot geometry equals the installed census (positions 5e-6 m, UVs exact). The adapter pairs eave fronts by shared edges (INC-433).

## Pages and intended shares

- `korean_barracks_mata` (own): every roof tile.
- `korean_shared_matc_r65`: the sloped faces read only plaster and wood swatch cells that every Korean building shares. Intended; no tiles.

## Owner decisions

- 18 Oct 2026 "Looks clean install ...": roofs at about .35 m (Hall .3574, Upper .360/.347, guard roofs .354, skirts .345), module END on the eave fronts, texture only.

## Frozen

Geometry, UVs, GR2, Havok, r65.

## Known false positives

- `roof_channel_consistency`:
  - Reading: FAIL on one window ([1824,1872]), a rotated chart where the pan/cover course repeat is 2.4.
  - Why expected: the main tool misreads that ratio. PASS with `--course-ratio 2.4` (INC-434, branch `fix/inc-434-channel-course-harmonic`, not merged).
- `measure_tile_density.py`: the old installed reading ".391" was mostly the upper roof covering the main roof in the projection (main roof about .374). Use the INC-435 rhythm tool (branch `fix/inc-435-density-normal-rhythm`) on module pages.
- Disc-to-tube phase: 6 sides INCONCLUSIVE and 4 not measurable (short spans). The fine-grid field check confirms the design pitch.
- INC-432 face-normal gate: `0815_end` INCONCLUSIVE (too few bins).
- Alpha reader gate: 425 cut-out texels are held at the installed alpha where damaged fragments contradict intact ones. Expected.

## Open (owner choices from the overnight report)

- END depth fitted to the lips (discs about 14 % squeezed) vs the module's .16 m.
- Guard-roof skirts: one pitch (.345) vs denser.
- Hall .3574 vs .3425.
- Edge-dust cross-roof marks (9 blobs).
- The GuardRoof S fronts face the Hall wall; only a grazing review view exists.
