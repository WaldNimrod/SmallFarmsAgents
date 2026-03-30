"""measurement_units and unit_conversions tables."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    VARCHAR,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base


class MeasurementUnit(Base):
    __tablename__ = "measurement_units"
    __table_args__ = (
        CheckConstraint(
            "unit_type IN ('weight','count','bundle','basket','pack')",
            name="chk_mu_unit_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, unique=True)
    name_he: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    unit_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    is_normalizable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    conversions_from: Mapped[list["UnitConversion"]] = relationship(
        "UnitConversion", foreign_keys="UnitConversion.from_unit_id", back_populates="from_unit"
    )
    conversions_to: Mapped[list["UnitConversion"]] = relationship(
        "UnitConversion", foreign_keys="UnitConversion.to_unit_id", back_populates="to_unit"
    )

    def __repr__(self) -> str:
        return f"<MeasurementUnit code={self.code!r}>"


class UnitConversion(Base):
    __tablename__ = "unit_conversions"
    __table_args__ = (
        UniqueConstraint("from_unit_id", "to_unit_id", "product_id", name="uq_unit_conversion"),
        CheckConstraint(
            "conversion_type IN ('exact','heuristic','product_specific')",
            name="chk_uc_conversion_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    from_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    to_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    factor: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    conversion_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    from_unit: Mapped["MeasurementUnit"] = relationship(
        "MeasurementUnit", foreign_keys=[from_unit_id], back_populates="conversions_from"
    )
    to_unit: Mapped["MeasurementUnit"] = relationship(
        "MeasurementUnit", foreign_keys=[to_unit_id], back_populates="conversions_to"
    )
