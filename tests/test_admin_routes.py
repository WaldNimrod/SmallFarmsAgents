"""M5 admin HTTP tests (Flask test client)."""
from __future__ import annotations

import uuid
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
        "/aliases",
        "/rules",
        "/runs",
        "/qa_flags",
        "/audit",
    ]
    for path in paths:
        r = client.get(path)
        assert r.status_code == 200, path
    dash = client.get("/")
    assert dash.status_code == 200
    assert b"sortable_tables.js" in dash.data


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

    before = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    with patch("organic_market_agent.admin.routes.runs.run_pipeline"):
        r = logged_in_client.post("/runs/trigger", follow_redirects=False)
    assert r.status_code in (302, 303)
    after = db_session.execute(sa.select(sa.func.count()).select_from(IngestionRun)).scalar_one()
    assert after > before


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


def test_t11_audit_lists_prior_actions(logged_in_client, db_session):
    r = logged_in_client.get("/audit")
    assert r.status_code == 200
    assert b"create_alias" in r.data or b"disable_alias" in r.data or b"trigger_run" in r.data
