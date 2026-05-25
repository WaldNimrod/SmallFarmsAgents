"""ספר גידולים — SQLAlchemy ORM models for the 6 crop-book tables."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    VARCHAR,
)

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base

if TYPE_CHECKING:
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment


class CropFamily(Base):
    __tablename__ = "crop_families"

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    scientific_name: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, unique=True)
    name_he: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)

    crops: Mapped[list["Crop"]] = relationship("Crop", back_populates="family")

    def __repr__(self) -> str:
        return f"<CropFamily scientific_name={self.scientific_name!r}>"


class CropConversionGroup(Base):
    __tablename__ = "crop_conversion_groups"

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    crops: Mapped[list["Crop"]] = relationship("Crop", back_populates="conversion_group")
    conversions: Mapped[list["CropUnitConversion"]] = relationship(
        "CropUnitConversion",
        foreign_keys="CropUnitConversion.conversion_group_id",
        back_populates="conversion_group",
    )

    def __repr__(self) -> str:
        return f"<CropConversionGroup name={self.name!r}>"


class Crop(Base):
    __tablename__ = "crops"
    __table_args__ = (
        CheckConstraint(
            "category IN ('vegetables','herbs','baby','legumes','fruits','fruit_trees','grains','cover_crops')",
            name="chk_crops_category",
        ),
        CheckConstraint(
            "growth_cycle IS NULL OR growth_cycle IN ('annual','biennial','perennial')",
            name="chk_crops_growth_cycle",
        ),
        CheckConstraint(
            "harvest_unit_default IS NULL OR harvest_unit_default IN ('kg','bunch','head','case','unit','seedling')",
            name="chk_crops_harvest_unit_default",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    name_he: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, unique=True)
    name_en: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("crop_families.id", name="fk_crops_family_id"), nullable=False
    )
    category: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    growth_cycle: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    harvest_unit_default: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    first_fruit_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    conversion_group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("crop_conversion_groups.id", name="fk_crops_conversion_group_id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    oma_product_id: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)

    family: Mapped["CropFamily"] = relationship("CropFamily", back_populates="crops")
    conversion_group: Mapped[Optional["CropConversionGroup"]] = relationship(
        "CropConversionGroup", back_populates="crops"
    )
    varieties: Mapped[list["CropVariety"]] = relationship("CropVariety", back_populates="crop")
    # patch04: many-to-many back-ref for cross-crop knowledge notes (Migration 047)
    knowledge_notes_linked: Mapped[list] = relationship(
        "CropKnowledgeNote",
        secondary="crop_knowledge_notes_crops",
        back_populates="crops_linked",
    )
    unit_conversions: Mapped[list["CropUnitConversion"]] = relationship(
        "CropUnitConversion",
        foreign_keys="CropUnitConversion.crop_id",
        back_populates="crop",
    )

    def __repr__(self) -> str:
        return f"<Crop name_he={self.name_he!r}>"


class CropVariety(Base):
    __tablename__ = "crop_varieties"
    __table_args__ = (
        CheckConstraint(
            "planting_method IS NULL OR planting_method IN ('direct_sow','transplant','greenhouse_transplant','cutting','purchase')",
            name="chk_cv_planting_method",
        ),
        CheckConstraint(
            "harvest_stage IS NULL OR harvest_stage IN ('full_size','baby_leaf','head','plant_sale','seed')",
            name="chk_cv_harvest_stage",
        ),
        CheckConstraint(
            "harvest_unit IS NULL OR harvest_unit IN ('kg','bunch','head','case','unit','seedling')",
            name="chk_cv_harvest_unit",
        ),
        UniqueConstraint("crop_id", "name_en", name="uq_cv_crop_name_en"),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        ForeignKey("crops.id", name="fk_cv_crop_id"), nullable=False
    )
    name_en: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    name_he: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_grafted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    rootstock_variety: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    planting_method: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    days_to_maturity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    harvest_window_min_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    harvest_window_max_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    in_row_spacing_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    rows_per_bed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    planting_season: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    succession_interval_weeks: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    harvest_unit: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    avg_yield_per_bed_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    yield_source: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    documented_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    documented_price_unit: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    documented_price_source: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    pricebook_product_id: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    avg_revenue_per_bed_m: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    days_to_germinate_gh: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_in_gh_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seeder: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    seeder_front_gear: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    seeder_rear_gear: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    seeder_roller_plate: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    harvest_stage: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    crop: Mapped["Crop"] = relationship("Crop", back_populates="varieties")
    source_values: Mapped[list["CropVarietySourceValue"]] = relationship(
        "CropVarietySourceValue", back_populates="variety", cascade="all, delete-orphan"
    )
    # GCR_1 — back-reference to enrichment consensus rows (migration 041)
    enrichments: Mapped[list["CropFieldEnrichment"]] = relationship(
        "CropFieldEnrichment", back_populates="variety", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CropVariety crop_id={self.crop_id} name_en={self.name_en!r}>"


class CropVarietySourceValue(Base):
    __tablename__ = "crop_variety_source_values"

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    variety_id: Mapped[int] = mapped_column(
        ForeignKey("crop_varieties.id", name="fk_cvsv_variety_id", ondelete="CASCADE"),
        nullable=False,
    )
    field_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    value_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_numeric: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # GCR_1 — migration 042 additive columns
    trust_tier: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    confidence_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    is_outlier_rejected: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    variety: Mapped["CropVariety"] = relationship("CropVariety", back_populates="source_values")

    def __repr__(self) -> str:
        return f"<CropVarietySourceValue variety_id={self.variety_id} field={self.field_name!r} source={self.source!r}>"


class CropUnitConversion(Base):
    __tablename__ = "crop_unit_conversions"
    __table_args__ = (
        CheckConstraint(
            "(conversion_group_id IS NOT NULL AND crop_id IS NULL) OR "
            "(conversion_group_id IS NULL AND crop_id IS NOT NULL)",
            name="chk_cuc_exclusion",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    conversion_group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("crop_conversion_groups.id", name="fk_cuc_conversion_group_id", ondelete="CASCADE"),
        nullable=True,
    )
    crop_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("crops.id", name="fk_cuc_crop_id", ondelete="CASCADE"),
        nullable=True,
    )
    source_unit: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    target_unit: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    conversion_factor: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    context: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    source: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    conversion_group: Mapped[Optional["CropConversionGroup"]] = relationship(
        "CropConversionGroup", back_populates="conversions"
    )
    crop: Mapped[Optional["Crop"]] = relationship("Crop", back_populates="unit_conversions")

    def __repr__(self) -> str:
        return (
            f"<CropUnitConversion {self.source_unit!r}→{self.target_unit!r} "
            f"×{self.conversion_factor}>"
        )
