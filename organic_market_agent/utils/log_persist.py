"""Persist structured rows to log_entries (errors + pipeline diagnostics)."""
from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.models import LogEntry

_VALID_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def persist_log(
    session: Session,
    *,
    level: str,
    module: str,
    message: str,
    ingestion_run_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """Insert one log_entries row (caller commits)."""
    lv = (level or "INFO").upper()
    if lv not in _VALID_LEVELS:
        lv = "INFO"
    session.add(
        LogEntry(
            level=lv,
            module=(module or "unknown")[:60],
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
            extra_json=extra,
            ingestion_run_id=ingestion_run_id,
        )
    )


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
    persist_log(
        session,
        level="ERROR",
        module=module,
        message=message,
        ingestion_run_id=ingestion_run_id,
        entity_type=entity_type,
        entity_id=entity_id,
        extra=extra,
    )
