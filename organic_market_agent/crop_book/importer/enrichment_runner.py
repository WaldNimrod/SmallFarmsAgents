"""Enrichment runner — SFA-S003-P002-WP-A LOD400 §17 Step 6.

Loads CropVarietySourceValue rows from the DB, builds Candidate lists,
calls reconcile_field() for every (variety, field) pair, and upserts
consensus rows into crop_field_enrichment.

Public entry point:
    run_enrichment(session, variety_ids=None, dry_run=False) -> EnrichmentSummary
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
from organic_market_agent.crop_book.importer.reconciler import Candidate, FieldConsensus, reconcile_field
from organic_market_agent.crop_book.models import CropVariety, CropVarietySourceValue
from organic_market_agent.crop_book.source_registry import get_source_spec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Summary dataclass
# ---------------------------------------------------------------------------

@dataclass
class EnrichmentSummary:
    """Aggregated stats from a run_enrichment() call."""

    variety_count: int
    field_count: int
    outlier_count: int
    high_confidence_count: int
    """Number of (variety, field) rows with confidence_score >= 0.70."""

    def __str__(self) -> str:
        return (
            f"EnrichmentSummary(varieties={self.variety_count}, "
            f"fields={self.field_count}, outliers={self.outlier_count}, "
            f"high_conf={self.high_confidence_count})"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _upsert_enrichment(
    session: Session,
    variety_id: int,
    consensus: FieldConsensus,
) -> None:
    """INSERT or UPDATE one crop_field_enrichment row."""
    now = datetime.now(timezone.utc)
    obj = (
        session.query(CropFieldEnrichment)
        .filter_by(variety_id=variety_id, field_name=consensus.field_name)
        .first()
    )
    if obj is None:
        obj = CropFieldEnrichment(
            variety_id=variety_id,
            field_name=consensus.field_name,
            value_min=consensus.value_min,
            value_max=consensus.value_max,
            value_best=consensus.value_best,
            confidence_score=consensus.confidence_score,
            source_count=consensus.source_count,
            winning_source_class=consensus.winning_source_class,
            computed_at=now,
        )
        session.add(obj)
    else:
        obj.value_min = consensus.value_min
        obj.value_max = consensus.value_max
        obj.value_best = consensus.value_best
        obj.confidence_score = consensus.confidence_score
        obj.source_count = consensus.source_count
        obj.winning_source_class = consensus.winning_source_class
        obj.computed_at = now


def _build_candidates(
    sv_rows: list[CropVarietySourceValue],
    name_he: str,
    session: Session,
    dry_run: bool,
) -> dict[str, list[Candidate]]:
    """Group source value rows by field_name into Candidate lists.

    - Skips non-numeric rows (value_numeric IS NULL).
    - Skips is_outlier_rejected=True rows already flagged at seed time.
      (enrichment_runner re-evaluates outliers independently; seed-time flags
      are informational on the source row, not binding here.)
    - Back-populates trust_tier on the source row if missing.
    - Applies UC moderation gate: requires confidence_weight IS NOT NULL AND > 0.
    """
    by_field: dict[str, list[Candidate]] = {}

    for sv in sv_rows:
        if sv.value_numeric is None:
            continue  # text-only source rows are not numerically reconciled

        spec = get_source_spec(sv.source)

        # Back-populate trust_tier if missing (idempotent)
        if sv.trust_tier is None and not dry_run:
            sv.trust_tier = spec.cls

        # UC moderation gate
        mod_weight: Optional[float] = None
        if spec.requires_moderation:
            if sv.confidence_weight is not None and float(sv.confidence_weight) > 0:
                mod_weight = float(sv.confidence_weight)
            else:
                logger.debug(
                    "UC row excluded (not moderated): variety_id=%s field=%r source=%r",
                    sv.variety_id, sv.field_name, sv.source,
                )
                continue  # UC row not moderated → exclude from blend

        by_field.setdefault(sv.field_name, []).append(Candidate(
            source_label=sv.source,
            value=Decimal(str(sv.value_numeric)),
            name_he=name_he,
            moderation_weight=mod_weight,
        ))

    return by_field


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_enrichment(
    session: Session,
    variety_ids: Optional[list[int]] = None,
    dry_run: bool = False,
) -> EnrichmentSummary:
    """Run enrichment for all (or selected) varieties.

    For each variety:
    1. Loads CropVarietySourceValue rows.
    2. Builds Candidate lists per field (skipping non-numeric + unmoderated UC).
    3. Calls reconcile_field() for each field.
    4. Upserts FieldConsensus into crop_field_enrichment (unless dry_run).

    Back-populates `trust_tier` on source rows where it is NULL.

    Args:
        session:      Active SQLAlchemy session.
        variety_ids:  If given, restrict to these variety IDs only.
        dry_run:      If True, compute consensus but do not write to DB.

    Returns:
        EnrichmentSummary with aggregated statistics.
    """
    q = session.query(CropVariety)
    if variety_ids:
        q = q.filter(CropVariety.id.in_(variety_ids))
    varieties = q.all()

    variety_count = 0
    field_count = 0
    outlier_count = 0
    high_conf_count = 0

    for variety in varieties:
        sv_rows = (
            session.query(CropVarietySourceValue)
            .filter_by(variety_id=variety.id)
            .all()
        )

        name_he: str = ""
        if variety.crop is not None:
            name_he = variety.crop.name_he or ""

        by_field = _build_candidates(sv_rows, name_he, session, dry_run)

        for field_name, candidates in by_field.items():
            if not candidates:
                continue

            consensus = reconcile_field(field_name, candidates)

            if consensus.value_best is None:
                logger.debug(
                    "No consensus: variety_id=%s field=%r (all candidates outlier-rejected or empty)",
                    variety.id, field_name,
                )
                continue

            if not dry_run:
                _upsert_enrichment(session, variety.id, consensus)

            field_count += 1
            outlier_count += len(consensus.outlier_rejected)
            if (
                consensus.confidence_score is not None
                and float(consensus.confidence_score) >= 0.70
            ):
                high_conf_count += 1

            logger.debug(
                "Enriched: variety_id=%s field=%r best=%s conf=%s sources=%d",
                variety.id, field_name, consensus.value_best,
                consensus.confidence_score, consensus.source_count,
            )

        variety_count += 1

        if not dry_run:
            session.flush()

    summary = EnrichmentSummary(
        variety_count=variety_count,
        field_count=field_count,
        outlier_count=outlier_count,
        high_confidence_count=high_conf_count,
    )
    logger.info("Enrichment complete: %s", summary)
    return summary
