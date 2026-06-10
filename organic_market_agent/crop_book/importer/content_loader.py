"""CropContentLoader — load curated narrative prose into crop_content[+_source].

SFA-S003-P004-WP-CB-CONTENT.

Reads a curated authoring file (``data/crop_content/authoring.json``), resolves each crop
via ``JMF_CROP_MAP → name_he → crops.id`` (same idiom as the NI importers), and upserts:

    * one ``crop_content`` row per (crop, content_type)   — the consolidated canonical body
    * N ``crop_content_source`` rows per unit             — the per-source variants (Deep mode)

``source_class`` / ``display_order`` / ``winning_source_class`` are DERIVED from
``source_registry`` (CLASS_RANK) — never hand-authored. Idempotent: re-running upserts on
the two UNIQUE constraints and prunes variants for sources removed from the authoring file.

⚠ LICENSING FIREWALL: this module MUST NOT import or read ``crop_knowledge_notes`` (internal-
only / copyrighted). Every body it writes is OUR own authored Hebrew text, sourced solely from
the human-curated authoring file. Enforced by tests/crop_book/test_ni_publisher_isolation.py.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.content_models import (
    CONTENT_TYPE_VALUES,
    CropContent,
    CropContentSource,
)
from organic_market_agent.crop_book.source_registry import CLASS_RANK, get_source_spec

logger = logging.getLogger(__name__)

_AUTHORING_FILE = Path(__file__).resolve().parents[3] / "data" / "crop_content" / "authoring.json"
_SCHEMA_VERSION = "1.0"


@dataclass
class ContentLoadSummary:
    crops_seen: int = 0
    crops_resolved: int = 0
    units_upserted: int = 0
    sources_upserted: int = 0
    sources_pruned: int = 0
    skipped: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (
            f"crops_seen={self.crops_seen} resolved={self.crops_resolved} "
            f"units={self.units_upserted} sources={self.sources_upserted} "
            f"pruned={self.sources_pruned} skipped={len(self.skipped)}"
        )


def _compute_confidence(source_classes: list[str]) -> Decimal:
    """Confidence for the consolidated canonical.

    1.0 when a hard-override source (EX/NI) is present; otherwise a corroboration heuristic
    that grows with the number of sources. All authored units clear the field_state τ (0.40):
    the content is curated + adversarially verified, so it publishes as VALIDATED while the
    per-source pills still honestly show the originating class (EX/PR/WR/…).
    """
    if any(c in ("EX", "NI") for c in source_classes):
        return Decimal("1.0")
    n = len(source_classes)
    return Decimal(str(min(0.95, round(0.40 + 0.15 * n, 4))))


def _winning_class(source_classes: list[str]) -> str | None:
    """Class with the best (lowest) CLASS_RANK among this unit's sources."""
    if not source_classes:
        return None
    return min(source_classes, key=lambda c: CLASS_RANK.get(c, 99))


