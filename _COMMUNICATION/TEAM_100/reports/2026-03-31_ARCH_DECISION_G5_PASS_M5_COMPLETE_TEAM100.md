# ARCH_DECISION — G5 PASS + M5 COMPLETE

**Document ID:** `ARCH-20260331-G5-PASS-M5-COMPLETE`  
**From:** Team 100 (Architecture)  
**To:** Team 10 · Team 20 · Team 50  
**Date:** 2026-03-31  
**Milestone:** M5 — Admin UI  
**Template:** `_COMMUNICATION/templates/ARCH_DECISION.md`

---

## Decision

**Gate G5 — PASS. Milestone M5 — COMPLETE.**

All 11 mandate test slices passed (T01–T11). Zero critical failures. Team 50 written sign-off filed at `_COMMUNICATION/TEAM_50/reports/2026-03-31_QA_G5_TEAM50.md`. Team 100 architectural review (`ARCH-20260331-M5-REVIEW-TEAM100`) confirms critical bugs were patched before handoff.

---

## Evidence Review

| Test | Team 50 Result | Team 100 Assessment |
|------|---------------|---------------------|
| T01 — `pytest test_admin_routes.py` | 11 passed | ✅ Accepted |
| T02 — Authentication | PASS (two-step curl) | ✅ Accepted — known curl `-L` POST/GET issue; see mandate patch |
| T03 — Read routes (9 paths) | PASS | ✅ Accepted — route count corrected in mandate patch |
| T04 — Alias create + audit | PASS | ✅ Accepted |
| T05 — Alias disable | PASS | ✅ Accepted |
| T06 — Rule create + disable | PASS (`profile_id=1`) | ✅ Accepted — mandate patched to include `profile_id` |
| T07 — Run trigger | PASS (54→55 runs) | ✅ Accepted; Bug 1 patch confirmed trigger now works |
| T08 — Audit log page | PASS (24 matches) | ✅ Accepted |
| T09 — QA flags view | PASS | ✅ Accepted |
| T10 — Regression counts | sources=20, products=29, aliases=103, obs=317, daily_aggs=25 | ✅ All at or above G4 baseline |
| T11 — Full `pytest tests/` | 73 passed, 1 skipped | ✅ Skip: QA001 — G4 waiver applies |

---

## Mandate Patches Applied

`QA_MANDATE_G5.md` amended per Team 50 findings (non-blocking, retrospective corrections):

1. **T03 route count:** "10 routes" corrected to "9 routes."
2. **T06 curl command:** Added `profile_id=1` field (required for rule creation).
3. **T02c curl note:** Added footnote — do not use `curl -L` after POST login; use separate POST (save cookies) then GET.

---

## Advisory Items (carried forward, non-blocking)

| Item | Finding | Status |
|------|---------|--------|
| Duplicate alias rows on double POST | T04 produced two rows with identical `alias_text` on accidental double-submit. T05 disabled max(id). | Team 10 may add uniqueness guard at UI/route level in M6 cleanup scope. Non-blocking. |
| Python 3.9.6 on QA runner | Below project policy of 3.11+. Did not affect results. | Team 20 to address as environment maintenance. Non-blocking. |

---

## Transition to M6

Gate G5 is now open. **M6 — Automation + Resilience** is the active milestone.

- Team 20: cron setup, `runner.py` schedule entrypoint.
- Team 10: SMTP alerting, retry logic, `log_entries` 90-day cleanup.
- M6 mandates to be issued by Team 100.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Sign-off ID:** `ARCH-20260331-G5-PASS-M5-COMPLETE`
