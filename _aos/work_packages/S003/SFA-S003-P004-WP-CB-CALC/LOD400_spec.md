---
id: SFA-S003-P004-WP-CB-CALC-LOD400
wp: SFA-S003-P004-WP-CB-CALC — calculator completion (6/14 → 15 goals)
gate: L-GATE_D (design) → ready for L-GATE_BUILD on team_00 go + team_35 mockups
status: SPEC (decision-complete; presentation layer pending team_35 mockups)
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50 (visual/QA) + team_190 (constitutional, cross-engine)
depends_on:
  - SFA-S003-P004-WP-CB-MOBILE (closed)
  - SFA-S003-P004-WP-CB-CALC-MANDATE-MOCKUPS (team_35 — presentation layer)
  - SFA-S003-P004-WP-CB-CROPDATA-DATES (Phase B-later only)
refs:
  - _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
  - _COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md
  - organic_market_agent/crop_book/calculators.py
  - organic_market_agent/crop_book/assumptions.py
---

# LOD400 — WP-CB-CALC

> Engine/data/logic is implementation-ready here. The **visual + interaction layer is owned by team_35** (mandate `MANDATE_CALC_MOCKUPS_2026-06-07.md`); this spec defines the **UI contract** (§7) the mockups must satisfy and will be merged with the returned mockups before build.

