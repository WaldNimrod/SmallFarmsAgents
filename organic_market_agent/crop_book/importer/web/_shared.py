"""Shared helpers for WP-C4 web-source importers."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.constants import resolve_en_crop
from organic_market_agent.crop_book.companion_matrix import CropCompanionMatrix
from organic_market_agent.crop_book.models import Crop, CropVariety, CropVarietySourceValue
from organic_market_agent.crop_book.source_registry import get_source_spec

logger = logging.getLogger(__name__)

WEB_SOURCES_ROOT = (
    Path(__file__).resolve().parents[4] / "data" / "external_sources" / "web"
)

LBS_PER_ACRE_TO_KG_HA = Decimal("1.12085")
P2O5_TO_P = Decimal("0.4364")
K2O_TO_K = Decimal("0.8301")

FROST_CLASS_ORDER = ("very_tender", "tender", "semi_hardy", "hardy")


@dataclass
class WebImportSummary:
    rows_parsed: int = 0
    rows_upserted: int = 0
    map_misses: list[str] = field(default_factory=list)
    db_misses: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def source_dir(source_key: str) -> Path:
    return WEB_SOURCES_ROOT / source_key


def require_cache(source_key: str, *filenames: str) -> Path:
    """Return first existing cached file or raise with download hint."""
    base = source_dir(source_key)
    for name in filenames:
        p = base / name
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Missing cache for {source_key}. Run: "
        f"python3 scripts/download_web_sources.py --source {source_key}"
    )


def load_extract(source_key: str) -> list[dict[str, Any]]:
    """Load committed JSON extract if present."""
    path = source_dir(source_key) / "extract.json"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "rows" in data:
        return data["rows"]
    return []


def save_extract(source_key: str, rows: list[dict[str, Any]]) -> None:
    base = source_dir(source_key)
    base.mkdir(parents=True, exist_ok=True)
    path = base / "extract.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump({"rows": rows}, fh, ensure_ascii=False, indent=2)


def fahrenheit_to_celsius(f: float) -> Decimal:
    return Decimal(str(round((f - 32) * 5 / 9, 1)))


def lbs_acre_to_kg_ha(lbs: float) -> Decimal:
    return (Decimal(str(lbs)) * LBS_PER_ACRE_TO_KG_HA).quantize(Decimal("0.01"))


def resolve_crop_id_en(session: Session, name_en: str) -> tuple[int | None, str | None]:
    canonical = resolve_en_crop(name_en)
    if canonical is None:
        logger.warning("EN crop unmapped: %r — skipping", name_en)
        return None, None
    crop = session.query(Crop).filter_by(name_he=canonical).one_or_none()
    if crop is None:
        logger.warning("EN crop %r → %r not in DB — skipping", name_en, canonical)
        return None, canonical
    return crop.id, canonical


def default_variety_id(session: Session, crop_id: int) -> int:
    v = (
        session.query(CropVariety)
        .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
        .first()
    )
    if v is None:
        v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
        session.add(v)
        session.flush()
    return v.id


def lookup_crop_by_scientific_name(session: Session, scientific: str) -> int | None:
    sci = (scientific or "").strip()
    if not sci:
        return None
    crop = session.query(Crop).filter(Crop.scientific_name.ilike(sci)).first()
    if crop:
        return crop.id
    crop = session.query(Crop).filter(Crop.scientific_name.ilike(f"%{sci}%")).first()
    return crop.id if crop else None


def upsert_variety_sv(
    session: Session,
    variety_id: int,
    field_name: str,
    source: str,
    *,
    value_numeric: Optional[Decimal] = None,
    value_text: Optional[str] = None,
    unit: Optional[str] = None,
    note: Optional[str] = None,
) -> bool:
    spec = get_source_spec(source)
    weight = spec.weight
    row = (
        session.query(CropVarietySourceValue)
        .filter_by(variety_id=variety_id, field_name=field_name, source=source)
        .one_or_none()
    )
    if row is None:
        row = CropVarietySourceValue(
            variety_id=variety_id,
            field_name=field_name,
            source=source,
        )
        session.add(row)
        inserted = True
    else:
        inserted = False
    row.value_numeric = value_numeric
    row.value_text = value_text
    row.unit = unit
    row.note = note
    row.trust_tier = spec.cls
    row.confidence_weight = Decimal(str(weight)) if weight is not None else None
    row.is_outlier_rejected = False
    session.flush()
    return inserted


def canonical_pair_ids(crop_a_id: int, crop_b_id: int) -> tuple[int, int]:
    if crop_a_id <= crop_b_id:
        return crop_a_id, crop_b_id
    return crop_b_id, crop_a_id


def upsert_companion_pair(
    session: Session,
    crop_a_id: int,
    crop_b_id: int,
    compatibility: str,
    source: str,
    *,
    evidence_strength: str = "weak",
    notes: str | None = None,
) -> bool:
    a_id, b_id = canonical_pair_ids(crop_a_id, crop_b_id)
    if a_id == b_id:
        return False
    spec = get_source_spec(source)
    existing = (
        session.query(CropCompanionMatrix)
        .filter_by(crop_a_id=a_id, crop_b_id=b_id, source=source)
        .one_or_none()
    )
    if existing is None:
        session.add(
            CropCompanionMatrix(
                crop_a_id=a_id,
                crop_b_id=b_id,
                compatibility=compatibility,
                source=source,
                trust_tier=spec.cls,
                evidence_strength=evidence_strength,
                notes=notes,
            )
        )
        session.flush()
        return True
    existing.compatibility = compatibility
    existing.evidence_strength = evidence_strength
    existing.notes = notes
    session.flush()
    return False


def normalize_frost_label(raw: str) -> str | None:
    text = (raw or "").strip().lower()
    if not text:
        return None
    if "very tender" in text or "cold-sensitive" in text or "cold sensitive" in text:
        return "very_tender"
    if "semi-hardy" in text or "semi hardy" in text or "half-hardy" in text or "half hardy" in text:
        return "semi_hardy"
    if re.search(r"\bhardy\b", text) and "semi" not in text and "half" not in text:
        return "hardy"
    if "tender" in text:
        return "tender"
    return None


def reconcile_frost_classes(classes: list[str]) -> tuple[str, str]:
    """Return (chosen_class, log_note). Most-tender on disagreement."""
    valid = [c for c in classes if c]
    if not valid:
        return "tender", "no_valid_classes"
    counts: dict[str, int] = {}
    for c in valid:
        counts[c] = counts.get(c, 0) + 1
    best = max(counts.items(), key=lambda x: x[1])
    if best[1] >= 2:
        return best[0], f"consensus_{best[0]}_{best[1]}_of_{len(valid)}"
    # disagree — most conservative (most tender = lowest index in FROST_CLASS_ORDER)
    chosen = min(valid, key=lambda c: FROST_CLASS_ORDER.index(c))
    return chosen, f"disagree_default_{chosen}_from_{valid}"


def parse_float_cell(cell: str | None) -> float | None:
    if cell is None:
        return None
    m = re.search(r"[\d.]+", str(cell).replace(",", ""))
    return float(m.group()) if m else None
