"""Curtis Stone OCR narrative importer (L41 cached JSONs) — WP-C3 §6.

Source: data/external_sources/extracted/curtis_ocr/L41_curtis_chart_NN.json
Target: crop_knowledge_notes with source='NI:curtis_stone_book'
When a page covers ≤_AMBIGUITY_THRESHOLD crops, we upsert one note per crop
(same narrative_text body) so each crop gets NI coverage.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.urban_farmer._shared import (
    CURTIS_CROP_MAP,
    CURTIS_OCR_DIR,
    ImportSummary,
)

logger = logging.getLogger(__name__)

SOURCE = "NI:curtis_stone_book"
_BODY_MAX = 2000

# Additional OCR → Hebrew mappings beyond the main CURTIS_CROP_MAP
_OCR_EXTRA_MAP: dict[str, str] = {
    "Pea shoots": "אפונה",
    "Pea Shoots": "אפונה",
    "Sunflower shoots": "חמנייה",
    "Sunflower Shoots": "חמנייה",
    "Cucumber": "מלפפון",
    "Tomato": "עגבנייה",
    "Tomatoes": "עגבנייה",
    "Pepper": "פלפל",
    "Lettuce": "חסה",
    "Carrot": "גזר",
    "Carrots": "גזר",
    "Turnip": "לפת",
    "Radish": "צנונית",
    "Spinach": "תרד",
    "Kale": "קייל",
    "Basil": "בזיל",
    "Beet": "סלק",
    "Hakurei": "לפת",
    "Tatsoi": "חסה",
    "Mustard": "ארוגולה",
}

# If ≤ this many distinct crops are found on a page, create one note per crop.
# Pages with more crops than this are summary/index pages — skip them.
_AMBIGUITY_THRESHOLD = 4


def _resolve_crops(crop_name: str, narrative: str) -> list[str]:
    """Return list of canonical Hebrew crop names for this page.

    First tries the `crop` field from the JSON. Falls back to keyword scanning
    narrative_text (tesseract often extracts page headers, not crop names).
    Returns one entry per distinct crop found when ≤_AMBIGUITY_THRESHOLD crops.
    """
    combined: dict[str, str] = {**CURTIS_CROP_MAP, **_OCR_EXTRA_MAP}

    # Direct / prefix match on the crop field
    canonical_he = combined.get(crop_name)
    if canonical_he is None:
        name_lower = crop_name.lower()
        for en, he in combined.items():
            if name_lower.startswith(en.lower()) or en.lower().startswith(name_lower):
                canonical_he = he
                break

    if canonical_he is not None:
        return [canonical_he]

    if not narrative:
        return []

    # Keyword scan — find all crops mentioned, deduplicate by Hebrew name
    text_lower = narrative.lower()
    he_to_count: dict[str, int] = {}
    for en, he in combined.items():
        cnt = text_lower.count(en.lower())
        if cnt:
            he_to_count[he] = he_to_count.get(he, 0) + cnt

    if not he_to_count:
        return []

    if len(he_to_count) > _AMBIGUITY_THRESHOLD:
        logger.debug(
            "Curtis OCR: %d crops on page — too ambiguous, skipping (%s...)",
            len(he_to_count), crop_name[:40],
        )
        return []

    logger.debug(
        "Curtis OCR: keyword-resolved %r → %s",
        crop_name[:40], list(he_to_count.keys()),
    )
    return list(he_to_count.keys())


def import_all(session: Session, ocr_dir: Path | None = None) -> ImportSummary:
    cache_dir = ocr_dir or CURTIS_OCR_DIR
    summary = ImportSummary()

    if not cache_dir.exists():
        logger.warning("Curtis OCR cache dir not found: %s — skipping", cache_dir)
        return summary

    from organic_market_agent.crop_book.models import Crop
    from organic_market_agent.crop_book.importer.ni_importer import _upsert_knowledge_note

    for json_path in sorted(cache_dir.glob("L41_curtis_chart_*.json")):
        try:
            data = json.loads(json_path.read_text())
        except Exception as exc:
            logger.warning("Cannot read %s: %s", json_path.name, exc)
            continue

        summary.rows_parsed += 1
        narrative = (data.get("narrative_text") or "").strip()
        crop_name = (data.get("crop") or "").strip()

        if not narrative or not crop_name:
            continue

        he_names = _resolve_crops(crop_name, narrative)
        if not he_names:
            summary.map_misses.append(crop_name)
            continue

        varieties = data.get("varieties") or []
        note_type = "cultivar_recommendation" if varieties else "growing_tip"
        body = narrative[:_BODY_MAX]

        upserted_any = False
        for he in he_names:
            crop = session.query(Crop).filter_by(name_he=he).one_or_none()
            if crop is None:
                logger.debug("Curtis OCR: %r not in DB — skipping", he)
                continue
            _upsert_knowledge_note(
                session,
                crop_id=crop.id,
                source=SOURCE,
                note_type=note_type,
                body_text=body,
            )
            upserted_any = True

        if upserted_any:
            summary.rows_upserted += 1
        else:
            summary.map_misses.append(crop_name)

    logger.info(
        "Curtis OCR: parsed=%d upserted=%d map_misses=%d",
        summary.rows_parsed, summary.rows_upserted, len(summary.map_misses),
    )
    return summary
