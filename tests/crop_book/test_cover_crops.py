"""Tests for migration 050 — crop_cover_crops (WP-C1 AC-C1-02)."""
import importlib.util
import pytest

pytestmark = pytest.mark.crop_book

MIGRATION_PATH = "organic_market_agent/db/versions/050_crop_cover_crops.py"


def _load_migration(path: str):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="function")
def migrated_engine():
    from sqlalchemy import create_engine
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    m050 = _load_migration(MIGRATION_PATH)
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m050.upgrade.__globals__["op"] = ops
        m050.upgrade()
    return engine, m050


class TestMigration050:
    def test_table_exists(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = migrated_engine
        assert "crop_cover_crops" in sa_inspect(engine).get_table_names()

    def test_category_check(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_cover_crops "
                    "(name_en, category, source, trust_tier) "
                    "VALUES ('Bad', 'fungus', 'PR:jmf_cover_crops', 'PR')"
                ))
                conn.commit()

    def test_unique_name_source(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO crop_cover_crops "
                "(name_en, category, source, trust_tier) "
                "VALUES ('Clover', 'legume', 'PR:jmf_cover_crops', 'PR')"
            ))
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_cover_crops "
                    "(name_en, category, source, trust_tier) "
                    "VALUES ('Clover', 'legume', 'PR:jmf_cover_crops', 'PR')"
                ))
                conn.commit()

    def test_insert_select_round_trip(self, migrated_engine):
        from sqlalchemy import text

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO crop_cover_crops "
                "(name_en, category, source, trust_tier, total_days_garden, "
                "germination_temp_c_min, hardiness_zone, survives_winter) "
                "VALUES ('Crimson Clover', 'legume', 'PR:jmf_cover_crops', 'PR', "
                "70, 7.0, 7, 1)"
            ))
            row = conn.execute(text(
                "SELECT name_en, category, germination_temp_c_min FROM crop_cover_crops"
            )).one()
        assert row[0] == "Crimson Clover"
        assert row[1] == "legume"
        assert float(row[2]) == 7.0
