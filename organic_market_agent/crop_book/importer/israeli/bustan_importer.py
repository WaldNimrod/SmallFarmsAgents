"""BUSTAN sowing calendar PDF importer (L36) — WP-C1 LOD400 §4.2."""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.constants import IL_CROP_MAP
from organic_market_agent.crop_book.importer.israeli._shared import (
    ImportSummary,
    PlantingCalendarRow,
    decode_bustan_token,
    merge_month_rows,
    resolve_crop_id,
    strip_hebrew_markup,
    upsert_planting_calendar,
)

logger = logging.getLogger(__name__)

SOURCE = "NI:bustan"
TRUST = "NI"

_BUSTAN_MONTH_FIELDS = [
    "month_aug", "month_sep", "month_oct", "month_nov", "month_dec",
    "month_jul", "month_jun", "month_may", "month_apr", "month_mar",
    "month_feb", "month_jan",
]

_ACTIVITY_TOKEN_RE = re.compile(
    r"ש\s*/\s*ז\*?|ש/ז\*?|ז\*|ש/ז|(?<![א-ת])ש(?![א-ת/])|(?<![א-ת])ז(?![א-ת*])"
)


def _pdftotext_layout(pdf_path: Path) -> str:
    try:
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return proc.stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        logger.warning("pdftotext failed for %s: %s", pdf_path, exc)
        return ""


def _pdfplumber_text(pdf_path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        return ""
    try:
        with pdfplumber.open(pdf_path) as doc:
            return "\n".join(page.extract_text() or "" for page in doc.pages)
    except Exception as exc:
        logger.warning("pdfplumber failed for %s: %s", pdf_path, exc)
        return ""


def _match_crop_name(cleaned_line: str) -> str | None:
    for key in sorted(IL_CROP_MAP.keys(), key=len, reverse=True):
        if cleaned_line.endswith(key):
            return key
        norm_key = key.replace(" ", "")
        if cleaned_line.replace(" ", "").endswith(norm_key):
            return key
    return None


def _extract_activity_tokens(prefix: str) -> list[str]:
    """Take up to 12 activity tokens from the left portion of a table row."""
    tokens = _ACTIVITY_TOKEN_RE.findall(prefix)
    if len(tokens) >= 12:
        return tokens[:12]
    if tokens:
        return tokens
    return []


def parse_bustan(pdf_path: Path) -> list[PlantingCalendarRow]:
    """Parse BUSTAN PDF into planting-calendar rows."""
    text = _pdftotext_layout(pdf_path)
    if not text.strip():
        text = _pdfplumber_text(pdf_path)
    if not text.strip():
        return []

    partial: list[PlantingCalendarRow] = []
    for line in text.splitlines():
        cleaned = strip_hebrew_markup(line)
        if not cleaned or "הירק" in cleaned or "לוח השנה" in cleaned:
            continue
        crop_name = _match_crop_name(cleaned)
        if not crop_name:
            continue
        prefix = cleaned[: cleaned.rfind(crop_name)].strip()
        if not _ACTIVITY_TOKEN_RE.search(prefix):
            continue
        tokens = _extract_activity_tokens(prefix)
        if not tokens:
            continue
        while len(tokens) < 12:
            tokens.append("")
        tokens = tokens[:12]

        per_activity: dict[str, dict[str, bool]] = {
            "seed": {f: False for f in _BUSTAN_MONTH_FIELDS},
            "transplant": {f: False for f in _BUSTAN_MONTH_FIELDS},
        }
        for field_name, token in zip(_BUSTAN_MONTH_FIELDS, tokens):
            for act in decode_bustan_token(token):
                per_activity[act][field_name] = True

        for act, flags in per_activity.items():
            if any(flags.values()):
                partial.append(
                    PlantingCalendarRow(
                        crop_name_he=crop_name,
                        activity_type=act,
                        **flags,
                    )
                )

    return merge_month_rows(partial)


def import_all(session: Session, pdf_path: Path) -> ImportSummary:
    summary = ImportSummary()
    rows = parse_bustan(pdf_path)
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
            session, crop_id, row, source=SOURCE, trust_tier=TRUST, region="IL",
        ):
            summary.rows_upserted += 1

    logger.info(
        "BUSTAN: parsed=%d upserted=%d map_misses=%d db_misses=%d",
        summary.rows_parsed,
        summary.rows_upserted,
        len(summary.map_misses),
        len(summary.db_misses),
    )
    return summary
