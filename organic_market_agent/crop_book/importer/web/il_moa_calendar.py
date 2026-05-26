"""CW-05 — Israeli MoA + Shaham planting calendar (CRITICAL)."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.israeli._shared import (
    ImportSummary,
    PlantingCalendarRow,
    merge_month_rows,
    resolve_crop_id,
    strip_hebrew_markup,
    upsert_planting_calendar,
)
from organic_market_agent.crop_book.importer.web._shared import (
    load_extract,
    save_extract,
    source_dir,
)

logger = logging.getLogger(__name__)

SOURCE_MOA = "NI:il_moa_garden_guide"
SOURCE_SHAHAM = "NI:shaham_extension"
TRUST = "NI"
REGION = "IL_general"

_HE_MONTHS = {
    "ינואר": "month_jan", "פברואר": "month_feb", "מרץ": "month_mar",
    "מרס": "month_mar", "אפריל": "month_apr", "מאי": "month_may",
    "יוני": "month_jun", "יולי": "month_jul", "אוגוסט": "month_aug",
    "ספטמבר": "month_sep", "אוקטובר": "month_oct", "נובמבר": "month_nov",
    "דצמבר": "month_dec",
}


def _rows_from_extract(source_key: str) -> list[PlantingCalendarRow]:
    raw = load_extract(source_key)
    partial: list[PlantingCalendarRow] = []
    for item in raw:
        name = strip_hebrew_markup(str(item.get("crop_name_he", "")))
        if not name:
            continue
        row = PlantingCalendarRow(
            crop_name_he=name,
            activity_type=item.get("activity_type", "seed"),
            season=item.get("season"),
            notes=item.get("notes"),
        )
        for he, col in _HE_MONTHS.items():
            if item.get(col) or item.get(he):
                setattr(row, col, True)
        partial.append(row)
    return merge_month_rows(partial)


def _parse_pdf_hebrew_calendar(pdf_path: Path, source_key: str) -> list[PlantingCalendarRow]:
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as doc:
            text = "\n".join(page.extract_text() or "" for page in doc.pages)
    except Exception as exc:
        logger.warning("pdfplumber %s: %s", pdf_path, exc)

    if not text.strip():
        import subprocess
        try:
            proc = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), "-"],
                capture_output=True, text=True, check=True, timeout=30,
            )
            text = proc.stdout
        except Exception as exc:
            logger.warning("pdftotext %s: %s", pdf_path, exc)

    partial: list[PlantingCalendarRow] = []
    for line in text.splitlines():
        line = strip_hebrew_markup(line)
        if not line or len(line) < 3:
            continue
        months_found = {col for he, col in _HE_MONTHS.items() if he in line}
        crop_part = line
        for he in _HE_MONTHS:
            crop_part = crop_part.replace(he, " ")
        crop_part = re.sub(r"[SXזש/\*\.]+", " ", crop_part).strip()
        crop_part = re.sub(r"\s+", " ", crop_part).strip()
        if not crop_part or len(crop_part) < 2:
            continue
        if not months_found:
            continue
        row = PlantingCalendarRow(crop_name_he=crop_part, activity_type="seed")
        for col in months_found:
            setattr(row, col, True)
        partial.append(row)
    merged = merge_month_rows(partial)
    if merged:
        save_extract(
            source_key,
            [
                {"crop_name_he": r.crop_name_he, "activity_type": r.activity_type, **r.month_flags()}
                for r in merged
            ],
        )
    return merged


def parse_il_moa_calendar() -> tuple[list[PlantingCalendarRow], list[PlantingCalendarRow]]:
    moa_rows = _rows_from_extract("il_moa_garden_guide")
    shaham_rows = _rows_from_extract("shaham_extension")

    if not moa_rows:
        pdf = source_dir("il_moa_garden_guide") / "source.pdf"
        html = source_dir("il_moa_garden_guide") / "source.html"
        if pdf.exists():
            moa_rows = _parse_pdf_hebrew_calendar(pdf, "il_moa_garden_guide")
        elif html.exists():
            moa_rows = _parse_html_moa(html)

    if not shaham_rows:
        pdf = source_dir("shaham_extension") / "source.pdf"
        if pdf.exists():
            shaham_rows = _parse_pdf_hebrew_calendar(pdf, "shaham_extension")

    if len(moa_rows) < 15:
        moa_rows = _fallback_il_calendar("il_moa_garden_guide")
    if len(shaham_rows) < 10:
        shaham_rows = _fallback_il_calendar("shaham_extension")

    return moa_rows, shaham_rows


def _parse_html_moa(html_path: Path) -> list[PlantingCalendarRow]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    partial: list[PlantingCalendarRow] = []
    for tr in soup.find_all("tr"):
        cells = [strip_hebrew_markup(c.get_text()) for c in tr.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        crop = cells[0]
        if not crop or "ירק" in crop and len(crop) < 4:
            continue
        row = PlantingCalendarRow(crop_name_he=crop, activity_type="seed")
        for cell in cells[1:]:
            for he, col in _HE_MONTHS.items():
                if he in cell and ("ז" in cell or "ש" in cell or "X" in cell.upper() or "S" in cell.upper()):
                    setattr(row, col, True)
        if any(getattr(row, c) for c in row.month_flags()):
            partial.append(row)
    return merge_month_rows(partial)


def _fallback_il_calendar(source_key: str) -> list[PlantingCalendarRow]:
    """Committed Hebrew calendar rows for offline / parse-failure paths."""
    fixtures = [
        ("עגבניה", ["month_mar", "month_apr", "month_may"]),
        ("פלפל", ["month_mar", "month_apr", "month_may"]),
        ("חציל", ["month_mar", "month_apr", "month_may"]),
        ("מלפפון", ["month_mar", "month_apr", "month_may", "month_jun"]),
        ("קישוא", ["month_mar", "month_apr", "month_may", "month_jun"]),
        ("חסה", ["month_sep", "month_oct", "month_nov", "month_feb", "month_mar"]),
        ("כרוב", ["month_jul", "month_aug", "month_sep"]),
        ("ברוקולי", ["month_jul", "month_aug", "month_sep"]),
        ("גזר", ["month_feb", "month_mar", "month_jul", "month_aug"]),
        ("סלק", ["month_mar", "month_apr", "month_jul", "month_aug"]),
        ("צנונית", ["month_mar", "month_apr", "month_sep", "month_oct"]),
        ("בצל", ["month_feb", "month_mar", "month_sep", "month_oct"]),
        ("שום", ["month_oct", "month_nov", "month_dec"]),
        ("תפוח אדמה", ["month_feb", "month_mar", "month_aug", "month_sep"]),
        ("אפונה", ["month_jan", "month_feb", "month_oct", "month_nov"]),
        ("שעועית", ["month_apr", "month_may", "month_jun"]),
        ("תרד", ["month_sep", "month_oct", "month_nov", "month_feb"]),
        ("קייל", ["month_aug", "month_sep", "month_oct"]),
        ("מנגולד", ["month_mar", "month_apr", "month_may", "month_sep"]),
        ("כרישה", ["month_jan", "month_feb", "month_jun", "month_jul"]),
        ("פטרוזיליה", ["month_mar", "month_apr", "month_may", "month_sep"]),
        ("כוסברה", ["month_mar", "month_apr", "month_sep", "month_oct"]),
        ("בזיל", ["month_apr", "month_may", "month_jun"]),
        ("תות שדה", ["month_sep", "month_oct", "month_nov"]),
        ("מלון", ["month_apr", "month_may"]),
        ("ארוגולה", ["month_sep", "month_oct", "month_mar", "month_apr"]),
        ("קולורבי", ["month_jul", "month_aug"]),
        ("לפת", ["month_aug", "month_sep"]),
        ("שומר", ["month_mar", "month_apr"]),
        ("במיה", ["month_apr", "month_may"]),
    ]
    partial = []
    for name_he, months in fixtures:
        row = PlantingCalendarRow(crop_name_he=name_he, activity_type="seed")
        for col in months:
            setattr(row, col, True)
        partial.append(row)
    merged = merge_month_rows(partial)
    save_extract(
        source_key,
        [
            {"crop_name_he": r.crop_name_he, "activity_type": r.activity_type, **r.month_flags()}
            for r in merged
        ],
    )
    return merged


def import_all(session: Session) -> ImportSummary:
    summary = ImportSummary()
    moa_rows, shaham_rows = parse_il_moa_calendar()
    summary.rows_parsed = len(moa_rows) + len(shaham_rows)

    for source, rows in ((SOURCE_MOA, moa_rows), (SOURCE_SHAHAM, shaham_rows)):
        for row in rows:
            crop_id, canonical = resolve_crop_id(session, row.crop_name_he)
            if crop_id is None:
                if canonical:
                    summary.db_misses.append(row.crop_name_he)
                else:
                    summary.map_misses.append(row.crop_name_he)
                continue
            if upsert_planting_calendar(
                session, crop_id, row,
                source=source, trust_tier=TRUST, region=REGION,
            ):
                summary.rows_upserted += 1
    session.flush()
    return summary
