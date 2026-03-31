"""IngestionRunner CLI — run a full ingestion cycle."""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

import click
import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.collectors.engine import CollectorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import IngestionRun, NormalizerProfile, Source, SourceFetchProfile
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.parsers.engine import ParserEngine
from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

collector_engine = CollectorEngine()
parser_engine = ParserEngine()


def _get_active_sources_with_profiles(session: Session) -> list[tuple[Source, SourceFetchProfile]]:
    rows = session.execute(
        sa.select(Source, SourceFetchProfile)
        .join(SourceFetchProfile, SourceFetchProfile.source_id == Source.id)
        .where(Source.is_active.is_(True))
        .where(SourceFetchProfile.is_active.is_(True))
        .order_by(Source.priority.asc())
    ).all()
    return [(r[0], r[1]) for r in rows]


def _get_normalizer_type(session: Session, source_id: int) -> str | None:
    return session.execute(
        sa.select(NormalizerProfile.normalizer_type).where(
            NormalizerProfile.source_id == source_id,
            NormalizerProfile.is_active.is_(True),
        )
    ).scalar_one_or_none()


def execute_ingestion_for_run(
    session: Session,
    ingestion_run: IngestionRun,
    pairs: list[tuple[Source, SourceFetchProfile]],
    *,
    retry_attempts: int = 2,
) -> None:
    """Collect + parse for each source; update ingestion_run counters (no commit).

    Plain Python helper — no Click decoration. Called by pipeline.run_pipeline
    (background thread) and by run_ingestion() (CLI path).

    On HTTP/collector failure, each source is retried up to ``retry_attempts``
    additional times (1s pause between attempts).
    """
    ingestion_run.sources_total = len(pairs)
    succeeded = 0
    failed = 0
    skipped = 0
    community_succeeded = 0

    max_tries = 1 + max(0, retry_attempts)

    for source, profile in pairs:
        raw_asset = None
        status = "failed"
        for attempt in range(max_tries):
            raw_asset, status = collector_engine.run(
                session,
                ingestion_run.id,
                source,
                profile,
            )
            if status in ("success", "skipped"):
                break
            if status == "failed" and attempt < max_tries - 1:
                time.sleep(1)

        if status == "success" and raw_asset is not None:
            normalizer_type = _get_normalizer_type(session, source.id)
            if normalizer_type:
                parser_engine.run(
                    session,
                    raw_asset,
                    source,
                    normalizer_type,
                    ingestion_run_id=ingestion_run.id,
                    charset_hint=profile.charset_hint,
                    selector_overrides=profile.selector_profile,
                )
            succeeded += 1
            if source.market_scope == "community":
                community_succeeded += 1
        elif status == "failed":
            failed += 1
        elif status == "skipped":
            skipped += 1

    ingestion_run.sources_succeeded = succeeded
    ingestion_run.sources_failed = failed
    ingestion_run.community_sources_succeeded = community_succeeded
    ingestion_run.finished_at = datetime.now(timezone.utc)
    ingestion_run.status = (
        "completed" if failed == 0 else ("partial" if succeeded > 0 else "failed")
    )


def run_ingestion(
    run_type: str,
    source_code: str | None,
    normalize: bool,
) -> None:
    """Execute a full (or single-source) ingestion run."""
    config.ensure_dirs()

    with SessionFactory() as session:
        pairs = _get_active_sources_with_profiles(session)
        if source_code:
            pairs = [(s, p) for s, p in pairs if s.code == source_code]
            if not pairs:
                click.echo(f"No active source with code={source_code!r}", err=True)
                sys.exit(1)

        ingestion_run = IngestionRun(
            run_type=run_type,
            triggered_by="cli",
            sources_total=len(pairs),
        )
        session.add(ingestion_run)
        session.flush()

        execute_ingestion_for_run(session, ingestion_run, pairs)
        session.commit()

        # Read counters from the model fields populated by execute_ingestion_for_run
        click.echo(
            f"IngestionRun #{ingestion_run.id}: "
            f"status={ingestion_run.status} "
            f"succeeded={ingestion_run.sources_succeeded} "
            f"failed={ingestion_run.sources_failed} "
            f"community_ok={ingestion_run.community_sources_succeeded}"
        )

        if normalize:
            with SessionFactory() as norm_session:
                norm_engine = NormalizerEngine()
                ncounts = norm_engine.run(norm_session, ingestion_run_id=ingestion_run.id)
                click.echo(
                    f"Normalizer: resolved={ncounts['resolved']} "
                    f"unresolvable={ncounts['unresolvable']} skipped={ncounts['skipped']}"
                )


@click.command("run_ingestion")
@click.option("--run-type", default="daily", type=click.Choice(["daily", "manual", "retry"]))
@click.option("--source-code", default=None, help="Run a single source by code (for debugging)")
@click.option(
    "--normalize",
    is_flag=True,
    default=False,
    help="Run M3 normalizer after ingestion for this ingestion run",
)
def run_ingestion_cli(run_type: str, source_code: str | None, normalize: bool) -> None:
    """CLI entry point — thin wrapper around run_ingestion()."""
    run_ingestion(run_type, source_code, normalize)


if __name__ == "__main__":
    run_ingestion_cli(standalone_mode=True)
