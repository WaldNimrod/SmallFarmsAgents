"""Enrichment calibration harness — SFA-S003-P002-WP-A LOD400 §12 / AC-13.

Shadow-run calibration: for each variety with at least one EX source_value,
exclude EX rows, run reconcile_field on the non-EX candidates, and compare the
auto-reconciled value against the EX ground truth.

Algorithm (LOD400 §12):
  1. Connect to DB (reads DATABASE_URL from env).
  2. For each variety with at least one EX source_value:
     a. Load all source_values for that variety + field.
     b. Shadow run: exclude EX rows (trust_tier='EX').
     c. Call reconcile_field(field, non_ex_candidates).
     d. Compare auto_value vs ex_value.
     e. Classify: CALIBRATED (≤±20%) / MARGINAL (≤±40%) / MISALIGNED (>±40%).
  3. Print CALIBRATION REPORT ASCII table.
  4. Exit 0 always — misalignment is a data quality signal, not a build failure.

Usage:
    python scripts/validate_enrichment.py
    python scripts/validate_enrichment.py --field days_to_maturity
    python scripts/validate_enrichment.py --verbose
"""

from __future__ import annotations

import argparse
import logging
import sys
from decimal import Decimal
from typing import Optional

sys.path.insert(0, ".")

logger = logging.getLogger(__name__)

# Classification thresholds (relative delta = |auto - ex| / |ex|)
_CALIBRATED_THRESHOLD = Decimal("0.20")
_MARGINAL_THRESHOLD = Decimal("0.40")


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        format="%(levelname)s %(name)s: %(message)s",
        level=level,
        stream=sys.stderr,
    )


def _classify(delta_rel: Optional[Decimal]) -> str:
    """Classify a relative delta into CALIBRATED / MARGINAL / MISALIGNED."""
    if delta_rel is None:
        return "MISALIGNED"
    if delta_rel <= _CALIBRATED_THRESHOLD:
        return "CALIBRATED"
    if delta_rel <= _MARGINAL_THRESHOLD:
        return "MARGINAL"
    return "MISALIGNED"


def _print_report(rows: list[dict]) -> None:
    """Print the CALIBRATION REPORT ASCII table to stdout."""
    col_widths = {
        "crop": max(12, max((len(r["crop"]) for r in rows), default=0)),
        "variety_id": 10,
        "field": max(8, max((len(r["field"]) for r in rows), default=0)),
        "ex_value": 10,
        "auto_value": 10,
        "delta_pct": 10,
        "status": 11,
    }

    def _row_fmt(r: dict) -> str:
        ex_s = str(r["ex_value"]) if r["ex_value"] is not None else "N/A"
        auto_s = str(r["auto_value"]) if r["auto_value"] is not None else "N/A"
        delta_s = (
            f"{float(r['delta_pct']):.1f}%"
            if r["delta_pct"] is not None else "N/A"
        )
        return (
            f"| {r['crop']:<{col_widths['crop']}} "
            f"| {r['variety_id']:<{col_widths['variety_id']}} "
            f"| {r['field']:<{col_widths['field']}} "
            f"| {ex_s:>{col_widths['ex_value']}} "
            f"| {auto_s:>{col_widths['auto_value']}} "
            f"| {delta_s:>{col_widths['delta_pct']}} "
            f"| {r['status']:<{col_widths['status']}} |"
        )

    sep = (
        f"+{'-'*(col_widths['crop']+2)}"
        f"+{'-'*(col_widths['variety_id']+2)}"
        f"+{'-'*(col_widths['field']+2)}"
        f"+{'-'*(col_widths['ex_value']+2)}"
        f"+{'-'*(col_widths['auto_value']+2)}"
        f"+{'-'*(col_widths['delta_pct']+2)}"
        f"+{'-'*(col_widths['status']+2)}+"
    )
    header = (
        f"| {'crop':<{col_widths['crop']}} "
        f"| {'variety_id':<{col_widths['variety_id']}} "
        f"| {'field':<{col_widths['field']}} "
        f"| {'ex_value':>{col_widths['ex_value']}} "
        f"| {'auto_value':>{col_widths['auto_value']}} "
        f"| {'delta_%':>{col_widths['delta_pct']}} "
        f"| {'status':<{col_widths['status']}} |"
    )

    print()
    print("=" * len(sep))
    print("CALIBRATION REPORT — SFA-S003-P002-WP-A shadow-run calibration")
    print("=" * len(sep))
    print(sep)
    print(header)
    print(sep)
    for r in rows:
        print(_row_fmt(r))
    print(sep)

    total = len(rows)
    cal = sum(1 for r in rows if r["status"] == "CALIBRATED")
    mar = sum(1 for r in rows if r["status"] == "MARGINAL")
    mis = sum(1 for r in rows if r["status"] == "MISALIGNED")
    print(
        f"\nSummary: {total} rows — "
        f"CALIBRATED={cal}  MARGINAL={mar}  MISALIGNED={mis}"
    )
    print()


