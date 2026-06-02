---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G11

**Mandate ID:** QA-MANDATE-G11
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**CC:** Team 10 (Feature Dev), Nimrod (product)
**Date:** 2026-04-04
**Milestone:** M13 — Public Product Details Module, CSA Standardization & Channel Variants
**Gate:** G11
**Architectural Approval:** `_COMMUNICATION/TEAM_100/reports/2026-04-04_M13_ARCHITECTURAL_APPROVAL_TEAM100.md`

---

## Scope

M13 introduces three major changes:
1. **Publish JSON v3** — `details` object on every product with `price_series`, `details_variant`, `source_count`, and channel-specific blocks (`csa`, `store`, `benchmark`)
2. **Frontend details module** — inline accordion per product row with price chart (Chart.js), variant-specific content blocks, RTL layout
3. **Privacy enforcement** — no source identification (codes, names, URLs) in any public-facing output

**Privacy constraint is BINDING:** Any source-identifying data in the public report constitutes a Critical failure regardless of other criteria.

**Key files changed (expected):**
- `organic_market_agent/publisher/rolling_aggregate.py`
- `organic_market_agent/publisher/engine.py`
- `organic_market_agent/publisher/templates/public_report_body.html`
- `organic_market_agent/publisher/templates/public_report.html`
- New unit tests for schema validation and privacy checks

---

## Pre-conditions (verify before starting)

**Amended 2026-04-06 (ROADMAP v5.4 + M13-PRE addendum + Team 100 waiver):** M13-PRE §4 is **not** a hard blocker for G11. Product count **≥90** is **waived** when **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER** is on file.

```bash
# 1. M13-PRE / data readiness — one of:
#    (a) Scoped G-PRE-1..7 PASS or CONDITIONAL PASS (see QA_MANDATE_M13_PRE_GPRE_TEAM50.md), OR
#    (b) ROADMAP v5.4 direction + addendum + Team 100 G-PRE-5 waiver for sub-90 product count.
#    Verify waiver path: _COMMUNICATION/TEAM_100/reports/2026-04-05_ARCH_DECISION_GPRE5_PUBLISHED_PRODUCT_COUNT_WAIVER_TEAM100.md

# 2. Alembic at head
python3 -m alembic current
# Expected: latest revision (head)

# 3. DB health
python3 -m organic_market_agent.db.check
# Expected: RESULT: PASS

# 4. Full test suite green
python3 -m pytest tests/ -q
# Expected: all passed, 0 failures

# 5. PostgreSQL — EITHER:
#    (a) docker ps | grep postgres  → running container, OR
#    (b) direct local PostgreSQL with same DB used for publish — db.check PASS satisfies this row

# 6. Published report exists (after run_publisher on certified DB)
python3 -c "import json; d=json.load(open('output/public/public_report.json')); print('products:', len(d['products']), 'schema:', d.get('report_schema_version', 'N/A'))"
# Expected: report_schema_version == '3.0'; products >= 90 OR waiver ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER documents lower count
```

---

## Test Suite

### T01 — Full pytest suite (regression)

```bash
python3 -m pytest tests/ -q
```

**Pass criterion:** All passed, 0 failures. Skips acceptable (upress markers).
**Weight:** Critical

---

### T02 — Publish JSON v3 schema validation

```bash
python3 -m organic_market_agent run_publisher
python3 -c "
import json
d = json.load(open('output/public/public_report.json'))
assert d.get('report_schema_version') == '3.0', f'Expected 3.0, got {d.get(\"report_schema_version\")}'
for p in d['products']:
    assert 'details' in p, f'Missing details on {p[\"product_id\"]}'
    det = p['details']
    assert 'details_variant' in det, f'Missing details_variant on {p[\"product_id\"]}'
    assert 'source_count' in det, f'Missing source_count on {p[\"product_id\"]}'
    assert isinstance(det['source_count'], int), f'source_count not int on {p[\"product_id\"]}'
    assert det['details_variant'] in ('grower_price_grid', 'basket_csa', 'store_retail', 'chain_benchmark'), f'Unknown variant {det[\"details_variant\"]} on {p[\"product_id\"]}'
print('PASS: all products have valid details object')
print(f'Products: {len(d[\"products\"])}')
"
```

**Pass criterion:** All products have `details` with valid `details_variant` and integer `source_count`.
**Weight:** Critical

---

### T03 — Price series validation

