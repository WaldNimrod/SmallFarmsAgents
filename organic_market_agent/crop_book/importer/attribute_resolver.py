"""Attribute resolver — resolves T2/T3 categoricals → crop_attribute.

Mirrors enrichment_runner structure (do NOT modify enrichment_runner).
Public entry point:
    run_attribute_resolver(session, variety_ids=None, dry_run=False) -> AttributeSummary

For each variety and each §7.2 attribute:
  - source_values-origin: gather candidates from crop_variety_source_values
  - column-origin: read column from crop_varieties, wrap as single provenance-tagged candidate
  - enum-canonicalize (closed-enum) or normalize (open-vocab)
  - hard_winner by trust order (reuse source_registry CLASS_RANK)
  - upsert into crop_attribute with provenance (candidates jsonb)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.attribute_models import CropAttribute
from organic_market_agent.crop_book.canon.enums import (
    canonicalize_enum,
    parse_month_list,
    parse_list_attr,
    OPEN_VOCAB_ATTRS,
    ENUM_TOKENS,
)
from organic_market_agent.crop_book.models import CropVariety, CropVarietySourceValue
from organic_market_agent.crop_book.source_registry import CLASS_RANK, get_source_spec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Attribute definitions — Canon §7.2 (all 11 attributes)
# ---------------------------------------------------------------------------

# Attributes sourced from crop_variety_source_values rows (multi-source)
_SOURCE_VALUES_ATTRS: dict[str, str] = {
    # canonical_attr_name: source_field_name (the field_name in source_values)
    "planting_method":               "planting_method",
    "frost_tolerance_class":         "frost_tolerance_class",
    "sowing_months":                 "seed_months_list",
    "transplant_months":             "transplant_months_list",
    "storage_ethylene_sensitivity":  "storage_ethylene_sensitivity",
    "variety_provider":              "variety_provider",
    "rootstock_variety":             "rootstock_variety",
    # Canon §16 — MIG2 additions (Amendment v1.3.0)
    "irrigation_type":               "irrigation_type",       # T2 CLOSED-ENUM
    "root_depth_class":              "root_depth_class",      # T2 CLOSED-ENUM
    "needs_summer_shade":            "needs_summer_shade",    # T2 CLOSED-ENUM
    "common_pests":                  "common_pests",          # T3 OPEN-VOCAB list
    "foliar_feeding_program":        "foliar_feeding_program",# T2 OPEN-VOCAB
    "unit_size":                     "unit_size",             # T2 OPEN-VOCAB
    # NOTE: sale_unit → alias to harvest_unit (D-MIG2-1); NO resolver entry here.
    # NOTE: seeder_model → alias to seeder column (D-MIG2-2); NO resolver entry here.
}

# Attributes sourced from crop_varieties columns (single value, column-origin)
# Maps canonical_attr_name → column_name on crop_varieties
_COLUMN_ORIGIN_ATTRS: dict[str, str] = {
    "season_window": "planting_season",
    "harvest_unit":  "harvest_unit",
    "harvest_stage": "harvest_stage",
}

# All 11 §7.2 attributes (union of above)
ALL_ATTRIBUTES: list[str] = (
    list(_SOURCE_VALUES_ATTRS.keys()) + list(_COLUMN_ORIGIN_ATTRS.keys())
)


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

@dataclass
class AttributeSummary:
    """Aggregated stats from a run_attribute_resolver() call."""

    variety_count: int
    attribute_rows_written: int
    attributes_missing: int
    """Count of (variety, attribute) pairs with no candidates."""

    def __str__(self) -> str:
        return (
            f"AttributeSummary(varieties={self.variety_count}, "
            f"rows_written={self.attribute_rows_written}, "
            f"missing={self.attributes_missing})"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _class_rank(source_label: str) -> int:
    """Return CLASS_RANK for source_label (lower = higher trust)."""
    spec = get_source_spec(source_label)
    return CLASS_RANK.get(spec.cls, 99)


def _hard_winner(
    candidates: dict[str, Any],
) -> tuple[str, str, float]:
    """Select winning source by class rank.

    Args:
        candidates: {source_label: raw_value (str or list)}

    Returns:
        (winning_source_label, winning_value_raw, confidence_score)
        confidence_score = 1.0 if single source or unanimous; lower if contested.
    """
    if not candidates:
        raise ValueError("No candidates")

    sorted_sources = sorted(candidates.keys(), key=_class_rank)
    winner_label = sorted_sources[0]
    winner_value = candidates[winner_label]

    # Confidence: 1.0 for single source; otherwise check agreement
    n = len(candidates)
    if n == 1:
        confidence = 1.0
    else:
        # Count sources that agree with winner (for list: exact match; for str: exact)
        agree = sum(1 for v in candidates.values() if v == winner_value)
        confidence = agree / n

    winning_class = get_source_spec(winner_label).cls
    return winner_label, winner_value, confidence


def _canonicalize_value(
    attr_name: str,
    raw_value: str | None,
) -> Any:
    """Apply enum-canonicalization or open-vocab normalization."""
    if raw_value is None:
        return None

    # Month lists (T3 int-list)
    if attr_name in ("sowing_months", "transplant_months"):
        return parse_month_list(raw_value)

    # T3 open-vocab list (common_pests) — comma-delimited
    if attr_name == "common_pests":
        return parse_list_attr(raw_value, attr_name)

    # Open-vocab (single-value)
    if attr_name in OPEN_VOCAB_ATTRS:
        from organic_market_agent.crop_book.canon.enums import _normalize_open_vocab
        return _normalize_open_vocab(raw_value)

    # Closed-enum
    return canonicalize_enum(attr_name, raw_value)


def _upsert_attribute(
    session: Session,
    variety_id: int,
    attr_name: str,
    value_canonical: str | None,
    value_list: list | None,
    winning_source_class: str,
    confidence_score: float,
    source_count: int,
    candidates: dict[str, Any],
) -> None:
    """INSERT or UPDATE one crop_attribute row."""
    now = datetime.now(timezone.utc)
    obj = (
        session.query(CropAttribute)
        .filter_by(variety_id=variety_id, attribute_name=attr_name)
        .first()
    )
    data = dict(
        value_canonical=value_canonical,
        value_list=value_list,
        winning_source_class=winning_source_class,
        confidence_score=confidence_score,
        source_count=source_count,
        candidates=candidates,
        computed_at=now,
    )
    if obj is None:
        obj = CropAttribute(
            variety_id=variety_id,
            attribute_name=attr_name,
            **data,
        )
        session.add(obj)
    else:
        for k, v in data.items():
            setattr(obj, k, v)


def _resolve_source_values_attr(
    sv_rows: list[CropVarietySourceValue],
    attr_name: str,
    source_field_name: str,
) -> dict[str, Any]:
    """Gather candidates for a source_values-origin attribute.

    Returns {source_label: canonicalized_value}.
    """
    candidates: dict[str, Any] = {}
    for sv in sv_rows:
        if sv.field_name != source_field_name:
            continue
        raw = sv.value_text
        if raw is None and sv.value_numeric is not None:
            raw = str(sv.value_numeric)
        if raw is None:
            continue
        canonical_val = _canonicalize_value(attr_name, raw)
        if canonical_val is None:
            continue
        # Last source with same label wins (de-dup by label)
        candidates[sv.source] = canonical_val
    return candidates


def _resolve_column_origin_attr(
    variety: CropVariety,
    attr_name: str,
    column_name: str,
) -> dict[str, Any]:
    """Gather candidate for a column-origin attribute.

    The column is read as a single provenance-tagged candidate.
    Source class is 'OP' for operational columns; 'EX' if we later have overrides.
    For now all column-origin attrs use 'OP' class as source label 'column_origin'.
    """
    raw_val = getattr(variety, column_name, None)
    if raw_val is None:
        return {}
    canonical_val = _canonicalize_value(attr_name, str(raw_val))
    if canonical_val is None:
        return {}
    # Tag with 'column_origin' as the source label (class OP)
    return {"column_origin": canonical_val}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_attribute_resolver(
    session: Session,
    variety_ids: Optional[list[int]] = None,
    dry_run: bool = False,
) -> AttributeSummary:
    """Resolve all §7.2 T2/T3 attributes for all (or selected) varieties.

    For each variety:
    1. Loads CropVarietySourceValue rows.
    2. For source_values-origin attributes: gathers candidates by field_name.
    3. For column-origin attributes: reads column value directly.
    4. Applies hard_winner by trust order.
    5. Upserts crop_attribute with full provenance (unless dry_run).

    Args:
        session:      Active SQLAlchemy session.
        variety_ids:  If given, restrict to these variety IDs only.
        dry_run:      If True, compute but do not write to DB.

    Returns:
        AttributeSummary.
    """
    q = session.query(CropVariety)
    if variety_ids:
        q = q.filter(CropVariety.id.in_(variety_ids))
    varieties = q.all()

    variety_count = 0
    rows_written = 0
    missing = 0

    for variety in varieties:
        sv_rows = (
            session.query(CropVarietySourceValue)
            .filter_by(variety_id=variety.id)
            .all()
        )

        # --- source_values-origin attributes ---
        for attr_name, source_field in _SOURCE_VALUES_ATTRS.items():
            candidates = _resolve_source_values_attr(sv_rows, attr_name, source_field)

            if not candidates:
                logger.debug(
                    "No candidates: variety_id=%s attr=%r (source field=%r)",
                    variety.id, attr_name, source_field,
                )
                missing += 1
                continue

            winner_label, winner_value, confidence = _hard_winner(candidates)
            winning_class = get_source_spec(winner_label).cls

            # Split T2 vs T3
            is_list = isinstance(winner_value, list)
            value_canonical = None if is_list else str(winner_value)
            value_list = winner_value if is_list else None

            if not dry_run:
                _upsert_attribute(
                    session=session,
                    variety_id=variety.id,
                    attr_name=attr_name,
                    value_canonical=value_canonical,
                    value_list=value_list,
                    winning_source_class=winning_class,
                    confidence_score=confidence,
                    source_count=len(candidates),
                    candidates={src: (v if isinstance(v, (str, int)) else str(v))
                                 for src, v in candidates.items()},
                )
                rows_written += 1

            logger.debug(
                "Attr: variety_id=%s attr=%r winner=%r conf=%.2f sources=%d",
                variety.id, attr_name, winner_label, confidence, len(candidates),
            )

        # --- column-origin attributes ---
        for attr_name, col_name in _COLUMN_ORIGIN_ATTRS.items():
            candidates = _resolve_column_origin_attr(variety, attr_name, col_name)

            if not candidates:
                logger.debug(
                    "No column value: variety_id=%s attr=%r col=%r",
                    variety.id, attr_name, col_name,
                )
                missing += 1
                continue

            winner_label, winner_value, confidence = _hard_winner(candidates)
            winning_class = get_source_spec(winner_label).cls

            is_list = isinstance(winner_value, list)
            value_canonical = None if is_list else str(winner_value)
            value_list = winner_value if is_list else None

            if not dry_run:
                _upsert_attribute(
                    session=session,
                    variety_id=variety.id,
                    attr_name=attr_name,
                    value_canonical=value_canonical,
                    value_list=value_list,
                    winning_source_class=winning_class,
                    confidence_score=confidence,
                    source_count=len(candidates),
                    candidates={src: (v if isinstance(v, (str, int)) else str(v))
                                 for src, v in candidates.items()},
                )
                rows_written += 1

            logger.debug(
                "ColAttr: variety_id=%s attr=%r col=%r value=%r",
                variety.id, attr_name, col_name, winner_value,
            )

        variety_count += 1

        if not dry_run:
            session.flush()

    summary = AttributeSummary(
        variety_count=variety_count,
        attribute_rows_written=rows_written,
        attributes_missing=missing,
    )
    logger.info("Attribute resolution complete: %s", summary)
    return summary
