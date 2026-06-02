"""Optional live Playwright + DB checks for mypips (set RUN_MYPIPS_E2E=1).

When E2E is enabled, the headless browser appends a per-run cache-busting query
parameter to the fetch URL so checksum dedupe does not skip parsing on repeat
runs (T09 / duplicate-asset path).
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def _require_e2e() -> None:
    if os.environ.get("RUN_MYPIPS_E2E", "").lower() not in ("1", "true", "yes"):
        pytest.skip("RUN_MYPIPS_E2E not set — skipping live mypips e2e")


def _assert_latest_run_has_rows(code: str) -> None:
    from sqlalchemy import create_engine, text

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL not set")

    eng = create_engine(db_url)
    with eng.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT COUNT(rei.id)
                FROM source_fetch_runs sfr
                JOIN sources s ON s.id = sfr.source_id
                LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
                WHERE s.code = :code
                GROUP BY sfr.id
                ORDER BY sfr.id DESC
                LIMIT 1
                """
            ),
            {"code": code},
        ).fetchone()
    assert row is not None and row[0] > 0, f"{code} expected raw rows after ingestion"


@pytest.mark.timeout(180)
def test_mypips_e2e_src061(_require_e2e: None) -> None:
    from organic_market_agent.scheduler.run_ingestion import run_ingestion

    run_ingestion("manual", "SRC061", True)
    _assert_latest_run_has_rows("SRC061")


@pytest.mark.timeout(180)
def test_mypips_e2e_src060(_require_e2e: None) -> None:
    from organic_market_agent.scheduler.run_ingestion import run_ingestion

    run_ingestion("manual", "SRC060", True)
    _assert_latest_run_has_rows("SRC060")


@pytest.mark.timeout(180)
def test_mypips_e2e_src070(_require_e2e: None) -> None:
    from organic_market_agent.scheduler.run_ingestion import run_ingestion

    run_ingestion("manual", "SRC070", True)
    _assert_latest_run_has_rows("SRC070")
