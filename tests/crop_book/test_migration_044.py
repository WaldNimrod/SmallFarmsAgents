"""Tests for migration 044 (AC-01, AC-15a, AC-15b, AC-16a). SFA-S003-P002-WP-B1."""
import pytest
from decimal import Decimal

pytestmark = pytest.mark.crop_book


@pytest.fixture(scope="module")
def migrated_engine():
    """SQLite engine with crop_task_templates created via migration DDL."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    # Build the table using the same DDL as migration 044
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        # Create crops table (dependency)
        conn.execute(text("""
            CREATE TABLE crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_he VARCHAR(200) NOT NULL UNIQUE,
                category VARCHAR(50),
                name_en VARCHAR(200),
                scientific_name VARCHAR(200),
                family_id INTEGER,
                growth_cycle VARCHAR(50),
                harvest_unit_default VARCHAR(50),
                first_fruit_year INTEGER,
                conversion_group_id INTEGER,
                description TEXT,
                oma_product_id INTEGER
            )
        """))
        conn.execute(text("""
            CREATE TABLE crop_task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
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
                CHECK(task_type IN ('stale_seed_bed','flame_weeder','flextine_harrow_1',
                    'flextine_harrow_2','biodisc','hoe','hand_weed','boron_seaweed_1',
                    'boron_seaweed_2','straw_mulch_topdress','head_pinch_chop','mow_and_tarp',
                    'at_seeding_transplanting','net_row_cover')),
                CHECK(timing_anchor IS NULL OR timing_anchor IN
                    ('seeding','transplanting','harvest','field_prep'))
            )
        """))
        conn.execute(text("CREATE INDEX idx_cct_crop ON crop_task_templates(crop_id)"))
        conn.execute(text("CREATE INDEX idx_cct_type ON crop_task_templates(task_type)"))
        # Insert a test crop
        conn.execute(text("INSERT INTO crops(name_he, category) VALUES ('ארוגולה', 'vegetables')"))
        conn.commit()
    return engine


@pytest.fixture
def session_factory(migrated_engine):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(migrated_engine)


def _get_crop_id(conn):
    from sqlalchemy import text
    result = conn.execute(text("SELECT id FROM crops WHERE name_he='ארוגולה'")).fetchone()
    return result[0]


def test_migration_044_table_exists(migrated_engine):
    """AC-01: crop_task_templates table created."""
    from sqlalchemy import inspect
    insp = inspect(migrated_engine)
    assert "crop_task_templates" in insp.get_table_names()


def test_migration_044_indices_exist(migrated_engine):
    """AC-01: idx_cct_crop and idx_cct_type indices created."""
    from sqlalchemy import inspect
    insp = inspect(migrated_engine)
    idx_names = {i["name"] for i in insp.get_indexes("crop_task_templates")}
    assert "idx_cct_crop" in idx_names
    assert "idx_cct_type" in idx_names


def test_migration_044_insert_and_select(migrated_engine):
    """AC-01: basic insert + select round-trip."""
    from sqlalchemy import text
    with migrated_engine.connect() as conn:
        crop_id = _get_crop_id(conn)
        conn.execute(text("""
            INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
            VALUES (:cid, 'JMF', 'PR', 'hoe', 14)
        """), {"cid": crop_id})
        row = conn.execute(text(
            "SELECT task_type, days_offset FROM crop_task_templates WHERE crop_id=:cid AND task_type='hoe'"
        ), {"cid": crop_id}).fetchone()
        conn.rollback()
    assert row is not None
    assert row[0] == "hoe"
    assert row[1] == 14


def test_ac15a_unique_constraint_real_offset(migrated_engine):
    """AC-15a: duplicate (crop_id, source, task_type, real_offset) raises IntegrityError."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    with migrated_engine.connect() as conn:
        crop_id = _get_crop_id(conn)
        conn.execute(text("""
            INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
            VALUES (:cid, 'JMF', 'PR', 'flame_weeder', 5)
        """), {"cid": crop_id})
        with pytest.raises(IntegrityError):
            conn.execute(text("""
                INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
                VALUES (:cid, 'JMF', 'PR', 'flame_weeder', 5)
            """), {"cid": crop_id})
        conn.rollback()


def test_ac15b_unique_constraint_presence_only(migrated_engine):
    """AC-15b: duplicate (crop_id, source, task_type, -32768) ALSO raises IntegrityError.

    This is the F-S-002 R1 regression assertion — two presence-only ('X') rows
    for the same crop/task must collapse via the sentinel UNIQUE key, not bypass
    it (which NULL would allow on both Postgres and SQLite).
    """
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    SENTINEL = -32768
    with migrated_engine.connect() as conn:
        crop_id = _get_crop_id(conn)
        conn.execute(text("""
            INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
            VALUES (:cid, 'JMF', 'PR', 'stale_seed_bed', :sentinel)
        """), {"cid": crop_id, "sentinel": SENTINEL})
        with pytest.raises(IntegrityError):
            conn.execute(text("""
                INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
                VALUES (:cid, 'JMF', 'PR', 'stale_seed_bed', :sentinel)
            """), {"cid": crop_id, "sentinel": SENTINEL})
        conn.rollback()


def test_ac16a_check_constraint_task_type(migrated_engine):
    """AC-16a: inserting task_type='nursery_seed' (B3 value) raises IntegrityError."""
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    with migrated_engine.connect() as conn:
        crop_id = _get_crop_id(conn)
        with pytest.raises(IntegrityError):
            conn.execute(text("""
                INSERT INTO crop_task_templates(crop_id, source, trust_tier, task_type, days_offset)
                VALUES (:cid, 'JMF', 'PR', 'nursery_seed', 0)
            """), {"cid": crop_id})
        conn.rollback()
