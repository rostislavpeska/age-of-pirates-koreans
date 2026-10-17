# Korean Home City Customizations & Visual Bench

This document tracks all customization options, lightset evaluations, backdrop integration, and architectural decisions for the Korean Home City (`data/homecityzpkoreans.xml`) in Age of Pirates: Koreans.

---

## 1. Executive Summary & Baseline Configuration

| Parameter | Current Value | Notes |
| :--- | :--- | :--- |
| **Default Lightset** | `Tenochtitlan` (Aztec Daytime) | **Approved permanent default**. Highest visual fidelity. |
| **Backdrop Geometry** | `korean_background.gr2` | 4 panels (A, B, C, D), 108 vertices, R=160m, H=65m, Y_base=-20m. |
| **Backdrop Textures** | 4 $\times$ 2048x1024 DXT1 DDT | Softened, -25% desaturated, atmospheric haze blend. |
| **Original Sharp Textures** | Archived safely aside | Located in `art/homecity/korean/korean_background/textures_backup_original_sharp/`. |
| **Customization Hub** | Fortress (`asianhomecityprops.xml`) | Houses all selectable lightsets and visual props. |

---

## 2. Lightset Evaluation & Test Records

### 2.1 Aztec Home City Lightsets (Primary Suite)

Dedicated Home City lightsets feature high directional sun intensity, zero fill-wash (`fillintensity = 0.0`), deep contrast shadows, and sky reflection cubemaps.

| Lightset | Engine ID | Icon | Status / Owner Feedback | Findings & Next Actions |
| :--- | :--- | :--- | :--- | :--- |
| **Aztec Daytime** | `Tenochtitlan` | `az_lightset_day` | **APPROVED AS DEFAULT** | Perfect balance. Foreground Hanok buildings and background mountains match in tone and contrast. |
| **Aztec Sunrise** | `tenochtitlan_sunrise` | `az_lightset_Sunrise` | **USABLE** (Requires dawn backdrop) | Strong low-angle amber/rose morning sun hits building roofs. Foreground is warm; current neutral backdrop feels too cool/pale by comparison. Needs warm dawn-graded backdrop variant. |
| **Aztec Stormy Night** | `tenochtitlan_thunderstorm` | `az_lightset_Storm` | In Testing | Replaces Blue Mountains. Dark stormy atmosphere with lightning flashes. |
| **Aztec Eclipse** | `tenochtitlan_eclipse` | `az_lightset_Eclipse` | In Testing | Replaces Andes. Dramatic solar eclipse darkness with eerie corona rim-light. |

### 2.2 RTS / Skirmish Map Lightsets (Evaluated & Disqualified)

| Lightset | Engine ID | Status | Reason for Disqualification |
| :--- | :--- | :--- | :--- |
| **Korea Skirmish** | `Korea_Skirmish` | **REJECTED** | Low sun (`3.0`), heavy fill wash (`1.32`), and ground fog (`60m`) milky-washes 3D models while 2D backdrop remains punchy. |
| **Yellow River** | `yellow_river_wet_skirmish` | **REJECTED** | Excessive green-tinted haze and low contrast on city structures. |
| **Herald Island** | `Herald_Island_Skirmish` | **REJECTED** | Overly dense blue-grey fog obscuring city details. |
| **Blue Mountains** | `blue_mountains` | **REPLACED** | Displaced by Aztec Stormy Night. |
| **Andes** | `andes` | **REPLACED** | Displaced by Aztec Eclipse. |

### 2.3 Legacy / Asian Fallbacks

| Lightset | Engine ID | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Japanese Sunset** | `japan` | Legacy Active | Labeled "Sunset Lighting" in Fortress. Retained as original Asian warm sunset option. |
| **Night Lighting** | `japan_night` | Legacy Active | Japanese night set. |
| **Snowy Season** | `japan_snow` | Legacy Active | Japanese snow set. |

---

## 3. Programmatic Backdrop Variant Architecture

The user asked whether the original backdrop can be adapted for **Aztec Sunrise** purely programmatically without re-prompting or generating a new AI image.

### 3.1 Feasibility: 100% Programmatic

Because we have the high-resolution, un-cropped source and exact 4-panel slicing coordinates, we can produce dedicated variants using pure mathematical color science:

1. **Color Grading & Temperature Shift**:
   - Warm golden-hour matrix shift: multiply high-luminance sky and sun-facing mountain slopes by warm amber/peach coefficients ($R \times 1.15, G \times 1.05, B \times 0.90$).
   - Shadow tinting: infuse deep mountain valleys and occluded crevices with subtle cool violet/slate blue to harmonize with the sunrise shadow color in `tenochtitlan_sunrise`.
