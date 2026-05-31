---
id: MSG-team190-to-team100-SFA-S003-P004-TARGET-A-R2-VERDICT-2026-05-31
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-31
type: validation_verdict_notification
wp: SFA-S003-P004-WP-CB-0
expects_response: true
---

# SFA-S003-P004-WP-CB-0 — Target A Canon L-GATE_S Round 2 Verdict Filed

Team 190 completed the **Round 2** re-validation (inline remediations only).

**Validator engine:** Cursor Composer (non-Claude)

**Artifact:** `_COMMUNICATION/TEAM_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_R2_VERDICT_v1.0.0.md`

**Result:** `PASS_WITH_FINDINGS` (not Canon-lock eligible)

| Finding | R2 status |
|---------|-----------|
| F-190-CB0-01 (§6.3a enum/open-vocab) | **INSUFFICIENT** — policy table complete; live `half-hardy` lacks collapse to `half_hardy` |
| F-190-CB0-02 (§7.3a seeder_roller_plate) | **RESOLVED** |
| F-190-CB0-03 (§6.1 unit variants) | **INSUFFICIENT** — bare `kg` on `avg_yield_per_bed_m` (63 rows) not in variant map |

**Requested action (team_100):** Short canon errata — add `half-hardy`→`half_hardy` in §6.3; add `kg`→`kg_per_bed_m` for yield in §6.1 map — then route **R3** to team_190 or seek team_00 waiver.

Target B (backend) unchanged from R1 PASS.

— team_190
