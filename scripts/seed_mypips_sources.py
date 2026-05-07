#!/usr/bin/env python3
"""
Seed the 4 priority MyPIPS sources into the sources table (WP002, AC-06).

This is a DATA seeder, not a schema migration. Run once after migration 034
(display_bucket column) has been applied.

Usage:
    python3 scripts/seed_mypips_sources.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import select  # noqa: E402

from organic_market_agent.db.session import get_session  # noqa: E402
from organic_market_agent.models.sources import Source  # noqa: E402

# 4 priority sources — Phase 2 onboarding (Team 100 plan 2026-04-04)
MYPIPS_SOURCES = [
    {
        "code": "SRC_MP01",
        "name": "משתלת הראה",
        "base_url": "https://www.mypips.co.il/shop/mashtelatharoe",
        "source_group": "direct_price",
        "market_scope": "community",
        "sales_channel": "community_direct",
        "status": "candidate",
        "priority": 3,
        "source_tier": "price_grid",
        "display_bucket": "grower",
        "is_active": True,
        "notes": "MyPIPS storefront. Handle: mashtelatharoe. WP002 onboarding.",
    },
    {
        "code": "SRC_MP02",
        "name": "הננתיות",
        "base_url": "https://www.mypips.co.il/shop/anatiyot",
        "source_group": "direct_price",
        "market_scope": "community",
        "sales_channel": "community_direct",
        "status": "candidate",
        "priority": 3,
        "source_tier": "price_grid",
        "display_bucket": "store",
        "is_active": True,
        "notes": "MyPIPS storefront. Handle: anatiyot. AC-07: includeOrganic=true. WP002 onboarding.",
    },
    {
        "code": "SRC_MP03",
        "name": "השחקן שהפך לירקן",
        "base_url": "https://www.mypips.co.il/shop/fruit4soul",
        "source_group": "direct_price",
        "market_scope": "community",
        "sales_channel": "community_direct",
        "status": "candidate",
        "priority": 3,
        "source_tier": "price_grid",
        "display_bucket": "store",
        "is_active": True,
        "notes": "MyPIPS storefront. Handle: fruit4soul. WP002 onboarding.",
    },
    {
        "code": "SRC_MP04",
        "name": "משק רתם פיין",
        "base_url": "https://www.mypips.co.il/shop/finerotem",
        "source_group": "direct_price",
        "market_scope": "community",
        "sales_channel": "community_direct",
        "status": "candidate",
        "priority": 3,
        "source_tier": "price_grid",
        "display_bucket": "grower",
        "is_active": True,
        "notes": "MyPIPS storefront. Handle: finerotem. WP002 onboarding.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed 4 MyPIPS sources into sources table.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be inserted; do not write.")
    args = parser.parse_args()

    with get_session() as session:
        inserted = 0
        skipped = 0
        for src_data in MYPIPS_SOURCES:
            code = src_data["code"]
            existing = session.execute(
                select(Source).where(Source.code == code)
            ).scalar_one_or_none()

            if existing is not None:
                print(f"SKIP  {code} ({src_data['name']}) — already exists (id={existing.id})")
                skipped += 1
                continue

            if args.dry_run:
                print(f"DRY   {code} ({src_data['name']}) — would insert")
                inserted += 1
                continue

            src = Source(**src_data)
            session.add(src)
            session.flush()
            print(f"INSERT {code} ({src_data['name']}) — id={src.id}")
            inserted += 1

        if not args.dry_run:
            session.commit()
            print(f"\nDone: inserted={inserted}, skipped={skipped}")
        else:
            print(f"\nDry run: would insert={inserted}, already exists={skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
