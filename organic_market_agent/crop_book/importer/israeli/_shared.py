"""Shared helpers for WP-C1 Israeli planting-calendar importers."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.constants import resolve_il_crop
from organic_market_agent.crop_book.planting_calendar import (
    MONTH_COLUMNS,
    CropPlantingCalendar,
)

logger = logging.getLogger(__name__)

_SKIP_IL_ROWS = frozenset({
    "ירקות, פירות ושורשים",
    "ירקות,\xa0פירות ושורשים",
    "סיכום",
    "ניתן להוסיף",
    'סה"כ שטח גידול',
    "1023",
    "גידול",
})


@dataclass
class PlantingCalendarRow:
    crop_name_he: str
    activity_type: str
    season: str | None = None
    month_jan: bool = False
    month_feb: bool = False
    month_mar: bool = False
    month_apr: bool = False
    month_may: bool = False
    month_jun: bool = False
    month_jul: bool = False
    month_aug: bool = False
    month_sep: bool = False
    month_oct: bool = False
    month_nov: bool = False
    month_dec: bool = False
    notes: str | None = None

    def month_flags(self) -> dict[str, bool]:
        return {col: getattr(self, col) for col in MONTH_COLUMNS}


def decode_l01_cell(cell: str | None) -> set[str]:
    """Return activity types present in a GROWORGANIC cell (S/X/SX)."""
    raw = (str(cell) if cell is not None else "").strip().upper().replace(".", "")
    if not raw:
        return set()
    if "SX" in raw or "XS" in raw or ("S" in raw and "X" in raw):
        return {"seed", "transplant"}
    out: set[str] = set()
    if "S" in raw:
        out.add("transplant")
    if "X" in raw:
        out.add("seed")
    return out


def decode_bustan_token(token: str | None) -> set[str]:
    """Decode BUSTAN legend token (ז/ש/ש/ז/ז*)."""
    raw = strip_hebrew_markup(token or "")
    if not raw:
        return set()
    cleaned = raw.replace(" ", "")
    has_seed = "ז" in cleaned
    has_trans = "ש" in cleaned
    if has_seed and has_trans:
        return {"seed", "transplant"}
    if has_trans:
        return {"transplant"}
    if has_seed:
        return {"seed"}
    return set()


def merge_month_rows(rows: list[PlantingCalendarRow]) -> list[PlantingCalendarRow]:
    """Merge rows sharing (crop_name_he, activity_type) by OR-ing month flags."""
    merged: dict[tuple[str, str], PlantingCalendarRow] = {}
    for row in rows:
        key = (row.crop_name_he, row.activity_type)
        if key not in merged:
            merged[key] = PlantingCalendarRow(
                crop_name_he=row.crop_name_he,
                activity_type=row.activity_type,
                season=row.season,
                notes=row.notes,
                **row.month_flags(),
            )
        else:
            existing = merged[key]
            for col in MONTH_COLUMNS:
                setattr(existing, col, getattr(existing, col) or getattr(row, col))
    return list(merged.values())


def resolve_crop_id(session: Session, source_name_he: str) -> tuple[int | None, str | None]:
    """Resolve source Hebrew label → (crop_id, canonical name_he)."""
    from organic_market_agent.crop_book.models import Crop

    canonical = resolve_il_crop(source_name_he)
    if canonical is None:
        logger.warning("IL crop unmapped: %r — skipping", source_name_he)
        return None, None
    crop = session.query(Crop).filter_by(name_he=canonical).one_or_none()
    if crop is None:
        logger.warning(
            "IL crop mapped to %r but not in DB — skipping source %r",
            canonical,
            source_name_he,
        )
        return None, canonical
    return crop.id, canonical


def upsert_planting_calendar(
    session: Session,
    crop_id: int,
    row: PlantingCalendarRow,
    *,
    source: str,
    trust_tier: str,
    region: str | None = None,
) -> bool:
    """Upsert on (crop_id, source, activity_type). Returns True if inserted."""
    existing = (
        session.query(CropPlantingCalendar)
        .filter_by(crop_id=crop_id, source=source, activity_type=row.activity_type)
        .one_or_none()
    )
    flags = row.month_flags()
    if existing is None:
        obj = CropPlantingCalendar(
            crop_id=crop_id,
            source=source,
            trust_tier=trust_tier,
            region=region,
            activity_type=row.activity_type,
            season=row.season,
            notes=row.notes,
            **flags,
        )
        session.add(obj)
        session.flush()
        return True
    for col in MONTH_COLUMNS:
        setattr(existing, col, flags[col])
    existing.season = row.season
    existing.notes = row.notes
    session.flush()
    return False


def strip_hebrew_markup(text: str) -> str:
    return re.sub(r"[\u200e\u200f\u202a-\u202e‫‬]", "", text).strip()


@dataclass
class ImportSummary:
    rows_parsed: int = 0
    rows_upserted: int = 0
    map_misses: list[str] = field(default_factory=list)
    db_misses: list[str] = field(default_factory=list)
