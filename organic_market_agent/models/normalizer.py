"""normalizer_profiles and normalizer_rules tables."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Text,
    VARCHAR,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base


class NormalizerProfile(Base):
    __tablename__ = "normalizer_profiles"
    __table_args__ = (
        CheckConstraint(
            "normalizer_type IN ("
            "'easyfarm_catalog','simple_product_grid','basket_only',"
            "'retail_benchmark','official_wholesale')",
            name="chk_np_normalizer_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    normalizer_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    version: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, server_default="1.0")
    config_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    rules: Mapped[list["NormalizerRule"]] = relationship(
        "NormalizerRule", back_populates="profile"
    )


class NormalizerRule(Base):
    __tablename__ = "normalizer_rules"
    __table_args__ = (
        CheckConstraint(
            "rule_kind IN ("
            "'product_alias','unit_map','quantity_parse','organic_flag',"
            "'ignore_pattern','benchmark_tag','basket_parse','price_correction')",
            name="chk_nr_rule_kind",
        ),
        CheckConstraint(
            "match_type IN ('exact','regex','contains','prefix')",
            name="chk_nr_match_type",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    normalizer_profile_id: Mapped[int] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=False
    )
    rule_kind: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    match_pattern: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    match_type: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, server_default="exact")
    replacement_value: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    extra_params_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, server_default="system")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile: Mapped["NormalizerProfile"] = relationship("NormalizerProfile", back_populates="rules")
