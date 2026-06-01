# BUILD_REPORT — SFA-S003-P004-WP-CB-1-patch01 — v1.0.0

**Date:** 2026-06-01 · **Builder:** team_10 (Claude) · **QA:** team_50 (independent) · **Branch:** `claude/wp-cb-1-ui-2026-05-31` · **Commit:** `ba68b38`

## §1 Summary
Closes all WP-CB-1 L-GATE_V PASS_WITH_FINDINGS follow-ups (verdict 8018df6) — delivery-tier only,
no LOCKED Python backend or migration touched.

## §2 Scope delivered (5 LOD200 items)
| Item | Implementation | Files |
|------|----------------|-------|
| V-03 parity #7/#9/#12 | JS `CALC[...]` == `calculators.py` asserted | `tests/CropBookV1MacroTest.php` |
| Server-side filters | `entry()` q/family/season/dtm_max (SQL) + sow/frost (payload); GET form; recoverable empty-state | `CropBookViewController.php`, `book_entry.php`, `crop-book-v1.css` |
| /calc export | `GET /calc/export.{csv,pdf}` — CSV (UTF-8 BOM) + print-PDF; buttons un-stubbed; JS plan→params | `HubController.php`, `routes.php`, `calc_export_print.php`, `calc_dash.php`, `crop-book-v1.js` |
| F-UI-01 | `buildCb1Fields()` falls back to default-variety payload (agronomy + field_state) | `CropBookViewController.php` |
| Art wiring | (done in prior patch01 commits up to 883437d) 28 crops + hero + 3 module heroes | — |

## §3 AC / evidence
- `composer test` → **107 / 313 assertions / 0 failures** (was 96). 11 new tests, all green.
- `php -l` clean on all 8 changed PHP files.
- Parity independently recomputed by QA: #7 (300/3/30→3.33), #9 (3.5×30×12→1260), #12 (120/50m²→80kg) — JS == Python.
- Filters proven by route tests (family / dtm_max / text / empty-state recovers).
- Export proven by route tests (CSV headers + body; PDF print HTML).
- F-UI-01 proven by `testFieldStateLightsUpFromVarietyPayload` (cues light from payload, no enrichment table).

## §4 Findings (from QA)
- **F-50-patch01-01 (LOW, latent, out-of-scope):** `crop-book-v1.js CALC.revenue` uses `book.price` as ₪/kg with
  **no non-kg unit conversion**, whereas `calculators.py expected_revenue` converts via `kg_per_unit`. Not reachable
  today (prices stored per-kg; dashboard panel has no price `[data-book]`), and the V-03 charter is the per-kg path.
  Pre-existing JS property, not introduced here. Flag to team_190; track for a future non-kg-priced variety.

## §5 Verification output
- `validate_aos.sh .` → **29 PASS / 19 SKIP / 0 FAIL** (clean tree).
- `pytest tests/crop_book/` → **631 passed / 2 pre-existing fail / 1 skip** (no Python touched).
- Constitutional: `git diff --name-only main..HEAD` → no calc/model/*.py, no migration.

## §6 Artifacts
Created: `calc_export_print.php`. Modified: controllers (CropBookView, Hub), routes, book_entry, calc_dash,
crop-book-v1.{js,css}, both test files, patch01 LOD200.

## §7 Next
team_190 (non-Claude) patch01 L-GATE_V per the mandate. On PASS → patch01 LOD500_LOCKED.
