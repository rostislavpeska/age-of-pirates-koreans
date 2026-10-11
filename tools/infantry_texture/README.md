# Korean infantry: texture and hat recipe

The Korean infantry wear vanilla Chinese bodies with Joseon retextures (owner 2026-10-09): the Jochong Musketeer
(`zpJochong`) the Arquebusier's three bodies plus a jeollip modelled for the mod, the Jangchang Spearman
(`zpJangchang`) the Qiang pikeman's three bodies, the Gakgung Archer (`zpGakgung`) the Changdao's three bodies with the
Yumi's bow animations and the vanilla Azap short composite bow. Every runtime file below comes from these scripts; each step was
re-run and reproduced the shipped files byte for byte.

| Skin | Look | Own maps (1024, DXT1) | Vanilla maps by path |
|---|---|---|---|
| Jochong age 1 (base) | jeonbok vest in player colour over a white hemp coat, white baji, indigo haengjeon leg wraps | BaseColor, Details | Normals, Masks |
| Jochong age 2 (Disciplined) | + white beoseon socks, cream ties, darker leather bandoliers, indigo jeondae belt with its own relief | all four | - |
| Jochong age 3 (Honored, Exalted) | red dongdari sleeves, black jeondae; the Chinese breast mirror painted out (texture only) | all four | - |
| jeollip (512) | black felt dome and wide brim, brass jeongja knob, red sangmo horsehair; no player colour | BaseColor, Normals, Masks | - |
| Jangchang age 1 (Colonial base; the Qiang's fur-cap body 0 is not used) | the steel tugu helmet with red plume and mail kept; the round Qing badge on the back painted out | all four | - |
| Jangchang age 2w (Disciplined: the age 2 material's base parameters) | the studded dujeong-gap kept, studs brass, white sleeves, black jeondae; the front opening keeps the vanilla dark inner robe | BaseColor (`korean_jangchang_age2w`), Details (age 2's) | Normals, Masks |
| Jangchang age 2 (Honored, Exalted: material variant 1) | as 2w with red dongdari sleeves, gilt studs, a gilt rim band on the helmet bowl and a gilt cup under the red tassel (gilt metallic, roughness 0.35) | BaseColor, Details, Masks | Normals |
| Gakgung age 0 (base) | helmet with mail hood kept, coat in player colour, the Ming cloud-collar trims as black edging, the round chest mirror painted out, white sleeves and baji, indigo leg wraps | all four (BaseColor DXT5) | - |
| Gakgung age 1 (Disciplined) | + the red plume and the studded skirt (brass studs); the red armour lacing as an indigo jeondae | BaseColor (DXT5), Details | Normals, Masks |
| Gakgung age 2 (Honored, Exalted) | the armour kept (iron cuirass, lamellar bracers), brass studs, the chest mirror filled with cuirass; the gold Ming phoenix-wing ornament cut out (alpha 0) | all four (BaseColor DXT5) | - |

History: the Joseon soldier's jeollip (felt hat with a red tassel) or beonggeoji (plain felt hat), the tugu helmet
with a plume, the dujeong-gap (studded cloth armour), jeonbok (sleeveless vest) over a coat, dongdari (coat with red
sleeves), jeondae (belt), haengjeon (leg wraps). Vanilla shapes stay where they fit; Chinese or Qing cues that are only
paint go (owner: "resolve the upgrade only by reskin"): the Arquebusier's studded breast mirror (a taegeuk on it read as
the modern flag), the Qiang's back badge, the Changdao's chest mirror and its age 2 phoenix-wing ornament (a cut-out card:
its alpha set to 0, so the BaseColor is DXT5 like the vanilla Changdao's); the Qiang's chest piping and the Changdao's
cloud collar become black edging. The Chu Ko Nu bodies were not used: Qing frog-button jackets. Belts are real bands in the
Normals and Masks where the retexture adds them (owner: "for belts etc - edit also normals and masks maps"); never red
(a red belt vanishes on a red player).

## Rebuild

Every intermediate goes to a short scratch folder `W` (never this repo; Blender cannot open Windows paths over 260
characters). `<AoP>` is the Age of Pirates checkout; `<pose_sim>` = `<AoP>/.claude/skills/aoe3de-unit-animation/scripts`.

1. Extract into `W` (AoP `bar-extract`) the bodies - `art/units/asians/chinese/arquebusier/arquebusier_age1/2/3.gr2`
   (Jochong), `art/units/asians/chinese/qiang_pikeman/qiang_pikeman_age1/2.gr2` (Jangchang),
   `art/units/asians/chinese/changdao/changdao_0/1/2.gr2` (Gakgung) - with the four maps each
   of their `.material` names, and `art/units/spc/outlaws/bandido_hat.gr2`. Convert the GR2s to GXO (AoP `gxo-convert`,
   under Wine in WSL). Decode the maps to `W/ageN_{BaseColor,Normals,Masks,Details}.png` (one folder per unit).
2. `python texmap.py <pose_sim> W/<body>N.gxo W/ageN_BaseColor.png W/ageN`: texel -> 3D position, body part and UV
   island (`W/ageN_texmap.npz`, `W/ageN_islands.png` to check the islands).
3. `python retexture_jochong.py W N` (N = 1, 2, 3), `python retexture_jangchang.py W N` (N = 1, 2, 2w) or
   `python retexture_gakgung.py W N` (N = 0, 1, 2) ->
   `W/<unit>_ageN_{BaseColor,Details,Normals,Masks}.png` (+ `_blue`/`_red` previews, player colour multiplied in).
4. `python jeollip_model.py <pose_sim> W/bandido_hat.gxo W` -> `W/jeollip.obj`, `W/jeollip_{BaseColor,Normals,Masks}.png`
   and `jeollip_parts.json` here (the hat geometry in the engine frame of the vanilla bandido hat).
5. DDTs: `python <AoP>/scripts/havok/ddt_dxt1.py W/<unit>_ageN_<Map>.png
   art/units/korean_<unit>/textures/korean_<unit>_ageN_matA_<Map>.ddt --size 1024` for the own maps in the table, and
   `W/jeollip_<Map>.png` -> `art/units/korean_jochong/textures/korean_jochong_hat_matA_<Map>.ddt --size 512`; the
   Gakgung BaseColors with `--dxt5` (their cut-out cards: plume, hidden ornament).
6. `python tools/korean_infantry_model.py` (bodies + hat GR2), `python tools/build.py` (animfiles, materials, XMBs),
   `python -m pytest tests -q`.

Review renders (Blender in background, no GUI): `python obj_on_head.py <pose_sim> W/arquebusier_ageN.gxo W/jeollip.obj
W/on_ageN.obj`, then `blender -b --factory-startup --python render_obj.py -- W/turn.png W/<body>N.obj
W/<unit>_ageN_blue.png W/<unit>_ageN_Normals.png [W/on_ageN.obj W/jeollip_BaseColor.png W/jeollip_Normals.png]`
(the body OBJs: AoP `pose_sim.write_obj` of the GXO meshes).

## Proof of the hat GR2

`tools/korean_infantry_model.py` writes it with AoP `scripts/havok/multimaterial_gr2.py` (refuses orphan pointer
fixups, INC-187). AoP `scripts/havok/gr2_fixups.py art/units/korean_jochong/korean_jochong_hat.gr2` -> 0 orphans;
AoP `gr2_lint.dll_read` (the game's Granny DLL, wsl and native routes) -> PASS, one bound mesh of 364 triangles
(2026-10-09). The converter's GXO dump of appended meshes is no proof either way (it prints a garbage triangle-group
count for them while the DLL reads them). AoP's `gr2_editmesh.py` is not used: it leaves orphan fixups (INC-203).
