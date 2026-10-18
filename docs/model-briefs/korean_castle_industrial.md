# korean_castle_industrial (Industrial castle) - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed GR2s (sha256 prefix):
  - `art/buildings/korean_castle_industrial/korean_castle_industrial.gr2` 3cedd1b7c346
  - `_con.gr2` d9ebd4d753e2
  - `_damaged.gr2` 7e88d578431b
- Port (read-only, made for the Colonial castle share check): `C:/work/castle-density-r1/industrial-port/`, 18 Oct 2026, PASS.
  - Position and UV error 0.
  - Materials: mata, matb (own industrial pages), matc (r65), matd (= the Colonial castle page), mate, matz (damaged).

## Pages and intended shares

- `korean_castle_industrial_mata`, `_matb`: own (registry rows exist).
- Submaterial `matd` = `buildings/korean_castle/textures/korean_castle_mata_*`, **the Colonial castle page, on purpose**.
  - Intact: 2,306 triangles, mostly masonry.
  - Includes one 1.1 m curved tiled cap that the Colonial castle has too (same geometry, same UVs).
- `korean_shared_matc_r65`: shared by every Korean building.

## Owner decisions

- 18 Oct 2026 "both castles share some textures. It's on purpose". Any edit of the Colonial castle page changes this
  castle wherever matd reads. A Colonial-only edit must prove that every texel read by matd is unchanged.

## Frozen

Not part of the Colonial roof density pass (18 Oct): no texel read by matd may change in that pass.

## Known false positives

- Hidden-share checks on `korean_castle_mata`: the matd readers are an intended share, not a defect (see
  `korean_castle.md`).

## Open

- No density measurement for this castle's own roof pages yet.
