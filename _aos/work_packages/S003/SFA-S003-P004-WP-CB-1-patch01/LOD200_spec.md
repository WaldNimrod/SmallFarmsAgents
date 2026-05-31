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

## Scope
1. **F-190-CB1-V-03 — JS↔Python calc parity (#7, #9, #12).** A headless parity fixture; today only
   #1/#8/#10 are asserted. Extend the existing `crop-book-v1.js CALC[...]` parity approach.
2. **Server-side filter execution on `book_index`.** The multi-param filter rail is UI-only (client
   chips); wire family / season / sow-method / frost / DTM-range / completeness to the controller query.
3. **`/calc` PDF/CSV export.** `GET /calc/export.pdf` + `export.csv` are stubs (`aria-disabled`); implement
   server-side plan render.
4. **Watercolor art wiring.** Build 720px derivatives (`scripts/wc_derivatives.sh`) for the confirmed new
   masters (tomato, cucumber, beet, pepper — see `CROP_ART_MASTERS/`) + extend the art maps
   (`CropBookViewController::WC_ART`, `book_entry.php $wc_art_map`, `ICON_MAP` add `beet`), replacing the
   emoji/glyph fallback. Lands as art batches are confirmed (more incoming; see CROP_ART_MASTERS/README open items).
5. **F-UI-01 closure.** Once the backend ingest deploys per-field `field_state` to the MySQL mirror, drop the
   defensive UNKNOWN-cue degrade path in `prov_value.php`.

## Out of scope
The locked WP-CB-1 UI itself (LOD500_LOCKED) — this patch only adds; it does not re-open locked behavior.
F-CB1-UI-01 (field_policy canon-alignment) stays with WP-CB-MIG2, not here.

## Execution shape (for the LOD400)
Builder team_10 (Claude); validator team_190 (non-Claude, IR#1). Delivery-tier only (`sfa_delivery/` +
`public_assets/`); no LOCKED Python backend or migration edits.
