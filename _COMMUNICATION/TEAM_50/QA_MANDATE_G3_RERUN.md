> ⚠️ **SUPERSEDED — 2026-03-30**
> This document served as the binding authority that opened G3 (PASS).
> It is now superseded by `QA_MANDATE_G3_v2.md`, which is the single forward-looking G3 reference.
> This document is preserved as a historical record of the gate decision only.
> Do NOT use this document for any new QA execution.

# Mandate — Team 50: Re-run QA Gate G3 (Post-Fix)
**From:** Team 100 (Architecture)
**Date:** 2026-03-30
**Status:** G3 re-opened for QA after fixes by Team 20 and Team 10

---

## Summary of Fixes Applied

| Fix | Team | Status |
|-----|------|--------|
| Migration 008: `unresolvable_reason VARCHAR(200) → TEXT` | Team 20 | ✅ Applied, Alembic v008 |
| `simple_product_grid._try_list`: requires name+price elements | Team 10 | ✅ Applied |
| `easyfarm_catalog`: skips rows where price is None | Team 10 | ✅ Applied |
| `engine.py`: caps unresolvable_reason at 500 chars | Team 10 | ✅ Applied |
| `test_normalizer_engine_resolves_one_row`: fixed skip condition | Team 10 | ✅ Applied |
| `tests/test_parsers.py`: updated `_try_list` test expectations | Team 10 | ✅ Applied |

---

## Pre-conditions

Before running any test:

```bash
python --version          # must be 3.11+
docker ps | grep postgres # must show OMA postgres container running
echo $DATABASE_URL        # must point to Docker port
alembic current           # must show 008 (head)
```

---

## T01 — Unit Tests (updated suite)

```bash
python3.11 -m pytest tests/ -q
```

**Pass criterion:** All 46 tests PASS, 0 skipped, 0 failures.

> Note: test count increased from 44 to 46:
> - `test_normalizer_engine_resolves_one_row` now PASSES (was skipped)
> - `test_simple_grid_list_structured_extracts` is a new test
> - `test_simple_grid_list_fallback_extracts` now expects `[]` (correct new behavior)

---

## T02 — Normalizer Run (no crash)

```bash
python3.11 -m organic_market_agent run_normalizer
```

**Pass criterion:**
- No `StringDataRightTruncation` error
- Output line: `NormalizerEngine complete: resolved=N unresolvable=M skipped=K`
- If `resolved=0`: check Team 10's re-ingestion was completed (Step 5 of their mandate).
  If re-ingestion has not been run yet, resolved=0 is expected from existing G2 data
  (those 1635 items are legitimate unresolvables — garbage extracted by old parser).

**Critical check after run:**
```sql
SELECT extraction_status, COUNT(*) FROM raw_extracted_items GROUP BY extraction_status;
```
→ Must NOT show any items remaining as `extracted` (all processed).

---

## T03 — normalized_observations integrity

Run ONLY after Team 10 has completed re-ingestion (Step 5 of their mandate).

```sql
SELECT COUNT(*) FROM normalized_observations;
```

**Pass criterion (after re-ingestion):** `COUNT(*) > 0`

If Team 10 has not yet re-ingested, record `0` and note as pending re-ingestion.
This T03 check gates G3 final sign-off only after re-ingestion is complete.

Type safety:
```sql
SELECT COUNT(*) FROM normalized_observations
WHERE price_amount::text LIKE '%.%'
AND price_amount != CAST(price_amount AS NUMERIC(12,4));
```
→ 0 rows (all prices store as exact NUMERIC).

---

## T04 — unresolvable_reason column type

```bash
docker exec oma-g2-ev psql -U oma -d organic -c "\d raw_extracted_items" | grep unresolvable
```

**Pass criterion:**
```
 unresolvable_reason   | text    |    | |
```
NOT `character varying(200)`.

---

## T05 — confidence score range

```sql
SELECT COUNT(*) FROM normalized_observations
WHERE confidence_score < 0 OR confidence_score > 1;
```
→ 0 rows (only meaningful after re-ingestion produces normalized rows).

---

## T06 — basket policy

```sql
SELECT COUNT(*) FROM normalized_observations no_obs
WHERE no_obs.is_basket_product = true
AND no_obs.normalized_price_value IS NOT NULL;
```
→ 0 rows (basket products must have normalized_price_value = NULL).

---

## T07 — extraction_status updated

```sql
SELECT extraction_status, COUNT(*) FROM raw_extracted_items
GROUP BY extraction_status;
```

**Pass criterion:**
- No rows with `extraction_status = 'extracted'` after normalizer run
- `unresolvable` count ≤ total count (some may be genuinely unresolvable)
- `normalized` count ≥ 0 (> 0 required only after re-ingestion)

---

## T08 — unresolvable_reason not truncated

```sql
SELECT MAX(LENGTH(unresolvable_reason)) FROM raw_extracted_items
WHERE unresolvable_reason IS NOT NULL;
```

**Pass criterion:** No error. Result may exceed 200 (confirms TEXT column works).
Note: application caps at 500 chars, so result ≤ 500.

---

## T09 — M1 + M2 regression

```bash
python3.11 -m pytest tests/test_db_health.py tests/test_collectors.py tests/test_parsers.py -q
```

**Pass criterion:** All pass. No regression from parser or engine changes.

---

## T10 — Code quality

```bash
python3.11 -m pytest tests/ -q   # no session.query(), no float()
grep -rn "session\.query(" organic_market_agent/
grep -rn "float(" organic_market_agent/normalizer/
```

Both grep commands must return 0 matches.

---

## Gate G3 Sign-off Criteria

| Test | Pass Condition | Priority |
|------|---------------|---------|
| T01 | 46 passed, 0 skipped | Critical |
| T02 | Normalizer runs without crash | Critical |
| T03 | `normalized_observations` > 0 (post re-ingestion) | Critical |
| T04 | `unresolvable_reason` column is TEXT | Critical |
| T05 | Confidence 0–1 (post re-ingestion) | High |
| T06 | Basket policy correct | High |
| T07 | No items stuck in `extracted` | High |
| T08 | Long unresolvable_reason stored without truncation | High |
| T09 | M1+M2 regression pass | Critical |
| T10 | No session.query(), no float() | High |

**Gate G3 PASS requires:** All Critical items pass + at least 8/10 total.

> T03/T05/T06 can be marked "PENDING re-ingestion" if Team 10 has not yet
> completed Step 5. In that case, G3 opens as Conditional Pass pending re-ingestion verification.
