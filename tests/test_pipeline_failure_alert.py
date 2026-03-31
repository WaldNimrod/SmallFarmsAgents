"""Pipeline writes pipeline_alerts on failure paths.

If you see dashboard alerts like ``RuntimeError: simulated collector failure`` on a shared
PostgreSQL used for both development and ``pytest``, they come from this module: the test
patches ``execute_ingestion_for_run`` to raise that error on purpose.

Verify suspicious runs in SQL::

    SELECT id, triggered_by, status, created_at, notes
    FROM ingestion_runs
    WHERE id IN (569, 571);

Expect ``triggered_by = 'test'`` for rows created by this test before teardown was added.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
import sqlalchemy as sa
from sqlalchemy import select, text

from organic_market_agent.models.runs import IngestionRun
from organic_market_agent.models.scheduler import PipelineAlert
from organic_market_agent.scheduler.pipeline import run_pipeline


@pytest.fixture
def _skip_if_no_pg(db_session):
    try:
        db_session.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("PostgreSQL not available")


def test_run_pipeline_exception_creates_pipeline_alert(db_session, _skip_if_no_pg):
    n_pairs = db_session.scalar(
        text(
            """
            SELECT COUNT(*) FROM sources s
            JOIN source_fetch_profiles sfp ON sfp.source_id = s.id
            WHERE s.is_active AND sfp.is_active
            """
        )
    )
    if not n_pairs:
        pytest.skip("No active source+fetch profile for pipeline")

    run = IngestionRun(
        run_type="manual",
        triggered_by="test",
        status="running",
        sources_total=int(n_pairs),
        sources_succeeded=0,
        sources_failed=0,
        community_sources_succeeded=0,
    )
    db_session.add(run)
    db_session.commit()
    rid = run.id

    try:
        before = db_session.execute(
            select(sa.func.count())
            .select_from(PipelineAlert)
            .where(PipelineAlert.ingestion_run_id == rid)
        ).scalar_one()

        with patch(
            "organic_market_agent.scheduler.pipeline.execute_ingestion_for_run",
            side_effect=RuntimeError("simulated collector failure"),
        ):
            run_pipeline(rid, retry_attempts=0)

        after = db_session.execute(
            select(sa.func.count())
            .select_from(PipelineAlert)
            .where(PipelineAlert.ingestion_run_id == rid)
        ).scalar_one()
        assert int(after) > int(before)

        db_session.expire_all()
        run2 = db_session.get(IngestionRun, rid)
        assert run2 is not None
        assert run2.status == "failed"
        assert run2.finished_at is not None

        msg = db_session.execute(
            select(PipelineAlert.message)
            .where(PipelineAlert.ingestion_run_id == rid)
            .order_by(PipelineAlert.id.desc())
            .limit(1)
        ).scalar_one()
        assert "simulated collector failure" in (msg or "")
    finally:
        db_session.execute(text("DELETE FROM pipeline_alerts WHERE ingestion_run_id = :rid"), {"rid": rid})
        db_session.execute(text("DELETE FROM log_entries WHERE ingestion_run_id = :rid"), {"rid": rid})
        db_session.execute(text("DELETE FROM ingestion_runs WHERE id = :rid"), {"rid": rid})
        db_session.commit()
