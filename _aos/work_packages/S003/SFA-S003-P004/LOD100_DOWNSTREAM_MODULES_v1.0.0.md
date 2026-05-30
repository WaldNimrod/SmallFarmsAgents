# LOD100 — SFA-S003-P004 Downstream Modules (CB-2..CB-5) — team_100 — v1.0.0

**Date:** 2026-05-30
**Author:** team_100 (Chief System Architect, Claude Code)
**Type:** LOD100 (brief direction only — NOT for execution)
**Program:** SFA-S003-P004 (ספר גידולים / Crop Book)
**Status:** PLACEHOLDER briefs. Activate (LOD200+) only after `SFA-S003-P004-WP-CB-1` LOD500_LOCKED and team_00 prioritization.

---

## Purpose

Crop Book v1 (`WP-CB-1`) owns **agronomic knowledge + the 14 calculators only**. These four modules are FUTURE consumers of WP-CB-1's typed calculator outputs (LOD400 §12 API contracts). This LOD100 records brief direction and the module boundary so WP-CB-1 designs stable contracts now. Each gets its own LOD200 when prioritized.

---

## WP-CB-2 — Planner v0 (bed-map / season plan)
**Direction:** Assign crops to physical beds across a season. **Consumes:** `beds_for_target_yield` (#7), `plant_population` (#10), `succession_schedule` (#6), sow/harvest dates (#4/#5). **Owns:** scheduling + bed layout. **Reads** agronomic truth from Crop Book; never re-derives it.

## WP-CB-3 — Tasks (crop task scheduling)
**Direction:** Generate dated field tasks. **Consumes:** `crop_task_templates` (already seeded from JMF) anchored on sow/transplant/harvest dates (#4/#5) + seed/tray procurement (#1/#3). **Owns:** task timeline. **Reads** anchors from Crop Book + Planner.

## WP-CB-4 — Sales / POS
**Direction:** Revenue planning + point-of-sale. **Consumes:** `expected_revenue` (#9), `crop_profit_comparison` (#13), `seed_input_cost` (#14) + `documented_price` + OMA market index (MK class). **Owns:** transactions. **Reads** economics from Crop Book.

## WP-CB-5 — Tend integration (operational write-back loop)
**Direction:** Feed real farm operational data (Tend exports — already an OP-class source) back into enrichment, closing book-vs-reality. **Consumes:** `crop_field_enrichment` + provenance. **Writes:** OP-class `source_values` that re-reconcile. **Owns:** the ops feedback loop.

---

## Module boundary (locked)
Crop Book = agronomic knowledge + calculators. CB-2..CB-5 are downstream; they consume calculator outputs via the LOD400 §12 contracts and do not reach into the enrichment/reconciler internals (except CB-5's sanctioned OP-class write-back). LOD200+ deferred per WP; not for execution until WP-CB-1 closes.
