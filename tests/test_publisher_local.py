"""M4 PublishEngine local artifacts (PostgreSQL + tmp_path)."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun, NormalizedObservation, Product, Source, SourceFetchRun
from organic_market_agent.publisher import PublishEngine
from organic_market_agent.utils.exceptions import PublishAbortError

M4_NOTES = "m4_pub_pytest"
PUB_DATE = date(2099, 8, 12)
OBS_TS = datetime(2099, 8, 12, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def pg_session() -> Session:
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available for M4 publisher tests")

    session = SessionFactory()
    yield session
    session.close()


def _cleanup_pub(session: Session) -> None:
    session.execute(
        text(
            """
            DELETE FROM normalized_observations
            WHERE source_fetch_run_id IN (
              SELECT sfr.id FROM source_fetch_runs sfr
              JOIN ingestion_runs ir ON ir.id = sfr.ingestion_run_id
              WHERE ir.notes = :tag
            )
            """
        ),
        {"tag": M4_NOTES},
    )
    session.execute(text("DELETE FROM daily_aggregates WHERE aggregate_date = :d"), {"d": PUB_DATE})
    session.execute(
        text(
            """
            DELETE FROM weekly_snapshots
            WHERE week_start_date <= :d AND week_end_date >= :d
            """
        ),
        {"d": PUB_DATE},
    )
    session.execute(
        text(
            """
            DELETE FROM source_fetch_runs
            WHERE ingestion_run_id IN (SELECT id FROM ingestion_runs WHERE notes = :tag)
            """
        ),
        {"tag": M4_NOTES},
    )
    session.execute(text("DELETE FROM ingestion_runs WHERE notes = :tag"), {"tag": M4_NOTES})
    session.commit()


def _pick_sources_product(session: Session) -> tuple[int, int, int, int]:
    rows = session.execute(
        sa.select(Source.id).where(Source.is_active.is_(True)).order_by(Source.id).limit(2)
    ).scalars().all()
    if len(rows) < 2:
        pytest.skip("Need at least 2 active sources")
    prod = session.execute(sa.select(Product.id, Product.default_measurement_unit_id).limit(1)).one()
    return int(rows[0]), int(rows[1]), int(prod[0]), int(prod[1])


def _seed_two_community_obs(session: Session) -> None:
    sid1, sid2, pid, uid = _pick_sources_product(session)
    ir = IngestionRun(
        run_type="manual",
        status="completed",
        finished_at=datetime.now(timezone.utc),
        notes=M4_NOTES,
    )
    session.add(ir)
    session.flush()
    for sid in (sid1, sid2):
        sfr = SourceFetchRun(
            ingestion_run_id=ir.id,
            source_id=sid,
            status="success",
            finished_at=datetime.now(timezone.utc),
        )
        session.add(sfr)
        session.flush()
        session.add(
            NormalizedObservation(
                source_id=sid,
                source_fetch_run_id=sfr.id,
                product_id=pid,
                market_scope="community",
                sales_channel="community_direct",
                price_amount=Decimal("12"),
                display_unit_id=uid,
                normalized_price_value=Decimal("12"),
                observed_at=OBS_TS,
                flag_status="ok",
            )
        )
    session.commit()


def test_publish_abort_fewer_than_two_community_sources(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        sid1, _, pid, uid = _pick_sources_product(pg_session)
        ir = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M4_NOTES,
        )
        pg_session.add(ir)
        pg_session.flush()
        sfr = SourceFetchRun(
            ingestion_run_id=ir.id,
            source_id=sid1,
            status="success",
            finished_at=datetime.now(timezone.utc),
        )
        pg_session.add(sfr)
        pg_session.flush()
        pg_session.add(
            NormalizedObservation(
                source_id=sid1,
                source_fetch_run_id=sfr.id,
                product_id=pid,
                market_scope="community",
                sales_channel="community_direct",
                price_amount=Decimal("9"),
                display_unit_id=uid,
                normalized_price_value=Decimal("9"),
                observed_at=OBS_TS,
                flag_status="ok",
            )
        )
        pg_session.commit()

        with pytest.raises(PublishAbortError, match="at least 2 distinct community sources"):
            PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
    finally:
        _cleanup_pub(pg_session)


def test_publish_writes_json_and_html(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        js = json.loads((tmp_path / "public_report.json").read_text(encoding="utf-8"))
        html = (tmp_path / "public_report.html").read_text(encoding="utf-8")
        assert "products" in js
        assert "data_quality" in js
        dq = js["data_quality"]
        assert "raw_extracted_items" in dq
        for k in (
            "normalized",
            "unresolvable",
            "extracted_pending",
            "ignored",
            "ignored_approved_scope_skip",
        ):
            assert k in dq["raw_extracted_items"]
        assert "resolution_pct_norm_vs_unres" in dq
        assert "active_scope_skip_rules" in dq
        assert js.get("index", {}).get("mode") == "rolling_7d"
        assert isinstance(js["products"], list)
        assert len(js["products"]) >= 1
        p0 = js["products"][0]
        for key in (
            "product_id",
            "canonical_name_he",
            "avg_price",
            "sample_size",
            "distinct_sources",
            "normalized_unit",
        ):
            assert key in p0
        assert "<html" in html.lower()
        assert 'dir="rtl"' in html or "dir='rtl'" in html
    finally:
        _cleanup_pub(pg_session)


def test_manifest_staleness_current(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        gen = datetime(2099, 8, 12, 15, 0, tzinfo=timezone.utc)
        ref = datetime(2099, 8, 12, 16, 0, tzinfo=timezone.utc)
        PublishEngine().run(
            pg_session, tmp_path, report_date=PUB_DATE, generated_at=gen, reference_now=ref
        )
        man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert man["staleness_level"] == "current"
    finally:
        _cleanup_pub(pg_session)


def test_manifest_staleness_warning(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        gen = datetime(2099, 8, 1, 12, 0, tzinfo=timezone.utc)
        ref = datetime(2099, 8, 5, 12, 0, tzinfo=timezone.utc)
        PublishEngine().run(
            pg_session, tmp_path, report_date=PUB_DATE, generated_at=gen, reference_now=ref
        )
        man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert man["staleness_level"] == "warning"
    finally:
        _cleanup_pub(pg_session)


def test_manifest_staleness_irrelevant(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        gen = datetime(2099, 8, 1, 12, 0, tzinfo=timezone.utc)
        ref = datetime(2099, 8, 12, 12, 0, tzinfo=timezone.utc)
        PublishEngine().run(
            pg_session, tmp_path, report_date=PUB_DATE, generated_at=gen, reference_now=ref
        )
        man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert man["staleness_level"] == "irrelevant"
    finally:
        _cleanup_pub(pg_session)


def test_publish_manifest_includes_expected_keys(pg_session: Session, tmp_path: Path) -> None:
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        for key in (
            "schema_version",
            "artifact_version",
            "last_published_at",
            "report_date",
            "product_count",
            "staleness_level",
            "staleness_days",
            "community_sources",
            "index_window_days",
            "window_start_date",
            "window_end_date",
            "distinct_community_sources_in_window",
            "upload_base",
            "artifacts",
            "fixed_names",
        ):
            assert key in man, f"Missing manifest key: {key}"
        assert man["schema_version"] == "2.0"
        assert man["community_sources"] >= 2
        assert man["product_count"] >= 1
        assert man["index_window_days"] == 7
        assert "json" in man["artifacts"]
        assert "html" in man["artifacts"]
        assert "body" in man["artifacts"]
        assert "json" in man["fixed_names"]
    finally:
        _cleanup_pub(pg_session)


def test_publish_rolling_two_sources_different_days_in_window(pg_session: Session, tmp_path: Path) -> None:
    """Two community sources contribute on different UTC days inside the 7d window — no daily_aggregate."""
    _cleanup_pub(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        ir = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M4_NOTES,
        )
        pg_session.add(ir)
        pg_session.flush()
        t_early = datetime(2099, 8, 10, 12, 0, tzinfo=timezone.utc)
        t_late = datetime(2099, 8, 12, 12, 0, tzinfo=timezone.utc)
        for sid, ts in ((sid1, t_early), (sid2, t_late)):
            sfr = SourceFetchRun(
                ingestion_run_id=ir.id,
                source_id=sid,
                status="success",
                finished_at=datetime.now(timezone.utc),
            )
            pg_session.add(sfr)
            pg_session.flush()
            pg_session.add(
                NormalizedObservation(
                    source_id=sid,
                    source_fetch_run_id=sfr.id,
                    product_id=pid,
                    market_scope="community",
                    sales_channel="community_direct",
                    price_amount=Decimal("11"),
                    display_unit_id=uid,
                    normalized_price_value=Decimal("11"),
                    observed_at=ts,
                    flag_status="ok",
                )
            )
        pg_session.commit()
        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        js = json.loads((tmp_path / "public_report.json").read_text(encoding="utf-8"))
        assert len(js["products"]) >= 1
    finally:
        _cleanup_pub(pg_session)


def test_publish_rolling_abort_observations_outside_window(pg_session: Session, tmp_path: Path) -> None:
    """Observations exist but outside 7d window ending report_date — not enough sources in window."""
    _cleanup_pub(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        ir = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M4_NOTES,
        )
        pg_session.add(ir)
        pg_session.flush()
        old = datetime(2099, 8, 1, 12, 0, tzinfo=timezone.utc)
        for sid in (sid1, sid2):
            sfr = SourceFetchRun(
                ingestion_run_id=ir.id,
                source_id=sid,
                status="success",
                finished_at=datetime.now(timezone.utc),
            )
            pg_session.add(sfr)
            pg_session.flush()
            pg_session.add(
                NormalizedObservation(
                    source_id=sid,
                    source_fetch_run_id=sfr.id,
                    product_id=pid,
                    market_scope="community",
                    sales_channel="community_direct",
                    price_amount=Decimal("5"),
                    display_unit_id=uid,
                    normalized_price_value=Decimal("5"),
                    observed_at=old,
                    flag_status="ok",
                )
            )
        pg_session.commit()
        with pytest.raises(PublishAbortError, match="7d UTC window"):
            PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
    finally:
        _cleanup_pub(pg_session)


def test_publish_body_fragment_generated(pg_session: Session, tmp_path: Path) -> None:
    """M7: body fragment HTML is generated for WordPress embedding."""
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        summary = PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        body = (tmp_path / "public_report_body.html").read_text(encoding="utf-8")
        assert "sfagent-market-report" in body
        assert "<html" not in body.lower()
        assert "<!DOCTYPE" not in body
        assert "מחירי ירקות אורגניים" in body
        av = summary["artifact_version"]
        versioned = tmp_path / f"public_report_body-{av}.html"
        assert versioned.exists()
    finally:
        _cleanup_pub(pg_session)


def test_publish_versioned_filenames(pg_session: Session, tmp_path: Path) -> None:
    """M7: versioned filenames exist alongside fixed-name copies."""
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        summary = PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        av = summary["artifact_version"]
        for ext in ("json", "html"):
            assert (tmp_path / f"public_report-{av}.{ext}").exists()
            assert (tmp_path / f"public_report.{ext}").exists()
        assert (tmp_path / f"public_report_body-{av}.html").exists()
        assert (tmp_path / "public_report_body.html").exists()
        assert "files" in summary
        assert len(summary["files"]) == 8
    finally:
        _cleanup_pub(pg_session)


def test_manifest_last_good_created(pg_session: Session, tmp_path: Path) -> None:
    """M7: second publish creates manifest_last_good.json from previous manifest."""
    _cleanup_pub(pg_session)
    try:
        _seed_two_community_obs(pg_session)
        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        assert (tmp_path / "manifest.json").exists()
        assert not (tmp_path / "manifest_last_good.json").exists()

        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        assert (tmp_path / "manifest_last_good.json").exists()
        good = json.loads((tmp_path / "manifest_last_good.json").read_text(encoding="utf-8"))
        assert "schema_version" in good
    finally:
        _cleanup_pub(pg_session)
