"""JmfFtSeedingincellflatImporter — L16 seeding in cell flats guide.

SFA-S003-P002-WP-C2 LOD400 §4.
Reads cached JSON from data/external_sources/extracted/jmf_ft_seedingincellflats/.
FT table format (_table.json); English crop names resolved via JMF_CROP_MAP.
Populates: nursery_specific.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

_SOURCE_NOTE_TYPE = "nursery_specific"


class JmfFtSeedingincellflatImporter(NIImporter):
    name = "jmf_ft_seedingincellflats_v1"
    cache_dir = Path("data/external_sources/extracted/jmf_ft_seedingincellflats")
    canonical_pdf_filename = "L16_seeding_in_cell_flats.pdf"
    _table_file = "_table.json"

    def _iter_cache_entries(self):
        table_path = self.cache_dir / self._table_file
        if not table_path.exists():
            return
        try:
            data = json.loads(table_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("%s: failed to load %s — %s", self.name, table_path, exc)
            return
        crops = data.get("crops", {})
        provenance = data.get("provenance", {})
        for crop_jmf_en, notes in crops.items():
            yield crop_jmf_en, notes, provenance

    def _resolve_crop_id(self, session, crop_jmf_en: str) -> int | None:
        from organic_market_agent.crop_book.constants import JMF_CROP_MAP
        from organic_market_agent.crop_book.models import Crop

        name_he = JMF_CROP_MAP.get(crop_jmf_en)
        if name_he is None:
            logger.warning("%s: crop_jmf_en=%r not in JMF_CROP_MAP — skipped", self.name, crop_jmf_en)
            return None
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("%s: name_he=%r not in DB — skipped", self.name, name_he)
            return None
        return crop.id

    def load(self, session) -> list[dict[str, Any]]:
        return []

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        rows = []
        for crop_jmf_en, notes, provenance in self._iter_cache_entries():
            body = notes.get(_SOURCE_NOTE_TYPE)
            if not body:
                continue
            body = str(body)
            if len(body) > 2000:
                body = body[:2000]
            crop_id = self._resolve_crop_id(session, crop_jmf_en)
            if crop_id is None:
                continue
            rows.append({
                "crop_id": crop_id,
                "source": self.source_label,
                "trust_tier": "NI",
                "note_type": _SOURCE_NOTE_TYPE,
                "body_text": body,
                "provenance_pdf": provenance.get("pdf") or self.canonical_pdf_filename,
                "provenance_pages": provenance.get("pages"),
                "is_internal_farm_use_only": True,
                "extraction_model": provenance.get("extraction_model"),
                "extracted_at": provenance.get("extracted_at"),
            })
        return rows
