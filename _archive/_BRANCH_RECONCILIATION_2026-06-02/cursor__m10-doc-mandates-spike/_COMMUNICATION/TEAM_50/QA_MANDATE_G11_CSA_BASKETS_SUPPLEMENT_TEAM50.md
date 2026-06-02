---
document_type: QA_MANDATE_SUPPLEMENT
version: "1.0"
---

# QA Mandate Supplement — G11 CSA / Baskets (full matrix)

**Supplement ID:** `QA-MANDATE-G11-CSA-BASKETS-SUPP-TEAM50`  
**Parent:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G11.md` (Gate **G11**)  
**From:** Team 100 / Team 10 (coordination)  
**To:** Team 50 (QA)  
**Date:** 2026-04-07  
**Amended:** 2026-04-05 — **TB-DB-2** SQL uses `code AS product_id` (schema alignment).  
**Scope:** **Basket (CSA) channel** only — extends **T07**, **T08**, **T12**, **T13** with explicit commands, SQL, and admin checks.

**Rule:** Execute **after** G11 preconditions in the parent mandate. Record **PASS / FAIL / N/A** per row in your findings. **Privacy** failures (**TB-PRIV***) are **Critical** (same as T04/T05).

---

## 1. Purpose

Ensure **published** and **live** behavior for **`category: baskets`** / **`details_variant: basket_csa`** is complete: JSON shape, weekly price series cap, generalized CSA text, filter + badge UI, optional admin drill-down (local), and absence of source-identifying data in public artifacts.

---

## 2. Preconditions (inherit + basket-specific)

| ID | Check | Pass |
|----|--------|------|
| B-P0 | Parent G11 P1–P6 satisfied (or waived per ROADMAP + **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER**) | Yes |
| B-P1 | `run_publisher` succeeds on certified DB (or document **PublishAbortError** &lt;2 sources → supplement **BLOCKED**) | Document |
| B-P2 | At least **one** row in `products` with `category = 'baskets'` and `is_active` | Optional; many checks **N/A** if zero |

---

## 3. Catalog / DB — CSA sources

**TB-DB-1** — Last-fetch raw row counts (M13-PRE §3.1 style):

```sql
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
  AND sfr.id = (SELECT MAX(id) FROM source_fetch_runs WHERE source_id = s.id)
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code ORDER BY s.code;
```

**Record:** three rows; note **SRC035 = 0** is **INFO** only if **≥2** of the three have `raw_rows > 0` (aligned with scoped G-PRE-3).

**TB-DB-2** — Basket products:

```sql
SELECT code AS product_id, canonical_name_he, category, is_basket_product
FROM products
WHERE category = 'baskets' AND is_active = true
ORDER BY code;
```

**Note:** The public product identifier in JSON is `products.code` (e.g. `PRD025`). There is no `product_id` column on `products` — use `code` (aliased here as `product_id` for readability).

---

## 4. Publish JSON — basket row contract

Run after `python3 -m organic_market_agent run_publisher` (same tree Team 50 certifies for G11).

**TB-JSON-1** — Every published product with `category == "baskets"`:

```bash
python3 -c "
import json, re
d = json.load(open('output/public/public_report.json', encoding='utf-8'))
baskets = [p for p in d['products'] if p.get('category') == 'baskets']
print('basket rows:', len(baskets))
phone = re.compile(r'(?:0\d{1,2}[-\s]?\d{3}[-\s]?\d{4})|(?:\\+972)')
for p in baskets:
    det = p['details']
    assert det.get('details_variant') == 'basket_csa', p.get('product_id')
    ps = det.get('price_series') or []
    if ps:
        assert len(ps) >= 3, (p['product_id'], len(ps))
        assert len(ps) <= 12, (p['product_id'], 'weekly cap', len(ps))
        for pt in ps:
            assert 'd' in pt and 'v' in pt
    csa = det.get('csa')
    if csa is not None:
        assert isinstance(csa, dict)
        for k in csa.keys():
            assert k in ('contents_summary_generalized', 'cadence_note', 'context_incomplete'), k
        blob = json.dumps(csa, ensure_ascii=False)
        assert not phone.search(blob), ('phone-like in csa', p['product_id'], blob[:200])
    assert det.get('store') is None, p['product_id']
    assert det.get('benchmark') is None, p['product_id']
