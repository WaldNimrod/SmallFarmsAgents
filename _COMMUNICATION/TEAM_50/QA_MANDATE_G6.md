---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G6

**Mandate ID:** `QA-MANDATE-G6`  
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**CC:** Team 10 (Feature Dev), Team 20 (Infrastructure)  
**Date:** 2026-03-31  
**Milestone:** M6 — Automation + Resilience  
**Gate:** G6  

---

## Pre-conditions (verify before starting)

```bash
# 1. Alembic at 016
alembic current
# Expected: 016 (head)

# 2. scheduler_config seed row
psql $DATABASE_URL -tAc "SELECT is_enabled, run_hour, run_minute, retry_attempts FROM scheduler_config;"
# Expected: 1 row with defaults (t | 6 | 0 | 2)

# 3. pipeline_alerts table exists
psql $DATABASE_URL -tAc "SELECT to_regclass('public.pipeline_alerts');"
# Expected: pipeline_alerts

# 4. Admin server running on port 5001
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/
# Expected: 200 (dashboard is read-only; @login_required only on write routes)

# 5. Login — save cookie for subsequent tests
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/auth/login \
  -d "email=admin@local&password=admin" -o /dev/null -w "%{http_code}"
# Expected: 302

curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  http://127.0.0.1:5001/ -o /tmp/g6_dash.html -w "%{http_code}"
# Expected: 200
```

---

## Test Suite

### T01 — Full pytest suite

```bash
pytest tests/ -q
```

**Pass criterion:** 0 failures. Document any skips with rationale.  
**Weight:** Critical

---

### T02 — Scheduler page accessible and functional

```bash
# T02a: page renders
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  http://127.0.0.1:5001/scheduler -o /tmp/g6_sched.html -w "%{http_code}"
# Expected: 200

# T02b: form fields present
grep -c "run_hour\|run_minute\|retry_attempts\|cleanup_after_days" /tmp/g6_sched.html
# Expected: ≥4

# T02c: toggle is_enabled
BEFORE=$(psql $DATABASE_URL -tAc "SELECT is_enabled FROM scheduler_config WHERE id=1;")
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/scheduler/toggle -o /dev/null -w "%{http_code}"
# Expected: 302
AFTER=$(psql $DATABASE_URL -tAc "SELECT is_enabled FROM scheduler_config WHERE id=1;")
echo "BEFORE=$BEFORE AFTER=$AFTER"
# Expected: AFTER != BEFORE (toggled)

# Restore: toggle back
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/scheduler/toggle -o /dev/null
```

**Pass criterion:** 200, ≥4 form fields, is_enabled toggled.  
**Weight:** High

---

### T03 — Schedule update persists to DB

```bash
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/scheduler/update \
  -d "is_enabled=true&run_hour=7&run_minute=30&retry_attempts=3&cleanup_enabled=on&cleanup_after_days=60" \
  -o /dev/null -w "%{http_code}"
# Expected: 302 (redirect after save)
# Note: cleanup_enabled is a checkbox — use 'on' (not 'true') in POST body

psql $DATABASE_URL -tAc "SELECT run_hour, run_minute, retry_attempts, cleanup_after_days FROM scheduler_config WHERE id=1;"
# Expected: 7 | 30 | 3 | 60
```

Then restore defaults:
```bash
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/scheduler/update \
  -d "is_enabled=true&run_hour=6&run_minute=0&retry_attempts=2&cleanup_enabled=true&cleanup_after_days=90" \
  -o /dev/null
```

**Pass criterion:** DB row reflects updated values.  
**Weight:** High

---

### T04 — Focused run trigger (source_code parameter)

```bash
# Get count before
BEFORE=$(psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM ingestion_runs;")

# Trigger focused run for first active source
SOURCE=$(psql $DATABASE_URL -tAc "SELECT code FROM sources WHERE is_active=true ORDER BY id LIMIT 1;")
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/runs/trigger \
  -d "source_code=$SOURCE" -o /dev/null -w "%{http_code}"
# Expected: 302

sleep 3

AFTER=$(psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM ingestion_runs;")
echo "BEFORE=$BEFORE AFTER=$AFTER"
# Expected: AFTER = BEFORE + 1

# Verify triggered_by and that only that source was processed
LAST_RUN=$(psql $DATABASE_URL -tAc "SELECT id FROM ingestion_runs ORDER BY id DESC LIMIT 1;")
psql $DATABASE_URL -tAc "
  SELECT s.code FROM source_fetch_runs sfr
  JOIN sources s ON s.id = sfr.source_id
  WHERE sfr.ingestion_run_id = $LAST_RUN;"
# Expected: only $SOURCE appears (or empty if source had no active profile, documented)
```

**Pass criterion:** New ingestion_run created; if per-source breakdown exists, only the targeted source appears.  
**Weight:** High

---

### T05 — Dashboard charts render

```bash
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  http://127.0.0.1:5001/ -o /tmp/g6_dash2.html

grep -c "chartResolution\|chartSources\|chart.js\|Chart(" /tmp/g6_dash2.html
# Expected: ≥4 (canvas IDs + script references)

grep -c "canvas" /tmp/g6_dash2.html
# Expected: ≥2
```

