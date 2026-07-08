"""WP-E: OpenAI Tier 1 Vegetable Crop Research Importer.

Reads from:
  data/external_sources/web/openai_tier1_research/sfa_tier1_crops_research_pack_2026_05_27.json

Source: University extension data (UC ANR, CSU, UMN, UMD, NEVegetable, UC Davis)
curated and structured by OpenAI deep-research session, 2026-05-27.

Source label: WR:openai_tier1_research_v1
Trust tier:   WR (Web Research)
Confidence:   0.75

Fields written to crop_variety_source_values:
  days_to_maturity, germination_temp_c_min, germination_temp_c_max,
  soil_ph_target, soil_ph_liming_threshold, frost_tolerance_class,
  nutrient_removal_n_kg_ha, nutrient_removal_p2o5_kg_ha, nutrient_removal_k2o_kg_ha,
  storage_temp_c_min, storage_temp_c_max,
  storage_rh_pct_min, storage_rh_pct_max,
  storage_ethylene_sensitivity, storage_life_text
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "WR:openai_tier1_research_v1"
TRUST = "WR"
CONFIDENCE = 0.75

DATA_FILE = Path("data/external_sources/web/openai_tier1_research/sfa_tier1_crops_research_pack_2026_05_27.json")

# Map OpenAI crop_id → Hebrew name_he for DB lookup
# Uses canonical name as stored in the Crop table (after IL_CROP_MAP normalization)
OPENAI_CROP_MAP: dict[str, str] = {
    "tomato_cherry":    "עגבניית שרי",
    "tomato_field":     "עגבנייה",
    "pepper_bell":      "פלפל",
    "lettuce":          "חסה",
    "cucumber":         "מלפפון",
    "carrot":           "גזר",
    "onion":            "בצל",
    "potato":           "תפוח אדמה",
    "eggplant":         "חציל",
    "spinach":          "תרד",
    "bean_snap":        "שעועית ירוקה",
    "pea":              "אפונה",
    "cabbage":          "כרוב",
    "broccoli":         "ברוקולי",
    "cauliflower":      "כרובית",
    "zucchini":         "קישוא",
    "melon_muskmelon":  "מלון",
    "watermelon":       "אבטיח",
    "corn_sweet":       "תירס",       # IL_CROP_MAP: "תירס מתוק" → "תירס"
    "beet":             "סלק",
    "radish":           "צנון",
    "parsley":          "פטרוזיליה",
    "basil":            "בזיל",   # team_00 2026-06-10: canonical basil crop (was 'בזיליקום')
    "edamame":          "אדממה",
}


def _get_simple_numeric(obj: Any, *keys: str) -> float | None:
    """Navigate nested dict by keys and return float value, or None."""
    for k in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(k)
    if obj is None:
        return None
    try:
        return float(obj)
    except (TypeError, ValueError):
        return None


def _extract_temp_rh(storage: dict[str, Any]) -> tuple[float | None, float | None, float | None, float | None]:
    """Extract (temp_min, temp_max, rh_min, rh_max) from postharvest_storage dict.

    Handles simple {"min": X, "max": Y} and stage-specific nested dicts.
    For stage-specific, prefers "firm_ripe" > "late_crop" > first available stage.
    """
    if not storage:
        return None, None, None, None

    def _resolve_range(v: Any) -> tuple[float | None, float | None]:
        if not isinstance(v, dict):
            return None, None
        # Simple {"min": X, "max": Y}
        if "min" in v and "max" in v:
            try:
                return float(v["min"]), float(v["max"])
            except (TypeError, ValueError):
                return None, None
        # Stage-specific: prefer firm_ripe > late_crop > first value
        for preferred in ("firm_ripe", "late_crop"):
            if preferred in v:
                inner = v[preferred]
                if isinstance(inner, dict) and "min" in inner and "max" in inner:
                    try:
                        return float(inner["min"]), float(inner["max"])
                    except (TypeError, ValueError):
                        pass
        # Fall back to first nested value
        for stage_val in v.values():
            if isinstance(stage_val, dict) and "min" in stage_val and "max" in stage_val:
                try:
                    return float(stage_val["min"]), float(stage_val["max"])
                except (TypeError, ValueError):
                    pass
        return None, None

    temp = storage.get("temperature_c")
    rh = storage.get("relative_humidity_percent")
    temp_min, temp_max = _resolve_range(temp)
    rh_min, rh_max = _resolve_range(rh)
    return temp_min, temp_max, rh_min, rh_max


def _extract_ethylene_sensitivity(storage: dict[str, Any]) -> str | None:
    """Extract ethylene_sensitivity text, handling simple string and stage-specific dict."""
    v = storage.get("ethylene_sensitivity")
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        # Prefer firm_ripe > late_crop > first
        for preferred in ("firm_ripe", "late_crop"):
            if preferred in v and isinstance(v[preferred], str):
                return v[preferred]
        for val in v.values():
            if isinstance(val, str):
                return val
    return None


def _extract_storage_life(storage: dict[str, Any]) -> str | None:
    """Extract storage_life text, handling string and stage-specific dict."""
    v = storage.get("storage_life")
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        for preferred in ("firm_ripe", "late_crop"):
            if preferred in v and isinstance(v[preferred], str):
                return v[preferred]
        for val in v.values():
            if isinstance(val, str):
                return val
    return None


def _extract_dtm(dtm_obj: dict[str, Any]) -> tuple[float | None, str | None]:
    """Return (days_numeric, note_text) from DTM object.

    Uses midpoint of min/max range, or from_transplant if available.
    Returns None if no extractable value.
    """
    if not dtm_obj:
        return None, None

    days = dtm_obj.get("days")
    method = dtm_obj.get("method", "")
    stage = dtm_obj.get("harvest_stage", "")

    if isinstance(days, dict):
        if "min" in days and "max" in days:
            try:
                mn, mx = float(days["min"]), float(days["max"])
                mid = round((mn + mx) / 2, 1)
                note = f"range {int(mn)}–{int(mx)} days; method={method}; stage={stage}"
                return mid, note[:500]
            except (TypeError, ValueError):
                pass
        if "from_transplant" in days:
            try:
                val = float(days["from_transplant"])
                note = f"{val} days from_transplant; stage={stage}"
                return val, note[:500]
            except (TypeError, ValueError):
                pass
    return None, None


def _extract_npk(npk_obj: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    """Return (N_kg_ha, P2O5_kg_ha, K2O_kg_ha)."""
    if not npk_obj:
        return None, None, None

    def _to_float(v: Any) -> float | None:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, dict) and "min" in v and "max" in v:
            try:
                return round((float(v["min"]) + float(v["max"])) / 2, 2)
            except (TypeError, ValueError):
                return None
        return None

    return _to_float(npk_obj.get("N")), _to_float(npk_obj.get("P2O5")), _to_float(npk_obj.get("K2O"))


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


def _resolve_variety(session, name_he: str) -> tuple[int | None, int | None]:
    """Return (crop_id, variety_id) for the default variety of name_he.

    Uses IL_CROP_MAP for spelling normalization.
    """
    from organic_market_agent.crop_book.constants import IL_CROP_MAP, DEFAULT_VARIETY_NAME_HE
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(name_he, name_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).first()
    if crop is None:
        logger.warning("WP-E openai_tier1: crop %r not in DB — skipped", name_he)
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

    Returns: {source_values_written, crops_skipped, crops_processed}
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value

    if not DATA_FILE.exists():
        logger.warning("WP-E: data file not found: %s", DATA_FILE)
        return {"source_values": 0, "skipped": 0, "processed": 0}

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    crops = data.get("crops", [])

    sv_count = 0
    skip_count = 0
    processed_count = 0

    for crop_dict in crops:
        crop_id_key = crop_dict.get("crop_id", "")
        name_he = OPENAI_CROP_MAP.get(crop_id_key)
        if not name_he:
            logger.warning("WP-E: no Hebrew mapping for crop_id=%r — skipped", crop_id_key)
            skip_count += 1
            continue

        _, variety_id = _resolve_variety(session, name_he)
        if variety_id is None:
            skip_count += 1
            continue

        processed_count += 1

        def _write(field_name, *, value_text=None, value_numeric=None, unit=None, note=None):
            nonlocal sv_count
            if value_text is None and value_numeric is None:
                return
            sv = _make_sv(variety_id, field_name,
                          value_text=value_text, value_numeric=value_numeric,
                          unit=unit, note=note)
            _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
            sv_count += 1

        # ── DTM ────────────────────────────────────────────────────────────
        dtm_obj = crop_dict.get("days_to_maturity")
        if dtm_obj:
            dtm_val, dtm_note = _extract_dtm(dtm_obj)
            _write("days_to_maturity", value_numeric=dtm_val, unit="days", note=dtm_note)

        # ── Germination temperature ────────────────────────────────────────
        germ = crop_dict.get("seed_germination")
        if germ:
            germ_min = _get_simple_numeric(germ, "min_c")
            germ_max = _get_simple_numeric(germ, "max_c")
            germ_note = f"opt {germ.get('opt_c', {})}; orig={germ.get('original_units', '')}"[:500]
            _write("germination_temp_c_min", value_numeric=germ_min, unit="°C", note=germ_note)
            _write("germination_temp_c_max", value_numeric=germ_max, unit="°C")

        # ── Soil pH ────────────────────────────────────────────────────────
        ph = crop_dict.get("soil_pH_preference")
        if ph:
            _write("soil_ph_target",
                   value_numeric=_get_simple_numeric(ph, "target_pH"))
            _write("soil_ph_liming_threshold",
                   value_numeric=_get_simple_numeric(ph, "liming_threshold_pH"))

        # ── Frost tolerance ────────────────────────────────────────────────
        frost = crop_dict.get("frost_tolerance_class")
        if frost:
            _write("frost_tolerance_class", value_text=frost.get("value"))

        # ── Nutrient removal N/P/K ─────────────────────────────────────────
        npk = crop_dict.get("nutrient_removal_N_P_K")
        if npk:
            n_val, p2o5_val, k2o_val = _extract_npk(npk)
            basis = npk.get("basis", "")
            npk_note = f"basis={basis}"[:300]
            _write("nutrient_removal_n_kg_ha", value_numeric=n_val, unit="kg/ha", note=npk_note)
            _write("nutrient_removal_p2o5_kg_ha", value_numeric=p2o5_val, unit="kg/ha")
            _write("nutrient_removal_k2o_kg_ha", value_numeric=k2o_val, unit="kg/ha")

        # ── Postharvest storage ────────────────────────────────────────────
        storage = crop_dict.get("postharvest_storage")
        if storage:
            temp_min, temp_max, rh_min, rh_max = _extract_temp_rh(storage)
            stage_note = storage.get("for_stage", "")
            _write("storage_temp_c_min", value_numeric=temp_min, unit="°C",
                   note=f"stage={stage_note}"[:200] if stage_note else None)
            _write("storage_temp_c_max", value_numeric=temp_max, unit="°C")
            _write("storage_rh_pct_min", value_numeric=rh_min, unit="%")
            _write("storage_rh_pct_max", value_numeric=rh_max, unit="%")

            eth = _extract_ethylene_sensitivity(storage)
            _write("storage_ethylene_sensitivity", value_text=eth)

            life_text = _extract_storage_life(storage)
            _write("storage_life_text", value_text=life_text)

    session.flush()
    logger.info(
        "WP-E openai_tier1: %d source_values, %d crops processed, %d skipped",
        sv_count, processed_count, skip_count,
    )
    return {"source_values": sv_count, "processed": processed_count, "skipped": skip_count}
