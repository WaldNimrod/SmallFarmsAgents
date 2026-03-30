#!/usr/bin/env python3
"""Write SNAPSHOT_MANIFEST.json for a raw-files baseline (DATABASE_URL required)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "Usage: DATABASE_URL=... python scripts/generate_snapshot_manifest.py "
            "<RAW_FILES_ROOT_capture_dir> <manifest_output.json>",
            file=sys.stderr,
        )
        return 2
    capture_root = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.connect() as conn:
        runs = conn.execute(
            text(
                """
                SELECT id, run_type, status, sources_total, sources_succeeded,
                       sources_failed, community_sources_succeeded, started_at, finished_at
                FROM ingestion_runs
                ORDER BY id DESC
                LIMIT 10
                """
            )
        ).mappings().all()
        counts = dict(
            conn.execute(
                text(
                    """
                    SELECT
                      (SELECT COUNT(*) FROM raw_assets) AS raw_assets,
                      (SELECT COUNT(*) FROM raw_extracted_items) AS raw_extracted_items,
                      (SELECT COUNT(*) FROM source_fetch_runs) AS source_fetch_runs,
                      (SELECT COUNT(*) FROM log_entries) AS log_entries
                    """
                )
            ).one()._mapping
        )

    def scan_tree(root: Path) -> dict:
        files: list[dict[str, str | int]] = []
        if not root.exists():
            return {"root": str(root), "file_count": 0, "files": [], "truncated": False}
        for p in sorted(root.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(root))
                try:
                    sz = p.stat().st_size
                except OSError:
                    sz = -1
                files.append({"path": rel, "bytes": sz})
        return {
            "root": str(root),
            "file_count": len(files),
            "files": files[:500],
            "truncated": len(files) > 500,
        }

    capture_scan = scan_tree(capture_root)
    mirror_root = capture_root.parent / "full_mirror"
    mirror_scan = scan_tree(mirror_root)

    payload = {
        "snapshot_label": "first_full_scan_2026-03-30",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_files_root_capture": str(capture_root),
        "full_mirror_root": str(mirror_root),
        "ingestion_runs_last_10": [dict(r) for r in runs],
        "table_counts": counts,
        "capture": capture_scan,
        "full_mirror": mirror_scan,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
