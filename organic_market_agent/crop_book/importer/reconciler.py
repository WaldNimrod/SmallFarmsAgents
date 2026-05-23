"""Pluggable multi-source reconciler — SFA-S003-P002-WP-A LOD400 §9.

Public engine API (used by enrichment_runner):
    reconcile_field(field_name, candidates) -> FieldConsensus

Backward-compat wrappers (unchanged signatures — used by seed.py / tend.py / jmf.py):
    reconcile_dtm(name_he, tend_values, jmf_value) -> (int | None, list[dict])
    reconcile_variety(source_rows) -> dict[str, Any]

Outlier gate implements F-190-WP-A-02 MAD=0 branch (modified Z-score with IQR fallback).
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional

from organic_market_agent.crop_book.constants import OUTLIER_CROPS, TEAM00_DTM_OVERRIDES  # noqa: F401
from organic_market_agent.crop_book.field_policy import get_field_policy
from organic_market_agent.crop_book.source_registry import CLASS_RANK, get_source_spec

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Candidate:
    """A single source observation for one (variety, field) pair."""

    source_label: str
    value: Decimal
    name_he: str = ""
    moderation_weight: Optional[float] = None
    """UC moderation gate: None = not yet moderated (excluded from blend);
    a positive float = approved confidence weight override."""


@dataclass
class FieldConsensus:
    """Output of reconcile_field() — one (variety, field) consensus."""

    field_name: str
    value_best: Optional[Decimal]
    value_min: Optional[Decimal]
    value_max: Optional[Decimal]
    confidence_score: Optional[Decimal]
    source_count: int
    winning_source_class: Optional[str]
    outlier_rejected: list[tuple[str, Decimal]] = field(default_factory=list)
    """(source_label, value) pairs rejected by the statistical outlier gate.
    Storing the value avoids ambiguity when the same source label appears multiple times
    (e.g. 'Tend' called with several years of values in reconcile_dtm)."""


# ---------------------------------------------------------------------------
# Outlier gate helpers
# ---------------------------------------------------------------------------

def _percentile(sorted_vals: list[float], pct: float) -> float:
    """Linear-interpolation percentile on a *sorted* list."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    idx = pct / 100.0 * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (idx - lo) * (sorted_vals[hi] - sorted_vals[lo])


def _outlier_mask(
    values: list[float],
    z_threshold: float,
    domain_fn=None,
    names_he: Optional[list[str]] = None,
) -> list[bool]:
    """Return a boolean mask where True = outlier.

    Algorithm (LOD400 §9.2 step 4 / F-190-WP-A-02):
    1. Domain check via domain_fn(name_he, value) → bool if provided.
    2. Statistical gate on the surviving values:
       a. Compute median and MAD.
       b. MAD == 0 and all identical  → no outliers.
       c. MAD == 0 and not identical  → IQR fallback:
             IQR == 0 → flag every value that differs from median.
             IQR  > 0 → flag |v - median| > 1.5 × IQR.
       d. MAD  > 0 → flag modified Z-score = 0.6745 × |v − median| / MAD > z_threshold.

    Requires ≥ 3 values; returns all-False otherwise.
    """
    n = len(values)
    if n < 3:
        return [False] * n

    if names_he is None:
        names_he = [""] * n

    # Step 1: domain outlier check
    domain_mask: list[bool] = [False] * n
    if domain_fn is not None:
        for i, (v, name) in enumerate(zip(values, names_he)):
            try:
                domain_mask[i] = bool(domain_fn(name, v))
            except Exception:  # noqa: BLE001
                pass

    # Step 2: statistical gate on non-domain-outlier values
    remaining_idx = [i for i in range(n) if not domain_mask[i]]
    remaining = [values[i] for i in remaining_idx]

    stat_mask: list[bool] = [False] * n
    if len(remaining) < 3:
        return [d or s for d, s in zip(domain_mask, stat_mask)]

    med = statistics.median(remaining)
    deviations = [abs(v - med) for v in remaining]
    mad = statistics.median(deviations)

    if mad == 0:
        if len(set(remaining)) == 1:
            # All identical → no statistical outliers
            pass
        else:
            # IQR fallback
            sv = sorted(remaining)
            q1 = _percentile(sv, 25.0)
            q3 = _percentile(sv, 75.0)
            iqr = q3 - q1
            if iqr == 0:
                # Mark every value that differs from the median
                for orig_i, v in zip(remaining_idx, remaining):
                    if v != med:
                        stat_mask[orig_i] = True
            else:
                for orig_i, v in zip(remaining_idx, remaining):
                    if abs(v - med) > 1.5 * iqr:
                        stat_mask[orig_i] = True
    else:
        # Standard modified Z-score (Iglewicz & Hoaglin constant = 0.6745)
        for orig_i, v in zip(remaining_idx, remaining):
            mzs = 0.6745 * abs(v - med) / mad
            if mzs > z_threshold:
                stat_mask[orig_i] = True

    return [d or s for d, s in zip(domain_mask, stat_mask)]


