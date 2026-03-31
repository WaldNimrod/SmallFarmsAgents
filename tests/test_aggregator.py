"""M4 AggregatorEngine and QAEngine tests (PostgreSQL)."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from organic_market_agent.aggregator import AggregatorEngine, QAEngine
from organic_market_agent.models import (
    DailyAggregate,
    IngestionRun,
    NormalizedObservation,
    PipelineAlert,
    Product,
    Source,
    SourceFetchRun,
    WeeklySnapshot,
)

M4_NOTES = "m4_pytest"
TEST_DATE = date(2099, 6, 3)
OBS_TS = datetime(2099, 6, 3, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def pg_session() -> Session:
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available for M4 tests")

    session = SessionFactory()
    yield session
    session.close()


def _cleanup_m4(session: Session) -> None:
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
    session.execute(text("DELETE FROM daily_aggregates WHERE aggregate_date = :d"), {"d": TEST_DATE})
    session.execute(
        text(
            """
            DELETE FROM weekly_snapshots
            WHERE week_start_date <= :d AND week_end_date >= :d
            """
        ),
        {"d": TEST_DATE},
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
    session.execute(
        text(
            "DELETE FROM pipeline_alerts WHERE message LIKE '[AGG_PRICE_RULE%' "
            "AND message LIKE :dfrag"
        ),
        {"dfrag": f"%{TEST_DATE.isoformat()}%"},
    )
    session.commit()


def _pick_sources_product(session: Session) -> tuple[int, int, int, int]:
    rows = session.execute(
        sa.select(Source.id).where(Source.is_active.is_(True)).order_by(Source.id).limit(2)
    ).scalars().all()
    if len(rows) < 2:
        pytest.skip("Need at least 2 active sources")
    s1, s2 = int(rows[0]), int(rows[1])
    prod = session.execute(sa.select(Product.id, Product.default_measurement_unit_id).limit(1)).one()
    return s1, s2, int(prod[0]), int(prod[1])


def _pick_sources_for_qa001(session: Session) -> tuple[list[int], int, int]:
    """Eleven distinct sources: ten at 10 NIS and one at 500 exceed mean+3σ (same calendar day)."""
    rows = session.execute(
        sa.select(Source.id).where(Source.is_active.is_(True)).order_by(Source.id).limit(11)
    ).scalars().all()
    if len(rows) < 11:
        pytest.skip("Need at least 11 active sources for QA001 outlier test")
    ids = [int(x) for x in rows]
    prod = session.execute(sa.select(Product.id, Product.default_measurement_unit_id).limit(1)).one()
    return ids, int(prod[0]), int(prod[1])


def _make_run(session: Session) -> tuple[int, list[int]]:
    ir = IngestionRun(
        run_type="manual",
        status="completed",
        finished_at=datetime.now(timezone.utc),
        notes=M4_NOTES,
    )
    session.add(ir)
    session.flush()
    return ir.id, []


def _add_fetch(session: Session, ingestion_run_id: int, source_id: int) -> int:
    sfr = SourceFetchRun(
        ingestion_run_id=ingestion_run_id,
        source_id=source_id,
        status="success",
        finished_at=datetime.now(timezone.utc),
    )
    session.add(sfr)
    session.flush()
    return int(sfr.id)


def _add_obs(
    session: Session,
    *,
    sfr_id: int,
    source_id: int,
    product_id: int,
    unit_id: int,
    price: Decimal,
) -> None:
    session.add(
        NormalizedObservation(
            source_id=source_id,
            source_fetch_run_id=sfr_id,
            product_id=product_id,
            market_scope="community",
            sales_channel="community_direct",
            price_amount=price,
            display_unit_id=unit_id,
            normalized_price_value=price,
            observed_at=OBS_TS,
            flag_status="ok",
        )
    )


def test_aggregator_empty_day_returns_zero_counts(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        empty = date(2099, 1, 1)
        out = AggregatorEngine().run(pg_session, empty)
        assert out == {"created": 0, "updated": 0}
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_publish_threshold_false_single_source(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr = _add_fetch(pg_session, rid, sid1)
        _add_obs(pg_session, sfr_id=fr, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("12"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        row = pg_session.execute(
            sa.select(DailyAggregate).where(
                DailyAggregate.aggregate_date == TEST_DATE,
                DailyAggregate.product_id == pid,
            )
        ).scalar_one_or_none()
        assert row is not None
        assert row.meets_publish_threshold is False
        assert row.distinct_sources == 1
        assert row.sample_size == 2
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_two_source_wide_spread_suppresses_publish_and_alerts(
    pg_session: Session,
) -> None:
    """Per-source averages 10 vs 30 → >100% spread → meets_publish_threshold False + warning alert."""
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr1 = _add_fetch(pg_session, rid, sid1)
        fr2 = _add_fetch(pg_session, rid, sid2)
        _add_obs(pg_session, sfr_id=fr1, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr2, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("30"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        row = pg_session.execute(
            sa.select(DailyAggregate).where(
                DailyAggregate.aggregate_date == TEST_DATE,
                DailyAggregate.product_id == pid,
            )
        ).scalar_one()
        assert row.meets_publish_threshold is False
        assert row.distinct_sources == 2
        alert = pg_session.execute(
            sa.select(PipelineAlert).where(PipelineAlert.message.like("[AGG_PRICE_RULE%"))
        ).scalar_one_or_none()
        assert alert is not None
        assert "two_source_price_spread_gt_100pct" in alert.message
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_second_run_same_suppression_no_duplicate_alert(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr1 = _add_fetch(pg_session, rid, sid1)
        fr2 = _add_fetch(pg_session, rid, sid2)
        _add_obs(pg_session, sfr_id=fr1, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr2, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("30"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        n1 = pg_session.execute(
            sa.select(sa.func.count()).select_from(PipelineAlert).where(
                PipelineAlert.message.like("[AGG_PRICE_RULE%")
            )
        ).scalar_one()
        AggregatorEngine().run(pg_session, TEST_DATE)
        n2 = pg_session.execute(
            sa.select(sa.func.count()).select_from(PipelineAlert).where(
                PipelineAlert.message.like("[AGG_PRICE_RULE%")
            )
        ).scalar_one()
        assert int(n1) == 1
        assert int(n2) == 1
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_publish_threshold_true_two_sources(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr1 = _add_fetch(pg_session, rid, sid1)
        fr2 = _add_fetch(pg_session, rid, sid2)
        _add_obs(pg_session, sfr_id=fr1, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr2, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("14"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        row = pg_session.execute(
            sa.select(DailyAggregate).where(
                DailyAggregate.aggregate_date == TEST_DATE,
                DailyAggregate.product_id == pid,
            )
        ).scalar_one()
        assert row.meets_publish_threshold is True
        assert row.distinct_sources == 2
        assert row.sample_size == 2
        assert row.unweighted_avg_price == Decimal("12.0000")
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_upsert_second_run_updates(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr1 = _add_fetch(pg_session, rid, sid1)
        fr2 = _add_fetch(pg_session, rid, sid2)
        _add_obs(pg_session, sfr_id=fr1, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr2, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("14"))
        pg_session.commit()

        first = AggregatorEngine().run(pg_session, TEST_DATE)
        second = AggregatorEngine().run(pg_session, TEST_DATE)
        assert first["created"] >= 1
        assert second["updated"] >= 1
        assert second["created"] == 0
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_weekly_snapshot_rollup(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr1 = _add_fetch(pg_session, rid, sid1)
        fr2 = _add_fetch(pg_session, rid, sid2)
        _add_obs(pg_session, sfr_id=fr1, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("10"))
        _add_obs(pg_session, sfr_id=fr2, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("14"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        week_start = TEST_DATE - timedelta(days=TEST_DATE.weekday())
        week_end = week_start + timedelta(days=6)
        ws = pg_session.execute(
            sa.select(WeeklySnapshot).where(
                WeeklySnapshot.product_id == pid,
                WeeklySnapshot.week_start_date == week_start,
            )
        ).scalar_one_or_none()
        assert ws is not None
        assert ws.week_end_date == week_end
        assert ws.sample_size >= 2
    finally:
        _cleanup_m4(pg_session)


def test_aggregator_stddev_null_when_sample_size_one(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, _, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr = _add_fetch(pg_session, rid, sid1)
        _add_obs(pg_session, sfr_id=fr, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("7"))
        pg_session.commit()

        AggregatorEngine().run(pg_session, TEST_DATE)
        row = pg_session.execute(
            sa.select(DailyAggregate).where(
                DailyAggregate.aggregate_date == TEST_DATE,
                DailyAggregate.product_id == pid,
            )
        ).scalar_one()
        assert row.sample_size == 1
        assert row.stddev_price is None
    finally:
        _cleanup_m4(pg_session)


def test_qa003_duplicate_day_product_source(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, _, pid, uid = _pick_sources_product(pg_session)
        rid, _ = _make_run(pg_session)
        fr = _add_fetch(pg_session, rid, sid1)
        _add_obs(pg_session, sfr_id=fr, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("5"))
        _add_obs(pg_session, sfr_id=fr, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("6"))
        pg_session.commit()

        msgs = QAEngine().run(pg_session, rid)
        assert any("QA003" in m for m in msgs)
    finally:
        _cleanup_m4(pg_session)


def test_qa001_outlier_high_price(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        source_ids, pid, uid = _pick_sources_for_qa001(pg_session)
        rid, _ = _make_run(pg_session)
        for sid in source_ids[:-1]:
            fr = _add_fetch(pg_session, rid, sid)
            _add_obs(
                pg_session,
                sfr_id=fr,
                source_id=sid,
                product_id=pid,
                unit_id=uid,
                price=Decimal("10"),
            )
        last = source_ids[-1]
        fr_last = _add_fetch(pg_session, rid, last)
        _add_obs(
            pg_session,
            sfr_id=fr_last,
            source_id=last,
            product_id=pid,
            unit_id=uid,
            price=Decimal("500"),
        )
        pg_session.commit()

        msgs = QAEngine().run(pg_session, rid)
        assert any("QA001" in m for m in msgs)
    finally:
        _cleanup_m4(pg_session)


def test_qa002_missing_source_after_previous_success(pg_session: Session) -> None:
    _cleanup_m4(pg_session)
    try:
        sid1, sid2, pid, uid = _pick_sources_product(pg_session)
        ir1 = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M4_NOTES,
        )
        pg_session.add(ir1)
        pg_session.flush()
        fr_a = _add_fetch(pg_session, ir1.id, sid1)
        fr_b = _add_fetch(pg_session, ir1.id, sid2)
        _add_obs(pg_session, sfr_id=fr_a, source_id=sid1, product_id=pid, unit_id=uid, price=Decimal("1"))
        _add_obs(pg_session, sfr_id=fr_b, source_id=sid2, product_id=pid, unit_id=uid, price=Decimal("2"))
        pg_session.commit()

        ir2 = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M4_NOTES,
        )
        pg_session.add(ir2)
        pg_session.flush()
        _add_fetch(pg_session, ir2.id, sid1)
        pg_session.commit()

        msgs = QAEngine().run(pg_session, ir2.id)
        assert any("QA002" in m and str(sid2) in m for m in msgs)
    finally:
        _cleanup_m4(pg_session)
