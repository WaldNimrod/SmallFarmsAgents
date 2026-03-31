---
document_type: MANDATE
version: "1.0"
---

# Mandate — M6 Automation + Resilience (Admin UI + Scheduler)

**Mandate ID:** `MANDATE-M6-AUTOMATION-TEAM10`  
**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev)  
**CC:** Team 20 (Infrastructure), Team 50 (QA)  
**Date:** 2026-03-31  
**Milestone:** M6 — Automation + Resilience  
**Dependency:** Migration 016 applied (Team 20 completion report filed)  

---

## Context

M6 moves from a manual-only workflow to an automated scheduled pipeline with full dashboard visibility. There is **no SMTP** in this milestone — all alerts are in-app. The admin dashboard gains scheduling control, Chart.js graphs, and a log cleanup UI.

Chart.js is approved for use via CDN (no pip install). See §5.

---

## Deliverables

### Task 1 — `scheduler/runner.py` (new file)

Entry point: `python -m organic_market_agent.scheduler.runner`

**Behaviour:**
1. Open a DB session. Read the single `scheduler_config` row.
2. If `is_enabled = FALSE`: log "scheduler disabled" and exit immediately.
3. Compare `datetime.now(timezone.utc).hour` and `.minute` against `run_hour` / `run_minute` (±1 minute tolerance on the minute). If not the scheduled time: exit.
4. Check if an `IngestionRun` with `status='running'` already exists (to prevent overlap): if yes, exit.
5. Create an `IngestionRun` (`run_type='daily'`, `triggered_by='cron'`), flush, commit.
6. Call `run_pipeline(ingestion_run_id, retry_attempts=config.retry_attempts)`.
7. After pipeline completes, read the run's final `status`:
   - `status='failed'` → insert `PipelineAlert(level='error', message=..., ingestion_run_id=run_id)`
   - `sources_failed > 0` (partial) → insert `PipelineAlert(level='warning', message=..., ingestion_run_id=run_id)`
   - Clean success → insert `PipelineAlert(level='info', message=..., ingestion_run_id=run_id)` (brief, no noise)
8. Commit the alert. Exit.

**Cron line (Team 20 installs on the host):**
```bash
* * * * * cd /path/to/SmallFarmsAgents && /path/to/.venv/bin/python -m organic_market_agent.scheduler.runner >> logs/runner.log 2>&1
```
Runs every minute; the runner itself gates on the configured hour/minute. Team 20 must create `logs/` directory if absent.

---

### Task 2 — Extend `scheduler/pipeline.py`

Add optional parameters to `run_pipeline()`:

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

**Behaviour changes:**
- If `source_code` is provided: filter `pairs` from `_get_active_sources_with_profiles` to only the matching source. If no match: log warning and write `PipelineAlert(level='error', ...)`, return.
- If `skip_normalize=True`: skip the `NormalizerEngine().run(...)` step.
- If `skip_publish=True`: skip the `PublishEngine().run(...)` step.
- `retry_attempts`: each source in `execute_ingestion_for_run` is retried up to this many times on HTTP failure (`status='failed'`). Implement retry inside `execute_ingestion_for_run` with a short sleep (1s) between attempts.

---

### Task 3 — Extend `admin/routes/runs.py`

**Extend `/runs/trigger` form (POST):**

Accept new optional form fields:
- `source_code` (str, optional) — passed to `run_pipeline(source_code=...)`
- `skip_normalize` (checkbox, `'on'` / absent)
- `skip_publish` (checkbox, `'on'` / absent)

The trigger route passes these to `run_pipeline()` via the daemon thread args.

**Extend `/runs` list:**
- Return last 50 rows (up from 20).
- Add `duration_secs` computed field: `(finished_at - started_at)` in seconds, or `None` if still running.
- Add `alert_count` per run: `SELECT COUNT(*) FROM pipeline_alerts WHERE ingestion_run_id = :rid`.

**Live polling in `runs.html`:**
- If any run in the list has `status='running'`, add `<meta http-equiv="refresh" content="5">` in the `<head>` block so the page auto-refreshes every 5 seconds.

**Extend `run_detail.html`:**
- Show any linked `pipeline_alerts` for this run (level badge + message).
- Show run duration if `finished_at` is set.

---

### Task 4 — New blueprint: `admin/routes/scheduler.py`

```python
bp = Blueprint("scheduler", __name__)
```

