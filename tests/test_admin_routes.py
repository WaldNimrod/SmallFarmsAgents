"""M5 admin HTTP tests (Flask test client)."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from sqlalchemy import select

from organic_market_agent.models import NormalizerProfile, NormalizerRule, Product, ProductAlias
from organic_market_agent.models.runs import IngestionRun
from organic_market_agent.models.users import AuditLog, User

from tests.conftest import admin_login


def test_t01_readonly_get_routes_return_200(client, db_session):
    paths = [
        "/",
        "/sources",
        "/products",
        "/unresolved",
        "/diagnostics/normalizer",
        "/catalog/scope-skip",
        "/catalog/suggestions",
        "/catalog/pending-aliases",
        "/aliases",
        "/rules",
        "/runs",
        "/qa_flags",
        "/audit",
        "/alerts",
    ]
    for path in paths:
        r = client.get(path)
        assert r.status_code == 200, path
    dash = client.get("/")
    assert dash.status_code == 200
    assert b"sortable_tables.js" in dash.data


def test_t01b_diagnostics_export_requires_login(client):
    r = client.get("/diagnostics/normalizer/export.json", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers.get("Location", "")


def test_t01c_diagnostics_export_json_when_logged_in(logged_in_client):
    r = logged_in_client.get("/diagnostics/normalizer/export.json")
    assert r.status_code == 200
    assert r.mimetype.startswith("application/json")
    assert b"normalizer_diagnostics_v1" in r.data


def test_t01d_save_baseline_requires_login(client):
    r = client.post("/maintenance/save-baseline", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers.get("Location", "")


def test_t01e_save_baseline_writes_json(logged_in_client, db_session, tmp_path, monkeypatch):
    import organic_market_agent.admin.baseline_metrics as bm

    out = tmp_path / "baseline_test.json"
    monkeypatch.setenv("NORMALIZER_BASELINE_JSON", str(out))

    r = logged_in_client.post("/maintenance/save-baseline", follow_redirects=False)
    assert r.status_code in (302, 303)
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("schema") == bm.SCHEMA


def test_t01f_catalog_renormalize_requires_login(client):
    r = client.post("/maintenance/catalog-renormalize", follow_redirects=False)
    assert r.status_code == 302


def test_t01g_full_data_refresh_requires_login(client):
    r = client.post("/maintenance/full-data-refresh", follow_redirects=False)
    assert r.status_code == 302
    assert "/auth/login" in r.headers.get("Location", "")


def test_t02_login_success_sets_session_and_redirects(client, db_session):
    u = db_session.execute(select(User).where(User.email == "admin@local")).scalar_one_or_none()
    if u is None:
        pytest.skip("admin@local missing")
    r = admin_login(client, "admin@local", "admin")
    assert r.status_code in (302, 303)
    assert "Location" in r.headers
    assert any("session" in h.lower() for h in r.headers.getlist("Set-Cookie"))


def test_t03_login_wrong_password_shows_error(client, db_session):
    if db_session.execute(select(User).where(User.email == "admin@local")).scalar_one_or_none() is None:
        pytest.skip("admin@local missing")
    r = client.post(
        "/auth/login",
        data={"email": "admin@local", "password": "wrong-password-xyz"},
        follow_redirects=False,
    )
    assert r.status_code == 200
    assert "אימייל או סיסמה שגויים".encode("utf-8") in r.data


def test_t04_aliases_new_without_login_redirects_to_login(client):
    r = client.post(
        "/aliases/new",
        data={"product_code": "X", "alias_text": "y"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert "/auth/login" in r.headers.get("Location", "")


def test_t05_aliases_new_with_login_creates_row_and_audit(logged_in_client, db_session):
    prod = db_session.execute(select(Product).where(Product.is_active.is_(True)).limit(1)).scalar_one_or_none()
    if prod is None:
        pytest.skip("No active product")
    alias_text = f"m5-test-alias-{uuid.uuid4().hex[:12]}"
    r = logged_in_client.post(
        "/aliases/new",
        data={
            "product_code": prod.code,
            "alias_text": alias_text,
            "source_id": "",
        },
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    pa = db_session.execute(
        select(ProductAlias).where(ProductAlias.alias_text == alias_text)
    ).scalar_one_or_none()
    assert pa is not None
    assert pa.is_active is True
    aud = db_session.execute(
        select(AuditLog).where(AuditLog.action == "create_alias").order_by(AuditLog.id.desc()).limit(5)
    ).scalars().all()
    assert any(a.entity_id == pa.id for a in aud)
    # Teardown: avoid leaving m5-test-alias-* rows in DB for local / CI noise
    logged_in_client.post(f"/aliases/{pa.id}/disable", follow_redirects=False)
    db_session.expire_all()
    assert db_session.get(ProductAlias, pa.id).is_active is False


def test_t06_disable_alias_with_login(logged_in_client, db_session):
    prod = db_session.execute(select(Product).where(Product.is_active.is_(True)).limit(1)).scalar_one_or_none()
    if prod is None:
        pytest.skip("No active product")
    alias_text = f"m5-disable-{uuid.uuid4().hex[:12]}"
    pa = ProductAlias(
        product_id=prod.id,
        alias_text=alias_text,
        alias_text_normalized=alias_text.lower(),
        source_id=None,
        is_active=True,
    )
    db_session.add(pa)
    db_session.commit()
    r = logged_in_client.post(
        f"/aliases/{pa.id}/disable",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    db_session.expire_all()
    pa2 = db_session.get(ProductAlias, pa.id)
    assert pa2 is not None
    assert pa2.is_active is False


def test_t07_rules_new_with_login(logged_in_client, db_session):
    np = db_session.execute(select(NormalizerProfile).where(NormalizerProfile.is_active.is_(True)).limit(1)).scalar_one_or_none()
    if np is None:
        pytest.skip("No normalizer profile")
    pat = f"m5-rule-{uuid.uuid4().hex[:10]}"
    r = logged_in_client.post(
        "/rules/new",
        data={
            "profile_id": str(np.id),
            "rule_kind": "unit_map",
            "match_pattern": pat,
            "match_type": "exact",
            "replacement_value": "kg",
            "priority": "50",
            "notes": "m5 test",
        },
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    rule = db_session.execute(
        select(NormalizerRule).where(NormalizerRule.match_pattern == pat)
    ).scalar_one_or_none()
    assert rule is not None
    assert rule.is_active is True


def test_t08_rules_disable_with_login(logged_in_client, db_session):
    np = db_session.execute(select(NormalizerProfile).where(NormalizerProfile.is_active.is_(True)).limit(1)).scalar_one_or_none()
    if np is None:
        pytest.skip("No normalizer profile")
    pat = f"m5-rd-{uuid.uuid4().hex[:10]}"
    rule = NormalizerRule(
        normalizer_profile_id=np.id,
        rule_kind="organic_flag",
        match_pattern=pat,
        match_type="exact",
        replacement_value=None,
        priority=99,
        is_active=True,
        created_by="test",
    )
    db_session.add(rule)
    db_session.commit()
    rid = rule.id
    r = logged_in_client.post(f"/rules/{rid}/disable", follow_redirects=False)
    assert r.status_code in (302, 303)
    db_session.expire_all()
    rule2 = db_session.get(NormalizerRule, rid)
    assert rule2 is not None
    assert rule2.is_active is False


def test_t09_runs_trigger_creates_ingestion_run(logged_in_client, db_session):
    from organic_market_agent.scheduler.run_ingestion import _get_active_sources_with_profiles

    if not _get_active_sources_with_profiles(db_session):
        pytest.skip("No active sources with fetch profiles")

    # Integration-DB hygiene (this suite runs against a live, accumulated Postgres
    # DB — no per-test rollback). /runs/trigger has a concurrency guard that
    # redirects WITHOUT creating a run when any IngestionRun is still "running"
    # (runs.py runs_trigger §n_running). Because this test patches out run_pipeline,
    # the run it creates never transitions out of "running", so a prior interrupted
    # invocation can leave a stuck row that blocks every later run. Finalize any
    # such leftovers up front so the assertion reflects this trigger, not DB state.
    db_session.execute(
        sa.update(IngestionRun)
        .where(IngestionRun.status == "running")
        .values(status="failed", finished_at=datetime.now(timezone.utc))
    )
    db_session.commit()

    before = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    with patch("organic_market_agent.admin.routes.runs.run_pipeline"):
        r = logged_in_client.post("/runs/trigger", follow_redirects=False)
    assert r.status_code in (302, 303)
    after = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    assert after > before
    db_session.expire_all()
    last = db_session.execute(sa.select(IngestionRun).order_by(IngestionRun.id.desc()).limit(1)).scalar_one()
    last.status = "failed"
    last.finished_at = datetime.now(timezone.utc)
    db_session.commit()


class _ImmediateThread:
    """Runs thread target synchronously (for testing partial(run_pipeline, ...))."""

    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self._target = target

    def start(self):
        if self._target is not None:
            self._target()


def test_t09b_runs_trigger_passes_source_code_to_run_pipeline(logged_in_client, db_session):
    from organic_market_agent.models import Source, SourceFetchProfile

    expected = db_session.scalar(
        sa.select(sa.func.count())
        .select_from(Source)
        .join(SourceFetchProfile, SourceFetchProfile.source_id == Source.id)
        .where(
            Source.is_active.is_(True),
            SourceFetchProfile.is_active.is_(True),
            Source.code == "SRC001",
        )
    )
    expected = int(expected or 0)
    if expected == 0:
        pytest.skip("No active SRC001 with fetch profile")

    with patch("organic_market_agent.admin.routes.runs.threading.Thread", _ImmediateThread):
        with patch("organic_market_agent.admin.routes.runs.run_pipeline") as rp:
            r = logged_in_client.post(
                "/runs/trigger",
                data={"source_code": "SRC001"},
                follow_redirects=False,
            )
    assert r.status_code in (302, 303)
    rp.assert_called_once()
    _args, kwargs = rp.call_args
    assert kwargs.get("source_code") == "SRC001"
    assert kwargs.get("skip_normalize") is False
    assert kwargs.get("skip_publish") is False

    db_session.expire_all()
    last = db_session.execute(
        sa.select(IngestionRun).order_by(IngestionRun.id.desc()).limit(1)
    ).scalar_one()
    assert last.sources_total == expected
    last.status = "failed"
    last.finished_at = datetime.now(timezone.utc)
    db_session.commit()


def test_t09c_runs_trigger_rejected_when_already_running(logged_in_client, db_session):
    from organic_market_agent.scheduler.run_ingestion import _get_active_sources_with_profiles

    if not _get_active_sources_with_profiles(db_session):
        pytest.skip("No active sources with fetch profiles")

    stuck = IngestionRun(
        run_type="manual",
        triggered_by="test",
        status="running",
        started_at=datetime.now(timezone.utc),
        sources_total=1,
        sources_succeeded=0,
        sources_failed=0,
        community_sources_succeeded=0,
    )
    db_session.add(stuck)
    db_session.commit()
    before = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    with patch("organic_market_agent.admin.routes.runs.run_pipeline"):
        r = logged_in_client.post("/runs/trigger", follow_redirects=False)
    assert r.status_code in (302, 303)
    after = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    assert int(after) == int(before)
    stuck2 = db_session.get(IngestionRun, stuck.id)
    assert stuck2 is not None
    assert stuck2.status == "running"
    stuck2.status = "failed"
    stuck2.finished_at = datetime.now(timezone.utc)
    db_session.commit()


def test_t09d_runs_stop_active_marks_running_failed(logged_in_client, db_session):
    ir = IngestionRun(
        run_type="manual",
        triggered_by="test",
        status="running",
        started_at=datetime.now(timezone.utc),
        sources_total=1,
        sources_succeeded=0,
        sources_failed=0,
        community_sources_succeeded=0,
    )
    db_session.add(ir)
    db_session.commit()
    rid = ir.id
    r = logged_in_client.post("/runs/stop-active", follow_redirects=False)
    assert r.status_code in (302, 303)
    db_session.expire_all()
    ir2 = db_session.get(IngestionRun, rid)
    assert ir2 is not None
    assert ir2.status == "failed"
    assert ir2.finished_at is not None


def test_t10_product_disable_alias_with_login(logged_in_client, db_session):
    prod = db_session.execute(select(Product).where(Product.is_active.is_(True)).limit(1)).scalar_one_or_none()
    if prod is None:
        pytest.skip("No active product")
    alias_text = f"m5-pda-{uuid.uuid4().hex[:12]}"
    pa = ProductAlias(
        product_id=prod.id,
        alias_text=alias_text,
        alias_text_normalized=alias_text.lower(),
        source_id=None,
        is_active=True,
    )
    db_session.add(pa)
    db_session.commit()
    r = logged_in_client.post(
        f"/products/{prod.code}/disable_alias/{pa.id}",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    db_session.expire_all()
    assert db_session.get(ProductAlias, pa.id).is_active is False
    aud = db_session.execute(
        select(AuditLog).where(
            AuditLog.action == "disable_alias",
            AuditLog.entity_id == pa.id,
        )
    ).scalar_one_or_none()
    assert aud is not None


def test_t12_unresolved_export_json_requires_login(client, db_session):
    r = client.get("/unresolved/export.json")
    assert r.status_code in (302, 401)


def test_t13_unresolved_export_json_ok_when_logged_in(logged_in_client, db_session):
    r = logged_in_client.get("/unresolved/export.json?limit=5")
    assert r.status_code == 200
    assert r.is_json
    body = r.get_json()
    assert body.get("schema") == "unresolved_top_aggregate_v1"
    assert "generated_at" in body
    assert "items" in body
    assert isinstance(body["items"], list)


def test_t11_audit_lists_prior_actions(logged_in_client, db_session):
    r = logged_in_client.get("/audit")
    assert r.status_code == 200
    assert b"create_alias" in r.data or b"disable_alias" in r.data or b"trigger_run" in r.data


def test_t14_runs_list_shows_manager_columns(client, db_session):
    # db_session is required only for its connectivity skip-guard (mirrors t15/logged_in_client):
    # /runs queries the DB directly, and client alone performs no reachability check, so an
    # unreachable DB previously surfaced as a raw OperationalError instead of a clean skip.
    r = client.get("/runs")
    assert r.status_code == 200
    assert "מדד / נתונים".encode("utf-8") in r.data
    assert "התראות צינור".encode("utf-8") in r.data


def test_t15_runs_export_json_requires_login(client, db_session):
    rid = db_session.execute(sa.select(sa.func.max(IngestionRun.id))).scalar_one()
    if rid is None:
        pytest.skip("No ingestion run in DB")
    r = client.get(f"/runs/{int(rid)}/export.json", follow_redirects=False)
    assert r.status_code in (302, 401)


def test_t17_alerts_export_json_requires_login(client):
    r = client.get("/alerts/export.json", follow_redirects=False)
    assert r.status_code in (302, 401)


def test_t18_alerts_export_json_ok_when_logged_in(logged_in_client, db_session):
    r = logged_in_client.get("/alerts/export.json?scope=unread")
    assert r.status_code == 200
    assert r.content_type.startswith("application/json")
    body = r.get_json()
    assert body.get("schema") == "pipeline_alerts_export_v1"
    assert "exported_at" in body
    assert "alerts" in body
    assert isinstance(body["alerts"], list)


def test_t16_runs_export_json_ok_when_logged_in(logged_in_client, db_session):
    rid = db_session.execute(sa.select(sa.func.max(IngestionRun.id))).scalar_one()
    if rid is None:
        pytest.skip("No ingestion run in DB")
    r = logged_in_client.get(f"/runs/{int(rid)}/export.json")
    assert r.status_code == 200
    assert r.content_type.startswith("application/json")
    body = r.get_json()
    assert body is not None
    assert "ingestion_run" in body
    assert "totals" in body
    assert "source_fetch_runs" in body
    assert "pipeline_alerts" in body
    assert "log_entries" in body


# --- DV-1 deploy-verification health surface (SFA-S003-P005-WP001) ---


def test_t19_health_is_public_and_reports_status_and_build_sha(client):
    """The hook curls this unauthenticated; it must never redirect to login."""
    r = client.get("/api/health", follow_redirects=False)
    assert r.status_code == 200
    assert r.content_type.startswith("application/json")
    body = r.get_json()
    assert body["status"] == "ok"
    assert body["build_sha"]
    assert body["sha_source"] in ("env", "git", "unavailable")


def test_t20_health_prefers_env_build_sha(monkeypatch):
    """AOS_BUILD_SHA wins over the git fallback (deploy path stamps it)."""
    from organic_market_agent.admin.routes import health as health_mod

    monkeypatch.setenv("AOS_BUILD_SHA", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
    sha, source = health_mod.resolve_build_sha()
    assert sha == "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    assert source == "env"


def test_t21_health_falls_back_to_git_head(monkeypatch):
    """With no env stamp, the SHA comes from `git rev-parse HEAD` in the repo root."""
    import subprocess

    from organic_market_agent.admin.routes import health as health_mod

    monkeypatch.delenv("AOS_BUILD_SHA", raising=False)
    sha, source = health_mod.resolve_build_sha()
    if source == "unavailable":
        pytest.skip("git not available / not a work tree")
    expected = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(health_mod._REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert source == "git"
    assert sha == expected
    assert len(sha) == 40


def test_t22_health_sha_is_captured_at_process_start_not_per_request(client, monkeypatch):
    """Load-bearing: a live env change must NOT change the served SHA.

    If it did, a deploy whose `git pull` landed but whose service restart failed
    would still serve the new SHA and the DV-1 comparison would be a false green.
    """
    from organic_market_agent.admin.routes import health as health_mod

    served_before = client.get("/api/health").get_json()["build_sha"]
    monkeypatch.setenv("AOS_BUILD_SHA", "0000000000000000000000000000000000000000")
    served_after = client.get("/api/health").get_json()["build_sha"]
    assert served_after == served_before == health_mod.BUILD_SHA


def test_t23_health_never_leaks_more_than_status_and_build_identity(client):
    body = client.get("/api/health").get_json()
    assert set(body.keys()) == {"status", "build_sha", "sha_source"}
