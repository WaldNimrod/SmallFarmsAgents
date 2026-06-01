"""Ingest Nimrod validation JSON → NI source_values → re-resolve (WP-CB-MIG2 WI-11 / AC-13).

Reads the JSON exported from the crop gap console (or from stdin), writes
crop_variety_source_values rows as NI class ('NI:nimrod_validation', hard override),
then re-runs attribute_resolver + enrichment_runner so attributes/enrichment reflect
the new values. Idempotent. Supports --dry-run.

Input JSON shape (array):
    [
      {
        "variety_id": 123,
        "field_name": "irrigation_type",
        "value": "drip",
        "is_numeric": false,
        "crop_name_he": "עגבניה",
        "topic": "irrigation"
      },
      ...
    ]

Usage:
    python scripts/ingest_nimrod_validation.py --input data/nimrod_validation.json --db-url ...
    cat validation.json | python scripts/ingest_nimrod_validation.py --db-url ... --stdin
    python scripts/ingest_nimrod_validation.py --input ... --dry-run
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Source label for Nimrod validation (NI class — hard override above PR)
NI_SOURCE_LABEL = "NI:nimrod_validation"
NI_TRUST_TIER = "NI"
NI_WEIGHT = 1.0  # Full weight — NI is a hard override


def _validate_item(item: dict, idx: int) -> list[str]:
    """Validate a single validation item. Returns list of error strings."""
    errors = []
    if not isinstance(item.get("variety_id"), int):
        errors.append(f"[{idx}] variety_id must be int (got {item.get('variety_id')!r})")
    if not isinstance(item.get("field_name"), str) or not item["field_name"].strip():
        errors.append(f"[{idx}] field_name must be non-empty str")
    if "value" not in item:
        errors.append(f"[{idx}] value is required")
    if not isinstance(item.get("is_numeric"), bool):
        errors.append(f"[{idx}] is_numeric must be bool")
    return errors


def ingest_validation_json(
    items: list[dict],
    db_url: str,
    dry_run: bool = False,
) -> dict[str, int]:
    """Write NI source_values rows and re-run resolver + enrichment.

    Returns summary dict with counts.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    # Validate all items first
    all_errors = []
    for i, item in enumerate(items):
        all_errors.extend(_validate_item(item, i))
    if all_errors:
        for err in all_errors:
            logger.error("Validation error: %s", err)
        raise ValueError(f"{len(all_errors)} validation error(s) in input JSON")

    engine = create_engine(db_url)
    Session = sessionmaker(engine)
    rows_upserted = 0
    varieties_resolved = set()

    with Session() as session:
        now = datetime.now(timezone.utc).isoformat()

        for item in items:
            variety_id = int(item["variety_id"])
            field_name = str(item["field_name"]).strip()
            value = item["value"]
            is_numeric = bool(item["is_numeric"])

            value_text: str | None = None
            value_numeric: float | None = None
            if is_numeric:
                try:
                    value_numeric = float(value)
                except (TypeError, ValueError):
                    logger.warning(
                        "Could not parse numeric value %r for field %r variety %d — skipping",
                        value, field_name, variety_id,
                    )
                    continue
            else:
                value_text = str(value).strip() if value else None

            if value_text is None and value_numeric is None:
                logger.debug("Empty value for %r variety %d — skipping", field_name, variety_id)
                continue

            if not dry_run:
                session.execute(
                    text(
                        "INSERT INTO crop_variety_source_values "
                        "(variety_id, source, field_name, value_text, value_numeric, "
                        " trust_tier, confidence_weight, created_at, updated_at) "
                        "VALUES (:vid, :src, :fn, :vt, :vn, :tier, :weight, :now, :now) "
                        "ON CONFLICT (variety_id, source, field_name) DO UPDATE SET "
                        "  value_text = EXCLUDED.value_text, "
                        "  value_numeric = EXCLUDED.value_numeric, "
                        "  updated_at = EXCLUDED.updated_at"
                    ),
                    {
                        "vid": variety_id,
                        "src": NI_SOURCE_LABEL,
                        "fn": field_name,
                        "vt": value_text,
                        "vn": value_numeric,
                        "tier": NI_TRUST_TIER,
                        "weight": NI_WEIGHT,
                        "now": now,
                    },
                )
            rows_upserted += 1
            varieties_resolved.add(variety_id)
            logger.debug(
                "Upserted NI source_value: variety=%d field=%r value_text=%r value_numeric=%r",
                variety_id, field_name, value_text, value_numeric,
            )

        if not dry_run:
            session.commit()
            logger.info("Committed %d NI source_value rows", rows_upserted)

    # Re-run attribute_resolver + enrichment_runner for the affected varieties
    varieties_list = list(varieties_resolved)
    attr_rows_written = 0
    enrich_fields = 0

    if varieties_list and not dry_run:
        with Session() as session:
            from organic_market_agent.crop_book.importer.attribute_resolver import (
                run_attribute_resolver,
            )
            from organic_market_agent.crop_book.importer.enrichment_runner import (
                run_enrichment,
            )

            logger.info("Re-running attribute_resolver for %d varieties", len(varieties_list))
            attr_summary = run_attribute_resolver(session, variety_ids=varieties_list)
            attr_rows_written = attr_summary.attribute_rows_written

            logger.info("Re-running enrichment_runner for %d varieties", len(varieties_list))
            enrich_summary = run_enrichment(session, variety_ids=varieties_list)
            enrich_fields = enrich_summary.field_count

            session.commit()

    return {
        "rows_upserted": rows_upserted,
        "varieties_affected": len(varieties_resolved),
        "attr_rows_written": attr_rows_written,
        "enrich_fields": enrich_fields,
        "dry_run": dry_run,
    }


def cli_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest Nimrod validation JSON → NI source_values (WP-CB-MIG2)."
    )
    parser.add_argument("--input", "-i", default=None,
                        help="Path to validation JSON file (or use --stdin).")
    parser.add_argument("--stdin", action="store_true",
                        help="Read JSON from stdin.")
    parser.add_argument("--db-url", default="sqlite:///dev.db",
                        help="SQLAlchemy DB URL.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate input + count rows without writing to DB.")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.stdin:
        raw = sys.stdin.read()
    elif args.input:
        raw = Path(args.input).read_text(encoding="utf-8")
    else:
        logger.error("Provide --input FILE or --stdin")
        return 1

    try:
        items = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON: %s", exc)
        return 1

    if not isinstance(items, list):
        logger.error("Input JSON must be an array")
        return 1

    logger.info("Loaded %d validation items", len(items))

    try:
        summary = ingest_validation_json(items, args.db_url, dry_run=args.dry_run)
    except ValueError as exc:
        logger.error("Ingest failed: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return 1

    mode = "DRY-RUN" if args.dry_run else "COMMITTED"
    print(
        f"{mode}: {summary['rows_upserted']} rows upserted, "
        f"{summary['varieties_affected']} varieties affected, "
        f"{summary['attr_rows_written']} attr rows written, "
        f"{summary['enrich_fields']} enrichment fields updated."
    )
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
