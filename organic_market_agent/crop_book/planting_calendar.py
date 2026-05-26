"""CropPlantingCalendar ORM — monthly planting matrix (migration 049).

SFA-S003-P002-WP-C1 LOD400 §3.1. Separate from models.py (LOD500_LOCKED).

Region conventions (WP-C4 LOD400 §3.1 — free-text ``region`` column, not enforced):
  - ``IL_general`` — default Israel (NI:il_moa_garden_guide, NI:shaham_extension)
  - ``IL_north`` / ``IL_center`` / ``IL_south`` — zone-specific overlays
  - ``MED_general`` — Mediterranean climate reference
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, Text, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

ACTIVITY_TYPES: tuple[str, ...] = ("seed", "transplant", "both")
SEASON_VALUES: tuple[str, ...] = ("spring", "summer", "fall", "winter", "all")

MONTH_COLUMNS: tuple[str, ...] = (
    "month_jan", "month_feb", "month_mar", "month_apr",
    "month_may", "month_jun", "month_jul", "month_aug",
    "month_sep", "month_oct", "month_nov", "month_dec",
)


class CropPlantingCalendar(Base):
    __tablename__ = "crop_planting_calendar"
    __table_args__ = (
        UniqueConstraint(
            "crop_id", "source", "activity_type",
            name="uq_cpc_crop_source_activity",
        ),
        CheckConstraint(
            "activity_type IN ('seed','transplant','both')",
            name="ck_cpc_activity_type",
        ),
        CheckConstraint(
            "season IS NULL OR season IN ('spring','summer','fall','winter','all')",
            name="ck_cpc_season",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False,
    )
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    activity_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    season: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    month_jan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_feb: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_mar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_apr: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_may: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_jun: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_jul: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_aug: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_sep: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_oct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_nov: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    month_dec: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<CropPlantingCalendar crop_id={self.crop_id} "
            f"source={self.source!r} activity={self.activity_type}>"
        )
