# QA Review Request — M10.5 CSA baskets & Teva Shuk (Sellio)

**From:** Team 10  
**To:** Team 50 (QA)  
**Date:** 2026-03-30 (updated 2026-04-06 — CSA expansion report `2026-04-06_CSA_SOURCE_CANDIDATES_TEAM10.md`, Alembic **066**; **M13-PRE G-PRE:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_QA_REQUEST_M13_PRE_GPRE_TEAM10.md`)  
**Mandate:** [`_COMMUNICATION/TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md`](../TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md)  
**Analysis policy (CSA data value):** [`_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md`](../TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md)  
**QA remediation (Team 10):** [`_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_5_QA_REMEDIATION_COMPLETE_TEAM10.md`](../TEAM_10/reports/2026-04-05_M10_5_QA_REMEDIATION_COMPLETE_TEAM10.md)  
**Re-review request (R2):** [`reports/2026-04-05_M10_5_QA_REVIEW_REQUEST_R2_TEAM10.md`](reports/2026-04-05_M10_5_QA_REVIEW_REQUEST_R2_TEAM10.md)

---

## Preconditions

- `python3 -m alembic current` → revision **058** or later (M10.5 QA remediation: Teva search entry, scroll tuning, SRC036 scope-skips).
- `pip install -r requirements.txt` and `python3 -m playwright install chromium` for SRC036 fetches.
- `DATABASE_URL` configured.

---

## Deliverables implemented

| Area | Detail |
|------|--------|
| Parsers | `organic_market_agent/parsers/csa_basket.py`, `organic_market_agent/parsers/sellio.py` |
| Collector | `platform_family: sellio` → `HeadlessBrowserCollector`; `goto_wait_until` on headless profile |
| Migration | `056` — profiles, activation SRC033–036, CSA aliases, scope-skip `– השדה`; **`058`** — SRC036 search URL + scroll + packaged-line scope-skips |
| Tests | `tests/test_csa_parsers.py` (5 tests), `tests/test_sellio_parser.py` (5 tests) |
| Completion | [`2026-03-30_M10_5_COMPLETION_TEAM10.md`](../TEAM_10/reports/2026-03-30_M10_5_COMPLETION_TEAM10.md); **remediation** [`2026-04-05_M10_5_QA_REMEDIATION_COMPLETE_TEAM10.md`](../TEAM_10/reports/2026-04-05_M10_5_QA_REMEDIATION_COMPLETE_TEAM10.md) |

---

## QA execution

1. Run mandate acceptance criteria **AC1–AC9** (ingestion with live network for SRC036).  
2. File a new findings report under `_COMMUNICATION/TEAM_50/reports/` using `QA_FINDINGS_REPORT` template.  
3. **058** switches SRC036 entry to **organic search** (`q=אורגני`) so **AC2 (≥20)** is met without conventional titles from the mixed organic-aisle category page. **AC4/AC5/AC6** may still require Team 100 input if all SKUs are catalog out-of-scope (packaged retail).

---

## Team 100

Architectural review of organic filter strategy and CSA `raw_payload_json.csa_context` per analysis policy.
