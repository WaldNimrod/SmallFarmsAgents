"""Persist ingestion_run.progress_json for admin progress UI."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun


def merge_run_progress(session: Session, ingestion_run_id: int, **fields: Any) -> None:
    """Merge fields into ingestion_runs.progress_json and flush (caller commits)."""
    run = session.get(IngestionRun, ingestion_run_id)
    if run is None:
        return
    base: dict[str, Any] = dict(run.progress_json or {})
    for k, v in fields.items():
        if v is None and k in base:
            del base[k]
        elif v is not None:
            base[k] = v
    base["updated_at"] = datetime.now(timezone.utc).isoformat()
    run.progress_json = base
    session.flush()
