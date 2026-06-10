"""JmfBookImporter — Market Gardener 240-page main edition.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.2.

Subclass of WP-A NIImporter. Reads cached JSON from
data/jmf/extracted/jmf_book/<crop>.json. Produces:
  - 0-or-1 variety-source-value row per crop (cultivar_recommendation)
    via load() — goes through WP-A standard NI path
  - 0..8 crop_knowledge_notes rows per crop via load_knowledge_notes()
    — goes through the B2-specific path

NOT registered with ni_registry (see __init__.py rationale).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

# Note types produced by this source (8 JMF book types)
_SOURCE_NOTE_TYPES = (
    "pest_disease",
    "harvest_marker",
    "storage_handling",
    "rotation_companion",
    "cultivar_recommendation",
    "growing_tip",
    "irrigation",
    "nursery_specific",
)


class JmfBookImporter(NIImporter):
    name = "jmf_book_v1"
    cache_dir = Path("data/jmf/extracted/jmf_book")
    canonical_pdf_filename = (
        "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF"
    )

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
        # Validate note_type keys
        from organic_market_agent.crop_book.crop_knowledge_notes import NOTE_TYPE_VALUES
        for key in data["notes"]:
            if key not in NOTE_TYPE_VALUES:
                raise ValueError(f"{path}: unknown note_type key: {key!r}")
        # Validate body_text lengths
        for nt, body in data["notes"].items():
            if body is not None and len(body) > 2000:
                raise ValueError(f"{path}: note_type={nt!r} body_text > 2000 chars")
        return data

    def _resolve_crop_id(self, session, crop_jmf_en: str) -> int | None:
        """Resolve JMF English crop name -> crops.id via JMF_CROP_MAP.

        Returns None on miss (logs WARN). Shared helper used by both
        load() and load_knowledge_notes().
        """
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
        """Resolve crop_jmf_en -> default-baseline variety_id (name_en IS NULL).

        Mirrors B1's _default_variety_id helper (jmf_masterclass.py).
        Returns None on miss.
        """
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
        """Return variety-source-value rows for cultivar_recommendation only.

        Each row is fully-resolved (variety_id present) per the
        `_upsert_source_value(session, variety_id, sv)` call contract.
        Session is required — used to resolve crop_jmf_en -> variety_id.

        B2-specific signature (adds `session` param vs. WP-A base abstract `load()`).
        B2 subclasses are NOT auto-registered with ni_registry per §7.1.
        """
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
            # Normalize: cultivar_recommendation may be a list of note-dicts (current extraction:
            # [{"body_text": ..., "page_ref": ...}, ...]) or a plain string (legacy). value_text is
            # a Text column, so flatten to the joined body_text (a list would raise "can't adapt dict").
            if isinstance(cultivar, list):
                cultivar_text = " ".join(
                    str((c.get("body_text") if isinstance(c, dict) else c) or "").strip()
                    for c in cultivar
                ).strip()
            else:
                cultivar_text = str(cultivar).strip()
            if not cultivar_text:
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
                    "value_text": cultivar_text[:2000],
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
        """Return fully-resolved crop_knowledge_notes row dicts.

        Each row has `crop_id` (resolved from crop_jmf_en via session lookup);
        ready for `_upsert_knowledge_note(session, crop_id=..., **rest)`.
        """
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
                # body may be a list of note-dicts ([{"body_text": ...}, ...]), a single dict,
                # or a string — flatten to text (body_text is a Text column, max 2000 chars).
                if isinstance(body, list):
                    body_text = " ".join(
                        str((b.get("body_text") if isinstance(b, dict) else b) or "").strip()
                        for b in body
                    ).strip()
                elif isinstance(body, dict):
                    body_text = str(body.get("body_text") or "").strip()
                else:
                    body_text = str(body).strip()
                if not body_text:
                    continue
                body_text = body_text[:2000]
                rows.append(
                    {
                        "crop_id": crop_id,
                        "source": self.source_label,
                        "trust_tier": "NI",
                        "note_type": note_type,
                        "body_text": body_text,
                        "provenance_pdf": provenance.get("pdf"),
                        "provenance_pages": provenance.get("pages"),
                        "is_internal_farm_use_only": True,
                        "extraction_model": provenance.get("extraction_model"),
                        "extracted_at": provenance.get("extracted_at"),
                    }
                )
        return rows
