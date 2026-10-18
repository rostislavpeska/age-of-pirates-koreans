# korean_market - agent brief

Written 18 Oct 2026 by civic-density (claude-opus-5.5). Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed (sha256 prefix), 18 Oct 2026 night, **B3 corner ends** (not committed, not game-tested):
  - `art/buildings/korean_market/korean_market.gr2` ee3d6caf5d30 (was 508987b3fb43)
  - `_con.gr2` e89a02e175e0
  - `_damaged.gr2` 01be63cde41c (was 3c2187096c33)
  - `_damaged.hkt` 8b959eefb29c (unchanged: the moved damaged vertices stay inside their pieces' old hulls, worst 0.36 mm)
  - `textures/korean_market_mata_{BaseColor,Normals,Masks}.ddt` 2c340cab2f8e / c5377865e39a / b0661932282b (r4f); Details 5e7ce91c8570
  - `textures/korean_market_matb_{BaseColor,Normals,Masks}.ddt` ce9d36727ae7 / 11ce0a27c053 / 240adcaddf3f (B3 = r4f + tile
    ends baked to the tips + the r4f hole islands closed); Details cabb6c4613ad
  - UV contract `tools/gr2_lint/uv_contracts/korean_market_gr2canon_r2.json` (positions of matb/matc changed; every UV hash
    equal to r1). gr2_lint 38/0/0.
- Port: `C:/work/civic-density-r1/korean_market-port-r3/korean_market_INSTALLED_port_r1.blend`, sha 5b6aa461, 18 Oct 2026, PASS.
  - 100,221 faces in the blend (intact 38,168, damaged 48,601 of 48,603, construction 13,452).
  - Position and UV error 0.
  - Older ports (`korean_market-port`, `-port-r2`) are the 508987b3 model: do not edit from them.
- Port frame (−x, −z, y). The October packages use the frame (−x, −z − 21, y). The authoring file matches the game model on the roof pages only, so match frames on roof-page vertices.

## Pages and intended shares

- `korean_market_mata` (own, 2048): the upper parts of every tiled slope.
- `korean_market_matb` (own, 1024, **cut-out page**):
  - the lower eave bands of the same slopes, so each slope spans BOTH pages with one lattice;
  - the original round tile ends on the eave strips;
  - the thatched stall awnings (straw, not tiles).
- The Market "Eave" strip objects hold a thin **front band** plus fan pieces wrapping the rounded hip corners and
  undersides. Only the front band follows the row lattice.
- Mirrored and rotated sides share texels (Hall W reads E; Tower N/S/W read E; Stall, TowerSkirt likewise).
- `korean_shared_matc_r65`: the hip/verge woodwork reads generic grey plank swatches. `korean_shared_props_r6_2`: props.

## Owner decisions

- 14 Oct 2026: retained-terminal module roofs applied (eb88a7e).
- 18 Oct 2026, "So the benchmark are now the houses which are probably the most balanced ones" (roll about .35 m).
- 18 Oct 2026: "Yes: start one session for Dock, Market and Town Center at about .35 m, texture only, the shared prop
  protected; one review in my Blender before install." Their tiles have "the opposite problem: too dense".
- 18 Oct 2026 night, lifted corners: "None of these has anything. So at least you know you need to completely change the
  attitude" (the five texture-only approaches); then "Yes: prototype the geometry fix of the Market corner ends in a review
  copy (taper the strip ends like the Dock, tuck them under the ridge cap, tile ends to the tip). Show me before anything is
  exported."; "B is the right direction: refine it (fix the Hall NE fragment, the Stall ends and the Skirt)"; "Export B3";
  "Install the staged B3 into the add-on for a game test (copy the 5 changed files, pin the new contract and registry rows,
  build and pytest). Do not commit."

## Frozen

UVs, Havok, r65, props. Geometry: only the B3 strip-end shape the owner approved (32 eave-strip ends: top tapered to .75 where
strip-only, Stall/Skirt bottom raised, 5 mm under the ridge cap). Texture edits on mata/matb only with the owner's OK to install.

## Known false positives

- INC-439 `roof_rhythm_scope.py` with `--course-period .48`: FAIL on r65 sloped/vertical faces along hip and verge lines.
  - Scores are .25-.29; the faces read grey-wood plank swatches (`C:/work/civic-density-r1/scope/korean_market/r65_carriers_full.png`).
  - Agent judgment, not an owner decision: plank grain, not tiles. Row-rhythm-only scope PASS.
  - Only real when a change alters the course length.
- `roof_channel_consistency`: the INSTALLED mata FAILs (suspect gate). On matb it is INCONCLUSIVE ("no window fits"): the matb fields are thin curved bands.
- Density: a 5 m² matb surface reads .22 m by luma in every state. It is the thatched awning, not tiles.
- `face_normal_profile_gate` on mata: INCONCLUSIVE, because the strip faces live on matb.

## Open

- 18 Oct night, **B3 INSTALLED for a game test, not committed** (hand-over `C:/work/civic-density-r1/HANDOFF_market_corners.md`,
  staging and install plan `C:/work/civic-density-r1/market-corners/export/staging-B3/INSTALL_PLAN.json`, backup of the r4f
  files `.../export/backup_installed_before_B3`). Owner game test pending.
  - `KNOWN` for the test: tiny shards under the Tower tips (seen in the B3 review); the strip ends still show their own end-cap
    faces (geometry kept, only reshaped).
  - The tile ends at the tips are BAKED into matb under the faces' own UVs (the GR2 shares those vertices, so a UV remap would
    need vertex splits): 34,104 texels; 2,490 texels other faces read were held.

- 18 Oct evening, **r4f INSTALLED** (owner: "market too (original was also broken, so no regression)"; registry pinned; not committed; lifted corners still broken, session market-lifted-corners): `C:/work/civic-density-r1/korean_market/textures-staging-r4f` (hand-over
  `C:/work/civic-density-r1/HANDOFF_fix_v.md`). It supersedes r4c/r4d/r4e.
  - Fixes the ragged Hall roof corners: matb has 16,254 field-scope texels read only by corner/end pieces in the game,
    now back at installed values. The four Hall corner close-ups match installed.
  - Disc-to-tube (sign-safe): 14/14 PASS on the decoded pages.
  - `KNOWN`, not a candidate defect: the jagged white teeth under the Tower roof's west corner are in the installed
    page too.
  - Still open: the Stall corners seen from below show the moved tile ends running into the corner fan.
    - Those texels are shared with the eave band, so there is no texture-only split.
    - An end-zone restore was tried and rejected (.38-row end windows).
- Superseded: density candidate staged 18 Oct (`C:/work/civic-density-r1/review/REVIEW.md`): .348-.367 m, not installed.
  - The **Tower roof is unchanged** (its strips failed the disc-to-row gate).
  - Hall N/S and Stall strips are INCONCLUSIVE.
  - **A gap at the Hall south-west eave corner** in the close-up is not explained.
  - Owner review pending.
