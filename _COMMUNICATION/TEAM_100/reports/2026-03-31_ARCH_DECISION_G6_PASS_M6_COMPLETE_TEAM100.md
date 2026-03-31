# ARCH_DECISION — G6 PASS + M6 COMPLETE

**Document ID:** `ARCH-20260331-G6-PASS-M6-COMPLETE`  
**From:** Team 100 (Architecture)  
**To:** Team 10 · Team 20 · Team 50  
**Date:** 2026-03-31  
**Milestone:** M6 — Automation + Resilience  
**Template:** `_COMMUNICATION/templates/ARCH_DECISION.md`

---

## Decision

**Gate G6 — PASS. Milestone M6 — COMPLETE.**

All Critical and High tests passed. T06 PARTIAL is a mandate wording defect — see analysis below. Gate pass criterion (no Critical fail, < 3 High fails) is fully met.

---

## Evidence Review

| Test | Weight | Team 50 Result | Team 100 Assessment |
|------|--------|---------------|---------------------|
| T01 — `pytest tests/` | Critical | 85 passed, 1 skipped | ✅ Accepted |
| T02 — Scheduler page + toggle | High | PASS | ✅ Accepted |
| T03 — Schedule update persists | High | PASS (used `cleanup_enabled=on`) | ✅ Accepted — see mandate patch below |
| T04 — Focused trigger | High | PASS — run 461, only SRC002 | ✅ Accepted |
| T05 — Dashboard charts | High | PASS — 2 canvas, 5 grep matches | ✅ Accepted |
| T06 — Alert badge + panel | Medium | PARTIAL — DB count=6, HTML grep=0 | ✅ Accepted — mandate defect, not code defect (see below) |
| T07 — Log cleanup | Medium | PASS | ✅ Accepted |
| T08 — Runs list UI | Medium | PASS | ✅ Accepted |
| T09 — `test_runner.py` | High | 7 passed | ✅ Accepted |
| T10 — Regression | Critical | All baselines met | ✅ Accepted |

---

## T06 Analysis — PARTIAL is a Mandate Defect

Team 50 correctly identified that the dashboard alert panel only renders when `is_read = false` rows exist. The mandate's HTML grep (`pipeline_alerts|alert-danger|...|סמן כנקרא`) expects to find these strings in the page at test time, but by T06 all prior alerts from T04 trigger (and earlier sessions) had already been marked read.

**Code behaviour is correct.** Showing an alert panel only when unread alerts exist is the intended UX. The mandate should require a fresh unread alert to exist before checking the HTML.

`QA_MANDATE_G6.md` patched below.

---

## Pre-condition Note — `GET /` Returns 200

The admin dashboard route (`GET /`) is intentionally not `@login_required` — it is read-only. Write operations (trigger, aliases, rules, scheduler) all require login. This was established in M5 (same pattern as G5). The mandate pre-condition check saying "Expected: 302" was incorrect. Patched below.

---

## Mandate Patches Applied (`QA_MANDATE_G6.md`)

1. **Pre-conditions:** `GET /` unauthenticated — expected code corrected from `302` to `200`.
2. **T03:** `POST` body uses `cleanup_enabled=on` (checkbox semantics), not `cleanup_enabled=true`. Updated in mandate curl.
3. **T06:** Mandate now requires inserting a test `pipeline_alerts` row with `is_read=false` before the HTML grep, and deleting it after.

---

## Regression Data (G6 Final Baseline)

| Metric | G5 Baseline | G6 Final |
|--------|------------|---------|
| sources | 20 | 20 |
| products | 29 | 29 |
| active_aliases | ≥97 | 110 |
| observations | ≥1 | 359 |
| daily_aggs | ≥25 | 25 |

---

## Transition to M7

Gate G6 is now open. **M7 — Public Publishing / Go-Live** requires:
- Gate G6 ✅ PASS (now open)
- **Nimrod explicit approval** before M7 mandates are issued

No M7 mandates will be issued until Nimrod explicitly approves the transition.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Sign-off ID:** `ARCH-20260331-G6-PASS-M6-COMPLETE`