# ---------------------------------------------------------------------------
# Core reconciliation engine
# ---------------------------------------------------------------------------

def reconcile_field(
    field_name: str,
    candidates: list[Candidate],
) -> FieldConsensus:
    """Reconcile a list of Candidates for one field into a FieldConsensus.

    Steps (LOD400 §9):
    1. Classify: hard_override (EX/NI) | blend-eligible | excluded (UC unmoderated).
    2. If any hard override → highest-class wins; confidence = 1.0000, done.
    3. Statistical outlier gate on blend-eligible candidates.
    4. Apply blend strategy (weighted_mean / hard_winner / latest_op).
    5. Compute blended confidence score.
    """
    policy = get_field_policy(field_name)

    _empty = FieldConsensus(
        field_name=field_name,
        value_best=None, value_min=None, value_max=None,
        confidence_score=None, source_count=0, winning_source_class=None,
    )

    if not candidates:
        return _empty

    # --- 1. Classify ---
    hard_overrides: list[Candidate] = []
    blend_eligible: list[Candidate] = []

    for c in candidates:
        spec = get_source_spec(c.source_label)
        if spec.is_hard_override:
            hard_overrides.append(c)
        elif spec.requires_moderation:
            if c.moderation_weight is not None and c.moderation_weight > 0:
                blend_eligible.append(c)
            else:
                logger.debug(
                    "UC candidate excluded (not moderated): field=%r source=%r",
                    field_name, c.source_label,
                )
        else:
            blend_eligible.append(c)

    # --- 2. Hard override wins immediately ---
    if hard_overrides:
        winner = min(
            hard_overrides,
            key=lambda c: (CLASS_RANK.get(get_source_spec(c.source_label).cls, 999), c.source_label),
        )
        w_cls = get_source_spec(winner.source_label).cls
        return FieldConsensus(
            field_name=field_name,
            value_best=winner.value,
            value_min=winner.value,
            value_max=winner.value,
            confidence_score=Decimal("1.0000"),
            source_count=1,
            winning_source_class=w_cls,
        )

    if not blend_eligible:
        return _empty

    # --- 3. Statistical outlier gate ---
    float_vals = [float(c.value) for c in blend_eligible]
    names = [c.name_he for c in blend_eligible]
    outlier_cfg = policy.outlier
    mask = _outlier_mask(
        float_vals,
        z_threshold=outlier_cfg.z_threshold,
        domain_fn=outlier_cfg.domain_fn,
        names_he=names,
    )

    outlier_rejected: list[tuple[str, Decimal]] = []
    valid: list[Candidate] = []
    for c, is_out in zip(blend_eligible, mask):
        if is_out:
            outlier_rejected.append((c.source_label, c.value))
            logger.warning(
                "Outlier rejected: field=%r source=%r value=%s",
                field_name, c.source_label, c.value,
            )
        else:
            valid.append(c)

    if not valid:
        return FieldConsensus(
            field_name=field_name,
            value_best=None, value_min=None, value_max=None,
            confidence_score=None, source_count=0, winning_source_class=None,
            outlier_rejected=outlier_rejected,
        )

    # --- 3b. multi_year_op_mean: collapse OP observations to one mean first ---
    if policy.multi_year_op_mean:
        op = [c for c in valid if get_source_spec(c.source_label).cls == "OP"]
        non_op = [c for c in valid if get_source_spec(c.source_label).cls != "OP"]
        if len(op) > 1:
            op_mean = Decimal(str(sum(float(c.value) for c in op) / len(op)))
            rep_label = max(c.source_label for c in op)  # lexicographically latest
            valid = non_op + [Candidate(
                source_label=rep_label,
                value=op_mean,
                name_he=op[0].name_he,
                moderation_weight=None,
            )]

    # Compute range across valid observations
    valid_floats = [float(c.value) for c in valid]
    value_min = Decimal(str(min(valid_floats)))
    value_max = Decimal(str(max(valid_floats)))

    # --- 4. Apply blend strategy ---
    strategy = policy.blend_strategy
    value_best: Optional[Decimal] = None
    winning_cls: Optional[str] = None

    if strategy == "weighted_mean":
        total_w = 0.0
        weighted_sum = 0.0
        best_rank = 999
        for c in valid:
            spec = get_source_spec(c.source_label)
            w = c.moderation_weight if c.moderation_weight is not None else (spec.weight or 0.0)
            total_w += w
            weighted_sum += float(c.value) * w
            rank = CLASS_RANK.get(spec.cls, 999)
            if rank < best_rank:
                best_rank = rank
                winning_cls = spec.cls
        if total_w > 0:
            value_best = Decimal(str(weighted_sum / total_w))

    elif strategy == "hard_winner":
        winner_c = min(
            valid,
            key=lambda c: (CLASS_RANK.get(get_source_spec(c.source_label).cls, 999), c.source_label),
        )
        value_best = winner_c.value
        winning_cls = get_source_spec(winner_c.source_label).cls

    elif strategy == "latest_op":
        op_valid = [c for c in valid if get_source_spec(c.source_label).cls == "OP"]
        if op_valid:
            winner_c = max(op_valid, key=lambda c: c.source_label)
            value_best = winner_c.value
            winning_cls = "OP"
        else:
            # Fallback: hard_winner among non-OP
            winner_c = min(
                valid,
                key=lambda c: (CLASS_RANK.get(get_source_spec(c.source_label).cls, 999), c.source_label),
            )
            value_best = winner_c.value
            winning_cls = get_source_spec(winner_c.source_label).cls

    else:
        raise ValueError(f"Unknown blend_strategy: {strategy!r}")

    # --- 5. Confidence score: mean weight of contributing sources, capped at 1.0 ---
    weights_list: list[float] = []
    for c in valid:
        spec = get_source_spec(c.source_label)
        if c.moderation_weight is not None:
            weights_list.append(c.moderation_weight)
        elif spec.weight is not None:
            weights_list.append(spec.weight)
        else:
            weights_list.append(1.0)  # hard override (shouldn't reach here but defensive)

    conf = Decimal(str(min(1.0, sum(weights_list) / len(weights_list)))) if weights_list else None

    return FieldConsensus(
        field_name=field_name,
        value_best=value_best,
        value_min=value_min,
        value_max=value_max,
        confidence_score=conf,
        source_count=len(valid),
        winning_source_class=winning_cls,
        outlier_rejected=outlier_rejected,
    )


