"""Tests for migration 046 — crop_harvest_stats + task_type CHECK extension.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-01a, AC-01b, AC-11.
"""
import importlib.util
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book

MIGRATION_PATH = "organic_market_agent/db/versions/046_tend_overlay.py"
MIGRATION_044_PATH = "organic_market_agent/db/versions/044_crop_task_templates.py"


def _load_migration(path: str):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def migrated_engine():
    """SQLite engine with pre-046 tables then upgraded via migration 046."""
    from sqlalchemy import create_engine, text
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    m046 = _load_migration(MIGRATION_PATH)

    engine = create_engine("sqlite:///:memory:")

    # Create prerequisites: crops + crop_task_templates (B1 baseline — 14 values)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_he TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE crop_task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL REFERENCES crops(id),
                source VARCHAR(50) NOT NULL,
                trust_tier VARCHAR(20) NOT NULL,
                task_type VARCHAR(40) NOT NULL,
                timing_anchor VARCHAR(20),
                days_offset INTEGER NOT NULL DEFAULT -32768,
                method TEXT,
                input_material TEXT,
                notes TEXT,
                display_order INTEGER NOT NULL DEFAULT 100,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(crop_id, source, task_type, days_offset),
                CHECK(task_type IN (
                    'stale_seed_bed','flame_weeder','flextine_harrow_1','flextine_harrow_2',
                    'biodisc','hoe','hand_weed','boron_seaweed_1','boron_seaweed_2',
                    'straw_mulch_topdress','head_pinch_chop','mow_and_tarp',
                    'at_seeding_transplanting','net_row_cover'
                )),
                CHECK(timing_anchor IS NULL OR timing_anchor IN
                    ('seeding','transplanting','harvest','field_prep'))
            )
        """))
        conn.execute(text("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL
            )
        """))
        # Insert a test crop
        conn.execute(text("INSERT INTO crops(name_he) VALUES ('עגבנייה')"))
        conn.execute(text("INSERT INTO alembic_version(version_num) VALUES ('045')"))

    # Run migration 046 upgrade
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m046.upgrade.__globals__["op"] = ops
        m046.upgrade()

    return engine, m046


class TestMigration046UpgradeAC01a:
    """AC-01a: crop_harvest_stats created with correct DDL."""

    def test_table_exists(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = migrated_engine
        assert "crop_harvest_stats" in sa_inspect(engine).get_table_names()

    def test_columns_present(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = migrated_engine
        cols = {c["name"] for c in sa_inspect(engine).get_columns("crop_harvest_stats")}
        expected = {
            "id", "crop_id", "season", "year", "source",
            "cycles_count", "first_harvest_week", "peak_harvest_week", "last_harvest_week",
            "yield_total", "yield_unit",
            "yield_per_bed_min", "yield_per_bed_max", "yield_per_bed_median",
            "created_at",
        }
        assert expected.issubset(cols), f"Missing columns: {expected - cols}"

    def test_season_check_enforced(self, migrated_engine):
        """Season CHECK constraint rejects invalid values."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime

        engine, _ = migrated_engine
        with engine.begin() as conn:
            crop_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he='עגבנייה'")
            ).fetchone()[0]

        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_harvest_stats "
                    "(crop_id, season, year, source, created_at) "
                    "VALUES (:cid, 'monsoon', 2022, 'Test', '2022-01-01')"
                ), {"cid": crop_id})

    def test_valid_season_accepted(self, migrated_engine):
        """Valid season values are accepted."""
        from sqlalchemy import text

        engine, _ = migrated_engine
        with engine.begin() as conn:
            crop_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he='עגבנייה'")
            ).fetchone()[0]
            for season in ("spring", "summer", "fall", "winter"):
                conn.execute(text(
                    "INSERT INTO crop_harvest_stats "
                    "(crop_id, season, year, source, created_at) "
                    "VALUES (:cid, :season, 2022, 'Test', '2022-01-01')"
                ), {"cid": crop_id, "season": season})
        # No exception → PASS


class TestMigration046CheckConstraintAC01b:
    """AC-01b: task_type CHECK extended to 20 values; B1 baseline still accepted."""

    def test_b1_baseline_still_accepted(self, migrated_engine):
        """AC-11: B1 baseline task_types still accepted after migration 046."""
        from sqlalchemy import text

        engine, _ = migrated_engine
        b1_values = [
            "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
            "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
            "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
            "at_seeding_transplanting", "net_row_cover",
        ]
        with engine.begin() as conn:
            crop_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he='עגבנייה'")
            ).fetchone()[0]
            for i, tt in enumerate(b1_values):
                conn.execute(text(
                    "INSERT INTO crop_task_templates "
                    "(crop_id, source, trust_tier, task_type, created_at) "
                    "VALUES (:cid, 'Test', 'OP', :tt, '2022-01-01')"
                ), {"cid": crop_id, "tt": tt})
        # No IntegrityError → PASS

    def test_b3_new_values_accepted(self, migrated_engine):
        """After migration 046, new B3 task_type values are accepted."""
        from sqlalchemy import text

        engine, _ = migrated_engine
        b3_values = ["nursery_seed", "pest_spray", "potting_up", "thinning",
                     "trellis", "fertilize"]
        with engine.begin() as conn:
            crop_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he='עגבנייה'")
            ).fetchone()[0]
            for tt in b3_values:
                conn.execute(text(
                    "INSERT INTO crop_task_templates "
                    "(crop_id, source, trust_tier, task_type, created_at) "
                    "VALUES (:cid, 'Tend_2022', 'OP', :tt, '2022-01-01')"
                ), {"cid": crop_id, "tt": tt})
        # No IntegrityError → PASS

    def test_nonsense_value_rejected(self, migrated_engine):
        """Inserting an unknown task_type raises IntegrityError."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.connect() as conn:
            crop_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he='עגבנייה'")
            ).fetchone()[0]
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_task_templates "
                    "(crop_id, source, trust_tier, task_type, created_at) "
                    "VALUES (:cid, 'Test', 'OP', 'nonsense_value', '2022-01-01')"
                ), {"cid": crop_id})
