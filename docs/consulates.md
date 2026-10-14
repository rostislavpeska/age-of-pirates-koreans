# Korean consulates — implementation plan

Owner assignment, 13 October 2026. Russia uses the buttons that already exist. China is the new column in this document, on a standard button and an AoP clone. The campaign mercenary button is not this ally. United States is still the embassy wiring; its commandery column is not built yet.

Allies: Russia verbatim, United States from the embassy's own shipments, China as a new consulate rather than the campaign one.

Owner correction, 14 October 2026: Japan is not Isolation. Korea has its own Japanese Allies button in this add-on (`zpBigConsulateJapaneseAllies`, sequester `zpBigSequesterJapaneseAllies`, the end-relations icon) and an AoP clone (`zpBigConsulateJapaneseAlliesKorea`). Isolation (`ypBigConsulateJapanese`, `zpBigConsulateJapaneseClone`) stays Japan's. Khmer keeps `zpBigConsulateJapaneseAlliesClone`. The wiring is in AoP's [consulate system note](../../age-of-pirates/docs/consulate-system.md).

## How the consulate actually works

Two layers, and Korea needs both.

**Standard maps.** `zpAge0Korean` activates `YPAge0Japanese`, and that activates `YPAge0JapaneseConsulate`. That shadow makes four buttons obtainable: Dutch, Portuguese, Spanish, and Japanese Isolation, plus the politician picker `ypPickConsulateTech`. The armies those buttons enable are already sitting on `ypConsulate`, disabled, until the relation tech enables them. What the army contains is not on the proto. It is a `multipleblocktrain` on the civ. `zpKoreans` already has the Japanese, Spanish, Dutch, Portuguese and Russian blocks, copied from the Japanese civ.

**AoP maps.** The map trigger does the switch, not Age 0. On Burma (`game/randmaps/zpburma_b.xs`, "Activate Consulate Japan/China/India/Khmer") the trigger waits until `zpPickConsulateTechAvailable` is researching, then sets `zpTurnConsulateOn*` active, sets `zpBigButtonResearchDecrease`, fires `ZP Pick Consulate Tech`, and fires `Cheat_Returner`. The turn-on tech is a shadow that makes that civ's four `zpBigConsulate*Clone` buttons obtainable and sets every other politician unobtainable. Asian switches fire only Cheat Returner (skill `map-politician-triggers`). Burma has no `zpKoreans` branch, so a Korean player on that map never gets a consulate ally list.

Russia and Japanese Isolation already exist in both layers:

| Ally | Standard button | AoP clone |
|---|---|---|
| Russia | `ypBigConsulateRussians` | `zpBigConsulateRussiansClone` |
| Japanese Allies | `zpBigConsulateJapaneseAllies` (this add-on) | `zpBigConsulateJapaneseAlliesKorea` (AoP) |

The United States has no consulate button in either layer. Campaign China (`ypBigConsulateSPCChina`) has a standard button and no AoP clone. `zpBigConsulateChinaEuropean` is a different system and is not this ally.

## Where the work goes

AoP, because the owner assigned the map hook, the politician switch, and the Korean consulate records to AoP:

- `zpTurnConsulateOnKorean`, copied from `zpTurnConsulateOnJapanese`: the same long unobtainable list, with Russia's clone, the new USA clone, the new China clone, and `zpBigConsulateJapaneseAlliesKorea` made obtainable. Isolation's clone is set unobtainable.
- Burma only: `Activate Consulate Korea` for civilization `zpKoreans`, same five effects as Japan, wired into `Human_Check` the same way. Other AoP maps stay as they are (AUDIT item 2).
- The new USA and China buttons, both the standard one and the AoP clone, and the new banner-army protos. Clones follow `zpBigConsulateRussiansClone`: Trade 100, the clone sequester, `zpPickConsulateTechAvailable` set unobtainable. Standard buttons follow `ypBigConsulateRussians`.
- The USA big-button flag.

Korean add-on:

- A shadow fired by `zpAge0Korean` after `YPAge0Japanese`. It sets Dutch, Portuguese and Spanish unobtainable, and sets Russia, the new USA button, the new China button, and Japanese Isolation obtainable. `YPAge0Japanese` stays. It also enables the buildings.
- `multipleblocktrain` rows on `zpKoreans` for the new USA and China armies. Russia and Japan are already there.

