"""CropAttribute ORM — uniform attributes layer (Canon §4, migration 058).

Parallel to CropFieldEnrichment for T2/T3 categorical + list attributes.
Mirrors the same provenance shape so consumers read one uniform contract.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, Text, TIMESTAMP, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

from organic_market_agent.db.base import Base

if TYPE_CHECKING:
    from organic_market_agent.crop_book.models import CropVariety

# SQLite-safe JSONB (uses Text on SQLite)
from sqlalchemy import JSON as _JSON

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

try:
    from sqlalchemy.dialects.postgresql import JSONB as _JSONB_TYPE
    _JSONB_COLUMN = _JSONB_TYPE().with_variant(_JSON(), "sqlite")
except Exception:
    _JSONB_COLUMN = _JSON()


class CropAttribute(Base):
    """Per-(variety, attribute) categorical/list consensus row.

    Canon §4 — uniform attributes layer.
    Mirrors CropFieldEnrichment for consistent consumer shape:
        T2 (single): value_canonical (str)
        T3 (list):   value_list (jsonb array of ints/strings)
    """

    __tablename__ = "crop_attribute"
    __table_args__ = (
        UniqueConstraint("variety_id", "attribute_name", name="uq_ca_variety_attribute"),
    )

    id: Mapped[int] = mapped_column(
        _PK_TYPE, primary_key=True, autoincrement=True
    )
    variety_id: Mapped[int] = mapped_column(
        _PK_TYPE,
        ForeignKey("crop_varieties.id", name="fk_ca_variety_id", ondelete="CASCADE"),
        nullable=False,
    )
    attribute_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    value_canonical: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="T2: one canonical enum token; NULL for list attributes",
    )
    value_list: Mapped[Optional[Any]] = mapped_column(
        _JSONB_COLUMN, nullable=True,
        doc="T3: ordered array of canonical tokens (int[] for months, str[] for others)",
    )
    winning_source_class: Mapped[Optional[str]] = mapped_column(
        VARCHAR(20), nullable=True,
        doc="EX|NI|PR|WR|OP|MK|WB|UC — class of the winning source",
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True,
        doc="0..1 (1 = single authoritative source; lower = contested)",
    )
    source_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
        doc="Number of distinct sources that provided a candidate",
    )
    candidates: Mapped[Optional[Any]] = mapped_column(
        _JSONB_COLUMN, nullable=True,
        doc="Provenance audit: {source_label: value} mapping for drill-down",
    )
    computed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    variety: Mapped["CropVariety"] = relationship(
        "CropVariety", back_populates="attributes"
    )

    def __repr__(self) -> str:
        return (
            f"<CropAttribute variety_id={self.variety_id} "
            f"attr={self.attribute_name!r} canonical={self.value_canonical!r} "
            f"list={self.value_list} conf={self.confidence_score}>"
        )
