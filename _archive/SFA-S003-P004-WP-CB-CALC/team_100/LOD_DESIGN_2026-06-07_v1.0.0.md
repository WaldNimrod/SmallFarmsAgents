# LOD (DESIGN) — SFA-S003-P004-WP-CB-CALC — Calculator completion (6/14 → 15 live)

**WP:** `SFA-S003-P004-WP-CB-CALC` · **Tier at authoring:** REGISTER → proposed **DESIGN (L-GATE_D)**
**Date:** 2026-06-07 · **Author:** team_100 (Chief Architect) · **Engine:** Claude Code (Opus)
**Branch:** `claude/cb-followups-2026-06-07` (isolated — parallel UI_REDESIGN session live on `main`)
**Spec/scope ref:** `_COMMUNICATION/team_100/REPORT_WP-CB-MOBILE_FOLLOWUPS_calc-and-deep-provenance_2026-06-07.md`
**Builder:** team_10 · **Validator:** team_50 (external visual/QA) + team_190 (constitutional)
**Status of this doc:** RESEARCH-FIRST design — **DECISION-COMPLETE** (team_00 resolved all §7 decisions 2026-06-07). **Build is gated only on team_00's explicit go.**

> ⚠ This is a *design* artifact, not a build. No application code was changed in authoring it. All findings below were re-verified against the working tree at branch base `f3e693c`.

