"""Approved V1 out-of-scope rules: mark raw rows as ignored (not unresolvable)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    Integer,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base


class CatalogScopeSkipRule(Base):
    """Numbered catalog of patterns that are intentionally outside OrganicMarketAgent V1 scope."""

    __tablename__ = "catalog_scope_skip_rules"
    __table_args__ = (
        CheckConstraint(
            "category_code IN ('donation','cleaning','dry_grocery','other')",
            name="chk_cssr_category",
        ),
        CheckConstraint(
            "match_type IN ('exact','prefix','contains','regex')",
            name="chk_cssr_match_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    display_order: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)
    category_code: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    match_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    pattern: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    future_product_code: Mapped[Optional[str]] = mapped_column(VARCHAR(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
