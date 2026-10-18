# korean_monastery - agent brief

Updated 18 Oct 2026 by monastery-density. Owner decisions are quoted; only the owner changes them.

## Current model (edit base = the game)

- Installed GR2s (sha256 prefix):
  - `art/buildings/korean_monastery/korean_monastery.gr2` 5ae81ca0f8f2
  - `_con.gr2` 37ee2fec6a48
  - `_damaged.gr2` e0a2ccb329f2
- Installed mata (committed, bacae7f): BaseColor a64c47f9, Normals f0792a5d, Masks 06404b06.
- Port: `C:/work/monastery-installed-port-r1/port/korean_monastery_INSTALLED_port_r1.blend`, sha 7df88d64, PASS.
  - 53,003 faces, UV error 0.
  - Its `textures/` predate bacae7f.
  - Command: `--building korean_monastery --origin-x 6.4`; runtime→authoring is (-x + 6.4, -z, y).
- Authoring source: c4r9j in `Korean_Consulate_Monastery_UV_*` (shared chain with the Consulate). It is NOT the edit base for texture work.

## Pages and intended shares

- `korean_monastery_mata` (own).
- The pagoda shares texels across its D4 symmetry about (6.4, 0) on purpose. Mirror copies read the same texels, and the tier layouts are centred so the copies keep phase.

## Owner decisions

- 18 Oct 2026: "I only wanted to edit texture, no UV map, no new model". The c4r9h UV/geometry path was rejected.
- 18 Oct 2026: candidate B (rolls about .35), "all textures - normals and masks too, verification before you port textures to game"; installed and committed.
- Benchmark for the other buildings: the houses, "probably the most balanced ones".

## Frozen

Geometry, UVs, GR2, Havok; the c4r9h path (rejected).

## Known false positives

- `texel_provenance_gate`:
  - Reading: shared texels across the D4 copies.
  - Why expected: the intended symmetry share. Declare the mirrors (`declared_mirror`) and judge them by mirrored phase.
  - Evidence: `C:/work/korean-colonial-roof-specimens-r1/monastery/monastery_texel_provenance.py`.
- Reader-only charts in a transfer's FRAMES.json keep auto-fit first/pitch values. Use the tier's centred layout instead; otherwise the checks report false phase errors.

## Open

- None recorded.
