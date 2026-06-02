---
document_type: QA_REVIEW_REQUEST
version: "1.0"
---

# QA Review Request — M10.5 (re-review after QA-RPT-20260405-M10_5)
**Request ID:** QA-REQ-20260405-M10_5-R2  
**From:** Team 10  
**To:** Team 50 (QA)  
**Date:** 2026-04-05  
**Gate / milestone:** M10.5 — CSA baskets & Teva Shuk (Sellio)  
**Prior findings:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_M10_5_QA_FINDINGS_TEAM50.md`  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md`  

---

## 1. What Was Completed

| Team | Work | Report |
|------|------|--------|
| Team 10 | M10.5 QA remediation (AC1/AC2 technical fixes, migration **058**, scope-skip hygiene for SRC036) | `_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_5_QA_REMEDIATION_COMPLETE_TEAM10.md` |

---

## 2. Pre-conditions Confirmed

- [x] Alembic at head → **058**
- [x] `python3 -m organic_market_agent.db.check` → **RESULT: PASS**
- [x] `python3 -m pytest tests/ -q` → **177 passed, 4 skipped**

---

## 3. What Team 50 Should Re-validate

1. **AC1** — CSA raw row counts for SRC033–SRC035 after fresh fetch (SRC034 parser fix; SRC035 may remain 0).  
2. **AC2** — SRC036 ≥20 organic-marked rows, 0 conventional (expect **search** entry URL in profile after **058**).  
3. **AC4** — Resolution rate for SRC033 and SRC036; **note:** SRC036 SKUs may be **entirely** `approved_scope_skip` (V1 packaged retail). Team 10 requests **explicit ruling** whether T04 `pct` **NULL** when `(normalized+unresolvable)=0` is PASS, FAIL, or N/A, and whether **Team 100** must waive AC4 for this source class.  
4. **AC5 / AC6** — Published product count and **חנויות** / `store` evidence; SRC036 may contribute **no** `normalized_observations` until catalog or mandate changes.  
5. **AC7–AC9** — Regression tests, CSA+Sellio test count, live publish if applicable.  

---

## 4. Team 100

Architectural decision requested on **retail packaged organic** vs **V1 vegetable catalog** for AC4/AC5/AC6 (see completion report §4).
