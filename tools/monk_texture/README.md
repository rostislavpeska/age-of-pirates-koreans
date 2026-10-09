# Korean monk texture recipe

The Korean monk's rider textures (`art/units/korean_monk/textures/korean_monk_rider_matA_{BaseColor,Normals,Details}.ddt`,
1024, DXT1) are the vanilla Shaolin Disciple's maps re-made after the WoL Jeobju (owner 2026-10-09): light grey-white
hanbok, mid-grey trousers, white leg wraps and socks, a red tie cord with teal beads at the collar crossing. The collar
band and sash keep the vanilla player-colour weight (Details R) and stay light, so the team colour shows; the weight
is cleared under the cord. The cloth normals lose the coarse weave; the Masks stay vanilla (referenced by path).

Rebuild (every intermediate in a scratch folder W, never in this repo):

1. Extract `art/units/asians/chinese/shaolin_disciple/shaolin_disciple_01.gr2` and its four `textures/*_matA_*.ddt`
   (AoP `bar-extract`), convert the GR2 to FBX (AoP `gxo-convert`).
2. `blender -b --factory-startup --python dump_uv3d.py -- disciple.fbx W/tris.json`
3. `python texmap.py W/tris.json W` (texture-space positions and UV islands)
4. Decode the vanilla BaseColor, Normals and Details DDTs to `W/base.png`, `W/van_Normals.png`, `W/van_Details.png`
   (keep the paths short: Blender on Windows cannot open image paths over 260 characters).
5. `python retexture_wol.py W` -> `W/korean_disciple_wol.png`, `..._Normals.png`, `..._Details.png`
6. AoP `scripts/havok/ddt_dxt1.py <png> art/units/korean_monk/textures/korean_monk_rider_matA_<Map>.ddt --size 1024`

The island numbers and the collar-crossing coordinates in `retexture_wol.py` belong to the vanilla Disciple's UV
layout; re-check them (`W/renders/islands.png`) if the vanilla model ever changes.
