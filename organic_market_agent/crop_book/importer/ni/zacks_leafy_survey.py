"""ZacksLeafySurveyImporter — L10 Dr. Zacks leafy hydro survey.

SFA-S003-P002-WP-C2 LOD400 §4.
Reads cached JSON from data/external_sources/extracted/zacks_leafy_survey/.
Per-crop JSON files with Hebrew crop_he key.
Populates: hydro_suitability (potentially low-yield source per AC-C2-06).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

# WP-C2 deepening (2026-05-28): the L10 source is a 52-slide image deck that
# the original text-extraction missed entirely (0 notes). Re-extracted via
# vision by Claude; expanded beyond hydro_suitability to capture the deck's
# disease, variety-trial, cultivar and harvest data. All within the
# crop_knowledge_notes.note_type CHECK constraint (migration 053).
_SOURCE_NOTE_TYPES = (
    "hydro_suitability",
    "pest_disease",
    "variety_trial_score",
    "cultivar_recommendation",
    "harvest_marker",
)


class ZacksLeafySurveyImporter(NIImporter):
    name = "zacks_leafy_survey_v1"
    cache_dir = Path("data/external_sources/extracted/zacks_leafy_survey")
    canonical_pdf_filename = "L10_DR_ZACKS_leafy_hydro_survey.pdf"

    def _iter_cache_files(self):
        if not self.cache_dir.exists():
            return
        for path in sorted(self.cache_dir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
                if entry.get("schema_version") != "1.0":
                    raise ValueError(f"{path}: missing or wrong schema_version")
                if "crop_he" not in entry:
                    raise ValueError(f"{path}: missing crop_he")
                yield entry["crop_he"], entry.get("notes", {}), entry.get("provenance", {})
            except (ValueError, json.JSONDecodeError, KeyError) as exc:
                logger.warning("%s: skipping %s — %s", self.name, path.name, exc)

    def _resolve_crop_id(self, session, crop_he: str) -> int | None:
        from organic_market_agent.crop_book.constants import IL_CROP_MAP
        from organic_market_agent.crop_book.models import Crop

        canonical_he = IL_CROP_MAP.get(crop_he, crop_he)
        crop = session.query(Crop).filter_by(name_he=canonical_he).one_or_none()
        if crop is None and canonical_he != crop_he:
            crop = session.query(Crop).filter_by(name_he=crop_he).one_or_none()
        if crop is None:
            logger.warning("%s: crop_he=%r not in DB — skipped", self.name, crop_he)
            return None
        return crop.id

    def load(self, session) -> list[dict[str, Any]]:
        return []

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        rows = []
        for crop_he, notes, provenance in self._iter_cache_files():
            crop_id = self._resolve_crop_id(session, crop_he)
            if crop_id is None:
                continue
            for note_type in _SOURCE_NOTE_TYPES:
                body = notes.get(note_type)
                if not body:
                    continue
                body = str(body)
                if len(body) > 2000:
                    body = body[:2000]
                rows.append({
                    "crop_id": crop_id,
                    "source": self.source_label,
                    "trust_tier": "NI",
                    "note_type": note_type,
                    "body_text": body,
                    "provenance_pdf": provenance.get("pdf") or self.canonical_pdf_filename,
                    "provenance_pages": provenance.get("pages"),
                    "is_internal_farm_use_only": True,
                    "extraction_model": provenance.get("extraction_model"),
                    "extracted_at": provenance.get("extracted_at"),
                })
        return rows
