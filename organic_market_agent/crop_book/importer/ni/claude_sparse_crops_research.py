"""WP-C6: Claude Sparse-Crops Research Importer — WR-tier agronomic data.

Reads from:
  data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json

Brings the 19 "sparse" crops (<=2 enriched fields after WP-C5) up to >=6 enriched
fields each. Values are AI-synthesized (Claude in-session, $0) — the WR trust tier
(weight 0.60, added in WP-C5) exists precisely for this. Recommend PR-tier
cross-check before promotion to higher confidence.

Source label: WR:claude_sparse_crops_v1
Trust tier:   WR (Web Research / AI-synthesized)
Confidence:   0.60

Pack schema (flat): crops[].fields maps an existing canonical field_name ->
{value, unit, note}. No new field_names are introduced. Mirrors the ingest()
contract of ni/gemini_il_research.py.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SOURCE = "WR:claude_sparse_crops_v1"
TRUST = "WR"
CONFIDENCE = 0.60

DATA_FILE = Path(
    "data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json"
)

# Map pack crop_id -> DB crops.name_he (exact). The 19 sparse crops (WP-C6 LOD400 §2).
CLAUDE_SPARSE_CROP_MAP: dict[str, str] = {
    "anise_hyssop":        "אזוב מצוי",
    "lemon_balm":          "לימון בלם",
    "mint":                "נענע",
    "sage":                "מרווה",
    "tarragon":            "טרגון",
    "thyme":               "טימין",
    "hibiscus":            "היביסקוס",
    "lemon_verbena":       "לימון ורבנה",
    "lovage":              "לובסטייה",
    "turmeric":            "כורכום",
    "ginger":              "ג'ינג'ר",
    "chinese_lantern":     "פנס סיני",
    "watercress":          "גרגר נחלים",
    "jerusalem_artichoke": "ארטישוק ירושלמי",
    "jicama":              "ג'יקמה",
    "salad_mix":           "עלי בייבי",
    "pac_choi":            "פאק צ'וי",
    "bay":                 "דפנה",
    "oranges":             "תפוז",
}

# Categorical (text) fields — everything else is treated as numeric.
_TEXT_FIELDS = {"frost_tolerance_class"}


def _resolve_variety(session, name_he: str) -> tuple[int | None, int | None]:
    """Return (crop_id, variety_id) for the default variety of name_he."""
    from organic_market_agent.crop_book.constants import IL_CROP_MAP, DEFAULT_VARIETY_NAME_HE
    from organic_market_agent.crop_book.models import Crop, CropVariety

    canonical = IL_CROP_MAP.get(name_he, name_he)
    crop = session.query(Crop).filter_by(name_he=canonical).first()
    if crop is None and canonical != name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).first()
    if crop is None:
        logger.warning("WP-C6: crop_he=%r not in DB — skipped", name_he)
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


def _make_sv(field_name: str, *,
             value_text: str | None = None,
             value_numeric: float | None = None,
             unit: str | None = None,
             note: str | None = None) -> dict[str, Any]:
    return {
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

    Returns: {source_values, processed, skipped}
    """
    from organic_market_agent.crop_book.importer.seed import _upsert_source_value

    if not DATA_FILE.exists():
        logger.warning("WP-C6: data file not found: %s", DATA_FILE)
        return {"source_values": 0, "processed": 0, "skipped": 0}

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    crops = data.get("crops", [])

    sv_count = 0
    skip_count = 0
    processed_count = 0

    for crop_dict in crops:
        crop_id_key = crop_dict.get("crop_id", "")
        name_he = CLAUDE_SPARSE_CROP_MAP.get(crop_id_key)
        if not name_he:
            logger.warning("WP-C6: no Hebrew mapping for crop_id=%r — skipped", crop_id_key)
            skip_count += 1
            continue

        _, variety_id = _resolve_variety(session, name_he)
        if variety_id is None:
            skip_count += 1
            continue

        processed_count += 1
        fields = crop_dict.get("fields", {})

        for field_name, spec in fields.items():
            if not isinstance(spec, dict):
                continue
            value = spec.get("value")
            if value is None:
                continue
            unit = spec.get("unit")
            note = spec.get("note")
            if field_name in _TEXT_FIELDS or isinstance(value, str):
                sv = _make_sv(field_name, value_text=str(value), unit=unit, note=note)
            else:
                try:
                    sv = _make_sv(field_name, value_numeric=float(value), unit=unit, note=note)
                except (TypeError, ValueError):
                    logger.warning("WP-C6: non-numeric value %r for %s/%s — skipped",
                                   value, name_he, field_name)
                    continue
            _upsert_source_value(session, variety_id, sv)
            sv_count += 1

    logger.info("WP-C6 claude_sparse_crops: %d source values, %d crops processed, %d skipped",
                sv_count, processed_count, skip_count)
    return {"source_values": sv_count, "processed": processed_count, "skipped": skip_count}
