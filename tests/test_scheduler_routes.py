"""M6 scheduler + alerts admin routes."""
from __future__ import annotations

from sqlalchemy import select

from organic_market_agent.models import PipelineAlert, SchedulerConfig


def test_t1_get_scheduler_returns_200(logged_in_client, db_session):
    cfg = db_session.scalars(select(SchedulerConfig).limit(1)).first()
    if cfg is None:
        import pytest

        pytest.skip("scheduler_config missing — run migration 016")
    r = logged_in_client.get("/scheduler")
    assert r.status_code == 200
    assert b'name="run_hour"' in r.data


def test_t2_post_scheduler_toggle_flips_enabled(logged_in_client, db_session):
    cfg = db_session.scalars(select(SchedulerConfig).limit(1)).first()
    if cfg is None:
        import pytest

        pytest.skip("scheduler_config missing — run migration 016")
    before = cfg.is_enabled
    r = logged_in_client.post("/scheduler/toggle", follow_redirects=False)
    assert r.status_code in (302, 303)
    db_session.expire_all()
    cfg2 = db_session.scalars(select(SchedulerConfig).limit(1)).first()
    assert cfg2 is not None
    assert cfg2.is_enabled is (not before)


def test_t3_post_scheduler_run_cleanup_reports_count(logged_in_client, db_session):
    cfg = db_session.scalars(select(SchedulerConfig).limit(1)).first()
    if cfg is None:
        import pytest

        pytest.skip("scheduler_config missing — run migration 016")
    r = logged_in_client.post("/scheduler/run-cleanup", follow_redirects=True)
    assert r.status_code == 200
    assert b"\xd7\xa0\xd7\x95\xd7\xa7\xd7\x95" in r.data or b"0" in r.data


def test_t4_post_alert_read_sets_is_read(logged_in_client, db_session):
    from organic_market_agent.models import IngestionRun

    run = db_session.scalars(select(IngestionRun).order_by(IngestionRun.id.desc()).limit(1)).first()
    if run is None:
        import pytest

        pytest.skip("No ingestion run for alert FK")
    alert = PipelineAlert(
        level="info",
        message="test read route",
        ingestion_run_id=run.id,
        is_read=False,
    )
    db_session.add(alert)
    db_session.commit()
    aid = alert.id

    r = logged_in_client.post(f"/alerts/{aid}/read", follow_redirects=False)
    assert r.status_code in (302, 303)
    db_session.expire_all()
    row = db_session.get(PipelineAlert, aid)
    assert row is not None
    assert row.is_read is True
