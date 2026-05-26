"""JMF cover crop chart importer (L12) — WP-C1 LOD400 §4.4."""

from __future__ import annotations

import logging
import re
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.cover_crops import CropCoverCrop

logger = logging.getLogger(__name__)

SOURCE = "PR:jmf_cover_crops"
TRUST = "PR"

_CATEGORY_HEADERS = {
    "legumes (fabaceae)": "legume",
    "cereals (grasses)": "cereal",
    "brassicas": "brassica",
}


def _extract_text(pdf_path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as doc:
            text = "\n".join(page.extract_text() or "" for page in doc.pages)
            if text.strip():
                return text
    except Exception:
        pass
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return proc.stdout
    except Exception as exc:
        logger.warning("cover crops PDF text extract failed: %s", exc)
        return ""


def _parse_temp_c(text: str) -> Decimal | None:
    m = re.search(r"(\d+)\s*°?\s*F.*?(\d+)\s*°?\s*C", text)
    if m:
        try:
            return Decimal(m.group(2))
        except InvalidOperation:
            return None
    m = re.search(r"(\d+)\s*°?\s*C", text)
    if m:
        try:
            return Decimal(m.group(1))
        except InvalidOperation:
            return None
    return None


def _parse_zone(text: str) -> int | None:
    m = re.search(r"zone\s*(\d+)", text, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r":\s*(\d+)\s*$", text.strip())
    if m:
        return int(m.group(1))
    return None


def _parse_days(text: str) -> int | None:
    m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*days", text, re.I)
    if m:
        return int(m.group(2))
    m = re.search(r"(\d+)\s*days", text, re.I)
    if m:
        return int(m.group(1))
    return None


def _parse_survives_winter(text: str) -> bool | None:
    low = text.lower()
    if "yes" in low or "survive" in low:
        return True
    if "no" in low:
        return False
    return None


def parse_cover_crops(pdf_path: Path) -> list[dict]:
    """Parse L12 PDF into cover-crop row dicts."""
    text = _extract_text(pdf_path)
    if not text.strip():
        return []

    category = "other"
    rows: list[dict] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        low = stripped.lower()
        for header, cat in _CATEGORY_HEADERS.items():
            if header in low:
                category = cat
                continue

        if low.startswith("cover crop") or low.startswith("total days"):
            continue
        if "fixes atmospheric nitrogen" in low:
            continue

        parts = re.split(r"\s{2,}|\t", stripped)
        name = parts[0].strip()
        if not name or len(name) > 55:
            continue
        if name.lower() in ("note", "inoculum", "when to sow"):
            continue
        if not re.match(r"^[A-Za-z]", name):
            continue

        blob = " ".join(parts[1:]) if len(parts) > 1 else stripped
        rows.append({
            "name_en": name,
            "category": category,
            "total_days_garden": _parse_days(blob),
            "germination_temp_c_min": _parse_temp_c(blob),
            "hardiness_zone": _parse_zone(blob),
            "sow_window": parts[4].strip() if len(parts) > 4 else None,
            "inoculum": parts[5].strip() if len(parts) > 5 else None,
            "survives_winter": _parse_survives_winter(blob),
            "notes": parts[-1].strip() if len(parts) > 6 else None,
        })

    # Deduplicate by name
    seen: set[str] = set()
    unique: list[dict] = []
    for row in rows:
        key = row["name_en"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def import_all(session: Session, pdf_path: Path) -> dict:
    parsed = parse_cover_crops(pdf_path)
    upserted = 0
    for row in parsed:
        existing = (
            session.query(CropCoverCrop)
            .filter_by(name_en=row["name_en"], source=SOURCE)
            .one_or_none()
        )
        if existing is None:
            obj = CropCoverCrop(
                name_en=row["name_en"],
                name_he=None,
                category=row["category"],
                source=SOURCE,
                trust_tier=TRUST,
                total_days_garden=row.get("total_days_garden"),
                germination_temp_c_min=row.get("germination_temp_c_min"),
                hardiness_zone=row.get("hardiness_zone"),
                sow_window=row.get("sow_window"),
                inoculum=row.get("inoculum"),
                survives_winter=row.get("survives_winter"),
                notes=row.get("notes"),
            )
            session.add(obj)
            upserted += 1
        else:
            existing.category = row["category"]
            existing.total_days_garden = row.get("total_days_garden")
            existing.germination_temp_c_min = row.get("germination_temp_c_min")
            existing.hardiness_zone = row.get("hardiness_zone")
            existing.sow_window = row.get("sow_window")
            existing.inoculum = row.get("inoculum")
            existing.survives_winter = row.get("survives_winter")
            existing.notes = row.get("notes")
        session.flush()

    summary = {"parsed": len(parsed), "upserted": upserted}
    logger.info("JMF cover crops: %s", summary)
    return summary
