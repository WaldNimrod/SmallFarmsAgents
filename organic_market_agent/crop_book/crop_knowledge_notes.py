"""CropKnowledgeNote ORM — per-crop NI narrative (migration 045).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §4. Mirrors WP-A/B1/B3 pattern.
Internal use only — see §3.1 OPERATIVE LICENSING INVARIANT.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    TIMESTAMP,
    Text,
    UniqueConstraint,
    VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

NOTE_TYPE_VALUES: tuple[str, ...] = (
    "pest_disease",
    "harvest_marker",
    "storage_handling",
    "rotation_companion",
    "cultivar_recommendation",
    "growing_tip",
    "irrigation",
    "nursery_specific",
    "flame_weed_timing",
    "biopesticide_spray",
    "phytoprotection_substance",
    "phytoprotection_application",
    "nursery_seeding_process",
)
# 13 values total: 8 JMF book types + 2 FT baseline + 3 Q5 additions.

BODY_TEXT_MAX_LENGTH: int = 2000


class CropKnowledgeNote(Base):
    __tablename__ = "crop_knowledge_notes"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", "note_type", name="uq_ckn_crop_source_type"),
        CheckConstraint(
            "note_type IN ({})".format(",".join(repr(v) for v in NOTE_TYPE_VALUES)),
            name="ck_ckn_note_type",
        ),
        CheckConstraint(
            f"length(body_text) <= {BODY_TEXT_MAX_LENGTH}",
            name="ck_ckn_body_text_length",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    note_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_pdf: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    provenance_pages: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    is_internal_farm_use_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    extraction_model: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    extracted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    # patch04: many-to-many link via junction table (Migration 047)
    # secondary= references 'crop_knowledge_notes_crops' Table object from crop_knowledge_notes_crops module
    crops_linked: Mapped[list] = relationship(
        'Crop',
        secondary='crop_knowledge_notes_crops',
        back_populates='knowledge_notes_linked',
    )

    def __repr__(self) -> str:
        return (
            f"<CropKnowledgeNote crop_id={self.crop_id} type={self.note_type!r} "
            f"source={self.source!r} len(body)={len(self.body_text)}>"
        )