**Pass criterion:** ≥2 canvas elements, chart.js referenced or Chart( constructor present.  
**Weight:** High

---

### T06 — Alert badge visible after run

```bash
# Insert a test unread alert to ensure the dashboard panel renders
TEST_ALERT_ID=$(psql $DATABASE_URL -tAc "
  INSERT INTO pipeline_alerts (level, message, is_read)
  VALUES ('warning', 'G6-QA-test-alert', false)
  RETURNING id;")
echo "TEST_ALERT_ID=$TEST_ALERT_ID"

# Fetch dashboard and verify alert panel renders
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  http://127.0.0.1:5001/ -o /tmp/g6_alerts.html

# Verify unread alert badge / panel substrings are present
grep -c "סמן כנקרא\|alert-warning\|badge" /tmp/g6_alerts.html
# Expected: ≥1 (alert panel rendered with unread row)

# At minimum: pipeline_alerts has ≥1 unread row
psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM pipeline_alerts WHERE is_read = false;"
# Expected: ≥1

# Cleanup: mark test alert read
psql $DATABASE_URL -c "UPDATE pipeline_alerts SET is_read = true WHERE id = $TEST_ALERT_ID;"
```

**Pass criterion:** Test alert inserted; dashboard HTML contains alert panel substrings; pipeline_alerts has ≥1 unread row before mark-read.  
**Weight:** Medium

---

### T07 — Manual log cleanup

```bash
# Insert synthetic old source_fetch_run for testing (if safe to do so)
# Or verify cleanup route functions without error even if no rows qualify
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  -X POST http://127.0.0.1:5001/scheduler/run-cleanup \
  -o /tmp/g6_cleanup.html -w "%{http_code}"
# Expected: 302 (redirect after flash)

# Verify cleanup_last_run was updated
psql $DATABASE_URL -tAc "SELECT cleanup_last_run FROM scheduler_config WHERE id=1;"
# Expected: non-null timestamp (updated to now)

# Verify audit_log entry
psql $DATABASE_URL -tAc "
  SELECT action FROM audit_log ORDER BY created_at DESC LIMIT 1;"
# Expected: includes 'cleanup' or 'run_cleanup'
```

**Pass criterion:** 302 redirect, `cleanup_last_run` updated, audit entry written.  
**Weight:** Medium

---

### T08 — Runs list live polling indicator

```bash
curl -s -c /tmp/g6_cookies.txt -b /tmp/g6_cookies.txt \
  http://127.0.0.1:5001/runs -o /tmp/g6_runs.html

# Check that page shows last 50 (or all current runs up to 50)
# Verify duration field rendered
grep -c "duration\|סטטוס\|הרץ\|מקורות" /tmp/g6_runs.html
# Expected: ≥2 (Hebrew column headers present)
```

**Pass criterion:** Runs page renders 200, Hebrew headers present, duration column exists.  
**Weight:** Medium

---

### T09 — runner.py self-gates correctly (unit evidence)

```bash
pytest tests/test_runner.py -v
```

**Pass criterion:** All tests pass. Document any skips.  
**Weight:** High

---

### T10 — Regression (G5 baselines)

```sql
SELECT
  (SELECT COUNT(*) FROM sources)                          AS sources,
  (SELECT COUNT(*) FROM products)                         AS products,
  (SELECT COUNT(*) FROM product_aliases WHERE is_active)  AS active_aliases,
  (SELECT COUNT(*) FROM normalized_observations)          AS observations,
  (SELECT COUNT(*) FROM daily_aggregates)                 AS daily_aggs;
```

**Expected minimums:**
- `sources` = 20
- `products` = 29
- `active_aliases` ≥ 97
- `observations` ≥ 1
- `daily_aggs` ≥ 25

**Pass criterion:** All at or above G5 baselines.  
**Weight:** Critical

---

## Gate G6 — Pass Criteria Summary

| Test | Pass Criterion | Weight |
|------|---------------|--------|
| T01 | `pytest tests/` — 0 failures | Critical |
| T02 | /scheduler renders, toggle functional | High |
| T03 | Schedule update persists to DB | High |
| T04 | Focused trigger scopes run to source | High |
| T05 | Dashboard has 2 Chart.js canvas elements | High |
| T06 | pipeline_alerts written; dashboard shows panel | Medium |
| T07 | Cleanup trigger executes; cleanup_last_run updated | Medium |
| T08 | Runs list renders with Hebrew headers + duration | Medium |
| T09 | test_runner.py — all pass | High |
| T10 | All G5 regression baselines met | Critical |

**Additional requirement:** Team 100 architectural review sign-off (per Gate Passage Policy §5).

**Gate fails if:** Any Critical test fails, or ≥3 High tests fail.

---

## QA Report

File at: `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_QA_G6_TEAM50.md`  
Use canonical template `_COMMUNICATION/templates/QA_FINDINGS_REPORT.md`.  
Include: per-test result table, DB evidence queries + output, pytest output (last 20 lines), gate decision (PASS / FAIL / CONDITIONAL PASS).

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Mandate ID:** `QA-MANDATE-G6`
