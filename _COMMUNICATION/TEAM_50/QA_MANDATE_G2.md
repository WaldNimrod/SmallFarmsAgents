# QA Mandate — Gate G2 (M2 Collection Layer)
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**Date:** 2026-03-30  
**Gate:** G2  
**Prerequisites:**
- Gate G1 formally open (Team 50 sign-off filed)
- Team 10 completion report filed in `_COMMUNICATION/TEAM_10/reports/`

---

## Context

Team 10 has completed M2 (Collection Layer). This mandate defines exactly what
Team 50 must test and verify before Gate G2 can open.

Read before starting:
- `_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md` — implementation spec
- `docs/PIPELINE_ALGORITHMS_HE.md` — pipeline algorithm spec (+ GLOSSARY for terms)
- `docs/SOURCE_MAP_MASTER_HE.md` — source catalog

---

## Environment Reminder

Before running any test:
```bash
python --version          # must be 3.11+
docker ps | grep postgres # must show OMA postgres container running
echo $DATABASE_URL        # must point to Docker port (55435 or 5433)
```

> PostgreSQL via Docker only. Homebrew PostgreSQL removed 2026-03-30.
> See `docker-compose.yml` and `.env.example` at repo root.

---

## T01 — Unit Tests

```bash
python -m pytest tests/test_collectors.py tests/test_parsers.py -v
```

**Pass criterion:** All tests PASS. No skips. No live HTTP calls
(inspect test source to confirm all httpx calls are mocked).

---

## T02 — Live Ingestion Run

```bash
python -m organic_market_agent.scheduler.run_ingestion --run-type manual
```

Run against at least 3 active sources with status `active` in the `sources` table.
Capture the full CLI output.

**Pass criterion:**
- Exit code 0
- Output shows `status=completed` or `status=partial` (not `failed`)
- `sources_succeeded` ≥ 3

**DB verification:**
```sql
SELECT id, run_type, status, sources_total, sources_succeeded, sources_failed,
       community_sources_succeeded, finished_at
FROM ingestion_runs
ORDER BY id DESC LIMIT 5;
```

---

## T03 — raw_assets Written Correctly

```sql
SELECT
    s.code AS source_code,
    ra.file_type,
    ra.bytes_size,
    LENGTH(ra.checksum_sha256) AS checksum_len,
    ra.storage_path,
    ra.captured_at
FROM raw_assets ra
JOIN sources s ON s.id = ra.source_id
ORDER BY ra.id DESC
LIMIT 20;
```

**Pass criterion:**
- ≥3 rows (one per collected source)
- `checksum_sha256` length = 64 for all rows
- `bytes_size > 0` for all rows
- `file_type` is one of: `html`, `json`, `pdf`, `rss`, `text`, `other`

**File system verification:**
```bash
ls -lh $RAW_FILES_ROOT/   # verify subdirectory structure exists
# expect: RAW_FILES_ROOT/{source_code}/{YYYY-MM-DD}/source_code_HHMMSS.{ext}
```

---

## T04 — raw_extracted_items Volume

```sql
SELECT COUNT(*) AS total_items,
       COUNT(DISTINCT source_fetch_run_id) AS fetch_runs_covered,
       COUNT(CASE WHEN raw_product_name IS NOT NULL THEN 1 END) AS named_items
FROM raw_extracted_items;
```

**Pass criterion:**
- `total_items` ≥ 50
- `fetch_runs_covered` ≥ 3
- `named_items` / `total_items` ≥ 0.7 (at least 70% have a product name)

---

## T05 — source_fetch_runs Status Breakdown

```sql
SELECT status, COUNT(*) AS cnt
FROM source_fetch_runs
GROUP BY status;
```

**Pass criterion:**
- `success` count ≥ 3
- No `running` status rows (all runs have terminated)

---

## T06 — Deduplication Test

Run ingestion a second time immediately after T02:

```bash
python -m organic_market_agent.scheduler.run_ingestion --run-type manual
```

Then:
```sql
-- Count new raw_assets created in the second run
SELECT COUNT(*) AS new_assets
FROM raw_assets ra
JOIN source_fetch_runs sfr ON sfr.id = ra.source_fetch_run_id
JOIN ingestion_runs ir ON ir.id = sfr.ingestion_run_id
WHERE ir.id = (SELECT MAX(id) FROM ingestion_runs);
```

```sql
-- Verify second run's fetch_runs show 'skipped'
SELECT sfr.status, COUNT(*) AS cnt
FROM source_fetch_runs sfr
JOIN ingestion_runs ir ON ir.id = sfr.ingestion_run_id
WHERE ir.id = (SELECT MAX(id) FROM ingestion_runs)
GROUP BY sfr.status;
```

**Pass criterion (amended 2026-03-30 per Team 100 decision):**

Dedup is proven when **both** of the following hold:

1. At least one source in the second run produced `status='skipped'` — confirming the dedup path executes
2. No duplicate rows exist in `raw_assets` for the same `(source_id, checksum_sha256)`:

```sql
SELECT source_id, checksum_sha256, COUNT(*) AS cnt
FROM raw_assets
GROUP BY source_id, checksum_sha256
HAVING COUNT(*) > 1;
```
→ must return **0 rows**