A banner with no row on `zpKoreans` trains the banner itself. That is why the campaign Chinese armies cannot be enabled from the Korean civ file as it stands: those three rows exist only on civ `SPCChinese`.

## What a full ally contains

The 100-export flag turns on the armies and a passive. The armies are the soldiers, and they can be trained again. The tech column is something else.

Eight European allies have four techs, and the fourth is Imperial. It is the Brigade: 2300 export, it requires the Imperial Age, and it carries the flag `ypConsulateImprovementImperial`. That is the one large soldier shipment. Japan has no Brigade and no Imperial tech. Meiji is Industrial, and it costs 4000.

The other techs are the identity. Portugal ships boats. France ships crates. Russia ships buildings. Spain changes the rules. Germany starts trickles. The Dutch ship buildings and are the only ally with five techs.

| Ally | On the flag | Tech 1 | Tech 2 | Tech 3 | Imperial |
|---|---|---|---|---|---|
| Russia | villagers train in 90% of the time | 250, no age: blockhouse wagon | 600, Fortress: fort wagon | 800, Industrial: factory wagon | 2300: 25 counter-jaegers, 3 culverins |
| Portugal | buildings cost 15% less food and wood | 250, Colonial: 3 fishing boats | 425, Fortress: 1 caravel, 3 petards | 700, Industrial: 1 ironclad | 2300: 4 horse artillery, 11 jinetes |
| France | villagers gather 5% faster from farms, berries and paddies | 150, no age: 400 food | 300, Colonial: 500 wood | 350, Fortress: 600 coin | 2300: the French brigade |
| Spain | — | 125, Colonial: home-city shipments finish in half the time | 325, Colonial: crates hold 25% more | 700, Fortress: 1500 experience | 2300: the Spanish brigade |
| Germany | — | 200, no age: +1.50 food a second | 250, Colonial: +1.25 wood a second | 250, Fortress: +1.65 coin a second | 2300: the German brigade |
| Dutch | +0.80 coin a second | 150, Colonial: church wagon | 450, Colonial: bank wagon | 300, Fortress: arsenal wagon. 900, Industrial: livestock-pen wagon | 2300: the Dutch brigade |
| Britain | land units and villagers have +7% hit points | 250, Colonial, repeats: 2 surgeons | 300, Colonial, repeats: 4 spies | 450, Fortress, repeats: 5 petards | 2300: 16 rangers, 5 falconets |
| Ottomans | — | 200, Colonial: 6 azaps | 300, Colonial: 4 villagers | 850, Industrial: 2 great bombards | 2300: the Ottoman brigade |
| Japan | land military and villagers have +7% damage | 100, Colonial: a rickshaw | 300, Colonial: train 10 at a time | 400, Colonial: the castle can spawn a samurai | none. Meiji, Industrial, 4000, skips to Imperial |

Britain is the ally whose early techs are small squads. Portugal, France and Russia are not. Their soldiers are the armies and the Imperial brigade. The three techs before that are boats, crates, buildings, or a rule.

## Russia — use both existing buttons

No new units, no new costs.

`zpKoreans` matches the Japanese civ's Russian rows, which is the right verbatim. The Chinese civ's second army is different (5 Kalmucks and a culverin). Korea keeps the Japanese one.

| Army | Export | Age | Banner population | Spawns |
|---|---|---|---|---|
| 1 | 400 | Colonial | 4 | 4 Siberian Cossacks (225 HP, 26 hand, 1 pop, 75 food 75 coin) |
| 2 | 800 | Fortress | 14 | 6 Siberian Cossacks + 1 consulate culverin |
| 3 | 1600 | Industrial | 26 | 9 Kalmucks (200 HP dragoons, 2 pop) + 3 consulate culverins |

Techs, all one-shot, paid in export: blockhouse wagon 250, fort wagon 600 (Fortress), factory wagon 800 (Industrial), brigade 2300 (Imperial: 25 counter-jaegers and 3 culverins). The AoP clone also makes villagers train in 90% of the time and renames the frontier and fortified castle. Leave that clone as it is.

## United States — the Civil War commandery, not only the embassy

The American Embassy (`zpAmericanEmbassy`) has the five shipment techs. The Civil War commandery (`zpSPCCivilWarCommandery`, placed by `randmaps/zpcivilwar.xs`) has those five and the improvement techs the embassy does not. Fishing boats, a wood discount, and faster home-city cards are not on either building.

