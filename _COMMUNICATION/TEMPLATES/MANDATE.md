# CANONICAL TEMPLATE: MANDATE
# File: _COMMUNICATION/TEMPLATES/MANDATE.md
# Version: 1.0 | 2026-03-30 | Team 100
#
# USAGE:
#   Copy this file to: _COMMUNICATION/TEAM_{RECIPIENT}/MANDATE_{TOPIC}_{TEAM_RECIPIENT}.md
#   Fill every field marked with <ANGLE_BRACKETS>.
#   Remove all lines starting with '#'.
#   A mandate is ONLY valid when signed by Team 100 or the project lead (Nimrod).
# =============================================================================

---
document_type: MANDATE
version: "1.0"
---

# Mandate — <TOPIC>
**Mandate ID:** MANDATE-<YYYYMMDD>-<TOPIC_SLUG>
**From:** Team <SENDER_ID> (<SENDER_NAME>)
**To:** Team <RECIPIENT_ID> (<RECIPIENT_NAME>)
**Date:** <YYYY-MM-DD>
**Priority:** <CRITICAL | HIGH | MEDIUM>
**Gate dependency:** <e.g. "Blocks G3" | "Does not block current gate">
**Status:** ACTIVE

---

## 1. Context

<!-- Why does this mandate exist? What problem does it solve?
     Include references to previous reports, gates, or decisions that led here. -->

<Brief explanation of what happened / why this work is needed.>

**Triggered by:** <e.g. "G3 QA FAIL — T02 StringDataRightTruncation" | "Architectural decision ARCH-2026-03-30">
**Related documents:**
- <path/to/relevant_report_or_mandate.md>
- <path/to/another_reference.md>

---

## 2. Requirements

<!-- Number every task. Each task must be independently verifiable.
     Provide exact code snippets, SQL, or commands where precision matters. -->

### Task 1 — <Short Task Name>

<Detailed description of what must be done.>

```<language>
# Exact code / command / SQL to implement
```

**Acceptance criterion:** <Exactly what "done" looks like — a test output, a DB query result, a log line.>

---

### Task 2 — <Short Task Name>

<Detailed description.>

**Acceptance criterion:** <Verifiable condition.>

---

<!-- Add more tasks as needed. Do not exceed 7 tasks in a single mandate.
     If more work is needed, issue a follow-up mandate. -->

---

## 3. Out of Scope

<!-- Explicitly state what is NOT part of this mandate to prevent scope creep. -->

- <Thing Team should NOT do>
- <Thing that belongs to a different team or a later milestone>

---

## 4. Verification Checklist

Run these before submitting the completion report:

```bash
# Example verification commands
python3.11 -m pytest tests/ -q          # all tests pass
alembic current                          # correct revision
python3.11 -m organic_market_agent.db.check  # RESULT: PASS
```

Expected results:
- [ ] <Specific outcome 1>
- [ ] <Specific outcome 2>
- [ ] <All existing tests still pass (no regression)>

---

## 5. Completion Report

When all tasks are complete, file a **Completion Report** using the canonical template:
`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_<RECIPIENT_ID>/reports/<YYYY-MM-DD>_<TOPIC>_COMPLETE_TEAM<RECIPIENT_ID>.md`

Include this Mandate ID in the report header.

If this mandate unblocks a QA gate, also file a **QA Review Request** using:
`_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md`

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_<RECIPIENT_ID>/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide

---

*Issued by: Team <SENDER_ID> (<SENDER_NAME>)*
*Date: <YYYY-MM-DD>*
*Authorized by: Team 100 (Architecture)*
