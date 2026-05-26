"""CropCoverCrop ORM — cover crop reference chart (migration 050).

SFA-S003-P002-WP-C1 LOD400 §3.2. Standalone from market-vegetable crops table.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Integer, Numeric, Text, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

CATEGORY_VALUES: tuple[str, ...] = ("legume", "cereal", "brassica", "other")


class CropCoverCrop(Base):
    __tablename__ = "crop_cover_crops"
    __table_args__ = (
        UniqueConstraint("name_en", "source", name="uq_ccc_name_source"),
        CheckConstraint(
            "category IN ('legume','cereal','brassica','other')",
            name="ck_ccc_category",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    name_he: Mapped[Optional[str]] = mapped_column(VARCHAR(60), nullable=True)
    category: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    total_days_garden: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    germination_temp_c_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1), nullable=True,
    )
    hardiness_zone: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sow_window: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inoculum: Mapped[Optional[str]] = mapped_column(VARCHAR(80), nullable=True)
    survives_winter: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<CropCoverCrop {self.name_en!r} category={self.category}>"
