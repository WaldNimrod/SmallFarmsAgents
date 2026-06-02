# QA Request — M13-PRE Data Foundation (G-PRE-1..7)

**Canonical filing (Team 50 inbox):** `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md` — use that path for the formal review request. This TEAM_10 copy is retained as a working checklist only.

**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA)  
**CC:** Team 100 (Architecture), Nimrod  
**Date:** 2026-04-06  
**Mandate:** `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10.md`

---

## Purpose

Request validation of **M13-PRE** gate criteria (§4 combined criteria G-PRE-1..7) after M10.4 (mypips) and M10.5 (CSA + retail) remediation work reaches the thresholds defined in the mandate.

**Coordination note:** M10.5 §3 remediation may be executed primarily by another squad per Nimrod. Evidence for SRC034/SRC036/publish-count fixes may appear in that team’s completion report; this request still asks Team 50 to verify **all** G-PRE criteria against the live DB and published artifacts.

---

## Criteria checklist (Team 50 to mark PASS/FAIL)

| ID | Criterion | Threshold | Evidence location |
|----|-----------|-----------|-------------------|
| G-PRE-1 | mypips sources active + data | ≥5 of 9 producing normalized observations | SQL §2.2 PRE-D4–D6 |
| G-PRE-2 | mypips resolution | ≥85% per activated source | SQL PRE-D9 |
| G-PRE-3 | CSA extraction | ≥2 of 3 CSA sources with basket items | SQL §3.1 |
| G-PRE-4 | SRC036 resolution | ≥85% | SQL §3.2 |
| G-PRE-5 | Published product count | ≥90 | `run_publisher` + `len(products)` |
| G-PRE-6 | Test suite | 0 failures | `python3 -m pytest tests/ -q` |
| G-PRE-7 | Live upload | `run_publisher --upload` OK, HTTP 200 | curl / browser |

---

## Team 10 deliverables (attach when ready)

1. `YYYY-MM-DD_M10_4_COMPLETION_TEAM10.md` — if Team 10 owns M10.4 closure  
2. `YYYY-MM-DD_M10_5_REMEDIATION_TEAM10.md` — or cross-team pack with SQL outputs for §3 fixes  
3. Screenshot or log: `alembic current` = head  
4. `output/public/public_report.json` product count line + optional manifest excerpt  

---

## After Team 50 PASS

Team 10 will file `YYYY-MM-DD_M13_PRE_COMPLETION_TEAM10.md` to Team 100 per mandate §5 Step 6. **M13-B** (public details UI) remains blocked until that PRE completion is acknowledged.

---

*This request is filed to establish the QA workflow; execution evidence may follow in a later update when remediation is complete.*
