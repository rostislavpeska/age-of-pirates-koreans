# Koreans v1 - honest audit (2026-10-08)

Version 1 is a Japanese clone with a Korean identity layer. This lists what is done, what is verified where, and
everything still missing for a fully playable, fully Korean civilization, most important first.

## Done

| Part | State | Verified |
|---|---|---|
| Civ `zpKoreans` (lobby + editor, hotkey K) | vanilla Japanese entry field for field, own name/rollover | owner's match 2026-10-08: civ picked, match started |
| Age0 tech `zpAge0Korean` | activates `YPAge0Japanese` + marker `zpKoreanVisuals` | same match (Japanese start, Korean TC appeared) |
| Flags (object flag, lobby/HC/legacy buttons, icon, techtree, both postgame flags) | Korean Empire flag through the owner's Flag Maker templates | in-game flag on the TC panel and player list seen; postgame/HC not yet seen |
| Korean Town Center, Barracks, Stable | from the first upgrade (Colonial) on; Discovery Age keeps the vanilla Asian look | TC seen in game (before the age fix); Barracks, Stable and the age switch not yet seen |
| Home city | Japanese scene and cards, named Hanseong, hero Samyeong Daesa | static only |
| AI personality | Empress Myeongseong (name, tooltip) | static only |
| Asian villager `ypSettlerAsian` speaking Korean | replaces the Japanese villager (`zpKoreanUnits`; civ entry, 6 starting and 13 Empire Wars villagers); hunts and herds; 20 Korean voice choices wired in `sound/ypsettlerasian_snds.xml` (`tools/korean_sounds.py`) | offline only (tests); not yet seen in game |
| Korean villager voices | 34 lines, 22 soundsets; the 20 villager sets wired to the Asian villager; the 2 fishing-boat sets on the Asian fishing boat and the male villager Select/Acknowledge on the 49 wagon sound files and the military rickshaw (builds Barracks and Stable; owner 2026-10-09: "no sound") that give the Japanese a voice (owner 2026-10-09: "same as Japanese wagons", "no new soundsets, only reuse"): a zpKoreans choice after every Japanese one, Japanese voices as their Korean twins, the Dutch/Russian voices the game gives Japanese consulate and DLC wagons kept (`tools/korean_sounds.py`) | files, definitions and wiring checked offline (`test_korean_wagons_and_fishing_boats_speak_like_the_japanese_ones`); not yet heard in game |
| Korean House "Hanok" `zpHouseKorean` (22000) | replaces the Shrine: standard-house values, refuge for 3 villagers or infantry (town bell; 5 was too strong, owner 2026-10-09), arrows only while occupied from Colonial (`zpKoreanBuildings`, `zpKoreanHouseArrows`); look `art/buildings/korean_house/korean_house.xml` (2026-10-09): the vanilla Shrine age 1 in the Discovery Age, Korean House A/B/C from the Colonial Age on (owner: "Colonial on; Shrine in Discovery"), each with its small garrison mast (flag at 0.7 scale), an own last construction stage (p66) and Havok destruction on the vanilla shrine body graph; added to every villager's build menu in the Shrine's slot by `CommandAdd` (page 6, column 0) | owner's tests: 2026-10-08 the Hanok appeared in the villager menu (first route `AddTrain` put it alone in the top row, replaced by `CommandAdd`); 2026-10-09 refuge worked (5 inside), arrows never fired - the Colonial tech was never armed, fixed (`zpKoreanBuildings` sets it obtainable); capacity cut to 3. Slot and arrows to re-check. Korean House model: offline gates only - `gr2_lint` 6 profiles 0 FAIL / 0 SKIP (`tools/gr2_lint/profiles.json`, Granny DLL both routes), state frames, UV contracts, tests; not yet seen in game (checklist below) |
| Korean monks `zpMonkKorean`, `zpMonkKorean2` (22001-22002) | mounted explorers on the vanilla Manchu horse archer model (placeholder, Manchu icons); Japanese monk explorer rules without stealth or sabotage, cavalry types; build Town Center, Trading Post, Hanok; retrained in the Town Center's monk slots; Korean soldier voices (AoP soundsets); animfiles and tactics generated (`tools/korean_monk.py`); treasure pickup, build and smoke bomb animations from vanilla General Kichiro (horse and rider pair) | owner's test 2026-10-09: the monk stood still while building and picking up treasure (Idle copies) - fixed with the Kichiro animations, guarded by `test_every_tactics_animation_exists_and_moves`; to re-check in game. Final unit (owner 2026-10-09): the vanilla Shaolin Disciple on the yabusame rider skeleton (`art/units/korean_monk/korean_monk_rider.gr2`, `tools/korean_monk_model.py`, AoP `gr2_reskeleton.py`) on the vanilla yabusame horse; riding confirmed in the owner's game test ("Works!"), arrow sync fixed (Manchu archer's tuned horse attacks); hero cavalry selection (Elmeti decal); heal from the Lakota war chief; retextured after the WoL Jeobju (own 1024 BaseColor/Normals/Details, vanilla Masks; collar band and sash keep the team colour; recipe `tools/monk_texture/`). The riding bench was removed. To check in game: look, team colour, heal, build, pickup. Portrait and icon replaced 2026-10-09 (owner: the old one "too yellowish / creepy"): one Gemini call with vanilla Asian portraits as style references, keyed onto the vanilla portrait backdrop with the measured halo, the kasaya transparent for the player colour (provenance `tools/provenance/portraits_2026-10-09`). Owner's test 2026-10-09: empty Abilities grid, called "Korean Monk" - fixed: the Japanese monk's abilities without Sabotage (`data/abilities/abilitymods.xml`), 10 Korean monk names (`data/randomnamemods.xml`, strings 600028-600037), title Seungjang (600010); to check in game, plus AoP's own abilities (pirate ship Broadside) with the add-on loaded (first add-on abilitymods/randomnamemods) |
| Korean monastery (`zpMonasteryHyangyak`, `Dure`, `Pyeonjeon`, `Seungbyeong`) | replace the four Japanese monk techs in their slots: heal; villagers near a monk gather +10% (aura); bow and stun +4 range, +25% damage; the Seungjang trains the Seungbyeong in the field and their limit rises from 10 to 15 (the Chinese Disciple placeholder replaced 2026-10-09); Compunction kept; own icons (third set 2026-10-09, after the icon visual language) | owner's test 2026-10-09: the four techs in their slots; first icons all amber, second not AoE style - replaced; third set not yet seen in game |
| Seungbyeong `zpSeungbyeong` (22010), Korean monk soldier (design: `docs/seungbyeong.md`) | owner 2026-10-09: "extra unit like disciple", "no pop costs but lower stats", "distinct from Disciple", the white monk "as footman". The vanilla native Sohei with lower stats (100 HP, 9 hand attack x3 against cavalry and x2 against light infantry, 10% hand armour, 50 food 30 wood, 20 s), no population, limit 10 (15 with Seungbyeong); the Sohei's glaive and pikeman.tactics on the vanilla Disciple body with the Seungjang's white retexture (`art/units/korean_monk/korean_seungbyeong.*`: the library's Bip01 twin of each Sohei `*_pikeman` animation, glaive on `Bip01 Prop1`); a special unit (owner 2026-10-09: "not trainable from barracks"): only the Seungjang trains it, slot 7 after `zpMonasterySeungbyeong`; Korean soldier voices; scales with the ages like the Disciple (hit points and damage x1.20 / 1.30 / 1.40 / 1.50, +0.5 speed at Colonial: `zpSeungbyeongColonial` ... `Imperial`, the Disciple lines of the Chinese age techs); own portrait and icon (2026-10-09, player-colour kasaya) | offline: tests (data, animation set equals the vanilla Sohei's, every file in the archive), pose preview (charge idle and attack, glaive in both hands); not yet seen in game. Open: Barracks unit upgrades |
| Jochong Musketeer `zpJochong` (22012), the Korean musketeer (recipe: `tools/infantry_texture/README.md`) | owner 2026-10-09: "Jochong can stay Jochong", "the upgrades are must have ... vanilla always upgrades skins", "full retextures", hats crafted ("Hats are the easiest thing to craft"). The vanilla `ypAshigaru` field for field (170 HP, 24 ranged, 80 food 40 gold, musketBayonet.tactics) on the vanilla Arquebusier bodies with a Joseon retexture: jeonbok vest in player colour over a white hemp coat; Disciplined adds bandoliers and an indigo jeondae, Honored the long coat with red dongdari sleeves (the Chinese breast mirror painted out); a crafted jeollip (black felt, red sangmo, brass knob, 364 triangles, no player colour) on every age. Trained wherever Japan trains the Ashigaru, same slots (Barracks column 1, forts, daimyos, Atakebune, Maya castle, AoP camp/fort/palace; Ashigaru off for Korea); own upgrades `zpDisciplined/Honored/ExaltedJochong` = the Ashigaru upgrades (+20/+30/+50%, same costs) in the Ashigaru slot, also granted by a post-industrial start and the Meiji Restoration; Korean soldier voices; own portrait and icon (one Gemini call, player-colour vest) | offline: 6 tests against the live vanilla data (proto = Ashigaru, every trainer, upgrades, animation set, every file resolves, texture budget, models rebuild byte for byte); the jeollip GR2 read by the game's Granny DLL (both routes, 0 orphan fixups); renders. Not yet seen in game. Open: the home city still ships Ashigaru (cards below), Dojo Ashigaru army, AI |
| Jangchang Spearman `zpJangchang` (22013), the Korean spearman (recipe: `tools/infantry_texture/README.md`) | owner 2026-10-09: the roster's anti-cavalry unit, added (nothing Japanese replaced), "good, next one". The vanilla `ypQiangPikeman` field for field (Colonial Age, 105 HP, 7 hand attack x5 against cavalry, 60 wood, pikeman.tactics) with its three upgrades (Disciplined 100/50, Honored 350/350, Exalted 750/750 wood/gold, +20/+30/+50%, +0.5 hand range each), Korea's Colonial melee infantry since the Samurai is off for Korea (owner 2026-10-10: "no colonial age melee infantry", "add Colonial state too"; it was a Fortress unit with a free Disciplined from 2026-10-09 evening). Skins on the vanilla Qiang bodies 1 and 2 (`tools/korean_infantry.py`; owner 2026-10-10: "use fortress as colonial", "split industrial", "only the industrial gilded"): Colonial the steel tugu helmet with red plume and mail (Qing back badge painted out), Disciplined the studded dujeong-gap with white sleeves and brass studs, Honored the same body's material variant 1 with red dongdari sleeves, gilt studs, a gilt helmet rim band and a gilt cup under the red tassel (vanilla `abus_gun.xml` pattern); the Qiang's fur-cap body is not used. Barracks column 4 for Korea, the upgrades in the same column of the upgrade page with the Japanese hand-infantry medallions, visible from the start; Korean soldier voices; own portrait and icon (one Gemini call, player-colour armour coat) | offline: the parameterised infantry tests against the live vanilla data (proto, upgrades, button visibility, animation set and skin variant, files, texture budget, materialdef, models); renders. Fortress-only version seen in game 2026-10-10; the Colonial version not yet |
| Gakgung Archer `zpGakgung` (22014), the Korean archer (recipe: `tools/infantry_texture/README.md`) | owner 2026-10-09: the roster's archer in the Yumi's place, "and then next one". The vanilla `ypYumi` field for field (100 HP, 19 ranged, 55 food 50 wood, archer.tactics) on the vanilla Changdao bodies (the history check's pick; the Chu Ko Nu reads Qing) with the Yumi's bow animations and the vanilla Azap short composite bow (closest to the Korean horn bow) by path; base = helmet with mail, coat in player colour with black edging, white sleeves; Disciplined = red plume, studded skirt with brass studs, indigo jeondae; Honored = iron cuirass and lamellar bracers; the Ming chest mirror painted out and the gold phoenix-wing ornament cut out (BaseColor DXT5, AoP `ddt_dxt1.py --dxt5`). Trained wherever Japan trains the Yumi, same slots (Barracks column 0, forts, daimyos, Atakebune, Maya castle, AoP camp/fort/palace; Yumi off for Korea); own upgrades `zpDisciplined/Honored/ExaltedGakgung` = the Yumi upgrades (200/100, 600/600, 1500/1500, +20/+30/+50%) in the Yumi slot, also granted by the post-industrial and post-imperial starts; Korean soldier voices; own portrait and icon (one Gemini call) | offline: the parameterised infantry tests (proto, every trainer, upgrades and every vanilla tech that grants them, animation set, files, texture budget and DXT5, models); renders with bow and quiver. Not yet seen in game. Open: the home city ships Yumi (cards), AI |
| Market hunting pair (`zpKoreanEconomy`) | Hunting Eagles and Professional Hunters instead of the Japanese berry pair (debt B9 closed) | offline only |
| Separate add-on | this repo is the only source (tools/build.py, tests/); AoP holds no Korean source, only a guard test | build and tests offline; AoP + add-on together run by the owner 2026-10-08 (Hanok in the villager menu) |

## A. Blocking for real play

1. **The AI cannot play Koreans properly.** The AoP AI core decides by civ id: 67 `cCivJapanese` checks and
   `civIsAsian()` (46 uses) do not know `zpKoreans`, so an AI Korean is treated as a European civ: no wonder
   age-ups (it will likely stay in the Discovery Age), no shrine, Dojo or Daimyo logic, generic cards. A random-civ
   AI can roll Koreans. Fixing it touches the adopted core files (rule 7: core stays byte for byte, mod AI only in
   `aipiraterules.xs`) - needs the owner's decision on how.
2. **AoP maps branch on the civ name "Japanese"**: 19 scripts in `randmaps/` (+34 in `game/randmaps/`), 67 checks
   (Asian politician/consulate switchers, map setup). Koreans fall through to the generic branch on those maps.
3. **Tech Tree screen**: vanilla has per-civ `Data/uitechtree/techtreedata_<civ>.xml` (additive per the official
   table) and a class-bound WPF page `Data/wpfg/pages/uitechtree/techtree_<civ>.xaml`. Koreans have neither; the
   in-game Tech Tree for Koreans is probably empty. Research: can a mod add a page for a new civ at all?
4. **Two mods together are untested in game.** The official docs say additive files (`civmods`, `techtreemods`,
   `stringmods`, `homecity`...) merge; one match with AoP + the add-on must confirm it, plus the add-on's priority
   above AoP for the shared animfiles and soundset file.
5. **Korean Town Center model** still fails `gr2_lint` (6 checks: texture budget, texel density, UV lineage);
   shipped on the owner's go. Barracks and Stable pass (23/0 and 25/0) but live under the bench path
   `art/zbench_korean_military/` and carry material-binding warnings in `xmlcheck`.

## B. It still looks and sounds Japanese

6. **Units**: the roster is Japanese apart from the Jochong Musketeer, which replaces the Ashigaru (2026-10-09) - but the home city still ships Ashigaru (`YPHCShipAshigaru1-4`, `YPHCAshigaruDamage`, `YPHCAshigaruAntiCavalryDamage`: Jochong cards wanted), the Dojo trains the Ashigaru army and the AI still asks for Ashigaru (AI changes need the owner's approval). The Jangchang Spearman (2026-10-09) adds an anti-cavalry unit and is the Colonial melee infantry (2026-10-10), the Samurai is off for Korea (2026-10-10; the home city still ships Samurai: `YPHCShipSamurai1-4`, `YPHCSamuraiDamage`, `YPHCSamuraiSpeed`, and the Dojo can still give a Samurai army), the Gakgung Archer replaces the Yumi (2026-10-09; the home city still ships Yumi: `YPHCShipYumi*` cards). The Jochong also gets the Exalted upgrade from the post-imperial start (`zpJochongPostImperial`, missed in its first build). Still Japanese: Samurai, Yumi, Naginata Rider, Yabusame, Shinobi, Morutaru,
   Flaming Arrow, Atakebune, Tekkousen, Fune, Daimyo, Dojo armies). No Korean unit (the WoL study suggests Hwacha,
   turtle ship, long-range archers, Panokseon).
7. **Wonders** are the five Japanese ones (Golden Pavilion, Great Buddha, Shogunate, Torii Gates, Toshogu Shrine)
   with Japanese art, names and age-up bonuses.
8. **Every other building** is Japanese by culture (the Hanok has its Korean model from the Colonial Age; from 2026-10-10 the Castle has its Korean model from its first upgrade, which the player researches - the castle has no automatic upgrade; the Castle: intact + construction p66 + Havok destruction on the Japanese castle donor, `art/buildings/korean_castle/`, shown from the castle's FIRST UPGRADE `ypFrontierCastle` on (owner 2026-10-10: "as castle 1st upgrade Korean variant"; vanilla Japanese castle before it, the Korean look holds through Fortified) and on the test bed `zzTESTKoreanCastle`; roof = the Town Center's own tile and cap texels (owner-approved mock C15); destruction r5 (2026-10-10: roof cut over all 63 donor roof bodies, cut faces on the vanilla destruction sheet, masses by hull volume; workspace states_r1/REPRODUCE_r5.md); gr2_lint 37/0/0 and 17/0/0; not yet seen in game): Dojo,
   Market, walls, Trading Post. **The Dock** is Korean from the Discovery Age on (2026-10-11; owner 2026-10-10: "export
   dock to the game - construction, destruction - ... then add as age1 Korean Dock"): `art/buildings/korean_dock/` =
   intact + construction p66 r3 (2026-10-11, AoP aoe3de-building-states s.4 pattern as the castle/houses; owner: "One
   building can stand, without roof, other can be UC but final beam shape, no windows in the air", "use proper beam
   textures": finished platform; the Store standing with its walls (rough openings: owner 2026-10-11 "con model shouldn't have windows and doors if these
   are separate shapes") under an open fresh-timber roof frame;
   the Hall and the shelter as their final beam shape in fresh r65 timber; rafters/hips/ridges/gable trusses under the real
   roofs; 0 floating members; vanilla `dock_stage2` scaffold attached) + Havok destruction r2 on the vanilla Japanese dock age 1 donor (2026-10-11, owner "Destruction r2 +
   inspection": capped Voronoi cuts on the vanilla destruction sheet, roof re-seeded into compact chunks of at most 3.1 m2,
   piles snapped 0.4 m under the water, 196 of 217 donor bodies, 0 support conflicts; the quay and the pile stumps stay
   as the ruin; two read-only inspectors found no blockers), merged into `asian_civs/dock/dock.xml` (no AoP override of it) as the
   `zpkoreanvisuals` branch with only `<none>` (`korean_visuals.py` first upgrade 'none'), so it holds in every age.
   Pages: Dock 2048 (player colour in its Details at full strength, owner rule 2026-10-11) + platform 2048 + the shared r65 + the shared Korean props page
   `korean_shared/textures/korean_shared_props_r6` (art repo library package korean-props props-r6). gr2_lint korean_dock
   35/0/0 and korean_dock_con 17/0/0 (owner: "Yes: Dock = large", 2026-10-11). Worn quay corners (owner's game test 2026-10-11: "the masonry base should have smooth
   shading on corners or somehow cut corners"): rounded, r 0.12 m. Test bed `zzTESTKoreanDock` (22015, on the test
   builder wagon). Library package dock/export-r3. Seen in game by the owner 2026-10-11 ("otherwise good!").
   **The Consulate and the Monastery** are Korean from the Discovery Age on (2026-10-11; owner: "add both models into game -
   incl damaged and construction states", "From Discovery", "Oh no, in Korean mod", "Same monastery, but override in both using
   aop code"): `art/buildings/korean_consulate/` and `art/buildings/korean_monastery/` = intact + construction p66 (s.4: walls
   with rough openings under fresh-timber roof frames; the Monastery tiers 2-3 as their final beam shape; 0 floating members;
   vanilla Asian scaffold attached) + Havok destruction r1 on the vanilla Japanese consulate / monastery age 1 donors. The
   monastery: this add-on ships the merged `asian_civs/monastery/monastery.xml` (vanilla base; AoP has no override). The
   consulate: AoP overrides `consulate.xml` and has mod priority 1 above this add-on (2), so the add-on's copy never showed -
   the owner's game 2026-10-11 showed the Japanese consulate ("Consulate still original Japanese ... follow pattern"). Now
   AoP-hosted like the castle (`korean_visuals.AOP_HOSTED`, AoP `xmlcheck.py` COMPANION_ART); the add-on copy goes once the
   owner approves deleting it and the game is closed (until then `build.py --check` and `tests/test_no_shadowed_files.py`
   fail on purpose). Each with a `zpkoreanvisuals` branch of only `<none>`. Pages: one own 2048 each (player colour as junction bands at full strength)
   + the shared r65 + the shared Korean props page (owner: "Yes: Consulate = small, Monastery = small"). gr2_lint
   korean_consulate / korean_monastery 35/0/0, *_con 17/0/0. Test beds `zzTESTKoreanConsulate` (22016) and
   `zzTESTKoreanMonastery` (22017) on the test builder wagon. Workspace korean-civic-pair-claude export_r1. Not yet seen in game.
   **The Rice Paddy** is Korean from the Discovery Age on (2026-10-11; owner: "finish the last model - the very simplest one -
   Rice paddy ... in the Korean style with proper roof", "Let's try fully automated run on simple model - no checkpoints",
   "for field. you create only the shelter. rest is generic and should be reused", "and Ricepaddy also needs construction and
   destruction"): `art/buildings/korean_rice_paddy/` = a raised timber shelter at vanilla detail (square pyramid tile roof,
   hip caps, mast through the apex, ladder, back plaster panel, props from the shared props page) on the VANILLA field
   (`paddy` / `paddy_con` attachments at ROOT, the footprint decal, the asi_2x2 construction kit) + construction p66 (the
   shelter without roof under a fresh r65 roof frame: king post, hip and jack rafters; vanilla asi_2x2_stage2 scaffold) + Havok
   destruction r1 on the vanilla Japanese rice paddy age 1 donor (130 bodies, 140 cut caps on the vanilla destruction sheet).
   Merged into `asian_civs/rice_paddy/rice_paddy.xml` (vanilla base; AoP has no override) as a `zpkoreanvisuals` branch of
   only `<none>`. Page: ONE own 1024 page with an alpha cutout (owner "Try 1x1024 texture with alpha layer"; roof field from
   the TC tile canon, eave end tiles cut out, timber with analytic edge wear, plaster + player colour band) + the shared r65
   + the shared props page. gr2_lint korean_rice_paddy 33 PASS / 2 FAIL, korean_rice_paddy_con 16 / 1: the only FAIL is
   texture_budget - class small (1x2048 ceiling, the page is 1024) is PROPOSED; the owner's words name neither the class nor
   the building, so it waits for "Rice Paddy = small". state frames PASS (damaged on mata, construction on matc).
   attachment_check flags the field attach at ROOT: none of the vanilla rice paddy models has a ROOT bone either (20 vanilla
   ROOT attaches) - the game test decides whether ROOT is engine-provided like ATTACHPOINT. Two roof bodies of the on-death
   model exceed the compactness target (3.64 / 3.96 m against 3.0 / 3.24 m). Test bed `zzTESTKoreanRicePaddy` (22018,
   test builder wagon row 1). Workspace C:/work/korean-rice-paddy (r6, export out_r6, recipes). Not yet seen in game.
   **The Market** is Korean from the Discovery Age on (2026-10-11; owner: "When done, add the market to the game as market
   asian", "same as japanese / chinese", "plus the destruction test bed and skill update - add"): `art/buildings/korean_market/`
   = the Korean Market (hall, tower, entry bay, gallery, two stalls with goods and alpha straw thatch, Hangul signboard 장터,
   castle-graded masonry; korean-market-dock UV r7c + texture r7c step 10 + corner seams) + construction p66 **r2** (owner:
   "IDENTIFY WHY YOU CLEARLY IGNORED THE CONSTRUCTION GUIDELINES, THEN FIX" -> "construction now TOP!": the checklist port of
   the shipped Dock recipe - finished lower walls, the Tower standing without its roof, the Hall's upper storey as a
   fresh-timber beam frame, fresh-timber roof frames under the real roofs on r65, 0 floating; r1 was a payload filter without
   walls or roof frames; vanilla asi_4x4_stage2 scaffold) + Havok destruction on the vanilla Japanese market age 2 donor (`japanese_market_age2_damaged`: 142
   of 273 bodies refit, 902 cut caps on the vanilla destruction sheet; foundations, plinths and stone stairs stay as the
   ruin). Merged into `asian_civs/trade_market/trade_market.xml` (vanilla base; AoP has no override) as a `zpkoreanvisuals`
   branch of only `<none>` in the Japanese culture; the Chinese branch is untouched. Pages: own 2048 (opaque, player colour)
   + own 1024 (alpha cutout: thatch fringe, railing wind-holes, eave scallops; player colour) + the shared r65 + the shared
   props page **r6.2** (`korean_shared_props_r6_2`: the cart deck fix; the installed Dock keeps r6 - two props pages in memory
   until the Dock moves). gr2_lint korean_market 33 PASS / 2 FAIL, korean_market_con 16 / 1: the only FAIL is texture_budget -
   class medium (2048 + 1024) is PROPOSED; the owner's "2048+1024  is ok" names neither the class nor the building, so it
   waits for "Market = medium". state frames PASS (construction 547 pairs, damaged 2114 pairs, inliers 1.0); attachment_check
   PASS. Three on-death bodies exceed the compactness target (6.1 / 4.1 / 4.4 m against 3.0 m). r2 (2026-10-11 game test):
   bone_flag_civ 1.378 m under the pole tip ("flag sits too high"; r1 0.20 m; AoP flag_heights.py vanilla median), and one
   minimal roof patch on the r1 maps ("some artifact on the roof": the hall field's tile pan beside the corner ridge caps,
   shifted half a tile period; ~10k P0 texels, all other texels byte-identical to r1). Test bed
   `zzTESTKoreanMarket` (22019, test builder wagon row 1 column 1). Workspace C:/work/korean-market-dock (export_market,
   recipes). Not yet seen in game.
9. **Villagers and explorers**: villagers are now the Asian (Chinese) villager (owner, 2026-10-08), but the
   home city still ships **Japanese** villagers (`YPHCShipSettlersAsian1/2/5`) and Zen Diet targets the Japanese
   one (debt B1, plan section 8); explorers are now the mounted Korean monks (own model and icons; knocked out they fall like the vanilla mounted
   heroes - Hetman, Ras: no Knockout/KnockoutIdle/Recover anims, the engine plays the death animation; 2026-10-09).
10. **Voices**: villagers speak Korean (`sound/ypsettlerasian_snds.xml`); fishing boats and wagons speak Korean
    (male villager lines) where the Japanese ones speak Japanese (2026-10-09, `tools/korean_sounds.py`). Monks keep
    the Korean soldier voice (AoP's `Korean_Soldier_*`; owner 2026-10-09; generated voices only as a plan, AoP
    `docs/plans/elevenlabs_voice_plan.md`). Soldiers, ships and the home city speak Japanese. AoE2 also has Korean soldier, monk and king lines (soldier lines are already in AoP).
11. **Home city**: Japanese 3D scene (Edo), Japanese card set and default deck, Japanese card art.
12. **Lobby and menu art** still Japanese: history preview `h_pc_japanese`, independence icon, AI avatar
    (Tokugawa's face for the Empress), matchmaking textures, legacy flag button sets, legacy postgame texture. The
    Consulate & Age Up flag was not made (that template needs the Photoshop 2020 warp).
13. **Personality**: Tokugawa's chatset (a male voice, Japanese-themed lines) and avatar; no Korean chat lines, no
    portrait, no home-city chat set.
14. **Text**: the 14 non-English languages show the English strings; the civ rollover lists the Japanese units; no
    civ history / encyclopedia entry; no leader quotes or loading tips.
15. **Editor names** still read "Barracks Japanese" / "Stable Japanese" (plan P3: rewrite to "Asian Barracks" /
    "Asian Stable" in 15 languages).
16. **Random names**: no Korean explorer, ship or unit name lists.
17. **Balance**: identical to Japan; nothing in the gameplay is Korean yet.

## Tracked debts

- **Two wagons keep Japanese voices: AoP shadows their sound files (found 2026-10-11, owner decision pending).** AoP (mod
  priority 1) ships `sound/factorywagon_snds.xml` and `sound/fortwagon_snds.xml`; this add-on's copies with the
  `zpKoreans` choice (tools/korean_sounds.py) never reach the game. Fix options: AoP hosts the `zpKoreans` choice in its
  own two files (the castle pattern; AoP's `xmlcheck.py` must then accept the add-on's `zpKoreanVillagerM_*` soundsets as
  companion references), or leave these two wagons Japanese-voiced. `tests/test_no_shadowed_files.py` lists them as
  strict xfails. Also unverified: whether the engine merges `sound/soundsetsde.mods.xml` across mods (the add-on carries
  AoP's full file plus its own sets; AoP's copy wins if it does not merge).
- **Construction stages to fix (backlog, owner 2026-10-11: "these can be tracked somewhere in backlog to be fixed
  later").** Found by a read-only check of every installed `*_con.gr2` (floating = a mesh island not connected to the
  ground through contacts of <= 2 cm; renders in C:/work/korean-market-dock/export/other_con_check). Rules: the
  construction checklist (korean-buildings-blender `docs/methods/construction_models.md`, AoP `aoe3de-building-states` s.4):
  windows and doors are removed, including wooden door/window panels that are faces of their own; the frame and the
  plaster wall stay and the wall keeps its rough opening (owner 2026-10-11 evening, which withdrew the morning's
  "if baked like Town center, they must stay"); no floating member.
  - House A/B/C (`korean_house_*_con.gr2`): 81 separate window/door parts each (jambs, stiles, mullions, paper receivers,
    lower panels; house_states_r1 CONSTRUCTION_QA r13 `retained`) -> remove in `build_construction.py` (class rule), rebuild,
    re-export, gr2_lint, frame check.
  - Barracks (`korean_barracks_physics_con.gr2`): separate hall windows, door light and clerestory lights (r68e
    GEOMETRY_QA `retained`: window*/door-light/Clerestory) -> remove; both courtyard gate frames (3,080 triangles) end
    0.30 m above the ground with nothing under their posts -> posts down to the ground (or footings).
  - Stable (`korean_stable_physics_con.gr2`): separate rear-hall windows and door light -> remove.
  - Town Center (`korean_tc_con.gr2`): the 14 wooden panels (plank door + lattice window) go (owner 2026-10-11:
    "TownCenterCon -> strip all the wooden pannels and leave only the beams"; candidate construction-r74 in the library,
    not installed yet); one 1.7 x 1.27 m upright
    panel (12 triangles, raw y 7.17-8.90) in the top tower touches nothing, 0.81 m from the nearest structure (likely
    the signboard without its support) -> remove from the construction stage.
  Done for the Dock (export-r5): Store rough openings, 0 floating members.
- **Icons:** done 2026-10-09 - Korean monk (unit icon + 512 portrait) and the four monastery techs, generated
  through the image harness (5 paid calls, gpt-image low quality; provenance in `tools/provenance/icons_2026-10-09/`),
  bordered with `icon-forge`. The Hanok's icon and 512 portrait (2026-10-09, owner: "in the same style as Japanese Shrine") are a
  Cycles render of Korean House B (`data/wpfg/resources/art/buildings/korean_house/`), building border by `icon-forge`. Redone
  2026-10-09 (owner: "still need improvement to look cleaner", "somehow stylized", "use Gemini ... with strong prompt",
  "clear front view"): a straight front render with de-weathered texture copies, one Gemini stylization edit with
  the Shrine portrait as reference, the roof darkened back to the model's neutral slate (Gemini made it light and
  bluish), a thin rim light on the roof outline; AoP `visual-detail-check` at 128/64/48 px: cleaner than the old one
  (mottle 5.7 vs 8.1 at 64 px) and stands out more (0.36 vs 0.28; roof-edge contrast 10 vs 3, Shrine 18). The owner found the tech icons all
  amber; second set the same day with one palette per icon (6 more paid calls: one rejected 3x2 grid - a grid
  splits one image's detail between its cells -, four icons, one rejected Seungbyeong retry), "not much in AoE
  style". Third set wired the same day (4 paid calls, 15 in all) after AoP's icon visual language
  (`icon-forge/references/visual-language.md`): rendered props on plain fields - Hyangyak medicine jar and ginseng
  (jade), Dure rice sheaf, hoe and sickle (dark field; the prompt asked for blue), Pyeonjeon horn bow and dart guide
  (crimson), Seungbyeong straw hat, staff, spear and beads (purple); `iconsheet.py` panel check with Compunction
  passes. Open: the monk unit icon is still the first, warm one.
- **Balance placeholders (B10):** monk speed 6.0/7.25 and 250 HP, Dure +10% within 16, Pyeonjeon +4 range +25%,
  tech costs copied from the replaced Japanese techs.

- **F1 - city maps forbid houses, not the Hanok.** AoP's `zpSPCDisableHousesShadow` (London, Florence, Bosporus,
  Versailles attacker, Aztec city defender) disables the standard houses and removes them from the villagers' build
  menu, and caps special houses (Shrine 5, Village 3, Torp and others 5). The Hanok must be forbidden there too
  (owner, 2026-10-08). Plan: an add-on shadow tech with prerequisites `zpSPCDisableHousesShadow` and
  `zpKoreanBuildings` active, disabling `zpHouseKorean` and removing it from `AbstractVillager`; AoP stays Korean-free.
  Open: Koreans then have no house on those maps (the Shrine is off for them); alternative: cap the Hanok at 5.

- **Korean House roof junction r15f (2026-10-09):** owner: "the junction of two roofs ... should have special texture,
  only on texture level without adding more geometry". A 3D distance field from each roof texel to the other roof
  (porch <-> main, `roof_junction.py`, Houses B/C) drives a valley at texture level: a weathered lime-mortar seam on
  the junction, a calmer, darker channel ~0.1-0.16 m each side (roll relief eased in the normal map), a cut-tile line,
  moss and grime collecting along the valley. Rule in korean-buildings-blender `patterns/korean/roof_surface_finish.md`.
- **Korean House roof valley tiles r15g/r15h (2026-10-09):** owner on r15f: "I don't see it. It needs special tiles
  matching on both sides - study real Korean valley ridges", then "almost there ... a bit more subtle", "thinner".
  The seam became a hoecheom valley (회첨골): a narrow gutter (~0.16 m) of its own pan tiles running down the valley,
  courses at equal heights on both roofs so the laps meet in matching V's, field tiles cut to the gutter edge with small
  lime plugs in the cut cover rolls, gutter toned towards the field tiles, shallow concave relief and lap steps in the
  normal map. Roofs BaseColor/Masks/Normals only; walls unchanged. **Owner-accepted in game** ("use that version";
  game started after the r15h install). The soft Blender preview had made it look invisible: judge such details in
  game. Rule: korean-buildings-blender `patterns/korean/roof_valleys.md` (KR-ROOF-VALLEY-01).
- **Bench names (2026-10-09):** owner: "please also add test town center, barracks and stables" - the benches
  `zzTESTKoreanTownCenter` / `Barracks` / `Stable` (22003-22005, on the test builder wagon) existed but used the
  vanilla names; they now read "zzTEST Korean Town Center / Barracks / Stable (destruction bench)" (600038-600043).
- **Korean House roofs r15e (2026-10-09):** owner: the TC roof "looks more contrasting and pronounced ... normals edit or
  more contrast? Explore the textures forensically". Same normal tilt per texel (24 deg mean) and brightness as the TC, but
  the TC rolls carry broad curvature and ~20-40 % more tile-scale albedo contrast (std 15.4 vs 12.7) on a matte
  surface (roughness 207 vs 186). r15e: roof-field normals widened (blend with a mask-normalised blur) and amplified
  x1.35, crowns/channels +-20 %, crest highlight, dark line under each course lip, roughness toward 207. ROOFS only.
- **Korean House gables r15c (2026-10-09):** owner: "maybe some player color decorations on the gables? ... TC too
  decorative, barracks and stables use simpler. house can use even simpler one". Barracks/Stable: broad player-colour
  frame + double-square emblem; the House: one painted frieze above the gable foot + one emblem standing on it
  (Details.R). A game-camera ray test showed the 0.6 m roof overhang hides the gables above ~0.75 m on Houses A/B
  and both porches, so the decoration sits low, where it is seen. The r14 tan diamond emblem was removed. The emblem
  (r15d) was designed with the image harness (1 paid call, gpt-image-1 low, ~$0.011; ring + four-lobed flower,
  made symmetric) and is also in the neutral Hanok icon. Not yet seen in game.
- **Korean House textures r15b (2026-10-09):** owner on r15: "the green on the roofs is masking everything beneath it" and
  "why the roof endings are pure grey?". Moss is now a translucent, grainy tint (opacity <= 0.8 with holes, the tile's
  own light/dark detail kept) in shorter cushions; the eave ends (r12 had flattened them to the TC grey, detail +-3)
  keep that grey as their mean but get clay grain, per-tile tone, worn rims, damp lower edges and grime. ROOFS only.
  gr2_lint 6 profiles 0 FAIL / 0 SKIP, DDT decode PASS; not yet seen in game.
- **Korean House textures r15 (2026-10-09):** owner after the r14c test: "The textures need more love ... more moss,
  imperfection - roof imperfections - like towncenter". Weathering pass over texture-r14 (the newest release, checked in
  the producer folder, the package and here) on the WALLS and ROOFS pages: Painter generator masks (Dirt, Dripping
  Rust, Metal Edge Wear, fine Dirt; own second Painter instance on a copy of the r14 master) placed by per-texel 3D
  fields (height above ground, world-down runs, ridge/eave, tile pans). Roof: moss cushions in the pans on 14.6 % of the
  up-facing tiles (r14: 3.3 %), lichen, lighter tile crowns, worn lips, a few replaced/bleached tiles; ridge beam and
  barge timbers weathered. Walls: foot grime and algae, rain runs below edges and windows, earthen plaster chips,
  stone moss/grime, gable streaks. Unchanged: grey eave ends, alpha, AO, metallic, Normals, Details, UVs, budget.
  Offline: gr2_lint 6 profiles 0 FAIL / 0 SKIP, DDT decode PASS; not yet seen in game.
- **Korean House r14d (2026-10-09):** owner after the r14c test: "The destruction is too decent ... one of the model
  didn't have the continuous destruction basically at all". Stage (HKT type 0) pieces now carry 20.3 / 14.1 / 18.5 %
  of the damaged surface (A/B/C; vanilla Shrine donors 16.8 / 12.4 / 17.9; r14c 4.2 / 6.6 / 2.7): roof plates,
  rafters, gable ends, attic and wall plaster/window/door pieces break off as hitpoints drop, nothing left unsupported.
  Not yet seen in game.
- **Korean House r14c (2026-10-09):** the owner's first game test of r14b showed black roofs, too-dark walls and faces
  turned around - every House GR2 was inside out (mirrored export frame without corner reversal, INC-198). r14c
  writes the engine winding (AoP gr2_lint check `winding` now guards every model), makes the garrison pole 15 %
  taller and puts BONE_GARRISONFLAG at the flag's lower edge (owner: the bone is the cloth's lower edge). Test
  benches `zzTESTKoreanHouseA/B/C` place one variant each in the editor (no age logic). To re-test in game.
- **Korean House model (2026-10-09, texture-r14; release game-states-r14b):** every state derives from the r14
  geometry and maps (source retention audited: exact UVs/normals; DDTs byte-identical re-encodes); r14b fixed the
  construction timbers' mirrored UVs found by AoP's uv_integrity gate. 128 source faces per House (TC pots, pot
  base discs, mast) keep a negative UV winding, kept verbatim and reported (INC-194). To see in game - slow construction (vanilla p0/p33, Korean p66
  with the vanilla scaffold), completion, the garrison flag on the small mast (engine scale 0.7 unverified), partial
  damage (the damaged model) and the final collapse (mast falls as one piece). Open: the Discovery Age keeps the
  Shrine placeholder and its floating garrison flag; damage-decal (.dmg) templates not made; donor Havok bodies
  without Korean geometry keep their vanilla hulls; House C's hidden roof-deck strip (`Roof.Main.Receiver`, matc)
  is scaled +3 % at export (owner, 2026-10-09: float16 UVs put it at 53.5 t/u, floor 54) - the House source should
  carry that margin; the source marks the mast UV cell "generic source cell unresolved"; the attic bearing-wall
  panels question stays with the House producer.

## C. Housekeeping

18. `statsid KR` and `gameid ypack` are copied conventions, untested online; multiplayer needs both mods on every
    machine.
19. The `korean-civ` branch (full AoP fork prototype) is superseded by the add-on and kept as history.
