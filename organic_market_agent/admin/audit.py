"""Append-only audit trail for admin write actions."""
from __future__ import annotations

from typing import Any

from flask_login import current_user
from sqlalchemy.orm import Session

from organic_market_agent.models.users import AuditLog


def audit_write(
    session: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    notes: str | None = None,
) -> None:
    """Insert one audit_log row. Caller must commit the session."""
    user_id = (
        int(current_user.get_id())
        if current_user.is_authenticated
        else None
    )
    actor = (
        (getattr(current_user, "display_name", None) or getattr(current_user, "email", None))
        if current_user.is_authenticated
        else "system"
    )
    session.add(
        AuditLog(
            user_id=user_id,
            actor_name=actor or "system",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before,
            after_state=after,
            notes=notes,
        )
    )
