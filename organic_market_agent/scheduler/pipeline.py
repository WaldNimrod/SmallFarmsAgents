"""Full pipeline: ingestion for an existing run, then normalize, aggregate, publish."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from organic_market_agent.aggregator.engine import AggregatorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import IngestionRun
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


def run_pipeline(ingestion_run_id: int) -> None:
    """Background worker: collect/parse, normalizer, aggregator (today UTC), publish."""
    config.ensure_dirs()
    try:
        with SessionFactory() as session:
            ingestion_run = session.get(IngestionRun, ingestion_run_id)
            if ingestion_run is None:
                logger.error("run_pipeline: IngestionRun id=%s not found", ingestion_run_id)
                return
            pairs = _get_active_sources_with_profiles(session)
            execute_ingestion_for_run(session, ingestion_run, pairs)
            session.commit()

        with SessionFactory() as session:
            NormalizerEngine().run(session, ingestion_run_id=ingestion_run_id)

        agg_date = datetime.now(timezone.utc).date()
        with SessionFactory() as session:
            AggregatorEngine().run(session, agg_date)

        with SessionFactory() as session:
            try:
                PublishEngine().run(session, Path("output/public"))
            except PublishAbortError as exc:
                logger.warning("run_pipeline: publish aborted: %s", exc)
    except Exception:
        logger.exception("run_pipeline failed for ingestion_run_id=%s", ingestion_run_id)
