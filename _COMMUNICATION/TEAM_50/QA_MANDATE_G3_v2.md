---
document_type: QA_MANDATE
version: "2.0"
supersedes: QA_MANDATE_G3.md, QA_MANDATE_G3_RERUN.md
---

# QA Mandate — Gate G3 (Version 2)
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**Date:** 2026-03-30
**Status:** ACTIVE — this is the single binding G3 QA reference

> **Prior mandates SUPERSEDED.** Both `QA_MANDATE_G3.md` and `QA_MANDATE_G3_RERUN.md` are
> retired. Per architectural decision `ARCH-20260330-G3-DATA-QUALITY`, this document is the
> forward-looking G3 QA specification. It uses cohort-scoped metrics and replaces historical
> count thresholds with per-cycle KPIs.

---

## Scope

This mandate defines all checks Team 50 must run to certify Gate G3 for **any new normalizer
validation cycle** — whether a first-time G3 check on a fresh deployment or a re-validation
triggered by a mandate fix.

Key change from v1: **metrics are scoped to a single ingestion cohort** identified by
`--ingestion-run-id <N>`. The DB-wide `≥ 40` threshold is retired.

---

## Pre-conditions

Before running any test, confirm the environment is ready:

```bash
python3.11 --version               # must be 3.11+
docker ps | grep postgres          # must show OMA postgres container running
echo $DATABASE_URL                 # must point to Docker port (55435 or 5433)
alembic current                    # must show head (008 or later)
```

Identify the target ingestion run:
```bash
# List recent runs — pick the most recent successful ingestion from price_grid sources
python3.11 -m organic_market_agent run_ingestion --list-runs
# Note the run_id, call it <RUN_ID>
```

Confirm run has qualifying rows:
```sql
SELECT COUNT(*) FROM raw_extracted_items
WHERE source_fetch_run_id = (
    SELECT id FROM source_fetch_runs WHERE ingestion_run_id = <RUN_ID> LIMIT 1
)
AND extraction_status = 'extracted';
```
→ Must be > 0 before proceeding to T02.

---

## T01 — Unit Test Suite

```bash
python3.11 -m pytest tests/ -q
```

**Pass criterion:** All tests PASS, 0 skipped, 0 failures.
Expected minimum: 46 tests (may grow as new tests are added).

---

## T02 — Normalizer Run (Cohort-Scoped)

Run the normalizer against a specific ingestion cohort:

```bash
python3.11 -m organic_market_agent run_normalizer --ingestion-run-id <RUN_ID>
```

**Pass criterion (all three must hold):**

1. No runtime exception (no `StringDataRightTruncation`, no unhandled crash)
2. Log line confirms completion:
   `NormalizerEngine complete: resolved=N unresolvable=M skipped=K`
3. **`resolved ≥ 10`** — at least 10 items resolved within this cohort

> If `resolved < 10` for this cohort, the issue is either source availability (fetch failures)
> or missing aliases. Record the actual count and check T02-DIAG below before declaring FAIL.

**T02-DIAG (run if resolved < 10):**
```sql
SELECT s.code, COUNT(*) AS item_count, r.extraction_status
FROM raw_extracted_items r
JOIN source_fetch_runs sfr ON r.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE sfr.ingestion_run_id = <RUN_ID>
GROUP BY s.code, r.extraction_status
ORDER BY s.code;
```
Document: how many active price_grid sources participated, and which had extraction_status = 'normalized'.

---

## T03 — Normalized Observations (Cohort-Scoped)

```sql
-- Check total observations from this cohort
SELECT COUNT(*) AS total_observations,
       COUNT(DISTINCT product_id) AS distinct_products
FROM normalized_observations no_obs
WHERE no_obs.source_fetch_run_id IN (
    SELECT id FROM source_fetch_runs WHERE ingestion_run_id = <RUN_ID>
);
```

**Pass criterion (both must hold):**
1. `total_observations > 0`
2. `distinct_products ≥ 3`

Type safety check:
```sql
SELECT COUNT(*) FROM normalized_observations
WHERE price_amount != CAST(price_amount AS NUMERIC(12,4));
```
→ 0 rows.

---

## T04 — Schema: `unresolvable_reason` Column Type

```bash
# Adjust container/db name to match environment
docker exec <oma-container> psql -U oma -d organic -c "\d raw_extracted_items" | grep unresolvable
```

**Pass criterion:**
```
 unresolvable_reason   | text    |    | |
```
Must NOT be `character varying(200)`.

---

## T05 — Confidence Score Range

```sql
SELECT COUNT(*) FROM normalized_observations no_obs
JOIN source_fetch_runs sfr ON no_obs.source_fetch_run_id = sfr.id
WHERE sfr.ingestion_run_id = <RUN_ID>
AND (no_obs.confidence_score < 0 OR no_obs.confidence_score > 1);
```
→ 0 rows.

---

## T06 — Basket Policy

```sql
SELECT COUNT(*) FROM normalized_observations no_obs
JOIN source_fetch_runs sfr ON no_obs.source_fetch_run_id = sfr.id
WHERE sfr.ingestion_run_id = <RUN_ID>
AND no_obs.is_basket_product = true
AND no_obs.normalized_price_value IS NOT NULL;
```
→ 0 rows (basket products must have `normalized_price_value = NULL`).

---

## T07 — Extraction Status Completeness

