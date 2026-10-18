# korean_castle (Colonial castle) - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed (sha256 prefix):
  - `art/buildings/korean_castle/korean_castle.gr2` 5d9c34511324
  - `_con.gr2` 75abaa0c9ba8
  - `_damaged.gr2` d02e70ef3fa0
  - `_damaged.hkt` bbd3c7fd46dc
  - `textures/korean_castle_mata_{BaseColor,Normals,Masks}.ddt` 10899ce26124 / ca8ed0fd34fd / a9ac5424b077 (18 Oct density pass)
  - `textures/korean_castle_matb_{BaseColor,Normals,Masks}.ddt` 9a2ceac7fc21 / ce46367d3e57 / 25a953774215 (18 Oct: eave tile-end strip respaced, final r2)
  - before 18 Oct (rollback `C:/work/castle-density-r1/rollback-installed-before`): mata f6a1c5ba / 2ce01a94 / a275509a
- Port: `C:/work/castle-density-r1/port-installed/korean_castle_INSTALLED_port_r1.blend`, sha b8064cda, 18 Oct 2026, PASS.
  - 44,087 faces (intact 9,216, damaged 28,355, construction 6,516).
  - Position and UV error 0.
  - Command: `--building korean_castle --origin-x 0`.

## Pages and intended shares

- `korean_castle_mata` (own): every roof tile, plus masonry.
  - **Shared with the Industrial castle on purpose.** Its submaterial `matd` is this page: 2,306 intact triangles, mostly masonry.
  - One object is shared with identical geometry and UVs: a 1.1 m curved tiled cap (14 triangles, about 2.1–2.6 m high), read by both castles (`C:/work/castle-density-r1/STEP0.md`).
- `korean_castle_matb` (own; not read by the Industrial castle):
  - sloped wood planks and iron-studded beams at 9.3–9.8 m;
  - **the round tile ends on the eave fronts** (vertical faces, so the 18 Oct step 0, which checked sloped faces only, missed them). They line up with the installed .379 m rows. A density change on mata must re-space them too, or they drift (castle-density-r1 REVIEW.md: about 8 of 23 rows per side out of step).
- `korean_shared_matc_r65` (shared by every Korean building): small wood/plaster swatches. No tiles.

## Owner decisions

- 18 Oct 2026 "both castles share some textures. It's on purpose": the Industrial castle reading this page is intended.
  Never "fix" the share. When editing this page, every texel the Industrial castle reads must stay unchanged, unless the
  owner asks for both castles to change.
- 18 Oct 2026 "Looks clean install and start the castle", then "Ok, edit game model then. It's texture only anyway":
  unlocked for the roof density pass (house benchmark ~.35 m), texture only. The shared cap is protected by default.
- Earlier, still valid outside that pass: "castle stays locked for now", "Both castle bakes remain locked", "preserve
  the approved castle r11 pattern".
- Approved roof look (add-on commits):
  - TC roof + caps C15 (70a5103), "only the Town Center's shading, roll stripes dominant" (e4d1bfc);
  - corner eave discs (b4a2508);
  - decorations (8fabe8f);
  - ArmorPaint roof effects (f13a989);
  - Zen normals (a3ed928).
  Change only what the owner names.

## Frozen

Geometry, UVs, GR2, Havok, the Industrial castle's texels on this page, r65. matb: frozen except the eave-front tile-end strips, and those only with the owner's OK.

## Known false positives

- Shared-page / hidden-share checks (texel provenance, step-0 share checks):
  - Reading: Industrial castle readers of `korean_castle_mata` (matd, 2,306 intact triangles) and the tiled cap overlap (2,368 texels at 1024).
  - Why expected: an intended share (owner 18 Oct).
  - Evidence: `C:/work/castle-density-r1/SHARED_PAGE_CHECK.json`, `SHARED_PAGE_mata.png`.
- Density with `measure_tile_density.py` on sloped mata: castle rolls .379 m (two slopes, 25°). Read module-made pages
  with the INC-435 rhythm tool as well (the contract tool misreads them).

## Open

- Registry rows `korean_castle_mata` and `korean_castle_matb` added 18 Oct with the density install.
- gr2_lint pins of this page (AO acceptance, the Industrial castle's shared-page permission) re-pinned 18 Oct under the owner's words "The castle eave looks right now".
- Roof density: installed 18 Oct (rolls .344, tile ends respaced); owner game test pending. Work and evidence: `C:/work/castle-density-r1/`.