Routes:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/scheduler` | `@login_required` | Show scheduler_config form |
| POST | `/scheduler/update` | `@login_required` | Save is_enabled, run_hour, run_minute, retry_attempts, cleanup_enabled, cleanup_after_days |
| POST | `/scheduler/toggle` | `@login_required` | Flip is_enabled boolean; flash result |
| POST | `/scheduler/run-cleanup` | `@login_required` | Execute cleanup SQL; flash row count deleted |

**`/scheduler/update` logic:**
- Read form fields, validate ranges (hour 0–23, minute 0–59, retry 0–10, days ≥7).
- Update the single `scheduler_config` row. Set `updated_at = now()`.
- Write `audit_log` row via `audit_write(session, 'update_scheduler', 'scheduler_config', ...)`.
- Flash "הגדרות תזמון נשמרו." and redirect to GET `/scheduler`.

**`/scheduler/run-cleanup` logic:**
```sql
WITH deleted AS (
    DELETE FROM source_fetch_runs
    WHERE started_at < now() - make_interval(days => :days)
      AND ingestion_run_id IN (
          SELECT id FROM ingestion_runs
          WHERE status IN ('completed', 'partial', 'failed')
      )
    RETURNING id
)
SELECT COUNT(*) FROM deleted;
```
- Update `scheduler_config.cleanup_last_run = now()`.
- Write `audit_log` row via `audit_write`.
- Flash "נוקו {n} רשומות." and redirect.

Register blueprint in `organic_market_agent/admin/__init__.py`.

---

### Task 5 — New blueprint: `admin/routes/alerts.py`

```python
bp = Blueprint("alerts", __name__)
```

Routes:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/alerts/<int:alert_id>/read` | `@login_required` | Set is_read=True, redirect back |
| POST | `/alerts/read-all` | `@login_required` | Mark all is_read=True, redirect to dashboard |

Register blueprint in `__init__.py`.

---

### Task 6 — Dashboard charts (Chart.js CDN)

**`base.html`** — add before `</body>`:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
```

**`admin/routes/dashboard.py`** — enrich with two data series (last 14 days):

```python
# Chart 1 — daily resolution rate
chart_resolution = session.execute(text("""
    SELECT
        ir.finished_at::date AS day,
        COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized') AS resolved,
        COUNT(rei.id) AS total
    FROM ingestion_runs ir
    LEFT JOIN source_fetch_runs sfr ON sfr.ingestion_run_id = ir.id
    LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
    WHERE ir.finished_at >= now() - interval '14 days'
      AND ir.status IN ('completed','partial')
    GROUP BY day
    ORDER BY day
""")).all()

# Chart 2 — source success / fail per run (last 14 runs)
chart_sources = session.execute(text("""
    SELECT id, started_at::date AS day, sources_succeeded, sources_failed, status
    FROM ingestion_runs
    WHERE started_at >= now() - interval '14 days'
    ORDER BY started_at
""")).all()
```

Pass as `chart_resolution_json` and `chart_sources_json` (serialized with `json.dumps`) to the template.

**`dashboard.html`** — add two `<canvas>` sections with inline Chart.js initialization:

```html
<!-- Chart 1: Resolution Rate (line) -->
<canvas id="chartResolution" height="100"></canvas>
<script>
new Chart(document.getElementById('chartResolution'), {
    type: 'line',
    data: {
        labels: {{ chart_resolution_json | safe }}.map(r => r.day),
        datasets: [{
            label: 'שיעור פתרון (%)',
            data: {{ chart_resolution_json | safe }}.map(r =>
                r.total > 0 ? Math.round(r.resolved / r.total * 100) : 0
            ),
            tension: 0.3, fill: true
        }]
    }
});
</script>

