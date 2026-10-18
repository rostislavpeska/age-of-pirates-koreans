# korean_dock - agent brief

Written 18 Oct 2026 by civic-density (claude-opus-5.5). Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed (sha256 prefix):
  - `art/buildings/korean_dock/korean_dock.gr2` 86ecbdd2790b
  - `_con.gr2` 35434a74d90c
  - `_damaged.gr2` efa661988e51
  - `_damaged.hkt` 9c22613ad741
  - `textures/korean_dock_mata_{BaseColor,Normals,Masks}.ddt` d060c2461efa / a0867692c877 / b0a5e6e33a98 (14 Oct retained-terminal roof, commit e67f7e6); Details 4ca743d9f946
  - `textures/korean_dock_matb_{BaseColor,Normals,Masks}.ddt` 1b0c6ef56875 / 5aff62903a33 / 752d4120c4e5
- Port: `C:/work/civic-density-r1/korean_dock-port/korean_dock_INSTALLED_port_r1.blend`, sha 03a8a59a, 18 Oct 2026, PASS.
  - 79,507 faces (intact 28,440, damaged 38,647, construction 12,420).
  - Position and UV error 0. Command: `--building korean_dock --origin-x 0`.
- Port frame (−x, −z, y). The October module packages use the frame (−x, −z + 22, y). Their GEOMETRY is the
  authoring triangulation, not the game's (INC-388). Map game triangles onto it by texels, not by ids:
  `C:/work/civic-density-r1/tools/civic_module_adapter.py`.

## Pages and intended shares

- `korean_dock_mata` (own, 2048, **cut-out page**): every roof tile field, AND the original round tile ends on the eave
  strips (authoring objects `Dock.Roof.<roof>.Eave.<side>`, vertical faces next to each field). The fields were fitted to
  those retained ends on 14 Oct (`roof-rollout/versions/retained-ports-r1/dock`, alignment in
  `morning-review-holds-r1/dock-alignment`). A density change must re-space the ends too (INC-439).
- Mirrored strips share all their texels: HallTop E/W and N/S, HallSkirt E/W and N/S.
- `korean_dock_matb` (own, platform page): no tiles.
- `korean_shared_matc_r65`, `korean_shared_props_r6`: shared by many buildings; no tile rhythm (rhythm scope 18 Oct).

## Owner decisions

- 14 Oct 2026, "Allow this texture-only exception": retained-terminal roof textures installed (e67f7e6).
- 18 Oct 2026, "So the benchmark are now the houses which are probably the most balanced ones" (roll about .35 m).
- 18 Oct 2026: "Yes: start one session for Dock, Market and Town Center at about .35 m, texture only, the shared prop
  protected; one review in my Blender before install." Their tiles have "the opposite problem: too dense".

## Frozen

Geometry, UVs, GR2, Havok, matb, r65, props. Texture-only edits on mata, and only with the owner's OK to install.

## Known false positives

- `roof_channel_consistency` on the INSTALLED mata: FAIL (Masks.R AO windows). It fails the accepted page, so treat it as a suspect gate. Candidate and decoded pages PASS.
- `texel_provenance_gate`: 1 `shared_offset` reader (triangle 5019, labelled HallTop_S_0).
  - It is a near-flat hip-corner triangle that reads E-side texels through the W mirror.
  - Its relation to the writer is a property of the layout, so the installed layout has it too.
- `measure_tile_density.py` misreads module pages (INC-435); use the INC-435 rhythm tool (installed .266-.279 m).
- Disc-to-row per interval (`civic_terminal_respace.py phase`): HallTop N/S have one composite interval at .20 pitch.
  The candidate copy skips an installed tube there (k*NI/NC), so this reading is INCONCLUSIVE, not a defect.

## Open

- 18 Oct evening, **r9f INSTALLED** (owner: "install Dock and TC to the game"; registry pinned; not committed; owner game test pending): `C:/work/civic-density-r1/korean_dock/textures-staging-r9f` (mata only;
  hand-over `C:/work/civic-density-r1/HANDOFF_fix_v.md`). It supersedes r9c/r9d/r9e.
  - Fixes the owner's dark wedges under the upturned upper-roof corners: 5,111 field-scope texels are read in the game
    only by corner/end pieces. They get the installed value back (`tools/civic_game_reader_restore.py`).
  - Do not use r9d/r9e: their corner restores read the census UVs upside down.
  - Disc-to-tube (sign-safe `disc_tube`): 14/14 PASS on the decoded pages. matb untouched (the masonry session owns it).
- Superseded: density candidate .340-.363 m staged 18 Oct (`C:/work/civic-density-r1/review/REVIEW.md`), not installed.
  - Owner review pending.
  - Shelter N eave has no clear review camera.
  - Damaged-state rigidity of the debris reading changed texels is not checked.
