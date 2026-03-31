"""Cron entrypoint: self-gating daily pipeline + in-app alerts.

Run: python -m organic_market_agent.scheduler.runner
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import IngestionRun, PipelineAlert, SchedulerConfig
from organic_market_agent.scheduler.pipeline import run_pipeline
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def _scheduler_config(session: Session) -> SchedulerConfig | None:
    return session.scalars(sa.select(SchedulerConfig).limit(1)).first()


def _minutes_since_midnight_utc(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def scheduled_time_matches(now: datetime, run_hour: int, run_minute: int) -> bool:
    """True if now (UTC) is within ±1 minute of run_hour:run_minute."""
    target = run_hour * 60 + run_minute
    current = _minutes_since_midnight_utc(now)
    return abs(current - target) <= 1


def alert_for_run_outcome(run: IngestionRun) -> tuple[str, str]:
    """Return (level, message) for a finished ingestion run."""
    if run.status == "failed":
        return (
            "error",
            f"Ingestion run #{run.id} failed "
            f"(succeeded={run.sources_succeeded}, failed={run.sources_failed}).",
        )
    if run.sources_failed > 0:
        return (
            "warning",
            f"Ingestion run #{run.id} partial: {run.sources_failed} source(s) failed, "
            f"{run.sources_succeeded} succeeded.",
        )
    return (
        "info",
        f"Ingestion run #{run.id} completed ({run.sources_succeeded} sources ok).",
    )


def main() -> None:
    with SessionFactory() as session:
        cfg = _scheduler_config(session)
        if cfg is None:
            logger.error("scheduler runner: no scheduler_config row")
            return
        if not cfg.is_enabled:
            logger.info("scheduler disabled")
            return

        retry_attempts = cfg.retry_attempts
        now = datetime.now(timezone.utc)
        if not scheduled_time_matches(now, cfg.run_hour, cfg.run_minute):
            return

        running = session.execute(
            sa.select(sa.func.count())
            .select_from(IngestionRun)
            .where(IngestionRun.status == "running")
        ).scalar_one()
        if int(running or 0) > 0:
            logger.info("scheduler runner: skip — an ingestion run is already running")
            return

        run = IngestionRun(
            run_type="daily",
            triggered_by="cron",
            status="running",
            started_at=now,
            sources_total=0,
            sources_succeeded=0,
            sources_failed=0,
            community_sources_succeeded=0,
        )
        session.add(run)
        session.flush()
        run_id = run.id
        session.commit()

    run_pipeline(run_id, retry_attempts=retry_attempts)

    with SessionFactory() as session:
        finished = session.get(IngestionRun, run_id)
        if finished is None:
            logger.error("scheduler runner: IngestionRun id=%s missing after pipeline", run_id)
            return
        level, message = alert_for_run_outcome(finished)
        session.add(
            PipelineAlert(
                level=level,
                message=message,
                ingestion_run_id=run_id,
            )
        )
        session.commit()


if __name__ == "__main__":
    main()
