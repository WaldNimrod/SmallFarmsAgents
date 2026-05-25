"""Idempotent cleanup of crops rows whose name_he is no longer reachable from
the cleaned JMF_CROP_MAP. Specifically targets the patch03 §1.3 anomaly row
(name_he = 'מלפפון חממה').

Usage:
  python scripts/patch06_db_cleanup.py --dry-run
  python scripts/patch06_db_cleanup.py --apply

Per DECISION_WP-B1-patch04-patch06 §3.5.
"""
from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Iterable
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("patch06_db_cleanup")

# ---------------------------------------------------------------------------
# Orphan definition
# ---------------------------------------------------------------------------
# These crops.name_he values are no longer reachable from any JMF_CROP_MAP
# key after patch06. Any rows linked to them (crop_varieties, crop_knowledge_notes)
# should be re-pointed to the canonical baseline before the orphan row is deleted.
#
# Format: { orphan_name_he: canonical_replacement_name_he }
ORPHAN_MAP: dict[str, str] = {
    "מלפפון חממה": "מלפפון",   # patch03 §1.3 anomaly — Greenhouse Libanese Cucumber removed from MAP
}


def _get_session_cm() -> Any:
    """Return the project's get_session() context manager.

    NOTE: get_session is decorated with @contextmanager — callers MUST use
    `with _get_session_cm() as session:`. team_190 L-GATE_V R1 BLOCKER
    confirmed that treating the return value as a raw Session fails at
    runtime. Also imports all related models so SQLAlchemy can resolve
    cross-model relationships before any session.query() runs."""
    try:
        # Pre-import all models referenced by Crop's relationships so the
        # SQLAlchemy mapper registry is complete before query execution.
        # Without this, CropFieldEnrichment (used in Crop relationships) is
        # not resolvable when Crop's mapper initializes via session.query(Crop).
        from organic_market_agent.crop_book import models  # noqa: F401 — register
        from organic_market_agent.crop_book import enrichment_models  # noqa: F401 — register CropFieldEnrichment
        try:
            from organic_market_agent.crop_book import crop_knowledge_notes_crops  # noqa: F401 — register patch04 junction
        except ImportError:
            pass  # junction model exists only if patch04 is applied — gracefully optional
        from organic_market_agent.db.session import get_session
        return get_session()
    except ImportError as exc:
        log.error("Cannot import DB session: %s", exc)
        sys.exit(1)


def _find_orphan_crop(session: Any, name_he: str) -> Any | None:
    """Return the Crop ORM row with name_he, or None if not found."""
    try:
        from organic_market_agent.crop_book.crop import Crop  # type: ignore[import]
    except ImportError:
        try:
            from organic_market_agent.crop_book.models import Crop  # type: ignore[import]
        except ImportError:
            log.error("Cannot import Crop model — check project structure")
            sys.exit(1)
    return session.query(Crop).filter_by(name_he=name_he).first()


def _find_canonical_crop(session: Any, name_he: str) -> Any | None:
    """Return the canonical Crop ORM row for the replacement name_he."""
    try:
        from organic_market_agent.crop_book.crop import Crop  # type: ignore[import]
    except ImportError:
        from organic_market_agent.crop_book.models import Crop  # type: ignore[import]
    return session.query(Crop).filter_by(name_he=name_he).first()


def process_orphan(
    session: Any,
    orphan_name_he: str,
    canonical_name_he: str,
    dry_run: bool,
) -> dict[str, int]:
    """Re-point FK references from orphan crop to canonical crop, then delete orphan.

    Returns a dict of {"crop_varieties": N, "crop_knowledge_notes": N, "crops_deleted": N}.
    """
    stats: dict[str, int] = {
        "crop_varieties": 0,
        "crop_knowledge_notes": 0,
        "crops_deleted": 0,
    }

    orphan = _find_orphan_crop(session, orphan_name_he)
    if orphan is None:
        log.info("Orphan crop '%s' not found in DB — nothing to do (idempotent).", orphan_name_he)
        return stats

    canonical = _find_canonical_crop(session, canonical_name_he)
    if canonical is None:
        log.error(
            "Canonical replacement crop '%s' not found in DB. Cannot re-point FKs. Skipping.",
            canonical_name_he,
        )
        return stats

    log.info(
        "%s: orphan crop id=%s ('%s') → canonical id=%s ('%s')",
        "DRY-RUN" if dry_run else "APPLY",
        orphan.id,
        orphan_name_he,
        canonical.id,
        canonical_name_he,
    )

    # Re-point crop_varieties
    try:
        from organic_market_agent.crop_book.crop_varieties import CropVariety  # type: ignore[import]
        varieties = session.query(CropVariety).filter_by(crop_id=orphan.id).all()
        for v in varieties:
            log.info("  crop_varieties id=%s: crop_id %s → %s", v.id, orphan.id, canonical.id)
            stats["crop_varieties"] += 1
            if not dry_run:
                v.crop_id = canonical.id
    except ImportError:
        log.warning("CropVariety model not importable — skipping crop_varieties re-pointing")

    # Re-point crop_knowledge_notes
    try:
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote  # type: ignore[import]
        notes = session.query(CropKnowledgeNote).filter_by(crop_id=orphan.id).all()
        for n in notes:
            log.info("  crop_knowledge_notes id=%s: crop_id %s → %s", n.id, orphan.id, canonical.id)
            stats["crop_knowledge_notes"] += 1
            if not dry_run:
                n.crop_id = canonical.id
    except ImportError:
        log.warning("CropKnowledgeNote model not importable — skipping crop_knowledge_notes re-pointing")

    # Delete orphan
    stats["crops_deleted"] = 1
    if not dry_run:
        session.delete(orphan)
        log.info("  Deleted orphan crop id=%s ('%s')", orphan.id, orphan_name_he)
    else:
        log.info("  [DRY-RUN] Would delete orphan crop id=%s ('%s')", orphan.id, orphan_name_he)

    return stats


def main(dry_run: bool) -> None:
    if dry_run:
        log.info("=== patch06_db_cleanup: DRY-RUN mode (no DB changes) ===")
    else:
        log.info("=== patch06_db_cleanup: APPLY mode ===")

    total: dict[str, int] = {"crop_varieties": 0, "crop_knowledge_notes": 0, "crops_deleted": 0}

    # get_session() is a @contextmanager — must use `with`. The CM handles
    # commit-on-success / rollback-on-exception / close in its own teardown,
    # so we only commit explicitly inside the block for the --apply path
    # (the CM's default behavior commits on clean exit, matching our intent).
    try:
        with _get_session_cm() as session:
            for orphan_name_he, canonical_name_he in ORPHAN_MAP.items():
                stats = process_orphan(session, orphan_name_he, canonical_name_he, dry_run)
                for k in total:
                    total[k] += stats[k]

            if dry_run:
                # Roll back any speculative changes (process_orphan may have
                # done session.delete on dry-run path — defensively undo)
                session.rollback()
                log.info("=== DRY-RUN complete. Planned changes: %s", total)
            else:
                session.commit()
                log.info("=== Committed. Summary: %s", total)
    except Exception:
        log.exception("Error during cleanup — context manager rolled back")
        sys.exit(1)

    if total["crops_deleted"] == 0:
        log.info("=== No orphan crops found — DB is already clean (idempotent). ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Idempotent cleanup of orphan crops rows after patch06 JMF_CROP_MAP cleanup."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report planned changes without applying")
    group.add_argument("--apply", action="store_true", help="Apply changes to the database")
    args = parser.parse_args()

    main(dry_run=args.dry_run)
