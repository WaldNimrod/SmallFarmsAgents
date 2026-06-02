---
document_type: QA_GATE_REPORT
version: "1.0"
---

# Gate G11 Report — M13 Public Product Details + Publish v3

**Report ID:** QA-RPT-20260406-G11-M13  
**From:** Team 50 (QA) — executed in automation-assisted session (Cursor agent + MCP browser)  
**To:** Team 100 (Architecture), Team 10 (Feature Dev), Nimrod  
**Date:** 2026-04-06  
**Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md` (amended 2026-04-06)  
**Waiver (product count):** `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` — **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**

---

## Environment

| Check | Result |
|-------|--------|
| Alembic | Head at execution time — matches Team 10 workspace (066+ lineage) |
| `db.check` | Used for publish run (same session as `run_publisher`) |
| `pytest tests/ -q` | **183 passed, 5 skipped**, 0 failures |
| `run_publisher` + `--upload` | **OK** — 8 files FTPS; refreshed `public_report_body.html` on live host |
| Live URL | `https://www.nimrod.bio/smallfarmsagent/` — HTTP **200**; post-upload HTML contains **81** `sfa-details-trigger` (prior stale cache had **0** — remediated by upload + cache-bust query) |

---

## Results summary

| Test | Result | Notes |
|------|--------|-------|
| T01 | **PASS** | `pytest tests/ -q` — 183 passed, 5 skipped |
| T02 | **PASS** | `report_schema_version` 3.0; all products have valid `details` |
| T03 | **PASS** | `price_series` where present: ≥3 points, cap 30 (non-basket) / 12 (`basket_csa`) |
| T04 | **PASS** | No SRC###, blocklist farm strings, or http URLs in `public_report.json` |
| T05 | **PASS** | Same checks on `public_report.html` + `public_report_body.html` |
| T06 | **PASS (waiver)** | `manifest.schema_version` **3.0**; `product_count` **76** — **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER** |
| T07 | **PASS** | 4 basket rows; `details_variant == basket_csa` |
| T08 | **PASS** | Variants: grower_price_grid, store_retail, basket_csa |
| T09 | **PASS** | JSON size within 500 KB budget |
| T10 | **PASS** | MCP: filter bar + **▼** detail triggers; expand shows panel; cookie banner dismissed first |
| T11 | **PASS** | Live HTML contains Chart.js canvas elements (`canvas` count **89** in downloaded page); a11y tree may not expose canvas — DOM verified |
| T12 | **PASS** | Filter **סלים**; expanded headings include basket CSA generalized text + disclaimer tone (e.g. סל ירקות גדול) |
| T13 | **PASS** | Filter **סלים** applied; row set reduced vs **הכל**; no console errors captured in this pass |
| T14 | **PASS (spot)** | Viewport resized **375×800** in tool session; table/detail structure remains in snapshot (full pixel audit deferred) |
| T15 | **CONDITIONAL** | **▼** trigger shows **expanded** + **focused** state in MCP after click; full focus-trap / Escape cycle **not** exhaustively scripted — acceptable with documented follow-up per mandate “remediation plan” for High |

---

## Gate decision

### CONDITIONAL PASS

**Critical criteria:** T01–T06, T10 — **met** (T06 via **Team 100 G-PRE-5 waiver**).  
**High criteria:** T07, T08, T11, T12, T14 — **met**; **T15** — **partial** (documented above).  
**Medium:** T13 — **met**.

**Waivers / conditions:**

1. **Published product count &lt; 90** — covered by **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**.
2. **T15 focus management** — confirm in a future pass or accept as known limitation until JS focus-trap hardening if Nimrod requires.

**Privacy:** No T04/T05 violations detected.

---

## G11 — CSA baskets supplement (2026-04-05)

**Executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` per `_COMMUNICATION/TEAM_10/reports/2026-04-07_QA_REQUEST_CSA_BASKETS_FULL_G11_TEAM10.md`.

**Findings:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_G11_CSA_BASKETS_SUPPLEMENT_FINDINGS_TEAM50.md` — Critical TB-JSON / TB-LIVE **PASS**; **TB-DB-2** **PASS** after mandate SQL correction (`code AS product_id`).

---

## References

- Team 10 request: `_COMMUNICATION/TEAM_10/reports/2026-04-06_QA_REQUEST_G11_M13_TEAM10.md`
- Data snapshot: `_COMMUNICATION/TEAM_10/reports/2026-04-06_M13_DATA_SNAPSHOT_AND_M10_FREEZE_TEAM10.md`
- MCP browser logs (snapshots): `~/.cursor/browser-logs/snapshot-2026-04-04T23-58-*.log`

---

*Filed for gate closure workflow — Team 50*
