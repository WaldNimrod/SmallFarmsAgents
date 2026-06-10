"""JmfFtFlameweedImporter — FT_FLAMEWEEDING (3pp).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2.

Reads a single _table.json file at data/jmf/extracted/jmf_ft_flameweed/_table.json.
Populates note_type='flame_weed_timing' only.
NOT registered with ni_registry (see __init__.py rationale).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

_SOURCE_NOTE_TYPE = "flame_weed_timing"


class JmfFtFlameweedImporter(NIImporter):
    name = "jmf_ft_flameweed_v1"
    cache_dir = Path("data/jmf/extracted/jmf_ft_flameweed")
    canonical_pdf_filename = "FT_FINALE_FLAMEWEEDING.PDF"
    _table_file = "_table.json"

    def _load_table(self) -> dict:
        """Load the single-file FT table JSON.

        Returns a dict mapping crop_jmf_en -> {note_type: body_text, ..., provenance: {...}}.
        Also accepts per-crop JSON files (*.json excluding _table.json).
        """
        table_path = self.cache_dir / self._table_file
        if table_path.exists():
            data = json.loads(table_path.read_text(encoding="utf-8"))
            if data.get("schema_version") != "1.0":
                raise ValueError(f"{table_path}: missing or wrong schema_version")
            return data
        # Fallback: individual per-crop files
        return {}

    def _iter_cache_files(self):
        """Yield (crop_jmf_en, notes_dict, provenance_dict) tuples."""
        if not self.cache_dir.exists():
            return
        # Single-table style
        table_path = self.cache_dir / self._table_file
        if table_path.exists():
            data = json.loads(table_path.read_text(encoding="utf-8"))
            crops = data.get("crops", {})
            provenance = data.get("provenance", {})
            for crop_jmf_en, notes in crops.items():
                yield crop_jmf_en, notes, provenance
            return
        # Per-crop file style (for test fixtures)
        for path in sorted(self.cache_dir.glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
                if entry.get("schema_version") != "1.0":
                    raise ValueError(f"{path}: missing or wrong schema_version")
                yield entry["crop_jmf_en"], entry.get("notes", {}), entry.get("provenance", {})
            except (ValueError, json.JSONDecodeError, KeyError) as exc:
                logger.warning("%s: skipping %s — %s", self.name, path.name, exc)

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

    def _resolve_default_variety_id(self, session, crop_jmf_en: str) -> int | None:
        from organic_market_agent.crop_book.models import CropVariety

        crop_id = self._resolve_crop_id(session, crop_jmf_en)
        if crop_id is None:
            return None
        v = (
            session.query(CropVariety)
            .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
            .order_by(CropVariety.is_default.desc(), CropVariety.id)
            .first()
        )
        if v is None:
            v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
            session.add(v)
            session.flush()
        return v.id

    def load(self, session) -> list[dict[str, Any]]:
        """FT sources do not produce cultivar_recommendation rows; returns empty list."""
        return []

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        """Return crop_knowledge_notes rows for flame_weed_timing."""
        rows = []
        for crop_jmf_en, notes, provenance in self._iter_cache_files():
            body = notes.get(_SOURCE_NOTE_TYPE)
            if not body:
                continue
            if len(body) > 2000:
                logger.warning("%s: %r body_text > 2000 chars — truncating", self.name, crop_jmf_en)
                body = body[:2000]
            crop_id = self._resolve_crop_id(session, crop_jmf_en)
            if crop_id is None:
                continue
            rows.append(
                {
                    "crop_id": crop_id,
                    "source": self.source_label,
                    "trust_tier": "NI",
                    "note_type": _SOURCE_NOTE_TYPE,
                    "body_text": body,
                    "provenance_pdf": provenance.get("pdf"),
                    "provenance_pages": provenance.get("pages"),
                    "is_internal_farm_use_only": True,
                    "extraction_model": provenance.get("extraction_model"),
                    "extracted_at": provenance.get("extracted_at"),
                }
            )
        return rows
