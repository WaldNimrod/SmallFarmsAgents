---
document_type: MANDATE
version: "1.0"
---

# Mandate — M7 Completion Report & QA Review Request

**Mandate ID:** MANDATE-20260402-M7-COMPLETION
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Dev)
**Date:** 2026-04-02
**Priority:** HIGH
**Gate dependency:** Blocks G7
**Status:** ACTIVE

---

## 1. Context

Milestone M7 (Public Publishing / Go-Live) has been implemented and operational since 2026-03-31. The SmallFarmsAgent public page is live at `https://nimrod.bio/smallfarmsagent/`, the pipeline publishes data via FTPS to uPress, and all tests pass.

However, formal closure documentation has never been filed. G7 cannot be formally closed without a Completion Report from Team 10 and a QA Review Request to Team 50.

**Triggered by:** Gate closure initiative — all gates M7–M9 must be formally closed.
**Related documents:**
- `_COMMUNICATION/TEAM_50/QA_MANDATE_G7.md` (amended 2026-04-02 for M8 class name refactor)
- `_COMMUNICATION/TEAM_100/reports/2026-04-02_G8_ACKNOWLEDGMENT_TEAM100.md`

---

## 2. Requirements

### Task 1 — File M7 Completion Report

File a Completion Report per the canonical template (`_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md`) covering all M7 deliverables.

The report must document:

1. **Pipeline publishing system** — `run_publisher` generates versioned artifacts (JSON, HTML, body fragment, manifest v2)
2. **FTPS upload system** — `run_upload` deploys artifacts to uPress via `ReusedSessionFTP_TLS`
3. **WordPress integration** — SmallFarmsAgent page live at `/smallfarmsagent/` with shortcode embedding body fragment
4. **Manifest v2 schema** — `schema_version: "2.0"`, `artifacts`, `fixed_names`, `upload_base`
5. **Stale data banner** — auto-display after 3+ days without fresh data
6. **Test coverage** — pytest suite (140+ pass, 2 skip), including `test_ftps_upload.py`, `test_publisher_local.py`, `test_pipeline_upload.py`

**Evidence required:** Paste verbatim `pytest tests/ -q` output, `alembic current` output, and manifest schema keys.

**Acceptance criterion:** Report filed at `_COMMUNICATION/TEAM_10/reports/2026-04-02_M7_COMPLETION_REPORT_TEAM10.md`

---

### Task 2 — File G7 QA Review Request to Team 50

File a QA Review Request per the canonical template (`_COMMUNICATION/TEMPLATES/QA_REVIEW_REQUEST.md`) requesting Team 50 to execute the amended `QA_MANDATE_G7.md`.

Pre-conditions to verify and document:
- Alembic at revision 030 (head)
- `db.check` → RESULT: PASS
- pytest → 140+ passed, 0 failed
- `.env` has `UPRESS_SFTP_HOST` configured
- `output/public/manifest.json` exists with `schema_version: "2.0"`

**Acceptance criterion:** Request filed at `_COMMUNICATION/TEAM_50/reports/2026-04-02_G7_REVIEW_REQUEST_TEAM10.md`

---

## 3. Out of Scope

- M8 (UX Polish) deliverables — already closed as G8 PASS
- M9 (Site Optimization) deliverables — separate gate
- Any code changes — M7 code is complete, this is documentation only
- Running the actual QA tests — that is Team 50's responsibility

---

## 4. Verification Checklist

Run these before submitting:

```bash
python3 -m pytest tests/ -q
alembic current
python3 -m organic_market_agent.db.check
ls output/public/manifest.json
```

Expected results:
- [ ] pytest: 140+ passed, 0 failed
- [ ] Alembic: 030 (head)
- [ ] db.check: RESULT: PASS
- [ ] manifest.json exists

---

## 5. Completion Report

When both tasks are complete, this mandate is considered fulfilled.

The M7 Completion Report IS the deliverable of Task 1.
The G7 QA Review Request IS the deliverable of Task 2.

No separate completion report for this mandate is required.

---

## 6. Escalation

If blocked:
1. File a report in `_COMMUNICATION/TEAM_10/reports/` with prefix `BLOCKED_`
2. State the exact blocking condition
3. Tag with `[USER ACTION REQUIRED]` if Nimrod must decide

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-04-02*
*Authorized by: Team 100 (Architecture)*