After normalizer run, no items from the target cohort should remain `extracted`:

```sql
SELECT extraction_status, COUNT(*)
FROM raw_extracted_items
WHERE source_fetch_run_id IN (
    SELECT id FROM source_fetch_runs WHERE ingestion_run_id = <RUN_ID>
)
GROUP BY extraction_status;
```

**Pass criterion:** No rows with `extraction_status = 'extracted'`.
Valid statuses after normalization: `normalized`, `unresolvable`, `ignored`.

---

## T08 — Long Reason Storage (Not Truncated)

```sql
SELECT MAX(LENGTH(unresolvable_reason)) AS max_len FROM raw_extracted_items
WHERE unresolvable_reason IS NOT NULL;
```

**Pass criterion:** Query runs without error.
Result ≤ 500 (application cap), column accepts values > 200 (confirms TEXT, not VARCHAR(200)).

---

## T09 — Regression: M1 + M2 Layers Intact (Quiet-DB Protocol)

This test must follow the quiet-DB protocol: capture counts before and after the cohort run,
confirm M1/M2 data is unchanged.

**Step 1 — Baseline (before normalizer run):**
```sql
SELECT
    (SELECT COUNT(*) FROM raw_assets) AS raw_assets_count,
    (SELECT COUNT(*) FROM raw_extracted_items) AS raw_extracted_count;
```
Record result as `BASELINE`.

**Step 2 — After cohort normalizer run, re-check:**
```sql
SELECT
    (SELECT COUNT(*) FROM raw_assets) AS raw_assets_count,
    (SELECT COUNT(*) FROM raw_extracted_items) AS raw_extracted_count;
```
Record result as `POST_RUN`.

**Pass criterion:**
- `raw_assets_count`: BASELINE == POST_RUN (normalizer never writes to raw_assets)
- `raw_extracted_items`: POST_RUN >= BASELINE (may grow if ingestion ran with normalization; must NOT shrink)

Also run unit regression:
```bash
python3.11 -m pytest tests/test_db_health.py tests/test_collectors.py tests/test_parsers.py -q
```
→ All pass.

---

## T10 — Code Quality: No Deprecated Patterns

```bash
grep -rn "session\.query(" organic_market_agent/
grep -rn "float(" organic_market_agent/normalizer/
```

Both commands must return 0 matches.

---

## T11 — Forward Metrics: Per-Cycle KPIs

After the cohort normalizer run, verify forward metrics. This test requires migration 009
to be applied (if it has not been applied yet, record T11 as PENDING).

```sql
-- Unresolvable rate on price_grid sources only (requires source_tier column from migration 009)
SELECT
    COUNT(*) FILTER (WHERE r.extraction_status = 'normalized') AS resolved,
    COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable') AS unresolvable,
    COUNT(*) AS total,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable')
        / NULLIF(COUNT(*), 0),
        1
    ) AS unresolvable_rate_pct
FROM raw_extracted_items r
JOIN source_fetch_runs sfr ON r.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
WHERE sfr.ingestion_run_id = <RUN_ID>
  AND s.source_tier = 'price_grid'
  AND r.is_quarantined = false;
```

**Pass criterion (after migration 009):**
- `unresolvable_rate_pct ≤ 30%` on price_grid, non-quarantined items
- Community source count: at least 2 price_grid sources with `extraction_status = 'normalized'` rows

> If migration 009 has not been applied, run T11 with source_group = 'community' filter as
> a proxy and mark result as "T11-PARTIAL (pre-009)".

---

## Gate G3 Sign-off Criteria

| Test | Pass Condition | Priority | Pre-009 OK? |
|------|---------------|----------|-------------|
| T01 | All unit tests pass, 0 skipped | Critical | Yes |
| T02 | No crash, `resolved ≥ 10` in cohort | Critical | Yes |
| T03 | `total > 0`, `distinct_products ≥ 3` in cohort | Critical | Yes |
| T04 | `unresolvable_reason` is TEXT | Critical | Yes |
| T05 | Confidence 0–1 in cohort | High | Yes |
| T06 | Basket policy correct in cohort | High | Yes |
| T07 | No items stuck in `extracted` in cohort | High | Yes |
| T08 | Long reason stored without error | High | Yes |
| T09 | Quiet-DB: M1/M2 counts unchanged | Critical | Yes |
| T10 | No `session.query()`, no `float()` | High | Yes |
| T11 | `unresolvable_rate ≤ 30%` on price_grid | Medium | PARTIAL |

**Gate G3 PASS requires:** All Critical items pass + at least 9/11 total.
T11 may be PARTIAL (proxy mode) without blocking gate closure.

---

## Reporting

Use the `QA_FINDINGS_REPORT.md` template from `_COMMUNICATION/TEMPLATES/`.
Submit to: `_COMMUNICATION/TEAM_50/reports/` with naming:
`YYYY-MM-DD_QA_G3_v2_TEAM50.md`

Include:
- Environment details (Python version, Docker container, DATABASE_URL port, Alembic revision)
- `<RUN_ID>` used for cohort-scoped tests
- Results table for all 11 tests
- Gate G3 decision (PASS / FAIL / CONDITIONAL)
- Any T11-PARTIAL notes

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*This mandate supersedes `QA_MANDATE_G3.md` and `QA_MANDATE_G3_RERUN.md`.*
