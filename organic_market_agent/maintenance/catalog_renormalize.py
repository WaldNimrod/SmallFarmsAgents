"""Re-queue raw rows after catalog / alias changes, then normalize → aggregate → publish.

Typical use: new global `product_aliases` rows; previously `unresolvable` lines are set back
to `extraction_status='extracted'` so `NormalizerEngine` can resolve them on the next pass.

Does not reset already-`normalized` rows (avoids duplicate observations and wide re-aggregation).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from organic_market_agent.aggregator.engine import AggregatorEngine
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.publisher.engine import PublishEngine
from organic_market_agent.utils.exceptions import PublishAbortError


@dataclass(frozen=True)
class RequeueStats:
    """Counts from a catalog re-normalize maintenance run."""

    unresolvable_requeued: int
    normalizer_resolved: int
    normalizer_unresolvable: int
    normalizer_scope_skipped: int
    normalizer_skipped: int
    aggregate_created: int
    aggregate_updated: int
    aggregate_date: date
    publish_ok: bool
    publish_error: str | None


def count_unresolvable_requeueable(session: Session) -> int:
    """Rows that can be sent back through the normalizer (non-quarantined unresolvable)."""
    n = session.execute(
        text(
            """
            SELECT COUNT(*) FROM raw_extracted_items
            WHERE extraction_status = 'unresolvable'
              AND is_quarantined IS NOT TRUE
            """
        )
    ).scalar_one()
    return int(n or 0)


def requeue_unresolvable_raw_items(session: Session) -> int:
    """Set `unresolvable` → `extracted` so `NormalizerEngine` picks them up."""
    result = session.execute(
        text(
            """
            UPDATE raw_extracted_items
            SET extraction_status = 'extracted',
                unresolvable_reason = NULL,
                ignore_reason_code = NULL
            WHERE extraction_status = 'unresolvable'
              AND is_quarantined IS NOT TRUE
            """
        )
    )
    session.commit()
    return int(result.rowcount or 0)


def run_catalog_renormalize(
    *,
    skip_normalize: bool = False,
    skip_aggregate: bool = False,
    skip_publish: bool = False,
    aggregate_date: date | None = None,
    output_dir: Path | None = None,
) -> RequeueStats:
    """Requeue unresolvable raw items, normalize, aggregate one day, publish (optional).

    New observations use `observed_at=now()` in `NormalizerEngine` (same as pipeline); the
    aggregate step should use the same calendar day (default: today UTC).
    """
    from organic_market_agent.db.session import SessionFactory

    agg_d = aggregate_date or datetime.now(timezone.utc).date()
    out = output_dir or Path("output/public")

    requeued = 0
    with SessionFactory() as session:
        requeued = requeue_unresolvable_raw_items(session)

    n_res = n_unres = n_scope = n_skip = 0
    if not skip_normalize:
        with SessionFactory() as session:
            counts = NormalizerEngine().run(session, ingestion_run_id=None, source_id=None)
        n_res = int(counts.get("resolved", 0))
        n_unres = int(counts.get("unresolvable", 0))
        n_scope = int(counts.get("scope_skipped", 0))
        n_skip = int(counts.get("skipped", 0))

    cr = cu = 0
    if not skip_aggregate:
        with SessionFactory() as session:
            agg = AggregatorEngine().run(session, agg_d)
        cr = int(agg.get("created", 0))
        cu = int(agg.get("updated", 0))

    publish_ok = False
    publish_err: str | None = None
    if not skip_publish:
        try:
            with SessionFactory() as session:
                PublishEngine().run(session, out, report_date=agg_d)
            publish_ok = True
        except PublishAbortError as exc:
            publish_err = str(exc)

    return RequeueStats(
        unresolvable_requeued=requeued,
        normalizer_resolved=n_res,
        normalizer_unresolvable=n_unres,
        normalizer_scope_skipped=n_scope,
        normalizer_skipped=n_skip,
        aggregate_created=cr,
        aggregate_updated=cu,
        aggregate_date=agg_d,
        publish_ok=publish_ok,
        publish_error=publish_err,
    )
