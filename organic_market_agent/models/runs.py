"""ingestion_runs, source_fetch_runs, raw_assets, raw_extracted_items tables."""
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    __table_args__ = (
        CheckConstraint("run_type IN ('daily','manual','retry')", name="chk_ir_run_type"),
        CheckConstraint(
            "status IN ('running','completed','partial','failed')",
            name="chk_ir_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    run_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="daily")
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="running")
    sources_total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sources_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sources_failed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    community_sources_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    triggered_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, server_default="cron")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    source_fetch_runs: Mapped[list["SourceFetchRun"]] = relationship(
        "SourceFetchRun", back_populates="ingestion_run"
    )


class SourceFetchRun(Base):
    __tablename__ = "source_fetch_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running','success','failed','skipped','timeout')",
            name="chk_sfr_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    fetch_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("source_fetch_profiles.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="running")
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bytes_fetched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("raw_assets.id"), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    ingestion_run: Mapped["IngestionRun"] = relationship(
        "IngestionRun", back_populates="source_fetch_runs"
    )


class RawAsset(Base):
    __tablename__ = "raw_assets"
    __table_args__ = (
        CheckConstraint(
            "file_type IN ('html','json','pdf','rss','text','other')",
            name="chk_ra_file_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    file_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    bytes_size: Mapped[int] = mapped_column(Integer, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class RawExtractedItem(Base):
    __tablename__ = "raw_extracted_items"
    __table_args__ = (
        CheckConstraint(
            "extraction_status IN ('extracted','normalized','unresolvable','ignored')",
            name="chk_rei_extraction_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    raw_asset_id: Mapped[int] = mapped_column(ForeignKey("raw_assets.id"), nullable=False)
    normalizer_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=True
    )
    raw_product_name: Mapped[Optional[str]] = mapped_column(VARCHAR(300), nullable=True)
    raw_price_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_unit_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_quantity_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_payload_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    extraction_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="extracted")
    unresolvable_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ignore_reason_code: Mapped[Optional[str]] = mapped_column(VARCHAR(80), nullable=True)
    is_quarantined: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false", default=False)
    extracted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
