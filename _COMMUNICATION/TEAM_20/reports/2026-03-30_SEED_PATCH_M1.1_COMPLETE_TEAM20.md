# Team 20 — Seed Patch M1.1 Complete
**Date:** 2026-03-30
**From:** Team 20 (Infrastructure)
**Gate dependency:** G3 (unblocks alias completeness check in T10 scope)

---

## Alembic Upgrade Output

```
INFO  [alembic.runtime.migration] Running upgrade 005 -> 006, 006: Complete product alias coverage — 13 products missing from revision 005.
INFO  [alembic.runtime.migration] Running upgrade 006 -> 007, 007: Fix source profiles — normalizer_type alignment + selector overrides.
```

Current version: `007`

---

## Alias Completeness Verification

```sql
SELECT p.code, p.canonical_name_he
FROM products p
LEFT JOIN product_aliases pa ON pa.product_id = p.id AND pa.is_active = true
WHERE pa.id IS NULL AND p.is_active = true;
```

**Result: 0 rows** ✅

---

## Source Profiles Verification

```sql
SELECT s.code, np.normalizer_type, sfp.is_active AS profile_active, s.is_active AS src_active
FROM sources s
JOIN normalizer_profiles np ON np.source_id = s.id
JOIN source_fetch_profiles sfp ON sfp.source_id = s.id
WHERE s.code IN ('SRC015','SRC016','SRC018','SRC019','SRC020')
ORDER BY s.code;
```

```
 code  |    normalizer_type    | profile_active | src_active
-------+-----------------------+----------------+------------
 SRC015 | official_wholesale   | f              | f
 SRC016 | official_wholesale   | f              | f
 SRC018 | simple_product_grid  | t              | t
 SRC019 | simple_product_grid  | t              | t
 SRC020 | simple_product_grid  | t              | t
```

✅ SRC015, SRC016 deactivated  
✅ SRC018–SRC020 normalizer_type corrected  

---

## DB Health Check

```
RESULT: PASS
  OK  measurement_units: 11 rows
  OK  products: 29 rows
  OK  sources: 20 rows
```

---

## Deliverables

- [x] `organic_market_agent/db/versions/006_seed_aliases_complete.py`
- [x] `organic_market_agent/db/versions/007_fix_source_profiles.py`
- [x] `alembic upgrade head` — both revisions applied cleanly
- [x] Alias completeness: 0 products without aliases
- [x] Source profiles: SRC018–020 fixed, SRC015–016 deactivated
- [x] EasyFarm `selector_profile` JSONB populated for SRC002, 004, 005, 006
- [x] `db.check` PASS

---

Seed Patch M1.1 complete. Blocking items P1–P3 from G1/G2 are resolved.
