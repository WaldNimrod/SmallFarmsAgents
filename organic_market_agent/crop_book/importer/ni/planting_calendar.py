"""WP-G: Planting Calendar Importer — Israeli seasonal sowing dates.

Reads JSON cache files produced from:
  L01 GrowOrganic: data/external_sources/extracted/groworganic_calendar/_table.json
  L36 Bustan:      data/external_sources/extracted/bustan_calendar/_table.json

Each file schema:
  {
    "schema_version": "1.0",
    "source": "NI:groworganic_calendar_v1",
    "crops": [
      {
        "crop_he": "...",
        "seed_months": [1, 2, 10, 11, 12],   # calendar month numbers
        "transplant_months": [3, 4],
        "notes": "..."
      },
      ...
    ]
  }

Aggregation: union of seed_months and transplant_months across both sources.
If a crop has data from both sources, the union is stored in a single merged record.

Source labels (per-file provenance kept in note):
  NI:groworganic_calendar_v1   (L01)
  NI:bustan_calendar_v1        (L36)

Combined label for merged record: NI:planting_calendar_il_v1

Trust tier:   NI (Narrative Intelligence / structured local guide)
Confidence:   0.70

Fields written to crop_variety_source_values (value_text = comma-separated months):
  seed_months_list         — "1,2,10,11,12"
  transplant_months_list   — "3,4"
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "NI:planting_calendar_il_v1"
TRUST = "NI"
CONFIDENCE = 0.70

CACHE_FILES = [
    Path("data/external_sources/extracted/groworganic_calendar/_table.json"),
    Path("data/external_sources/extracted/bustan_calendar/_table.json"),
]


def _load_all() -> dict[str, dict[str, Any]]:
    """Load and merge calendar data by crop_he.

    Returns {crop_he: {"seed_months": set, "transplant_months": set, "notes": [...]}}
    """
    merged: dict[str, dict[str, Any]] = {}

    for path in CACHE_FILES:
        if not path.exists():
            logger.warning("WP-G: cache file not found: %s", path)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for crop in data.get("crops", []):
            crop_he = crop.get("crop_he", "").strip()
            if not crop_he:
                continue

            if crop_he not in merged:
                merged[crop_he] = {"seed_months": set(), "transplant_months": set(), "notes": []}

            for m in crop.get("seed_months", []):
                try:
                    merged[crop_he]["seed_months"].add(int(m))
                except (TypeError, ValueError):
                    pass
            for m in crop.get("transplant_months", []):
                try:
                    merged[crop_he]["transplant_months"].add(int(m))
                except (TypeError, ValueError):
                    pass
            note = crop.get("notes")
            if note:
                merged[crop_he]["notes"].append(str(note)[:300])

    return merged


def _resolve_variety(session, name_he: str) -> tuple[int | None, int | None]:
    """Return (crop_id, variety_id) for the default variety of name_he."""
    from organic_market_agent.crop_book.constants import IL_CROP_MAP, DEFAULT_VARIETY_NAME_HE
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(name_he, name_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).first()
    if crop is None:
        logger.debug("WP-G: crop_he=%r not in DB — skipped", name_he)
        return None, None

    variety = session.query(CropVariety).filter_by(crop_id=crop.id, is_default=True).first()
    if variety is None:
        variety = CropVariety(
            crop_id=crop.id,
            name_he=DEFAULT_VARIETY_NAME_HE,
            name_en=None,
            is_default=True,
        )
        session.add(variety)
        session.flush()
    elif variety.name_he is None:
        variety.name_he = DEFAULT_VARIETY_NAME_HE

    return crop.id, variety.id


def _months_to_str(months: set[int]) -> str | None:
    """Return sorted comma-separated month string, or None if empty."""
    if not months:
        return None
    return ",".join(str(m) for m in sorted(months))


def ingest(session) -> dict[str, int]:
    """Main ingestion entry point.

    Returns: {source_values_written, crops_processed, crops_skipped}
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value

    calendar = _load_all()
    if not calendar:
        return {"source_values": 0, "processed": 0, "skipped": 0}

    sv_count = 0
    skip_count = 0
    processed_count = 0

    for crop_he, cal in calendar.items():
        seed_str = _months_to_str(cal["seed_months"])
        transplant_str = _months_to_str(cal["transplant_months"])

        # Skip if no calendar data at all
        if seed_str is None and transplant_str is None:
            continue

        _, variety_id = _resolve_variety(session, crop_he)
        if variety_id is None:
            skip_count += 1
            continue

        processed_count += 1
        note_text = "; ".join(cal["notes"])[:500] if cal["notes"] else None

        if seed_str:
            _upsert_source_value(session, variety_id, {
                "field_name": "seed_months_list",
                "source": SOURCE,
                "value_text": seed_str,
                "note": note_text,
                "trust_tier": TRUST,
                "confidence_weight": CONFIDENCE,
            })
            sv_count += 1

        if transplant_str:
            _upsert_source_value(session, variety_id, {
                "field_name": "transplant_months_list",
                "source": SOURCE,
                "value_text": transplant_str,
                "note": note_text,
                "trust_tier": TRUST,
                "confidence_weight": CONFIDENCE,
            })
            sv_count += 1

    session.flush()
    logger.info(
        "WP-G planting_calendar: %d source_values, %d crops processed, %d skipped",
        sv_count, processed_count, skip_count,
    )
    return {"source_values": sv_count, "processed": processed_count, "skipped": skip_count}
