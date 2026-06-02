"""M13 / G11: publish JSON v3 shape, privacy, manifest (mirrors QA mandate checks)."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal
import pytest
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun, NormalizedObservation, Product, Source, SourceFetchRun
from organic_market_agent.publisher import PublishEngine
from organic_market_agent.utils.exceptions import PublishAbortError
from organic_market_agent.publisher.report_details import (
    REPORT_JSON_SOFT_LIMIT_BYTES,
    _sanitize_public_text,
    apply_soft_json_size_limit_to_payload,
    resolve_details_variant,
)

M13_NOTES = "m13_g11_pytest"
PUB_DATE = date(2099, 9, 1)
OBS_TS = datetime(2099, 8, 30, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
def pg_session() -> Session:
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available")

    session = SessionFactory()
    yield session
    session.close()


def _cleanup(session: Session) -> None:
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
        {"tag": M13_NOTES},
    )
    session.execute(
        text(
            """
            DELETE FROM source_fetch_runs
            WHERE ingestion_run_id IN (SELECT id FROM ingestion_runs WHERE notes = :tag)
            """
        ),
        {"tag": M13_NOTES},
    )
    session.execute(text("DELETE FROM ingestion_runs WHERE notes = :tag"), {"tag": M13_NOTES})
    session.commit()


def _pick_two_sources_and_product(session: Session) -> tuple[int, int, Product, int]:
    rows = session.execute(
        sa.select(Source.id).where(Source.is_active.is_(True)).order_by(Source.id).limit(2)
    ).scalars().all()
    if len(rows) < 2:
        pytest.skip("Need at least 2 active sources")
    prod = session.execute(sa.select(Product).where(Product.is_active.is_(True)).limit(1)).scalar_one()
    uid = int(prod.default_measurement_unit_id)
    return int(rows[0]), int(rows[1]), prod, uid


def test_sanitize_public_text_strips_phones() -> None:
    out = _sanitize_public_text("ליצירת קשר 052-331-1376 או +972-52-1234567")
    assert out is not None
    assert "052" not in out
    assert "331" not in out
    assert "972" not in out


def test_resolve_details_variant_mapping() -> None:
    assert (
        resolve_details_variant(
            category="baskets",
            is_basket_product=True,
            market_scope="community",
            display_buckets={"grower"},
        )
        == "basket_csa"
    )
    assert (
        resolve_details_variant(
            category="fruiting_vegetables",
            is_basket_product=False,
            market_scope="community",
            display_buckets={"store"},
        )
        == "store_retail"
    )
    assert (
        resolve_details_variant(
            category="fruiting_vegetables",
            is_basket_product=False,
            market_scope="benchmark",
            display_buckets={"grower"},
        )
        == "chain_benchmark"
    )
    assert (
        resolve_details_variant(
            category="fruiting_vegetables",
            is_basket_product=False,
            market_scope="community",
            display_buckets={"grower"},
        )
        == "grower_price_grid"
    )


def test_g11_privacy_patterns_on_publish_json(pg_session: Session, tmp_path) -> None:
    """T04-style: no SRC###, known farm names, or http(s) URLs in public_report.json."""
    _cleanup(pg_session)
    try:
        sid1, sid2, prod, uid = _pick_two_sources_and_product(pg_session)
        ir = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M13_NOTES,
        )
        pg_session.add(ir)
        pg_session.flush()
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
                    product_id=prod.id,
                    market_scope="community",
                    sales_channel="community_direct",
                    price_amount=Decimal("10"),
                    display_unit_id=uid,
                    normalized_price_value=Decimal("10"),
                    observed_at=OBS_TS,
                    flag_status="ok",
                )
            )
        pg_session.commit()

        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        raw = (tmp_path / "public_report.json").read_text(encoding="utf-8")
        d = json.loads(raw)
        report_str = json.dumps(d, ensure_ascii=False)
        assert not re.findall(r"SRC\d{3}", report_str)
        assert "https://" not in report_str and "http://" not in report_str
        for name in ("חוות שורשים", "טבע שוק"):
            assert name not in report_str

        assert d.get("report_schema_version") == "3.0"
        man = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
        assert man.get("schema_version") == "3.0"

        for p in d["products"]:
            det = p["details"]
            assert det["details_variant"] in (
                "grower_price_grid",
                "basket_csa",
                "store_retail",
                "chain_benchmark",
            )
            assert isinstance(det["source_count"], int)
            ps = det.get("price_series") or []
            if ps:
                assert len(ps) >= 3
                assert len(ps) <= 30
                for pt in ps:
                    assert "d" in pt and "v" in pt
                    assert isinstance(pt["v"], (int, float))
                    assert not isinstance(pt["v"], float) or __import__("math").isfinite(pt["v"])
    finally:
        _cleanup(pg_session)


