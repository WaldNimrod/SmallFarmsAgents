"""Integration tests for enrichment_runner.py — SFA-S003-P002-WP-A LOD400 §17 Step 10.

Requires live PostgreSQL (port 5433).  Tests use the conftest db_session fixture
and perform real DB round-trips to validate run_enrichment() end-to-end.
"""

from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def enrichment_session(db_session):
    """Wrap db_session for enrichment tests — rolls back after each test."""
    yield db_session
    db_session.rollback()


def test_run_enrichment_returns_summary(enrichment_session) -> None:
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

    summary = run_enrichment(enrichment_session, dry_run=True)
    assert summary.variety_count >= 0
    assert summary.field_count >= 0
    assert summary.outlier_count >= 0
    assert summary.high_confidence_count >= 0


def test_run_enrichment_dry_run_writes_nothing(enrichment_session) -> None:
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment

    before_count = enrichment_session.query(CropFieldEnrichment).count()
    run_enrichment(enrichment_session, dry_run=True)
    enrichment_session.flush()
    after_count = enrichment_session.query(CropFieldEnrichment).count()

    assert before_count == after_count, "dry_run=True must not write any rows"


def test_run_enrichment_upserts_field_consensus(enrichment_session) -> None:
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.models import CropVariety

    # Find a variety that has source values
    from organic_market_agent.crop_book.models import CropVarietySourceValue
    sv = enrichment_session.query(CropVarietySourceValue).filter(
        CropVarietySourceValue.value_numeric.isnot(None)
    ).first()

    if sv is None:
        pytest.skip("No numeric source values in DB — run seed first")

    variety_id = sv.variety_id

    run_enrichment(enrichment_session, variety_ids=[variety_id], dry_run=False)
    enrichment_session.flush()

    enrichment_rows = (
        enrichment_session.query(CropFieldEnrichment)
        .filter_by(variety_id=variety_id)
        .all()
    )

    # At least one enrichment row should exist
    assert len(enrichment_rows) > 0, (
        f"No enrichment rows written for variety_id={variety_id}"
    )

    for row in enrichment_rows:
        assert row.value_best is not None
        assert row.source_count > 0
        assert row.computed_at is not None
        assert row.winning_source_class is not None


def test_run_enrichment_idempotent(enrichment_session) -> None:
    """Running enrichment twice should produce the same result (upsert semantics)."""
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    sv = enrichment_session.query(CropVarietySourceValue).filter(
        CropVarietySourceValue.value_numeric.isnot(None)
    ).first()
    if sv is None:
        pytest.skip("No numeric source values in DB")

    variety_id = sv.variety_id

    run_enrichment(enrichment_session, variety_ids=[variety_id], dry_run=False)
    enrichment_session.flush()
    count_1 = (
        enrichment_session.query(CropFieldEnrichment)
        .filter_by(variety_id=variety_id)
        .count()
    )

    run_enrichment(enrichment_session, variety_ids=[variety_id], dry_run=False)
    enrichment_session.flush()
    count_2 = (
        enrichment_session.query(CropFieldEnrichment)
        .filter_by(variety_id=variety_id)
        .count()
    )

    assert count_1 == count_2, "Second run should not create duplicate rows"


def test_run_enrichment_ex_override_wins(enrichment_session) -> None:
    """A variety with a team_00 EX source value must get confidence_score=1.0000."""
    from organic_market_agent.crop_book.constants import TEAM00_DTM_OVERRIDES
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
    from organic_market_agent.crop_book.models import Crop, CropVariety, CropVarietySourceValue

    if not TEAM00_DTM_OVERRIDES:
        pytest.skip("No TEAM00_DTM_OVERRIDES defined in constants")

    name_he = next(iter(TEAM00_DTM_OVERRIDES))

    variety = (
        enrichment_session.query(CropVariety)
        .join(Crop, CropVariety.crop_id == Crop.id)
        .filter(Crop.name_he == name_he, CropVariety.is_default == True)
        .first()
    )
    if variety is None:
        pytest.skip(f"No default variety for {name_he!r} — run seed first")

    # Check if there's a team_00 source value
    ex_sv = (
        enrichment_session.query(CropVarietySourceValue)
        .filter_by(variety_id=variety.id, source="team_00")
        .first()
    )
    if ex_sv is None:
        pytest.skip(f"No team_00 source value for {name_he!r}")

    run_enrichment(enrichment_session, variety_ids=[variety.id], dry_run=False)
    enrichment_session.flush()

    row = (
        enrichment_session.query(CropFieldEnrichment)
        .filter_by(variety_id=variety.id, field_name="days_to_maturity")
        .first()
    )
    assert row is not None
    assert row.confidence_score == Decimal("1.0000")
    assert row.winning_source_class == "EX"
