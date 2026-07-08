"""IL farm 2017 base-data importer (L45) — SFA-S003-P004-WP-CB-SRC-SWEEP.

Cherry-pick of the 'נתוני בסיס' (base-data) sheet from L45_2017_data_summary.xlsx,
a real Israeli market-garden farm's 2017 operations workbook. Per team_00
(2026-06-10) only the agronomically-useful, non-duplicate data is integrated —
the planting-calendar, price, budget, trees and cannabis sheets are intentionally
excluded (see scripts/extract_l45_basedata.py for the full exclusion rationale).

Reads the tracked cache produced by that extractor:
  data/external_sources/extracted/il_farm_2017_l45/_table.json

Writes to crop_variety_source_values (default variety per crop):
  days_to_maturity, in_row_spacing_cm, rows_per_bed
and one growing_tip crop_knowledge_notes row per crop carrying the season +
cultural notes (internal-only, like all knowledge notes).

Source label: OP:il_farm_2017_l45  (Operator / real farm records)
Trust tier:   OP        Confidence: 0.80   (NOT a hard override — blends with
                                            other sources in the reconciler)

Crop resolution reuses the Idan importer's _resolve_variety (IL_CROP_MAP aliases
בצל יבש->בצל, תפו"א->תפוח אדמה, תרד טורקי->תרד, etc.; generic names skipped).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "OP:il_farm_2017_l45"
TRUST = "OP"
CONFIDENCE = 0.80

CACHE_FILE = Path("data/external_sources/extracted/il_farm_2017_l45/_table.json")

# (json_key, db_field_name, unit)
_NUMERIC_FIELDS: list[tuple[str, str, str | None]] = [
    ("days_to_maturity", "days_to_maturity", "days"),
    ("in_row_spacing_cm", "in_row_spacing_cm", "cm"),
    ("rows_per_bed", "rows_per_bed", None),
]


def _load_records() -> list[dict[str, Any]]:
    if not CACHE_FILE.exists():
        logger.warning("L45: cache file not found: %s", CACHE_FILE)
        return []
    data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return data.get("crops", [])


def ingest(session) -> dict[str, int]:
    """Ingest L45 base-data. Returns counts dict."""
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value
    from organic_market_agent.crop_book.importer.ni.idan_planner import _resolve_variety
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    records = _load_records()
    if not records:
        return {"source_values": 0, "notes": 0, "processed": 0, "skipped": 0}

    sv_count = 0
    note_count = 0
    processed = 0
    skipped = 0

    for rec in records:
        crop_he = (rec.get("crop_he") or "").strip()
        if not crop_he:
            skipped += 1
            continue

        crop_id, variety_id = _resolve_variety(session, crop_he)
        if variety_id is None or crop_id is None:
            logger.debug("L45: crop_he=%r not resolved — skipped", crop_he)
            skipped += 1
            continue
        processed += 1

        dtm_raw = rec.get("dtm_raw")
        # ── Numeric source values ───────────────────────────────────────────
        for json_key, db_field, unit in _NUMERIC_FIELDS:
            val = rec.get(json_key)
            if val is None:
                continue
            note = "src=L45 IL farm 2017 base-data"
            if db_field == "days_to_maturity" and dtm_raw:
                note += f"; raw={dtm_raw} (transplant->harvest)"
            sv = {
                "field_name": db_field,
                "source": SOURCE,
                "value_numeric": float(val),
                "unit": unit,
                "note": note[:500],
                "trust_tier": TRUST,
                "confidence_weight": CONFIDENCE,
            }
            _upsert_source_value(session, variety_id, sv)
            sv_count += 1

        # ── Knowledge note (internal): season + cultural notes ──────────────
        parts: list[str] = []
        season = rec.get("season_he")
        if season:
            parts.append(f"עונה: {season}.")
        notes_he = rec.get("notes")
        if notes_he:
            parts.append(notes_he)
        body = " ".join(parts).strip()
        if body:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source=SOURCE,
                note_type="growing_tip",
                body_text=body[:2000],
                provenance_pdf="L45_2017_data_summary.xlsx",
                provenance_pages="נתוני בסיס",
                extraction_model="claude-code-direct",
            )
            note_count += 1

    session.flush()
    logger.info(
        "L45 il_farm_2017: %d source_values, %d notes, %d processed, %d skipped",
        sv_count, note_count, processed, skipped,
    )
    return {"source_values": sv_count, "notes": note_count, "processed": processed, "skipped": skipped}
