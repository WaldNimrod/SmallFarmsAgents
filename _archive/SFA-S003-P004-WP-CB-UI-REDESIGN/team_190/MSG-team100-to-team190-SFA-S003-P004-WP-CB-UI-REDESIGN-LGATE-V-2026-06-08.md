---
from: team_100
to: team_190
type: task
date: 2026-06-08
subject: "L-GATE_VALIDATE for SFA-S003-P004-WP-CB-UI-REDESIGN — Round #1"
related_wp: SFA-S003-P004-WP-CB-UI-REDESIGN
mandate_ref: _COMMUNICATION/team_190/MANDATE_SFA-S003-P004-WP-CB-UI-REDESIGN_L-GATE_VALIDATE_v1.0.0.md
expects_response: true
engine_constraint: "cross-engine: builder=claude-code → validator MUST be non-Claude (Cursor/Codex/Desktop)"
---

## Task: L-GATE_VALIDATE — SFA-S003-P004-WP-CB-UI-REDESIGN (Round #1)

The full SFA public redesign (7 surfaces + calc re-skin + internal tool) is built on
branch `feat/wp-cb-ui-redesign` (baseline `8d03f2e` → HEAD `f71dfbc`) and routed for the
constitutional gate.

**Mandate:** `_COMMUNICATION/team_190/MANDATE_SFA-S003-P004-WP-CB-UI-REDESIGN_L-GATE_VALIDATE_v1.0.0.md`
(10 validation criteria VC-1..VC-10).

**Cross-engine (IR#1/#5):** builder was Claude Code — **validate on a non-Claude engine**
(Cursor / Codex / Desktop). Do NOT validate on Claude Code.

**Verdict path:** `_COMMUNICATION/team_190/VERDICT_SFA-S003-P004-WP-CB-UI-REDESIGN_L-GATE_VALIDATE_v1.0.0.md`

Key checks: re-run the PHP suite (226 expected) + `qa_probe.mjs` (16/16, no overflow) yourself;
confirm the **WP-CB-CALC engine is byte-untouched** (`git diff 8d03f2e..HEAD -- sfa_delivery/public_assets/js/crop-book-v1.js` empty); honest empty-states / no fabrication; `validate_aos.sh` 0 FAIL.