# ---------------------------------------------------------------------------
# Backward-compat wrapper — reconcile_dtm
# ---------------------------------------------------------------------------

def reconcile_dtm(
    name_he: str,
    tend_values: list[int | None],
    jmf_value: int | None,
) -> tuple[int | None, list[dict[str, Any]]]:
    """Return (unified_dtm, source_value_rows_to_store).

    Source value row dict keys:
        field_name, source, value_text, value_numeric, unit, note,
        trust_tier, confidence_weight, is_outlier_rejected  (GCR_1 additions).

    Delegates outlier detection to reconcile_field("days_to_maturity", ...).
    """
    rows: list[dict[str, Any]] = []
    candidates: list[Candidate] = []

    # team_00 EX override
    team00 = TEAM00_DTM_OVERRIDES.get(name_he)
    if team00 is not None:
        spec = get_source_spec("team_00")
        rows.append({
            "field_name": "days_to_maturity",
            "source": "team_00",
            "value_text": str(team00),
            "value_numeric": Decimal(team00),
            "unit": "days",
            "note": "team_00 Israel-specific override — highest priority",
            "trust_tier": spec.cls,
            "confidence_weight": None,
            "is_outlier_rejected": False,
        })
        candidates.append(Candidate("team_00", Decimal(team00), name_he=name_he))

    # JMF PR source
    if jmf_value is not None:
        spec = get_source_spec("JMF")
        rows.append({
            "field_name": "days_to_maturity",
            "source": "JMF",
            "value_text": str(jmf_value),
            "value_numeric": Decimal(jmf_value),
            "unit": "days",
            "note": None,
            "trust_tier": spec.cls,
            "confidence_weight": spec.weight,
            "is_outlier_rejected": False,
        })
        candidates.append(Candidate("JMF", Decimal(jmf_value), name_he=name_he))

    # Tend OP source(s)
    for tend_dtm in tend_values:
        if tend_dtm is None:
            continue
        spec = get_source_spec("Tend")
        rows.append({
            "field_name": "days_to_maturity",
            "source": "Tend",
            "value_text": str(tend_dtm),
            "value_numeric": Decimal(tend_dtm),
            "unit": "days",
            "note": None,
            "trust_tier": spec.cls,
            "confidence_weight": spec.weight,
            "is_outlier_rejected": False,
        })
        candidates.append(Candidate("Tend", Decimal(tend_dtm), name_he=name_he))

    # Reconcile to detect outliers and determine best value
    consensus = reconcile_field("days_to_maturity", candidates)

    # Back-populate outlier flag + note on emitted row dicts.
    # Match by (source, value) tuple to handle repeated source labels (e.g. multiple Tend years).
    _rejected_sv: set[tuple[str, Decimal]] = set(consensus.outlier_rejected)
    for row in rows:
        key = (row["source"], row["value_numeric"])
        if key in _rejected_sv:
            row["is_outlier_rejected"] = True
            row["note"] = "OUTLIER_REJECTED — statistical gate"
            logger.warning(
                "DTM outlier rejected: crop=%r source=%r value=%s",
                name_he, row["source"], row["value_numeric"],
            )

    unified = consensus.value_best
    if unified is not None:
        return int(unified), rows
    return None, rows


