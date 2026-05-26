"""Idempotent DELETE of noise variety rows from crop_varieties.

SFA-S003-P002-WP-B1-patch08 LOD400 §3.2.

Deletes rows that match known noise heuristics (URLs, bullets, single
chars, sentence fragments, comma-separated lists, overly long strings)
OR the explicit section-header blacklist (mirrors KNOWN_SECTION_HEADERS
in load_masterclass_sheets.py).

Usage:
    python scripts/patch08_cleanup_noise_varieties.py --dry-run
        (default: report planned deletions without mutating)

    python scripts/patch08_cleanup_noise_varieties.py --apply --db-url <url>
        (delete rows; idempotent — second run is a no-op)

CRITICAL: Do NOT run against production Postgres until after L-GATE_V PASS.
    The actual production DELETE is an operational step post-LOD500_LOCKED.
    This script is built and verified via dry-run + SQLite fixture tests only
    at build time.
"""
from __future__ import annotations

import argparse
import logging
import sys

log = logging.getLogger(__name__)

# Mirrors the Python filter's KNOWN_SECTION_HEADERS — kept in sync.
# Adding 'Intensive Spacing' explicitly resolves F-S-PATCH08-01 BLOCKER (v1.0.1 R2).
KNOWN_SECTION_HEADERS = (
    'Intensive Spacing',
    'Cultivars',
    'Cultivar Suggestions',
    'Pests',
    'Diseases',
    'Harvest',
    'Storage',
    'Sowing',
    'Transplanting',
    'Yield',
)


def run_cleanup(db_url: str, dry_run: bool) -> int:
    """Find and optionally delete noise variety rows.

    Returns exit code (0 = success, 1 = error).
    """
    try:
        from sqlalchemy import create_engine, text
    except ImportError:
        log.error("sqlalchemy is required: pip install sqlalchemy")
        return 1

    try:
        engine = create_engine(db_url)
        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT id, name_en FROM crop_varieties
                    WHERE
                        name_en LIKE '%://%' OR
                        name_en LIKE '%.com%' OR
                        name_en LIKE '%.org%' OR
                        name_en LIKE '%.io%' OR
                        name_en IN ('●', '○', '-', '*', '1', '2', '3') OR
                        length(name_en) > 40 OR
                        name_en LIKE '%: %' OR
                        (length(name_en) > 6 AND name_en LIKE '%.') OR
                        name_en = ANY(:section_headers)
                """),
                {"section_headers": list(KNOWN_SECTION_HEADERS)},
            )
            rows = result.fetchall()
    except Exception as exc:
        # SQLite does not support ANY(:section_headers); fall back to IN clause
        # for SQLite compatibility (used in test fixtures)
        try:
            placeholders = ", ".join(f":sh{i}" for i in range(len(KNOWN_SECTION_HEADERS)))
            params: dict = {f"sh{i}": v for i, v in enumerate(KNOWN_SECTION_HEADERS)}
            with engine.begin() as conn:
                result = conn.execute(
                    text(f"""
                        SELECT id, name_en FROM crop_varieties
                        WHERE
                            name_en LIKE '%://%' OR
                            name_en LIKE '%.com%' OR
                            name_en LIKE '%.org%' OR
                            name_en LIKE '%.io%' OR
                            name_en IN ('●', '○', '-', '*', '1', '2', '3') OR
                            length(name_en) > 40 OR
                            name_en LIKE '%: %' OR
                            (length(name_en) > 6 AND name_en LIKE '%.') OR
                            name_en IN ({placeholders})
                    """),
                    params,
                )
                rows = result.fetchall()
        except Exception as exc2:
            log.error("Query failed: %s", exc2)
            return 1

    log.info("Found %d noise variety row(s)", len(rows))
    for r in rows:
        log.info("  id=%s name_en=%r", r[0], r[1])

    if dry_run:
        print(f"[DRY-RUN] Would delete {len(rows)} noise variety row(s).")
        for r in rows:
            print(f"  id={r[0]} name_en={r[1]!r}")
        return 0

    if not rows:
        log.info("No noise rows found — already clean (idempotent no-op).")
        return 0

    try:
        ids = [r[0] for r in rows]
        # Use dialect-aware delete: ANY for Postgres, IN for SQLite
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM crop_varieties WHERE id = ANY(:ids)"),
                    {"ids": ids},
                )
        except Exception:
            # SQLite fallback
            placeholders = ", ".join(f":id{i}" for i in range(len(ids)))
            id_params = {f"id{i}": v for i, v in enumerate(ids)}
            with engine.begin() as conn:
                conn.execute(
                    text(f"DELETE FROM crop_varieties WHERE id IN ({placeholders})"),
                    id_params,
                )
        log.info("Deleted %d noise variety row(s).", len(rows))
        print(f"Deleted {len(rows)} noise variety row(s).")
    except Exception as exc:
        log.error("DELETE failed: %s", exc)
        return 1

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Delete noise variety rows from crop_varieties (idempotent)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Report planned deletions without mutating (default: True).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete the rows (overrides --dry-run).",
    )
    parser.add_argument(
        "--db-url",
        default="sqlite:///dev.db",
        help="SQLAlchemy DB URL (default: sqlite:///dev.db).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    dry_run = not args.apply
    if dry_run:
        print("[DRY-RUN MODE] No rows will be deleted. Pass --apply to mutate.")

    return run_cleanup(db_url=args.db_url, dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
