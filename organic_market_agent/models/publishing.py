"""publish_runs and publish_artifacts tables."""
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


class PublishRun(Base):
    __tablename__ = "publish_runs"
    __table_args__ = (
        CheckConstraint("run_type IN ('auto','manual','retry')", name="chk_pr_run_type"),
        CheckConstraint(
            "status IN ("
            "'building','build_failed','uploading','upload_failed',"
            "'published','aborted')",
            name="chk_pr_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ingestion_runs.id"), nullable=True
    )
    run_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="auto")
    build_started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    build_finished_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    upload_started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    upload_finished_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="building")
    artifact_version: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_last_good: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    products_included: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    community_products: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    benchmark_products: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, server_default="auto")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class PublishArtifact(Base):
    __tablename__ = "publish_artifacts"
    __table_args__ = (
        CheckConstraint(
            "artifact_type IN ("
            "'public_json','public_html','manifest_json','manifest_last_good_json')",
            name="chk_pa_artifact_type",
        ),
        CheckConstraint(
            "upload_status IS NULL OR upload_status IN ('pending','uploaded','failed','skipped')",
            name="chk_pa_upload_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    publish_run_id: Mapped[int] = mapped_column(ForeignKey("publish_runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    local_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    bytes_size: Mapped[int] = mapped_column(Integer, nullable=False)
    remote_path: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    upload_status: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True, server_default="pending")
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
