"""NI (Nimrod-Input) importer skeleton — SFA-S003-P002-WP-A LOD400 §17 Step 7.

NI sources are files or links supplied directly by team_00 (Nimrod).
They carry hard-override trust (class NI, weight=None, is_hard_override=True) —
higher than JMF/Tend, lower only than EX (team_00 explicit overrides).

Source label convention: "NI:<name>"  (e.g. "NI:rehovot_trials_2024")
Registered on-load via get_source_spec("NI:<name>") prefix detection in source_registry.

Design notes (WP-B will flesh this out):
  - Concrete subclasses register themselves by calling ni_registry.register().
  - The enrichment_runner calls ni_registry.load_all() to obtain source value rows
    before building Candidate lists.
  - Each row must include: variety_id, field_name, source="NI:<name>",
    value_numeric (if applicable), value_text, unit, note,
    trust_tier="NI", confidence_weight=None, is_outlier_rejected=False.
"""

from __future__ import annotations

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


def ni_source_label(name: str) -> str:
    """Return the canonical NI source label for a given importer name."""
    if name.startswith("NI:"):
        return name
    return f"NI:{name}"


class NIImporter(abc.ABC):
    """Abstract base class for all NI (Nimrod-Input) importers.

    Subclasses must implement :meth:`load` and provide a ``name`` attribute.
    """

    name: str  # used as the NI:<name> suffix in source labels

    @property
    def source_label(self) -> str:
        """Canonical source label for this importer, e.g. 'NI:rehovot_trials_2024'."""
        return ni_source_label(self.name)

    @abc.abstractmethod
    def load(self) -> list[dict[str, Any]]:
        """Load and return source value row dicts ready for DB insertion.

        Each dict must include at minimum:
            variety_id:         int
            field_name:         str
            source:             str  (== self.source_label)
            value_text:         str | None
            value_numeric:      Decimal | None
            unit:               str | None
            note:               str | None
            trust_tier:         "NI"
            confidence_weight:  None  (hard override — not blended)
            is_outlier_rejected: False

        Returns:
            List of source value row dicts. May be empty if no data available.
        """

    def validate(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Optional post-load validation hook. Override to add checks.

        Default implementation back-fills mandatory fields and logs warnings.
        """
        validated: list[dict[str, Any]] = []
        for row in rows:
            # Ensure source label is correct
            row["source"] = self.source_label
            row.setdefault("trust_tier", "NI")
            row.setdefault("confidence_weight", None)
            row.setdefault("is_outlier_rejected", False)
            if row.get("variety_id") is None:
                logger.warning("%s: row missing variety_id — skipped: %r", self.name, row)
                continue
            if row.get("field_name") is None:
                logger.warning("%s: row missing field_name — skipped: %r", self.name, row)
                continue
            if row.get("value_numeric") is None and row.get("value_text") is None:
                logger.warning("%s: row has no value — skipped: %r", self.name, row)
                continue
            validated.append(row)
        return validated


# ---------------------------------------------------------------------------
# Global NI importer registry
# ---------------------------------------------------------------------------

class _NIRegistry:
    """Singleton registry for all registered NIImporter instances."""

    def __init__(self) -> None:
        self._importers: dict[str, NIImporter] = {}

    def register(self, importer: NIImporter) -> None:
        """Register an NIImporter. Call at module load time."""
        label = importer.source_label
        if label in self._importers:
            logger.warning("NI importer already registered: %r — replacing", label)
        self._importers[label] = importer
        logger.debug("NI importer registered: %r", label)

    def load_all(self) -> list[dict[str, Any]]:
        """Call load() + validate() on all registered importers, return combined rows."""
        all_rows: list[dict[str, Any]] = []
        for label, imp in self._importers.items():
            try:
                rows = imp.load()
                rows = imp.validate(rows)
                logger.info("NI importer %r loaded %d rows", label, len(rows))
                all_rows.extend(rows)
            except Exception:  # noqa: BLE001
                logger.exception("NI importer %r failed", label)
        return all_rows

    @property
    def registered_labels(self) -> list[str]:
        return list(self._importers.keys())


ni_registry = _NIRegistry()


# ---------------------------------------------------------------------------
# Knowledge-note upsert helper (added by WP-B2)
# ---------------------------------------------------------------------------


def _upsert_knowledge_note(
    session,
    crop_id: int,
    source: str,
    note_type: str,
    body_text: str,
    *,
    trust_tier: str = "NI",
    provenance_pdf: "str | None" = None,
    provenance_pages: "str | None" = None,
    is_internal_farm_use_only: bool = True,
    extraction_model: "str | None" = None,
    extracted_at=None,
) -> "CropKnowledgeNote":
    """Upsert one crop_knowledge_notes row on (crop_id, source, note_type).

    Always sets trust_tier='NI' and is_internal_farm_use_only=True (enforced
    by this helper regardless of the is_internal_farm_use_only argument, which
    is accepted only to allow **row unpacking from load_knowledge_notes()).
    Body text bounded <= 2000 chars (DB CHECK + ORM constraint also enforce).

    Added by SFA-S003-P002-WP-B2 LOD400 v1.1.3 §7.3.
    """
    # Lazy import to avoid circular dependency at module load
    from organic_market_agent.crop_book.crop_knowledge_notes import (
        CropKnowledgeNote,
        BODY_TEXT_MAX_LENGTH,
    )

    if len(body_text) > BODY_TEXT_MAX_LENGTH:
        raise ValueError(f"body_text exceeds {BODY_TEXT_MAX_LENGTH} chars")

    row = (
        session.query(CropKnowledgeNote)
        .filter_by(crop_id=crop_id, source=source, note_type=note_type)
        .one_or_none()
    )
    if row is None:
        row = CropKnowledgeNote(
            crop_id=crop_id,
            source=source,
            note_type=note_type,
        )
        session.add(row)

    # Hardcoded trust and licensing — cannot be overridden by importer code
    row.trust_tier = "NI"
    row.body_text = body_text
    row.provenance_pdf = provenance_pdf
    row.provenance_pages = provenance_pages
    row.is_internal_farm_use_only = True
    row.extraction_model = extraction_model
    row.extracted_at = extracted_at
    if row.created_at is None:
        from datetime import datetime, timezone
        row.created_at = datetime.now(timezone.utc)
    session.flush()
    return row
