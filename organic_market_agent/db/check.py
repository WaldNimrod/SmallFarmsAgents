"""
DB Health Check CLI.
Usage: python -m organic_market_agent.db.check
Exit code: 0 = PASS, 1 = FAIL
"""
import sys

from sqlalchemy import inspect, text

from organic_market_agent.db.session import engine

REQUIRED_TABLES = [
    "measurement_units",
    "unit_conversions",
    "products",
    "product_aliases",
    "product_variants",
    "product_merges",
    "sources",
    "source_fetch_profiles",
    "normalizer_profiles",
    "normalizer_rules",
    "ingestion_runs",
    "source_fetch_runs",
    "raw_assets",
    "raw_extracted_items",
    "normalized_observations",
    "observation_flags",
    "daily_aggregates",
    "weekly_snapshots",
    "publish_runs",
    "publish_artifacts",
    "users",
    "audit_log",
    "log_entries",
]

REQUIRED_COUNTS = {
    "measurement_units": 11,
    "products": 29,
    "sources": 20,
}


def check() -> bool:
    all_pass = True
    insp = inspect(engine)
    existing = set(insp.get_table_names())

    print("OrganicMarketAgent — DB Health Check")
    print("=" * 50)

    for table in REQUIRED_TABLES:
        if table in existing:
            print(f"  OK  {table}")
        else:
            print(f"  MISSING  {table}")
            all_pass = False

    with engine.connect() as conn:
        for table, min_count in REQUIRED_COUNTS.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = "OK" if count >= min_count else "FAIL"
            print(f"  {status}  {table}: {count} rows (expected >= {min_count})")
            if count < min_count:
                all_pass = False

    print("=" * 50)
    print(f"RESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    sys.exit(0 if check() else 1)
