"""WP-F: Idan Farm Planning Importer — Israeli operator seasonal plans.

Reads JSON cache files produced by the background extraction agent from:
  data/external_sources/extracted/idan_winter_planning/_table.json  (L03)
  data/external_sources/extracted/idan_summer_planning/_table.json   (L04)
  data/external_sources/extracted/idan_2018_tech/_table.json         (L49)

Each file schema:
  {
    "schema_version": "1.0",
    "source": "OP:Idan_winter_planning_v1",
    "provenance": {...},
    "crops": [
      {
        "crop_he": "...",
        "variety_he": "...",
        "days_to_maturity": int | null,
        "dtm_method": "...",
        "in_row_spacing_cm": float | null,
        "rows_per_bed": int | null,
        "avg_yield_per_bed_m": float | null,   # kg/m2 approximation
        "harvest_window_max_days": int | null,
        "planting_method": str | null,
        "notes": str | null,
      },
      ...
    ]
  }

Aggregation strategy: per (crop_he, field), take the FIRST non-null value across all
records across all three files (winter → summer → 2018 tech).  Subsequent non-null
values from the same crop are appended to the note but do not overwrite the primary value.

Source label: OP:idan_planner_v1   (single label; provenance preserved in note)
Trust tier:   OP (Operator / real farm records)
Confidence:   0.80

Fields written to crop_variety_source_values:
  days_to_maturity, in_row_spacing_cm, rows_per_bed,
  harvest_window_max_days, planting_method
  (yield_per_m2_kg removed — forbidden AC-05 derived field; see _NUMERIC_FIELDS)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "OP:idan_planner_v1"
TRUST = "OP"
CONFIDENCE = 0.80

CACHE_FILES = [
    Path("data/external_sources/extracted/idan_winter_planning/_table.json"),
    Path("data/external_sources/extracted/idan_summer_planning/_table.json"),
    Path("data/external_sources/extracted/idan_2018_tech/_table.json"),
]

# Fields to extract from each crop record
_NUMERIC_FIELDS: list[tuple[str, str, str | None]] = [
    # (json_key, db_field_name, unit)
    ("days_to_maturity",         "days_to_maturity",        "days"),
    ("in_row_spacing_cm",        "in_row_spacing_cm",       "cm"),
    ("rows_per_bed",             "rows_per_bed",            None),
    # WP-CB tails cleanup (AC-05): the `avg_yield_per_bed_m` source was emitted to the
    # FORBIDDEN derived field `yield_per_m2_kg` (and was unit-mislabeled per-m² vs the
    # per-bed-meter source). Dropped at source so it no longer relies on the post-seed
    # strip. To resurface it, map to the legit `yield_per_bed_m` after verifying the unit.
    ("harvest_window_max_days",  "harvest_window_max_days", "days"),
]

_TEXT_FIELDS: list[tuple[str, str]] = [
    # (json_key, db_field_name)
    ("planting_method", "planting_method"),
]


def _load_all_records() -> list[dict[str, Any]]:
    """Return flat list of all crop records from all cache files, in order."""
    records: list[dict[str, Any]] = []
    for path in CACHE_FILES:
        if not path.exists():
            logger.warning("WP-F: cache file not found: %s", path)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        crops = data.get("crops", [])
        file_source = data.get("source", SOURCE)
        for c in crops:
            c["_file_source"] = file_source
        records.extend(crops)
    logger.info("WP-F idan_planner: loaded %d records from %d files", len(records), len(CACHE_FILES))
    return records


def _aggregate_by_crop(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate records by crop_he.

    For each field: take first non-null value; accumulate variety names.
    Returns {crop_he: {field: value, "dtm_method": ..., "_varieties": [...], "_sources": [...]}}.
    """
    aggregated: dict[str, dict[str, Any]] = {}

    for rec in records:
        crop_he = rec.get("crop_he", "").strip()
        if not crop_he:
            continue

        if crop_he not in aggregated:
            aggregated[crop_he] = {
                "_varieties": [],
                "_sources": [],
                "_dtm_methods": [],
            }

        agg = aggregated[crop_he]
        variety_he = rec.get("variety_he")
        if variety_he and variety_he not in agg["_varieties"]:
            agg["_varieties"].append(variety_he)
        file_src = rec.get("_file_source", SOURCE)
        if file_src not in agg["_sources"]:
            agg["_sources"].append(file_src)

        # Numeric fields: first non-null wins
        for json_key, db_field, _ in _NUMERIC_FIELDS:
            val = rec.get(json_key)
            if val is not None and db_field not in agg:
                try:
                    agg[db_field] = float(val)
                    # Attach dtm_method as metadata on days_to_maturity
                    if json_key == "days_to_maturity":
                        dm = rec.get("dtm_method")
                        if dm and dm not in agg["_dtm_methods"]:
                            agg["_dtm_methods"].append(dm)
                except (TypeError, ValueError):
                    pass

        # Text fields: first non-null wins
        for json_key, db_field in _TEXT_FIELDS:
            val = rec.get(json_key)
            if val and db_field not in agg:
                agg[db_field] = str(val)

    return aggregated