print('TB-JSON-1 PASS')
"
```

**TB-JSON-2** — Non-basket products must **not** use `basket_csa`:

```bash
python3 -c "
import json
d = json.load(open('output/public/public_report.json', encoding='utf-8'))
for p in d['products']:
    if p.get('category') != 'baskets':
        assert p['details'].get('details_variant') != 'basket_csa', p['product_id']
print('TB-JSON-2 PASS')
"
```

**Weight:** Critical for TB-JSON-1/2 together with parent T02/T03.

---

## 5. HTML artifacts — filter, badge, triggers

**TB-HTML-1** — Body fragment contains basket filter and markers:

```bash
python3 -c "
from pathlib import Path
h = Path('output/public/public_report_body.html').read_text(encoding='utf-8')
assert 'data-filter=\"baskets\"' in h or \"data-filter='baskets'\" in h
assert 'sfa-product-row' in h  # clickable product row opens detail modal (no separate details column)
assert 'סל' in h  # basket badge label
assert 'סלים' in h  # filter label
print('TB-HTML-1 PASS')
"
```

**TB-HTML-2** — Same privacy rules as **T05** for `SRC###` in HTML (no source codes in fragment).

**Weight:** High

---

## 6. Live site (MCP browser) — baskets

**URL:** `https://www.nimrod.bio/smallfarmsagent/` (or latest certified URL).

| ID | Action | Pass |
|----|--------|------|
| **TB-LIVE-1** | Open page (cache-bust query if needed). Click filter **סלים**. | Only `data-category="baskets"` product groups visible (spot-check). |
| **TB-LIVE-2** | Expand a basket row (**▼**). | Panel shows CSA-oriented copy and/or “אין מספיק נתונים…”; **no** farm names from blocklist; **no** `SRC###`. |
| **TB-LIVE-3** | If `price_series` exists for that product in JSON, chart canvas renders. | Canvas or empty state consistent with data. |
| **TB-LIVE-4** | Switch filter back to **הכל**; expand a non-basket row. | Variant copy matches **store** / **grower** / **benchmark** — not CSA basket template. |

**Weight:** Critical for TB-LIVE-1/2; High for TB-LIVE-3/4.

---

## 7. Admin UI (local only — optional for G11)

**Not** a public gate unless Nimrod promotes admin — document **N/A** if no local run.

| ID | Action | Pass |
|----|--------|------|
| **TB-ADM-1** | `python3 -m organic_market_agent run_admin` → login → **Products** → open a **basket** product. | Section **“סל CSA — הקשר מהמקור (ניהול)”** present with per-source accordion. |
| **TB-ADM-2** | **Last 50 observations** table for that product | **הקשר** expandable when `csa_context` exists (internal text; may include richer detail than public). |

**Weight:** Medium (traceability for Nimrod / Team 10).

---

## 8. Automated regression (Team 50 may re-run)

```bash
python3 -m pytest tests/test_publisher_local.py tests/test_m13_publish_g11.py tests/test_csa_parsers.py -q
```

**Pass:** 0 failures (skips acceptable per markers). **`test_m13_publish_g11.py::test_g11_basket_products_json_contract_when_published`** mirrors **TB-JSON-1/2** when DB has baskets and publish succeeds.

---

## 9. Reporting

File basket-specific results either:

- Inside `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_GATE_G11_REPORT_TEAM50.md` as an addendum section **“G11 — CSA baskets supplement”**, **or**
- A standalone `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_G11_CSA_BASKETS_SUPPLEMENT_FINDINGS_TEAM50.md` linked from the main G11 report.

---

## 10. References

- Team 10 evidence: `_COMMUNICATION/TEAM_10/reports/2026-04-05_CSA_ROLLOUT_INTERNAL_EVIDENCE_TEAM10.md`
- Data snapshot: `_COMMUNICATION/TEAM_10/reports/2026-04-06_M13_DATA_SNAPSHOT_AND_M10_FREEZE_TEAM10.md`
- CSA policy: `_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md`
- QA request: `_COMMUNICATION/TEAM_10/reports/2026-04-07_QA_REQUEST_CSA_BASKETS_FULL_G11_TEAM10.md`

---

*Supplement issued for Team 50 full basket coverage under G11.*
