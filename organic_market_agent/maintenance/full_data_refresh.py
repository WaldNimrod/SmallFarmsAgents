"""One-off: delete normalized observations for a raw-item subset, re-queue, normalize, aggregate, publish.

Used to refresh quality on existing DB data without new ingestion. Does not reset rows already
`ignored` (e.g. approved scope skips).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import bindparam, text

from organic_market_agent.aggregator.engine import AggregatorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.publisher.engine import PublishEngine
from organic_market_agent.utils.exceptions import PublishAbortError


@dataclass(frozen=True)
class FullDataRefreshStats:
    """Counts from a full raw re-normalize maintenance run."""

    target_raw_item_count: int
    observation_flags_deleted: int
    normalized_observations_deleted: int
    raw_items_reset_to_extracted: int
    normalizer_resolved: int
    normalizer_unresolvable: int
    normalizer_scope_skipped: int
    normalizer_skipped: int
    aggregate_created: int
    aggregate_updated: int
    aggregate_date: date
    publish_ok: bool
    publish_error: str | None


def run_full_data_refresh(
    *,
    community_only: bool = True,
    aggregate_date: date | None = None,
    output_dir: Path | None = None,
) -> FullDataRefreshStats:
    """Delete NO for matching raw items, set them to extracted, normalize, aggregate one day, publish."""
    agg_d = aggregate_date or datetime.now(timezone.utc).date()
    out = output_dir or Path("output/public")

    community_clause = "AND s.market_scope = 'community'" if community_only else ""

    with SessionFactory() as session:
        ids_rows = session.execute(
            text(
                f"""
                SELECT rei.id FROM raw_extracted_items rei
                JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
                JOIN sources s ON s.id = sfr.source_id
                WHERE rei.is_quarantined IS NOT TRUE
                  AND rei.extraction_status IN ('normalized', 'unresolvable')
                  {community_clause}
                """
            )
        ).all()
        target_ids = [int(r[0]) for r in ids_rows]
        n_target = len(target_ids)
        if n_target == 0:
            n_flags = n_no = n_reset = 0
        else:
            del_flags = text(
                """
                DELETE FROM observation_flags
                WHERE observation_id IN (
                    SELECT id FROM normalized_observations
                    WHERE raw_extracted_item_id IN :ids
                )
                """
            ).bindparams(bindparam("ids", expanding=True))
            r1 = session.execute(del_flags, {"ids": target_ids})
            n_flags = int(r1.rowcount or 0)
            del_no = text(
                "DELETE FROM normalized_observations WHERE raw_extracted_item_id IN :ids"
            ).bindparams(bindparam("ids", expanding=True))
            r2 = session.execute(del_no, {"ids": target_ids})
            n_no = int(r2.rowcount or 0)
            upd_rei = text(
                """
                UPDATE raw_extracted_items
                SET extraction_status = 'extracted',
                    unresolvable_reason = NULL,
                    ignore_reason_code = NULL
                WHERE id IN :ids
                """
            ).bindparams(bindparam("ids", expanding=True))
            r3 = session.execute(upd_rei, {"ids": target_ids})
            n_reset = int(r3.rowcount or 0)
        session.commit()

    n_res = n_unres = n_scope = n_skip = 0
    with SessionFactory() as session:
        counts = NormalizerEngine().run(session, ingestion_run_id=None, source_id=None)
    n_res = int(counts.get("resolved", 0))
    n_unres = int(counts.get("unresolvable", 0))
    n_scope = int(counts.get("scope_skipped", 0))
    n_skip = int(counts.get("skipped", 0))

    cr = cu = 0
    with SessionFactory() as session:
        agg = AggregatorEngine().run(session, agg_d)
    cr = int(agg.get("created", 0))
    cu = int(agg.get("updated", 0))

    publish_ok = False
    publish_err: str | None = None
    try:
        with SessionFactory() as session:
            PublishEngine().run(session, out, report_date=agg_d)
        publish_ok = True
    except PublishAbortError as exc:
        publish_err = str(exc)

    return FullDataRefreshStats(
        target_raw_item_count=n_target,
        observation_flags_deleted=n_flags,
        normalized_observations_deleted=n_no,
        raw_items_reset_to_extracted=n_reset,
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
