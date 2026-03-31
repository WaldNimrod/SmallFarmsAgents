# M6 Automation + Resilience — G6 QA review request (Team 50)

**Date:** 2026-03-31  
**From:** Team 10 (Feature Dev)  
**Mandate:** `MANDATE-M6-AUTOMATION-TEAM10`  
**Completion report:** `_COMMUNICATION/TEAM_10/reports/2026-03-31_M6_IMPLEMENTATION_COMPLETE_TEAM10.md`  
**QA mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G6.md`

## Ask

Please begin **Gate G6** QA against the codebase per `QA_MANDATE_G6.md` and file a dated report under `_COMMUNICATION/TEAM_50/reports/` (e.g. `YYYY-MM-DD_QA_G6_TEAM50.md`) with **PASS / FAIL** and evidence.

## Preconditions

- PostgreSQL with Alembic through **016** (`scheduler_config`, `pipeline_alerts`).
- Seed admin user for authenticated routes (`admin@local` / `admin` per migration 015).
- Optional: `crontab` runner line per `docs/OPERATIONS.md` (Team 20 host); not required to execute all UI-focused checks.

## Suggested test entrypoints

```bash
python3 -m pytest tests/test_runner.py tests/test_scheduler_routes.py -v
python3 -m pytest tests/ -q
python3 -m organic_market_agent.db.check
```

## Scope reminder (high level)

- `organic_market_agent.scheduler.runner` — gating, daily run, post-run `PipelineAlert`.
- `run_pipeline()` — `source_code`, `skip_normalize`, `skip_publish`, `retry_attempts`.
- Admin: `/scheduler`, `/alerts/*`, extended `/runs`, dashboard charts + unread alerts.
- `docs/OPERATIONS.md` — cron documentation.

---

*Team 10 — handoff for G6 QA*
