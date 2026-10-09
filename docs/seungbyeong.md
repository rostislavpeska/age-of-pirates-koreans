# Seungbyeong (`zpSeungbyeong`, 22010): design note

Decided with the owner on 2026-10-09. Status and checks live in `AUDIT.md`; this note keeps the reasoning.

## Why it exists

The Korean monk (Seungjang) trained `ypMonkDisciple`, a placeholder from the `zpMonasterySeungbyeong` tech. Owner:
"Monk trains disciples... isn't it a bit too Chinese". Disciples are the Chinese Shaolin Master's unit. The idea is
Korean: during the Imjin War (1592-98) Seosan Daesa and Samyeong Daesa raised monk armies, the seungbyeong, and
Yeonggyu's monks helped retake Cheongju (1592). So the unit stays; it becomes Korean.

## Rules taken from vanilla

| Question | Vanilla precedent | Decision |
|---|---|---|
| Same unit from a hero and a building? | Inca War Chief and Kancha house both train Inca dogs; Hetman and Town Center both train Envoys | Barracks (Colonial Age) and the Seungjang (after the tech) |
| What is it worth if it costs population? | Owner: nothing - at 1 pop it is just another pikeman | no population, with a cap |
| How are no-pop units held back? | Disciple: 0 pop, cap 5; native Sohei: 0 pop, cap 16; Inca dog: 0 pop, cap 7 | cap 10, 15 after `zpMonasterySeungbyeong` |

Historically fitting: the monk soldiers were volunteers outside the conscripted army.

## Stats (owner: "no pop costs but lower stats")

| | Disciple | **Seungbyeong** | native Sohei | Pikeman |
|---|---|---|---|---|
| Hit points | 80 | **100** | 140 | 120 |
| Hand attack | 10 (x0.5 vs heroes) | **9; x3 vs cavalry, x2 vs light infantry** | 13 (x3.5 / x2.5) | 8 (x5 / x3.5) |
| Armour | 10% ranged | **10% hand** | 20% hand | 10% hand |
| Cost | 80 food | **50 food, 30 wood** | 55 food, 40 wood | 40 food, 40 wood |
| Training | 14 s | **20 s** | 30 s | 27 s |
| Population | 0 | **0** | 0 | 1 |

Korea has the Japanese roster; its only anti-cavalry infantry is the Ashigaru (a musketeer). The Seungbyeong adds a
melee one on top of the normal army.

## Weapon and look (owner: "distinct from Disciple", the white monk "as footman")

- The Disciple fights unarmed (kung-fu hand attacks), so the Seungbyeong gets the vanilla Sohei's glaive, the closest
  vanilla shape to the Korean woldo. Sources on the monk armies' own weapons are thin: one unsourced forum post says
  spears and sickles; spears and polearms were standard Joseon infantry weapons.
- Body: the vanilla Disciple with the Seungjang's white retexture (`art/units/korean_monk/korean_seungbyeong.*`).
- Animations: the Sohei animfile with the library's `Bip01` twin of each `*_pikeman` file, glaive on `Bip01 Prop1`.
  Owner: the library animations are universal; about 20 vanilla `Bip01_` units play this set. No re-rig.

## Age scaling (owner: "your new unit must work the same way")

The Disciple's only scaling with the ages is in the Chinese age-up techs: hit points and damage x1.20 (Colonial),
x1.30 (Fortress), x1.40 (Industrial), x1.50 (Imperial), +0.5 speed at Colonial, killing-blow chance off at Colonial.
Korea ages up with the Japanese techs, which activate the generic `Colonialize` ... `Imperialize`; four shadow techs
(`zpSeungbyeongColonial` ... `zpSeungbyeongImperial`, armed by `zpKoreanUnits`) give the Seungbyeong the same lines.
The killing-blow lines are left out: its attacks have none. Chinese-only extras (Shaolin monastery techs, White
Pagoda, Disciple shipments) have no Korean counterpart.

## Portrait and icon

Own 512 portrait and 128 icon (2026-10-09): one Gemini call with vanilla Asian portraits as style references, keyed
onto the vanilla portrait backdrop with the measured halo; the kasaya is transparent so the player colour fills it,
as the vanilla monk sashes. Provenance: `tools/provenance/portraits_2026-10-09`.

## Sources

- [Yeonggyu (Wikipedia)](https://en.wikipedia.org/wiki/Yeonggyu)
- [Battle of Cheongju (Wikipedia)](https://en.wikipedia.org/wiki/Battle_of_Cheongju)
- [Korea Times: Imjin War, monk-warriors](https://www.koreatimes.co.kr/www/opinion/2024/09/715_286460.html)
- [Slitherine forum: Korean list (unsourced weapons claim)](https://forum.slitherine.com/viewtopic.php?p=155459)
