"""CropContent + CropContentSource ORM — multi-source narrative prose with provenance.

SFA-S003-P004-WP-CB-CONTENT.

Applies the existing attribute-provenance pattern (crop_attribute, migration 058)
to NARRATIVE PROSE. A *content unit* is a (crop, content_type) pair carrying:

    * one consolidated canonical markdown body (Normal mode)  → ``crop_content.text_md``
    * N per-source variants, each with attribution (Deep mode) → ``crop_content_source`` rows

Content is CROP-level (keyed on ``crops.id``, like CropKnowledgeNote), not variety-level.

⚠ LICENSING: every body stored here — canonical AND per-source ``raw_text_md`` — is OUR
own newly-authored Hebrew text (translation/synthesis), never verbatim copyrighted source
text. This table is PUBLIC (published to the delivery tier). It is wholly separate from
``crop_knowledge_notes`` (internal-only, never published). No loader/publisher path reads
``crop_knowledge_notes`` into this table — enforced by test_ni_publisher_isolation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

# Canonical content_type vocabulary for the crop book.
# story            → hero growing-story (supersedes the legacy Crop.description)
# care_watering    → השקיה topic
# care_fertilizing → דישון topic
# care_pests       → מזיקים ומחלות topic
CONTENT_TYPE_VALUES: tuple[str, ...] = (
    "story",
    "care_watering",
    "care_fertilizing",
    "care_pests",
)


class CropContent(Base):
    """Per-(crop, content_type) consolidated canonical prose row (Normal mode).

    Mirrors CropAttribute's provenance columns (winning_source_class / confidence_score /
    source_count) so consumers read one uniform contract. The per-source variants live in
    the child ``crop_content_source`` table (Deep mode) — never discarded.
    """

    __tablename__ = "crop_content"
    __table_args__ = (
        UniqueConstraint("crop_id", "content_type", name="uq_cc_crop_content_type"),
        CheckConstraint(
            "content_type IN ({})".format(",".join(repr(v) for v in CONTENT_TYPE_VALUES)),
            name="ck_cc_content_type",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE,
        ForeignKey("crops.id", name="fk_cc_crop_id", ondelete="CASCADE"),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    text_md: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        doc="Consolidated canonical Hebrew markdown — OUR synthesis (Normal mode)",
    )
    winning_source_class: Mapped[Optional[str]] = mapped_column(
        VARCHAR(20), nullable=True,
        doc="EX|NI|PR|WR|OP|MK|WB|UC — best CLASS_RANK among this unit's sources",
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4), nullable=True,
        doc="0..1 (1 = hard-override source present)",
    )
    source_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
        doc="Number of per-source variants attached to this unit",
    )
    computed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    sources: Mapped[list["CropContentSource"]] = relationship(
        "CropContentSource",
        back_populates="content",
        cascade="all, delete-orphan",
        order_by="CropContentSource.display_order",
    )

    def __repr__(self) -> str:
        return (
            f"<CropContent crop_id={self.crop_id} type={self.content_type!r} "
            f"win={self.winning_source_class!r} n={self.source_count}>"
        )


class CropContentSource(Base):
    """One per-source narrative variant for a content unit (Deep mode).

    ``raw_text_md`` is OUR full Hebrew rendering of that source's take — license-safe,
    never verbatim copyrighted text — accompanied by its attribution (label + class + url).
    """

    __tablename__ = "crop_content_source"
    __table_args__ = (
        UniqueConstraint("content_id", "source_label", name="uq_ccs_content_source"),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    content_id: Mapped[int] = mapped_column(
        _PK_TYPE,
        ForeignKey("crop_content.id", name="fk_ccs_content_id", ondelete="CASCADE"),
        nullable=False,
    )
    source_label: Mapped[str] = mapped_column(
        VARCHAR(100), nullable=False,
        doc="Registry label (e.g. 'JMF', 'NI:groworganic', 'WR:claude_research')",
    )
    source_class: Mapped[str] = mapped_column(
        VARCHAR(20), nullable=False,
        doc="EX|NI|PR|WR|OP|MK|WB|UC — derived from source_registry, never hand-authored",
    )
    raw_text_md: Mapped[str] = mapped_column(
        Text, nullable=False,
        doc="OUR full Hebrew rendering of this source's take (license-safe)",
    )
    source_url: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0",
        doc="Stable Deep-mode ordering — populated from CLASS_RANK at load",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    content: Mapped["CropContent"] = relationship("CropContent", back_populates="sources")

    def __repr__(self) -> str:
        return (
            f"<CropContentSource content_id={self.content_id} "
            f"label={self.source_label!r} cls={self.source_class!r}>"
        )
