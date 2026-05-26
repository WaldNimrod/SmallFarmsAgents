---
id: PRE_APPROVAL_REQUEST_SFA-CROP-DATA-SCOUT_2026-05-26
from: team_10 (acting as orchestrator on this spoke)
to: team_00
date: 2026-05-26
type: TEAM_80_KICKOFF_PREAPPROVAL
binding_directive: "ADR046 §2.6 Rule 3 (pre-approval template at every team_80 kickoff)"
mission_ref: _COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/MISSION_v1.0.0.md
status: AWAITING_TEAM_00
---

# TEAM_80 RESEARCH KICKOFF — METHOD + ENGINE PLAN PROPOSED

```
Mandate:   SFA-CROP-DATA-SCOUT-2026-05-26
Topic:     Scout free/open crop data sources to complement SFA crop book
SLA:       2 days
Cost cap:  $5

RECOMMENDED METHOD: mixed (primary: MCP; secondary: manual_hybrid)

Reasoning for this case:
  - Target sources are heterogeneous (USDA, FAO, university extensions,
    Israeli MoA, Hebrew sites) — no single search engine covers all.
  - Perplexity MCP excels at structured discovery + citation extraction
    from English authoritative sources (USDA, FAO, US extensions).
  - Hebrew/Israeli sources (שה"ם, וולקני) typically need direct WebFetch
    on .gov.il / .agri.gov.il URLs — Perplexity coverage is weaker for
    these. Manual_hybrid handles this layer.
  - No API mode needed — this is high-volume / low-criticality discovery
    work (Rule 2 reserves API credits for production).

PROPOSED ENGINE PLAN:
  - Perplexity MCP × ~12 queries (mode: mcp)
      Reasoning: English-language source discovery (USDA, FAO, university
        extensions, organic farming networks). Perplexity returns citations
        which we can validate against URL accessibility.
      Estimated cost: $0  (Perplexity subscription = flat-rate)
      Estimated time: 25 minutes

  - WebFetch (manual_hybrid) × ~8 fetches (mode: manual)
      Reasoning: Validate URLs returned by Perplexity; pull Hebrew/Israeli
        sources directly (שה"ם, וולקני, משרד החקלאות) where Perplexity
        coverage is thin.
      Estimated cost: $0
      Estimated time: 20 minutes

  - Manual review + write-up (mode: manual)
      Reasoning: Compose FINDINGS_v1.0.0.md in the prescribed 14-parameter
        format, validate samples, write recommendation rationales.
      Estimated cost: $0  (no API calls)
      Estimated time: 30 minutes

TOTAL ESTIMATE: $0 / 75 minutes / 20 queries
```

---

## Pre-approval block — what team_00 controls

team_00 may:
- **CONFIRM**: proceed exactly as proposed
- **MODIFY**: change scope, cost cap, SLA, recommended method, or engine plan
  before execution
- **DEFER**: postpone the mission (e.g., until WP-C is scoped)

team_10 will NOT activate team_80 until explicit CONFIRM or MODIFIED-then-CONFIRM
from team_00.

---

## Cross-rule compliance audit

| Rule | Status | Evidence |
|------|--------|----------|
| ADR046 §2.6 Rule 1 (method recommended per case + reasoning) | ✅ | "mixed" recommended with reasoning above |
| ADR046 §2.6 Rule 2 (API discouraged + cost reasoning) | ✅ | No API mode in plan; reason: research is high-volume/low-criticality |
| ADR046 §2.6 Rule 3 (pre-approval template at every kickoff) | ✅ | This block (per template format) |
| team_80 IR#3 (activation requires explicit team_00 instruction) | ⏳ | Awaiting your CONFIRM/MODIFY/DEFER |
| Iron Rule #4 (single roadmap writer) | N/A | This is a scout mission, no roadmap mutation |
| Iron Rule #1 (cross-engine) | N/A | Scout is advisory, no gate verdict |

---

*PRE_APPROVAL_REQUEST | team_10 → team_00 | issued 2026-05-26*