## 0. team_00 decisions (RESOLVED 2026-06-07) — authoritative
1. **`water` (#0) → split to its own WP** (`WP-CB-WATER`, proposed §9). Needs a *new model* (ET₀×Kc) **and** *new data* (per-crop Kc + region ET₀) — out of scope for this ports-WP. Keep the "בפיתוח" stub until that WP ships.
2. **`profit` (#13) → reframe to a quantity-first crop comparison.** No "profit"/"margin" wording. Primary figure = **quantity (yield/m)**; value/revenue (from *our* price-list) is a **secondary line** only. Relabel the goal (e.g. "השוואת גידולים" / "שווי הגידול").
3. **`frost` (#11) → region picker.** Ship an Israel **region → last/first-frost** table; user selects a region (frost in Israel is "fairly easy and constant"). No free-text frost dates.
4. **`harvest_window` (#5) → surface as a 15th goal** (anchor=sow → harvest start/end).
5. **Date-data coverage (data investigation 2026-06-07) — the gap collapsed.** `days_to_maturity` 66/70 + `harvest_window_max_days` 68/70 ≈ complete. **`succession_interval_weeks` → DERIVED** `round(harvest_window_max_days/7)` (agronomic definition; עידן's empirical cadence dropped — corr 0.10 with biology). `days_in_nursery` is NOT a real gap (8/9 known transplants covered; gated by planting_method). The only true gaps are the two **categoricals** — `planting_method` (31/70) + `frost_tolerance_class` (37/70) — filled via a **guided-entry tool** (`WP-CB-CROPDATA-DATES`). Result: **B-now ships on existing data; only B-later (transplant/frost) waits on the tool.**
6. **Session persistence → keep per-device `sessionStorage`** (deferred until accounts exist).
7. **`WP-CB-CROPDATA-DATES` includes a guided classification UI** (per-crop Q&A) for team_00 to fill planting_method + frost_class fast; add a **`both`** canonical planting_method value.

---

## 1. Problem & goal

The `/calc/` "define the question" builder (`sfa_delivery/templates/pages/calc_dash.php`) exposes **14 calculator goals** (6 primary buttons + 8 in a dropdown). Only **6** compute a real client-side result; the other **8** dead-end on a "מחשבון זה בפיתוח" notice (`calc_dash.php:221-225`, fired when `runEngine()` returns `{ok:false}` for a goal with empty `kind` or `soon:true` — `crop-book-v1.js:626`).

The calculator is a **core product pillar** (market-price → plan → profit loop is the #1 competitive wedge per `project_ci_competitor_findings`). Eight of fourteen goals dead-ending undercuts that pillar.

**Goal:** bring the 8 stub goals to live computation (or make a deliberate product decision to drop one), reusing the existing math that is already implemented and unit-tested in Python.

---

## 2. Verified current state (code-grounded)

### 2.1 The math already exists in Python
All 14 calculators (+ a 15th, `harvest_window_from_sowing`) are pure, tested functions in `organic_market_agent/crop_book/calculators.py`. The only goal with **no model anywhere** is `water` (#0). So the work is overwhelmingly a **Python→JS port**, not new math.

### 2.2 The 14-goal map (verified against `calc_dash.php:57-74` + `crop-book-v1.js` `CALC` L31-129)

| Goal (he) | id | JS `CALC` | State | Python | Type | Port difficulty |
|---|---|---|---|---|---|---|
| זרעים לקנות | 1 `seed` | ✅ | LIVE | ✓ | scalar | — |
| יבול צפוי | 8 `yield` | ✅ | LIVE | ✓ | scalar | — |
| הכנסה צפויה | 9 `revenue` | ✅ | LIVE | ✓ | scalar | — |
| צפיפות שתילה | 10 `pop` | ✅ | LIVE | ✓ | scalar | — |
| כמות דישון | 12 `fert` | ✅ | LIVE | ✓ | scalar | — |
| ערוגות ליעד | 7 `beds` | ✅ | LIVE | ✓ | scalar | — |
| כמות שתילים | 2 `transplants` | ✗ | STUB | ✓ | scalar | **trivial** |
| עלות זרעים | 14 `seed_cost` | ✗ | STUB | ✓ | scalar | small (new inputs + chain) |
| רווח גולמי | 13 `profit` | ✗ | STUB | ✓ | **list** | medium (multi-crop + data gaps) |
| תאריך זריעה | 4 `sow_date` | ✗ | STUB | ✓ | **date** | date engine |
| ימי משתלה | 3 `nursery` | ✗ | STUB | ✓ | **date** | date engine + extra input |
| רצף גידולים | 6 `succession` | ✗ | STUB | ✓ | **date list** | date engine + extra input |
| חלון קרה | 11 `frost` | ✗ | STUB | ✓ | **date range** | date engine + frost-date inputs |
| צריכת מים | 0 `water` | ✗ | STUB | ✗ NONE | undefined | **product decision** |

### 2.3 The dead time-anchor (verified `crop-book-v1.js:561-662`)
The builder renders a Step-4 "עוגן זמן" with three chips (תאריך יעד / תאריך זריעה / עכשיו) and two date inputs (`target_date`, `sow_date`) — `calc_dash.php:179-197`. But:
- `state.anchor` (default `'target'`) **only drives input visibility** via `showAnchorInput()` (`crop-book-v1.js:594-598`).
- `runEngine()` (`crop-book-v1.js:624-662`) reads **only** the basis number → `bed_len`/`area`/`area_m2`/`target_kg`. It **never reads** `state.anchor`, `target_date`, or `sow_date`.
- The only consumer of `target_date` anywhere is the legacy single-result CSV/PDF export path (`crop-book-v1.js:502-503`).

So the date scaffolding is **built but inert**. The date engine's job is to make `runEngine()` actually consume it.

### 2.4 Assumption tables exist but are not exposed to JS (verified `assumptions.py`)
`TRAY_CELLS` (default 128) and `HARDINESS_OFFSET` (frost class → offset days) are defined in `assumptions.py:110-132` and consumed by the Python date calcs. The JS side (`window.SFA_ASSUMPTIONS`, `crop-book-v1.js:484`) exposes only the 7 scalar keys. **The two lookup tables are not exposed** — the date engine needs them.

---

## 3. ⚠ NEW findings beyond the report — server-side plumbing gaps

The original report (§1.2b iii) framed the date plumbing as "through `QB_BOOK_ALIAS` + the engine `[data-book]` chips" — i.e. **client-side**. Re-tracing the data path shows the real blockers are **upstream and server-side**:

### 3.1 The calc controller fetches ONLY numeric fields (blocking for Phase B)
`HubController::calc()` builds `window.SFA_CROP_BOOK` from a **hard-coded field whitelist** (`HubController.php:147-156`):
```
spacing_in_row_cm, in_row_spacing_cm, rows_per_bed, seeds_per_g, seeds_per_gram,
yield_per_bed_m, avg_yield_per_bed_m, price_documented, documented_price,
nutrient_removal_n_kg_per_ha, nutrient_removal_N,
nutrient_removal_p_kg_per_ha, nutrient_removal_k_kg_per_ha
```
The date book-fields the date calcs require — `days_to_maturity`, `days_in_nursery` (a.k.a. `days_in_nursery_cell`), `harvest_window_max_days`, `succession_interval_weeks` — **are not in this list and never reach the client**. Phase B MUST widen this whitelist (server change), not just touch JS.

### 3.2 Categorical fields are dropped twice
`planting_method` and `frost_tolerance_class` are **strings/categoricals**, likely stored in `crop_attribute` (not `crop_field_enrichment`). The calc controller does **not** query `crop_attribute` at all (contrast `CropBookViewController::detail()` which does — L681-683). And even if delivered, `runEngine()`'s flattener rejects non-numerics: `var v = parseFloat(...); if (isFinite(v)) flat[key] = v;` (`crop-book-v1.js:635`). So categorical date inputs need a **separate, non-numeric delivery channel** end-to-end (controller query + a `window.SFA_CROP_BOOK` text sub-map + a JS path that bypasses the parseFloat filter).

### 3.3 The engine `[data-book]` chips are numeric-only
The hidden engine (`calc_dash.php:276-291`) has 8 numeric `[data-book]` chips. Date book-values won't fit this DOM-chip model cleanly (it round-trips through `parseFloat` in `readBook()`, `crop-book-v1.js:131-138`). The date engine should read book-values **directly from `window.SFA_CROP_BOOK[slug]`** rather than via the chip DOM.

**Implication:** Phase B is genuinely a vertical slice (PHP controller → JSON payload → JS engine → render), not a JS-only port. This raises Phase B's effort estimate and adds a PHP route test.

---

## 4. Phased build plan

### Phase A — non-date ports (re-scoped from the report's single "~1 day")

| Sub | Goal | Work | Effort | Notes |
|---|---|---|---|---|
| **A1** | `transplants` (#2) | Add `CALC.transplants(g,book)` = `round((bed_len·100/spacing)·rows)`; flip goal `kind:'transplants'`, `soon:false`. | **trivial (hrs)** | Book fields (`spacing`,`rows`) already plumbed + already in the whitelist. Truly free. |
| **A2** | `seed_cost` (#14) | New builder inputs (₪/gram **or** pack-price + grams/pack); chain `grams` from the `seed` calc output; `CALC.seed_cost`. | **small (~1d)** | Pure user-input math (no book field). Decide UX: a sub-field on the result, or its own goal flow. |
| **A3** | `compare` (#13, ex-`profit`) | Loop `window.SFA_CROP_BOOK`, rank crops by **yield/m** (primary); render a **ranked list** with value/revenue/m as a secondary line. | **medium** | Reframed per decision #2 — see §4.1. |

#### 4.1 `compare` (#13) — reframed to quantity-first (decision #2)
**No "profit"/"margin" anywhere.** The goal is a *multi-crop comparison*; the hero metric is **quantity (yield per bed-m)**, with **value/revenue per bed-m as a secondary line** (revenue = yield × price-list price — a "gimmick", explicitly secondary). This also distinguishes #13 from the live single-crop "הכנסה צפויה" (#9).
- **Rename** the goal label away from "רווח גולמי" → e.g. "השוואת גידולים" / "שווי הגידול"; update `rlabel`/`runit` (primary unit `ק״ג/מ׳`).
- **Multi-crop:** iterates all crops in `window.SFA_CROP_BOOK`, breaking the single-`cropSel` model. Result is a **ranked list**, but `showResult`/`renderBreakdown`/`pushSession` (`crop-book-v1.js:719-760`) assume a **scalar** in `[data-result]` — list rendering + a sensible single session-row string must be designed (shared with the date-list rendering in B0.5).
- **Data:** rank by `avg_yield_per_bed_m` (already in the whitelist — no widening needed for the primary metric). The secondary revenue line uses `price_documented` (already whitelisted), assumed ₪/kg from the price-list — **no** `kg_per_unit`/`seed_cost` dependency since we're not computing margin. So A3 is now buildable in Phase A without the date-engine whitelist work.

**Phase A outcome:** 6 → **9 live** — transplants (#2) + seed_cost (#14) + compare (#13, quantity-first). No engine rework, no whitelist widening.

### Phase B — date engine (the substantive piece)

> **⚠ Re-split by DATA DEPENDENCY (data investigation, 2026-06-07).** The supposed gap collapsed: `days_to_maturity` (66/70) + `harvest_window_max_days` (68/70) are nearly complete, and **`succession_interval_weeks` is no longer a data field — it is DERIVED** `round(harvest_window_max_days/7)` (decision: agronomic definition). Empirical proof: עידן's stored cadence (old source, 19 crops) does NOT correlate with crop biology (corr 0.10, ±5wk) — an operational ordering rhythm, a different thing. **So most of Phase B ships on EXISTING data; only the transplant-accuracy + frost paths wait on the `WP-CB-CROPDATA-DATES` guided-entry tool** (planting_method 31/70, frost_class 37/70; days_in_nursery is NOT a real gap — 8/9 of *known* transplants already covered, gated by planting_method).

Sub-grouped by **data dependency** (not anchor fit):

**B0 — foundations (shared):**
1. **Server:** widen the `HubController.php:147-156` whitelist to add `days_to_maturity`, `days_in_nursery`/`days_in_nursery_cell`, `harvest_window_max_days` (NOT `succession_interval_weeks` — now derived from `harvest_window_max_days/7`, not delivered); add a `crop_attribute` query for `planting_method` + `frost_tolerance_class`; emit a text sub-map in `window.SFA_CROP_BOOK` (or a sibling `window.SFA_CROP_BOOK_TXT`).
2. **JS date engine:** a small date module doing **date-only** arithmetic on `YYYY-MM-DD` (no `Date`-timezone math — avoids DST/off-by-one; mirror Python `date + timedelta` exactly). Mirror `sowing_date_from_harvest`, `harvest_window_from_sowing`, `succession_schedule`, `nursery_trays_and_sow_date`, `frost_planting_window`.
3. **Assumptions:** expose `TRAY_CELLS` + `HARDINESS_OFFSET` (and `rotation_gap_seasons`) to `window.SFA_ASSUMPTIONS`.
4. **`runEngine()` rework:** branch on goal "type" (scalar | date | date-range | date-list); for date goals read `state.anchor` + the date input + the (new) date book-fields directly from `window.SFA_CROP_BOOK[slug]`.
5. **Rendering:** date-aware `showResult`/`renderBreakdown`/`pushSession` — format `dd/mm/yyyy`, render a **range** (frost: earliest→latest plant) and a **list** (succession: N sow dates), and a sane session-row string for each.

**B-now — buildable on EXISTING data (no enrichment dependency):**
- `harvest_window` (#5): **surfaced as the 15th goal** (decision #4). anchor=`sow` → `sow_date` → harvest start/end, from `days_to_maturity` (66) + `harvest_window_max_days` (68). **Best coverage — ship first.** Add a `$CALC_GOALS` entry + dropdown slot.
- `succession` (#6): **derived** `round(harvest_window_max_days/7)` (decision: agronomic) → 68/70, zero new data. anchor=`sow` → `first_sow` + a new input (number of successions **or** season-end date). The interval is computed, not asked.
- `sow_date` (#4), direct-seed path: anchor=`target` → `target_date` − `days_to_maturity` (66). **Default to direct-seed** when `planting_method` is unknown (transplant accuracy comes in B-later).

**B-later — needs the `WP-CB-CROPDATA-DATES` guided-entry tool (planting_method / frost_class / days_in_nursery):**
- `sow_date` (#4) transplant path: also subtract `days_in_nursery` when `planting_method`∈{transplant,both} (known transplants already 8/9 covered).
- `nursery` (#3): `days_in_nursery` (gated by planting_method) + `field_set_date` + `plants` (chained from `transplants`/#2). Needs an anchor extension or a dedicated field-set-date input.
- `frost` (#11): **region picker** (decision #3). Ship a small **Israel region → {last_spring_frost, first_autumn_frost}** table (static asset) + `frost_tolerance_class` via `HARDINESS_OFFSET`. No free-text frost dates.

**Phase B outcome:** 9 → **15 goals total**. B-now ≈ +3 (harvest_window/succession/sow_date-direct) on existing data — **not gated** on the enrichment WP. B-later ≈ +2 (nursery/frost) + transplant-accurate sow_date, after the guided tool. Sequencing: B0 → B-now → (guided tool) → B-later.

### Phase C — `water` (#0): SPLIT OUT (decision #1)
**Resolved:** `water` is **not** built in this WP. It needs a *new model* (ET₀×Kc×area − effective rainfall) **and** *new data* (per-crop Kc book field + region/month ET₀ — the frost region table can supply the region axis, but Kc-per-crop does not exist). Tracked as the proposed `WP-CB-WATER` (§9). The "בפיתוח" stub stays until that WP ships — no fabricated number.

---

## 5. Acceptance criteria

- Every shipped goal returns a real result — **no "בפיתוח"** for goals declared live in that phase.
- **Parity:** each new JS calc matches its Python function on a shared fixture (the repo already asserts CALC↔Python parity per `crop-book-v1.js:28` AC-11 — extend that fixture for each new calc).
- Date calcs honor `state.anchor` + the date input; date math is date-only and matches Python `timedelta` results exactly (incl. transplant nursery-offset branches).
- Session accumulates the new results and export-all (`/calc/print`, `/calc/export.csv`) includes them with a sensible representation for ranges/lists.
- **PHP suite green (217/217)** + **one route test per touched server path**, seeding a **RICH** crop payload (NOT an empty fixture — the WP-CB-MOBILE 500 lesson: `feedback_shared_include_scope_var_clobber`) and asserting the numeric/date/list result renders.
- `water`: either computes, or is cleanly removed with the goal count updated — no dangling stub.

## 6. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Date parity Python↔JS (DST/timezone off-by-one) | Date-only string math; shared parity fixture; test transplant + direct-seed branches. |
| Scalar-only render assumptions break on date/range/list | Refactor `showResult`/render/session to a typed result before B1; cover with route + JS tests. |
| Categorical fields silently dropped (§3.2) | Explicit non-numeric channel end-to-end; assert in the route test that `planting_method`/`frost_class` survive to the client. |
| `profit` mislabels revenue as margin (§4.1) | Label as "revenue ranking" until the whitelist carries unit/kg_per_unit/seed_cost, or defer to B0. |
| Shared include-scope var clobber (the `$notes` 500) | Namespace any new template locals; seed rich route fixtures; smoke the LIVE page post-deploy. |
| Overlap with the parallel UI_REDESIGN session (touches `calc_dash.php`, `crop-book-v1.js`) | Coordinate via Nimrod before merge; rebase on `main` first; do not touch `UI_REDESIGN_2026-06/`. |

## 7. Decisions — RESOLVED (team_00, 2026-06-07)
All decisions resolved — see §0. Summary: (a) water → split to `WP-CB-WATER`; (b) session → keep per-device; (c) harvest_window → surface as 15th goal; (d) date-data gap collapsed — succession DERIVED, days_in_nursery not a real gap, only planting_method + frost_class need a guided-entry tool (gates B-later only); (e) frost → region picker; (f) #13 → quantity-first comparison (not profit). No open decisions remain.

## 8. Recommended sequencing
1. **Phase A** (no prereqs, no engine rework, immediate value): transplants + seed_cost + compare → **6 → 9 live**.
2. **B0 → B-now** (date-engine foundations + harvest_window/succession/sow_date-direct) — **runs on existing data, NOT gated** on the enrichment WP → **9 → 12 live**.
3. **`WP-CB-CROPDATA-DATES`** (§9) — guided-entry tool fills planting_method + frost_class (in parallel with steps 1–2).
4. **B-later** (nursery + frost + transplant-accurate sow_date) → **12 → 15 live**, after the tool.
5. **`WP-CB-WATER`** (§9) — separate model+data effort, independent timeline.

Phase A and B-now can both start on team_00 go (no data prereq). Build runs on `claude/cb-followups-2026-06-07` (rebased on `main`; coordinate with the UI_REDESIGN session via Nimrod before merge), team_100 commits, with team_50 external visual QA + team_190 constitutional validation (IR#1/#5 — team_100 never self-issues the binding verdict).

## 9. Spin-off WPs (REGISTERED 2026-06-07)
These fell out of the resolved decisions and are now on the roadmap (REGISTER / L-GATE_E).

- **`WP-CB-WATER`** (decision #1) — `water` (#0) calculator: define an ET₀×Kc water model + add a per-crop **Kc** book field + region/month **ET₀** data (region axis can reuse the Phase-B frost region table). Model + data; medium-large; independent of WP-CB-CALC.
- **`WP-CB-CROPDATA-DATES`** (decisions #5/#7) — **rescoped much smaller** by the data investigation. Real work: **(a)** a **guided classification UI** (per-crop Q&A) for team_00 to fill the two categoricals — `planting_method` (39 to classify; add a `both` canonical value) + `frost_tolerance_class` (33, web-research-friendly); **(b)** `days_in_nursery` for the transplant/both crops the classification reveals (most known transplants already covered); **(c)** the server-side delivery plumbing from §3 (calc-controller whitelist + `crop_attribute` query + non-numeric channel). **NOT** in scope: `succession_interval_weeks` (now a calc derivation) and `days_to_maturity`/`harvest_window_max_days` (already ≈complete). Gates **B-later only**, not B-now.
