"""Idan seedlings succession importer (L05a + L05b) — WP-C3 §7.

Derives succession_interval_weeks per crop from bi-weekly tray order trackers.
Target: crop_variety_source_values with source='OP:Idan_seedlings'
"""

from __future__ import annotations

import logging
import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Sequence

import openpyxl
from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.israeli._shared import (
    ImportSummary,
    resolve_crop_id,
)

logger = logging.getLogger(__name__)

SOURCE = "OP:Idan_seedlings"
TRUST = "OP"
CONFIDENCE = Decimal("0.55")

# Cells that indicate a real seedling order (non-empty, not header)
_ORDER_MARKERS = frozenset({"מגש", "חצי מגש", "½ מגש", "מגש מלא", "80 שתילים", "160 שתילים"})

_REPO_ROOT = Path(__file__).resolve().parents[4]
_EXTERNAL_SOURCES_DIR = _REPO_ROOT / "data" / "external_sources"


def _parse_date_header(raw: object, fallback_year: int) -> date | None:
    """Parse column header like '18/9', '2.10', '22.3', or a float like 23.8."""
    if raw is None:
        return None
    # numeric float from Excel (e.g. 23.8 = 23rd of August)
    if isinstance(raw, (int, float)):
        s = f"{raw:.1f}"
        m = re.match(r"^(\d+)\.(\d+)$", s)
        if m:
            day, month = int(m.group(1)), int(m.group(2))
            if 1 <= day <= 31 and 1 <= month <= 12:
                try:
                    return date(fallback_year, month, day)
                except ValueError:
                    return None
        return None
    raw_str = str(raw).strip()
    # Try DD/MM or D/M
    m = re.match(r"^(\d{1,2})[/.](\d{1,2})$", raw_str)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        if 1 <= day <= 31 and 1 <= month <= 12:
            try:
                return date(fallback_year, month, day)
            except ValueError:
                return None
    return None


def _is_order(cell: object) -> bool:
    if cell is None:
        return False
    cell_str = str(cell).strip()
    if not cell_str:
        return False
    # Any non-empty non-None cell counts (could be "מגש", "מגש+", number, etc.)
    return True


def _derive_intervals_from_xlsx(
    xlsx_path: Path, season_start_year: int
) -> dict[str, list[date]]:
    """Return {crop_name_he: sorted list of order dates} from one workbook."""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    crop_dates: dict[str, list[date]] = {}

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return crop_dates

    # Find header row (contains 'גידול')
    header_row_idx = None
    for i, row in enumerate(rows):
        if row and row[0] == "גידול":
            header_row_idx = i
            break
    if header_row_idx is None:
        return crop_dates

    header = rows[header_row_idx]
    # Parse date columns (skip col 0 = 'גידול')
    col_dates: list[date | None] = [None]  # col 0 placeholder
    for h in header[1:]:
        parsed = _parse_date_header(h, season_start_year)
        col_dates.append(parsed)

    for row in rows[header_row_idx + 1:]:
        if not row or row[0] is None:
            continue
        crop_he = str(row[0]).strip()
        if not crop_he:
            continue
        dates_for_crop: list[date] = []
        for col_idx, cell in enumerate(row[1:], start=1):
            if _is_order(cell) and col_idx < len(col_dates) and col_dates[col_idx]:
                dates_for_crop.append(col_dates[col_idx])
        if dates_for_crop:
            crop_dates.setdefault(crop_he, []).extend(dates_for_crop)

    return crop_dates


def derive_succession_intervals(xlsx_paths: Sequence[Path]) -> dict[str, int]:
    """Derive median succession interval (weeks) per crop from L05a + L05b.

    L05a covers winter 18-19 (Sep 2018 – Feb 2019).
    L05b covers summer 18-19 (Mar 2019 – Aug 2019).
    Returns {crop_name_he: median_weeks} for crops with ≥2 orders.
    """
    combined: dict[str, list[date]] = {}

    start_years = [2018, 2019]  # L05a starts Sep 2018; L05b starts Mar 2019
    for path, start_year in zip(xlsx_paths, start_years):
        if not path.exists():
            logger.warning("Seedlings file not found: %s", path)
            continue
        crop_dates = _derive_intervals_from_xlsx(path, start_year)
        for crop, dates in crop_dates.items():
            combined.setdefault(crop, []).extend(dates)

    result: dict[str, int] = {}
    for crop_he, dates in combined.items():
        sorted_dates = sorted(set(dates))
        if len(sorted_dates) < 2:
            continue
        diffs: list[float] = []
        for i in range(1, len(sorted_dates)):
            delta = (sorted_dates[i] - sorted_dates[i - 1]).days / 7.0
            diffs.append(delta)
        median_weeks = int(round(median(diffs)))
        if median_weeks > 0:
            result[crop_he] = median_weeks

    return result


def _get_or_create_variety_id(session: Session, crop_id: int) -> int:
    from organic_market_agent.crop_book.models import CropVariety

    v = (
        session.query(CropVariety)
        .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
        .order_by(CropVariety.id)
        .first()
    )
    if v is None:
        v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
        session.add(v)
        session.flush()
    return v.id


def import_all(
    session: Session,
    xlsx_paths: Sequence[Path] | None = None,
) -> ImportSummary:
    if xlsx_paths is None:
        xlsx_paths = [
            _EXTERNAL_SOURCES_DIR / "israeli" / "L05a_IDAN_seedlings_winter_18-19.xlsx",
            _EXTERNAL_SOURCES_DIR / "israeli" / "L05b_IDAN_seedlings_summer_18-19.xlsx",
        ]

    summary = ImportSummary()
    intervals = derive_succession_intervals(xlsx_paths)
    summary.rows_parsed = len(intervals)

    from organic_market_agent.crop_book.models import CropVarietySourceValue

    for crop_he, weeks in intervals.items():
        crop_id, canonical = resolve_crop_id(session, crop_he)
        if crop_id is None:
            summary.map_misses.append(crop_he)
            continue
        variety_id = _get_or_create_variety_id(session, crop_id)

        row = (
            session.query(CropVarietySourceValue)
            .filter_by(variety_id=variety_id, field_name="succession_interval_weeks", source=SOURCE)
            .one_or_none()
        )
        if row is None:
            row = CropVarietySourceValue(
                variety_id=variety_id,
                field_name="succession_interval_weeks",
                source=SOURCE,
            )
            session.add(row)
        row.value_numeric = Decimal(weeks)
        row.value_text = str(weeks)
        row.unit = "weeks"
        row.trust_tier = TRUST
        row.confidence_weight = CONFIDENCE
        row.is_outlier_rejected = False
        session.flush()
        summary.rows_upserted += 1

    logger.info(
        "Idan seedlings: intervals=%d upserted=%d map_misses=%d",
        summary.rows_parsed, summary.rows_upserted, len(summary.map_misses),
    )
    return summary
