"""scheduler_config and pipeline_alerts (M6 automation)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base


class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"
    __table_args__ = (
        CheckConstraint("run_hour >= 0 AND run_hour <= 23", name="chk_sc_run_hour"),
        CheckConstraint("run_minute >= 0 AND run_minute <= 59", name="chk_sc_run_minute"),
        CheckConstraint(
            "retry_attempts >= 0 AND retry_attempts <= 10",
            name="chk_sc_retry_attempts",
        ),
        CheckConstraint("cleanup_after_days >= 7", name="chk_sc_cleanup_after_days"),
    )

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    run_hour: Mapped[int] = mapped_column(Integer, nullable=False, server_default="6")
    run_minute: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    retry_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="2")
    cleanup_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    cleanup_after_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="90")
    cleanup_last_run: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    upload_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PipelineAlert(Base):
    __tablename__ = "pipeline_alerts"
    __table_args__ = (
        CheckConstraint(
            "level IN ('info', 'warning', 'error')",
            name="chk_pa_level",
        ),
    )

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        BigInteger(),
        ForeignKey("ingestion_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    level: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
