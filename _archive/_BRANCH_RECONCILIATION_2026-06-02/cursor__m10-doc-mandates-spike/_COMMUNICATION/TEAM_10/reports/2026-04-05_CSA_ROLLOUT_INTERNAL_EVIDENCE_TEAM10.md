# CSA + public index rollout — internal evidence (no formal QA gate)

**Formal QA:** Team 50 — `_COMMUNICATION/TEAM_50/QA_MANDATE_G11_CSA_BASKETS_SUPPLEMENT_TEAM50.md` + `2026-04-07_QA_REQUEST_CSA_BASKETS_FULL_G11_TEAM10.md`.

**Team:** Team 10 (Feature Dev)  
**Date:** 2026-04-05  
**Plan:** CSA end-to-end rollout (DB → publish → UI)

---

## 1. Database / catalog verification

Executed locally against PostgreSQL:

- **Basket products:** `PRD025`, `PRD026`, `PRD027`, `PRD028`, `PRD029` — `category = 'baskets'`, `is_basket_product = true`.
- **CSA sources:** `SRC033`, `SRC034`, `SRC035` — `is_active = true`.
- **Normalized observations (community, ok):** basket rows present (example counts at verification time): `PRD025` 11, `PRD026` 14, `PRD027` 29, `PRD028` 4.

**M13-PRE CSA row counts (last fetch per source)** — use for formal evidence:

```sql
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
  AND sfr.id = (SELECT MAX(id) FROM source_fetch_runs WHERE source_id = s.id)
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code ORDER BY s.code;
```

---

## 2. Publisher + privacy spot-check

```bash
python3 -m organic_market_agent run_publisher
python3 -c "
import json, re
d = json.load(open('output/public/public_report.json', encoding='utf-8'))
assert d.get('report_schema_version') == '3.0'
s = json.dumps(d, ensure_ascii=False)
assert not re.findall(r'SRC\d{3}', s)
assert 'http://' not in s and 'https://' not in s
b = [p for p in d['products'] if p.get('category') == 'baskets']
print('published basket rows:', len(b))
for x in b:
    assert x['details']['details_variant'] == 'basket_csa'
print('OK')
"
```

**Automated regression:**

```bash
python3 -m pytest tests/test_publisher_local.py tests/test_m13_publish_g11.py -q
```

---

## 3a. Admin UI (local Flask — `127.0.0.1:5000`)

- **Products → פירוט** on any basket catalog row (`category=baskets` or `is_basket_product`): card **“סל CSA — הקשר מהמקור (ניהול)”** with accordion per source (full `csa_context`, not privacy-sanitized).
- **Last 50 observations:** expandable **הקשר** per row when `csa_context` exists.
- **Product list:** **סל** badge for basket rows.

## 3. UI + publisher hygiene (in-repo)

- **Filter:** `data-filter="baskets"` — shows rows where `data-category="baskets"` (same table as architecture mandate).
- **Badge:** Hebrew label `סל` on basket product names (no source identification).
- **Files:** `organic_market_agent/publisher/templates/public_report_body.html`, `public_report.html`.
- **CSA text:** `report_details._sanitize_public_text` also removes Israeli-style phone patterns from `contents_summary_generalized` / `cadence_note` before they reach `public_report.json` / HTML.

---

## 4. WordPress / live deploy (owner: Nimrod) — checklist

1. Run publisher (and `--upload` if using FTPS pipeline).
2. Confirm uploaded artifacts include `public_report_body.html` and versioned copies if used.
3. Hard-refresh or cache-bust uPress/CDN so the fragment updates.
4. **Smoke:** open dynamic page — filter **סלים**, expand a basket row — CSA text (if any) + chart or “אין מספיק נתונים להצגת מגמה”.
5. **CSP:** if the site blocks third-party scripts, allow `https://cdn.jsdelivr.net` for Chart.js 4.

---

## 5. Formal QA

This document is **internal** only. Gate **G11** / Team 50 sign-off remains the canonical path when scheduled.