# ---------------------------------------------------------------------------
# Backward-compat wrapper — reconcile_variety
# ---------------------------------------------------------------------------

_VARIETY_FIELDS = [
    "avg_yield_per_bed_m",
    "in_row_spacing_cm",
    "rows_per_bed",
    "planting_season",
    "harvest_window_min_days",
    "harvest_window_max_days",
    "documented_price",
    "rootstock_variety",
    "seeder",
    "seeder_front_gear",
    "seeder_rear_gear",
    "seeder_roller_plate",
]


def reconcile_variety(source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge per-source rows into a unified crop_varieties field dict.

    Accepts list[dict] format produced by tend.py / jmf.py importers.
    Delegates numeric fields to reconcile_field(); non-numeric fields use
    hard_winner trust order from FIELD_POLICY.

    Returns a partial dict suitable for setting unified fields on CropVariety.
    Only fields with a winning value are included.
    """
    unified: dict[str, Any] = {}

    # Group source rows by field_name
    by_field: dict[str, list[dict[str, Any]]] = {}
    for row in source_rows:
        fn = row.get("field_name", "")
        by_field.setdefault(fn, []).append(row)

    for fn in _VARIETY_FIELDS:
        field_rows = by_field.get(fn, [])
        if not field_rows:
            continue

        numeric_candidates: list[Candidate] = []
        text_by_source: dict[str, tuple[str, str]] = {}  # source → (value_text, unit)

        for row in field_rows:
            src = row.get("source", "")
            vn = row.get("value_numeric")
            vt = row.get("value_text") or ""
            name_he = row.get("name_he", "")

            if vn is not None:
                numeric_candidates.append(Candidate(
                    source_label=src,
                    value=Decimal(str(vn)),
                    name_he=name_he,
                ))
            elif vt:
                text_by_source[src] = (vt, row.get("unit") or "")

        if numeric_candidates:
            consensus = reconcile_field(fn, numeric_candidates)
            if consensus.value_best is not None:
                unified[fn] = consensus.value_best
                if fn == "avg_yield_per_bed_m":
                    # Store the winning source LABEL (e.g. "Tend_2022" or "JMF"),
                    # not the class code, for backward compat with CropVariety.yield_source.
                    unified["yield_source"] = _winning_source_label(numeric_candidates, fn)
                if fn == "documented_price":
                    best_src = _winning_source_label(numeric_candidates, fn)
                    unified["documented_price_source"] = best_src
                    if best_src in text_by_source:
                        unified["documented_price_unit"] = text_by_source[best_src][1]
                    else:
                        for row in field_rows:
                            if row.get("source") == best_src and row.get("unit"):
                                unified["documented_price_unit"] = row["unit"]
                                break

        elif text_by_source:
            # Non-numeric: hard_winner by CLASS_RANK from policy trust_order
            policy = get_field_policy(fn)
            for cls in policy.trust_order:
                for src, (vt, _unit) in text_by_source.items():
                    if get_source_spec(src).cls == cls:
                        unified[fn] = vt
                        break
                if fn in unified:
                    break

    # rootstock → set is_grafted flag
    if unified.get("rootstock_variety"):
        unified["is_grafted"] = True

    return unified


def _winning_source_label(candidates: list[Candidate], field_name: str) -> str:
    """Return the source label of the consensus winner for side-effect tracking.

    Mirrors the strategy logic of reconcile_field so the returned label is consistent
    with the synthetic 'rep_label' used inside the blend (multi_year_op_mean collapse).
    """
    policy = get_field_policy(field_name)
    op = [c for c in candidates if get_source_spec(c.source_label).cls == "OP"]

    if policy.blend_strategy == "latest_op":
        if op:
            return max(c.source_label for c in op)

    if policy.multi_year_op_mean and len(op) > 1:
        # reconcile_field collapses OP values to rep_label = max(source_label)
        return max(c.source_label for c in op)

    winner = min(
        candidates,
        key=lambda c: (CLASS_RANK.get(get_source_spec(c.source_label).cls, 999), c.source_label),
    )
    return winner.source_label
