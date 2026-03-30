---
document_type: QA_MANDATE
version: "1.0"
template: _COMMUNICATION/TEMPLATES/MANDATE.md
---

# QA Mandate — Gate G4: Aggregation + Local Viewer + Admin Dashboard
**Mandate ID:** QA-MANDATE-20260330-G4
**From:** Team 100 (Architecture)
**To:** Team 50 (QA)
**Date:** 2026-03-30
**Priority:** HIGH
**Gate dependency:** Blocks Gate G4 sign-off
**Status:** ACTIVE

---

## 1. Context

M4 Phase A implementation is being built by Team 10 per
`MANDATE_M4_AGGREGATION_LOCAL_VIEWER_TEAM10.md`. When Team 10 files their
completion report and a G4 Review Request, Team 50 must execute this mandate to
validate the gate.

G4 validates four new components: `AggregatorEngine`, `QAEngine`, `PublishEngine`,
and the Admin Monitoring Dashboard.

**Prerequisite checks before starting QA:**
1. `alembic current` → `014 (head)` (migration 014 applied)
2. `pytest tests/ -q` → all pass (Team 10 completion baseline)
3. Latest ingestion run has ≥3 community sources and ≥15 products in
   `normalized_observations`
4. `public_report.json` exists in `output/public/` from Team 10's test run

---

## 2. Test Plan

### T01 — Unit tests (automated)

```bash
.venv/bin/python -m pytest tests/test_aggregator.py tests/test_publisher_local.py -v
```

**Pass criterion:** All tests pass. Minimum: 8 in `test_aggregator.py`, 6 in
`test_publisher_local.py`. Zero failures.

---

### T02 — End-to-end pipeline run

Run the full pipeline from scratch:

```bash
.venv/bin/python -m organic_market_agent run_ingestion --normalize
.venv/bin/python -m organic_market_agent run_normalizer --metrics
# Note the ingestion run ID from the output
.venv/bin/python -m organic_market_agent run_aggregator   # (if CLI exists)
.venv/bin/python -m organic_market_agent run_publisher
```

Or via a combined script if Team 10 provides one.

**Pass criterion:**
- `SELECT COUNT(*) FROM daily_aggregates` → > 0
- `SELECT COUNT(*) FROM weekly_snapshots` → > 0
- `output/public/public_report.json` exists and is valid JSON
- `output/public/manifest.json` exists and is valid JSON
- `output/public/public_report.html` exists and is readable HTML

---

### T03 — Publish threshold enforcement

```sql
-- Verify products below threshold are absent from public_report.json
SELECT p.code, da.distinct_sources, da.meets_publish_threshold
FROM daily_aggregates da
JOIN products p ON da.product_id = p.id
WHERE da.aggregate_date = CURRENT_DATE
ORDER BY da.meets_publish_threshold, p.code;
```

Cross-reference: every product with `meets_publish_threshold = false` in the DB
must be absent from `public_report.json`.

**Pass criterion:** No product with `meets_publish_threshold = false` appears in
`public_report.json`. At least 5 products with `meets_publish_threshold = true`.

---

### T04 — JSON schema validation

`public_report.json` must contain all required fields:

```python
import json, pathlib
report = json.loads(pathlib.Path("output/public/public_report.json").read_text())
assert "generated_at" in report
assert "report_date" in report
assert isinstance(report["products"], list)
for p in report["products"]:
    for field in ("product_id","canonical_name_he","market_scope",
                  "meets_publish_threshold","sample_size","distinct_sources",
                  "min_price","max_price","avg_price","median_price",
                  "normalized_unit","last_observed_at"):
        assert field in p, f"Missing field: {field}"
```

**Pass criterion:** Script runs without AssertionError.

---

### T05 — Data quality: aggregation consistency

```sql
-- min ≤ median ≤ max for all aggregates
SELECT COUNT(*) AS violations
FROM daily_aggregates
WHERE min_price > median_price
   OR median_price > max_price;
-- Must return 0

-- sample_size matches distinct observations
SELECT da.id, da.sample_size,
       COUNT(no.id) AS actual_count
FROM daily_aggregates da
JOIN normalized_observations no
     ON no.product_id = da.product_id
    AND no.source_fetch_run_id IN (
        SELECT id FROM source_fetch_runs
        WHERE started_at::date = da.aggregate_date
    )
GROUP BY da.id, da.sample_size
HAVING da.sample_size != COUNT(no.id);
-- Must return 0 rows
```

