"""Reconcile DB state after process restart or admin stop.

Call from the **admin** Flask app on startup only. Do not invoke from the cron ``runner``
process while another app may legitimately be executing a pipeline in a different
process—shared PostgreSQL would then mark an active run as failed incorrectly.
"""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun, PipelineAlert


def reconcile_stale_running_runs(
    session: Session,
    *,
    reason_code: str,
    message_prefix: str,
    create_summary_alert: bool = True,
) -> list[int]:
    """Set status=failed and finished_at for all rows with status=running.

    Returns affected ingestion_run ids (newest first).
    """
    ids = list(
        session.scalars(
            sa.select(IngestionRun.id).where(IngestionRun.status == "running").order_by(IngestionRun.id.desc())
        ).all()
    )
    if not ids:
        return []

    now = datetime.now(timezone.utc)
    suffix = f" ({reason_code})"
    for ir in session.scalars(
        sa.select(IngestionRun).where(IngestionRun.status == "running")
    ).all():
        ir.status = "failed"
        ir.finished_at = now
        note = (ir.notes or "").strip()
        ir.notes = (note + " " if note else "") + f"marked_failed:{reason_code}"

    if create_summary_alert and ids:
        id_part = ", ".join(str(i) for i in ids[:40])
        if len(ids) > 40:
            id_part += f", … (+{len(ids) - 40} more)"
        session.add(
            PipelineAlert(
                level="warning",
                message=f"{message_prefix} Count={len(ids)}. Run ids: {id_part}",
                ingestion_run_id=None,
            )
        )
    session.flush()
    return ids
