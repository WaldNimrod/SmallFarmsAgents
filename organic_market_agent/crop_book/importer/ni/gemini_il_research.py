"""WP-H: Gemini IL Research Importer — Israeli-context vegetable crop data.

Reads from:
  data/external_sources/web/gemini_il_research/sfa_gemini_crops_2026-05-27.json

20 complete crop records extracted from Gemini deep-research session (2026-05-27).
Covers 11 crops NOT in OpenAI report: sweet_potato, okra, fava_bean, chicory,
chickpea, sesame, sunflower, wheat, blackberry, chinese_cabbage, brussels_sprouts.
Also fills edamame germination + postharvest (missing from OpenAI).

NOTE: NPK values are in ELEMENTAL form (N/P/K), not oxide (N/P₂O₅/K₂O).
      Stored in separate field_names: nutrient_removal_p_kg_ha, nutrient_removal_k_kg_ha.
      'half-hardy' frost class normalized to 'semi_hardy' to match existing schema.

Source label: WR:gemini_il_research_v1
Trust tier:   WR (Web Research)
Confidence:   0.70

Fields written to crop_variety_source_values:
  days_to_maturity, germination_temp_c_min, germination_temp_c_max,
  soil_ph_target, soil_ph_liming_threshold, frost_tolerance_class,
  nutrient_removal_n_kg_ha, nutrient_removal_p_kg_ha, nutrient_removal_k_kg_ha,
  storage_temp_c_min, storage_temp_c_max,
  storage_rh_pct_min, storage_rh_pct_max,
  storage_ethylene_sensitivity, storage_life_days
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "WR:gemini_il_research_v1"
TRUST = "WR"
CONFIDENCE = 0.70

DATA_FILE = Path("data/external_sources/web/gemini_il_research/sfa_gemini_crops_2026-05-27.json")

# Map Gemini crop_id → Hebrew name_he for DB lookup
GEMINI_CROP_MAP: dict[str, str] = {
    "cauliflower":      "כרובית",
    "sweet_potato":     "בטטה",
    "okra":             "במיה",
    "fava_bean":        "פול",
    "watermelon":       "אבטיח",
    "sweet_corn":       "תירס",       # IL_CROP_MAP: "תירס מתוק" → "תירס"
    "potato":           "תפוח אדמה",
    "edamame":          "אדממה",
    "chicory":          "ציקוריה",
    "chickpea":         "חומוס",
    "sesame":           "שומשום",
    "sunflower":        "חמניה",
    "wheat":            "חיטה",
    "soybean":          "סויה",
    "blackberry":       "אוסנה",
    "beet":             "סלק",
    "broccoli":         "ברוקולי",
    "cabbage":          "כרוב",
    "chinese_cabbage":  "כרוב סיני",
    "brussels_sprouts": "כרוב ניצנים",
}

# Normalize Gemini frost class values to our schema vocabulary
_FROST_NORMALIZE: dict[str, str] = {
    "half-hardy": "semi_hardy",
    "semihardy":  "semi_hardy",
    "very_tender": "very_tender",
    "tender":     "tender",
    "hardy":      "hardy",
}


def _resolve_variety(session, name_he: str) -> tuple[int | None, int | None]:
    """Return (crop_id, variety_id) for the default variety of name_he."""
    from organic_market_agent.crop_book.constants import IL_CROP_MAP, DEFAULT_VARIETY_NAME_HE
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(name_he, name_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).first()
    if crop is None:
        logger.debug("WP-H gemini: crop_he=%r not in DB — skipped", name_he)
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

    Returns: {source_values_written, crops_processed, crops_skipped}
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value

    if not DATA_FILE.exists():
        logger.warning("WP-H: data file not found: %s", DATA_FILE)
        return {"source_values": 0, "processed": 0, "skipped": 0}

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    crops = data.get("crops", [])

    sv_count = 0
    skip_count = 0
    processed_count = 0

    for crop_dict in crops:
        crop_id_key = crop_dict.get("crop_id", "")
        name_he = GEMINI_CROP_MAP.get(crop_id_key)
        if not name_he:
            logger.warning("WP-H: no Hebrew mapping for crop_id=%r — skipped", crop_id_key)
            skip_count += 1
            continue

        _, variety_id = _resolve_variety(session, name_he)
        if variety_id is None:
            skip_count += 1
            continue

        processed_count += 1

        def _w(field_name, *, vt=None, vn=None, unit=None, note=None):
            nonlocal sv_count
            if vt is None and vn is None:
                return
            sv = _make_sv(variety_id, field_name,
                          value_text=vt, value_numeric=vn, unit=unit, note=note)
            _upsert_source_value(session, variety_id, {k: v for k, v in sv.items() if k != "variety_id"})
            sv_count += 1

        # ── DTM ────────────────────────────────────────────────────────────
        dtm = crop_dict.get("DTM", {})
        if dtm:
            mn = dtm.get("min_days")
            mx = dtm.get("max_days")
            stage = dtm.get("harvest_stage", "")
            if mn is not None and mx is not None:
                try:
                    mid = round((float(mn) + float(mx)) / 2, 1)
                    _w("days_to_maturity", vn=mid, unit="days",
                       note=f"range {int(mn)}-{int(mx)} days; stage={stage}"[:500])
                except (TypeError, ValueError):
                    pass

        # ── Germination ────────────────────────────────────────────────────
        germ = crop_dict.get("germination_temp_c", {})
        if germ:
            gmin = germ.get("min")
            gmax = germ.get("max")
            gopt = germ.get("opt")
            if gmin is not None:
                try:
                    _w("germination_temp_c_min", vn=float(gmin), unit="°C",
                       note=f"opt={gopt}°C" if gopt is not None else None)
                except (TypeError, ValueError):
                    pass
            if gmax is not None:
                try:
                    _w("germination_temp_c_max", vn=float(gmax), unit="°C")
                except (TypeError, ValueError):
                    pass

        # ── Soil pH ────────────────────────────────────────────────────────
        ph = crop_dict.get("soil_pH", {})
        if ph:
            if ph.get("target") is not None:
                try:
                    _w("soil_ph_target", vn=float(ph["target"]))
                except (TypeError, ValueError):
                    pass
            if ph.get("liming_threshold") is not None:
                try:
                    _w("soil_ph_liming_threshold", vn=float(ph["liming_threshold"]))
                except (TypeError, ValueError):
                    pass

        # ── Frost tolerance ────────────────────────────────────────────────
        frost_raw = crop_dict.get("frost_tolerance_class")
        if frost_raw:
            frost_norm = _FROST_NORMALIZE.get(str(frost_raw).lower(), str(frost_raw))
            _w("frost_tolerance_class", vt=frost_norm)

        # ── NPK (elemental form: N, P, K — not oxide) ──────────────────────
        npk = crop_dict.get("nutrient_removal_N_P_K", {})
        if npk:
            if npk.get("N") is not None:
                try:
                    _w("nutrient_removal_n_kg_ha", vn=float(npk["N"]), unit="kg/ha",
                       note="elemental N")
                except (TypeError, ValueError):
                    pass
            if npk.get("P") is not None:
                try:
                    _w("nutrient_removal_p_kg_ha", vn=float(npk["P"]), unit="kg/ha",
                       note="elemental P (not P2O5)")
                except (TypeError, ValueError):
                    pass
            if npk.get("K") is not None:
                try:
                    _w("nutrient_removal_k_kg_ha", vn=float(npk["K"]), unit="kg/ha",
                       note="elemental K (not K2O)")
                except (TypeError, ValueError):
                    pass

        # ── Postharvest storage ────────────────────────────────────────────
        stor = crop_dict.get("postharvest_storage", {})
        if stor:
            tc = stor.get("temp_c")
            rh = stor.get("RH_pct")
            eth = stor.get("ethylene_sensitivity")
            life = stor.get("storage_life_days")
            if tc is not None:
                try:
                    _w("storage_temp_c_min", vn=float(tc), unit="°C")
                    _w("storage_temp_c_max", vn=float(tc), unit="°C")
                except (TypeError, ValueError):
                    pass
            if rh is not None:
                try:
                    _w("storage_rh_pct_min", vn=float(rh), unit="%")
                    _w("storage_rh_pct_max", vn=float(rh), unit="%")
                except (TypeError, ValueError):
                    pass
            if eth:
                _w("storage_ethylene_sensitivity", vt=str(eth))
            if life is not None:
                try:
                    _w("storage_life_days", vn=float(life), unit="days")
                except (TypeError, ValueError):
                    pass

    session.flush()
    logger.info(
        "WP-H gemini_il_research: %d source_values, %d crops processed, %d skipped",
        sv_count, processed_count, skip_count,
    )
    return {"source_values": sv_count, "processed": processed_count, "skipped": skip_count}