The embassy and the commandery stay as they are. Korea does not get a second copy of the coin buttons. The consulate uses the commandery's improvements, paid in export. Combat numbers stay:

| Unit | Pop | HP | Age on the proto | Combat | Cost |
|---|---|---|---|---|---|
| Regular | 1 | 150 | Colonial | 25 ranged, range 14 | 55 food, 50 coin |
| US Cavalry | 2 | 180 | Fortress | 19 ranged, range 12, ×3 against heavy cavalry | 80 food, 80 coin |
| Gatling | 4 | 150 | Fortress | 30 siege, range 24 | 100 wood, 250 coin |

The five shipment techs are on both buildings:

| Tech | Cost today | Repeats | Ships | Population |
|---|---|---|---|---|
| Company | 600 coin | yes | 8 Regulars | 8 |
| Force | 700 coin | yes | 5 US Cavalry | 10 |
| Army | 1000 coin | yes | 3 US Cavalry + 6 Regulars | 12 |
| American Brigade | 2000 coin | no | 5 US Cavalry + 8 Regulars + 3 Gatlings | 30 |
| Expeditionary Fleet | 1700 coin | no | 1 Dispatch Vessel + 12 Regulars | 12, plus the ship |

The commandery also has these. The embassy does not.

| Tech | Age | Cost today | What it does |
|---|---|---|---|
| Peace Pipe | Colonial | 300 wood, 300 coin | Ships an American war hut and opens the map's native consulate (Cherokee, Seminole, Lakota). |
| Ironclads | Industrial | 800 coin, 500 wood | Monitors become ironclads. The Asian dock can train one ironclad. |
| Union Factory | Industrial | 200 wood, 400 coin | One factory wagon. Opened by the President politician. |
| Field Hospitals | Industrial | 300 wood, 300 coin | Enables the field hospital and the surgeon. Opened by the General. |
| Fleet of Freedom | Industrial | 800 coin, 400 wood | Enables the Wokou steamer at the dock. Opened by the Admiral. |
| Emancipation | Imperial | 800 food, 500 wood | +20 population. Opened by the President. |
| Breech Loading | Imperial | 700 wood, 700 coin | Enables the siege rifle. The commandery already trains that unit. Opened by the General. |
| Silent Hunter | Imperial | 800 coin, 400 wood | Ships one submarine. Opened by the Admiral. |

The map picks one Union politician when the commandery exists. President also has no army passive. General makes artillery train in 85% of the time. Admiral adds 3 range to warships. The Confederate commandery is the other team: irregulars, a fort wagon, a steam tank, a privateer, a dry dock, and a banner that turns villagers into militia. That is not this ally.

`zpCivilWarGeneralStup` also turns on Railroad Logistics, Boomtown Industry, Hired Guns and Western Tales. Those are native-improvement team techs. They are not buttons on the commandery.

Consulate USA, new banner protos, Russian export ladder, banner population equal to the men:

| Army | Export | Age | Population | Spawns |
|---|---|---|---|---|
| 1 | 400 | Colonial | 6 | 6 Regulars (630 resources, next to 4 Cossacks at 600) |
| 2 | 800 | Fortress | 10 | 3 US Cavalry + 1 Gatling (830 resources) |
| 3 | 1600 | Industrial | 20 | 4 US Cavalry + 4 Regulars + 2 Gatlings (1760 resources) |

The armies stay the soldiers you train. The four techs are commandery improvements, plus the one shipment that is the Imperial brigade. A second Dispatch Vessel is not one of them. Industrial is the factory, which is the President's land tech.

| Tech | Age | Export | What it does |
|---|---|---|---|
| On the flag | — | — | Warships gain 3 range. This is the Union Admiral's effect, on the player's warships. |
| Company | Colonial | 600 | 8 Regulars. Repeats. The colonial shipment. Peace Pipe is the other colonial button, and it opens a native consulate that belongs to the Civil War map. |
| Ironclads | Fortress | 800 | The dock trains one ironclad. The commandery charges 800 coin and 500 wood and gates it at Industrial. Here the cost is the coin figure, and the age is Fortress so Industrial can be the factory. One hull, trained, not a shipped steamer. |
| Factory | Industrial | 600 | 1 factory wagon. The commandery charges 200 wood and 400 coin. Export is that sum. |
| American Brigade | Imperial | 2000 | 5 US Cavalry, 8 Regulars, 3 Gatlings. Once. Requires Imperial. The price stays 2000. |

