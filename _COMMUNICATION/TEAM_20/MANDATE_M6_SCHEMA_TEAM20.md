---
document_type: MANDATE
version: "1.0"
---

# Mandate — M6 Schema: Scheduler Config + Pipeline Alerts

**Mandate ID:** `MANDATE-M6-SCHEMA-TEAM20`  
**From:** Team 100 (Architecture)  
**To:** Team 20 (Infrastructure)  
**CC:** Team 10 (Feature Dev), Team 50 (QA)  
**Date:** 2026-03-31  
**Milestone:** M6 — Automation + Resilience  
**Dependency:** Gate G5 ✅ PASS — implement immediately  

---

## Context

M6 introduces dashboard-first automation: a scheduler controlled from the admin UI (no SMTP), in-app pipeline alerts, and log cleanup. Team 10 cannot begin M6 feature work until migration 016 is applied. Team 20 must complete this migration first.

---

## Deliverable: Migration 016

**File:** `organic_market_agent/db/versions/016_m6_scheduler_and_alerts.py`  
`revision = "016"`, `down_revision = "015"`

### Table 1 — `scheduler_config`

Single-row configuration table for the automated pipeline runner.

```sql
CREATE TABLE scheduler_config (
    id               SERIAL PRIMARY KEY,
    is_enabled       BOOLEAN      NOT NULL DEFAULT TRUE,
    run_hour         INTEGER      NOT NULL DEFAULT 6
                     CHECK (run_hour >= 0 AND run_hour <= 23),
    run_minute       INTEGER      NOT NULL DEFAULT 0
                     CHECK (run_minute >= 0 AND run_minute <= 59),
    retry_attempts   INTEGER      NOT NULL DEFAULT 2
                     CHECK (retry_attempts >= 0 AND retry_attempts <= 10),
    cleanup_enabled  BOOLEAN      NOT NULL DEFAULT TRUE,
    cleanup_after_days INTEGER    NOT NULL DEFAULT 90
                     CHECK (cleanup_after_days >= 7),
    cleanup_last_run TIMESTAMPTZ,
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);
```

**Seed:** insert exactly one row with all defaults:
```sql
INSERT INTO scheduler_config
    (is_enabled, run_hour, run_minute, retry_attempts, cleanup_enabled, cleanup_after_days)
VALUES (TRUE, 6, 0, 2, TRUE, 90)
ON CONFLICT DO NOTHING;
```

### Table 2 — `pipeline_alerts`

In-app alerts written by `scheduler/runner.py` and displayed in the admin dashboard.

```sql
CREATE TABLE pipeline_alerts (
    id                SERIAL PRIMARY KEY,
    ingestion_run_id  INTEGER REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    level             VARCHAR(20) NOT NULL
                      CHECK (level IN ('info', 'warning', 'error')),
    message           TEXT        NOT NULL,
    is_read           BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_pipeline_alerts_is_read ON pipeline_alerts (is_read);
CREATE INDEX ix_pipeline_alerts_created_at ON pipeline_alerts (created_at DESC);
```

### `downgrade()`

Drop both tables in reverse order:
```sql
DROP TABLE IF EXISTS pipeline_alerts;
DROP TABLE IF EXISTS scheduler_config;
```

---

## `db.check` Extension

Extend `organic_market_agent/db/check.py` to verify:

1. `scheduler_config` table exists.
2. `pipeline_alerts` table exists.
3. Exactly one row in `scheduler_config` (the seed row).

```python
# Example check block to add:
sc_count = session.execute(text("SELECT COUNT(*) FROM scheduler_config")).scalar()
assert sc_count == 1, f"scheduler_config seed row missing (count={sc_count})"

pa_exists = session.execute(
    text("SELECT to_regclass('public.pipeline_alerts')")
).scalar()
assert pa_exists is not None, "pipeline_alerts table missing"
```

---

## Alembic Models

Add SQLAlchemy models to `organic_market_agent/models/`:

**`organic_market_agent/models/scheduler.py`** (new file):

```python
from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Integer, Text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from organic_market_agent.db.base import Base

class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    run_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    run_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    cleanup_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cleanup_after_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    cleanup_last_run: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

class PipelineAlert(Base):
    __tablename__ = "pipeline_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingestion_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    level: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
```

Export both from `organic_market_agent/models/__init__.py`.

---

## Verification Commands

```bash
# Apply migration
alembic upgrade head
# Expected output includes: 015 -> 016

# Confirm revision
alembic current
# Expected: 016 (head)

# Run db.check
python -m organic_market_agent.db.check
# Expected: PASS (includes scheduler_config seed row and pipeline_alerts table)

# Verify tables and seed
psql $DATABASE_URL -c "\d scheduler_config"
psql $DATABASE_URL -c "SELECT * FROM scheduler_config;"
psql $DATABASE_URL -c "\d pipeline_alerts"

# Full test suite
pytest tests/ -q
# Expected: all existing tests pass (no new tests required from Team 20)
```

---

## Completion Report

File: `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_M6_SCHEMA_COMPLETE_TEAM20.md`  
Template: `_COMMUNICATION/templates/COMPLETION_REPORT.md`

Must include:
- `alembic upgrade head` output
- `alembic current` output  
- `python -m organic_market_agent.db.check` output (PASS)
- `SELECT * FROM scheduler_config` output (1 row with defaults)
- `pytest tests/ -q` output (0 failures)

---

## Implementation Order

Team 20 must complete migration 016 **before** Team 10 begins M6 feature work. Signal completion by filing the report above and notifying Team 100.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31  
**Mandate ID:** `MANDATE-M6-SCHEMA-TEAM20`
