"""
DB health tests — Gate G1 acceptance criteria.
Requires a running PostgreSQL DB with applied Alembic migrations.
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from organic_market_agent.db.check import REQUIRED_COUNTS, REQUIRED_TABLES, check
from organic_market_agent.db.session import engine

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except OperationalError:
    pytest.skip(
        "PostgreSQL not reachable — G1/G-V1.1 certified runs require a live database",
        allow_module_level=True,
    )


def test_all_required_tables_exist():
    insp = inspect(engine)
    existing = set(insp.get_table_names())
    missing = [t for t in REQUIRED_TABLES if t not in existing]
    assert not missing, f"Missing tables: {missing}"


def test_seed_data_counts():
    with engine.connect() as conn:
        for table, min_count in REQUIRED_COUNTS.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            assert count >= min_count, f"{table}: expected >= {min_count} rows, got {count}"


def test_products_have_aliases():
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COUNT(DISTINCT product_id) FROM product_aliases "
                "WHERE is_active = true"
            )
        )
        count = result.scalar()
        assert count >= 10, f"Expected aliases for >= 10 products, got {count}"


def test_all_products_have_valid_unit():
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT COUNT(*) FROM products p
            WHERE p.is_active = true
              AND NOT EXISTS (
                SELECT 1 FROM measurement_units mu
                WHERE mu.id = p.default_measurement_unit_id
              )
        """
            )
        )
        count = result.scalar()
        assert count == 0, f"{count} products have a missing or invalid default unit"


def test_no_float_price_columns():
    """Verify no price columns are stored as float (must be NUMERIC)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('normalized_observations', 'daily_aggregates')
              AND column_name LIKE '%price%'
              AND data_type = 'double precision'
        """
            )
        )
        floats = result.fetchall()
        assert not floats, f"Found float price columns: {floats}"


def test_all_timestamp_columns_are_timestamptz():
    """All *_at columns must be TIMESTAMPTZ (timezone-aware)."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND column_name LIKE '%_at'
              AND data_type = 'timestamp without time zone'
        """
            )
        )
        naive = result.fetchall()
        assert not naive, f"Found naive (non-timezone) timestamp columns: {naive}"


def test_check_cli_passes():
    assert check() is True
