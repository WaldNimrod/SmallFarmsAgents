"""Tests for migration 049 — crop_planting_calendar (WP-C1 AC-C1-01)."""
import importlib.util
import pytest

pytestmark = pytest.mark.crop_book

MIGRATION_PATH = "organic_market_agent/db/versions/049_crop_planting_calendar.py"


def _load_migration(path: str):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="function")
def migrated_engine():
    from sqlalchemy import create_engine, text
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    m049 = _load_migration(MIGRATION_PATH)
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE crops (id INTEGER PRIMARY KEY AUTOINCREMENT, name_he TEXT NOT NULL)"
        ))
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m049.upgrade.__globals__["op"] = ops
        m049.upgrade()
    return engine, m049


class TestMigration049:
    def test_table_exists(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = migrated_engine
        assert "crop_planting_calendar" in sa_inspect(engine).get_table_names()

    def test_unique_constraint_enforced(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('חסה')"))
            crop_id = conn.execute(text("SELECT id FROM crops")).scalar()
            conn.execute(text(
                "INSERT INTO crop_planting_calendar "
                "(crop_id, source, trust_tier, activity_type) "
                "VALUES (:cid, 'NI:groworganic', 'NI', 'seed')"
            ), {"cid": crop_id})
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_planting_calendar "
                    "(crop_id, source, trust_tier, activity_type) "
                    "VALUES (:cid, 'NI:groworganic', 'NI', 'seed')"
                ), {"cid": crop_id})
                conn.commit()

    def test_activity_type_check(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.begin() as conn:
            crop_id = conn.execute(
                text("INSERT INTO crops (name_he) VALUES ('גזר') RETURNING id")
            ).scalar() if False else 1
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('גזר')"))
            crop_id = conn.execute(text("SELECT id FROM crops")).scalar()
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_planting_calendar "
                    "(crop_id, source, trust_tier, activity_type) "
                    "VALUES (:cid, 'NI:bustan', 'NI', 'invalid')"
                ), {"cid": crop_id})
                conn.commit()

    def test_season_check(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('פלפל')"))
            crop_id = conn.execute(text("SELECT id FROM crops")).scalar()
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_planting_calendar "
                    "(crop_id, source, trust_tier, activity_type, season) "
                    "VALUES (:cid, 'NI:bustan', 'NI', 'seed', 'monsoon')"
                ), {"cid": crop_id})
                conn.commit()

    def test_insert_select_round_trip(self, migrated_engine):
        from sqlalchemy import text

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('ברוקולי')"))
            crop_id = conn.execute(text("SELECT id FROM crops")).scalar()
            conn.execute(text(
                "INSERT INTO crop_planting_calendar "
                "(crop_id, source, trust_tier, activity_type, season, month_mar, month_apr) "
                "VALUES (:cid, 'NI:groworganic', 'NI', 'transplant', 'spring', 1, 1)"
            ), {"cid": crop_id})
            row = conn.execute(text(
                "SELECT activity_type, month_mar, month_apr FROM crop_planting_calendar "
                "WHERE crop_id = :cid"
            ), {"cid": crop_id}).one()
        assert row[0] == "transplant"
        assert row[1] is True or row[1] == 1
        assert row[2] is True or row[2] == 1
