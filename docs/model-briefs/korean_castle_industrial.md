# korean_castle_industrial (Industrial castle) - agent brief

Updated 18 Oct 2026 by monastery-density, industrial-castle-density (green roof install) and the Havok hull refit
session. Owner decisions are quoted;
only the owner changes them.

## Current model (edit base = the game)

- Installed 18 Oct 2026 (sha256 prefix), uncommitted at the time of writing:
  - `art/buildings/korean_castle_industrial/korean_castle_industrial.gr2` ccc3509b898f (eave strips lifted 20 deg)
  - `_damaged.gr2` 0adab616c3a9 (strip fragments lifted the same way)
  - `_damaged.hkt` f6197e20c102 (collision hulls of the 37 lifted strip bodies refit; installed later the same day on
    the owner's yes, see "Havok hull refit" below)
  - `_con.gr2` d9ebd4d753e2 (unchanged)
  - `textures/korean_castle_industrial_mata_{BaseColor,Normals,Masks}.ddt` 8fd23a196b11 / 507395ee5270 / 9985d38af19d
  - `textures/korean_castle_industrial_matb_{BaseColor,Normals,Masks}.ddt` 86d30c731bc2 / 5ae1f24c2eb3 / be4f02e5d9c1
  - Details pages, .material files and animfile unchanged.
  - Roof roll density .344 / .351 / .362 m (lower skirt / middle skirt / hip roof; was .377 / .375 / .395).
  - Before this install: GR2 3cedd1b7 / damaged 7e88d578 / hkt 7d74127530ef; pages b1afb635 cdb55d62 93215ec0 /
    5b2f5f67 c63c4051 f338461827fa (rollback copy `C:/work/industrial-castle-density-r1/rollback-before-green/`, and
    git HEAD).
- Port of the installed files (current edit base): `C:/work/industrial-castle-density-r1/port-installed-green/` sha
  a63aa42ec750, 18 Oct 2026, PASS (`port_installed_building_r1.py --building korean_castle_industrial --origin-x 0`):
  intact 24,046 / damaged 46,974 / construction 10,808 triangles; every state binds the pages above.
  - Materials: mata, matb (own industrial pages), matc (r65), matd (= the Colonial castle page), mate (shared guardians),
    matz (damaged).
- gr2_lint (`--profiles tools/gr2_lint/profiles.json`): korean_castle_industrial 40 PASS, _con 18 PASS; UV contract
  `tools/gr2_lint/uv_contracts/korean_castle_industrial_r2.json` (r1 + the lifted strip positions; UVs unchanged).
- Registry: both page sets re-pinned (`tools/texture_registry.py check`: matches).

## Pages and intended shares

- `korean_castle_industrial_mata`, `_matb`: own (registry rows exist).
- Submaterial `matd` = `buildings/korean_castle/textures/korean_castle_mata_*`, **the Colonial castle page, on purpose**.
  - Intact: 2,306 triangles, mostly masonry.
  - Includes one 1.1 m curved tiled cap that the Colonial castle has too (same geometry, same UVs).
- `korean_shared_matc_r65`: shared by every Korean building.
- `korean_shared_guardians_r14` (mate, 512, the jade figures): read only by this castle today, but made as the standard
  jade page for other buildings (owner 12 Oct: "use them everywhere"). Untouched by the green install.
- Roof tiles: fields on mata; every eave-front tile-end strip, ridge, hip and cap tube on matb (own pages).

## Owner decisions

- 18 Oct 2026 "both castles share some textures. It's on purpose". Any edit of the Colonial castle page changes this
  castle wherever matd reads. A Colonial-only edit must prove that every texel read by matd is unchanged.
- 18 Oct 2026 (style trial seen in Blender): "Love the rift lift. use it for Industrial castle and lock the rift lift to
  Industrial buildings guidelines". Eave-front strips lifted 20 deg outward about their top edge (about 100 deg to the
  roof end). Rule: korean-buildings-blender `patterns/korean/sets/industrial/roofs.md`.
- 18 Oct 2026, colour choice after in-game test beds and the 4-castle Blender review: "Green, install to the game ans
  let's use the jade green roof as canonical color reference for Industrial age roofs"; "simply use the new castle model
  (export havok destruction and _damaged model and the green texture ... So basuiically the green variant design from
  test bed as final version". Installed = the green test bed byte for byte (roof density r1 + variant B of
  `variants-r4`: green glaze, varied tiles, every ridge/hip/cap/eave tile end graded like the field). Canonical colour:
  the guideline section "Roof colour: jade-green glaze".
- 18 Oct 2026 on the guardians: "Do NOT touch jade guardians"; asked again, the owner chose "Leave as installed". The
  stronger jade of the test beds was not installed.
