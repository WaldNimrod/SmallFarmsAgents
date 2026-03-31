"""catalog_scope_skip_rules + NormalizerEngine scope_skip stage."""
from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
import sqlalchemy as sa

from organic_market_agent.models import CatalogScopeSkipRule
from organic_market_agent.models.runs import IngestionRun, RawAsset, RawExtractedItem, SourceFetchRun
from organic_market_agent.normalizer import scope_skip as scope_skip_mod
from organic_market_agent.normalizer.engine import NormalizerEngine


def test_scope_skip_matches_prefix_and_contains():
    r_prefix = SimpleNamespace(
        id=1,
        is_active=True,
        match_type="prefix",
        pattern="תרומה",
        category_code="donation",
        display_order=1,
    )
    assert scope_skip_mod._matches(r_prefix, "תרומה למנזר")
    assert not scope_skip_mod._matches(r_prefix, "עגבנייה")

    r_contains = SimpleNamespace(
        id=2,
        is_active=True,
        match_type="contains",
        pattern="מרכך",
        category_code="cleaning",
        display_order=2,
    )
    assert scope_skip_mod._matches(r_contains, "מרכך כביסה מרוכז")


@pytest.mark.parametrize(
    "pat,raw,expect",
    [
        ("18 שח", "18 שח", True),
        ("foo", "bar", False),
    ],
)
def test_scope_skip_exact(pat: str, raw: str, expect: bool):
    r = SimpleNamespace(
        id=3,
        is_active=True,
        match_type="exact",
        pattern=pat,
        category_code="other",
        display_order=3,
    )
    assert scope_skip_mod._matches(r, raw) is expect


def test_normalizer_marks_scope_skip_ignored(db_session):
    from organic_market_agent.models import NormalizerProfile, Source

    src = db_session.scalar(sa.select(Source).where(Source.is_active.is_(True)).limit(1))
    if src is None:
        pytest.skip("No active source")
    np_id = db_session.scalar(
        sa.select(NormalizerProfile.id).where(NormalizerProfile.source_id == src.id).limit(1)
    )
    if np_id is None:
        pytest.skip("No normalizer profile")

    rule = CatalogScopeSkipRule(
        display_order=990,
        category_code="donation",
        match_type="prefix",
        pattern="תרומה-סקופ-טסט",
        notes="pytest scope_skip integration",
        is_active=True,
    )
    db_session.add(rule)
    db_session.flush()

    ir = IngestionRun(run_type="manual", triggered_by="test", status="completed")
    db_session.add(ir)
    db_session.flush()
    sfr = SourceFetchRun(ingestion_run_id=ir.id, source_id=src.id, status="success")
    db_session.add(sfr)
    db_session.flush()
    checksum = uuid.uuid4().hex
    ra = RawAsset(
        source_id=src.id,
        source_fetch_run_id=sfr.id,
        storage_path=f"test/scope_skip_{checksum[:8]}.bin",
        file_type="html",
        checksum_sha256=checksum,
        bytes_size=1,
    )
    db_session.add(ra)
    db_session.flush()
    rei = RawExtractedItem(
        source_fetch_run_id=sfr.id,
        raw_asset_id=ra.id,
        normalizer_profile_id=np_id,
        raw_product_name="תרומה-סקופ-טסט XYZ",
        raw_price_text="1",
        raw_unit_text="kg",
        extraction_status="extracted",
    )
    db_session.add(rei)
    db_session.commit()

    eng = NormalizerEngine()
    counts = eng.run(db_session, ingestion_run_id=ir.id)
    assert counts.get("scope_skipped", 0) >= 1
    db_session.refresh(rei)
    assert rei.extraction_status == "ignored"
    assert rei.ignore_reason_code == "approved_scope_skip"
    assert rei.unresolvable_reason and rei.unresolvable_reason.startswith("approved_scope_skip:donation#")

    # teardown
    db_session.execute(sa.delete(RawExtractedItem).where(RawExtractedItem.id == rei.id))
    db_session.execute(sa.delete(RawAsset).where(RawAsset.id == ra.id))
    db_session.execute(sa.delete(SourceFetchRun).where(SourceFetchRun.id == sfr.id))
    db_session.execute(sa.delete(IngestionRun).where(IngestionRun.id == ir.id))
    db_session.execute(sa.delete(CatalogScopeSkipRule).where(CatalogScopeSkipRule.id == rule.id))
    db_session.commit()
