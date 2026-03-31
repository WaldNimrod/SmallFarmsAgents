"""Admin queues: future catalog ideas and aliases awaiting approval."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base

if TYPE_CHECKING:
    from organic_market_agent.models.products import Product


class ProductCatalogSuggestion(Base):
    """Proposed catalog entries — no automatic insert into `products` (project policy)."""

    __tablename__ = "product_catalog_suggestions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="chk_pcs_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    canonical_name_he: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    proposed_code: Mapped[Optional[str]] = mapped_column(VARCHAR(32), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PendingProductAlias(Base):
    """Alias proposals; approve copies row into `product_aliases`."""

    __tablename__ = "pending_product_aliases"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="chk_ppa_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    alias_text: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    alias_text_normalized: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="pending")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    product: Mapped["Product"] = relationship("Product", foreign_keys=[product_id])
