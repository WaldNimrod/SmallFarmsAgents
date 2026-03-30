"""Unit tests for M3 normalizer stages and engine (see MANDATE_M3_NORMALIZER_ENGINE)."""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from organic_market_agent.models import (
    IngestionRun,
    NormalizerProfile,
    ProductAlias,
    RawAsset,
    RawExtractedItem,
    Source,
    SourceFetchRun,
)
from organic_market_agent.normalizer import (
    alias_resolver,
    basket_handler,
    confidence as conf_mod,
    organic_flag,
    price_normalizer,
    price_parser,
    quantity_parser,
    unit_resolver,
)
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.normalizer.engine import NormalizerEngine


def _ctx(**kwargs) -> NormContext:
    defaults: dict = dict(
        raw_item_id=1,
        source_id=1,
        source_fetch_run_id=1,
        normalizer_profile_id=None,
        raw_product_name=None,
        raw_price_text=None,
        raw_unit_text=None,
        raw_quantity_text=None,
    )
    defaults.update(kwargs)
    return NormContext(**defaults)


# --- price_parser ---


def test_price_parser_simple_integer():
    ctx = _ctx(raw_price_text="18")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("18.0000")
    assert result.stage_failed is None


def test_price_parser_with_shekel_sign():
    ctx = _ctx(raw_price_text="₪22.50")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("22.5000")


def test_price_parser_comma_decimal():
    ctx = _ctx(raw_price_text="15,5")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("15.5000")


def test_price_parser_empty_fails():
    ctx = _ctx(raw_price_text=None)
    result = price_parser.run(ctx, MagicMock())
    assert result.stage_failed == "price_parse"


def test_price_parser_returns_decimal_not_float():
    ctx = _ctx(raw_price_text="12.5")
    result = price_parser.run(ctx, MagicMock())
    assert isinstance(result.price_amount, Decimal)


# --- quantity_parser ---


def test_quantity_parser_divides_price():
    ctx = _ctx(raw_quantity_text="3")
    ctx.price_amount = Decimal("30.0000")
    result = quantity_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("10.0000")


def test_quantity_parser_qty_1_no_change():
    ctx = _ctx(raw_quantity_text="1")
    ctx.price_amount = Decimal("20.0000")
    result = quantity_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("20.0000")


# --- basket_handler ---


def test_basket_handler_clears_normalized_fields():
    ctx = _ctx()
    ctx.is_basket_product = True
    ctx.normalized_price_value = Decimal("50.0000")
    ctx.normalized_unit_id = 1
    ctx.normalization_method = "direct"
    result = basket_handler.run(ctx, MagicMock())
    assert result.normalized_price_value is None
    assert result.normalized_unit_id is None
    assert result.normalization_method is None


def test_basket_handler_non_basket_unchanged():
    ctx = _ctx()
    ctx.is_basket_product = False
    ctx.normalized_price_value = Decimal("15.0000")
    result = basket_handler.run(ctx, MagicMock())
    assert result.normalized_price_value == Decimal("15.0000")


# --- confidence ---


def test_confidence_perfect_resolution():
    ctx = _ctx()
    ctx.normalization_method = "direct"
    score = conf_mod.calculate(ctx)
    assert score == Decimal("1.00")


def test_confidence_penalty_for_fallback():
    ctx = _ctx()
    ctx.resolution_notes = ["unit_fallback_to_product_default"]
    ctx.normalization_method = "direct"
    score = conf_mod.calculate(ctx)
    assert score == Decimal("0.90")


def test_confidence_minimum_floor():
    ctx = _ctx()
    ctx.resolution_notes = [
        "unit_fallback_to_product_default",
        "alias_contains_match:x",
    ]
    ctx.normalization_method = "unresolvable"
    score = conf_mod.calculate(ctx)
    assert score >= Decimal("0.10")


# --- organic_flag ---


def test_organic_flag_from_payload_json():
    ctx = _ctx(raw_product_name="tomato", raw_payload_json={"note": "organic fresh"})
    result = organic_flag.run(ctx, MagicMock())
    assert result.is_organic_claimed is True


# --- alias_resolver (DB) ---


@pytest.fixture
def db_session():
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available for integration tests")

    with SessionFactory() as session:
        yield session


def test_alias_resolver_empty_name_fails():
    ctx = _ctx(raw_product_name=None)
    result = alias_resolver.run(ctx, MagicMock())
    assert result.stage_failed == "alias"


def test_alias_resolver_exact_match(db_session):
    pa = db_session.scalar(
        sa.select(ProductAlias)
        .where(ProductAlias.is_active.is_(True))
        .where(ProductAlias.alias_text_normalized.isnot(None))
        .limit(1)
    )
    if pa is None:
        pytest.skip("No product_aliases in DB")
    sid = pa.source_id if pa.source_id is not None else 1
    src = db_session.get(Source, sid)
    if src is None:
        pytest.skip("Alias source missing")
    ctx = _ctx(
        source_id=sid,
        raw_product_name=pa.alias_text,
    )
    result = alias_resolver.run(ctx, db_session)
    assert result.stage_failed is None
    assert result.product_id == pa.product_id


# --- unit_resolver + engine (DB) ---