```bash
python3 -c "
import json
d = json.load(open('output/public/public_report.json'))
products_with_series = [p for p in d['products'] if p['details'].get('price_series')]
products_without = [p for p in d['products'] if not p['details'].get('price_series')]
print(f'Products WITH price_series: {len(products_with_series)}')
print(f'Products WITHOUT price_series: {len(products_without)}')
for p in products_with_series:
    series = p['details']['price_series']
    assert len(series) >= 3, f'{p[\"product_id\"]} has < 3 points ({len(series)})'
    assert len(series) <= 30, f'{p[\"product_id\"]} exceeds 30-point cap ({len(series)})'
    for pt in series:
        assert 'd' in pt and 'v' in pt, f'Missing d/v in point for {p[\"product_id\"]}'
        assert isinstance(pt['v'], (int, float)), f'Non-numeric value in {p[\"product_id\"]}'
print('PASS: all price_series valid, capped, min 3 points')
"
```

**Pass criterion:**
- Products with price_series have >= 3 and <= 30 points (or <= 12 for baskets)
- Each point has `d` (date string) and `v` (numeric value)
- No NaN or Infinity values

**Weight:** Critical

---

### T04 — Privacy audit (CRITICAL)

```bash
python3 -c "
import json, re
d = json.load(open('output/public/public_report.json'))
report_str = json.dumps(d, ensure_ascii=False)

# Check for source codes
src_pattern = re.compile(r'SRC\d{3}')
matches = src_pattern.findall(report_str)
assert not matches, f'PRIVACY VIOLATION: source codes found in public JSON: {matches}'

# Check for source names (known farms)
farm_names = ['חוות שורשים', 'משק אורגני', 'משק יוסף', 'קיימא', 'עץ השדה',
              'ניצת הדובדבן', 'ערן אורגני', 'טמרי', 'רעות', 'טבע שוק',
              'havatshorashim', 'meshekorgani', 'meshek-yosef', 'mypips.app']
for name in farm_names:
    assert name not in report_str, f'PRIVACY VIOLATION: farm name \"{name}\" found in public JSON'

# Check for source URLs
url_pattern = re.compile(r'https?://[^\s\"]+')
urls = url_pattern.findall(report_str)
assert not urls, f'PRIVACY VIOLATION: URLs found in public JSON: {urls}'

print('PASS: no source codes, names, or URLs in public JSON')
"
```

**Pass criterion:** Zero matches for source codes, farm names, or URLs in the public JSON output.
**Weight:** Critical (privacy violation = automatic gate FAIL)

---

### T05 — Privacy audit on HTML artifacts

```bash
python3 -c "
import re
for fname in ['output/public/public_report.html', 'output/public/public_report_body.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        html = f.read()
    src_matches = re.findall(r'SRC\d{3}', html)
    assert not src_matches, f'PRIVACY VIOLATION in {fname}: {src_matches}'
    farm_names = ['חוות שורשים', 'משק אורגני', 'משק יוסף', 'קיימא', 'עץ השדה',
                  'ניצת הדובדבן', 'ערן אורגני', 'טמרי', 'טבע שוק']
    for name in farm_names:
        assert name not in html, f'PRIVACY VIOLATION in {fname}: \"{name}\"'
    print(f'PASS: {fname} — no source identification')
"
```

**Pass criterion:** No source-identifying data in HTML artifacts.
**Weight:** Critical

---

### T06 — Manifest v3 schema

```bash
python3 -c "
import json
m = json.load(open('output/public/manifest.json'))
assert m.get('schema_version') == '3.0', f'Expected 3.0, got {m.get(\"schema_version\")}'
print(f'PASS: manifest schema_version = {m[\"schema_version\"]}')
print(f'Product count: {m.get(\"product_count\")}')
print(f'Staleness: {m.get(\"staleness_level\")}')
"
```

**Pass criterion:** `schema_version` is `"3.0"`. **`product_count` ≥ 90** OR **Team 100 waiver** **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER** applies (document observed count in findings).
**Weight:** Critical

---

### T07 — CSA basket details validation

```bash
python3 -c "
import json
d = json.load(open('output/public/public_report.json'))
baskets = [p for p in d['products'] if p.get('category') == 'baskets']
print(f'Basket products in report: {len(baskets)}')
for b in baskets:
    det = b['details']
    assert det['details_variant'] == 'basket_csa', f'{b[\"product_id\"]}: expected basket_csa, got {det[\"details_variant\"]}'
    csa = det.get('csa')
    if csa:
        print(f'  {b[\"product_id\"]} ({b[\"canonical_name_he\"]}): contents={bool(csa.get(\"contents_summary_generalized\"))}, cadence={bool(csa.get(\"cadence_note\"))}, incomplete={csa.get(\"context_incomplete\")}')
    else:
        print(f'  {b[\"product_id\"]} ({b[\"canonical_name_he\"]}): csa=null')
print('PASS: all basket products have basket_csa variant')
"
```

**Pass criterion:** All basket-category products have `details_variant: "basket_csa"`. CSA context present where sources provide it.
**Weight:** High

---

### T08 — Variant distribution check

