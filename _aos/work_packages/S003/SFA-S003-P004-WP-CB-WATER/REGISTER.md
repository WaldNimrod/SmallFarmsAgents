---
id: SFA-S003-P004-WP-CB-WATER-REGISTER
wp: SFA-S003-P004-WP-CB-WATER — water-need calculator (#0): model + data
gate: L-GATE_E (registered)
status: DEFERRED (team_00 2026-06-07) — revisit later
author: team_100
created: 2026-06-07
builder: TBD
validator: team_50
trigger: "water (#0) is the only calculator goal missing BOTH a model AND data — cannot be a Python→JS port."
design: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md (§0, §9)
---

# REGISTER — WP-CB-WATER (DEFERRED)

Spin-off from WP-CB-CALC (team_00 decision #1). `water` (#0) needs **both**:
- **a model** — none exists; e.g. weekly need = ET₀(region, month) × Kc(crop, stage) × area − effective rainfall;
- **new data** — a per-crop crop-coefficient (`Kc`) book field (does not exist) + region/month reference ET₀
  (the Israel region axis can reuse the WP-CB-CALC frost region table; Kc-per-crop must be sourced).

**Effort:** LARGE (agronomy data + model). **Status:** DEFERRED — the "בפיתוח" stub stays in `/calc` until this
ships. Builder TBD. No LOD until reactivated by team_00.
