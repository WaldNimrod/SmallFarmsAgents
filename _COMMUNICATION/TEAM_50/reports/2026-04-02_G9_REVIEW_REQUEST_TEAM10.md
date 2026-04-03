---
document_type: QA_REVIEW_REQUEST
version: "1.0"
---

# QA Review Request — Gate G9

**Request ID:** QA-REQ-20260402-G9
**From:** Team 10 (Feature Dev)
**To:** Team 50 (QA)
**Date:** 2026-04-02
**Gate:** G9 — Site Optimization + Maintenance + Accessibility
**Milestone:** M9 — Site Optimization + Maintenance + Accessibility
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G9.md`
**Priority:** HIGH

---

## 1. What Was Completed

| Team | Mandate | Completion Report |
|------|---------|------------------|
| Team 10 | `MANDATE-20260402-M9-COMPLETION` | `_COMMUNICATION/TEAM_10/reports/2026-04-02_M9_COMPLETION_REPORT_TEAM10_v2.md` |

---

## 2. Pre-conditions Confirmed

- [x] Alembic revision is at head (`alembic current` → `030 (head)`)
- [x] `python3 -m organic_market_agent.db.check` → RESULT: PASS
- [x] `python3 -m pytest tests/ -q` → `152 passed, 2 skipped`
- [x] WP Accessibility loading on live site (v2.3.3, Hebrew labels, focus outlines)
- [x] Yoast SEO active (v27.3, sitemap → 200, schema/LD+JSON present)
- [x] ezCache active (`x-cached-with: ezCache` in headers)
- [ ] **WP Admin tasks — NOT YET CONFIRMED** (see Section 3)

---

## 3. Known Issues at Time of Request

| Issue | Impact | Expected QA Behavior |
|-------|--------|----------------------|
| Phone still shows `052-42-42-342` | CRITICAL | T10 will FAIL — blocks gate |
| Email still shows `office@nimrod.bio` | CRITICAL | T10 will FAIL — blocks gate |
| `[wpforms id="90050"]` renders as raw text | CRITICAL | T07 will FAIL — blocks gate |
| "הזמנות" still in navigation | HIGH | T11 will FAIL |
| Footer hours not updated | HIGH | T10 partial FAIL |
| OG description references old farm | MEDIUM | T08 informational finding |
| WooCommerce orphan pages accessible | MEDIUM | Informational finding |

**These 7 WP Admin tasks must be completed by Nimrod before G9 can pass.**

---

## 4. Request to Team 50

Please execute the QA mandate:
`_COMMUNICATION/TEAM_50/QA_MANDATE_G9.md`

**Important:** The QA mandate specifies WP Admin pre-conditions that must be verified. If any Critical pre-condition is not met, document as FAIL per the mandate instructions.

File your findings report using the canonical template:
`_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`

Save it at:
`_COMMUNICATION/TEAM_50/reports/2026-04-02_GATE_G9_REPORT_TEAM50.md`

---

*Issued by: Team 10 (Feature Dev)*
*Date: 2026-04-02*
