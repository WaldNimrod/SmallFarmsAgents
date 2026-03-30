"""normalized_observations and observation_flags tables."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base


class NormalizedObservation(Base):
    __tablename__ = "normalized_observations"
    __table_args__ = (
        CheckConstraint(
            "market_scope IN ('community','benchmark','verification')",
            name="chk_no_market_scope",
        ),
        CheckConstraint(
            "sales_channel IN ("
            "'community_direct','csa_basket','farm_shop','farmers_market',"
            "'retail_chain_benchmark','discovery_only','verification_only')",
            name="chk_no_sales_channel",
        ),
        CheckConstraint(
            "normalization_method IS NULL OR normalization_method IN ("
            "'direct','unit_conversion_exact','unit_conversion_heuristic',"
            "'basket_composite','unresolvable')",
            name="chk_no_norm_method",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="chk_no_confidence",
        ),
        CheckConstraint(
            "flag_status IN ('ok','review','ignored','hidden')",
            name="chk_no_flag_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    raw_extracted_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("raw_extracted_items.id"), nullable=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id"), nullable=True
    )
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    is_benchmark: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_basket_product: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_organic_claimed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(VARCHAR(3), nullable=False, server_default="ILS")
    display_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    normalized_price_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    normalized_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    normalization_method: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default="1.0")
    flag_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="ok")
    flag_reason: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class ObservationFlag(Base):
    __tablename__ = "observation_flags"
    __table_args__ = (
        CheckConstraint(
            "flag_type IN ('hide','review','price_outlier','wrong_product')",
            name="chk_of_flag_type",
        ),
        CheckConstraint(
            "scope IN ('single','source_product','all_from_source')",
            name="chk_of_scope",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    observation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalized_observations.id"), nullable=True
    )
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    flag_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="single")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, server_default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
