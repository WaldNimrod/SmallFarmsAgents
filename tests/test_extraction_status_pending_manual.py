"""Post-migration 073: extraction_status CHECK includes pending_manual; SRC_WA seeded."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from organic_market_agent.db.session import engine


def _require_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available")


def test_chk_rei_extraction_status_includes_pending_manual():
    _require_db()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                WHERE t.relname = 'raw_extracted_items'
                  AND c.conname = 'chk_rei_extraction_status'
                """
            )
        ).fetchone()
        assert row is not None, "chk_rei_extraction_status missing"
        defn = row[0] or ""
        assert "pending_manual" in defn


def test_src_wa_source_exists():
    _require_db()
    with engine.connect() as conn:
        n = conn.execute(
            text("SELECT COUNT(*) FROM sources WHERE code = 'SRC_WA'")
        ).scalar()
        assert n == 1
