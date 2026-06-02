# A1 — Cherry + basket guard SQL (evidence placeholder)

**Date:** 2026-04-08  
**Spec:** `SPEC-20260408-PHASE-A-LOD400` §A1

## Queries (use `products.code`)

```sql
-- Cherry guard (expected: 0 rows after migration 067 + triage)
SELECT pa.id, pa.alias_text, p.code AS product_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code = 'PRD001'
  AND pa.is_active = TRUE
  AND (pa.alias_text ILIKE '%שרי%' OR pa.alias_text ILIKE '%cherry%' OR pa.alias_text ILIKE '%צ''רי%');

-- Basket inactive-product guard (expected: 0 rows after migration 068)
SELECT pa.id, pa.alias_text, p.code AS product_code
FROM product_aliases pa
JOIN products p ON pa.product_id = p.id
WHERE p.code IN ('PRD028', 'PRD029')
  AND pa.is_active = TRUE;
```

## Result (this session)

**Not executed** — PostgreSQL unreachable. Per spec §0 (F3, F4), drift-fix migrations **067** / **068** already addressed CQ-P08 / CQ-P09; expectation on a current DB is **0 rows**.

**Operator:** paste `psql` output into the v1.1 completion report §3 when DB is online.