## 1. Scope
**In:** bring the calculator from 6 live goals to **15** by porting the Python calculators to JS, adding a JS date engine, reworking the result layer to typed results, and widening the server delivery. **Reuse** the existing `CALC` registry + `recompute()` (no math duplication). **Out:** `water` (#0 — `WP-CB-WATER`); the categorical data-enrichment + guided tool (`WP-CB-CROPDATA-DATES`); account-scoped session (per-device stays).

### Phasing (by data dependency — see LOD_DESIGN §0.5)
- **Phase A** (no prereqs): `transplants`(#2), `seed_cost`(#14), `compare`(#13) → 6→9.
- **Phase B-now** (existing data): `harvest_window`(#5, new 15th goal), `succession`(#6, derived), `sow_date`(#4, direct-seed) → 9→12.
- **Phase B-later** (after `WP-CB-CROPDATA-DATES`): `nursery`(#3), `frost`(#11), transplant-accurate `sow_date` → 12→15.

## 2. Phase A — non-date ports
Each adds a `CALC.<kind>(g, book)` mirroring the Python function; flip the goal's `kind` + `soon:false` in `$CALC_GOALS`; extend the CALC↔Python parity fixture (AC-11, `crop-book-v1.js:28`).

- **`transplants` (#2)** — `round((bed_len*100/spacing)*rows)` (Py `transplants_needed`). Book fields `spacing`,`rows` already delivered. Result: scalar `שתילים`. Trivial.
- **`seed_cost` (#14)** — `seed_input_cost`: `grams*price_per_g` OR `ceil(grams/grams_per_pack)*pack_price`. Needs **new builder inputs** (price/gram OR pack price+grams/pack) + **chain `grams`** from the `seed`(#1) result. Result: scalar `₪` (+ packs).
- **`compare` (#13)** — **quantity-first** (team_00). Loop `window.SFA_CROP_BOOK`, rank by `avg_yield_per_bed_m` (primary). Secondary line: `₪/מ׳` = yield × `price_documented` (price-list, illustrative). **No "profit"/"margin".** Rename label (e.g. "השוואת גידולים"/"שווי הגידול"); `rlabel`/`runit`=`ק״ג/מ׳`. Result: **ranked list** (new type — §6). Uses only whitelisted fields (no widening). Crops missing yield are excluded (not zeroed).

## 3. Phase B-now — date engine on existing data
### 3.1 B0 foundations (shared by all date calcs)
1. **JS date module** — date-only arithmetic on `YYYY-MM-DD` strings (NO `Date` timezone math; avoids DST off-by-one). Mirror Py exactly:
   - `sowing_date_from_harvest`: `target_harvest − days_to_maturity` (direct); transplant also `− days_in_nursery`.
   - `harvest_window_from_sowing`: `harvest_start = sow + nursery_days + days_to_maturity`; `harvest_end = harvest_start + harvest_window_max_days`.
   - `succession_schedule`: from `first_sow`, step `interval_days = succession_interval_weeks*7`, until count/season-end.
   - `nursery_trays_and_sow_date`, `frost_planting_window` (B-later).
2. **Assumptions exposure** — add `TRAY_CELLS` + `HARDINESS_OFFSET` (+ `rotation_gap_seasons`) to `window.SFA_ASSUMPTIONS` (today only the 7 scalars).
3. **`runEngine()` rework** — return a **typed result** `{type, ...}` where `type ∈ {scalar, scalar_grid, date, date_range, date_list, ranked_list}`; for date goals read `state.anchor` + the date input + date book-fields **directly from `window.SFA_CROP_BOOK[slug]`** (not the numeric `[data-book]` chips, which `parseFloat`-filter — `crop-book-v1.js:635`).
4. **Server delivery** (§5).

### 3.2 The three B-now goals
- **`harvest_window` (#5)** — **NEW 15th goal**: add `$CALC_GOALS` entry + dropdown slot. anchor=`sow`. Uses `days_to_maturity`(66/70)+`harvest_window_max_days`(68/70). Result: **date_range**. Best coverage — ship first.
- **`succession` (#6)** — interval is **DERIVED** `round(harvest_window_max_days/7)` (team_00 decision; NOT a delivered field — עידן's empirical cadence is operational, corr 0.10 with biology). anchor=`sow`. New input: number of cycles OR season-end date. Result: **date_list**. Coverage 68/70.
- **`sow_date` (#4)** — anchor=`target` → `target_date − days_to_maturity` (66/70). **Default to direct-seed** when `planting_method` unknown (transplant accuracy in B-later). Result: **date**.

## 4. Phase B-later — gated on WP-CB-CROPDATA-DATES
Needs `planting_method` + `frost_tolerance_class` (+ `days_in_nursery` for revealed transplants), filled by the guided-entry tool.
- **`sow_date` transplant path** — also `− days_in_nursery` when `planting_method ∈ {transplant, both}`.
- **`nursery` (#3)** — `nursery_trays_and_sow_date`: trays `= ceil(plants*oversow/tray_cells)`, tray-sow `= field_set_date − days_in_nursery`. Needs `plants` (chain from #2) + a `field_set_date` input. Result: **scalar_grid**-like (trays + date).
- **`frost` (#11)** — `frost_planting_window`: earliest `= last_frost − HARDINESS_OFFSET[class]`; latest `= first_frost − days_to_maturity`. **Region picker** supplies last/first frost (Israel region table — static asset, assemble once). Result: **date_range**.

## 5. Server plumbing (NEW — beyond the report; blocking for §3/§4)
`HubController::calc()` builds `window.SFA_CROP_BOOK` from a hard-coded **numeric** whitelist (`HubController.php:147-156`). Required changes:
1. **Add numeric date fields** to the whitelist: `days_to_maturity`, `days_in_nursery`/`days_in_nursery_cell`, `harvest_window_max_days`. (NOT `succession_interval_weeks` — derived client-side.)
2. **Add a `crop_attribute` query** for the categoricals `planting_method`, `frost_tolerance_class` (the calc controller does not query `crop_attribute` today; `CropBookViewController::detail` shows the pattern at L681-683).
3. **Non-numeric channel** — emit categoricals in a text sub-map (e.g. `window.SFA_CROP_BOOK_TXT[slug]`) so they survive the JS `parseFloat`/`isFinite` filter (`crop-book-v1.js:635`).
4. **Route test** asserting `planting_method`/`frost_class` + the date numerics reach the rendered payload for a RICH-seeded crop.

## 6. Result-layer rework (typed results)
Today `showResult`/`renderBreakdown`/`pushSession` (`crop-book-v1.js:719-760`) assume a scalar in `[data-result]`. Refactor to render by `type`:
- `scalar`, `scalar_grid` — as today.
- `date` — Hebrew dd/mm/yyyy + the anchor used.
- `date_range` — two dates as a window.
- `date_list` — a schedule of N dates; session row = a compact summary string (e.g. "רצף · N תאריכים").
- `ranked_list` — ranked crops, quantity primary + ₪/מ׳ secondary.
**Visual design of each = team_35 mockups (mandate §3).** This spec fixes the **data each type carries**; mockups fix how it looks.

## 7. UI contract (what the mockups must satisfy — merged on return)
- ASK: 4 steps (goal / crop / basis / time-anchor) + a **region picker** (frost) + goal-specific inputs (succession count|season-end; seed price|pack; nursery field-set date).
- RESULT: typed answer (6 shapes §6) + breakdown rows + session (accumulate, per-device, cap 30) + export (whole session → `/calc/print`,`/calc/export.csv`) + assumptions editor (existing AssumptionField macro).
- Honest **no-data state** per goal/crop (no fabricated numbers).
- #13 is multi-crop — the crop step adapts (all/shortlist).

## 8. Acceptance criteria
1. Each shipped goal returns a real result; no "בפיתוח" for goals declared live in that phase; honest no-data state otherwise.
2. **Parity:** each new JS calc matches its Python function on the shared fixture (extend AC-11).
3. Date math is date-only and matches Python `timedelta` exactly (test direct-seed AND transplant branches).
4. Server delivery: route test (RICH payload — NOT empty; WP-CB-MOBILE 500 lesson) asserts the new numeric + categorical fields reach the client.
5. Session accumulates typed results; export includes a sensible representation for ranges/lists.
6. **PHP suite green (217/217)** + a route test per touched server path. `validate_aos` 0 FAIL.
7. Presentation matches the approved team_35 mockups (team_50 visual QA).

## 9. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Date parity Py↔JS (DST/off-by-one) | Date-only string math; shared fixture; both branches tested. |
| Scalar-only render breaks on date/range/list | Typed-result refactor (§6) before B-now; route+JS tests. |
| Categoricals silently dropped | Non-numeric channel (§5.3); assert in route test. |
| #13 mislabels revenue as profit | Quantity primary; ₪ secondary; no "profit" wording. |
| `$notes`-style include-scope clobber | Namespace new template locals; RICH route fixtures; live smoke post-deploy. |
| UI overlap with redesign | Engine/UI split; build presentation only from approved mockups; rebase on main; coordinate via Nimrod before merge. |

## 10. Build sequencing
team_00 go → **Phase A** (+B-now once mockups for the 5 result shapes return) → guided tool (`WP-CB-CROPDATA-DATES`) → **B-later**. Isolated branch `claude/cb-followups-2026-06-07`, team_100 commits (IR#4), team_50 + team_190 validate (IR#1/#5). Build does not start until team_35 mockups land (presentation layer) + team_00 go.
