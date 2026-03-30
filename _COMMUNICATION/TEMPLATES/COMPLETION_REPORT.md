# CANONICAL TEMPLATE: COMPLETION REPORT
# File: _COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md
# Version: 1.0 | 2026-03-30 | Team 100
#
# USAGE:
#   Copy this file to:
#     _COMMUNICATION/TEAM_{YOUR_ID}/reports/<YYYY-MM-DD>_<TOPIC>_COMPLETE_TEAM<YOUR_ID>.md
#   Fill every field marked with <ANGLE_BRACKETS>.
#   Remove all lines starting with '#'.
#   File this report as soon as ALL tasks in the mandate are complete.
# =============================================================================

---
document_type: COMPLETION_REPORT
version: "1.0"
---

# Completion Report — <TOPIC>
**Report ID:** REPORT-<YYYYMMDD>-<TOPIC_SLUG>
**Mandate ID:** MANDATE-<YYYYMMDD>-<TOPIC_SLUG>
**From:** Team <SENDER_ID> (<SENDER_NAME>)
**To:** Team <RECIPIENT_ID> (<RECIPIENT_NAME>)
**Date:** <YYYY-MM-DD>
**Mandate status:** COMPLETE | COMPLETE WITH DEVIATIONS | PARTIAL
**Gate readiness:** <e.g. "Ready for G3 QA" | "Not gate-related">

---

## 1. Summary

<!-- One paragraph. What was implemented, why, and what changed in the system. -->

<Summary of the completed work.>

---

## 2. Tasks Completed

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | <Task name from mandate> | ✅ DONE | <Brief note or deviation, if any> |
| 2 | <Task name from mandate> | ✅ DONE | |
| 3 | <Task name from mandate> | ⚠️ DEVIATION | <Explain why and what was done instead> |

---

## 3. Evidence

<!-- Paste actual terminal output, SQL results, and test output.
     Do NOT summarize — paste verbatim output. -->

### 3.1 Test Suite

```
<paste pytest -q output here>
```

### 3.2 DB Health Check

```
<paste python -m organic_market_agent.db.check output here>
```

### 3.3 <Additional Evidence — Task-Specific>

```
<paste alembic upgrade output, CLI run output, SQL query results, etc.>
```

---

## 4. Deviations from Mandate

<!-- If the mandate was followed exactly, write "None". -->

| Deviation | Reason | Team 100 approval needed? |
|-----------|--------|--------------------------|
| <What changed> | <Why> | Yes / No |

If Team 100 approval is needed, file a separate report in `_COMMUNICATION/TEAM_100/reports/`.

---

## 5. Known Issues / Follow-ups

<!-- Things that were discovered but are NOT blocking the current gate. -->

| Issue | Severity | Recommendation |
|-------|----------|---------------|
| <Issue description> | LOW / MEDIUM / HIGH | <Suggested action> |

---

## 6. Next Action Required

<!-- Clearly state what the receiving team should do upon reading this report. -->

- [ ] <Receiving team action — e.g. "Team 50: execute QA_MANDATE_G3_RERUN.md">
- [ ] <Or: "Team 100: review deviation in section 4 and approve">

---

*Filed by: Team <SENDER_ID> (<SENDER_NAME>)*
*Date: <YYYY-MM-DD>*