def test_unit_resolver_builtin_kg(db_session):
    pa = db_session.scalar(
        sa.select(ProductAlias).where(ProductAlias.is_active.is_(True)).limit(1)
    )
    if pa is None:
        pytest.skip("No product_aliases in DB")
    sid = pa.source_id if pa.source_id is not None else 1
    if db_session.get(Source, sid) is None:
        pytest.skip("No source")
    ctx = _ctx(
        source_id=sid,
        product_id=pa.product_id,
        raw_unit_text='ק"ג',
    )
    result = unit_resolver.run(ctx, db_session)
    assert result.display_unit_id is not None


def test_normalizer_engine_resolves_one_row(db_session):
    # Use any active alias — global (source_id=None) or source-scoped.
    pa = db_session.scalar(
        sa.select(ProductAlias)
        .where(ProductAlias.is_active.is_(True))
        .limit(1)
    )
    if pa is None:
        pytest.skip("No product aliases in DB for integration test")

    # If alias is global (source_id=None), pick any active source.
    source_id = pa.source_id
    if source_id is None:
        source_id = db_session.scalar(
            sa.select(Source.id).where(Source.is_active.is_(True)).limit(1)
        )
    if source_id is None:
        pytest.skip("No active source in DB")

    assert source_id is not None
    np_id = db_session.scalar(
        sa.select(NormalizerProfile.id).where(NormalizerProfile.source_id == source_id)
    )
    ir = IngestionRun(run_type="manual", triggered_by="test", sources_total=1)
    db_session.add(ir)
    db_session.flush()
    sfr = SourceFetchRun(
        ingestion_run_id=ir.id,
        source_id=source_id,
        status="success",
    )
    db_session.add(sfr)
    db_session.flush()
    checksum = uuid.uuid4().hex
    ra = RawAsset(
        source_id=source_id,
        source_fetch_run_id=sfr.id,
        storage_path=f"test/normalizer_engine_{checksum[:8]}.bin",
        file_type="html",
        checksum_sha256=checksum,
        bytes_size=10,
    )
    db_session.add(ra)
    db_session.flush()
    rei = RawExtractedItem(
        source_fetch_run_id=sfr.id,
        raw_asset_id=ra.id,
        normalizer_profile_id=np_id,
        raw_product_name=pa.alias_text,
        raw_price_text="9.99",
        raw_unit_text="kg",
        extraction_status="extracted",
    )
    db_session.add(rei)
    db_session.commit()

    eng = NormalizerEngine()
    counts = eng.run(db_session, ingestion_run_id=ir.id)
    assert counts["resolved"] >= 1
    db_session.refresh(rei)
    assert rei.extraction_status == "normalized"


def test_price_normalizer_direct_when_no_conversion(db_session):
    pa = db_session.scalar(sa.select(ProductAlias).where(ProductAlias.is_active.is_(True)).limit(1))
    if pa is None:
        pytest.skip("No product_aliases in DB")
    from organic_market_agent.models import Product

    prod = db_session.get(Product, pa.product_id)
    if prod is None:
        pytest.skip("No product")
    ctx = _ctx(
        product_id=prod.id,
        raw_price_text="5",
        price_amount=Decimal("5.0000"),
        display_unit_id=prod.default_measurement_unit_id,
        is_basket_product=False,
    )
    result = price_normalizer.run(ctx, db_session)
    assert result.normalization_method == "direct"
    assert result.normalized_price_value == Decimal("5.0000")


# --- quarantine filter ---


def test_normalizer_skips_quarantined_items(db_session):
    """NormalizerEngine must not process items with is_quarantined=True."""
    # Insert an ingestion run + fetch run + asset + ONE quarantined item in a clean transaction.
    src = db_session.scalar(
        sa.select(Source).where(Source.is_active.is_(True)).limit(1)
    )
    if src is None:
        pytest.skip("No active source in DB")

    ir = IngestionRun(run_type="manual", status="completed")
    db_session.add(ir)
    db_session.flush()

    sfr = SourceFetchRun(
        ingestion_run_id=ir.id,
        source_id=src.id,
        status="success",
    )
    db_session.add(sfr)
    db_session.flush()

    asset = RawAsset(
        source_id=src.id,
        source_fetch_run_id=sfr.id,
        storage_path="/tmp/test_quarantine.html",
        checksum_sha256="abc" + uuid.uuid4().hex,
        file_type="html",
        bytes_size=0,
    )
    db_session.add(asset)
    db_session.flush()

    item = RawExtractedItem(
        source_fetch_run_id=sfr.id,
        raw_asset_id=asset.id,
        raw_product_name="quarantined product",
        raw_price_text="9.99",
        extraction_status="extracted",
        is_quarantined=True,
    )
    db_session.add(item)
    db_session.flush()

    engine = NormalizerEngine()
    counts = engine.run(db_session, ingestion_run_id=ir.id)

    # Item must remain 'extracted' — normalizer should not have touched it
    db_session.refresh(item)
    assert item.extraction_status == "extracted", (
        "Quarantined item must not be normalized"
    )
    assert counts["resolved"] == 0
    assert counts["unresolvable"] == 0


def test_print_cycle_metrics_no_crash(db_session):
    """_print_cycle_metrics must not raise even when there are zero matching rows."""
    from organic_market_agent.normalizer.run_normalizer import _print_cycle_metrics

    # Should complete without exception, printing zeros
    _print_cycle_metrics(db_session, ingestion_run_id=999999)
