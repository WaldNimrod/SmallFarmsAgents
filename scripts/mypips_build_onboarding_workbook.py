#!/usr/bin/env python3
"""
Build ``data/mypips_source_onboarding_workbook.csv`` from the verified suspected-links CSV.

Uses ``storefront_likely_active`` rows only; dedupes to one row per mypips.app store slug.

Usage (repo root):
    python3 scripts/mypips_build_onboarding_workbook.py \\
        --in-csv _COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv \\
        --out-csv data/mypips_source_onboarding_workbook.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from organic_market_agent.discovery.mypips_onboarding import (  # noqa: E402
    build_workbook_rows,
    workbook_fieldnames,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Build MyPIPS source onboarding workbook CSV.")
    p.add_argument(
        "--in-csv",
        type=Path,
        default=_ROOT / "_COMMUNICATION" / "TEAM_80" / "mypips_suspected_links_60.csv",
        help="Verified suspected-links CSV (Team 80 + Team 10)",
    )
    p.add_argument(
        "--out-csv",
        type=Path,
        default=_ROOT / "data" / "mypips_source_onboarding_workbook.csv",
        help="Output workbook path",
    )
    args = p.parse_args()
    if not args.in_csv.is_file():
        print(f"Missing input: {args.in_csv}", file=sys.stderr)
        return 1
    rows = build_workbook_rows(args.in_csv)
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = workbook_fieldnames()
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
