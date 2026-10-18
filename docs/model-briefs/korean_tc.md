# korean_tc (Town Center) - agent brief

Written 18 Oct 2026 by civic-density (claude-opus-5.5). Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed (sha256 prefix):
  - `art/buildings/korean_tc/korean_tc.gr2` a8e3ef94c826
  - `_con.gr2` 91c460155795
  - `_damaged.gr2` fdbbe99183bf
  - `_damaged.hkt` 5b26350ee391
  - `textures/korean_tc_mata_{BaseColor,Normals,Masks}.ddt` e89777a5a59d / eccb6f225054 / ed34ac68f490; Details fe7959082d18
  - `textures/korean_tc_matb_{BaseColor,Normals,Masks}.ddt` 7430962854a7 / 4f8d7f18ff4e / 4809151ffddb
  - These are the 14 Oct retained-terminal roof (e67f7e6) plus the 14 Oct warm plaster on mata BaseColor (7b6d30e).
- Port: `C:/work/civic-density-r1/korean_tc-port/korean_tc_INSTALLED_port_r1.blend`, sha 2e82a2aa, 18 Oct 2026, PASS.
  - Position and UV error 0.
  - Faces: 16,593 intact, 89,045 damaged (of 89,122), 11,342 construction (of 11,346).
- The October specimen `C:/work/korean-colonial-roof-specimens-r1/town-center_RUNTIME_GEOM.npz` holds the installed
  triangles in the same order (UV error 0, materials equal), in the frame (−x + .692, z, y + 84.6). Its GROUPS ids
  (16 fields, 32 end receivers, 16 underlips) apply directly.
- The TC eaves are upturned: the eave line of each field is its downhill open boundary, not one vertex row.

## Pages and intended shares

- `korean_tc_mata` (own, 2048): 12 tile fields; walls, plaster, wood.
  - **Shared on purpose:** Houses A/B/C (intact, damaged, age0, age0_damaged), Barracks and Stable (intact, damaged)
    read it through one small ground prop (submaterial matd/matb). That is 41,961 texels at 2048, the same in all 16 GR2s.
  - Guard: `C:/work/civic-density-r1/korean_tc/guard/GUARD.npz` (+1 px = 46,793 texels). It does not overlap the TC roof fields.
- `korean_tc_matb` (own, 1024, **cut-out page**): 4 tile fields (2584-2587) and **all original tile ends and underlips**.
  - These strips form one shared atlas: the same strip texels are read by eaves of DIFFERENT roofs at different scales.
    Example: the band of 1833/1835/1845/1849/2583/2597 is read by fields 1837, 1839 and 2587.
  - The 14 Oct fields were each fitted to the shared art through their own UV scale.
- `korean_shared_matc_r65`, `korean_shared_props_r6_2`: shared; no tile rhythm (rhythm scope 18 Oct).

## Owner decisions

- 13 Oct 2026, "Yes, continue this direction", then "10/10": the TC reusable roof module (the original of the module
  used on every Korean roof since). The TC roof is the owner's look reference (per the parent session's brief); change
  only what the owner names ("improve, not replace").
- 14 Oct 2026, "Allow this texture-only exception": retained-terminal roof textures installed (e67f7e6).
- 18 Oct 2026: "Yes: start one session for Dock, Market and Town Center at about .35 m, texture only, the shared prop
  protected; one review in my Blender before install." Their tiles have "the opposite problem: too dense".

## Frozen

Geometry, UVs, GR2, Havok, r65, props, and every texel of `korean_tc_mata` that another building reads.

## Known false positives

- Shared-page / hidden-share checks on `korean_tc_mata`: the Houses, Barracks and Stable prop readers are an intended share. Protect them; do not "fix" them.
- Disc-to-row gate on the underlips: the cut-out phase gate (`civic_terminal_respace.py phase`) reads FAIL (about .48)
  on the underlips whether or not they are respaced: they are fully cut (alpha < 128 on every texel), so there is no
  cut-out phase to measure. Most end strips read INCONCLUSIVE for the same reason (cut-out resultant .00-.03). Measure
  the TC disc-to-row relation with `civic_terminal_respace.py phase_xcorr` (profile cross-correlation) instead.
  The underlips face out and down (n.z -.34 to -.47) and are hidden from the game camera.
- Shared-texel provenance on `korean_tc_mata`: the mirror-twin fields 249, 1518, 1519, 1838 read their twin's texels
  (305 triangles `shared_offset`). This is the installed design; it was not re-measured on the installed pages.

## Open

- 18 Oct evening, **r8 INSTALLED** (owner: "Town center is fine ... install"; registry pinned; not committed; owner game test pending): `C:/work/civic-density-r1/korean_tc/textures-staging-r8` (hand-over
  `C:/work/civic-density-r1/HANDOFF_fix_v.md`). It supersedes r3/r4.
  - Fixes the owner's "opposite rhythm": the old phase gates trusted a planned lattice that was half a row off.
    - Roof C (fields 1837/1839) and 1517 (+ its mirror 1519) field rows were moved by the measured offset.
    - The shared tile-end strip is kept.
  - Field normal X is negated back to the installed convention. Cause: the adapter GEOMETRY tangent opposes dP/du on
    every TC field triangle.
  - Gate: use the sign-safe `civic_terminal_respace.py disc_tube`, never `phase`/`phase_xcorr` alone.
    - r8 decoded: 46 PASS, 2 NOT_MEASURABLE.
    - Treat underlips 256/260 (coherence .13/.14) as `KNOWN`. They share every texel with the passing 244/246.
  - Guard: 0 changed.
- Census `READERS.npz` `uv_raw` is v-down (image row = v*N). Tools that raster it as v-up read mirrored texels.
- Superseded, kept as history: density pass 18 Oct, r3 **staged, not installed** (owner option (b), texture only):
  - Fields: r2 field run, rolls .338-.360 m. Tile ends: `tc_texel_respace.py composite` (one reader's mapping per
    shared texel, no averaging), `korean_tc/textures-staging-r3`.
  - Residual offsets: `korean_tc/gates/TERMINAL_XCORR_candidate_r3.json` and `RESIDUAL_PER_EAVE_r3.json`.
    Over .15 row: 1526 (roof 1517 end, about .17 on every interval) and the 1845 underlip (one interval).
  - The INC-439 stop rule refuses (cut-out phase gate on the underlips, see above). Review views are labelled FAILING.
  - Review: `C:/work/civic-density-r1/review/TC_REVIEW.blend`, `LIVE_PAGES_TC.json`, `renders_tc/`, labelled pairs in
    `sheets_tc/`, `TC_EAVES_CONTACT_SHEET.png`. Some eave cameras look from below (1842, 1844, 1846, 1848, 257, 2581,
    2590, 2592-2594) or at odd angles (246, 259, 260).
  - Proposed registry rows (not applied): `C:/work/civic-density-r1/korean_tc/REGISTRY_ROW_PROPOSED.json`.
  - The owner still chooses: (a) keep .27, (b) this candidate, (c) per-eave strip UVs (a GR2 change).
