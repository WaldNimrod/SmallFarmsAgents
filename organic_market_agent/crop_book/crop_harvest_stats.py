"""CropHarvestStat ORM — per-(crop, season, year, source) aggregates.

SFA-S003-P002-WP-B3 LOD400 §4. Mirrors the WP-A/B1 pattern of putting
new tables in their own module rather than touching LOD500_LOCKED models.py.
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, CheckConstraint, ForeignKey, Integer, Numeric, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

SEASON_VALUES: tuple[str, ...] = ("spring", "summer", "fall", "winter")


class CropHarvestStat(Base):
    __tablename__ = "crop_harvest_stats"
    __table_args__ = (
        UniqueConstraint("crop_id", "season", "year", "source",
                         name="uq_chs_crop_season_year_source"),
        CheckConstraint(
            "season IN ({})".format(",".join(repr(v) for v in SEASON_VALUES)),
            name="ck_chs_season",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    season: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    cycles_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    peak_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yield_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    yield_unit: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    yield_per_bed_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    yield_per_bed_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    yield_per_bed_median: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                  default=datetime.utcnow)

    def __repr__(self) -> str:
        return (f"<CropHarvestStat crop_id={self.crop_id} {self.season} {self.year} "
                f"cycles={self.cycles_count} source={self.source!r}>")
