"""GROWORGANIC.INFO sowing calendar importer (L01) — WP-C1 LOD400 §4.1."""

from __future__ import annotations

import logging
from pathlib import Path

import openpyxl
from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.israeli._shared import (
    ImportSummary,
    PlantingCalendarRow,
    _SKIP_IL_ROWS,
    decode_l01_cell,
    merge_month_rows,
    resolve_crop_id,
    upsert_planting_calendar,
)

logger = logging.getLogger(__name__)

SOURCE = "NI:groworganic"
TRUST = "NI"
SHEET = "גיליון1"

# Col D–O (0-based 3–14): Mar … Feb
_L01_MONTH_COLS: list[tuple[str, int]] = [
    ("month_mar", 3),
    ("month_apr", 4),
    ("month_may", 5),
    ("month_jun", 6),
    ("month_jul", 7),
    ("month_aug", 8),
    ("month_sep", 9),
    ("month_oct", 10),
    ("month_nov", 11),
    ("month_dec", 12),
    ("month_jan", 13),
    ("month_feb", 14),
]


def parse_groworganic(xlsx_path: Path) -> list[PlantingCalendarRow]:
    """Parse L01 workbook into planting-calendar rows."""
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[SHEET]
    partial: list[PlantingCalendarRow] = []

    for row in ws.iter_rows(min_row=15, values_only=True):
        name_raw = row[0]
        if not name_raw:
            continue
        name = str(name_raw).strip()
        if name in _SKIP_IL_ROWS:
            continue
        cells = row[3:15] if len(row) >= 15 else row[3:]
        if not any(c for c in cells):
            continue

        per_activity: dict[str, dict[str, bool]] = {
            "seed": {col: False for col, _ in _L01_MONTH_COLS},
            "transplant": {col: False for col, _ in _L01_MONTH_COLS},
        }
        for col_name, idx in _L01_MONTH_COLS:
            if idx >= len(row):
                continue
            activities = decode_l01_cell(row[idx])
            for act in activities:
                if act in per_activity:
                    per_activity[act][col_name] = True

        for act, flags in per_activity.items():
            if not any(flags.values()):
                continue
            partial.append(
                PlantingCalendarRow(crop_name_he=name, activity_type=act, **flags)
            )

    wb.close()
    return merge_month_rows(partial)


def import_all(session: Session, xlsx_path: Path) -> ImportSummary:
    """Load L01 into crop_planting_calendar."""
    summary = ImportSummary()
    rows = parse_groworganic(xlsx_path)
    summary.rows_parsed = len(rows)

    for row in rows:
        crop_id, canonical = resolve_crop_id(session, row.crop_name_he)
        if crop_id is None:
            if canonical is None:
                if row.crop_name_he not in summary.map_misses:
                    summary.map_misses.append(row.crop_name_he)
            else:
                if row.crop_name_he not in summary.db_misses:
                    summary.db_misses.append(row.crop_name_he)
            continue
        if upsert_planting_calendar(
            session, crop_id, row, source=SOURCE, trust_tier=TRUST,
        ):
            summary.rows_upserted += 1

    logger.info(
        "GROWORGANIC: parsed=%d upserted=%d map_misses=%d db_misses=%d",
        summary.rows_parsed,
        summary.rows_upserted,
        len(summary.map_misses),
        len(summary.db_misses),
    )
    return summary
