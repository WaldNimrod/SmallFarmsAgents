---
id: SFA-S003-P004-WP-CB-CALC-REGISTER
wp: SFA-S003-P004-WP-CB-CALC — calculator completion (6/14 → 15 goals)
gate: L-GATE_E (registered) → L-GATE_D design authored
status: OPEN — decision-complete; awaits team_35 mockups (presentation) + team_00 build go
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50
trigger: "Carried forward from WP-CB-MOBILE (LOD500_LOCKED). 8/14 calculator goals dead-end on 'בפיתוח'."
lod400: _aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/LOD400_spec.md
design: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
mandate: _COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md
---

# REGISTER — WP-CB-CALC

Complete the planning calculator: from 6 live goals to **15**, by porting the already-tested Python
calculators to JS, adding a JS date engine, a typed result layer, and widening the server delivery.

**team_00 decisions (2026-06-07):** hero metric = quantity (not profit); #13 reframed to a quantity-first
crop comparison; `water`(#0) split to `WP-CB-WATER`; `harvest_window`(#5) surfaced as the 15th goal;
frost = region picker; succession = derived `round(harvest_window_max_days/7)`; session stays per-device.

**Phasing:** Phase A (transplants/seed_cost/compare → 9) · Phase B-now (harvest_window/succession/sow_date-direct
→ 12, existing data, un-gated) · Phase B-later (nursery/frost/transplant sow_date → 15, gated on
`WP-CB-CROPDATA-DATES`).

**Status:** design + LOD400 authored. Presentation layer owned by team_35 (mandate issued; team_100 awaits
mockups). Build gated on team_00 go. Full detail → LOD400_spec.md.
