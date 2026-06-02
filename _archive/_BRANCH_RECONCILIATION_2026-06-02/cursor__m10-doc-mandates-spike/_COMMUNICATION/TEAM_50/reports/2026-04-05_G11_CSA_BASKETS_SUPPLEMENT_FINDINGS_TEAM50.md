---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — G11 CSA / Baskets Supplement

**Report ID:** QA-RPT-20260405-G11-CSA-BASKETS-SUPP  
**QA Review Request:** `_COMMUNICATION/TEAM_10/reports/2026-04-07_QA_REQUEST_CSA_BASKETS_FULL_G11_TEAM10.md`  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Nimrod (project lead)  
**Date:** 2026-04-05  
**Gate:** G11 — supplement only (`QA-MANDATE-G11-CSA-BASKETS-SUPP-TEAM50`)  
**Parent gate report:** `_COMMUNICATION/TEAM_50/reports/2026-04-06_GATE_G11_REPORT_TEAM50.md`  
**QA Mandates executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md` (T01–T09 re-run), `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` (TB-*)  
**B-P0 waiver:** `_COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md` — **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Alembic | **066 (head)** — PASS |
| `organic_market_agent.db.check` | **RESULT: PASS** |
| Interpreter | `.venv/bin/python` (Python 3.9.6) — used consistently |
| `run_publisher` | PASS — 76 products, `report_schema_version` **3.0** |
| `run_publisher --upload` | PASS — FTPS completed (**106** files this run, includes icon assets) |
| Product count vs T06 | **76** — **CONDITIONAL** per Team 100 waiver (same as parent G11) |

---

## 2. Parent G11 automated re-run (T01–T09)

| Test ID | Result | Notes |
|---------|--------|-------|
| T01 | **PASS** | `188 passed, 5 skipped`, 0 failures |
| T02 | **PASS** | All products have valid `details` / variants |
| T03 | **PASS** | 35 with `price_series`, caps and `d`/`v` OK |
| T04 | **PASS** | No SRC###, blocklist strings, or http URLs in JSON |
| T05 | **PASS** | No SRC### or blocklist farm strings in both HTML files |
| T06 | **PASS (waiver)** | `manifest.schema_version` 3.0; `product_count` 76 — waiver on file |
| T07 | **PASS** | 4 basket rows in report; all `basket_csa` (see INFO: duplicate `PRD027` lines in script output) |
| T08 | **PASS** | `grower_price_grid`, `store_retail`, `basket_csa` present |
| T09 | **PASS** | ~80.8 KB — under 500 KB |

**TB-HTML-2:** **PASS (by T05)** — same `SRC\d{3}` + farm blocklist rules on `public_report.html` and `public_report_body.html`.

---

## 3. Supplement matrix (TB-*)

| ID | Result | Weight | Notes |
|----|--------|--------|-------|
| TB-DB-1 | **PASS** | — | SRC033=3, SRC034=2, SRC035=0 — INFO SRC035=0 (≥2 of 3 with rows) |
| TB-DB-2 | **PASS** | — | Initial run: mandate used non-existent `products.product_id` → `UndefinedColumn`. **Corrected** in `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` to `code AS product_id` + `ORDER BY code`. Re-run: **3** rows (PRD025–PRD027). |
| TB-JSON-1 | **PASS** | Critical | `basket rows: 4`; `basket_csa`, weekly cap, `csa` keys, phone regex, `store`/`benchmark` null |
| TB-JSON-2 | **PASS** | Critical | No non-basket uses `basket_csa` |
| TB-HTML-1 | **PASS** | High | `data-filter="baskets"`, `sfa-details-trigger`, **סל**, **סלים** |
| TB-LIVE-1 | **PASS** | Critical | Filter **סלים** active; **4** ▼ triggers (matches 4 published basket rows). INFO: full accessibility tree may still list hidden non-basket detail regions (DOM retained). |
| TB-LIVE-2 | **PASS** | Critical | Expanded **סל ירקות בינוני**: empty-trend copy **אין מספיק נתונים להצגת מגמה**; expanded basket rows show generalized CSA text + disclaimer; **no `SRC###`** in snapshot grep (`snapshot-2026-04-05T00-45-25-538Z-jpv2ew.log` and basket pass log) |
| TB-LIVE-3 | **PASS (N/A data)** | High | All current basket `price_series` lengths **0** in `public_report.json` — empty state consistent; no chart required |
| TB-LIVE-4 | **PASS** | High | **הכל** → first row **אבוקדו**: panel **not** CSA basket template (insufficient data / non-CSA copy); **אגס** shows **מחירים מקטלוג…** (store channel) |
| TB-ADM-1 / TB-ADM-2 | **N/A** | Medium | Local admin (`run_admin`) not started in this session — optional per supplement §7 |
| Supplement pytest §8 | **PASS** | — | 23 passed, 1 skipped (`test_m13_publish_g11.py:217` synthesize payload soft limit — not basket contract) |

