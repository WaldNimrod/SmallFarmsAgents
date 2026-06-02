# QA Request — Full G11 coverage for CSA / baskets (סלים)

**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA)  
**CC:** Team 100 (Architecture), Nimrod  
**Date:** 2026-04-07  
**Parent gate:** **G11** — `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md`

---

## Ask

Run **all** parent tests **T01–T15** where applicable, **plus** the **basket (CSA) supplement** below. The supplement adds **verbatim SQL**, **JSON/HTML scripts**, **live** basket-filter steps, and **optional local admin** checks so basket behavior is not only implied by T07/T12.

---

## Canonical documents

| Role | Path |
|------|------|
| **Basket supplement (execute)** | `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` |
| **General G11 request + waivers** | `_COMMUNICATION/TEAM_10/reports/2026-04-06_QA_REQUEST_G11_M13_TEAM10.md` |
| **Internal rollout evidence** | `_COMMUNICATION/TEAM_10/reports/2026-04-05_CSA_ROLLOUT_INTERNAL_EVIDENCE_TEAM10.md` |

---

## Suggested order

1. Preconditions (DB, `pytest tests/`, `run_publisher`, `run_publisher --upload` if testing live).  
2. **T01–T09** from `QA_MANDATE_G11.md`.  
3. **Supplement** TB-DB-1, TB-DB-2, TB-JSON-1, TB-JSON-2, TB-HTML-1, TB-HTML-2.  
4. **T10–T15** on live URL, emphasizing **TB-LIVE-*** steps from supplement (filter **סלים**, basket accordion).  
5. **TB-ADM-*** if local admin is available.  
6. Record outcomes in G11 report (or linked basket findings file).

---

*Nimrod: product copy/layout feedback can follow QA; supplement focuses on correctness, privacy, and data shape.*
