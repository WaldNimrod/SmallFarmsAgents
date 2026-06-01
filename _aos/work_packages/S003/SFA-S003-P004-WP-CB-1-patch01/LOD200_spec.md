---
id: SFA-S003-P004-WP-CB-1-patch01-LOD200
wp: SFA-S003-P004-WP-CB-1-patch01 — Crop Book v1 UI follow-ups
gate: L-GATE_E PASS → L-GATE_S (LOD200 → LOD400 pending)
status: DRAFT (LOD200) — opened 2026-06-01
author: team_100
date: 2026-06-01
depends_on: SFA-S003-P004-WP-CB-1
triggered_by: _COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_R3_v1.0.0.md
---

# LOD200 — SFA-S003-P004-WP-CB-1-patch01: UI follow-ups

> Carries the **non-blocking** follow-ups from the WP-CB-1 L-GATE_V PASS_WITH_FINDINGS (team_190 R3,
> verdict `8018df6`) plus the watercolor art wiring. None of these blocked the WP-CB-1 LOD500 lock.
> Direction only; the executable LOD400 follows and routes to team_190 L-GATE_S (non-Claude, IR#1).

## Scope — ALL ITEMS IMPLEMENTED 2026-06-01 (awaiting team_190 patch01 L-GATE_V)
1. ✅ **F-190-CB1-V-03 — JS↔Python calc parity (#7, #9, #12).** DONE — added
   testCalc7BedsForYieldParity / testCalc9RevenueParity / testCalc12FertilizerParity
   asserting the JS `CALC[...]` formulas match `calculators.py` (#1/#8/#10 already covered).
2. ✅ **Server-side filter execution on `book_index`.** DONE — `entry()` reads q/family/season/
   dtm_max (SQL) + sow/frost (payload post-filter); filter bar is a real GET form with an
   empty-state that keeps the bar (recoverable). 4 route tests (family/dtm/text/empty).
3. ✅ **`/calc` PDF/CSV export.** DONE — `GET /calc/export.{csv|pdf}` (HubController::calcExport):
   CSV download (UTF-8 BOM) + print-friendly auto-print HTML for PDF (no server PDF engine on
   the shared LAMP host). Buttons un-stubbed; JS appends the live plan as query params. 3 route tests.
4. ✅ **Watercolor art wiring.** DONE (commits up to 883437d) — 28 crop masters + hero + 3 home
   module-card heroes wired; every WC_ART/$wc_art_map ref verified to resolve.
5. ✅ **F-UI-01.** DONE (defensive fix) — the MySQL mirror has no crop_field_enrichment/
   crop_attribute tables, so `buildCb1Fields()` now falls back to the DEFAULT variety payload
   (agronomy{} + field_state{}) the ingest already ships → prov cues + calculators light up
   without those tables. Covered by testFieldStateLightsUpFromVarietyPayload. The full removal of
   the UNKNOWN degrade path stays deferred until the enrichment tables (or a richer payload) land.

## Out of scope
The locked WP-CB-1 UI itself (LOD500_LOCKED) — this patch only adds; it does not re-open locked behavior.
F-CB1-UI-01 (field_policy canon-alignment) stays with WP-CB-MIG2, not here.

## Execution shape (for the LOD400)
Builder team_10 (Claude); validator team_190 (non-Claude, IR#1). Delivery-tier only (`sfa_delivery/` +
`public_assets/`); no LOCKED Python backend or migration edits.