Force, Army and the Expeditionary Fleet stay the shipment buttons on the embassy and the commandery. Emancipation, Field Hospitals, Breech Loading, Fleet of Freedom and Silent Hunter stay with their politicians. The column is four.

The missing art is the big-button flag. `scripts/tools/flagmaker_render.py` replays the Flag Maker pack's **Flag Icon** template onto a flat flag image and writes the `eso/flag_*_icon.png` the other allies use (`flag_russian_icon.png`, `flag_japanese_icon.png`). That template does not need Photoshop. The Consulate & Age Up cloth template does: it needs the Photoshop 2020 warp, which is the gap already noted in AUDIT item 12, and the route for it is the `photoshop-live-edit` skill. This task needs the Flag Icon. The consulate building hangs the player's own flag on `bone_flag_civ`; it does not swap a cloth to the ally.

## China — a new consulate, not the campaign one

The campaign ally is a gap list, not a template.

| Campaign offer | What is wrong with it |
|---|---|
| Colonial army: 3 Manchu for 400 export | Manchu is a Fortress mercenary, 400 HP, 3 population, 27 bow damage. Three of them are 9 population and 1200 HP in a Colonial button. |
| Fortress army: 8 Iron Troops for 800 export | Iron Troop is Industrial. 225 HP, 25 ranged, a shot every 1.5 seconds, 60% ranged armour. |
| Industrial army: 24 Rattan Shields and 8 Blind Monks | Rattan allows 10 and costs 0 population. The shipment cannot arrive as written. |
| Passive only | +5% gather, and then no Colonial tech, no Fortress tech, no Industrial tech, no brigade, no artillery. |

`zpBigConsulateChinaEuropean` is not the fill. It trains Iron Flail, Steppe Rider and Keshik for food and coin, and Mass Cavalry makes every cavalry unit train 25% faster, including Geomsabok, Gungdo Cavalry and Pyeongon Cavalry.

French crates are not the fill either. They belong to the French ally. A Chinese column of 400 food, 500 wood and 600 coin would be that ally with a different flag.

The armies are the soldiers. The four techs are not another copy of those soldiers.

| Army | Export | Age | Population | Spawns |
|---|---|---|---|---|
| 1 | 400 | Colonial | 8 | 6 Chu Ko Nu and 2 Steppe Riders |
| 2 | 800 | Fortress | 15 | 3 Manchu and 6 Hand Mortars |
| 3 | 1600 | Industrial | 18 | 6 Iron Troops and 6 Changdao |

Crates holding 25% more is new. It is Spain's `ypConsulateSpanishEnhancedProfits`, not a Chinese consulate tech. It does not stay. The food trickle is the same kind of paste: Germany's `ypConsulateGermansFoodTrickle`. It does not stay either.

The flag's +5% gather is current. It is the campaign passive. It stays.

The two replacements are Chinese buildings that already exist as wagons, in the slots Russia uses for a blockhouse and a fort. They are not France's crates and not Spain's crate rule.

| Tech | Age | Export | What it does |
|---|---|---|---|
| On the flag | — | — | Villagers gather 5% faster. Current campaign effect. |
| Rice paddy | Colonial | 250 | 1 `YPRicePaddyWagon`. Russia's Colonial tech is a blockhouse wagon at this price. This is the Chinese food building. |
| Castle | Fortress | 600 | 1 `YPCastleWagon`. Russia's Fortress tech is a fort wagon at this price. This replaces the crate rule. |
| Flying Crow | Industrial | 800 | 1 Flying Crow. The first one. Portugal's Industrial tech is one ironclad. |
| Battery | Imperial | 2300 | 3 Flying Crows. Requires Imperial. This is the late button, because the Flying Crow is the stronger piece. |

Manchu and Iron Troops are not the Imperial shipment. They are weaker than the Flying Crow, and a 2300 box of them sitting above a cheaper crow reads as a spreadsheet: the totals were added up and the famous gun was parked a tier earlier. Manchu stay on the Fortress army, which is their age. Iron Troops move to the Industrial army, which is their age. The Imperial button is the same gun, as a battery. Two would be the Ottoman bombard shipment, which is an Industrial tech at 850. Three is the late prize.

