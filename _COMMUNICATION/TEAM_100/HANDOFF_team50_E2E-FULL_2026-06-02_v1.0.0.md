---
id: HANDOFF_team50_E2E-FULL_2026-06-02
from: team_100
to: team_50
cc: [team_00]
date: 2026-06-02
type: SESSION_HANDOFF
depth: full
mission: Full E2E QA of the entire SFA delivery system (live, browser-driven, run from the server)
target_site: https://sfa.nimrod.bio
repo_state: main @ ce7b07f (deployed to uPress 2026-06-02)
---

# Handoff — team_50 · FULL E2E QA of the entire SFA system (live)

## Mission TL;DR
Run a **complete, browser-driven end-to-end QA** of the entire live SFA delivery system at
**https://sfa.nimrod.bio**, executed **from waldhomeserver** (headless Chromium / Playwright). Exercise
**every** interface in a real browser, **validate the data** on each page, confirm **every interface is
healthy**, and **validate every calculator computation** (all 14 calcs + the calculator dashboard + the
AssumptionFields). Produce one E2E QA report with per-area PASS/FAIL + findings. **Read-only on production —
report, do not fix or mutate.**

## Why now — what just deployed (validate against this)
A large data + UI deployment landed 2026-06-02 (team_100, team_00-approved). You are validating it end-to-end:
- **Crop Data Model Expansion (WP-CB-MIG2, LOD500_LOCKED):** 13-topic taxonomy, 7 new field groups +
  `needs_summer_shade`, migration 060 (`seeder_settings`), attribute/enrichment wiring, NI importer.
- **F-DATA-001 family fix:** 26 crops re-pointed off a bad `Aizoaceae` fallback to correct botanical
  families (tomato→Solanaceae, carrots→Apiaceae, lettuce→Asteraceae, cucumbers→Cucurbitaceae, …). New
  Zealand Spinach legitimately stays Aizoaceae.
- **Ingest fix:** `_fetch_crops` had queried a column dropped by migration 059 → all crop pushes had been
  frozen since 059; now fixed and re-pushed (crops/varieties/products accepted HTTP 200).
- **UI deploy:** crop-book-v1 UI (`crop-book-v1.css`/`.js`, watercolor art, Carmela font) deployed via FTPS
  (were 404 — the E2E "F-OPS-001" deploy drift; now 200).

## Scope — exercise ALL of it in a real browser

### A. Interface health (every route)
Hit every route, confirm **HTTP 200** (or correct redirect), **RTL legible**, **zero JS console errors**, no
raw entity keys / `Array` dumps / unrendered placeholders, and **mobile-responsive** (test ≥1 narrow viewport):
- `/` (home/hub) · `/market` (price index) · `/crop-book/` (crop list)
- `/crop-book/{slug}/` (crop detail — test several: tomatoes, carrots, lettuce, cucumbers, eggplant, chard)
- `/crop-book/family/{slug}` (family pages — e.g. `solanaceae`, `apiaceae` — confirm redirects, no 404)
- `/calc` (calculator dashboard) · `/clients/` · any auxiliary routes you discover in the nav.

### B. Data validation (per page)
- **Family taxonomy correct** on crop pages + the API: tomato→**Solanaceae** (סולניים), and spot-check
  carrots/lettuce/cucumbers/eggplant/beets/garlic/onions. Confirm **no crop shows Aizoaceae except New
  Zealand Spinach**.
- Crop detail renders all **13 topics in order** (זנים → ציוד וכיוונון → … → מזיקים ומחלות → קציר → רצף וחברה),
  agronomy values present where data exists, `field_state` cues (VALIDATED/UNVALIDATED) sane.