```bash
python3 -c "
import json
from collections import Counter
d = json.load(open('output/public/public_report.json'))
variants = Counter(p['details']['details_variant'] for p in d['products'])
print('Variant distribution:')
for v, c in variants.most_common():
    print(f'  {v}: {c}')
assert 'grower_price_grid' in variants, 'No grower_price_grid products'
print('PASS: variant distribution verified')
"
```

**Pass criterion:** At least `grower_price_grid` variant present. `store_retail` expected if SRC036 is active. `basket_csa` expected if CSA sources are active.
**Weight:** High

---

### T09 — JSON report size budget

```bash
python3 -c "
import os
size = os.path.getsize('output/public/public_report.json')
print(f'Report size: {size:,} bytes ({size/1024:.1f} KB)')
assert size <= 512_000, f'Report exceeds 500 KB soft limit: {size:,} bytes'
print('PASS: within 500 KB budget')
"
```

**Pass criterion:** Report file <= 500 KB.
**Weight:** Medium

---

## Live Site Tests (MCP Browser Required)

### T10 — Details module renders on live page

Navigate MCP browser to `https://nimrod.bio/SmallFarmsAgent/`. Take snapshot.

**Pass criterion:**
- Each product row has a details trigger (chevron or button)
- Clicking trigger opens an accordion panel
- Panel shows source count, price statistics
- No farm names or source codes visible in the expanded panel

**Weight:** Critical

---

### T11 — Price chart rendering

On the live page, expand a product detail that has >= 3 price series points.

**Pass criterion:**
- Chart.js canvas renders inside the accordion panel
- Chart has Hebrew date labels on X-axis
- RTL layout: chart direction correct (most recent on left for RTL)
- No JavaScript errors in console

**Weight:** High

---

### T12 — CSA basket variant display

Expand a basket product detail on the live page.

**Pass criterion:**
- "basket_csa" variant blocks visible: contents summary, cadence note
- "contents vary" disclaimer visible
- No specific farm name or URL shown

**Weight:** High

---

### T13 — Filter bar + details module interaction

On the live page, expand a product detail. Then click a different filter button.

**Pass criterion:**
- Filter correctly hides/shows rows
- Expanded detail accordion collapses or remains consistent
- No JavaScript errors

**Weight:** Medium

---

### T14 — Mobile RTL layout

Using MCP browser viewport simulation (375px width), navigate to the live page.

**Pass criterion:**
- Table is scrollable horizontally
- Details accordion opens below the row and is readable
- Chart scales to mobile width
- All Hebrew text is RTL-aligned

**Weight:** High

---

### T15 — Accessibility check

Using MCP browser, test keyboard navigation on the details module.

**Pass criterion:**
- Tab key reaches details trigger buttons
- Enter/Space opens accordion
- `aria-expanded` attribute toggles on the trigger
- Focus stays within the accordion when open (focus management)
- Escape or re-click closes the accordion

**Weight:** High

---

## Gate Pass Criteria

| # | Criterion | Weight |
|---|-----------|--------|
| 1 | Full pytest suite passes (T01) | Critical |
| 2 | Publish JSON v3 schema valid (T02) | Critical |
| 3 | Price series valid and capped (T03) | Critical |
| 4 | Privacy audit on JSON — zero violations (T04) | Critical |
| 5 | Privacy audit on HTML — zero violations (T05) | Critical |
| 6 | Manifest v3 schema correct (T06) | Critical |
| 7 | CSA basket variant correct (T07) | High |
| 8 | Variant distribution verified (T08) | High |
| 9 | JSON size within budget (T09) | Medium |
| 10 | Details module renders on live page (T10) | Critical |
| 11 | Price chart renders correctly (T11) | High |
| 12 | CSA variant display correct (T12) | High |
| 13 | Filter + details interaction (T13) | Medium |
| 14 | Mobile RTL layout correct (T14) | High |
| 15 | Keyboard accessibility (T15) | High |

**Gate G11 PASS** requires:
- All **Critical** criteria met (T01–T06, T10)
- All **High** criteria met or documented remediation plan (T07, T08, T11, T12, T14, T15)
- **Medium** failures logged as known issues

**PRIVACY OVERRIDE:** Any privacy violation (T04 or T05 fail) results in **automatic gate FAIL** regardless of all other criteria.

---

## Reporting

File your gate report at:
`_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_GATE_G11_REPORT_TEAM50.md`

Use the canonical template:
`_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`

---

*Issued by: Team 100 (Architecture)*  
*Date: 2026-04-04*  
*Amended: 2026-04-06 — preconditions + T06 aligned with ROADMAP v5.4, M13-PRE addendum, G-PRE-5 waiver **ARCH-20260405-GPRE5-PRODUCT-COUNT-WAIVER***
