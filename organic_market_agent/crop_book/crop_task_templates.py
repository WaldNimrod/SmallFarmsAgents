"""CropTaskTemplate ORM — discrete growing-task rows per crop (migration 044).

SFA-S003-P002-WP-B1 LOD400 §4. Mirrors the WP-A pattern of putting new tables in
their own module rather than touching the LOD500_LOCKED models.py.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, TIMESTAMP, Text,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

# Sentinel value for the `days_offset` column when the source data records
# only task presence (e.g., JMF "X" cells with no integer). NOT NULL on the
# column ensures the (crop_id, source, task_type, days_offset) UNIQUE
# constraint is deterministic on both Postgres and SQLite — see F-S-002 R1.
DAYS_OFFSET_PRESENCE_ONLY: int = -32768


def is_presence_only(days_offset: int) -> bool:
    """Return True if `days_offset` is the presence-only sentinel."""
    return days_offset == DAYS_OFFSET_PRESENCE_ONLY


TASK_TYPE_VALUES: tuple[str, ...] = (
    # ── B1 baseline (14) ──
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
    # ── B3 extensions (6 — added under GCR-B3-1, team_00 approved 2026-05-25) ──
    "nursery_seed", "pest_spray", "potting_up", "thinning",
    "trellis", "fertilize",
)

TIMING_ANCHOR_VALUES: tuple[str, ...] = (
    "seeding", "transplanting", "harvest", "field_prep",
)


class CropTaskTemplate(Base):
    __tablename__ = "crop_task_templates"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", "task_type", "days_offset",
                         name="uq_cct_crop_source_type_offset"),
        CheckConstraint(
            "task_type IN ({})".format(",".join(repr(v) for v in TASK_TYPE_VALUES)),
            name="ck_cct_task_type",
        ),
        CheckConstraint(
            "timing_anchor IS NULL OR timing_anchor IN ({})".format(
                ",".join(repr(v) for v in TIMING_ANCHOR_VALUES)),
            name="ck_cct_timing_anchor",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    task_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    timing_anchor: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    # F-S-002 (R1): NOT NULL + sentinel default. Use `is_presence_only(row.days_offset)`
    # to detect presence-only rows in callers — never compare against -32768 inline.
    days_offset: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DAYS_OFFSET_PRESENCE_ONLY,
        server_default=str(DAYS_OFFSET_PRESENCE_ONLY),
    )
    method: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_material: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False,
                                                  default=datetime.utcnow)

    def __repr__(self) -> str:
        return (f"<CropTaskTemplate crop_id={self.crop_id} task_type={self.task_type!r} "
                f"days_offset={self.days_offset} source={self.source!r}>")
