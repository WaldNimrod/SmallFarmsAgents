"""Maintenance: catalog_renormalize helpers (PostgreSQL)."""
from __future__ import annotations

import pytest
from sqlalchemy import text

from organic_market_agent.maintenance.catalog_renormalize import count_unresolvable_requeueable


def test_count_unresolvable_requeueable_runs(db_session):
    """Smoke: query succeeds when PostgreSQL is up."""
    n = count_unresolvable_requeueable(db_session)
    assert isinstance(n, int)
    assert n >= 0
    # Cross-check with raw SQL
    raw = db_session.execute(
        text(
            "SELECT COUNT(*) FROM raw_extracted_items "
            "WHERE extraction_status = 'unresolvable' AND is_quarantined IS NOT TRUE"
        )
    ).scalar_one()
    assert n == int(raw or 0)