def run_calibration(field_filter: Optional[str] = None, verbose: bool = False) -> list[dict]:
    """Execute shadow-run calibration and return report rows.

    Args:
        field_filter: If set, only calibrate this field_name.
        verbose:      Passed to _setup_logging (already called before this).

    Returns:
        List of dicts with keys: crop, variety_id, field, ex_value, auto_value,
        delta_pct (Decimal %, relative), status (str).
    """
    from decimal import Decimal as D

    from organic_market_agent.crop_book.importer.reconciler import Candidate, reconcile_field
    # Import enrichment_models so SQLAlchemy resolves the CropVariety.enrichments relationship
    import organic_market_agent.crop_book.enrichment_models  # noqa: F401
    from organic_market_agent.crop_book.models import Crop, CropVariety, CropVarietySourceValue
    from organic_market_agent.db.session import SessionFactory

    report_rows: list[dict] = []

    with SessionFactory() as session:
        # Find all (variety_id, field_name) pairs that have at least one EX row
        ex_rows_q = (
            session.query(
                CropVarietySourceValue.variety_id,
                CropVarietySourceValue.field_name,
            )
            .filter(CropVarietySourceValue.trust_tier == "EX")
            .distinct()
        )
        if field_filter:
            ex_rows_q = ex_rows_q.filter(
                CropVarietySourceValue.field_name == field_filter
            )

        ex_pairs = ex_rows_q.all()
        logger.debug("Found %d (variety, field) pairs with EX source values", len(ex_pairs))

        for variety_id, field_name in ex_pairs:
            # Resolve crop name for display
            variety = session.query(CropVariety).filter_by(id=variety_id).first()
            crop = session.query(Crop).filter_by(id=variety.crop_id).first() if variety else None
            crop_name = crop.name_he if crop else f"variety:{variety_id}"

            # Get EX value (use the first EX row's value)
            ex_sv = (
                session.query(CropVarietySourceValue)
                .filter_by(variety_id=variety_id, field_name=field_name, trust_tier="EX")
                .order_by(CropVarietySourceValue.id)
                .first()
            )
            if ex_sv is None or ex_sv.value_numeric is None:
                logger.debug(
                    "SKIP variety_id=%d field=%s: EX row has no numeric value",
                    variety_id, field_name,
                )
                continue

            ex_value: Decimal = ex_sv.value_numeric

            # Shadow run: collect non-EX source_values for this (variety, field)
            # with variety→species inheritance fallback (engine v1.1 — 2026-05-26).
            # If this variety has no own non-EX data, inherit from default
            # variety of same crop. See reconciler.collect_source_values_with_inheritance.
            from organic_market_agent.crop_book.importer.reconciler import (
                collect_source_values_with_inheritance,
            )
            non_ex_svs_all = collect_source_values_with_inheritance(
                session, variety_id, field_name=field_name, exclude_ex=True
            )
            non_ex_svs = [sv for sv in non_ex_svs_all if sv.value_numeric is not None]

            # Build Candidate list from non-EX rows
            candidates = []
            for sv in non_ex_svs:
                # UC unmoderated exclusion: confidence_weight must be set and > 0
                if sv.trust_tier == "UC" and (
                    sv.confidence_weight is None or sv.confidence_weight <= 0
                ):
                    continue
                candidates.append(
                    Candidate(
                        source_label=sv.source,
                        value=sv.value_numeric,
                        name_he=crop_name,
                        moderation_weight=(
                            float(sv.confidence_weight)
                            if sv.confidence_weight is not None else None
                        ),
                    )
                )

            # Run reconcile_field without EX rows
            consensus = reconcile_field(field_name, candidates)
            auto_value: Optional[Decimal] = consensus.value_best

            # Compute relative delta
            delta_rel: Optional[Decimal] = None
            delta_pct: Optional[Decimal] = None
            if auto_value is not None and ex_value != 0:
                delta_rel = abs(auto_value - ex_value) / abs(ex_value)
                delta_pct = delta_rel * D("100")
            elif auto_value is not None and ex_value == 0:
                # Special case: ex=0; use absolute difference
                delta_rel = abs(auto_value - ex_value)
                delta_pct = None  # cannot express as %

            status = _classify(delta_rel)
            logger.debug(
                "variety_id=%d field=%s ex=%s auto=%s delta_rel=%s => %s",
                variety_id, field_name, ex_value, auto_value, delta_rel, status,
            )

            report_rows.append({
                "crop": crop_name,
                "variety_id": variety_id,
                "field": field_name,
                "ex_value": ex_value,
                "auto_value": auto_value,
                "delta_pct": delta_pct,
                "status": status,
            })

    return report_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Enrichment calibration harness — shadow-run against EX overrides "
            "(LOD400 §12). Always exits 0."
        )
    )
    parser.add_argument(
        "--field", metavar="FIELD",
        help="Restrict calibration to a single field_name",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)

    rows = run_calibration(field_filter=args.field, verbose=args.verbose)
    _print_report(rows)

    # Exit 0 always — misalignment is data quality signal, not build failure (LOD400 §12)
    sys.exit(0)


if __name__ == "__main__":
    main()
