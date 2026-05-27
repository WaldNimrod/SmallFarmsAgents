"""Migration 053 fwd/bwd — AC-C2-01.

SFA-S003-P002-WP-C2 LOD400 §6.
Uses importlib.util pattern from test_c4_migrations.py.
"""
import importlib.util

import pytest

pytestmark = pytest.mark.crop_book

_MIGRATION_PATH = "organic_market_agent/db/versions/053_extend_ckn_note_type.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("m053", _MIGRATION_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestMigration053:
    """AC-C2-01: migration 053 has correct metadata and SQLite-safe skip."""

    def test_migration_053_revision_metadata(self):
        """revision='053', down_revision='052'."""
        m = _load_migration()
        assert m.revision == "053"
        assert m.down_revision == "052"

    def test_migration_053_sqlite_upgrade_is_noop(self):
        """upgrade() on SQLite returns without raising (SQLite guard)."""
        from sqlalchemy import create_engine
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m = _load_migration()
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m.upgrade.__globals__["op"] = ops
            m.upgrade()  # SQLite guard returns early — should not raise