---

## 4. Live + regression evidence (abridged)

### T01

```text
188 passed, 5 skipped in 17.93s
```

### TB-DB-1

```text
('SRC033', 3)
('SRC034', 2)
('SRC035', 0)
```

### TB-DB-2 (after mandate correction)

```text
('PRD025', 'סל ירקות קטן', 'baskets', True)
('PRD026', 'סל ירקות בינוני', 'baskets', True)
('PRD027', 'סל ירקות גדול', 'baskets', True)
TB-DB-2 corrected SQL: OK, 3 rows
```

**(First attempt)** verbatim legacy SQL failed: `column "product_id" does not exist` — see mandate file note.

### TB-JSON-1 / TB-JSON-2 / TB-HTML-1

```text
basket rows: 4
TB-JSON-1 PASS
TB-JSON-2 PASS
TB-HTML-1 PASS
```

### Focused pytest (supplement §8)

```text
23 passed, 1 skipped in 1.58s
SKIPPED tests/test_m13_publish_g11.py:217: could not synthesize payload over soft limit
```

### Live session

- **URL:** `https://www.nimrod.bio/smallfarmsagent/?_cb=20260405g11supp`
- **Upload:** FTPS OK after local `run_publisher --upload`
- **MCP snapshots:** `snapshot-2026-04-05T00-44-27-415Z-4qbn0w.log`, `snapshot-2026-04-05T00-45-25-538Z-jpv2ew.log` (under `~/.cursor/browser-logs/`)
- **Console:** No Chart.js/report JS **errors**; only WordPress/jQuery **warnings** (JQMIGRATE, WP Accessibility `/shop` href)

### T14 (mobile spot)

- Viewport **375×800** after `browser_resize` — structure remains navigable (spot check, same approach as 2026-04-06 baseline).

### T15 (accessibility)

- **Not** fully re-scripted (Enter/Space/Escape cycle). **Inherits** prior **CONDITIONAL** from `2026-04-06_GATE_G11_REPORT_TEAM50.md`.

---

## 5. Findings / INFO

1. **TB-DB-2 mandate fix (same session):** `QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` §3 updated to `SELECT code AS product_id ... ORDER BY code` with schema note.
2. **Published JSON:** **4** basket **rows** for **3** distinct product codes (PRD027 appears twice — likely variant/duplicate publish row). Not a supplement failure; Team 10 may trace publisher grouping.
3. **T07 script output** listed two lines for PRD027 — consistent with duplicate rows above.

---

## 6. Gate decision (supplement scope)

### Supplement: **PASS**

All **Critical** supplement items **TB-JSON-1**, **TB-JSON-2**, **TB-LIVE-1**, **TB-LIVE-2** **PASS**. **TB-DB-2** **PASS** after mandate SQL correction (`code AS product_id`).

### Cumulative G11 (parent + supplement)

**Unchanged from 2026-04-06:** **CONDITIONAL PASS** — **T15** accessibility not fully cleared; **T06** product count via **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**. **No new privacy regressions** (T04/T05/TB-JSON phone check).

---

## 7. Required follow-ups

| Owner | Action |
|-------|--------|
| Team 10 | Optional: investigate duplicate **PRD027** rows in `public_report.json`. |
| Team 50 / Nimrod | Optional: full **T15** keyboard pass or accept documented CONDITIONAL. |

---

*Filed by: Team 50 (QA)*  
*Execution date: 2026-04-05*
