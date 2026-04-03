"""Reconcile DB state after process restart or admin stop.

Call from the **admin** Flask app on startup only. Do not invoke from the cron ``runner``
process while another app may legitimately be executing a pipeline in a different
process—shared PostgreSQL would then mark an active run as failed incorrectly.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun, PipelineAlert
from organic_market_agent.utils.pipeline_alert_tags import (
    TAG_OPS_ADMIN_STOP_ALL,
    TAG_OPS_PROCESS_RESTART,
    tagged_message,
)

ReasonCode = Literal["process_restart", "admin_stop_all", "admin_manual_reconcile"]

_OPS_BODY: dict[ReasonCode, tuple[str, str]] = {
    "process_restart": (
        TAG_OPS_PROCESS_RESTART,
        "Stale running ingestion run(s) marked failed after admin process "
        "(re)start — no worker was attached.",
    ),
    "admin_stop_all": (
        TAG_OPS_ADMIN_STOP_ALL,
        "Admin stopped active ingestion run(s) (stop-all).",
    ),
    "admin_manual_reconcile": (
        TAG_OPS_PROCESS_RESTART,
        "Admin manually reconciled stale running ingestion run(s).",
    ),
}


def reconcile_stale_running_runs(
    session: Session,
    *,
    reason_code: ReasonCode,
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
    for ir in session.scalars(
        sa.select(IngestionRun).where(IngestionRun.status == "running")
    ).all():
        ir.status = "failed"
        ir.finished_at = now
        note = (ir.notes or "").strip()
        ir.notes = (note + " " if note else "") + f"marked_failed:{reason_code}"

    if create_summary_alert and ids:
        tag, body = _OPS_BODY[reason_code]
        id_part = ", ".join(str(i) for i in ids[:40])
        if len(ids) > 40:
            id_part += f", … (+{len(ids) - 40} more)"
        summary = f"{body} Count={len(ids)}. Run ids: {id_part}"
        session.add(
            PipelineAlert(
                level="warning",
                message=tagged_message(tag, summary),
                ingestion_run_id=None,
            )
        )
    session.flush()
    return ids
