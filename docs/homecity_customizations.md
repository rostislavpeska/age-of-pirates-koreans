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
