---
document_type: COMPLETION_REPORT
version: "1.0"
---

# M6 Automation + Resilience — implementation complete (Team 10)

**Report ID:** REPORT-20260331-M6-AUTOMATION  
**Mandate ID:** `MANDATE-M6-AUTOMATION-TEAM10`  
**From:** Team 10 (Feature Dev)  
**To:** Team 50 (QA), Team 20 (Operations), Team 100 (Architecture)  
**Date:** 2026-03-31  
**Mandate status:** COMPLETE  
**Gate readiness:** Ready for **G6** QA (`QA_MANDATE_G6.md`)

**Reference:** Team 20 schema handoff — `_COMMUNICATION/TEAM_20/reports/2026-03-31_M6_SCHEMA_COMPLETE_TEAM20.md` (migration **016**).

---

## 1. Summary

M6 adds a self-gating cron entrypoint (`python -m organic_market_agent.scheduler.runner`), extends `run_pipeline()` with optional `source_code`, `skip_normalize`, `skip_publish`, and per-source `retry_attempts`, in-app `pipeline_alerts` after scheduled runs, admin **Scheduler** and **Alerts** blueprints, richer **Runs** UI (trigger options, polling, alerts on detail), Chart.js on the dashboard plus unread alert badge/panel, Hebrew RTL `scheduler.html`, and `docs/OPERATIONS.md` cron instructions for Team 20.

---

## 2. Tasks Completed

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | `scheduler/runner.py` — cron entry, alerts after run | ✅ DONE | `scheduled_time_matches` ±1 min UTC; overlap guard |
| 2 | `pipeline.py` + ingestion retries | ✅ DONE | `execute_ingestion_for_run(..., retry_attempts=)`; empty filter → `PipelineAlert` + `failed` |
| 3 | `/runs` trigger, list, detail, polling | ✅ DONE | `LIMIT 50`, `alert_count`, `duration_secs`, meta refresh if any `running` |
| 4 | Blueprint `/scheduler` | ✅ DONE | update / toggle / run-cleanup + `audit_write` |
| 5 | Blueprint `/alerts` | ✅ DONE | mark read / read-all |
| 6 | Dashboard Chart.js | ✅ DONE | resolution rate + source success/fail (14-day SQL per mandate) |
| 7 | Alert badge + dashboard panel | ✅ DONE | `g.unread_alert_count` in `before_request` |
| 8 | `scheduler.html` RTL | ✅ DONE | Nav **תזמון** in `base.html` |
| 9 | `docs/OPERATIONS.md` | ✅ DONE | Cron line + `crontab -l` verification |
| — | Tests | ✅ DONE | `tests/test_runner.py`, `tests/test_scheduler_routes.py`, `test_t09b` in `test_admin_routes.py` |

---

## 3. Evidence

### 3.1 Test suite (`pytest tests/ -q`)

```
...................s.................................................... [ 83%]
..............                                                           [100%]
85 passed, 1 skipped in 3.84s
```

**Note:** One skip is **pre-existing** in the suite (not introduced by M6). Zero failures.

Focused M6-related tests:

```bash
python3 -m pytest tests/test_runner.py tests/test_scheduler_routes.py -q
```

### 3.2 DB health check (`python -m organic_market_agent.db.check`)

```
OrganicMarketAgent — DB Health Check
==================================================
  OK  measurement_units
  OK  unit_conversions
  OK  products
  OK  product_aliases
  OK  product_variants
  OK  product_merges
  OK  sources
  OK  source_fetch_profiles
  OK  normalizer_profiles
  OK  normalizer_rules
  OK  ingestion_runs
  OK  source_fetch_runs
  OK  raw_assets
  OK  raw_extracted_items
  OK  normalized_observations
  OK  observation_flags
  OK  daily_aggregates
  OK  weekly_snapshots
  OK  publish_runs
  OK  publish_artifacts
  OK  users
  OK  audit_log
  OK  log_entries
  OK  scheduler_config
  OK  pipeline_alerts
  OK  measurement_units: 11 rows (expected >= 11)
  OK  products: 29 rows (expected >= 29)
  OK  sources: 20 rows (expected >= 20)
  OK  users (active admin): 1 rows (expected >= 1)
  OK  scheduler_config: 1 rows (expected exactly 1)
  OK  audit_log index on (entity_type, entity_id)
  OK  audit_log index on (created_at)
  OK  observation_flags index on (product_id)
==================================================
RESULT: PASS
```

### 3.3 `/scheduler` page (200 + form)

**Automated:** `tests/test_scheduler_routes.py::test_t1_get_scheduler_returns_200` — logged-in GET `/scheduler` returns **200** and response body contains `name="run_hour"` (schedule form present).

**Manual / curl:** Route is `@login_required`. After login, e.g.:

```bash
# Start admin (example): python3 -m organic_market_agent run_admin
# Then in browser: http://127.0.0.1:5000/scheduler
```

Unauthenticated GET returns redirect to login (expected).

### 3.4 Dashboard charts (`canvas` elements)

Templates include `<canvas id="chartResolution">` and `<canvas id="chartSources">` with Chart.js loaded from CDN in `base.html`; initialization is in `dashboard.html` `{% block scripts %}`.

**Automated:** `GET /` returns 200 (`tests/test_admin_routes.py::test_t01_readonly_get_routes_return_200`).

### 3.5 `crontab -l` (runner line)

Per mandate, **Team 20** installs the cron line on the host after `runner.py` is delivered. Evidence may appear in a separate Team 20 operations note. Install instructions: `docs/OPERATIONS.md`.

### 3.6 `run_pipeline()` keyword parameters

Signature in `organic_market_agent/scheduler/pipeline.py`:

```python
def run_pipeline(
    ingestion_run_id: int,
    *,
    source_code: str | None = None,
    skip_normalize: bool = False,
    skip_publish: bool = False,
    retry_attempts: int = 2,
) -> None:
```

Confirmed in use by `admin/routes/runs.py` (`functools.partial`) and `scheduler/runner.py` (`retry_attempts` from `scheduler_config`).

---

## 4. Deviations from Mandate

None.

---

## 5. Known Issues / Follow-ups

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| One pytest skip remains in full suite (historical) | LOW | Team 50: confirm waiver or un-skip in scope of G6 / global test hygiene |
| POST forms without Flask-WTF CSRF (M5 note) | MEDIUM | Team 100 if production hardening required |

---

## 6. Next Action Required

- [ ] **Team 50:** Execute `QA_MANDATE_G6.md` and file dated `_COMMUNICATION/TEAM_50/reports/<DATE>_QA_G6_TEAM50.md`.
- [ ] **Team 20:** Install cron per `docs/OPERATIONS.md` on the host and optionally attach `crontab -l` evidence to operations notes.

---

*Filed by: Team 10 (Feature Dev)*  
*Date: 2026-03-31*
