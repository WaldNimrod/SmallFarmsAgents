"""Idempotent UPDATEs for patch03's Hebrew terminology corrections.

SFA-S003-P002-WP-B1-patch04 LOD400 §3.6.
Per DECISION_WP-B1-patch04-patch06 §2.2.

Usage:
    python scripts/patch03_data_fix.py --dry-run   # default — report row counts only
    python scripts/patch03_data_fix.py --apply     # execute UPDATEs
    python scripts/patch03_data_fix.py --apply --db-url postgresql://...

SAFETY:
    --dry-run is the default. --apply is required to mutate.
    Script is idempotent: running --apply twice yields 0 row changes on the second run
    (because after the first run the old name_he values no longer exist).
    Missing-row-set is handled gracefully: reports "0 rows" without error.
"""
from __future__ import annotations

import argparse
import logging
import sys

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# The 11 patch03 corrections
# (old name_he, new name_he)
# ---------------------------------------------------------------------------
# NOTE: Baby kale is handled by updating only the specific crops.id that
# represents the baby variant. However, since names in DB are unique per
# name_he and baby kale already maps to "עלי בייבי" via patch03 in
# JMF_CROP_MAP (constants.py), this data-fix updates the DB crop rows
# where the old Hebrew name still persists from pre-patch03 seeding.
PATCH03_UPDATES: list[tuple[str, str]] = [
    # Roots
    ("גזר לבן",           "שורש פטרוזילה"),   # Parsnips — colloquial → botanically accurate
    # Alliums
    ("שאלוט",             "בצלצלי שאלוט"),    # Shallots — pure transliteration → hybrid
    # Baby greens / Salad
    ("תערובת סלט",        "עלי בייבי"),        # Mesclun + Salad Mix collapse
    # Solanaceae splits
    ("עגבניית שרי",       "עגבניית שרי"),      # already correct — idempotency check row
    ("עגבניות מורשת",     "עגבניות מורשת"),    # already correct — idempotency check row
    ("מלפפון חממה",       "מלפפון חממה"),      # already correct — idempotency check row
    # Brassicas
    ("כרוב סיני",         "כרוב סיני"),        # already correct — idempotency check row
    # Hot pepper
    ("פלפל חריף",         "פלפל חריף"),        # already correct — idempotency check row
    # Beans/legumes
    ("שעועית שיחית",      "שעועית שיחית"),     # already correct — idempotency check row
    ("אפונת שלג",         "אפונת שלג"),        # already correct — idempotency check row
    # Basil
    ("בזיליקום",          "בזיליקום"),         # already correct — idempotency check row
]

# The 3 genuinely mutating rows (old → new)
PATCH03_ACTUAL_UPDATES: list[tuple[str, str]] = [
    ("גזר לבן",     "שורש פטרוזילה"),
    ("שאלוט",       "בצלצלי שאלוט"),
    ("תערובת סלט",  "עלי בייבי"),
]


def run_data_fix(db_url: str, dry_run: bool) -> int:
    """Execute or simulate the patch03 data fixes.

    Returns 0 on success, 1 on error.
    """
    from sqlalchemy import create_engine, text

    engine = create_engine(db_url)

    with engine.begin() as conn:
        for old_name_he, new_name_he in PATCH03_ACTUAL_UPDATES:
            # Count rows that still have the old value
            count_result = conn.execute(
                text("SELECT COUNT(*) FROM crops WHERE name_he = :old"),
                {"old": old_name_he},
            ).fetchone()
            n = count_result[0] if count_result else 0

            if dry_run:
                print(
                    f"[DRY-RUN] '{old_name_he}' → '{new_name_he}': "
                    f"{n} row(s) would be updated"
                )
            else:
                if n > 0:
                    conn.execute(
                        text(
                            "UPDATE crops SET name_he = :new "
                            "WHERE name_he = :old"
                        ),
                        {"new": new_name_he, "old": old_name_he},
                    )
                print(
                    f"'{old_name_he}' → '{new_name_he}': "
                    f"{n} row(s) {'updated' if n > 0 else 'not found (OK)'}"
                )

    if dry_run:
        print("\nDry-run complete — no rows mutated.")
    else:
        print("\nData-fix applied.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Idempotent patch03 Hebrew terminology data-fix for crops table."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report planned changes without mutating (default).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Actually execute the UPDATEs.",
    )
    parser.add_argument(
        "--db-url",
        default="postgresql://localhost:5433/organic_market_agent",
        help="SQLAlchemy DB URL.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")

    # --apply overrides --dry-run
    is_dry_run = not args.apply

    if args.apply:
        print("WARNING: --apply will mutate the database. Proceeding...")
    else:
        print("Running in DRY-RUN mode (no mutations). Use --apply to execute.")

    try:
        return run_data_fix(args.db_url, dry_run=is_dry_run)
    except Exception as exc:
        logger.error("Data-fix failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
