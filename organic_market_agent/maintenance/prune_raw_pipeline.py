"""Delete raw pipeline rows for all ingestion runs except one keep run.

Order respects FKs: observation_flags → normalized_observations → raw_extracted_items
→ raw_assets → source_fetch_runs → dependent tables → ingestion_runs.

Does not truncate daily_aggregates / weekly_snapshots; re-run Aggregator after prune
if you need aggregates to match remaining observations only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class PrunePlan:
    keep_ingestion_run_id: int
    doomed_ingestion_run_count: int
    doomed_sfr_count: int
    doomed_no_count: int
    doomed_rei_count: int
    doomed_ra_count: int


def resolve_keep_run_id(conn: Connection, *, timezone: str) -> int | None:
    """Latest finished ingestion_run today (Asia/Jerusalem by default); else latest any today."""
    row = conn.execute(
        text(
            """
            SELECT id
            FROM ingestion_runs
            WHERE (started_at AT TIME ZONE :tz)::date = (now() AT TIME ZONE :tz)::date
            ORDER BY
              CASE WHEN status IN ('completed', 'partial', 'failed') THEN 0 ELSE 1 END,
              id DESC
            LIMIT 1
            """
        ),
        {"tz": timezone},
    ).one_or_none()
    return int(row[0]) if row else None


def build_plan(conn: Connection, keep_id: int) -> PrunePlan:
    doomed_runs = conn.execute(
        text("SELECT COUNT(*) FROM ingestion_runs WHERE id <> :k"), {"k": keep_id}
    ).scalar_one()
    doomed_sfr = conn.execute(
        text(
            "SELECT COUNT(*) FROM source_fetch_runs WHERE ingestion_run_id <> :k"
        ),
        {"k": keep_id},
    ).scalar_one()
    doomed_no = conn.execute(
        text(
            """
            SELECT COUNT(*) FROM normalized_observations no
            JOIN source_fetch_runs sfr ON sfr.id = no.source_fetch_run_id
            WHERE sfr.ingestion_run_id <> :k
            """
        ),
        {"k": keep_id},
    ).scalar_one()
    doomed_rei = conn.execute(
        text(
            """
            SELECT COUNT(*) FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            WHERE sfr.ingestion_run_id <> :k
            """
        ),
        {"k": keep_id},
    ).scalar_one()
    doomed_ra = conn.execute(
        text(
            """
            SELECT COUNT(*) FROM raw_assets ra
            JOIN source_fetch_runs sfr ON sfr.id = ra.source_fetch_run_id
            WHERE sfr.ingestion_run_id <> :k
            """
        ),
        {"k": keep_id},
    ).scalar_one()
    return PrunePlan(
        keep_ingestion_run_id=keep_id,
        doomed_ingestion_run_count=int(doomed_runs or 0),
        doomed_sfr_count=int(doomed_sfr or 0),
        doomed_no_count=int(doomed_no or 0),
        doomed_rei_count=int(doomed_rei or 0),
        doomed_ra_count=int(doomed_ra or 0),
    )


def execute_prune(conn: Connection, keep_id: int) -> dict[str, int]:
    """Run deletes in one transaction (caller must commit). Returns rowcounts."""
    stats: dict[str, int] = {}

    r = conn.execute(
        text(
            """
            DELETE FROM observation_flags
            WHERE observation_id IN (
              SELECT no.id FROM normalized_observations no
              JOIN source_fetch_runs sfr ON sfr.id = no.source_fetch_run_id
              WHERE sfr.ingestion_run_id <> :k
            )
            """
        ),
        {"k": keep_id},
    )
    stats["observation_flags"] = r.rowcount or 0

    r = conn.execute(
        text(
            """
            DELETE FROM normalized_observations
            WHERE source_fetch_run_id IN (
              SELECT id FROM source_fetch_runs WHERE ingestion_run_id <> :k
            )
            """
        ),
        {"k": keep_id},
    )
    stats["normalized_observations"] = r.rowcount or 0

    r = conn.execute(
        text(
            """
            DELETE FROM raw_extracted_items
            WHERE source_fetch_run_id IN (
              SELECT id FROM source_fetch_runs WHERE ingestion_run_id <> :k
            )
            """
        ),
        {"k": keep_id},
    )
    stats["raw_extracted_items"] = r.rowcount or 0

    conn.execute(
        text(
            """
            UPDATE source_fetch_runs SET raw_asset_id = NULL
            WHERE ingestion_run_id <> :k
            """
        ),
        {"k": keep_id},
    )

    r = conn.execute(
        text(
            """
            DELETE FROM raw_assets
            WHERE source_fetch_run_id IN (
              SELECT id FROM source_fetch_runs WHERE ingestion_run_id <> :k
            )
            """
        ),
        {"k": keep_id},
    )
    stats["raw_assets"] = r.rowcount or 0

    r = conn.execute(
        text("DELETE FROM source_fetch_runs WHERE ingestion_run_id <> :k"),
        {"k": keep_id},
    )
    stats["source_fetch_runs"] = r.rowcount or 0

    r = conn.execute(
        text("UPDATE publish_runs SET ingestion_run_id = NULL WHERE ingestion_run_id <> :k"),
        {"k": keep_id},
    )
    stats["publish_runs_cleared"] = r.rowcount or 0

    r = conn.execute(
        text("DELETE FROM pipeline_alerts WHERE ingestion_run_id <> :k"),
        {"k": keep_id},
    )
    stats["pipeline_alerts"] = r.rowcount or 0

    r = conn.execute(
        text("DELETE FROM log_entries WHERE ingestion_run_id <> :k"),
        {"k": keep_id},
    )
    stats["log_entries"] = r.rowcount or 0

    r = conn.execute(
        text("DELETE FROM ingestion_runs WHERE id <> :k"),
        {"k": keep_id},
    )
    stats["ingestion_runs"] = r.rowcount or 0

    return stats


def prune_except_keep_run(
    session_or_conn: Session | Connection,
    *,
    keep_ingestion_run_id: int,
    dry_run: bool,
) -> tuple[PrunePlan, dict[str, Any] | None]:
    """Plan and optionally execute prune. Uses underlying connection from Session."""
    conn = session_or_conn.connection() if isinstance(session_or_conn, Session) else session_or_conn
    plan = build_plan(conn, keep_ingestion_run_id)
    if dry_run:
        return plan, None
    stats = execute_prune(conn, keep_ingestion_run_id)
    return plan, stats