**Pass criterion:** Both queries return 0 rows/violations.

---

### T06 — Staleness calculation

Manually set `manifest.json`'s `last_published_at` to different dates and verify:

| last_published_at | Expected staleness_level |
|-------------------|--------------------------|
| Today             | `current`                |
| Today - 4 days    | `warning`                |
| Today - 9 days    | `irrelevant`             |

This can be tested via the unit tests in `test_publisher_local.py` (T01 covers it)
or by directly checking `manifest.json` staleness after adjusting the date.

**Pass criterion:** Three staleness levels correctly computed per the thresholds.

---

### T07 — Local viewer

```bash
.venv/bin/python -m organic_market_agent run_viewer --port 8082 &
sleep 2
curl -s http://localhost:8082/manifest.json | python3 -m json.tool
curl -s http://localhost:8082/public_report.json | python3 -m json.tool
```

**Pass criterion:** Both `curl` commands return valid JSON with the expected fields.
Kill the viewer process after the test.

---

### T08 — Admin monitoring dashboard

```bash
.venv/bin/python -m organic_market_agent run_admin --port 8083 &
sleep 2
# Test each route returns HTTP 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/          # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/sources   # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/sources/SRC002  # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/products  # 200
curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/unresolved # 200
```

Additional manual checks:
- `/sources` table shows correct `resolution_%` for SRC002, SRC004, SRC005
- `/unresolved` shows top unresolved product names with their occurrence counts
- `/sources/SRC002` shows breakdown of unresolved items for SRC002

**Pass criterion:** All 5 routes return HTTP 200. Manual checks confirm data is
displayed correctly.

---

### T09 — Regression: M1–M3 tables unmodified

```sql
SELECT COUNT(*) FROM sources;            -- must equal pre-M4 count (20)
SELECT COUNT(*) FROM products;           -- must equal pre-M4 count (29)
SELECT COUNT(*) FROM product_aliases WHERE is_active = true;
SELECT COUNT(*) FROM normalized_observations;  -- must be ≥ pre-M4 count
SELECT COUNT(*) FROM raw_extracted_items;      -- must equal pre-M4 count
```

Record baseline before running M4. Compare after M4 run.

**Pass criterion:** `sources`, `products`, `product_aliases`, `raw_extracted_items`
counts unchanged. `normalized_observations` count equal or greater (M4 run may
add new observations).

---

## 3. Gate G4 — PASS criteria (all must be met)

- [ ] T01: `pytest tests/test_aggregator.py tests/test_publisher_local.py` — all PASS (≥14 tests)
- [ ] T02: Full pipeline run completes; `daily_aggregates` and `weekly_snapshots` populated
- [ ] T03: `meets_publish_threshold=true` for ≥5 products; no below-threshold product in JSON
- [ ] T04: `public_report.json` schema validates without error
- [ ] T05: Aggregation consistency — 0 violations
- [ ] T06: Staleness levels correct
- [ ] T07: Local viewer serves JSON files correctly
- [ ] T08: All 5 admin dashboard routes return HTTP 200; data is correct
- [ ] T09: M1–M3 tables unmodified (regression)
- [ ] All existing 48+ tests still pass

---

## 4. FAIL criteria (any one of these → Gate FAIL)

- Any test in T01 fails
- `daily_aggregates` empty after T02
- Products below publish threshold appear in `public_report.json` (T03)
- `public_report.json` fails schema validation (T04)
- Aggregation consistency violations > 0 (T05)
- Any admin dashboard route returns non-200 (T08)
- Regression detected in M1–M3 tables (T09)

---

## 5. Completion Report

File at: `_COMMUNICATION/TEAM_50/reports/<DATE>_QA_G4_TEAM50.md`

Include Mandate ID `QA-MANDATE-20260330-G4`, test results for T01–T09, pass/fail
decision, and sign-off.

If PASS: forward to Team 100 for architectural sign-off.
If FAIL: return to Team 10 with specific failing tests and evidence.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*Authorized by: Team 100 (Architecture)*
