"""Tests for migration 045 (AC-01, AC-04a).

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §3 / §9.
"""
import importlib.util
import pytest

pytestmark = pytest.mark.crop_book

MIGRATION_PATH = "organic_market_agent/db/versions/045_crop_knowledge_notes.py"


@pytest.fixture(scope="module")
def migrated_engine():
    """SQLite engine upgraded through migration 045 DDL."""
    from sqlalchemy import create_engine, text
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    spec = importlib.util.spec_from_file_location("m045", MIGRATION_PATH)
    m045 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m045)

    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE crops ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "name_he TEXT NOT NULL"
            ")"
        ))

    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m045.upgrade.__globals__["op"] = ops
        m045.upgrade()

    return engine, m045


class TestMigration045:
    """AC-01: alembic upgrade head succeeds; AC-04a: body_text CHECK enforced."""

    def test_ac01_upgrade_creates_table(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect

        engine, _ = migrated_engine
        inspector = sa_inspect(engine)
        tables = inspector.get_table_names()
        assert "crop_knowledge_notes" in tables

    def test_ac01_columns_present(self, migrated_engine):
        from sqlalchemy import inspect as sa_inspect

        engine, _ = migrated_engine
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("crop_knowledge_notes")}
        expected = {
            "id", "crop_id", "source", "trust_tier", "note_type", "body_text",
            "provenance_pdf", "provenance_pages", "is_internal_farm_use_only",
            "extraction_model", "extracted_at", "created_at",
        }
        assert expected.issubset(cols), f"Missing columns: {expected - cols}"

    def test_ac04a_body_text_length_check_enforced(self, migrated_engine):
        """AC-04a: Insert with 2001-char body_text raises IntegrityError (DB-level CHECK)."""
        from sqlalchemy import text
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.exc import IntegrityError
        from datetime import datetime, timezone

        engine, _ = migrated_engine
        SessionLocal = sessionmaker(engine)
        now_str = datetime.now(timezone.utc).isoformat()

        with engine.begin() as conn:
            conn.execute(text("INSERT INTO crops (name_he) VALUES ('ארוגולה')"))

        with SessionLocal() as session:
            with pytest.raises(IntegrityError):
                session.execute(text(
                    "INSERT INTO crop_knowledge_notes "
                    "(crop_id, source, trust_tier, note_type, body_text, is_internal_farm_use_only, created_at) "
                    "VALUES (1, 'NI:jmf_book_v1', 'NI', 'pest_disease', :body, 1, :ts)"
                ), {"body": "X" * 2001, "ts": now_str})
                session.commit()

    def test_ac01_downgrade_drops_table(self, migrated_engine):
        from sqlalchemy import create_engine, text, inspect as sa_inspect
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        _, m045 = migrated_engine
        # Create a fresh engine to test downgrade independently
        engine2 = create_engine("sqlite:///:memory:")
        with engine2.begin() as conn:
            conn.execute(text(
                "CREATE TABLE crops (id INTEGER PRIMARY KEY AUTOINCREMENT, name_he TEXT NOT NULL)"
            ))

        with engine2.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m045.upgrade.__globals__["op"] = ops
            m045.upgrade()

        assert "crop_knowledge_notes" in sa_inspect(engine2).get_table_names()

        with engine2.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m045.downgrade.__globals__["op"] = ops
            m045.downgrade()

        assert "crop_knowledge_notes" not in sa_inspect(engine2).get_table_names()
