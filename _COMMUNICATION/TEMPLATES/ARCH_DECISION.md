# CANONICAL TEMPLATE: ARCHITECTURAL DECISION
# File: _COMMUNICATION/TEMPLATES/ARCH_DECISION.md
# Version: 1.0 | 2026-03-30 | Team 100
#
# USAGE:
#   Used exclusively by Team 100 (Architecture) to formally record decisions,
#   open gates, issue amendments, or resolve disputes.
#   This is the only valid format for gate open/close decisions by Team 100.
#
#   Copy this file to:
#     _COMMUNICATION/TEAM_100/reports/<YYYY-MM-DD>_<TOPIC>_TEAM100.md
#   Fill every field. Remove all lines starting with '#'.
# =============================================================================

---
document_type: ARCH_DECISION
version: "1.0"
---

# Architectural Decision — <TOPIC>
**Decision ID:** ARCH-<YYYYMMDD>-<TOPIC_SLUG>
**From:** Team 100 (Architecture)
**To:** <All teams | Team <ID> | Team <ID>, Team <ID>>
**Date:** <YYYY-MM-DD>
**Type:** <GATE_DECISION | AMENDMENT | MANDATE | REVIEW | CLARIFICATION>

---

## 1. Context

<!-- What triggered this decision? Reference QA reports, completion reports,
     or escalations that led here. -->

<Background and triggering event.>

**References:**
- `<path/to/report.md>` — <brief description>
- `<path/to/mandate.md>` — <brief description>

---

## 2. Findings

<!-- What did Team 100 observe / conclude? -->

| Item | Finding | Severity |
|------|---------|----------|
| <Item> | <Observation> | Critical / High / Medium / Low |

---

## 3. Decision

<!-- State the decision clearly. If this is a gate decision, use the gate section below. -->

<Main decision text.>

### Gate Decision (if applicable)

| Gate | Status | Notes |
|------|--------|-------|
| G<N> | ✅ OPEN (PASS) / 🟡 OPEN (CONDITIONAL) / ❌ CLOSED (FAIL) / ⏸️ DEFERRED | <Notes> |

### Amendments (if applicable)

| Amendment ID | Target Document | Change |
|-------------|----------------|--------|
| AMD-<N> | `<path/to/document.md>` | <Description of change> |

---

## 4. Mandates Issued

<!-- List any new mandates triggered by this decision. -->

| Mandate | Team | File | Priority |
|---------|------|------|----------|
| <Topic> | Team <ID> | `<MANDATE_FILE.md>` | CRITICAL / HIGH / MEDIUM |

If no mandates issued: **None**.

---

## 5. Next Steps

| Team | Action | When |
|------|--------|------|
| Team <ID> | <What to do> | Immediately / Before G<N+1> |

---

*Issued by: Team 100 (Architecture)*
*Date: <YYYY-MM-DD>*
*This decision is binding on all teams unless overridden by Nimrod.*
