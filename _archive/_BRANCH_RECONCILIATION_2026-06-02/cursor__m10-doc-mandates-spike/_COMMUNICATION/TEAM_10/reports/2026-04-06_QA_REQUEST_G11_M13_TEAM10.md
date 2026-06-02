# QA Request — Gate G11 (M13 Public Product Details + Publish v3)

**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA)  
**CC:** Team 100 (Architecture), Nimrod  
**Date:** 2026-04-06  
**Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md`  
**CSA / baskets (full matrix):** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` + `_COMMUNICATION/TEAM_10/reports/2026-04-07_QA_REQUEST_CSA_BASKETS_FULL_G11_TEAM10.md`  
**Architectural approval:** `_COMMUNICATION/TEAM_100/reports/2026-04-04_M13_ARCHITECTURAL_APPROVAL_TEAM100.md`

---

## Preconditions (align with environment) — **updated 2026-04-06**

1. **M13-PRE / G-PRE:** Per **Nimrod direction** and `_COMMUNICATION/TEAM_10/MANDATE_M13_PRE_DATA_FOUNDATION_TEAM10_ADDENDUM.md`, **§4 is waived as a hard gate** for M13-B/C. Team 50 should run **`QA_MANDATE_G11.md`** (T01–T15) and may run G-PRE checks **in parallel** for traceability, but **M13 is not blocked** on full G-PRE numeric PASS unless Team 100 issues a revised binding mandate.

2. **Product count ≥ 90 (mandate T06 / legacy M13-PRE G-PRE-5):** **EXPLICIT WAIVER** — live snapshot shows **76** products after `run_publisher` (see data report below). Team 50: record **CONDITIONAL PASS** or listed waiver for this threshold.

3. **Partial data coverage (informational waivers):** Snapshot documents **5 of 9** mypips priority codes with normalized rows on this DB (not all nine); **SRC035** zero basket rows (parser policy). **Not** treated as M13 failure per freeze/addendum.

4. **Postgres:** G11 pre-conditions in the mandate may reference Docker Postgres — **this project uses direct PostgreSQL** when not in Docker; substitute `python3 -m organic_market_agent.db.check` and a running local Postgres per `README`.

5. **Schema 3.0** remains required; **product count** is the primary numeric waiver above.

---

## Team 10 implementation summary (this drop)

| Area | Change |
|------|--------|
| Publish JSON | `report_schema_version: "3.0"`, `details` on every product (`details_variant`, `source_count`, `price_series`, `csa` / `store` / `benchmark`) |
| Manifest | `schema_version` **3.0** |
| Privacy | No `SRC###`, URLs, or blocklisted farm strings in JSON; HTML body checked in tests |
| Price series | Daily median (30d cap) for non-baskets; weekly median (12w cap) for `basket_csa`; omitted if &lt; 3 points |
| UI | Accordion details row, Chart.js 4 (CDN), filter bar works per `tbody.sfa-product-group`, RTL-friendly chart `x.reverse` |
| Tests | `tests/test_m13_publish_g11.py` + updated `tests/test_publisher_local.py` |

---

## Data snapshot + freeze (authoritative evidence)

**File:** `_COMMUNICATION/TEAM_10/reports/2026-04-06_M13_DATA_SNAPSHOT_AND_M10_FREEZE_TEAM10.md`

Contains: publish timestamps, **product_count 76**, manifest **3.0**, community source count, CSA/SRC036/mypips SQL excerpts, and **M10.4/M10.5 freeze** narrative for ROADMAP **v5.4**.

---

## Evidence for Team 50

```bash
python3 -m pytest tests/test_publisher_local.py tests/test_m13_publish_g11.py -q
python3 -m organic_market_agent run_publisher
# Then run T02–T09 scripts from QA_MANDATE_G11.md against output/public/
```

Live checks **T10–T15** (MCP browser) after `run_publisher --upload` per mandate.

**Run T01–T15 with waivers** as documented above unless Team 100 publishes an amended `QA_MANDATE_G11.md` that codifies these waivers in the mandate body.

---

## Completion report

File `YYYY-MM-DD_M13_COMPLETION_TEAM10.md` when M13-A+B are signed off internally, attached to this thread for QA.

---

*Gate closure:* see `_COMMUNICATION/TEAM_50/reports/2026-04-06_GATE_G11_REPORT_TEAM50.md` and `_COMMUNICATION/TEAM_100/reports/2026-04-06_ARCH_SIGNOFF_M13_COMPLETE_TEAM100.md`. **Basket supplement** (2026-04-07) is for **extended CSA/סלים verification** on top of that baseline.*
