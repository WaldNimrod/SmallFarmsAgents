---
id: SFA-S003-P004-WP-CB-CROPDATA-DATES-REGISTER
wp: SFA-S003-P004-WP-CB-CROPDATA-DATES — crop date-field classification (guided-entry tool + plumbing)
gate: L-GATE_E (registered) → L-GATE_D design authored
status: OPEN — decision-complete; gates WP-CB-CALC Phase B-later
author: team_100
created: 2026-06-07
builder: team_10
validator: team_50
trigger: "WP-CB-CALC date calculators need planting_method + frost_class classified per crop (data investigation 2026-06-07)."
lod400: _aos/work_packages/S003/SFA-S003-P004-WP-CB-CROPDATA-DATES/LOD400_spec.md
mandate: _COMMUNICATION/team_35/MANDATE_CALC_MOCKUPS_2026-06-07.md (§5 entry-tool UI)
---

# REGISTER — WP-CB-CROPDATA-DATES

Spin-off from WP-CB-CALC. **Rescoped small** after measuring the PG SSoT (70 crops): the date-data gap
collapsed — `days_to_maturity` (66/70) + `harvest_window_max_days` (68/70) ≈ complete;
`succession_interval_weeks` dropped (now a calc derivation); `days_in_nursery` not a real gap (gated by
planting_method, 8/9 known transplants covered).

**Real work:** (a) a **guided classification tool** for team_00 to fill the two categoricals —
`planting_method` (add a `both` value) + `frost_tolerance_class`; (b) `days_in_nursery` for revealed
transplants; (c) the **server-side delivery plumbing** (calc-controller whitelist + crop_attribute query +
non-numeric channel) so the categoricals reach the calculator.

**Gates** WP-CB-CALC Phase B-later only (nursery/frost/transplant-accurate sow_date). Full detail → LOD400_spec.md.
