# CANONICAL TEMPLATE: QA REVIEW REQUEST
# File: _COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md
# Version: 1.0 | 2026-03-30 | Team 100
#
# USAGE:
#   This template is filed by the implementing team (Team 10 or Team 20)
#   addressed TO Team 50 (QA), requesting execution of the gate QA mandate.
#
#   Copy this file to:
#     _COMMUNICATION/TEAM_50/reports/<YYYY-MM-DD>_G<N>_REVIEW_REQUEST_TEAM<YOUR_ID>.md
#   Fill every field. Remove all lines starting with '#'.
#   Team 50 must acknowledge this request within the same session.
# =============================================================================

---
document_type: QA_REVIEW_REQUEST
version: "1.0"
---

# QA Review Request — Gate G<N>
**Request ID:** QA-REQ-<YYYYMMDD>-G<N>
**From:** Team <SENDER_ID> (<SENDER_NAME>)
**To:** Team 50 (QA)
**Date:** <YYYY-MM-DD>
**Gate:** G<N> — <Gate description, e.g. "Normalizer Engine">
**Milestone:** M<N> — <Milestone name>
**QA Mandate:** `_COMMUNICATION/TEAM_50/<QA_MANDATE_FILENAME>.md`
**Priority:** <CRITICAL | HIGH>

---

## 1. What Was Completed

<!-- Reference the completion report(s) filed for this gate. -->

| Team | Mandate | Completion Report |
|------|---------|------------------|
| Team <ID> | `<MANDATE_FILE.md>` | `<COMPLETION_REPORT_FILE.md>` |
| Team <ID> | `<MANDATE_FILE.md>` | `<COMPLETION_REPORT_FILE.md>` |

---

## 2. Pre-conditions Confirmed

<!-- The requesting team must verify these before filing this request.
     Team 50 will re-verify independently. -->

- [ ] Alembic revision is at head (`alembic current` → `<expected_revision>`)
- [ ] `python3.11 -m organic_market_agent.db.check` → RESULT: PASS
- [ ] `python3.11 -m pytest tests/ -q` → `<N> passed, 0 failed`
- [ ] Docker postgres container running (`docker ps | grep postgres`)
- [ ] `.env` set correctly (`DATABASE_URL` points to live Docker DB)
- [ ] <Any gate-specific pre-condition>

---

## 3. Known Issues at Time of Request

<!-- List any known issues that do NOT block the gate, but Team 50 should be aware of. -->

| Issue | Impact | Expected QA Behavior |
|-------|--------|----------------------|
| <Issue> | LOW / MEDIUM | <How Team 50 should classify this> |

If there are no known issues, write: **None**.

---

## 4. Request to Team 50

Please execute the QA mandate:
`_COMMUNICATION/TEAM_50/<QA_MANDATE_FILENAME>.md`

File your findings report using the canonical template:
`_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_50/reports/<YYYY-MM-DD>_G<N>_QA_FINDINGS_TEAM50.md`

---

*Issued by: Team <SENDER_ID> (<SENDER_NAME>)*
*Date: <YYYY-MM-DD>*
