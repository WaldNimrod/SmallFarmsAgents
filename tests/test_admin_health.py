"""DV-1 health surface tests (SFA-S003-P005-WP001).

The deploy hook's whole verification rests on this endpoint, so the tests pin
the properties the hook depends on: reachable without auth, answerable without
a database, JSON shape stable, and — critically — the build sha is a snapshot
of the process, not a live read of the working tree.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from organic_market_agent.admin import create_app
from organic_market_agent.admin.routes import health

REPO_ROOT = Path(__file__).resolve().parents[1]


def _client(monkeypatch, build_sha_env: str | None):
    if build_sha_env is None:
        monkeypatch.delenv(health.BUILD_SHA_ENV, raising=False)
    else:
        monkeypatch.setenv(health.BUILD_SHA_ENV, build_sha_env)
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health_returns_200_json_without_login(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.mimetype == "application/json"
    body = r.get_json()
    assert body["status"] == "ok"
    assert body["service"] == "sfa-admin"
    assert body["build_sha"]


def test_health_prefers_aos_build_sha_env(monkeypatch):
    cl = _client(monkeypatch, "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
    assert cl.get("/api/health").get_json()["build_sha"] == (
        "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    )


def test_health_falls_back_to_git_head_when_env_unset(monkeypatch):
    expected = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    if not expected:
        pytest.skip("not a git checkout")
    cl = _client(monkeypatch, None)
    assert cl.get("/api/health").get_json()["build_sha"] == expected


def test_health_blank_env_is_ignored(monkeypatch):
    """An empty AOS_BUILD_SHA must not shadow the git fallback."""
    cl = _client(monkeypatch, "   ")
    sha = cl.get("/api/health").get_json()["build_sha"]
    assert sha.strip() and sha != health.UNKNOWN_SHA


def test_resolve_build_sha_unknown_outside_a_repo(monkeypatch, tmp_path):
    monkeypatch.delenv(health.BUILD_SHA_ENV, raising=False)
    assert health.resolve_build_sha(tmp_path) == health.UNKNOWN_SHA


def test_resolve_build_sha_unknown_when_git_is_missing(monkeypatch):
    monkeypatch.delenv(health.BUILD_SHA_ENV, raising=False)

    def _boom(*_a, **_kw):
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", _boom)
    assert health.resolve_build_sha(REPO_ROOT) == health.UNKNOWN_SHA


def test_health_sha_is_a_process_snapshot_not_a_live_tree_read(monkeypatch):
    """The stale-process guarantee the hook relies on.

    After the app is built, changing what ``resolve_build_sha`` would return
    (i.e. the deploy tree moving to a new commit) must NOT change what the
    already-running process serves.
    """
    monkeypatch.setenv(health.BUILD_SHA_ENV, "1111111111111111111111111111111111111111")
    app = create_app()
    app.config["TESTING"] = True
    cl = app.test_client()

    monkeypatch.setenv(health.BUILD_SHA_ENV, "2222222222222222222222222222222222222222")

    assert cl.get("/api/health").get_json()["build_sha"] == (
        "1111111111111111111111111111111111111111"
    )


def test_health_does_not_open_a_db_session(monkeypatch, client):
    """DB outage must not take the health surface down with it."""
    import organic_market_agent.admin as admin_mod

    def _explode(*_a, **_kw):
        raise AssertionError("health must not touch the database")

    monkeypatch.setattr(admin_mod, "SessionFactory", _explode)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"
