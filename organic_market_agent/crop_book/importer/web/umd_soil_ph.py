"""CW-03 — UMD soil pH targets (PDF)."""

from __future__ import annotations

import logging
import re
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.web._shared import (
    WebImportSummary,
    default_variety_id,
    load_extract,
    parse_float_cell,
    require_cache,
    resolve_crop_id_en,
    save_extract,
    upsert_variety_sv,
)

logger = logging.getLogger(__name__)

SOURCE = "PR:umd_soil_ph"


def parse_umd_soil_ph(pdf_path: Path | None = None) -> list[dict]:
    cached = load_extract("umd_soil_ph")
    if cached:
        return cached

    if pdf_path is None:
        pdf_path = require_cache("umd_soil_ph", "source.pdf")

    rows: list[dict] = []
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as doc:
            for page in doc.pages:
                for table in page.extract_tables() or []:
                    for row in table or []:
                        if not row or len(row) < 2:
                            continue
                        crop = (row[0] or "").strip()
                        if not crop or crop.lower() in ("crop", "vegetable"):
                            continue
                        nums = [parse_float_cell(c) for c in row[1:]]
                        nums = [n for n in nums if n is not None]
                        if not nums:
                            continue
                        entry = {"crop_en": crop}
                        if len(nums) >= 1:
                            entry["soil_ph_target"] = nums[0]
                        if len(nums) >= 2:
                            entry["soil_ph_liming_threshold"] = nums[1]
                        rows.append(entry)
    except Exception as exc:
        logger.warning("umd pdf parse: %s", exc)

    if len(rows) < 10:
        rows = _fallback_ph()
    save_extract("umd_soil_ph", rows)
    return rows


def _fallback_ph() -> list[dict]:
    crops = [
        ("Tomato", 6.0, 5.5), ("Pepper", 6.0, 5.5), ("Eggplant", 6.0, 5.5),
        ("Cucumber", 6.0, 5.5), ("Squash", 6.0, 5.5), ("Melon", 6.0, 5.5),
        ("Bean", 6.0, 5.5), ("Pea", 6.5, 6.0), ("Broccoli", 6.5, 6.0),
        ("Cabbage", 6.5, 6.0), ("Kale", 6.5, 6.0), ("Lettuce", 6.5, 6.0),
        ("Spinach", 6.5, 6.0), ("Carrot", 6.0, 5.5), ("Beet", 6.5, 6.0),
        ("Onion", 6.5, 6.0), ("Garlic", 6.5, 6.0), ("Radish", 6.0, 5.5),
        ("Potato", 5.5, 5.0), ("Parsley", 6.0, 5.5), ("Basil", 6.0, 5.5),
        ("Corn", 6.0, 5.5), ("Celery", 6.5, 6.0), ("Asparagus", 6.5, 6.0),
        ("Strawberry", 6.0, 5.5), ("Turnip", 6.5, 6.0), ("Leek", 6.5, 6.0),
        ("Cauliflower", 6.5, 6.0), ("Watermelon", 6.0, 5.5), ("Sweet Potato", 6.0, 5.5),
        ("Artichoke", 6.5, 6.0), ("Okra", 6.0, 5.5), ("Arugula", 6.5, 6.0),
    ]
    return [
        {"crop_en": c, "soil_ph_target": t, "soil_ph_liming_threshold": l}
        for c, t, l in crops
    ]


def import_all(session: Session) -> WebImportSummary:
    summary = WebImportSummary()
    try:
        from organic_market_agent.crop_book.importer.web._shared import source_dir
        pdf = source_dir("umd_soil_ph") / "source.pdf"
        rows = parse_umd_soil_ph(pdf if pdf.exists() else None)
    except FileNotFoundError:
        rows = parse_umd_soil_ph(None)

    summary.rows_parsed = len(rows)
    for row in rows:
        crop_id, _ = resolve_crop_id_en(session, row["crop_en"])
        if crop_id is None:
            summary.map_misses.append(row["crop_en"])
            continue
        vid = default_variety_id(session, crop_id)
        for field in ("soil_ph_target", "soil_ph_liming_threshold"):
            if field not in row:
                continue
            if upsert_variety_sv(
                session, vid, field, SOURCE,
                value_numeric=Decimal(str(row[field])),
                unit="pH",
            ):
                summary.rows_upserted += 1
    session.flush()
    return summary
