"""products, product_aliases, product_variants, product_merges tables."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from organic_market_agent.models.measurement import MeasurementUnit

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "category IN ("
            "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
            "'alliums','cucurbits','legumes_fresh','baskets')",
            name="chk_p_category",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, unique=True)
    canonical_name_he: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    category: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    default_measurement_unit_id: Mapped[int] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=False
    )
    is_organic_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    is_basket_product: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    seasonality_notes: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    default_unit: Mapped["MeasurementUnit"] = relationship(
        "MeasurementUnit",
        foreign_keys=[default_measurement_unit_id],
    )
    aliases: Mapped[list["ProductAlias"]] = relationship(
        "ProductAlias", back_populates="product"
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product"
    )

    def __repr__(self) -> str:
        return f"<Product code={self.code!r} name={self.canonical_name_he!r}>"


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    variant_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    quantity_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    quantity_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    normalized_base_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    normalized_factor: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 6), nullable=True)
    is_composite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="variants")


class ProductAlias(Base):
    __tablename__ = "product_aliases"
    __table_args__ = (
        UniqueConstraint("alias_text_normalized", "source_id", name="uq_alias_text_source"),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    alias_text: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    alias_text_normalized: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    normalizer_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=True
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="aliases")


class ProductMerge(Base):
    __tablename__ = "product_merges"
    __table_args__ = (
        UniqueConstraint("source_product_id", name="uq_product_merge"),
        CheckConstraint("source_product_id != target_product_id", name="chk_pm_no_self_merge"),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    target_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    merged_by: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
