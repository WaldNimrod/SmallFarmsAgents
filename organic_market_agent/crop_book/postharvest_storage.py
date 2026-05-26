"""CropPostharvestStorage ORM — postharvest conditions (migration 052).

SFA-S003-P002-WP-C4 LOD400 §3.3. Separate from models.py (LOD500_LOCKED).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, ForeignKey, Integer, Numeric, Text, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")


class CropPostharvestStorage(Base):
    __tablename__ = "crop_postharvest_storage"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", name="uq_cps_crop_source"),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False,
    )
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    storage_temp_c_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1), nullable=True,
    )
    storage_temp_c_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1), nullable=True,
    )
    rh_pct_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rh_pct_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    freezing_point_c: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1), nullable=True,
    )
    ethylene_production: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    ethylene_sensitivity: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    storage_life_days_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    storage_life_days_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<CropPostharvestStorage crop_id={self.crop_id} "
            f"source={self.source!r}>"
        )
