"""daily_aggregates and weekly_snapshots tables."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base


class DailyAggregate(Base):
    __tablename__ = "daily_aggregates"
    __table_args__ = (
        UniqueConstraint(
            "aggregate_date",
            "product_id",
            "market_scope",
            "sales_channel",
            name="uq_daily_aggregate",
        ),
        CheckConstraint(
            "market_scope IN ('community','benchmark')",
            name="chk_da_market_scope",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    aggregate_date: Mapped[date] = mapped_column(Date, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    is_basket_aggregate: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    distinct_sources: Mapped[int] = mapped_column(Integer, nullable=False)
    min_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    unweighted_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    weighted_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    median_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    stddev_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    normalized_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    meets_publish_threshold: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    last_observed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class WeeklySnapshot(Base):
    __tablename__ = "weekly_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "week_start_date",
            "product_id",
            "market_scope",
            "sales_channel",
            name="uq_weekly_snapshot",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    week_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    distinct_sources: Mapped[int] = mapped_column(Integer, nullable=False)
    data_completeness_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    week_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    week_weighted_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    week_median_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    week_stddev_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    week_min_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    week_max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    normalized_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    snapshot_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
