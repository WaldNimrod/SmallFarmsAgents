#!/usr/bin/env python3
"""
Copy every on-disk file referenced by raw_assets.storage_path into a single archive tree.

Layout: <dest>/{SOURCE_CODE}/{YYYY-MM-DD}/<filename>

DATABASE_URL must be set. Skips missing files (logs warning).
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from sqlalchemy import create_engine, text


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: DATABASE_URL=... python scripts/mirror_raw_assets_to_folder.py <dest_dir>",
            file=sys.stderr,
        )
        return 2
    dest_root = Path(sys.argv[1]).resolve()
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 1

    engine = create_engine(url)
    with engine.connect() as conn:
        paths = [r[0] for r in conn.execute(text("SELECT DISTINCT storage_path FROM raw_assets ORDER BY storage_path"))]

    dest_root.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = 0
    for storage in paths:
        src = Path(storage)
        if not src.is_file():
            print(f"MISSING: {storage}", file=sys.stderr)
            missing += 1
            continue
        # Paths are .../{SOURCE_CODE}/{YYYY-MM-DD}/{filename}
        rel = Path(src.parent.parent.name) / src.parent.name / src.name
        out = dest_root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out)
        copied += 1

    print(f"Copied {copied} files to {dest_root}; missing {missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
