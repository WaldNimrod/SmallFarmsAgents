"""M6 scheduler runner — gating and alert outcome (mocked DB / pipeline)."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from organic_market_agent.scheduler.runner import (
    alert_for_run_outcome,
    main,
    scheduled_time_matches,
)


def test_scheduled_time_matches_within_one_minute():
    assert scheduled_time_matches(
        SimpleNamespace(hour=6, minute=0, tzinfo=None),
        6,
        0,
    )
    assert scheduled_time_matches(
        SimpleNamespace(hour=6, minute=1, tzinfo=None),
        6,
        0,
    )
    assert scheduled_time_matches(
        SimpleNamespace(hour=5, minute=59, tzinfo=None),
        6,
        0,
    )
    assert not scheduled_time_matches(
        SimpleNamespace(hour=6, minute=2, tzinfo=None),
        6,
        0,
    )


def test_t1_scheduler_exits_when_disabled():
    with patch("organic_market_agent.scheduler.runner.run_pipeline") as rp:
        mock_cm = MagicMock()
        mock_sess = MagicMock()
        mock_cm.__enter__.return_value = mock_sess
        mock_cm.__exit__.return_value = None
        cfg = SimpleNamespace(is_enabled=False)
        mock_sess.scalars.return_value.first.return_value = cfg
        with patch("organic_market_agent.scheduler.runner.SessionFactory", return_value=mock_cm):
            main()
        rp.assert_not_called()


def test_t2_scheduler_exits_when_time_does_not_match():
    with patch("organic_market_agent.scheduler.runner.run_pipeline") as rp:
        with patch(
            "organic_market_agent.scheduler.runner.scheduled_time_matches",
            return_value=False,
        ):
            mock_cm = MagicMock()
            mock_sess = MagicMock()
            mock_cm.__enter__.return_value = mock_sess
            mock_cm.__exit__.return_value = None
            cfg = SimpleNamespace(is_enabled=True, run_hour=6, run_minute=0, retry_attempts=2)
            mock_sess.scalars.return_value.first.return_value = cfg
            with patch("organic_market_agent.scheduler.runner.SessionFactory", return_value=mock_cm):
                main()
            rp.assert_not_called()


def test_t3_scheduler_calls_run_pipeline_when_gates_pass():
    pending_run = [None]

    def track_add(obj):
        pending_run[0] = obj

    def do_flush():
        o = pending_run[0]
        if o is not None and getattr(o, "id", None) is None:
            o.id = 77

    mock_cm = MagicMock()
    mock_sess = MagicMock()
    mock_cm.__enter__.return_value = mock_sess
    mock_cm.__exit__.return_value = None

    cfg = SimpleNamespace(is_enabled=True, run_hour=6, run_minute=0, retry_attempts=3)
    mock_sess.scalars.return_value.first.return_value = cfg
    mock_sess.execute.return_value.scalar_one.return_value = 0
    mock_sess.add.side_effect = track_add
    mock_sess.flush.side_effect = do_flush

    finished = SimpleNamespace(
        id=77,
        status="completed",
        sources_failed=0,
        sources_succeeded=2,
    )
    mock_sess.get.return_value = finished

    with patch("organic_market_agent.scheduler.runner.run_pipeline") as rp:
        with patch(
            "organic_market_agent.scheduler.runner.scheduled_time_matches",
            return_value=True,
        ):
            with patch("organic_market_agent.scheduler.runner.SessionFactory", return_value=mock_cm):
                main()
        rp.assert_called_once_with(77, retry_attempts=3)

    adds = [c.args[0] for c in mock_sess.add.call_args_list]
    assert any(getattr(a, "level", None) == "info" for a in adds)


def test_t4_main_writes_warning_pipeline_alert_for_partial():
    pending_run = [None]

    def track_add(obj):
        pending_run[0] = obj

    def do_flush():
        o = pending_run[0]
        if o is not None and getattr(o, "id", None) is None:
            o.id = 88

    mock_cm = MagicMock()
    mock_sess = MagicMock()
    mock_cm.__enter__.return_value = mock_sess
    mock_cm.__exit__.return_value = None

    cfg = SimpleNamespace(is_enabled=True, run_hour=6, run_minute=0, retry_attempts=2)
    mock_sess.scalars.return_value.first.return_value = cfg
    mock_sess.execute.return_value.scalar_one.return_value = 0
    mock_sess.add.side_effect = track_add
    mock_sess.flush.side_effect = do_flush

    finished = SimpleNamespace(
        id=88,
        status="partial",
        sources_failed=1,
        sources_succeeded=2,
    )
    mock_sess.get.return_value = finished

    with patch("organic_market_agent.scheduler.runner.run_pipeline"):
        with patch(
            "organic_market_agent.scheduler.runner.scheduled_time_matches",
            return_value=True,
        ):
            with patch("organic_market_agent.scheduler.runner.SessionFactory", return_value=mock_cm):
                main()

    adds = [c.args[0] for c in mock_sess.add.call_args_list]
    assert any(getattr(a, "level", None) == "warning" for a in adds)


def test_alert_outcome_partial_is_warning_level():
    run = SimpleNamespace(status="partial", sources_failed=2, sources_succeeded=1, id=1)
    level, _msg = alert_for_run_outcome(run)
    assert level == "warning"


def test_alert_for_failed_run_is_error():
    run = SimpleNamespace(status="failed", sources_failed=3, sources_succeeded=0, id=1)
    level, _msg = alert_for_run_outcome(run)
    assert level == "error"
