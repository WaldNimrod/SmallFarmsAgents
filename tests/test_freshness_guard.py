"""Smoke tests for the new-tier freshness_guard (sfa.nimrod.bio).

Covers:
- No SFA_PUBLIC_BASE set → state="error", exit non-zero
- Health probe unreachable (network error) → state="error", exit non-zero
- Health probe degraded (bad JSON payload) → state="tier_unhealthy", exit non-zero
- Health probe ok, --no-repair → state="healthy", exit 0
- Health probe ok + repair success → state="repaired", exit 0
- Health probe ok + repair failure → state="repair_failed", exit non-zero
- No reference to www.nimrod.bio / LEGACY_PUBLIC_MANIFEST_URL
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

import pytest

from organic_market_agent.publisher.freshness_guard import (
    run_guard,
    main,
    DEFAULT_STATUS_FILE,
    SFA_PUBLIC_BASE_ENV,
)


_HEALTH_OK = {"status": "ok", "db": "ok"}
_HEALTH_DEGRADED = {"status": "ok", "db": "degraded"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_url_open_ok(body: dict):
    """Context-manager mock for urllib.request.urlopen that returns JSON body."""
    import io

    class _FakeResp:
        def read(self):
            return json.dumps(body).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    return MagicMock(return_value=_FakeResp())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestNoSfaPublicBase:
    def test_state_error_when_env_missing(self, tmp_path, monkeypatch):
        monkeypatch.delenv(SFA_PUBLIC_BASE_ENV, raising=False)
        sf = tmp_path / "status.json"
        status = run_guard(status_file=sf, sfa_public_base=None)
        assert status.state == "error"
        assert status.sfa_public_base is None
        assert sf.exists()
        data = json.loads(sf.read_text())
        assert data["state"] == "error"

    def test_main_returns_nonzero_when_env_missing(self, tmp_path, monkeypatch):
        monkeypatch.delenv(SFA_PUBLIC_BASE_ENV, raising=False)
        sf = tmp_path / "status.json"
        rc = main(["--status-file", str(sf), "--no-repair"])
        assert rc != 0


class TestHealthUnreachable:
    def test_state_error_on_network_failure(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            status = run_guard(status_file=sf)
        assert status.state == "error"
        assert status.health_status == "unreachable"
        assert status.repair_attempted is False


class TestHealthDegraded:
    def test_state_tier_unhealthy(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with patch(
            "urllib.request.urlopen",
            _make_url_open_ok(_HEALTH_DEGRADED),
        ):
            status = run_guard(status_file=sf)
        assert status.state == "tier_unhealthy"
        assert status.health_status == "degraded"
        assert status.repair_attempted is False


class TestHealthOkNoRepair:
    def test_healthy_no_repair(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with patch(
            "urllib.request.urlopen",
            _make_url_open_ok(_HEALTH_OK),
        ):
            status = run_guard(status_file=sf, do_repair=False)
        assert status.state == "healthy"
        assert status.health_status == "ok"
        assert status.repair_attempted is False

    def test_main_exits_zero_on_healthy(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with patch(
            "urllib.request.urlopen",
            _make_url_open_ok(_HEALTH_OK),
        ):
            rc = main(["--status-file", str(sf), "--no-repair"])
        assert rc == 0


class TestRepairSuccess:
    def test_state_repaired_on_push_success(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with (
            patch("urllib.request.urlopen", _make_url_open_ok(_HEALTH_OK)),
            patch(
                "organic_market_agent.publisher.freshness_guard._attempt_repair",
                return_value=[],
            ),
        ):
            status = run_guard(status_file=sf, do_repair=True)
        assert status.state == "repaired"
        assert status.repair_attempted is True
        assert status.repair_errors == []

    def test_main_exits_zero_on_repaired(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with (
            patch("urllib.request.urlopen", _make_url_open_ok(_HEALTH_OK)),
            patch(
                "organic_market_agent.publisher.freshness_guard._attempt_repair",
                return_value=[],
            ),
        ):
            rc = main(["--status-file", str(sf)])
        assert rc == 0


class TestRepairFailure:
    def test_state_repair_failed(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with (
            patch("urllib.request.urlopen", _make_url_open_ok(_HEALTH_OK)),
            patch(
                "organic_market_agent.publisher.freshness_guard._attempt_repair",
                return_value=["DB connection refused"],
            ),
        ):
            status = run_guard(status_file=sf, do_repair=True)
        assert status.state == "repair_failed"
        assert "DB connection refused" in status.repair_errors

    def test_main_exits_nonzero_on_repair_failed(self, tmp_path, monkeypatch):
        monkeypatch.setenv(SFA_PUBLIC_BASE_ENV, "https://sfa.nimrod.bio")
        sf = tmp_path / "status.json"
        with (
            patch("urllib.request.urlopen", _make_url_open_ok(_HEALTH_OK)),
            patch(
                "organic_market_agent.publisher.freshness_guard._attempt_repair",
                return_value=["push error"],
            ),
        ):
            rc = main(["--status-file", str(sf)])
        assert rc != 0


class TestNoLegacyReferences:
    """Guard module must have no www.nimrod.bio / LEGACY_PUBLIC_MANIFEST_URL references."""

    def test_no_www_nimrod_bio_in_source(self):
        import organic_market_agent.publisher.freshness_guard as fg_mod
        import inspect

        source = inspect.getsource(fg_mod)
        assert "www.nimrod.bio" not in source
        assert "LEGACY_PUBLIC_MANIFEST_URL" not in source
        assert "dispatch_upload" not in source
