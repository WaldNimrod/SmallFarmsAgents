# M6 Schema — completion report (Team 20)

**Date:** 2026-03-31  
**Mandate ID:** `MANDATE-M6-SCHEMA-TEAM20`  
**Reference:** `_COMMUNICATION/TEAM_20/MANDATE_M6_SCHEMA_TEAM20.md`

---

## Deliverables

| Item | Path / note |
|------|-------------|
| Migration 016 | `organic_market_agent/db/versions/016_m6_scheduler_and_alerts.py` |
| SQLAlchemy models | `organic_market_agent/models/scheduler.py` (`SchedulerConfig`, `PipelineAlert`); exported from `models/__init__.py` |
| db.check | `organic_market_agent/db/check.py` — tables + exactly one `scheduler_config` row |

---

## Deviations from mandate text (documented)

1. **Seed:** Mandate `ON CONFLICT DO NOTHING` has no unique target. Implemented `INSERT ... SELECT ... WHERE NOT EXISTS (SELECT 1 FROM scheduler_config)`.
2. **`pipeline_alerts.ingestion_run_id`:** `BigInteger` FK to `ingestion_runs.id` (matches `001`; mandate said INTEGER).
3. **PK types:** `Integer` + `Identity` (PostgreSQL equivalent to SERIAL) for both new tables.

---

## `alembic upgrade head` / `alembic current`

```text
INFO  [alembic.runtime.migration] Running upgrade 015 -> 016, 016: M6 — scheduler_config + pipeline_alerts.

016 (head)
```

---

## `python -m organic_market_agent.db.check`

```text
  OK  scheduler_config
  OK  pipeline_alerts
  ...
  OK  scheduler_config: 1 rows (expected exactly 1)
RESULT: PASS
```

---

## `SELECT * FROM scheduler_config` (sample run)

```text
(1, True, 6, 0, 2, True, 90, None, <updated_at timestamptz>)
```

Columns: `id`, `is_enabled`, `run_hour`, `run_minute`, `retry_attempts`, `cleanup_enabled`, `cleanup_after_days`, `cleanup_last_run`, `updated_at`.

---

## Indexes (`pipeline_alerts`)

- `ix_pipeline_alerts_is_read` on `(is_read)`
- `ix_pipeline_alerts_created_at` on `(created_at DESC)` (raw `CREATE INDEX` in migration)

---

## `pytest tests/ -q`

```text
73 passed, 1 skipped
```

---

## Blockers

None.

---

*Team 20 (Infrastructure)*
