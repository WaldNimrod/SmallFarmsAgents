"""Persist ERROR-level messages to log_entries (Team 10 onboarding)."""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.models import LogEntry


def persist_error_log(
    session: Session,
    *,
    module: str,
    message: str,
    ingestion_run_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    session.add(
        LogEntry(
            level="ERROR",
            module=module[:60],
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            extra_json=extra,
            ingestion_run_id=ingestion_run_id,
        )
    )