**Why amended:** Live HTTP sources may return changed payloads between runs (new checksum → new asset, correctly marked `success`). The strict "all `skipped`" criterion is only valid for frozen/mocked endpoints. The meaningful test is that unchanged payloads are deduplicated (not re-fetched) and no duplicate `raw_assets` rows are created.

---

## T07 — Error Handling and Retry

Pick one active source. Temporarily update its `entry_url` to an invalid URL:

```sql
-- Note the original URL first
SELECT id, entry_url FROM source_fetch_profiles WHERE source_id = (
    SELECT id FROM sources WHERE code = 'SRC002' LIMIT 1
);

-- Set to bad URL
UPDATE source_fetch_profiles SET entry_url = 'http://127.0.0.1:1/nonexistent'
WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC002' LIMIT 1);
```

Run ingestion for just that source:
```bash
python -m organic_market_agent.scheduler.run_ingestion --source-code SRC002
```

Then verify:
```sql
-- fetch run should show failed with retry evidence
SELECT status, retry_count, error_message
FROM source_fetch_runs
WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC002')
ORDER BY id DESC LIMIT 1;
```

```sql
-- log_entries should have an ERROR row for this failure
SELECT level, module, message, created_at
FROM log_entries
WHERE level = 'ERROR'
ORDER BY id DESC LIMIT 5;
```

**Pass criterion:**
- `source_fetch_runs.status = 'failed'`
- `retry_count ≥ 1` (at least one retry attempted)
- `error_message` is not NULL
- At least one `log_entries` row with `level = 'ERROR'`

**Restore the URL afterward:**
```sql
UPDATE source_fetch_profiles SET entry_url = '<original_url>'
WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC002' LIMIT 1);
```

---

## T08 — Isolation: Normalizer Not Run

```sql
SELECT COUNT(*) AS obs_count FROM normalized_observations;
```

**Pass criterion:** `obs_count = 0`.

M2 must not populate `normalized_observations`. The normalizer runs in M3.

---

## T09 — Regression: M1 Tables Unchanged

```sql
SELECT 'measurement_units' AS tbl, COUNT(*) FROM measurement_units
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sources', COUNT(*) FROM sources
UNION ALL SELECT 'product_aliases', COUNT(*) FROM product_aliases
UNION ALL SELECT 'unit_conversions', COUNT(*) FROM unit_conversions;
```

**Pass criterion:** Row counts match exactly what was confirmed at Gate G1:
- `measurement_units` = 11
- `products` = 29
- `sources` = as confirmed in G1
- `product_aliases` = as confirmed in G1
- `unit_conversions` = as confirmed in G1

> If any count changed, this is a FAIL. M2 must not modify M1 seed data.

---

## T10 — Code Review: No Hardcoded URLs or Product Names

```bash
# No product name strings in collector/parser code
grep -rn "\"עגבניה\"\|\"מלפפון\"\|\"גזר\"\|\"בצל\"\|\"תפוח אדמה\"" \
    organic_market_agent/collectors/ organic_market_agent/parsers/
```

```bash
# No hardcoded URLs in collector logic (URLs must come from DB only)
grep -rn "https\?://" \
    organic_market_agent/collectors/ organic_market_agent/parsers/ \
    --include="*.py" | grep -v "test_\|#\|docstring\|example"
```

**Pass criterion:**
- No Hebrew product name strings in collector/parser source files
- No hardcoded `http://` or `https://` URLs in collector/parser logic (only in tests or comments)

---

## T11 — Code Review: No Live HTTP in Tests

```bash
grep -rn "httpx.get\|httpx.Client\|requests.get" tests/test_collectors.py tests/test_parsers.py
```

**Pass criterion:** Zero occurrences of real HTTP calls. All must be mocked
(`unittest.mock.patch`, `MagicMock`, `pytest-httpx`).

---

## T12 — SQLAlchemy 2.x Style Check

```bash
grep -rn "session\.query\(" organic_market_agent/collectors/ organic_market_agent/parsers/ \
    organic_market_agent/scheduler/
```

**Pass criterion:** Zero occurrences. All DB access must use `session.execute(select(...))`.

---

## Scoring

| # | Test | Weight |
|---|------|--------|
| T01 | Unit tests all PASS | Critical |
| T02 | Live ingestion run completes | Critical |
| T03 | raw_assets written correctly | Critical |
| T04 | raw_extracted_items ≥ 50 rows | Critical |
| T05 | source_fetch_runs status breakdown | High |
| T06 | Dedup verified | Critical |
| T07 | Error handling + retry + log_entries | Critical |
| T08 | normalized_observations still empty | Critical |
| T09 | M1 tables unchanged | Critical |
| T10 | No hardcoded URLs / product names | High |
| T11 | No live HTTP in tests | High |
| T12 | SQLAlchemy 2.x style | High |

**Gate G2 opens only if all Critical tests PASS.**
High-weight failures result in CONDITIONAL PASS with listed conditions.

---

## Submission

File your report at:
`_COMMUNICATION/TEAM_50/reports/{date}_QA_G2_TEAM50.md`

Include:
- Full `pytest -v` output
- Full CLI run output
- All SQL query outputs
- Result of code review grep commands