<!-- Chart 2: Source Success/Fail (stacked bar) -->
<canvas id="chartSources" height="100"></canvas>
<script>
const sd = {{ chart_sources_json | safe }};
new Chart(document.getElementById('chartSources'), {
    type: 'bar',
    data: {
        labels: sd.map(r => r.day),
        datasets: [
            { label: 'הצליחו', data: sd.map(r => r.sources_succeeded), stack: 'a' },
            { label: 'נכשלו',  data: sd.map(r => r.sources_failed),    stack: 'a' }
        ]
    },
    options: { scales: { x: { stacked: true }, y: { stacked: true } } }
});
</script>
```

---

### Task 7 — Alert badge + panel in dashboard

**`base.html` `before_request` hook (or query in each route via `g`):**

In `admin/__init__.py`, add to `before_request`:
```python
from organic_market_agent.models.scheduler import PipelineAlert
g.unread_alert_count = session.execute(
    text("SELECT COUNT(*) FROM pipeline_alerts WHERE is_read = false")
).scalar_one()
```

In `base.html` nav link for Runs (or a dedicated Alerts nav item):
```html
{% if g.unread_alert_count %}
<span class="badge bg-danger">{{ g.unread_alert_count }}</span>
{% endif %}
```

**Dashboard alert panel** (last 10 unread alerts, newest first):

```python
# In dashboard.py route:
alerts = session.execute(text("""
    SELECT id, level, message, created_at, ingestion_run_id
    FROM pipeline_alerts
    WHERE is_read = false
    ORDER BY created_at DESC
    LIMIT 10
""")).all()
```

Display in `dashboard.html` as a card with level-colored badges (error=red, warning=orange, info=blue), timestamp, optional run link, and "סמן כנקרא" button per row + "סמן הכל כנקרא" button.

---

### Task 8 — New template: `scheduler.html`

Hebrew RTL form page. Must include:

1. **Status indicator** — large badge: "מופעל" (green) / "מושבת" (red) + quick toggle button.
2. **Schedule form** — fields: שעת הרצה (0–23), דקת הרצה (0–59), ניסיונות חוזרים (0–10). Submit: "שמור הגדרות".
3. **Cleanup section** — current settings (cleanup_enabled toggle, cleanup_after_days input), last cleanup timestamp, manual trigger button "נקה כעת".
4. Display `updated_at` of the config row.

All forms POST to the correct endpoints. All inputs validated client-side (HTML5 `min`/`max`) and server-side.

---

### Task 9 — Cron setup instructions (for Team 20)

Add to `docs/OPERATIONS.md` (create if absent):

```bash
# Install cron (macOS / Linux):
crontab -e
# Add line:
* * * * * cd /Users/nimrod/Documents/SmallFarmsAgents && /path/to/.venv/bin/python -m organic_market_agent.scheduler.runner >> logs/runner.log 2>&1

# Verify:
crontab -l | grep runner
```

Team 20 is responsible for installing the cron line on the host machine after Team 10 delivers `runner.py`.

---

## Tests Required

### `tests/test_runner.py` (new — 4+ tests, no DB required for gating tests)

```python
# T1: scheduler exits immediately when is_enabled=False (mock DB response)
# T2: scheduler exits when current hour != run_hour (mock datetime + DB)
# T3: scheduler calls run_pipeline when hour/minute match (mock run_pipeline)
# T4: partial run (sources_failed > 0) → PipelineAlert written with level='warning'
```

Use `unittest.mock.patch` for `SessionFactory`, `run_pipeline`, and `datetime.now`.

### `tests/test_scheduler_routes.py` (new — 4+ tests)

```python
# T1: GET /scheduler returns 200 (logged_in_client)
# T2: POST /scheduler/toggle flips is_enabled in DB
# T3: POST /scheduler/run-cleanup (mock delete) returns flash with count
# T4: POST /alerts/<id>/read sets is_read=True
```

### `tests/test_admin_routes.py` extension

Add test: `POST /runs/trigger` with `source_code=SRC001` — verify the `IngestionRun` created has `sources_total` matching only that source (or that `run_pipeline` was called with `source_code='SRC001'`). Mock `run_pipeline` as in existing T09.

---

## Completion Report

File: `_COMMUNICATION/TEAM_10/reports/YYYY-MM-DD_M6_IMPLEMENTATION_COMPLETE_TEAM10.md`  
Template: `_COMMUNICATION/templates/COMPLETION_REPORT.md`

Must include:
- `pytest tests/ -q` output (0 failures)
- Screenshot or `curl` evidence of `/scheduler` page (200 + form present)
- Screenshot or `curl` evidence of dashboard charts (canvas elements present)
- `crontab -l` output (runner line present — Team 20 may file this separately)
- Confirmation that `run_pipeline()` accepts new kwargs

Then file QA Review Request to Team 50: `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_M6_REVIEW_REQUEST_TEAM50.md`

---

## Implementation Order

1. **Team 20** applies migration 016 and files completion report.
2. **Team 10** implements Tasks 1–9 in this order: Task 2 → Task 1 → Tasks 3–5 (parallel) → Tasks 6–8 (parallel) → tests.
3. **Team 10** files completion report + QA review request.
4. **Team 50** runs G6 QA per `QA_MANDATE_G6.md`.
5. **Team 100** reviews and signs off.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Mandate ID:** `MANDATE-M6-AUTOMATION-TEAM10`
