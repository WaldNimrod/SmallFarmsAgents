"""Admin list pages: summary bar data-* attributes match PostgreSQL counts."""
from __future__ import annotations

import re

import pytest
from sqlalchemy import text

_DISPLAYED = re.compile(rb'data-summary-displayed="(\d+)"')
_FULL = re.compile(rb'data-summary-full="(\d+)"')


def _first_int(pattern: re.Pattern[bytes], html: bytes) -> int | None:
    m = pattern.search(html)
    return int(m.group(1)) if m else None


def _all_pairs(html: bytes) -> list[tuple[int, int]]:
    """(displayed, full) for each bar that has both attributes."""
    out = []
    for dm, fm in zip(_DISPLAYED.findall(html), _FULL.findall(html)):
        out.append((int(dm), int(fm)))
    return out


@pytest.fixture
def _skip_if_no_pg(db_session):
    try:
        db_session.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("PostgreSQL session unavailable")


def test_products_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/products")
    assert r.status_code == 200
    db_total = int(db_session.execute(text("SELECT COUNT(*) FROM products")).scalar_one() or 0)
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == db_total
    assert d == min(db_total, 200)


def test_sources_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/sources")
    assert r.status_code == 200
    db_total = int(db_session.execute(text("SELECT COUNT(*) FROM sources")).scalar_one() or 0)
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == db_total
    assert d == min(db_total, 200)


def test_runs_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/runs")
    assert r.status_code == 200
    db_total = int(
        db_session.execute(text("SELECT COUNT(*) FROM ingestion_runs")).scalar_one() or 0
    )
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == db_total
    assert d == min(db_total, 50)


def test_unresolved_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/unresolved")
    assert r.status_code == 200
    distinct = int(
        db_session.execute(
            text(
                """
                SELECT COUNT(*) FROM (
                    SELECT 1
                    FROM raw_extracted_items rei
                    JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
                    JOIN sources s ON s.id = sfr.source_id
                    WHERE rei.extraction_status = 'unresolvable'
                      AND rei.is_quarantined = false
                    GROUP BY rei.raw_product_name
                ) x
                """
            )
        ).scalar_one()
        or 0
    )
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == distinct
    assert d == min(distinct, 200)


def test_audit_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/audit")
    assert r.status_code == 200
    db_total = int(db_session.execute(text("SELECT COUNT(*) FROM audit_log")).scalar_one() or 0)
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == db_total
    assert d == min(db_total, 200)


def test_qa_flags_summary_matches_db(client, db_session, _skip_if_no_pg):
    r = client.get("/qa_flags")
    assert r.status_code == 200
    db_total = int(
        db_session.execute(text("SELECT COUNT(*) FROM observation_flags")).scalar_one() or 0
    )
    d = _first_int(_DISPLAYED, r.data)
    f = _first_int(_FULL, r.data)
    assert d is not None and f is not None
    assert f == db_total
    assert d == min(db_total, 200)


def test_aliases_active_bar_matches_db(client, db_session, _skip_if_no_pg):
    from tests.conftest import admin_login
    from sqlalchemy import select
    from organic_market_agent.models.users import User

    u = db_session.execute(select(User).where(User.email == "admin@local")).scalar_one_or_none()
    if u is None:
        pytest.skip("admin@local missing")
    cl = client
    admin_login(cl, "admin@local", "admin")
    r = cl.get("/aliases")
    assert r.status_code == 200
    active_db = int(
        db_session.execute(
            text("SELECT COUNT(*) FROM product_aliases WHERE is_active = true")
        ).scalar_one()
        or 0
    )
    pairs = _all_pairs(r.data)
    assert pairs, "expected at least one summary bar with data-* counts"
    disp, full = pairs[0]
    assert full == active_db
    assert disp == min(active_db, 500)


def test_products_segments_sum_to_total(db_session, _skip_if_no_pg):
    act = int(
        db_session.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = true")
        ).scalar_one()
        or 0
    )
    iact = int(
        db_session.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = false")
        ).scalar_one()
        or 0
    )
    tot = int(db_session.execute(text("SELECT COUNT(*) FROM products")).scalar_one() or 0)
    assert act + iact == tot
