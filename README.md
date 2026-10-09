# Age of Pirates: Koreans (add-on mod)

A playable **Koreans** civilization for *Age of Empires III: Definitive Edition* with the
[Age of Pirates](https://github.com/rostislavpeska/age-of-pirates) mod. It starts as a clone of the Japanese
civilization with Korean flags, a Korean Town Center, Barracks and Stable, the Korean House (Hanok), a Korean
home city name and the AI personality Empress Myeongseong. What is still missing: [AUDIT.md](AUDIT.md).

## Install and play

1. Age of Pirates must be installed and enabled.
2. Put this folder into `<your AoE3DE profile>/mods/local/age-of-pirates-koreans`
   (`git clone https://github.com/rostislavpeska/age-of-pirates-koreans` there).
3. In the game: Manage Mods - enable Age of Pirates and Age of Pirates Koreans. Keep this add-on above Age of
   Pirates in priority. Restart the game after enabling or updating.
4. Pick "Koreans" in the skirmish lobby or the Scenario Editor. Disable the add-on to remove the civ again.

## For maintainers and agents: this repository is the single source of truth

Every Korean record, asset, tool and test lives here and is edited here. There is no second copy and no export
from another repository (owner, 2026-10-08: "One source of truth"). AoP stays free of Korean civ records; its
guard test is `scripts/tools/tests/test_no_korean_civ_in_aop.py` in AoP.

| What | Where |
|---|---|
| Game content | `art/`, `data/`, `game/`, `sound/` (the folders the game reads) |
| Build step | `tools/build.py` (+ `tools/korean_visuals.py`, `tools/korean_soundsets.xml`) |
| Tests | `tests/test_koreans.py` |
| Open work and debts | [AUDIT.md](AUDIT.md) |
| Design plan and research | korean-buildings-blender `research/Koreans_Civ_18/PLAN.md`, `research/WoL_Korea_15/` |
| Korean building models (3D pipeline) | this repo: `art/buildings/korean_tc/`, `korean_shared/`, `korean_tc_experiment/`, `art/zbench_korean_military/` (moved from AoP 2026-10-09; owned by the 3D agents) |

Workflow (any computer, AoP checked out next to this repo as `../age-of-pirates`):

```
edit art/ data/ game/ sound/ (and tools/korean_soundsets.xml for soundsets)
python tools/build.py                 # XMB twins, every language's string table, the 3 shared animfiles,
                                      # the merged soundsets, CRLF line endings
python -m pytest tests -q
restart the game and test
git add -A && git commit && git push
```

Files `tools/build.py` writes are generated: edit their source instead (listed at the top of `tools/build.py`).
`tools/` and `tests/` are not game content; leave them out of a mod-portal zip.

### Merge strategy with Age of Pirates

- **Two separate mods.** AoP is one mod and repo; this add-on is another. Each mod's additive data files
  (`civmods`, `protomods`, `techtreemods`, `stringmods`, `homecity`...) are merged by the engine with vanilla
  and with each other, so the add-on carries only its own records. Ids reserved for the add-on: strings 600000+,
  tech dbids 60000+, protos 22000+.
- **Merge-clean wiring.** Villager build menus are extended by techs (`CommandAdd` on `AbstractVillager`), never
  by editing villager records; AoP features that target every house reach the Korean House through its own
  tactics (tested).
- **Generated shared files** exist in both mods, so re-run `tools/build.py` after AoP changes them:
  - the Town Center, Barracks and Stable animfiles: vanilla (or AoP's own copy, if AoP ever overrides one) plus
    the Korean branch;
  - `sound/soundsetsde.mods.xml`: AoP's soundsets plus the Korean ones (cross-mod merging of this file is
    unverified, so the add-on carries both).
- **All Korean content lives here for now** (owner, 2026-10-09: "All Korean stuff should be there", "temporary. We
  will merge, but not now"), including the building models. The one exception stays in AoP as AoP gameplay: the
  Korean bombard native (`zpKoreanBombard`) and the Korean soldier voices it uses (`sound/korean/Koreans_Soldier_*`,
  `Korean_Soldier_*` soundsets), which the Korean monk also uses, so the add-on needs AoP for them.
- **History.** On 2026-10-08 the add-on was first kept as a source folder inside AoP (`koreans/`) with an export
  script; that layout was removed the same day in favour of this repository as the only source.

## Credits

- Flag: Korean Empire flag (1897-1910, public domain), rendered with the *AoE3DE Flag Maker Pack* v1.0.2.2 by
  EmpAhmadK (free for AoE3DE modding); AoP's generic flag tools `scripts/tools/flagmaker_render.py`, `flag_ddt.py`.
- Korean villager voices: *Age of Empires II: Definitive Edition* (Microsoft), from the Age of Empires wiki page
  "Koreans".
- Korean buildings: Age of Pirates 3D pipeline.
