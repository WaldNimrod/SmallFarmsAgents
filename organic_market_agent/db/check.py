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
    "scheduler_config",
    "pipeline_alerts",
]

REQUIRED_COUNTS = {
    "measurement_units": 11,
    "products": 67,
    "sources": 21,
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

        result = conn.execute(
            text(
                "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = true"
            )
        )
        admin_count = result.scalar()
        admin_ok = admin_count >= 1
        print(
            f"  {'OK' if admin_ok else 'FAIL'}  "
            f"users (active admin): {admin_count} rows (expected >= 1)"
        )
        if not admin_ok:
            all_pass = False

        result = conn.execute(text("SELECT COUNT(*) FROM scheduler_config"))
        sc_count = result.scalar()
        sc_ok = sc_count == 1
        print(
            f"  {'OK' if sc_ok else 'FAIL'}  "
            f"scheduler_config: {sc_count} rows (expected exactly 1)"
        )
        if not sc_ok:
            all_pass = False

    audit_indexes = insp.get_indexes("audit_log")
    entity_cols = {"entity_type", "entity_id"}
    created_cols = {"created_at"}
    has_entity_idx = any(set(idx.get("column_names") or []) == entity_cols for idx in audit_indexes)
    has_created_idx = any(set(idx.get("column_names") or []) == created_cols for idx in audit_indexes)
    print(
        f"  {'OK' if has_entity_idx else 'FAIL'}  "
        "audit_log index on (entity_type, entity_id)"
    )
    print(f"  {'OK' if has_created_idx else 'FAIL'}  audit_log index on (created_at)")
    if not has_entity_idx or not has_created_idx:
        all_pass = False

    obs_idx = insp.get_indexes("observation_flags")
    has_product_idx = any(
        (idx.get("column_names") or []) == ["product_id"] for idx in obs_idx
    )
    print(
        f"  {'OK' if has_product_idx else 'FAIL'}  "
        "observation_flags index on (product_id)"
    )
    if not has_product_idx:
        all_pass = False

    print("=" * 50)
    print(f"RESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    sys.exit(0 if check() else 1)