class CropContentLoader:
    name = "crop_content_v1"

    def __init__(self, authoring_file: Path | None = None) -> None:
        self.authoring_file = authoring_file or _AUTHORING_FILE

    def _iter_units(self) -> Iterator[tuple[str, str | None, str, str, list[dict[str, Any]]]]:
        """Yield (crop_jmf_en, name_he_override, content_type, canonical_md, sources_list).

        A crop entry may carry meta keys prefixed with ``_`` (e.g. ``"_name_he"``) that are NOT
        content types. ``_name_he`` lets the authoring file target a DB crop directly by its Hebrew
        name when JMF_CROP_MAP doesn't map to the right one (e.g. JMF "Beans (Bush)" → "שעועית שיחית"
        but the DB models beans as the single generic crop "שעועית").
        """
        if not self.authoring_file.exists():
            logger.warning("%s: authoring file missing — %s", self.name, self.authoring_file)
            return
        data = json.loads(self.authoring_file.read_text(encoding="utf-8"))
        if data.get("schema_version") != _SCHEMA_VERSION:
            raise ValueError(
                f"{self.authoring_file}: schema_version != {_SCHEMA_VERSION!r}"
            )
        for crop_jmf_en, units in data.get("crops", {}).items():
            name_he_override = (units or {}).get("_name_he")
            for content_type, unit in units.items():
                if content_type.startswith("_"):
                    continue  # meta key (e.g. _name_he) — not a content type
                if content_type not in CONTENT_TYPE_VALUES:
                    logger.warning(
                        "%s: %r/%r unknown content_type — skipped",
                        self.name, crop_jmf_en, content_type,
                    )
                    continue
                canonical_md = (unit or {}).get("canonical_md")
                if not canonical_md:
                    logger.warning(
                        "%s: %r/%r missing canonical_md — skipped",
                        self.name, crop_jmf_en, content_type,
                    )
                    continue
                sources = (unit or {}).get("sources", []) or []
                yield crop_jmf_en, name_he_override, content_type, canonical_md, sources

    def _resolve_crop_id(
        self, session: Session, crop_jmf_en: str, name_he_override: str | None = None
    ) -> int | None:
        from organic_market_agent.crop_book.constants import JMF_CROP_MAP
        from organic_market_agent.crop_book.models import Crop

        name_he = name_he_override or JMF_CROP_MAP.get(crop_jmf_en)
        if name_he is None:
            logger.warning(
                "%s: crop_jmf_en=%r not in JMF_CROP_MAP and no _name_he override — skipped",
                self.name, crop_jmf_en,
            )
            return None
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("%s: name_he=%r not in DB — skipped", self.name, name_he)
            return None
        return crop.id

    def load(self, session: Session) -> ContentLoadSummary:
        summary = ContentLoadSummary()
        resolved_crops: set[str] = set()
        now = datetime.now(timezone.utc)

        for crop_jmf_en, name_he_override, content_type, canonical_md, sources in self._iter_units():
            crop_id = self._resolve_crop_id(session, crop_jmf_en, name_he_override)
            if crop_id is None:
                summary.skipped.append(f"{crop_jmf_en}/{content_type}")
                continue
            if crop_jmf_en not in resolved_crops:
                resolved_crops.add(crop_jmf_en)
                summary.crops_resolved += 1

            # Resolve each source's class from the registry (never hand-authored).
            resolved_sources: list[dict[str, Any]] = []
            for s in sources:
                label = s.get("source_label")
                raw = s.get("raw_text_md")
                if not label or not raw:
                    logger.warning(
                        "%s: %r/%r source missing label/raw_text_md — skipped variant",
                        self.name, crop_jmf_en, content_type,
                    )
                    continue
                cls = get_source_spec(label).cls
                resolved_sources.append(
                    {
                        "source_label": label,
                        "source_class": cls,
                        "raw_text_md": raw,
                        "source_url": s.get("source_url"),
                        "display_order": CLASS_RANK.get(cls, 99),
                    }
                )

            classes = [s["source_class"] for s in resolved_sources]

            # ── Upsert the canonical parent on (crop_id, content_type) ──
            content = (
                session.query(CropContent)
                .filter_by(crop_id=crop_id, content_type=content_type)
                .one_or_none()
            )
            if content is None:
                content = CropContent(crop_id=crop_id, content_type=content_type)
                session.add(content)
            content.text_md = canonical_md
            content.winning_source_class = _winning_class(classes)
            content.confidence_score = _compute_confidence(classes)
            content.source_count = len(resolved_sources)
            content.computed_at = now
            session.flush()  # assign content.id
            summary.units_upserted += 1

            # ── Upsert per-source variants on (content_id, source_label) ──
            kept_labels: set[str] = set()
            for rs in resolved_sources:
                kept_labels.add(rs["source_label"])
                variant = (
                    session.query(CropContentSource)
                    .filter_by(content_id=content.id, source_label=rs["source_label"])
                    .one_or_none()
                )
                if variant is None:
                    variant = CropContentSource(
                        content_id=content.id, source_label=rs["source_label"]
                    )
                    session.add(variant)
                variant.source_class = rs["source_class"]
                variant.raw_text_md = rs["raw_text_md"]
                variant.source_url = rs["source_url"]
                variant.display_order = rs["display_order"]
                summary.sources_upserted += 1

            # ── Prune variants for sources removed from the authoring file ──
            existing = (
                session.query(CropContentSource).filter_by(content_id=content.id).all()
            )
            for v in existing:
                if v.source_label not in kept_labels:
                    session.delete(v)
                    summary.sources_pruned += 1

        # crops_seen = distinct crop keys present in the authoring file
        try:
            data = json.loads(self.authoring_file.read_text(encoding="utf-8"))
            summary.crops_seen = len(data.get("crops", {}))
        except Exception:
            pass

        session.flush()
        logger.info("%s: %s", self.name, summary)
        return summary


def load_content(session: Session, authoring_file: Path | None = None) -> ContentLoadSummary:
    """Convenience entry point used by seed.py's --content-only path."""
    return CropContentLoader(authoring_file).load(session)
