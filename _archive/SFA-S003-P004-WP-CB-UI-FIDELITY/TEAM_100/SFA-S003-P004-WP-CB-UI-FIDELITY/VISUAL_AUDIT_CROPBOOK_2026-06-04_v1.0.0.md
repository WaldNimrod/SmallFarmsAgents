# VISUAL AUDIT — Crop-book (ספר גידולים) — team_100 — 2026-06-04 — v1.0.0

**Trigger:** team_00 — crop-book "not per the sketch": elements mispositioned, cards too small/imprecise, missing many icons, crop page "broken / full-width / no structure". "I won't launch like this."
**Method:** team_100 reviewed live renders (sfa.nimrod.bio @ `6703313`) + traced root causes to `sfa_delivery/` CSS/code + quantified the art/icon inventory against the 70-crop DB.
**Scope of this audit:** crop-book entry (`/crop-book/`) + crop page (`/crop-book/{slug}`) + the art/icon system. (Hub/market/search/community/about already passed CLASSB L-GATE_V; recommend a full re-sweep as part of the fix WP.)

---

## A. Crop-book ENTRY page (`/crop-book/`)

| # | Finding | Root cause (file:line) | Fix |
|---|---------|------------------------|-----|
| A1 | **Cards far too small** — ~10 columns at 1440px; 120px tiles. patch01 over-densified (168→120). | `crop-book-v1.css:33` `.cards-grid { … minmax(120px,1fr); gap:10px }` | Larger min track per Board-A (≈170–200px → ~5–6 cols); restore card richness. **Design calibration → team_35.** |
| A2 | **Almost every card shows a generic 🌱** (only ~14/70 render real art) | Icon/art gap — see §C | Recover + generate art (§C) |
| A3 | **View toggle (כרטיסים/טבלה) floats centered**, detached from the section header | `crop-book-v1.css:28` `.aud-head { justify-content: space-between }` with 3 flex children pushes the switch to center | Align the switch with the header (group it right, or a compact segmented control per Board-A) |
| A4 | **No centered container** — entry content is full-bleed inside `.sh__body` (only 18px padding) | `_layout.php:127` `.sh__body` has no `max-width`; entry page adds none | Add a centered max-width wrapper (≈1100–1200px) so content holds structure on wide screens |
| A5 | **Card content sparse** — name + one big DTM number + dim pips only; "not the info that should show per crop" | `book_entry.php:200-231` `.ccard` markup | Define the per-crop card content vs Board-A (art, name, family, DTM, season, calc availability). **team_35.** |

## B. Crop PAGE (`/crop-book/{slug}`)

| # | Finding | Root cause | Fix |
|---|---------|-----------|-----|
| B1 | **Stretched full-width, no structure** ("נמטח לכל הרוחב") — content runs edge-to-edge | `crop-book-v1.css:563` `.cb-crop-detail { max-width: 100% }` — NO centered article container; `.sh__body` no max-width | Add `max-width ≈1080–1120px; margin-inline:auto` to `.cb-crop-detail` (article layout per Board-A). **NOT fixed by FIDELITY.** |
| B2 | Duplicate hero + raw 6-decimal floats + empty green icon-box + English units | D-1/D-2/D-5 | **Already FIXED in WP-CB-UI-FIDELITY (built, L-GATE_B PASS, undeployed).** Resolves on FIDELITY deploy. |
| B3 | Section spacing / headline-values / topic cards fidelity vs Board-A | to assess on the FIDELITY-deployed page | Fold into the fix WP's CDP sweep |

## C. ICONS / ART — the big gap (the "missing icons" + "images we made that weren't integrated")

**Inventory (70 crops):**
- **14 crops** render their watercolor (exact slug match).
- **14 watercolor PNGs EXIST but render for ZERO crops** — the `WC_ART` map keys are **singular** while the live crop slugs are **plural**: `carrot`↔`carrots`, `tomato`↔`tomatoes`, `cucumber`↔`cucumbers`, `onion`↔`onions`, `pepper`↔`peppers`, `pea`↔`peas`, `beet`↔`beets`, `radish`↔`radishes`, `melon`↔`melons`, `leek`↔`leeks`, plus `scallion`/`zucchini`/`bush-bean`/`pole-bean`. **← "the images we created that weren't integrated."**
- **56 crops have NO matching art** → generic leaf/seedling.
- **Icon sprite (`icons.svg`) has only 10 symbols** (carrot, cucumber, eggplant, leaf, lettuce, onion, pepper, seedling, tomato, zucchini) → non-watercolor crops fall to generic `leaf`.

**Root cause:** `CropBookViewController.php` `WC_ART` const (L216-245) + `book_entry.php` `$wc_art_map` (L79) are keyed by singular/short slugs that don't match the `_slugify(name_en)` plural slugs the DB produces.

**Fix — two tracks:**
1. **RECOVER NOW (zero-cost):** reconcile the slug→art map (add plural aliases / normalize) → immediately lights up ~14 existing watercolors. Pure render-layer.
2. **GENERATE the rest (~42 crops):** produce consistent watercolor icons for the crops with none.

### C-bonus — "Nano Banana" icon generation plan
"Nano Banana" = **Google Gemini 2.5 Flash Image** (image generation/editing). Approach for a consistent set:
- **Style-anchor:** feed an existing `wc-*.png` (e.g. `wc-tomato.png`) as a style reference + a per-crop prompt: *"watercolor botanical icon of {crop}, soft sage-green palette, transparent/paper background, loose brush style matching the reference, centered, ~512px"*.
- Batch the ~42 missing crops; review for consistency; export to `sfa_delivery/public_assets/img/crops/wc-{slug}.png` using the **actual plural slug**; verify render.
- **Access needed:** a Gemini API key / Google AI Studio (or a configured image-gen MCP). Not currently wired in this session — team_00 to provide access or run the batch; team_100 supplies the prompt set + style anchor + does the wiring + CDP verify.

## D. Recommendation

This is a **new build+design body of work** beyond FIDELITY's blocker fixes. Proposed **WP-CB-UICROP-FIDELITY2** (crop-book visual fidelity round 2):
- **Render-layer (no design needed):** B1 crop-page container, A4 entry container, C1 slug→art recovery, A3 toggle alignment. (team_10 build + team_100 CDP.)
- **Design-led (team_35):** A1 card size calibration, A5 card content design, B3 section fidelity, the icon-set style spec — all vs Board-A.
- **Icons:** C2 Nano-Banana generation (needs Gemini access).
- **Full-system CDP sweep** at 1440 + 375 (all surfaces) to confirm nothing else regressed visually.

**FIDELITY deploy question:** FIDELITY (single hero, formatted numbers, Hebrew units/chips, working filters, table-overflow fix) is a strict improvement over current live — but it does NOT make crop-book launch-beautiful (A/B1/C remain). Options: deploy FIDELITY now as incremental progress, or hold and ship FIDELITY + FIDELITY2 in one deploy. team_00 decides.

---
*Evidence: live screenshots `audit_evidence/live_crop-book-entry.png` + `live_crop-page_lettuce.png`; CSS/controller refs inline; art inventory cross-checked vs canonical Postgres (70 crops).*
