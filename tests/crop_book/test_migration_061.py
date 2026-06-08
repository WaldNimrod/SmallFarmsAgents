"""Tests for migration 061 (crop_content + crop_content_source).

SFA-S003-P004-WP-CB-CONTENT.
"""
import importlib.util
import pytest

pytestmark = pytest.mark.crop_book

MIGRATION_PATH = "organic_market_agent/db/versions/061_crop_content.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("m061", MIGRATION_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fresh_engine_with_crops():
    from sqlalchemy import create_engine, text

    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE crops (id INTEGER PRIMARY KEY AUTOINCREMENT, name_he TEXT NOT NULL)"
        ))
    return engine


@pytest.fixture(scope="module")
def migrated_engine():
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    m061 = _load_migration()
    engine = _fresh_engine_with_crops()
    with engine.begin() as conn:
        ops = Operations(MigrationContext.configure(conn))
        m061.upgrade.__globals__["op"] = ops
        m061.upgrade()
    return engine, m061


class TestMigration061:
    def test_revision_chain(self):
        m = _load_migration()
        assert m.revision == "061"
        assert m.down_revision == "060"

    def test_tables_created(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect

        engine, _ = migrated_engine
        tables = sa_inspect(engine).get_table_names()
        assert "crop_content" in tables
        assert "crop_content_source" in tables

    def test_columns_present(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect

        engine, _ = migrated_engine
        insp = sa_inspect(engine)
        cc = {c["name"] for c in insp.get_columns("crop_content")}
        ccs = {c["name"] for c in insp.get_columns("crop_content_source")}
        assert {
            "id", "crop_id", "content_type", "text_md", "winning_source_class",
            "confidence_score", "source_count", "computed_at",
        }.issubset(cc)
        assert {
            "id", "content_id", "source_label", "source_class", "raw_text_md",
            "source_url", "display_order", "created_at",
        }.issubset(ccs)

    def test_unique_crop_content_type_enforced(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('חסה')"))
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO crop_content (crop_id, content_type, text_md, source_count, computed_at) "
                "VALUES (1, 'story', 'a', 0, '2026-06-09')"
            ))
        with pytest.raises(IntegrityError):
            with engine.begin() as conn:
                conn.execute(text(
                    "INSERT INTO crop_content (crop_id, content_type, text_md, source_count, computed_at) "
                    "VALUES (1, 'story', 'b', 0, '2026-06-09')"
                ))

    def test_content_type_check_constraint(self, migrated_engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        engine, _ = migrated_engine
        with pytest.raises(IntegrityError):
            with engine.begin() as conn:
                conn.execute(text(
                    "INSERT INTO crop_content (crop_id, content_type, text_md, source_count, computed_at) "
                    "VALUES (1, 'not_a_type', 'x', 0, '2026-06-09')"
                ))

    def test_downgrade_drops_tables(self):
        from sqlalchemy import inspect as sa_inspect
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m061 = _load_migration()
        engine = _fresh_engine_with_crops()
        with engine.begin() as conn:
            ops = Operations(MigrationContext.configure(conn))
            m061.upgrade.__globals__["op"] = ops
            m061.upgrade()
        assert "crop_content" in sa_inspect(engine).get_table_names()
        with engine.begin() as conn:
            ops = Operations(MigrationContext.configure(conn))
            m061.downgrade.__globals__["op"] = ops
            m061.downgrade()
        names = sa_inspect(engine).get_table_names()
        assert "crop_content" not in names
        assert "crop_content_source" not in names
