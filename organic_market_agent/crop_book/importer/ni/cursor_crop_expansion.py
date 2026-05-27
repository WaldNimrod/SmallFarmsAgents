"""WP-D: CursorCropExpansionImporter — 16-crop web research batch ingestion.

Reads Cursor-generated batch JSON files from:
  data/external_sources/web/sfa_crop_batch{1,2,3,4}/SFA_CROP_JSON_BATCH{N}_v1.0.0.json

Each batch file schema:
  {
    "meta": {...},
    "sources": {"items": [{"source_id": "SRC-...", "organization": ..., "url": ..., ...}, ...]},
    "crops": [{"name_he": "...", "name_en": "...", "fields": {<field_key>: {"value":...,
               "unit":..., "notes":..., "source_ids": [...]}, ...}}, ...]
  }

Source label: WR:cursor_crop_expansion_v1
trust_tier:   WR (Web Research)
confidence_weight: 0.7

Fields written to crop_variety_source_values:
  days_to_maturity, in_row_spacing_cm, rows_per_bed, planting_method,
  yield_per_m2_kg, seeds_per_gram, germination_temp_c_min, germination_temp_c_max,
  frost_tolerance_class, harvest_window_max_days, succession_interval_weeks,
  soil_ph_target, soil_ph_liming_threshold

Fields written to crop_knowledge_notes (growing_tip):
  israel_mediterranean_notes  (note_type=growing_tip)
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "WR:cursor_crop_expansion_v1"
TRUST = "WR"
CONFIDENCE = 0.7

BATCH_DIR = Path("data/external_sources/web")
BATCH_FILES = [
    BATCH_DIR / f"sfa_crop_batch{i}" / f"SFA_CROP_JSON_BATCH{i}_v1.0.0.json"
    for i in range(1, 5)
]

# Maps batch field keys → DB field_name values
_NUMERIC_FIELD_MAP: dict[str, tuple[str, str | None]] = {
    # (batch_key): (db_field_name, unit)
    "dtm_days":               ("days_to_maturity",       "days"),
    "spacing_cm":             ("in_row_spacing_cm",       "cm"),
    "rows_per_bed":           ("rows_per_bed",            None),
    "yield_kg_per_m2":        ("yield_per_m2_kg",         "kg/m2"),
    "seeds_per_g":            ("seeds_per_gram",          "seeds/g"),
    "germ_temp_c_min":        ("germination_temp_c_min",  "°C"),
    "germ_temp_c_max":        ("germination_temp_c_max",  "°C"),
    "harvest_window_days":    ("harvest_window_max_days", "days"),
    "succession_interval_weeks": ("succession_interval_weeks", "weeks"),
}

_TEXT_FIELD_MAP: dict[str, str] = {
    "planting_method":        "planting_method",
    "frost_class":            "frost_tolerance_class",
}


def _load_batches() -> list[dict[str, Any]]:
    """Return flat list of all crop dicts across all 4 batch files."""
    all_crops: list[dict[str, Any]] = []
    for path in BATCH_FILES:
        if not path.exists():
            logger.warning("WP-D: batch file not found: %s", path)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        crops = data.get("crops", [])
        if isinstance(crops, list):
            all_crops.extend(crops)
        else:
            logger.warning("WP-D: unexpected crops format in %s", path.name)
    logger.info("WP-D: loaded %d crops from %d batch files", len(all_crops), len(BATCH_FILES))
    return all_crops


def _resolve_crop_and_variety(session, crop_he: str):
    """Return (crop_id, variety_id) for the default variety of crop_he.

    Uses IL_CROP_MAP for spelling normalization.
    Creates the default variety if it doesn't exist yet.
    """
    from organic_market_agent.crop_book.constants import IL_CROP_MAP
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(crop_he, crop_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != crop_he:
        crop = session.query(Crop).filter_by(name_he=crop_he).first()
    if crop is None:
        logger.warning("WP-D: crop_he=%r not in DB — skipped", crop_he)
        return None, None

    variety = session.query(CropVariety).filter_by(crop_id=crop.id, is_default=True).first()
    if variety is None:
        variety = CropVariety(crop_id=crop.id, name_en=None, is_default=True)
        session.add(variety)
        session.flush()

    return crop.id, variety.id


def _make_sv(variety_id: int, field_name: str, *,
             value_text: str | None = None,
             value_numeric: float | None = None,
             unit: str | None = None,
             note: str | None = None) -> dict[str, Any]:
    return {
        "variety_id": variety_id,
        "field_name": field_name,
        "source": SOURCE,
        "value_text": value_text,
        "value_numeric": value_numeric,
        "unit": unit,
        "note": note,
        "trust_tier": TRUST,
        "confidence_weight": CONFIDENCE,
    }


def ingest(session) -> dict[str, int]:
    """Main ingestion entry point.

    Returns summary dict: {source_values_written, knowledge_notes_written, crops_skipped}.
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    crops = _load_batches()
    sv_count = 0
    ckn_count = 0
    skip_count = 0

    for crop_dict in crops:
        crop_he = crop_dict.get("name_he", "")
        fields = crop_dict.get("fields", {})

        crop_id, variety_id = _resolve_crop_and_variety(session, crop_he)
        if crop_id is None:
            skip_count += 1
            continue

        # ── Numeric fields ─────────────────────────────────────────────────
        for batch_key, (db_field, unit) in _NUMERIC_FIELD_MAP.items():
            fdata = fields.get(batch_key, {})
            val = fdata.get("value")
            if val is None:
                continue
            try:
                val_f = float(val)
            except (TypeError, ValueError):
                logger.warning("WP-D: %s.%s non-numeric value %r — skipped", crop_he, batch_key, val)
                continue
            note_text = fdata.get("notes", "")[:500] if fdata.get("notes") else None
            # Append dtm_method as note context on days_to_maturity
            if batch_key == "dtm_days":
                dtm_method = fields.get("dtm_method", {}).get("value", "")
                if dtm_method:
                    prefix = f"[{dtm_method}] "
                    note_text = (prefix + (note_text or ""))[:500]
            sv = _make_sv(variety_id, db_field, value_numeric=val_f, unit=unit, note=note_text)
            _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
            sv_count += 1

        # ── Text fields ────────────────────────────────────────────────────
        for batch_key, db_field in _TEXT_FIELD_MAP.items():
            fdata = fields.get(batch_key, {})
            val = fdata.get("value")
            if val is None:
                continue
            note_text = fdata.get("notes", "")[:500] if fdata.get("notes") else None
            sv = _make_sv(variety_id, db_field, value_text=str(val), note=note_text)
            _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
            sv_count += 1

        # ── Soil pH (compute target + liming threshold from min/max) ───────
        ph_min_data = fields.get("soil_ph_min", {})
        ph_max_data = fields.get("soil_ph_max", {})
        ph_min = ph_min_data.get("value")
        ph_max = ph_max_data.get("value")
        if ph_min is not None:
            try:
                ph_min_f = float(ph_min)
                # soil_ph_liming_threshold = min pH
                sv = _make_sv(variety_id, "soil_ph_liming_threshold",
                               value_numeric=ph_min_f,
                               note=(ph_min_data.get("notes", "")[:500] or None))
                _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
                sv_count += 1
                # soil_ph_target = midpoint (or min if max unavailable)
                ph_max_f = float(ph_max) if ph_max is not None else ph_min_f
                target = round((ph_min_f + ph_max_f) / 2, 2)
                ph_note = f"range {ph_min_f}–{ph_max_f}; target = midpoint"
                sv = _make_sv(variety_id, "soil_ph_target",
                               value_numeric=target, note=ph_note)
                _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
                sv_count += 1
            except (TypeError, ValueError) as exc:
                logger.warning("WP-D: %s soil_ph parse error: %s", crop_he, exc)

        # ── Israeli/Mediterranean notes → crop_knowledge_notes ─────────────
        il_data = fields.get("israel_mediterranean_notes", {})
        il_val = il_data.get("value")
        if il_val:
            _upsert_knowledge_note(
                session,
                crop_id=crop_id,
                source=SOURCE,
                note_type="growing_tip",
                body_text=str(il_val)[:2000],
                trust_tier=TRUST,
                extraction_model="cursor_web_research",
            )
            ckn_count += 1

    session.flush()
    logger.info(
        "WP-D cursor_crop_expansion: %d source_values, %d knowledge_notes, %d crops skipped",
        sv_count, ckn_count, skip_count,
    )
    return {"source_values": sv_count, "knowledge_notes": ckn_count, "skipped": skip_count}