Chu Ko Nu, Steppe Rider, Hand Mortar, Changdao and Flying Crow are standard Chinese units. Manchu and Iron Troop are the campaign men, kept on the armies. No Rattan, no Blind Monk, no French crates, no Treasure Ship.

## Japan — Allies, not Isolation

Standard maps use `zpBigConsulateJapaneseAllies` in this add-on. AoP maps use `zpBigConsulateJapaneseAlliesKorea`. Both are the Isolation effect list (Yamabushi, Shinobi, Ninja, Ronin, +7% damage, the four Japanese techs) with two changes: the card is named Japanese Allies, and the undo button is its own sequester with the end-relations icon, not Isolation's shared `zpBigSequesterJapaneseClone` and not the end-isolation icon. `zpAge0Korean` already activates `zpKoreanConsulateAllies`, which turns Dutch, Portuguese, Spanish and Isolation off and turns Russia and this Allies button on.

Do not use `zpBigConsulateJapaneseAlliesClone`. That is the Khmer button: research points 10, and it shares Isolation's sequester.

The button enables Yamabushi (140 HP, 65 export, 1 pop), Shinobi (150 HP, 80 export), Ninja (400 HP, 4 pop, 145 export) and Ronin (540 HP, 4 pop, 290 export), sets +7% damage on all land military and on villagers, and opens four techs:

| Tech | Age | Export | What it does on a Korean player |
|---|---|---|---|
| Military Rickshaw | Colonial | 100 | One Japanese building wagon. |
| Master Training | Colonial | 300 | Sets the player's batch-train limit to 10. A buff, and it is the whole player, not just the consulate. |
| Koujou | Colonial | 400 | Adds `SpawnSamurai` to `ypCastle`. Korea uses that castle, so the castle gains a samurai spawn. |
| Meiji Restoration | Industrial | 4000 | Sets the age to Imperial and makes the five Japanese wonders unobtainable. Korea still ages with those wonders, so this skips the Industrial age-up and removes it. There is no 2300 brigade. |

Ship all four, including Meiji. The test on Burma is to research Meiji in Industrial and see the age skip. If that skip is wrong, the follow-up is to drop Meiji and keep the four units and the other three techs. The unit names stay Japanese. That is the ally.

The German clone's food discounts on Chu Ko Nu, Qiang and the other Chinese units are China's German ally. They are not part of this set.

## The four allies

| | Russia | United States | China | Japan |
|---|---|---|---|---|
| Passive | villagers train in 90% of the time | warships +3 range | gather +5% | land military and villagers +7% damage |
| Colonial army | 400: 4 Cossacks | 400: 6 Regulars | 400: 6 Chu Ko Nu, 2 Steppe Riders | Yamabushi and Shinobi |
| Fortress army | 800: 6 Cossacks, 1 culverin | 800: 3 US Cavalry, 1 Gatling | 800: 3 Manchu, 6 Hand Mortars | Ninja and Ronin |
| Industrial army | 1600: 9 Kalmucks, 3 culverins | 1600: 4 US Cavalry, 4 Regulars, 2 Gatlings | 1600: 6 Iron Troops, 6 Changdao | — |
| Techs, four | blockhouse, fort, factory, Imperial brigade | Company, ironclads at the dock, a factory wagon, American Brigade | rice paddy wagon, castle wagon, one Flying Crow, a battery of three | rickshaw, batch of 10, samurai spawn, Meiji. No Imperial tech. |

Russia uses the buttons that already exist. Japan is the new Allies pair above. United States and China are new buttons in both layers, with these shipments as `YPConsulateImprovement` techs (the Imperial row flagged `ypConsulateImprovementImperial`).

## Test, once it is built

Burma, Korean player. The four flags appear: Russia, United States, China, Japan. Dutch, Portuguese and Spanish do not. A standard map shows the same four from the Age 0 shadow. Russia still has its wagons. Each new ally shows four techs. The United States shows Company, ironclads, a factory wagon, and the American Brigade. China shows a rice paddy wagon, a castle wagon, one Flying Crow, and an Imperial battery of three Flying Crows. Meiji, if researched, is the age skip above.

`python .claude/skills/map-politician-triggers/scripts/politiciancheck.py` on the Burma script. Map scripts stay LF. New AoP techs get an `.xml.xmb` twin. Runtime XML stays CRLF.
