"""Tests for migrations 051–052 (WP-C4 AC-C4-01)."""
import importlib.util

import pytest

pytestmark = pytest.mark.crop_book


def _load_migration(path: str):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="function")
def engine_051():
    from sqlalchemy import create_engine, text
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    m051 = _load_migration("organic_market_agent/db/versions/051_crop_companion_matrix.py")
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE crops (id INTEGER PRIMARY KEY AUTOINCREMENT, name_he TEXT)"
        ))
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m051.upgrade.__globals__["op"] = ops
        m051.upgrade()
    return engine, m051


@pytest.fixture(scope="function")
def engine_052(engine_051):
    from sqlalchemy import create_engine, text
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    engine, _ = engine_051
    m052 = _load_migration("organic_market_agent/db/versions/052_crop_postharvest_storage.py")
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m052.upgrade.__globals__["op"] = ops
        m052.upgrade()
    return engine, m052


class TestMigration051:
    def test_companion_table_exists(self, engine_051):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = engine_051
        assert "crop_companion_matrix" in sa_inspect(engine).get_table_names()

    def test_no_self_pair_constraint(self, engine_051):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = engine_051
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('a')"))
            cid = conn.execute(text("SELECT id FROM crops")).scalar()
        with engine.connect() as conn:
            with pytest.raises(IntegrityError):
                conn.execute(text(
                    "INSERT INTO crop_companion_matrix "
                    "(crop_a_id, crop_b_id, compatibility, source, trust_tier) "
                    "VALUES (:id, :id, 'beneficial', 'PR:uf_ifas_companion', 'PR')"
                ), {"id": cid})
                conn.commit()


class TestMigration052:
    def test_postharvest_table_exists(self, engine_052):
        from sqlalchemy import inspect as sa_inspect
        engine, _ = engine_052
        assert "crop_postharvest_storage" in sa_inspect(engine).get_table_names()

    def test_downgrade_052(self, engine_052):
        from sqlalchemy import inspect as sa_inspect

        engine, m052 = engine_052
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m052.downgrade.__globals__["op"] = ops
            m052.downgrade()
        assert "crop_postharvest_storage" not in sa_inspect(engine).get_table_names()
