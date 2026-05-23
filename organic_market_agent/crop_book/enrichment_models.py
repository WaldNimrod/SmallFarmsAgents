"""CropFieldEnrichment ORM — per-field consensus + confidence (migration 041).

Separate from models.py (LOD500_LOCKED) per LOD400 §6.
GCR_1: back-reference `CropVariety.enrichments` is added to models.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base

if TYPE_CHECKING:
    from organic_market_agent.crop_book.models import CropVariety

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")


class CropFieldEnrichment(Base):
    """Per-(variety, field) consensus row computed by enrichment_runner."""

    __tablename__ = "crop_field_enrichment"

    id: Mapped[int] = mapped_column(
        _PK_TYPE, primary_key=True, autoincrement=True
    )
    variety_id: Mapped[int] = mapped_column(
        _PK_TYPE,
        ForeignKey("crop_varieties.id", name="fk_cfe_variety_id", ondelete="CASCADE"),
        nullable=False,
    )
    field_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    value_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    value_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    value_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    source_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    winning_source_class: Mapped[Optional[str]] = mapped_column(
        VARCHAR(20), nullable=True
    )
    computed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    variety: Mapped["CropVariety"] = relationship(
        "CropVariety", back_populates="enrichments"
    )

    def __repr__(self) -> str:
        return (
            f"<CropFieldEnrichment variety_id={self.variety_id} "
            f"field={self.field_name!r} best={self.value_best} "
            f"conf={self.confidence_score}>"
        )
