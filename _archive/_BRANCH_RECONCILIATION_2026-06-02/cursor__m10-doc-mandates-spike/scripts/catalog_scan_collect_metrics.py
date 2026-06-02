#!/usr/bin/env python3
"""Collect catalog/pipeline metrics for catalog scan before/after (plan Phase 0 / 5).

Usage:
  DATABASE_URL=... python3 scripts/catalog_scan_collect_metrics.py [--output path.json]
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text


def collect(engine) -> dict:
    with engine.connect() as c:
        by_status = {
            str(r[0]): int(r[1])
            for r in c.execute(
                text(
                    """
                    SELECT extraction_status::text, COUNT(*)::int
                    FROM raw_extracted_items
                    GROUP BY extraction_status
                    ORDER BY 1
                    """
                )
            ).all()
        }
        unres_rows = int(
            c.execute(
                text(
                    """
                    SELECT COUNT(*) FROM raw_extracted_items
                    WHERE extraction_status = 'unresolvable'
                      AND COALESCE(is_quarantined, false) IS NOT TRUE
                    """
                )
            ).scalar_one()
        )
        distinct_unres = int(
            c.execute(
                text(
                    """
                    SELECT COUNT(DISTINCT rei.raw_product_name) FROM raw_extracted_items rei
                    WHERE rei.extraction_status = 'unresolvable'
                      AND COALESCE(rei.is_quarantined, false) IS NOT TRUE
                      AND rei.raw_product_name IS NOT NULL
                      AND btrim(rei.raw_product_name) <> ''
                    """
                )
            ).scalar_one()
        )
        per_src_unres = [
            {"source_id": int(r[0]), "source_code": r[1], "unresolvable_count": int(r[2])}
            for r in c.execute(
                text(
                    """
                    SELECT s.id, s.code,
                           COUNT(rei.id)::int AS cnt
                    FROM sources s
                    JOIN source_fetch_runs sfr ON sfr.source_id = s.id
                    JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
                    WHERE rei.extraction_status = 'unresolvable'
                      AND COALESCE(rei.is_quarantined, false) IS NOT TRUE
                    GROUP BY s.id, s.code
                    HAVING COUNT(rei.id) > 0
                    ORDER BY cnt DESC
                    """
                )
            ).all()
        ]
        alembic = c.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    return {
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "alembic_version": alembic,
        "raw_extracted_items_by_status": by_status,
        "unresolvable_rows_non_quarantined": unres_rows,
        "distinct_unresolvable_raw_product_names": distinct_unres,
        "unresolvable_by_source": per_src_unres,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", "-o", type=Path, default=None)
    args = ap.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL required")
    data = collect(create_engine(url))
    out = args.output
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {out}")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
