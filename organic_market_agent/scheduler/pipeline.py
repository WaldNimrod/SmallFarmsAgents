"""Full pipeline: ingestion for an existing run, then normalize, aggregate, publish."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from organic_market_agent.aggregator.engine import AggregatorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import IngestionRun, PipelineAlert
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.publisher.engine import PublishEngine
from organic_market_agent.scheduler.run_ingestion import (
    _get_active_sources_with_profiles,
    execute_ingestion_for_run,
)
from organic_market_agent.utils.config import config
from organic_market_agent.utils.exceptions import PublishAbortError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def run_pipeline(
    ingestion_run_id: int,
    *,
    source_code: str | None = None,
    skip_normalize: bool = False,
    skip_publish: bool = False,
    retry_attempts: int = 2,
) -> None:
    """Background worker: collect/parse, optional normalizer, aggregator (today UTC), optional publish."""
    config.ensure_dirs()
    try:
        with SessionFactory() as session:
            ingestion_run = session.get(IngestionRun, ingestion_run_id)
            if ingestion_run is None:
                logger.error("run_pipeline: IngestionRun id=%s not found", ingestion_run_id)
                return
            pairs = _get_active_sources_with_profiles(session)
            if source_code:
                pairs = [(s, p) for s, p in pairs if s.code == source_code]
            if not pairs:
                msg = (
                    f"No active source matching code={source_code!r}"
                    if source_code
                    else "No active sources with fetch profiles"
                )
                logger.warning("run_pipeline: %s (ingestion_run_id=%s)", msg, ingestion_run_id)
                ingestion_run.sources_total = 0
                ingestion_run.sources_succeeded = 0
                ingestion_run.sources_failed = 0
                ingestion_run.community_sources_succeeded = 0
                ingestion_run.finished_at = datetime.now(timezone.utc)
                ingestion_run.status = "failed"
                session.add(
                    PipelineAlert(
                        level="error",
                        message=msg,
                        ingestion_run_id=ingestion_run_id,
                    )
                )
                session.commit()
                return

            execute_ingestion_for_run(
                session, ingestion_run, pairs, retry_attempts=retry_attempts
            )
            session.commit()

        if not skip_normalize:
            with SessionFactory() as session:
                NormalizerEngine().run(session, ingestion_run_id=ingestion_run_id)

        agg_date = datetime.now(timezone.utc).date()
        with SessionFactory() as session:
            AggregatorEngine().run(session, agg_date)

        if not skip_publish:
            with SessionFactory() as session:
                try:
                    PublishEngine().run(session, Path("output/public"))
                except PublishAbortError as exc:
                    logger.warning("run_pipeline: publish aborted: %s", exc)
    except Exception:
        logger.exception("run_pipeline failed for ingestion_run_id=%s", ingestion_run_id)
        try:
            with SessionFactory() as session:
                run = session.get(IngestionRun, ingestion_run_id)
                if run is not None and run.status == "running":
                    run.status = "failed"
                    run.finished_at = datetime.now(timezone.utc)
                    session.commit()
        except Exception:
            logger.exception(
                "run_pipeline: could not mark ingestion_run_id=%s failed", ingestion_run_id
            )
