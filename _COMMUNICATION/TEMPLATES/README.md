# CANONICAL TEMPLATE INDEX
# _COMMUNICATION/TEMPLATES/README.md
# Version: 1.0 | 2026-03-30 | Team 100

---
document_type: TEMPLATE_INDEX
version: "1.0"
---

# MyFarmAgents — Canonical Communication Templates

**Effective date:** 2026-03-30
**Maintained by:** Team 100 (Architecture)

> All inter-team communication **must** use these templates.
> Documents not conforming to these templates are informally valid but carry
> no binding authority for gate decisions or mandate obligations.

---

## Template Inventory

| Template | File | Used By | Purpose |
|----------|------|---------|---------|
| **Mandate** | `MANDATE.md` | Team 100, Nimrod | Issue work orders to implementing teams |
| **Completion Report** | `COMPLETION_REPORT.md` | Team 10, Team 20 | Report mandate completion + request next action |
| **QA Review Request** | `QA_REVIEW_REQUEST.md` | Team 10, Team 20 | Request Team 50 to execute a gate QA mandate |
| **QA Findings Report** | `QA_FINDINGS_REPORT.md` | Team 50 | Report gate QA results + gate decision |
| **Architectural Decision** | `ARCH_DECISION.md` | Team 100 | Record decisions, open/close gates, issue amendments |

---

## When to Use Each Template

### MANDATE
- **Trigger:** Team 100 (or Nimrod) assigns work to Team 10 or Team 20
- **Recipient:** Team 10 (`_COMMUNICATION/TEAM_10/`) or Team 20 (`_COMMUNICATION/TEAM_20/`)
- **Binding:** Yes — implementing team must complete all tasks or file a BLOCKED report
- **Filename:** `MANDATE_{TOPIC}_{TEAM_RECIPIENT}.md`

### COMPLETION REPORT
- **Trigger:** Implementing team finishes all tasks in a mandate
- **Recipient:** Team 100 (inform) + Team 50 (if gate QA needed)
- **Binding:** Triggers Team 50 QA when gate-related
- **Filename:** `{YYYY-MM-DD}_{TOPIC}_COMPLETE_TEAM{ID}.md`
- **Location:** `_COMMUNICATION/TEAM_{SENDER_ID}/reports/`

### QA REVIEW REQUEST
- **Trigger:** Implementing team files a completion report and requests gate QA
- **Recipient:** Team 50
- **Binding:** Yes — Team 50 must execute the referenced QA mandate
- **Filename:** `{YYYY-MM-DD}_G{N}_REVIEW_REQUEST_TEAM{SENDER_ID}.md`
- **Location:** `_COMMUNICATION/TEAM_50/reports/`

### QA FINDINGS REPORT
- **Trigger:** Team 50 completes gate QA mandate execution
- **Recipient:** Team 100 (primary) + implementing team (CC)
- **Binding:** Yes — gate status is only official via this report
- **Filename:** `{YYYY-MM-DD}_G{N}_QA_FINDINGS_TEAM50.md`
- **Location:** `_COMMUNICATION/TEAM_50/reports/`

### ARCH DECISION
- **Trigger:** Team 100 needs to record a gate decision, amendment, or binding ruling
- **Recipient:** All teams (or specific teams)
- **Binding:** Yes — overrides all other documents except Nimrod directives
- **Filename:** `{YYYY-MM-DD}_{TOPIC}_TEAM100.md`
- **Location:** `_COMMUNICATION/TEAM_100/reports/`

---

## Standard Communication Flow

```
Implementing Team           Team 100              Team 50
       │                       │                     │
       │  Read MANDATE         │                     │
       │◄──────────────────────│                     │
       │                       │                     │
       │  [implement work]     │                     │
       │                       │                     │
       │  COMPLETION_REPORT ──►│                     │
       │  + QA_REVIEW_REQUEST ─┼────────────────────►│
       │                       │                     │
       │                       │  [run QA mandate]   │
       │                       │                     │
       │◄──────────────────────┼─ QA_FINDINGS_REPORT │
       │                       │◄────────────────────│
       │                       │                     │
       │  [if PASS: next M]    │                     │
       │  [if FAIL: fix →loop] │                     │
```

---

## Mandatory Fields (all templates)

Every document must include:
- `document_type` — matches template name
- `version` — template version used
- `From:` / `To:` — explicit team identifiers
- `Date:` — ISO format `YYYY-MM-DD`
- Signature block at bottom

---

## Naming Conventions

```
Mandates:           MANDATE_{TOPIC}_{TEAM_RECIPIENT}.md
Completion Reports: {YYYY-MM-DD}_{TOPIC}_COMPLETE_TEAM{ID}.md
QA Review Request:  {YYYY-MM-DD}_G{N}_REVIEW_REQUEST_TEAM{ID}.md
QA Findings:        {YYYY-MM-DD}_G{N}_QA_FINDINGS_TEAM50.md
Arch Decisions:     {YYYY-MM-DD}_{TOPIC}_TEAM100.md
```

All filenames: `UPPERCASE_WITH_UNDERSCORES.md` (no spaces, no Hebrew).
