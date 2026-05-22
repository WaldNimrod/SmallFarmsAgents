"""users, audit_log, log_entries tables."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin','viewer')", name="chk_u_role"),)

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    role: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, server_default="system")
    action: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(BigInteger(), nullable=True)
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class LogEntry(Base):
    __tablename__ = "log_entries"
    __table_args__ = (
        CheckConstraint(
            "level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')",
            name="chk_le_level",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    module: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(BigInteger(), nullable=True)
    extra_json: Mapped[Optional[dict]] = mapped_column(JSONB().with_variant(JSON(), "sqlite"), nullable=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ingestion_runs.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