- **"מוצע" (proposed) fields** render as proposed where data hasn't landed (needs_summer_shade, irrigation_type,
  root_depth_class, unit_size, sale_unit, drip_lines_per_bed + the newly-wired seeder_settings, common_pests,
  foliar_feeding_program, labor_rate_*, plantings_per_season, harvest_weeks_span). These being empty/"מוצע" is
  EXPECTED (PR backfill + the NI validation-console cycle haven't run yet) — flag only if they render broken.
- **Watercolor art loads** (28 crop masters + hero + module heroes); confirm no broken `<img>` / glyph
  fallback where a master exists.
- Market page: disclaimer present, prices match `/api/v1` (spot-check one product), filters work.

### C. Calculator validation (the heart of this pass)
Validate **all 14 calculators** — both the per-crop in-context calculator overlays AND the full `/calc`
dashboard — for **numerical correctness** (recompute by hand / cross-check against the Python reference in
`organic_market_agent/crop_book/calculators.py`), correct units, and **JS↔Python parity**:
1. `seed_quantity_to_buy` 2. `transplants_needed` 3. `nursery_trays_and_sow_date`
4. `sowing_date_from_harvest` 5. `harvest_window_from_sowing` 6. `succession_schedule`
7. `beds_for_target_yield` 8. `expected_yield` 9. `expected_revenue` 10. `plant_population`
11. `frost_planting_window` 12. `fertilizer_compost_rate` 13. `crop_profit_comparison` 14. `seed_input_cost`
- **AssumptionFields**: verify the user-adjustable assumptions (germination 90%, bed width 0.8 m, etc.) flow
  into the math and changing them re-computes correctly (per-session persistence per design Q1).
- **Exports**: `/calc` CSV + print-PDF export produce correct content.
- **Known latent (verify, don't fix):** `crop-book-v1.js CALC.revenue` does **no non-kg unit conversion**
  (F-50-patch01-01). It's currently unreachable (sale_unit/unit_size not yet populated) — confirm it doesn't
  mis-compute for any crop that has a documented non-kg price; report if reachable.

### D. API validation
- `/api/v1/health` ok; `/api/v1/crops/{slug}` returns correct identity/family/agronomy; `/api/v1/contribute`
  (the "request info" CTA) behaves (note: it returned **404** in the prior sweep — verify it's wired now).
- Cross-check a few API values against what the browser renders (no drift between API and UI).

## How to run (from the server)
- Run from **waldhomeserver** (it has Playwright/headless Chromium; the live site is on uPress). Target the
  **live** site `https://sfa.nimrod.bio` (not a local server). Capture screenshots + console logs per interface.
- Do **not** mutate production data, do **not** POST to `/api/v1/ingest`, do **not** commit. This is observation only.

## Output
Write **`_COMMUNICATION/TEAM_50/SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md`** with:
- A per-area table (A interface-health / B data / C calculators / D API) with PASS / PARTIAL / FAIL + evidence
  (screenshot refs, URLs, computed-vs-expected values).
- A prioritized findings list (severity + repro), separating real defects from expected-empty "מוצע" states.
- An overall verdict (PASS / PASS_WITH_FINDINGS / FAIL) and the top items for team_100.
Route a short completion MSG to `_COMMUNICATION/team_100/` (ADR043 naming).

## Constraints / Iron Rules
- **Read-only on production.** No data mutation, no deploys, no git state changes (a prior build sub-agent
  corrupted the branch graph — do not run `git checkout/reset/commit`).
- You are **team_50 QA (Claude)** — this is internal QA. It does **not** substitute for a team_190 non-Claude
  constitutional gate (IR#1/#5); it informs team_100.
- Be skeptical and specific — your value is catching what's actually broken on the live site, not rubber-stamping.

---

## ACTIVATION PROMPT (copy-paste to start the team_50 session on the server)

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_50 only

# Agent Onboarding — team_50 (QA) · FULL live E2E

You are team_50 (QA, Claude) in the AOS spoke SmallFarmsAgents. Mission: a COMPLETE, browser-driven
end-to-end QA of the entire live SFA system at https://sfa.nimrod.bio, run from waldhomeserver
(headless Chromium / Playwright). Repo: /data/projects/smallfarmsagents (or the Mac checkout) @ main ce7b07f.

Validate the 2026-06-02 deployment: WP-CB-MIG2 crop data model + F-DATA-001 family fix (tomato→Solanaceae)
+ crop-book-v1 UI + migration 060 + the ingest fix.

DO, in a real browser, capturing screenshots + console logs:
1. INTERFACE HEALTH — every route 200/correct-redirect, RTL, zero console errors, no raw keys/Array, mobile:
   / , /market , /crop-book/ , /crop-book/{slug}/ (tomatoes/carrots/lettuce/cucumbers/eggplant/chard),
   /crop-book/family/{solanaceae,apiaceae} , /calc , /clients/ .
2. DATA — family taxonomy correct (tomato→Solanaceae; no crop on Aizoaceae except New Zealand Spinach);
   13 topics render in order; agronomy values present; "מוצע" proposed fields render as proposed (empty is
   EXPECTED — PR/NI backfill not run yet); watercolor art loads (no broken images); market prices match API.
3. CALCULATORS — validate ALL 14 for numerical correctness + units + JS↔Python parity (reference
   organic_market_agent/crop_book/calculators.py): seed_quantity_to_buy, transplants_needed,
   nursery_trays_and_sow_date, sowing_date_from_harvest, harvest_window_from_sowing, succession_schedule,
   beds_for_target_yield, expected_yield, expected_revenue, plant_population, frost_planting_window,
   fertilizer_compost_rate, crop_profit_comparison, seed_input_cost. Verify AssumptionFields (germ 90%,
   bed 0.8m) re-compute on change; /calc CSV + print-PDF export; the F-50-patch01-01 revenue non-kg note.
4. API — /api/v1/health, /api/v1/crops/{slug}, /api/v1/contribute (was 404 — verify); UI↔API no drift.

CONSTRAINTS: read-only on production — no data mutation, no /api/v1/ingest POST, no deploys, NO git
state changes (no checkout/reset/commit). team_50 QA ≠ team_190 constitutional gate (IR#1/#5).

OUTPUT: _COMMUNICATION/TEAM_50/SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md — per-area PASS/FAIL
table (interface/data/calculators/API) with evidence + a prioritized findings list + overall verdict.
Notify team_100 via _COMMUNICATION/team_100/ (ADR043 MSG). Be skeptical and specific.

First action: open https://sfa.nimrod.bio/crop-book/ in the browser, confirm it renders the v1 UI
(crop-book-v1.css/js 200, watercolor hero), then work through scopes 1→4 systematically.
```

-- team_100 (Chief System Architect)
