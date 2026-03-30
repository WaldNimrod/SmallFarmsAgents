"""sources and source_fetch_profiles tables."""
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
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


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = (
        CheckConstraint(
            "source_group IN ('direct_price','basket_csa','discovery','benchmark','verification')",
            name="chk_src_source_group",
        ),
        CheckConstraint(
            "market_scope IN ('community','benchmark','verification')",
            name="chk_src_market_scope",
        ),
        CheckConstraint(
            "sales_channel IN ("
            "'community_direct','csa_basket','farm_shop','farmers_market',"
            "'retail_chain_benchmark','discovery_only','verification_only')",
            name="chk_src_sales_channel",
        ),
        CheckConstraint(
            "status IN ('active','candidate','deprecated','discovery_only')",
            name="chk_src_status",
        ),
        CheckConstraint("priority BETWEEN 1 AND 10", name="chk_src_priority"),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    source_group: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="candidate")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
    legal_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    legal_review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    source_tier: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    fetch_profiles: Mapped[list["SourceFetchProfile"]] = relationship(
        "SourceFetchProfile", back_populates="source"
    )

    def __repr__(self) -> str:
        return f"<Source code={self.code!r} name={self.name!r}>"


class SourceFetchProfile(Base):
    __tablename__ = "source_fetch_profiles"
    __table_args__ = (
        CheckConstraint(
            "fetch_mode IN ('html_page','json_endpoint','pdf_download','rss','directory_page')",
            name="chk_sfp_fetch_mode",
        ),
        CheckConstraint(
            "schedule_kind IN ('daily','weekly','manual_check')",
            name="chk_sfp_schedule_kind",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    platform_family: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    fetch_mode: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    entry_url: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    http_method: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, server_default="GET")
    request_headers_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    schedule_kind: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="daily")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")
    retry_policy_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=sa.text("'{\"max_retries\": 2, \"backoff_seconds\": 60}'::jsonb"),
    )
    is_public_access: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    charset_hint: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    selector_profile: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    source: Mapped["Source"] = relationship("Source", back_populates="fetch_profiles")
