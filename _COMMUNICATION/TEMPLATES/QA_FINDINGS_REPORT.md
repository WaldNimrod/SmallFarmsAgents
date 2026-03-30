# CANONICAL TEMPLATE: QA FINDINGS REPORT
# File: _COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md
# Version: 1.0 | 2026-03-30 | Team 100
#
# USAGE:
#   This template is used exclusively by Team 50 (QA) after executing a gate mandate.
#   It is the ONLY valid format for gate decisions.
#
#   Copy this file to:
#     _COMMUNICATION/TEAM_50/reports/<YYYY-MM-DD>_G<N>_QA_FINDINGS_TEAM50.md
#   Fill every field. Remove all lines starting with '#'.
#   Gate decisions made in any other format are NOT binding.
# =============================================================================

---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G<N>
**Report ID:** QA-RPT-<YYYYMMDD>-G<N>
**QA Review Request:** `QA-REQ-<YYYYMMDD>-G<N>` (if filed)
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team <IMPLEMENTING_TEAM_ID> (<IMPLEMENTING_TEAM_NAME>)
**Date:** <YYYY-MM-DD>
**Gate:** G<N> — <Gate description>
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/<QA_MANDATE_FILENAME>.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `<X.Y.Z>` — ✅ meets 3.11+ / ❌ FAIL |
| Docker postgres | `<container_name>` running on port `<PORT>` — ✅ / ❌ |
| DATABASE_URL | `postgresql://<user>@localhost:<port>/<db>` — ✅ / ❌ |
| Alembic revision | `<revision>` — ✅ matches expected / ❌ FAIL |
| `db.check` result | PASS / FAIL |

If any environment check fails: **GATE BLOCKED — environment not valid for QA.**

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | Critical | <Evidence or reason> |
| T02 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | Critical | |
| T03 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | High | |
| T04 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | High | |
| T05 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | High | |
| T06 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | Medium | |
| T07 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | Medium | |
| T08 | <Name> | ✅ PASS / ❌ FAIL / ⏭️ SKIP | Medium | |

**Score:** <N_PASSED>/<N_TOTAL> tests passed.
**Critical failures:** <N> (must be 0 for PASS).

---

## 3. Evidence

<!-- Paste verbatim output for every test. -->

### T01 — <Test Name>
```
<paste exact output>
```

### T02 — <Test Name>
```
<paste exact output>
```

<!-- Continue for all tests -->

---

## 4. Findings Summary

### Passed Tests
- T<N>: <brief note>

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T<N> | <Root cause> | Critical / High / Medium | Yes / No |

### Skipped Tests
| Test | Reason |
|------|--------|
| T<N> | <Why skipped> |

---

## 5. Gate Decision

<!-- Only one of the three options below. Delete the other two. -->

### ✅ GATE G<N> — PASS
All critical tests passed. Gate is open.
**Next milestone:** M<N+1> — <Name>. Team 10 may begin.

---

### 🟡 GATE G<N> — CONDITIONAL PASS
Gate is open with conditions. The following items must be resolved before G<N+1> opens:

| Condition ID | Description | Assigned To | Due |
|-------------|-------------|-------------|-----|
| C<N>-1 | <What must be done> | Team <ID> | Before G<N+1> QA |
| C<N>-2 | <What must be done> | Team <ID> | Before G<N+1> QA |

Team 10 may begin M<N+1> implementation. Conditions do NOT block M<N+1> implementation.
Conditions MUST be resolved before G<N+1> QA sign-off.

---

### ❌ GATE G<N> — FAIL
Gate is BLOCKED. The following critical failures must be resolved:

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F<N>-1 | <Root cause + fix required> | Team <ID> |
| F<N>-2 | <Root cause + fix required> | Team <ID> |

**Required actions:**
1. <Team ID>: <Specific action — reference mandate if applicable>
2. Team 50: Re-execute QA mandate after fixes are confirmed

Gate remains CLOSED until Team 100 issues a re-open decision.

---

## 6. Required Actions

<!-- For the receiving team (Team 100) and implementing team. -->

| Team | Action | Priority |
|------|--------|----------|
| Team 100 | <e.g. "Issue patch mandate to Team 20"> | CRITICAL |
| Team <ID> | <e.g. "Apply fix and re-file completion report"> | HIGH |
| Team 50 | <e.g. "Stand by for re-QA after fix"> | MEDIUM |

---

*Filed by: Team 50 (QA)*
*Date: <YYYY-MM-DD>*
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
