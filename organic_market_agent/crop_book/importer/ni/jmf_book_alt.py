"""JmfBookAltImporter — Market Gardener 209-page alternate edition.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2 (Q5 addition).

Same note_type set as jmf_book (8 book types).
Different source label, so both can coexist in crop_knowledge_notes per AC-16.
NOT registered with ni_registry (see __init__.py rationale).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)


class JmfBookAltImporter(NIImporter):
    name = "jmf_book_alt_v1"
    cache_dir = Path("data/jmf/extracted/jmf_book_alt")
    canonical_pdf_filename = "THE MARKET GARDENER_*.PDF"

    def _iter_cache_files(self):
        if not self.cache_dir.exists():
            return
        yield from sorted(self.cache_dir.glob("*.json"))

    def _load_cache_file(self, path: Path) -> dict:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != "1.0":
            raise ValueError(f"{path}: missing or wrong schema_version")
        if "crop_jmf_en" not in data:
            raise ValueError(f"{path}: missing crop_jmf_en")
        if "notes" not in data or not isinstance(data["notes"], dict):
            raise ValueError(f"{path}: missing or invalid notes dict")
        from organic_market_agent.crop_book.crop_knowledge_notes import NOTE_TYPE_VALUES
        for key in data["notes"]:
            if key not in NOTE_TYPE_VALUES:
                raise ValueError(f"{path}: unknown note_type key: {key!r}")
        for nt, body in data["notes"].items():
            if body is not None and len(body) > 2000:
                raise ValueError(f"{path}: note_type={nt!r} body_text > 2000 chars")
        return data

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
        """Return variety-source-value rows for cultivar_recommendation only."""
        rows = []
        for path in self._iter_cache_files():
            try:
                data = self._load_cache_file(path)
            except (ValueError, json.JSONDecodeError) as exc:
                logger.warning("%s: skipping %s — %s", self.name, path.name, exc)
                continue
            crop_jmf_en = data["crop_jmf_en"]
            cultivar = data["notes"].get("cultivar_recommendation")
            if not cultivar:
                continue
            variety_id = self._resolve_default_variety_id(session, crop_jmf_en)
            if variety_id is None:
                continue
            provenance = data.get("provenance", {})
            rows.append(
                {
                    "variety_id": variety_id,
                    "field_name": "cultivar_recommendation",
                    "source": self.source_label,
                    "value_text": cultivar[:2000],
                    "value_numeric": None,
                    "unit": None,
                    "note": (
                        f"From {self.canonical_pdf_filename} pages "
                        f"{provenance.get('pages', 'N/A')}"
                    ),
                    "trust_tier": "NI",
                    "confidence_weight": None,
                    "is_outlier_rejected": False,
                }
            )
        return rows

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        """Return fully-resolved crop_knowledge_notes row dicts."""
        rows = []
        for path in self._iter_cache_files():
            try:
                data = self._load_cache_file(path)
            except (ValueError, json.JSONDecodeError) as exc:
                logger.warning("%s: skipping %s — %s", self.name, path.name, exc)
                continue
            crop_jmf_en = data["crop_jmf_en"]
            crop_id = self._resolve_crop_id(session, crop_jmf_en)
            if crop_id is None:
                continue
            provenance = data.get("provenance", {})
            for note_type, body in data["notes"].items():
                if not body:
                    continue
                rows.append(
                    {
                        "crop_id": crop_id,
                        "source": self.source_label,
                        "trust_tier": "NI",
                        "note_type": note_type,
                        "body_text": body,
                        "provenance_pdf": provenance.get("pdf"),
                        "provenance_pages": provenance.get("pages"),
                        "is_internal_farm_use_only": True,
                        "extraction_model": provenance.get("extraction_model"),
                        "extracted_at": provenance.get("extracted_at"),
                    }
                )
        return rows
