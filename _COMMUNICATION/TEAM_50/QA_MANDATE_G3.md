> ⚠️ **SUPERSEDED — 2026-03-30**
> This document is superseded by `QA_MANDATE_G3_v2.md`.
> Per architectural decision `ARCH-20260330-G3-DATA-QUALITY`, the `≥ 40` threshold in this
> document has been retired. `QA_MANDATE_G3_v2.md` is the single binding G3 QA reference.
> Do NOT use this document for any new QA execution.

# QA Mandate — Gate G3 (M3 Normalizer Engine)
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**Date:** 2026-03-30  
**Gate:** G3  
**Prerequisites:**
- Gate G2 formally open ✅
- Team 20 seed patch (migrations 006 + 007) applied and verified
- Team 10 M3 completion report filed in `_COMMUNICATION/TEAM_10/reports/`

---

## Pre-Test: Seed Patch Verification

Before running any normalizer tests, confirm:
```sql
-- No product missing aliases
SELECT COUNT(*) FROM products p
LEFT JOIN product_aliases pa ON pa.product_id = p.id AND pa.is_active = true
WHERE pa.id IS NULL AND p.is_active = true;
```
**Must return 0.** If not, stop and require Team 20 to apply migrations 006 + 007.

---

## T01 — Unit Tests

```bash
python -m pytest tests/test_normalizer.py -v
```
**Pass criterion:** All tests PASS. Minimum 12 tests present.

```bash
python -m pytest tests/ -v
```
**Pass criterion:** Full suite (M1 + M2 + M3 tests) all PASS — no regression.

---

## T02 — Normalizer Run

```bash
python -m organic_market_agent.normalizer.run_normalizer
```
Or: `python -m organic_market_agent.scheduler.run_ingestion --normalize`

Capture full output.

**Pass criterion:**
- `resolved` count ≥ 40
- Process exits normally (exit code 0)

---

## T03 — normalized_observations Volume and Integrity

```sql
SELECT COUNT(*) AS total,
       COUNT(CASE WHEN product_id IS NOT NULL THEN 1 END) AS with_product,
       COUNT(CASE WHEN price_amount IS NOT NULL THEN 1 END) AS with_price,
       COUNT(CASE WHEN flag_status = 'ok' THEN 1 END) AS ok_status
FROM normalized_observations;
```
**Pass criterion:** `total` ≥ 40, `with_product` = `total`, `with_price` = `total`

---

## T04 — No FLOAT

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'normalized_observations'
  AND data_type IN ('real','double precision','float4','float8');
```
**Pass criterion:** 0 rows.

---

## T05 — Confidence Score Range

```sql
SELECT MIN(confidence_score), MAX(confidence_score),
       COUNT(CASE WHEN confidence_score < 0.10 THEN 1 END) AS below_floor,
       COUNT(CASE WHEN confidence_score > 1.00 THEN 1 END) AS above_ceiling
FROM normalized_observations;
```
**Pass criterion:** `below_floor = 0`, `above_ceiling = 0`, min ≥ 0.10, max ≤ 1.00

---

## T06 — Basket Policy

```sql
SELECT COUNT(*) AS basket_with_normalized_price
FROM normalized_observations
WHERE is_basket_product = true
  AND normalized_price_value IS NOT NULL;
```
**Pass criterion:** 0 rows.

```sql
SELECT COUNT(*) AS basket_observations
FROM normalized_observations
WHERE is_basket_product = true;
```
**Informational:** confirm basket products are present and being collected.

---

## T07 — extraction_status Updated

```sql
SELECT extraction_status, COUNT(*) AS cnt
FROM raw_extracted_items
GROUP BY extraction_status;
```
**Pass criterion:**
- `normalized` count > 0
- `extracted` count = 0 (all pending items processed)
- `unresolvable` count acceptable (expect some; verify unresolvable_reason is populated)

```sql
SELECT COUNT(*) AS unresolvable_missing_reason
FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
  AND unresolvable_reason IS NULL;
```
**Pass criterion:** 0 rows.

---

## T08 — DB-Driven Alias Test

Insert a new alias for a product, re-run the normalizer on one raw item with that name, verify resolution changes:

```sql
-- Step 1: find a raw_extracted_item that is currently unresolvable
SELECT id, raw_product_name FROM raw_extracted_items
WHERE extraction_status = 'unresolvable'
LIMIT 1;
```

```sql
-- Step 2: insert an alias for that raw_product_name → map to an existing product
INSERT INTO product_aliases (product_id, alias_text, alias_text_normalized, source_id, confidence, is_active)
VALUES (
    (SELECT id FROM products WHERE code = 'PRD001'),
    '<raw_product_name from step 1>',
    lower(trim('<raw_product_name from step 1>')),
    NULL, 0.80, true
);
```

```sql
-- Step 3: reset the item to 'extracted' so normalizer re-processes it
UPDATE raw_extracted_items SET extraction_status = 'extracted' WHERE id = <id from step 1>;
```

```bash
# Step 4: re-run normalizer
python -m organic_market_agent.normalizer.run_normalizer
```

```sql
-- Step 5: verify it resolved
SELECT id, extraction_status, raw_product_name
FROM raw_extracted_items WHERE id = <id>;
```

**Pass criterion:** `extraction_status = 'normalized'`, corresponding `normalized_observations` row exists.

**Cleanup:**
```sql
DELETE FROM product_aliases WHERE alias_text = '<inserted alias text>' AND source_id IS NULL;
```

---

## T09 — Regression: M1 + M2 Tables Unchanged

```sql
SELECT 'measurement_units' AS tbl, COUNT(*) FROM measurement_units
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sources', COUNT(*) FROM sources
UNION ALL SELECT 'raw_assets', COUNT(*) FROM raw_assets
UNION ALL SELECT 'raw_extracted_items', COUNT(*) FROM raw_extracted_items;
```
**Pass criterion:** All counts match those confirmed at G2. M3 must not modify any M1 or M2 data.

---

## T10 — No session.query() + No Float in Code

```bash
grep -rn "session\.query\(" organic_market_agent/normalizer/
```
**Pass criterion:** 0 matches.

```bash
grep -rn "float(" organic_market_agent/normalizer/
grep -rn "= [0-9]\+\.[0-9]\+$" organic_market_agent/normalizer/
```
**Pass criterion:** No bare float literals assigned to price/score variables.

---

## Scoring

| # | Test | Weight |
|---|------|--------|
| Pre | Seed patch applied (0 products missing aliases) | Critical |
| T01 | Unit tests all PASS (M3 + full regression) | Critical |
| T02 | Normalizer run: resolved ≥ 40 | Critical |
| T03 | normalized_observations volume + integrity | Critical |
| T04 | No FLOAT columns | Critical |
| T05 | Confidence in [0.10, 1.00] | Critical |
| T06 | Basket policy: no normalized_price for baskets | Critical |
| T07 | extraction_status updated, unresolvable_reason populated | High |
| T08 | DB-driven alias test | Critical |
| T09 | M1 + M2 regression | Critical |
| T10 | No session.query(), no float literals | High |

**Gate G3 opens only if all Critical tests PASS.**

---

## Submission

File: `_COMMUNICATION/TEAM_50/reports/{date}_QA_G3_TEAM50.md`
Include all SQL outputs, CLI outputs, and reference to the G2 report that unlocked G3.