2. **Atmospheric Dawn Haze Gradient**:
   - Apply a vertical exponential atmospheric scatter gradient starting from the valley horizon line up to 40% height.
3. **Geometry & Seam Guarantee**:
   - Zero-delta boundary seams: Panel borders ($A \to B \to C \to D$) are processed globally on the master canvas *before* cutting, guaranteeing 0 seam artifacts.
   - UVs and vertex positions on `korean_background.gr2` remain 100% frozen.

### 3.2 Engine Integration Methods for Variants

When switching to Aztec Sunrise in the Fortress menu, the engine can switch the backdrop via:
- **Option A (Material Variants)**: Configure `<materialvariant>` blocks in `art/homecity/korean/korean_background.xml` linked to the lighting state.
- **Option B (Prop Swapping)**: Link the sunrise backdrop prop to activate when `Japanese_LightMistyMorning` (Aztec Sunrise) is selected, deactivating the daytime backdrop.

---

## 4. Current File References

- **Home City Definition**: [`data/homecityzpkoreans.xml`](file:///c:/Users/TIGO/Games/Age%20of%20Empires%203%20DE/76561198347905238/mods/local/age-of-pirates-koreans/data/homecityzpkoreans.xml) + `.xml.xmb`
- **Customization Props**: [`data/asianhomecityprops.xml`](file:///c:/Users/TIGO/Games/Age%20of%20Empires%203%20DE/76561198347905238/mods/local/age-of-pirates-koreans/data/asianhomecityprops.xml) + `.xml.xmb`
- **Active Profile Save**: [`Savegame/sp_zpKoreans_homecity.xml`](file:///c:/Users/TIGO/Games/Age%20of%20Empires%203%20DE/76561198347905238/Savegame/sp_zpKoreans_homecity.xml)
- **Shared Lesson Journal**: [`.claude/skills/JOURNAL.jsonl`](file:///c:/Users/TIGO/Games/Age%20of%20Empires%203%20DE/76561198347905238/mods/local/age-of-pirates/.claude/skills/JOURNAL.jsonl) (Entry `2026-10-16-gemini-02`)
- **Archived Original Textures**: [`art/homecity/korean/korean_background/textures_backup_original_sharp/`](file:///c:/Users/TIGO/Games/Age%20of%20Empires%203%20DE/76561198347905238/mods/local/age-of-pirates-koreans/art/homecity/korean/korean_background/textures_backup_original_sharp/)

---

## 5. Lantern cosmetics (2026-10-17)

**Owner decision (2026-10-17):** every lantern set is its own home-city cosmetic, **independent of the lighting
set**, with a name, a description and a painted icon in the style of the vanilla lantern cosmetics ("a cosmetics
completely independent on lighting set is probably the best solution. The same with the second lantern type").
Generic engine facts (how a prop visual is placed, LightSet switching): AoP skill `aoe3de-homecity-backdrop`
section 6 "Night lights".

### 5.1 The two lantern cosmetics

| Cosmetic (prop) | Model / animfile | Icon | State |
| :--- | :--- | :--- | :--- |
| **Building Lanterns** `Korean_Night_Lanterns` | `art/homecity/korean/night_lanterns/korean_night_lanterns.gr2` + `.material`, `art/homecity/korean/korean_night_lanterns.xml` (built by `tools/homecity_night_lanterns.py`) | `korean_night_lanterns` (painted cream paper lantern) | standalone cosmetic, Toggle, cost 2, strings 600132-600133. The 133 vanilla Japanese building lanterns + 135 PopcornFX lights on the Treasury, Fortress, Imperial Court, Merchants Guild and Customs House. Owner's game test 2026-10-17 (wired to Blood Moon then): lanterns on the Fortress correct. Standalone version not yet seen in game |
| **Cheongsachorong** `Korean_Lanterns` (the red-blue silk street lanterns) | `art/homecity/korean/lanterns/korean_lantern_upgrade.gr2`, `korean_lanterns.xml` (built by `tools/homecity_lanterns.py`) | `korean_street_lanterns` (painted red-blue cheongsachorong) | standalone cosmetic since 2026-10-17 (owner: "make it like China - independent"): no prereq, no LightSet link; Toggle, cost 2; own strings 600134-600135 (were the vanilla Chinese 49112/49113 "Lanterns" / "year of the Ox") |

### 5.2 How a home-city cosmetic works

1. **The record** - `data/asianhomecityprops.xml` (this add-on's file replaces the vanilla one; AoP ships none):
   ```xml
   <prop>
     <name>Korean_Night_Lanterns</name>
     <civ>zpKoreans</civ>
     <type>Object</type>
     <displayname>Building Lanterns</displayname>
     <displaynamestringid>600132</displaynamestringid>
     <description>Paper lanterns glowing under the eaves of the city's great halls.</description>
     <descriptionstringid>600133</descriptionstringid>
     <levelprereq>0</levelprereq>
     <position>
       <bone>bone_fx</bone>
       <building>Emperor's Treasury</building>
     </position>
     <visual>homecity\korean\korean_night_lanterns.xml</visual>
     <buttonaction>Toggle</buttonaction>
     <cost>2</cost>
     <icon>homecity\home_city_props\icons\korean_night_lanterns</icon>
   </prop>
   ```
   - **Placement:** a city-frame model (authored in `korean_hc_ground` coordinates) needs `Emperor's Treasury` +
     `bone_fx`: `korean_court.gr2`'s `bone_fx` is minus `bone_court`, i.e. the city origin (vanilla China's anchor).
     `korean_hc_ground` has no `bone_centered` and no `bone_fx`; a prop without `<bone>` most likely sits at its
     building's own placement (not game-proven).
   - **Unlock:** `<cost>` is what the player pays to unlock it in the customization panel (owner's test: "I have to
     unlock the cosmetics first ... Maybe it's ok"); `<buttonaction>Toggle</buttonaction>` lets it be switched off.
   - **Independent of lighting** = no `<prereq>`, no `<activateprops>` / `<deactivateprops>` with a LightSet, and no
     LightSet lists it. (The coupled form, for reference only: a LightSet `<activateprops>` the prop and every other
     LightSet `<deactivateprops>` it - vanilla `Inca_LightSetNight` -> `Inca_Night_Lights`.)
2. **The civ lists it** - `data/homecityzpkoreans.xml` `<obtainableprops>`: `<prop>Korean_Night_Lanterns</prop>`
   (`active="1"` would make it on by default; unlocked/active state per player is in the profile's
   `Savegame/sp_zpKoreans_homecity.xml`).
3. **Strings** - `data/strings/english/stringmods.xml`, ids 600000+ (last used: 600133), English only.
   `python tools/build.py` compiles them into every language (it runs again at acd042c; it crashed on
   `factorywagon_snds.xml` before, INC-374). If it crashes again, compile only the strings with its own function
   (same bytes):
   ```bash
   python -c "import sys,os; sys.path.insert(0,'tools'); import build; x=build.compile_xmb('stringmods.xml', build.crlf(open('data/strings/english/stringmods.xml','rb').read())); [open(os.path.join('data/strings',l,'stringmods.xml.xmb'),'wb').write(x) for l in os.listdir('data/strings') if os.path.isdir(os.path.join('data/strings',l))]"
   ```
4. **Icon** - 128x128 RGB, full-bleed (no game border, like every vanilla cosmetic icon), three files with the same
   name: `art/homecity/home_city_props/icons/<name>.png`, `<name>.ddt` (`python ../age-of-pirates/scripts/havok/ddt_dxt1.py
   <name>.png <name>.ddt --size 128`) and `data/wpfg/resources/art/homecity/home_city_props/icons/<name>.png`; the record
   names it without extension. The painted lantern icons: AoP image harness, Gemini route, one call per icon, style
   references = the vanilla `chinese_lanterns` and `Japan_hanging_lanterns-kamihinokinai1` icons (runner
   `C:/work/hcl/scripts/gen_lantern_icons.py`, provenance `tools/provenance/icons_2026-10-17/`).
5. **Rebuild and check** - `xmbc.py check` then `build` for every edited `data/*.xml`; `attachment_check.py` on the
   animfile (every PopcornFX `tobone` declared with `<definebone>` and present in the model); art XML and `.material` CRLF;
   `python tools/build.py --check`; `python -m pytest tests -q` (pre-existing failures, INC-374: compare against a clean
   HEAD worktree, not against zero - at acd042c two stale sound files and 4 failures, none from the lanterns).
6. **Game test** - data and art load once per game process: restart the game, open the Korean home city's
   customization, unlock the cosmetic, toggle it.

### 5.3 For the agent finishing the street lanterns (`Korean_Lanterns`)

Done 2026-10-17 (owner-approved): `Korean_Lanterns` lost its `<prereq>` and `<activateprops>` (Blood Moon), Daylight and
Korea Sunset lost their `<deactivateprops>` entries for it, its icon is `korean_street_lanterns` and its name and
description are its own strings 600134-600135. No lantern cosmetic is linked to a lighting set any more - keep it so
(owner: otherwise "debugging hell for edge cases"). Model work stays in `tools/homecity_lanterns.py`; both agents edit
`data/asianhomecityprops.xml`: re-read it right before editing, use exact-match edits, rebuild the twin after.
`Korean_Lanterns` sits at `Emperor's Treasury` + `bone_fx` (correct for a city-frame model).
