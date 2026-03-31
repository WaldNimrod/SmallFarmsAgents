"""IngestionRunner CLI — run a full ingestion cycle."""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone

import click
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import Session

from organic_market_agent.collectors.engine import CollectorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import (
    IngestionRun,
    NormalizerProfile,
    Source,
    SourceFetchProfile,
    SourceFetchRun,
)
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.parsers.engine import ParserEngine
from organic_market_agent.scheduler.pipeline_cancel import PipelineRunCancelled, is_cancelled
from organic_market_agent.scheduler.run_progress import merge_run_progress
from organic_market_agent.utils.config import config
from organic_market_agent.utils.log_persist import persist_log
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
    defer_terminal_status: bool = False,
) -> None:
    """Collect + parse for each source; update ingestion_run counters (no commit).

    Plain Python helper — no Click decoration. Called by pipeline.run_pipeline
    (background thread) and by run_ingestion() (CLI path).

    On HTTP/collector failure, each source is retried up to ``retry_attempts``
    additional times (1s pause between attempts).

    If ``defer_terminal_status`` is True (full background pipeline), keep
    ``status='running'`` and leave ``finished_at`` unset until the pipeline
    finishes; raises ``PipelineRunCancelled`` if cooperative cancel is set.
    """
    ingestion_run.sources_total = len(pairs)
    succeeded = 0
    failed = 0
    skipped = 0
    community_succeeded = 0

    max_tries = 1 + max(0, retry_attempts)

    persist_log(
        session,
        level="INFO",
        module="scheduler.run_ingestion",
        message=f"Ingestion phase started ({len(pairs)} sources, retry_attempts={retry_attempts})",
        ingestion_run_id=ingestion_run.id,
        extra={
            "sources_total": len(pairs),
            "retry_attempts": retry_attempts,
            "source_codes": [s.code for s, _ in pairs],
        },
    )
    merge_run_progress(
        session,
        ingestion_run.id,
        phase="ingestion",
        source_index=0,
        source_total=len(pairs),
        current_source_code=None,
        defer_terminal_status=defer_terminal_status,
    )

    for i, (source, profile) in enumerate(pairs, start=1):
        if is_cancelled(ingestion_run.id):
            ingestion_run.sources_succeeded = succeeded
            ingestion_run.sources_failed = failed
            ingestion_run.community_sources_succeeded = community_succeeded
            ingestion_run.finished_at = datetime.now(timezone.utc)
            ingestion_run.status = "failed"
            merge_run_progress(
                session,
                ingestion_run.id,
                phase="cancelled",
                source_index=i - 1,
                source_total=len(pairs),
                current_source_code=source.code,
            )
            persist_log(
                session,
                level="WARNING",
                module="scheduler.run_ingestion",
                message=f"Ingestion cancelled before source {source.code} ({i}/{len(pairs)})",
                ingestion_run_id=ingestion_run.id,
                extra={"source_index": i, "source_total": len(pairs), "source_code": source.code},
            )
            raise PipelineRunCancelled()

        raw_asset = None
        status = "failed"
        attempts_used = 0
        for attempt in range(max_tries):
            attempts_used = attempt + 1
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

        fetch_row = session.scalars(
            select(SourceFetchRun)
            .where(
                SourceFetchRun.ingestion_run_id == ingestion_run.id,
                SourceFetchRun.source_id == source.id,
            )
            .order_by(SourceFetchRun.id.desc())
            .limit(1)
        ).first()
        fr_id = fetch_row.id if fetch_row else None
        fetch_status = fetch_row.status if fetch_row else status
        fetch_err = (fetch_row.error_message if fetch_row else None) or None

        normalizer_type: str | None = None
        parser_items = 0
        parser_note: str | None = None

        if status == "success" and raw_asset is not None:
            normalizer_type = _get_normalizer_type(session, source.id)
            if normalizer_type:
                parser_items = parser_engine.run(
                    session,
                    raw_asset,
                    source,
                    normalizer_type,
                    ingestion_run_id=ingestion_run.id,
                    charset_hint=profile.charset_hint,
                    selector_overrides=profile.selector_profile,
                )
            else:
                parser_note = "no_active_normalizer_profile"
            succeeded += 1
            if source.market_scope == "community":
                community_succeeded += 1
        elif status == "failed":
            failed += 1
        elif status == "skipped":
            skipped += 1

        row_level = "INFO"
        if fetch_status == "failed" or parser_note == "no_active_normalizer_profile":
            row_level = "WARNING"
        persist_log(
            session,
            level=row_level,
            module="scheduler.run_ingestion",
            message=(
                f"Source {source.code}: fetch={fetch_status} "
                f"items_extracted={parser_items}"
                + (f" ({parser_note})" if parser_note else "")
            ),
            ingestion_run_id=ingestion_run.id,
            entity_type="source",
            entity_id=source.id,
            extra={
                "source_code": source.code,
                "fetch_status": fetch_status,
                "source_fetch_run_id": fr_id,
                "attempts_used": attempts_used,
                "fetch_retry_count": fetch_row.retry_count if fetch_row else None,
                "raw_asset_id": raw_asset.id if raw_asset else None,
                "items_extracted": parser_items,
                "normalizer_type": normalizer_type,
                "parser_note": parser_note,
                "fetch_error_message": fetch_err[:800] if fetch_err else None,
                "fetch_mode": profile.fetch_mode,
                "platform_family": profile.platform_family,
            },
        )
        merge_run_progress(
            session,
            ingestion_run.id,
            phase="ingestion",
            source_index=i,
            source_total=len(pairs),
            current_source_code=source.code,
        )

    ingestion_run.sources_succeeded = succeeded
    ingestion_run.sources_failed = failed
    ingestion_run.community_sources_succeeded = community_succeeded
    logical_status = (
        "completed" if failed == 0 else ("partial" if succeeded > 0 else "failed")
    )
    if defer_terminal_status:
        ingestion_run.status = "running"
        ingestion_run.finished_at = None
    else:
        ingestion_run.finished_at = datetime.now(timezone.utc)
        ingestion_run.status = logical_status

    persist_log(
        session,
        level="INFO",
        module="scheduler.run_ingestion",
        message=(
            f"Ingestion phase finished: logical_status={logical_status} "
            f"ok={succeeded} failed={failed} skipped={skipped} "
            f"community_ok={community_succeeded}"
            + (" (terminal status deferred for full pipeline)" if defer_terminal_status else "")
        ),
        ingestion_run_id=ingestion_run.id,
        extra={
            "sources_total": ingestion_run.sources_total,
            "sources_succeeded": succeeded,
            "sources_failed": failed,
            "sources_skipped": skipped,
            "community_sources_succeeded": community_succeeded,
            "run_status": logical_status,
            "defer_terminal_status": defer_terminal_status,
        },
    )
    merge_run_progress(
        session,
        ingestion_run.id,
        phase="ingestion_done",
        source_index=len(pairs),
        source_total=len(pairs),
        current_source_code=None,
        ingestion_logical_status=logical_status,
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
