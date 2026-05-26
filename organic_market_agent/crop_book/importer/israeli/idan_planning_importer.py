"""Idan Eliakim 2017 planning importer (L03 winter + L04 summer) — WP-C1 §4.3."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import openpyxl
from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.israeli._shared import (
    ImportSummary,
    PlantingCalendarRow,
    _SKIP_IL_ROWS,
    merge_month_rows,
    resolve_crop_id,
    upsert_planting_calendar,
)

logger = logging.getLogger(__name__)

SOURCE = "OP:Idan_2017"
TRUST = "OP"
CONFIDENCE = Decimal("0.55")
SHEET = "תוכנית גידול"

_HE_MONTH_NUM: dict[str, int] = {
    "ינ": 1, "ינו": 1, "ינואר": 1,
    "פבר": 2, "פברואר": 2,
    "מרץ": 3, "מר": 3,
    "אפר": 4, "אפריל": 4,
    "מאי": 5,
    "יונ": 6, "יוני": 6,
    "יול": 7, "יולי": 7, "7": 7, "8.2017": 8,
    "אוג": 8, "אוגוסט": 8,
    "ספט": 9, "ספטמבר": 9,
    "אוק": 10, "אוקטובר": 10, "תחילת אוקטובר": 10,
    "נוב": 11, "נובמבר": 11,
    "דצ": 12, "דצמבר": 12, "דצמ": 12,
}

_NUM_TO_MONTH_FIELD = {
    1: "month_jan", 2: "month_feb", 3: "month_mar", 4: "month_apr",
    5: "month_may", 6: "month_jun", 7: "month_jul", 8: "month_aug",
    9: "month_sep", 10: "month_oct", 11: "month_nov", 12: "month_dec",
}


def _parse_month_token(token: str | None) -> int | None:
    if token is None:
        return None
    raw = str(token).strip()
    if not raw:
        return None
    if isinstance(token, datetime):
        return token.month
    m = re.match(r"^(\d{1,2})[\./](\d{1,2})[\./](\d{4})$", raw)
    if m:
        return int(m.group(2))
    m = re.match(r"^(\d{1,2})[\./](\d{4})$", raw)
    if m:
        month = int(m.group(1))
        return month if 1 <= month <= 12 else None
    m = re.match(r"^(\d{1,2})[\./](\d{1,2})$", raw)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if b <= 12:
            return b
        if a <= 12:
            return a
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        return int(m.group(2))
    for key, num in sorted(_HE_MONTH_NUM.items(), key=lambda kv: -len(kv[0])):
        if len(key) >= 3 and key in raw:
            return num
    return None


def _month_range(start: str | None, end: str | None) -> set[str]:
    sm = _parse_month_token(start)
    em = _parse_month_token(end)
    if sm is None and em is None:
        return set()
    if sm is None:
        sm = em
    if em is None:
        em = sm
    fields: set[str] = set()
    cur = sm
    for _ in range(12):
        fields.add(_NUM_TO_MONTH_FIELD[cur])
        if cur == em:
            break
        cur = cur + 1 if cur < 12 else 1
    return fields


def _header_map(header_row: tuple) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, val in enumerate(header_row):
        if val is None:
            continue
        key = str(val).strip()
        if key:
            mapping[key] = idx
    return mapping


def _is_summary_row(row: tuple, header: dict[str, int]) -> bool:
    crop_idx = header.get("גידול", 0)
    crop_val = row[crop_idx] if crop_idx < len(row) else None
    if crop_val is None:
        return True
    crop = str(crop_val).strip()
    return crop in _SKIP_IL_ROWS or crop == ""


def _get_or_create_variety(session: Session, crop_id: int, variety_name: str | None) -> int:
    from organic_market_agent.crop_book.models import CropVariety

    name = (variety_name or "").strip() or None
    q = session.query(CropVariety).filter(CropVariety.crop_id == crop_id)
    if name:
        q = q.filter(CropVariety.name_he == name)
    else:
        q = q.filter(CropVariety.name_he.is_(None), CropVariety.name_en.is_(None))
    v = q.order_by(CropVariety.id).first()
    if v is None:
        v = CropVariety(crop_id=crop_id, name_he=name, name_en=None)
        session.add(v)
        session.flush()
    return v.id


def _upsert_source_value(
    session: Session,
    variety_id: int,
    field_name: str,
    value_numeric: Decimal | None,
    *,
    value_text: str | None = None,
    unit: str | None = None,
) -> None:
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    row = (
        session.query(CropVarietySourceValue)
        .filter_by(variety_id=variety_id, field_name=field_name, source=SOURCE)
        .one_or_none()
    )
    if row is None:
        row = CropVarietySourceValue(
            variety_id=variety_id,
            field_name=field_name,
            source=SOURCE,
        )
        session.add(row)
    row.value_numeric = value_numeric
    row.value_text = value_text if value_text is not None else (
        str(value_numeric) if value_numeric is not None else None
    )
    row.unit = unit
    row.trust_tier = TRUST
    row.confidence_weight = CONFIDENCE
    row.is_outlier_rejected = False
    session.flush()


def parse_idan_xlsx(xlsx_path: Path) -> tuple[list[dict], list[PlantingCalendarRow]]:
    """Return (source_value dicts, planting calendar rows) from one workbook."""
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[SHEET]
    rows_iter = ws.iter_rows(values_only=True)
    header: dict[str, int] | None = None
    sv_rows: list[dict] = []
    cal_partial: list[PlantingCalendarRow] = []
    current_crop: str | None = None

    for row in rows_iter:
        if not row or all(c is None or str(c).strip() == "" for c in row):
            continue
        first = str(row[0]).strip() if row[0] else ""
        if first == "גידול":
            header = _header_map(row)
            current_crop = None
            continue
        if header is None or first in _SKIP_IL_ROWS or first == "סיכום":
            continue

        crop_idx = header.get("גידול", 0)
        crop_cell = row[crop_idx] if crop_idx < len(row) else None
        crop_name = str(crop_cell).strip() if crop_cell else ""
        if crop_name:
            current_crop = crop_name
        elif current_crop:
            crop_name = current_crop
        else:
            continue

        def col(name: str, default: int | None = None) -> int | None:
            idx = header.get(name, default)
            if idx is None or idx >= len(row):
                return None
            return idx

        var_idx = col("זן", 1)
        variety = str(row[var_idx]).strip() if var_idx is not None and row[var_idx] else None

        plant_idx = col("תאריך שתילה", 3)
        harvest_start_idx = col("תאריך התחלת אסיף", 5)
        harvest_end_idx = col("תאריך סיום אסיף", 6)
        rows_bed_idx = col("מספר שורות בערוגה", 9)
        spacing_idx = col("מרווח בשורה", 10)
        qty_idx = col('כמות סה"כ(קילו)', 12)
        if qty_idx is None:
            qty_idx = col("כמות (קילו)", 12)
        if qty_idx is None:
            qty_idx = col("כמות (צרורות)", 12)

        plant_val = row[plant_idx] if plant_idx is not None else None
        hs = row[harvest_start_idx] if harvest_start_idx is not None else None
        he = row[harvest_end_idx] if harvest_end_idx is not None else None

        month_fields = {f"month_{m}": False for m in (
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec",
        )}
        for mf in _month_range(str(plant_val) if plant_val else None, str(plant_val) if plant_val else None):
            month_fields[mf] = True
        for mf in _month_range(str(hs) if hs else None, str(he) if he else None):
            month_fields[mf] = True

        if any(month_fields.values()):
            cal_partial.append(
                PlantingCalendarRow(
                    crop_name_he=crop_name,
                    activity_type="transplant",
                    **month_fields,
                )
            )

        entry: dict = {
            "crop_name_he": crop_name,
            "variety_name_he": variety,
        }
        if rows_bed_idx is not None and row[rows_bed_idx] is not None:
            try:
                entry["rows_per_bed"] = int(float(row[rows_bed_idx]))
            except (TypeError, ValueError):
                pass
        if spacing_idx is not None and row[spacing_idx] is not None:
            try:
                entry["in_row_spacing_cm"] = Decimal(str(row[spacing_idx]))
            except (InvalidOperation, ValueError):
                pass
        if qty_idx is not None and row[qty_idx] is not None:
            try:
                entry["avg_yield_per_bed_m"] = Decimal(str(row[qty_idx]))
            except (InvalidOperation, ValueError):
                pass
        sv_rows.append(entry)

    wb.close()
    return sv_rows, merge_month_rows(cal_partial)


def import_all(
    session: Session,
    winter_path: Path,
    summer_path: Path,
) -> ImportSummary:
    summary = ImportSummary()
    all_sv: list[dict] = []
    all_cal: list[PlantingCalendarRow] = []

    for path in (winter_path, summer_path):
        sv, cal = parse_idan_xlsx(path)
        all_sv.extend(sv)
        all_cal.extend(cal)

    summary.rows_parsed = len(all_sv)

    for entry in all_sv:
        crop_id, canonical = resolve_crop_id(session, entry["crop_name_he"])
        if crop_id is None:
            if canonical is None:
                if entry["crop_name_he"] not in summary.map_misses:
                    summary.map_misses.append(entry["crop_name_he"])
            else:
                if entry["crop_name_he"] not in summary.db_misses:
                    summary.db_misses.append(entry["crop_name_he"])
            continue

        variety_id = _get_or_create_variety(
            session, crop_id, entry.get("variety_name_he"),
        )
        if entry.get("rows_per_bed") is not None:
            _upsert_source_value(
                session, variety_id, "rows_per_bed",
                Decimal(entry["rows_per_bed"]), unit="count",
            )
            summary.rows_upserted += 1
        if entry.get("in_row_spacing_cm") is not None:
            _upsert_source_value(
                session, variety_id, "in_row_spacing_cm",
                entry["in_row_spacing_cm"], unit="cm",
            )
            summary.rows_upserted += 1
        if entry.get("avg_yield_per_bed_m") is not None:
            _upsert_source_value(
                session, variety_id, "avg_yield_per_bed_m",
                entry["avg_yield_per_bed_m"], unit="kg",
            )
            summary.rows_upserted += 1

    for row in merge_month_rows(all_cal):
        crop_id, _ = resolve_crop_id(session, row.crop_name_he)
        if crop_id is None:
            continue
        upsert_planting_calendar(
            session, crop_id, row, source=SOURCE, trust_tier=TRUST, region="IL",
        )

    logger.info(
        "Idan planning: parsed=%d source_upserts=%d map_misses=%d",
        summary.rows_parsed,
        summary.rows_upserted,
        len(summary.map_misses),
    )
    return summary
