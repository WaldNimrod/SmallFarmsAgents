"""CropCompanionMatrix ORM — companion planting pairs (migration 051).

SFA-S003-P002-WP-C4 LOD400 §3.2. Separate from models.py (LOD500_LOCKED).
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, CheckConstraint, ForeignKey, Integer, Text, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

COMPATIBILITY_VALUES: tuple[str, ...] = ("beneficial", "neutral", "antagonistic")
EVIDENCE_VALUES: tuple[str, ...] = ("strong", "weak", "anecdotal")


class CropCompanionMatrix(Base):
    __tablename__ = "crop_companion_matrix"
    __table_args__ = (
        UniqueConstraint("crop_a_id", "crop_b_id", "source", name="uq_ccm"),
        CheckConstraint(
            "compatibility IN ('beneficial','neutral','antagonistic')",
            name="ck_ccm_compat",
        ),
        CheckConstraint("crop_a_id != crop_b_id", name="ck_ccm_no_self"),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_a_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False,
    )
    crop_b_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False,
    )
    compatibility: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    evidence_strength: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"<CropCompanionMatrix {self.crop_a_id}-{self.crop_b_id} "
            f"{self.compatibility} source={self.source!r}>"
        )