def test_apply_soft_json_size_limit_trims_series() -> None:
    big_series = [{"d": f"2026-03-{i % 28 + 1:02d}", "v": float(i)} for i in range(40)]
    payload: dict = {"report_schema_version": "3.0", "products": []}
    for j in range(300):
        payload["products"].append(
            {
                "product_id": f"P{j}",
                "details": {
                    "price_series": [dict(x) for x in big_series],
                    "details_variant": "grower_price_grid",
                },
            }
        )
        if len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) > REPORT_JSON_SOFT_LIMIT_BYTES:
            break
    else:
        pytest.skip("could not synthesize payload over soft limit")
    apply_soft_json_size_limit_to_payload(payload, None)
    for p in payload["products"]:
        ps = p.get("details", {}).get("price_series") or []
        assert len(ps) <= 15


def test_g11_privacy_html_artifacts(pg_session: Session, tmp_path) -> None:
    """T05-style: no SRC codes in generated HTML body."""
    _cleanup(pg_session)
    try:
        sid1, sid2, prod, uid = _pick_two_sources_and_product(pg_session)
        ir = IngestionRun(
            run_type="manual",
            status="completed",
            finished_at=datetime.now(timezone.utc),
            notes=M13_NOTES,
        )
        pg_session.add(ir)
        pg_session.flush()
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
                    product_id=prod.id,
                    market_scope="community",
                    sales_channel="community_direct",
                    price_amount=Decimal("11"),
                    display_unit_id=uid,
                    normalized_price_value=Decimal("11"),
                    observed_at=OBS_TS,
                    flag_status="ok",
                )
            )
        pg_session.commit()
        PublishEngine().run(pg_session, tmp_path, report_date=PUB_DATE)
        for fname in ("public_report_body.html", "public_report.html"):
            html = (tmp_path / fname).read_text(encoding="utf-8")
            assert not re.findall(r"SRC\d{3}", html)
    finally:
        _cleanup(pg_session)


def test_g11_basket_products_json_contract_when_published(pg_session: Session, tmp_path) -> None:
    """CSA supplement TB-JSON: basket rows use weekly series cap, csa block keys, privacy on csa blob."""
    has_basket = pg_session.execute(
        sa.select(Product.id).where(Product.category == "baskets", Product.is_active.is_(True)).limit(1)
    ).scalar_one_or_none()
    if has_basket is None:
        pytest.skip("No active basket products in catalog")

    try:
        PublishEngine().run(pg_session, tmp_path)
    except PublishAbortError:
        pytest.skip("Publish aborted (<2 community sources in rolling window)")

    d = json.loads((tmp_path / "public_report.json").read_text(encoding="utf-8"))
    baskets = [p for p in d["products"] if p.get("category") == "baskets"]
    if not baskets:
        pytest.skip("No basket products in published report")

    phone = re.compile(r"(?:0\d{1,2}[-\s]?\d{3}[-\s]?\d{4})|(?:\+972)")
    allowed_csa = {"contents_summary_generalized", "cadence_note", "context_incomplete"}

    for p in baskets:
        det = p["details"]
        assert det["details_variant"] == "basket_csa"
        ps = det.get("price_series") or []
        if ps:
            assert len(ps) >= 3
            assert len(ps) <= 12
            for pt in ps:
                assert "d" in pt and "v" in pt
                assert isinstance(pt["v"], (int, float)) and __import__("math").isfinite(pt["v"])
        csa = det.get("csa")
        if csa is not None:
            assert isinstance(csa, dict)
            assert set(csa.keys()) <= allowed_csa
            assert not phone.search(json.dumps(csa, ensure_ascii=False))
        assert det.get("store") is None
        assert det.get("benchmark") is None

    for p in d["products"]:
        if p.get("category") != "baskets":
            assert p["details"].get("details_variant") != "basket_csa"
