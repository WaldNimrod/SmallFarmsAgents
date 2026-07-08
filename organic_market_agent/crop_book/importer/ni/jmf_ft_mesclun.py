"""JmfFtMesclunImporter — L39 mesclun guide (The Market Gardener's Masterclass).

SFA-S003-P004-WP-CB-SRC-SWEEP.

team_00 (2026-06-10): the crop 'עלי בייבי' (Lettuce: Salad Mix, crop_id resolved
by name_he) is the species; create a named variety 'חסה בייבי' (baby lettuce) that
the source specifically describes, and project the generally-applicable agronomy
to the whole species.

Reads data/jmf/extracted/jmf_ft_mesclun/Mesclun.json. Produces:
  - load(): one variety-source-value row (cultivar_recommendation) on the NEW
    named variety 'חסה בייבי' (created if missing). Hard-override NI text field —
    not numerically reconciled.
  - load_knowledge_notes(): species-level crop_knowledge_notes for the crop
    (cultivar_recommendation, growing_tip, irrigation, harvest_marker).

LICENSE: L39 is JMF Masterclass content. Knowledge notes are internal-only
(is_internal_farm_use_only forced True by the helper — never published). The
variety row and cultivar names are factual structure (published as a variety).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from organic_market_agent.crop_book.importer.ni_importer import NIImporter

logger = logging.getLogger(__name__)

_DATA_FILE = Path("data/jmf/extracted/jmf_ft_mesclun/Mesclun.json")


class JmfFtMesclunImporter(NIImporter):
    name = "jmf_ft_mesclun_v1"
    canonical_pdf_filename = "L39_mesclun_guide.pdf"

    def _load_data(self) -> dict | None:
        if not _DATA_FILE.exists():
            logger.warning("%s: data file not found: %s", self.name, _DATA_FILE)
            return None
        try:
            return json.loads(_DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("%s: failed to load %s — %s", self.name, _DATA_FILE, exc)
            return None

    def _resolve_crop_id(self, session, name_he: str) -> int | None:
        from organic_market_agent.crop_book.models import Crop

        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("%s: crop name_he=%r not in DB — skipped", self.name, name_he)
            return None
        return crop.id

    def _get_or_create_variety(self, session, crop_id: int, name_he: str, name_en: str) -> int:
        from organic_market_agent.crop_book.models import CropVariety

        v = (
            session.query(CropVariety)
            .filter_by(crop_id=crop_id, name_en=name_en)
            .one_or_none()
        )
        if v is None:
            v = CropVariety(
                crop_id=crop_id,
                name_he=name_he,
                name_en=name_en,
                is_default=False,
            )
            session.add(v)
            session.flush()
        elif v.name_he is None:
            v.name_he = name_he
        return v.id

    def load(self, session) -> list[dict[str, Any]]:
        data = self._load_data()
        if not data:
            return []
        crop_id = self._resolve_crop_id(session, data["crop_name_he"])
        if crop_id is None:
            return []
        var = data.get("variety") or {}
        variety_id = self._get_or_create_variety(
            session, crop_id, var.get("name_he"), var.get("name_en")
        )
        cultivar = (data.get("cultivar_recommendation") or "").strip()
        if not cultivar:
            return []
        provenance = data.get("provenance", {})
        return [
            {
                "variety_id": variety_id,
                "field_name": "cultivar_recommendation",
                "source": self.source_label,
                "value_text": cultivar[:2000],
                "value_numeric": None,
                "unit": None,
                "note": f"From {self.canonical_pdf_filename} pages {provenance.get('pages', 'N/A')}",
                "trust_tier": "NI",
                "confidence_weight": None,
                "is_outlier_rejected": False,
            }
        ]

    def load_knowledge_notes(self, session) -> list[dict[str, Any]]:
        data = self._load_data()
        if not data:
            return []
        crop_id = self._resolve_crop_id(session, data["crop_name_he"])
        if crop_id is None:
            return []
        provenance = data.get("provenance", {})
        rows = []
        for note_type, body in (data.get("species_notes") or {}).items():
            body_text = str(body or "").strip()
            if not body_text:
                continue
            rows.append(
                {
                    "crop_id": crop_id,
                    "source": self.source_label,
                    "trust_tier": "NI",
                    "note_type": note_type,
                    "body_text": body_text[:2000],
                    "provenance_pdf": provenance.get("pdf") or self.canonical_pdf_filename,
                    "provenance_pages": provenance.get("pages"),
                    "is_internal_farm_use_only": True,
                    "extraction_model": provenance.get("extraction_model"),
                    "extracted_at": provenance.get("extracted_at"),
                }
            )
        return rows