def _resolve_variety(session, name_he: str) -> tuple[int | None, int | None]:
    """Return (crop_id, variety_id) for the default variety of name_he."""
    from organic_market_agent.crop_book.constants import IL_CROP_MAP, DEFAULT_VARIETY_NAME_HE
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(name_he, name_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).first()
    if crop is None:
        logger.debug("WP-F: crop_he=%r (canonical=%r) not in DB — skipped", name_he, canonical)
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


def ingest(session) -> dict[str, int]:
    """Main ingestion entry point.

    Returns: {source_values_written, crops_processed, crops_skipped}
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value

    records = _load_all_records()
    if not records:
        return {"source_values": 0, "processed": 0, "skipped": 0}

    aggregated = _aggregate_by_crop(records)

    sv_count = 0
    skip_count = 0
    processed_count = 0

    # Skip generic/catch-all crop names
    SKIP_CROPS = {"תבלינים", "עשבי תבלין", "ירקות שורש"}

    for crop_he, agg in aggregated.items():
        if crop_he in SKIP_CROPS:
            logger.debug("WP-F: skipping generic crop name %r", crop_he)
            skip_count += 1
            continue

        _, variety_id = _resolve_variety(session, crop_he)
        if variety_id is None:
            skip_count += 1
            continue

        processed_count += 1

        # Build provenance note prefix
        sources_str = ", ".join(agg.get("_sources", [SOURCE]))
        varieties_str = ", ".join(agg.get("_varieties", []))[:200]
        dtm_methods = agg.get("_dtm_methods", [])

        # ── Numeric fields ─────────────────────────────────────────────────
        for _, db_field, unit in _NUMERIC_FIELDS:
            val = agg.get(db_field)
            if val is None:
                continue
            note_parts = [f"src={sources_str[:80]}"]
            if varieties_str:
                note_parts.append(f"varieties={varieties_str[:80]}")
            if db_field == "days_to_maturity" and dtm_methods:
                note_parts.append(f"method={', '.join(dtm_methods)}")
            note = "; ".join(note_parts)[:500]

            sv = {
                "field_name": db_field,
                "source": SOURCE,
                "value_numeric": val,
                "unit": unit,
                "note": note,
                "trust_tier": TRUST,
                "confidence_weight": CONFIDENCE,
            }
            _upsert_source_value(session, variety_id, sv)
            sv_count += 1

        # ── Text fields ────────────────────────────────────────────────────
        for _, db_field in _TEXT_FIELDS:
            val = agg.get(db_field)
            if val is None:
                continue
            sv = {
                "field_name": db_field,
                "source": SOURCE,
                "value_text": str(val),
                "note": f"src={sources_str[:80]}",
                "trust_tier": TRUST,
                "confidence_weight": CONFIDENCE,
            }
            _upsert_source_value(session, variety_id, sv)
            sv_count += 1

    session.flush()
    logger.info(
        "WP-F idan_planner: %d source_values, %d crops processed, %d skipped",
        sv_count, processed_count, skip_count,
    )
    return {"source_values": sv_count, "processed": processed_count, "skipped": skip_count}