- 18 Oct 2026: "remove the new test beds. Castle will only keep original test bed and the generic Castle unit with
  Korean designs". The four roof benches (22030-22033) are removed (protos, strings, buttons; art moved to
  `C:/work/industrial-castle-density-r1/removed-roof-benches/`). Kept: zzTESTKoreanCastleIndustrial (loads this
  production animfile) and the castle unit.

## Frozen

- The roof colour (jade-green glaze) and the eave lift, unless the owner reopens them.
- Not part of the Colonial roof density pass (18 Oct): no texel read by matd may change in that pass.

## Known false positives

- Strip phase gate (cut per tube) on the decoded roof pages: lower skirt E/N window 12 reads .101 (limit .10); the
  window's cut-out profile matches the earlier one with zero shift; weak circular-mean signal (strength .14).
- Roof variant matb encode (`industrial_encode_verify.py`): verdict FAIL from 43-50 BaseColor / 40 Masks / 8 Normals read
  texels outside the scope at the lower-skirt corners (block codec on mixed 4x4 blocks), the same in r2, r3 and r4.
- `industrial_tube_clean_check.py ddt`: mata "MISSED" texels (B 25, clusters of 3-7) are codec rounding of a small
  darkening; every one sits in a re-encoded block. Its mata near-original test is not valid; use
  `industrial_tube_colour_table.py`.
- Green roof end caps read 7 % lighter than the field grade: the deliberate per-tile filter (before it: .680 vs .679).
- gr2_lint `texel_density` prints a fragmentation note (323 / 478 islands per 100 u2 above a proposed 200): information,
  not a FAIL.
- Hidden-share checks on `korean_castle_mata`: the matd readers are an intended share, not a defect (see
  `korean_castle.md`).
- `lift-r1/LIFT_VERIFY.json` `havok_hull_exceedance` (0.25-8.6 m outside): a frame artefact. It compared raw GR2
  positions with HKT world directly. This castle's frame is HKT = 1.024 * raw[z, y, x] (export recipe; recalibrated
  18 Oct on the 112 unmoved convex bodies: 100 % of render vertices inside their hulls, naive frame 13.6 %). The add-on
  lint profile has no `hkt_pairing` block, so gr2_lint does not test hull containment for this castle; use
  `L.check_hkt` with axis map [2, 1, 0], scale 1.024 (as `industrial_hkt_refit.py` and
  `korean-industrial-runtime-r1/check_hkt_runtime.py` do).
- The `.hkt` holds unreferenced shape records: 174 from the first donor refit, plus the 37 pre-lift strip hulls that
  the 18 Oct refit replaced. The export recipe appends new hulls and repoints the bodies. Not a defect.

## Open

- Owner game test of the installed green castle (intact, construction, destruction). In destruction, also check
  that the lifted strip debris neither floats nor sinks (the hull refit below).
- Havok hull refit for the lift. Owner, 18 Oct 2026: "Yes, install the staged refit .hkt into the add-on". Installed
  over 7d74127530ef; not committed:
  - File: `C:/work/industrial-castle-density-r1/hkt-refit-r1/korean_castle_industrial_damaged.hkt` f6197e20c102 (the
    installed copy is identical).
  - Tool: `C:/work/industrial-castle-density-r1/tools/industrial_hkt_refit.py` (journal 2026-10-18-claude-opus-5.5-115
    / -118); QA in `REFIT_QA.json` there.
  - What it does: the export recipe's own hull step (`korean-industrial-runtime-r1/fracture-r1/export_damaged.py`) run
    on the lifted render of the 37 bodies whose vertices moved. That step rebuilds all 40 listed installed hulls from
    the pre-lift GR2 exactly.
  - Not refit: `roof_stone_solidhull_2`, `_hang_11`, `_hang_19`. They are listed in LIFT_QA, but none of their vertices
    moved, so their bytes are kept.
  - Containment (37 bodies, lifted render): inside the installed hulls .950 (max 4.3 cm out); inside the refit hulls
    1.000 (1 cm margin). Both pass the .05 tolerance. The other 115 bodies are unchanged.
  - Kept: mass, inertia and COM. The old COM lies inside every new hull, at most 3.7 cm from the new box centre.
  - Changed: `objectRadius`, which grew on 13 bodies.
  - Every other old byte, the body order, names, properties, pivots and the TYPE section are unchanged.
  - After install:
    - gr2_lint on the folder exits 0 (40 PASS).
    - `L.check_hkt` with the recipe frame PASS: farthest vertex .004 m outside, on the unrelated flagpole (.039 m on
      a strip body before the refit).
    - Add-on pytest: 87 passed, 2 xfailed.
  - Rollback: `rollback-before-green/korean_castle_industrial_damaged.hkt` (7d74127530ef), or git HEAD.
- The add-on's zzTESTKoreanCastleIndustrial shares id/dbid 22023 with zpKoreanLancer in git HEAD; a fix (bench to 22034
  + duplicate-id test) waits uncommitted on branch `claude/practical-nobel-6a8fac`.
