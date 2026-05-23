"""Enrichment validation harness — SFA-S003-P002-WP-A LOD400 §17 Step 8.

Shadow-run calibration: compares the enrichment_runner's computed consensus
against team_00 EX override values (ground truth) stored in constants.py.

For each variety/field where an EX override exists, this script verifies that:
  1. crop_field_enrichment has a row for that (variety_id, field_name).
  2. value_best matches the EX override (within numeric tolerance).
  3. winning_source_class == "EX".
  4. confidence_score == 1.0000.

Exit codes:
    0 — all checks pass
    1 — one or more calibration failures detected

Usage:
    python scripts/validate_enrichment.py
    python scripts/validate_enrichment.py --verbose
    python scripts/validate_enrichment.py --dry-run   (run enrichment first, then validate)
"""

from __future__ import annotations

import argparse
import logging
import sys
from decimal import Decimal
from typing import Any

sys.path.insert(0, ".")

logger = logging.getLogger(__name__)

# Numeric tolerance for float comparison
_TOL = Decimal("0.5")


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s %(name)s: %(message)s",
        level=level,
        stream=sys.stdout,
    )


def _run_enrichment_and_validate(dry_run_enrich: bool, verbose: bool) -> int:
    """Main validation logic. Returns exit code (0=pass, 1=fail)."""
    from organic_market_agent.crop_book.constants import TEAM00_DTM_OVERRIDES
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.models import Crop, CropVariety
    from organic_market_agent.db.session import SessionFactory

    failures: list[str] = []
    checks: int = 0

    with SessionFactory() as session:
        if dry_run_enrich:
            logger.info("Running enrichment before validation (dry_run=False)...")
            summary = run_enrichment(session, dry_run=False)
            session.commit()
            logger.info("Enrichment done: %s", summary)

        # --- Calibration check: TEAM00_DTM_OVERRIDES ---
        # These are EX hard overrides for days_to_maturity, keyed by name_he.
        logger.info(
            "Calibrating against TEAM00_DTM_OVERRIDES (%d crops)...",
            len(TEAM00_DTM_OVERRIDES),
        )

        for name_he, expected_dtm in TEAM00_DTM_OVERRIDES.items():
            # Find the default variety for this crop
            variety = (
                session.query(CropVariety)
                .join(Crop, CropVariety.crop_id == Crop.id)
                .filter(Crop.name_he == name_he, CropVariety.is_default == True)
                .first()
            )
            if variety is None:
                logger.debug("SKIP: no default variety found for crop %r", name_he)
                continue

            enrichment_row = (
                session.query(CropFieldEnrichment)
                .filter_by(variety_id=variety.id, field_name="days_to_maturity")
                .first()
            )

            checks += 1

            if enrichment_row is None:
                msg = (
                    f"FAIL crop={name_he!r} variety_id={variety.id}: "
                    f"no crop_field_enrichment row for days_to_maturity"
                )
                failures.append(msg)
                logger.error(msg)
                continue

            # Check winning_source_class
            if enrichment_row.winning_source_class != "EX":
                msg = (
                    f"FAIL crop={name_he!r} variety_id={variety.id}: "
                    f"winning_source_class={enrichment_row.winning_source_class!r} "
                    f"expected='EX'"
                )
                failures.append(msg)
                logger.error(msg)

            # Check confidence_score
            if enrichment_row.confidence_score != Decimal("1.0000"):
                msg = (
                    f"FAIL crop={name_he!r} variety_id={variety.id}: "
                    f"confidence_score={enrichment_row.confidence_score} expected=1.0000"
                )
                failures.append(msg)
                logger.error(msg)

            # Check value_best matches override (within tolerance)
            if enrichment_row.value_best is None:
                msg = (
                    f"FAIL crop={name_he!r} variety_id={variety.id}: "
                    f"value_best is NULL, expected {expected_dtm}"
                )
                failures.append(msg)
                logger.error(msg)
            else:
                diff = abs(enrichment_row.value_best - Decimal(expected_dtm))
                if diff > _TOL:
                    msg = (
                        f"FAIL crop={name_he!r} variety_id={variety.id}: "
                        f"value_best={enrichment_row.value_best} "
                        f"expected={expected_dtm} diff={diff} > tol={_TOL}"
                    )
                    failures.append(msg)
                    logger.error(msg)
                else:
                    logger.info(
                        "OK   crop=%-20r dtm=%s (EX override confirmed)",
                        name_he, enrichment_row.value_best,
                    )

        # --- Summary ---
        logger.info("")
        logger.info("Calibration checks: %d total, %d failures", checks, len(failures))

        if failures:
            logger.error("VALIDATION FAILED — %d/%d checks failed:", len(failures), checks)
            for f in failures:
                logger.error("  %s", f)
            return 1

        if checks == 0:
            logger.warning(
                "No EX override calibration rows found — "
                "ensure enrichment has been run and TEAM00_DTM_OVERRIDES is populated"
            )
            return 0

        logger.info("VALIDATION PASSED — all %d EX override calibration checks pass", checks)
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrichment calibration harness — validates EX override consensus rows"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run enrichment_runner before validating (ensures crop_field_enrichment is populated)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    _setup_logging(args.verbose)
    sys.exit(_run_enrichment_and_validate(dry_run_enrich=args.dry_run, verbose=args.verbose))


if __name__ == "__main__":
    main()
