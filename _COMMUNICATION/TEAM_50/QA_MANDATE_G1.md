# QA Mandate — Gate G1 (M1 Local Foundation)
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**Date:** 2026-03-30  
**Gate:** G1  
**Prerequisites:** Team 20 completion report filed in `_COMMUNICATION/TEAM_20/reports/`

---

## Context

Team 20 has completed M1 (Local Foundation). This mandate defines exactly what
Team 50 must test and verify before Gate G1 can open.

Read before starting:
- `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md` — the implementation spec
- `docs/DATABASE_SCHEMA_SPEC_HE.md` — full schema definition
- `docs/PRODUCT_CATALOG_V1.md` — 29 canonical products

---

## Environment Requirements

Before running any test, confirm:

```bash
python --version          # must be 3.11.x or higher
docker ps | grep postgres # must show OMA postgres container running
echo $DATABASE_URL        # must point to Docker port (e.g. 55435 or 5433)
```

**Stack note (2026-03-30):** Homebrew PostgreSQL has been removed.
PostgreSQL is served exclusively via Docker.
- Current dev DB: `oma-g2-ev` on port 55435 (`postgresql://oma:t@localhost:55435/organic`)
- Fresh installs: `docker-compose up -d` → port 5433 (`postgresql://oma:oma@localhost:5433/organic_market_agent`)

If Python < 3.11 or no postgres Docker container is running: **FAIL immediately, block gate.**

---

## T01 — Unit Tests

```bash
cd /path/to/SmallFarmsAgents
python -m pytest tests/test_db_health.py -v
```

**Pass criterion:** All 7 tests PASS. No skips. No errors.

Expected output:
```
tests/test_db_health.py::test_all_required_tables_exist        PASSED
tests/test_db_health.py::test_seed_data_counts                 PASSED
tests/test_db_health.py::test_products_have_aliases            PASSED
tests/test_db_health.py::test_all_products_have_valid_unit     PASSED
tests/test_db_health.py::test_no_float_price_columns           PASSED
tests/test_db_health.py::test_all_timestamp_columns_are_timestamptz PASSED
tests/test_db_health.py::test_check_cli_passes                 PASSED
7 passed
```

---

## T02 — CLI Health Check

```bash
python -m organic_market_agent.db.check
```

**Pass criterion:** Output ends with `RESULT: PASS`. All 23 table lines show `OK`.

---

## T03 — Migration Round-Trip

```bash
# Run on the existing database (alembic already at head)
alembic downgrade base
alembic upgrade head
python -m organic_market_agent.db.check
```

**Pass criterion:**
- `downgrade base` completes without error
- `upgrade head` completes without error
- `db.check` shows PASS after re-upgrade

---

## T04 — Schema Completeness

Connect to the DB and run:

```sql
-- Check all 23 tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

**Pass criterion:** Must include all 23 tables:
`audit_log`, `daily_aggregates`, `ingestion_runs`, `log_entries`,
`measurement_units`, `normalizer_profiles`, `normalizer_rules`,
`normalized_observations`, `observation_flags`, `product_aliases`,
`product_merges`, `product_variants`, `products`, `publish_artifacts`,
`publish_runs`, `raw_assets`, `raw_extracted_items`, `source_fetch_profiles`,
`source_fetch_runs`, `sources`, `unit_conversions`, `users`, `weekly_snapshots`

```sql
-- Check both views exist
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public';
```

**Pass criterion:** `public_market_view` and `admin_observations_view` present.

---

## T05 — Index Completeness

```sql
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

**Pass criterion:** Verify the following indexes are present (spot check):

| Table | Index |
|-------|-------|
| `normalized_observations` | `idx_obs_agg` (composite: product_id, market_scope, is_benchmark, flag_status, observed_at) |
| `products` | `idx_products_code` (unique) |
| `sources` | `uq_sources_code` (unique) |
| `raw_assets` | `idx_raw_assets_checksum` |
| `product_aliases` | `uq_alias_text_source` (unique) |
| `daily_aggregates` | `uq_daily_aggregate` (unique composite) |

---

## T06 — Seed Data Counts

```sql
SELECT 'measurement_units' AS tbl, COUNT(*) FROM measurement_units
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sources', COUNT(*) FROM sources
UNION ALL SELECT 'product_aliases', COUNT(*) FROM product_aliases
UNION ALL SELECT 'unit_conversions', COUNT(*) FROM unit_conversions;
```

**Pass criterion:**

| Table | Expected |
|-------|---------|
| `measurement_units` | = 11 |
| `products` | = 29 |
| `sources` | ≥ 20 |
| `product_aliases` | ≥ 10 |
| `unit_conversions` | ≥ 4 |

---

## T07 — Type Safety: No FLOAT

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND data_type IN ('real', 'double precision', 'float4', 'float8');
```

**Pass criterion:** Query returns **zero rows**.

---

## T08 — Type Safety: All Timestamps Are TIMESTAMPTZ

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name LIKE '%_at'
  AND data_type NOT LIKE '%with time zone%';
```

**Pass criterion:** Query returns **zero rows**.

---

## T09 — Price Columns Are NUMERIC(12,4)

```sql
SELECT table_name, column_name, data_type, numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name LIKE '%price%'
ORDER BY table_name;
```

**Pass criterion:** All price columns have `data_type = 'numeric'`,
`numeric_precision = 12`, `numeric_scale = 4`.

---

## T10 — Every Product Has at Least One Alias

```sql
SELECT p.code, p.canonical_name_he
FROM products p
LEFT JOIN product_aliases pa ON pa.product_id = p.id AND pa.is_active = true
WHERE pa.id IS NULL
  AND p.is_active = true;
```

**Pass criterion:** Query returns **zero rows**.

---

## T11 — Every Product Has a Valid Default Unit

```sql
SELECT p.code
FROM products p
LEFT JOIN measurement_units mu ON mu.id = p.default_measurement_unit_id
WHERE mu.id IS NULL;
```

**Pass criterion:** Query returns **zero rows**.

---

## T12 — CHECK Constraints Active

```sql
-- Attempt to insert a bad value — must fail
INSERT INTO sources (code, name, source_group, market_scope, sales_channel, is_active)
VALUES ('XTEST', 'Test', 'INVALID_GROUP', 'community', 'community_direct', true);
```

**Pass criterion:** INSERT fails with a constraint violation error.
(Immediately roll back / do not commit.)

---

## T13 — Import Sanity

```bash
python -c "from organic_market_agent.models import *; print('OK')"
```

**Pass criterion:** Prints `OK` with no errors or warnings.

---

## Scoring

| # | Test | Weight |
|---|------|--------|
| T01 | Unit tests (7/7) | Critical |
| T02 | CLI PASS | Critical |
| T03 | Migration round-trip | Critical |
| T04 | 23 tables + 2 views | Critical |
| T05 | Index completeness | High |
| T06 | Seed data counts | Critical |
| T07 | No FLOAT | Critical |
| T08 | All TIMESTAMPTZ | Critical |
| T09 | Price NUMERIC(12,4) | Critical |
| T10 | Every product has alias | High |
| T11 | Every product has valid unit | High |
| T12 | CHECK constraint active | High |
| T13 | Import sanity | Critical |

**Gate G1 opens only if all Critical tests PASS.**
High-weight findings that fail result in CONDITIONAL PASS with listed conditions.

---

## Submission

File your report at:
`_COMMUNICATION/TEAM_50/reports/{date}_QA_G1_TEAM50.md`

Use the QA Report Template from `_COMMUNICATION/TEAM_50/ONBOARDING.md`.
Include paste of every SQL query output and CLI output.
