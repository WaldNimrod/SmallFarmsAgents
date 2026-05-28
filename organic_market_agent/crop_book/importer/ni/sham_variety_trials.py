"""ShamVarietyTrialsImporter — L11 Israeli variety trials 2021.

SFA-S003-P002-WP-C2 LOD400 §4.
Reads cached JSON from data/external_sources/extracted/sham_variety_trials/_table.json.
Table format: crops keyed by Hebrew crop name.
Populates: variety_trial_score.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

# WP-C2 deepening (2026-05-28): the L11 PDF carries quantitative trial tables
# (nutrient solution chemistry, per-variety weights, quality traits) the
# original extraction reduced to a single score summary. Expanded to capture
# the full agronomic depth. All within migration-053 note_type CHECK.
_SOURCE_NOTE_TYPES = (
    "variety_trial_score",
    "cultivar_recommendation",
    "hydro_suitability",
    "pest_disease",
    "harvest_marker",
)


class ShamVarietyTrialsImporter(NIImporter):
    name = "sham_variety_trials_v1"
    cache_dir = Path("data/external_sources/extracted/sham_variety_trials")
    canonical_pdf_filename = "L11_variety_trials_2021.pdf"
    _table_file = "_table.json"

    def _iter_cache_entries(self):
        """Yield (crop_he, notes_dict, provenance_dict) from _table.json."""
        table_path = self.cache_dir / self._table_file
        if not table_path.exists():
            return
        try:
            data = json.loads(table_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("%s: failed to load %s — %s", self.name, table_path, exc)
            return
        if data.get("schema_version") != "1.0":
            logger.warning("%s: missing or wrong schema_version in %s", self.name, table_path)
            return
        crops = data.get("crops", {})
        provenance = data.get("provenance", {})
        for crop_he, notes in crops.items():
            yield crop_he, notes, provenance

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
        for crop_he, notes, provenance in self._iter_cache_entries():
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
