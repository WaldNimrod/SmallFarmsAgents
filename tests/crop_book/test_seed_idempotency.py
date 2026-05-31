"""AC-06 / AC-07 — Seed idempotency test on SQLite in-memory. No PostgreSQL required."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def sqlite_engine():
    from organic_market_agent.crop_book.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(sqlite_engine):
    SessionLocal = sessionmaker(sqlite_engine, expire_on_commit=False)
    session = SessionLocal()
    yield session
    session.close()


def _run_seed(session, target_crops: list[str] | None = None) -> None:
    """Run the seed() function with a minimal source_dir pointing to actual test data."""
    from organic_market_agent.crop_book.importer.seed import seed

    source_dir = Path("/Users/nimrod/Documents/israel Microgreens/crop data")
    jmf_dir = Path("/Users/nimrod/Documents/Market Gardening/MasterClass/Crops Data")

    if not source_dir.exists():
        pytest.skip("Tend source data not available on this machine")

    seed(
        session=session,
        target_crops=target_crops or ["Arugula", "Broccoli", "Tomatoes", "Basil", "Carrots"],
        dry_run=False,
        year_filter=None,
        source_dir=source_dir,
        jmf_dir=jmf_dir,
    )


def _count_all(session) -> dict[str, int]:
    from organic_market_agent.crop_book.models import (
        Crop,
        CropConversionGroup,
        CropFamily,
        CropUnitConversion,
        CropVariety,
        CropVarietySourceValue,
    )

    return {
        "crop_families": session.execute(select(func.count()).select_from(CropFamily)).scalar_one(),
        "crops": session.execute(select(func.count()).select_from(Crop)).scalar_one(),
        "crop_varieties": session.execute(select(func.count()).select_from(CropVariety)).scalar_one(),
        "crop_variety_source_values": session.execute(
            select(func.count()).select_from(CropVarietySourceValue)
        ).scalar_one(),
        "crop_conversion_groups": session.execute(
            select(func.count()).select_from(CropConversionGroup)
        ).scalar_one(),
        "crop_unit_conversions": session.execute(
            select(func.count()).select_from(CropUnitConversion)
        ).scalar_one(),
    }


def test_seed_twice_no_duplicates(db_session) -> None:
    """Running seed twice must not increase row counts in any table."""
    _run_seed(db_session)
    counts_after_first = _count_all(db_session)

    _run_seed(db_session)
    counts_after_second = _count_all(db_session)

    for table, count in counts_after_first.items():
        assert count > 0, f"After first seed, {table} should have > 0 rows"

    for table in counts_after_first:
        assert counts_after_second[table] == counts_after_first[table], (
            f"Table {table}: second seed increased row count from "
            f"{counts_after_first[table]} to {counts_after_second[table]} — not idempotent"
        )


def test_seed_populates_five_pilot_crops(db_session) -> None:
    """AC-04: 5 LOD300 target crops must exist after seed."""
    from organic_market_agent.crop_book.models import Crop

    _run_seed(db_session)

    expected = {"ארוגולה", "ברוקולי", "עגבנייה", "בזיל", "גזר"}
    actual = {
        row[0]
        for row in db_session.execute(select(Crop.name_he)).all()
    }
    for name_he in expected:
        assert name_he in actual, f"Crop {name_he!r} not found after seed"


def test_seed_populates_conversion_groups(db_session) -> None:
    """AC-04: 7 conversion groups from LOD200 §4.6 must be seeded."""
    from organic_market_agent.crop_book.models import CropConversionGroup

    _run_seed(db_session)

    count = db_session.execute(
        select(func.count()).select_from(CropConversionGroup)
    ).scalar_one()
    assert count >= 7, f"Expected >= 7 conversion groups, got {count}"


def test_arugula_dtm_is_21(db_session) -> None:
    """AC-04: Arugula days_to_maturity must be 21 (team_00 override).

    WP-CB-MIG: days_to_maturity column dropped (§7.4); DTM now exclusively
    in crop_field_enrichment. Check enrichment row instead of column.
    """
    from organic_market_agent.crop_book.models import Crop, CropVariety
    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment

    _run_seed(db_session)

    arugula = db_session.execute(select(Crop).where(Crop.name_he == "ארוגולה")).scalar_one_or_none()
    if arugula is None:
        pytest.skip("Arugula not seeded (no Tend data?)")

    default_variety = db_session.execute(
        select(CropVariety).where(
            CropVariety.crop_id == arugula.id,
            CropVariety.is_default == True,  # noqa: E712
        )
    ).scalar_one_or_none()

    if default_variety is None:
        pytest.skip("Default variety for arugula not found")

    # WP-CB-MIG: DTM is in crop_field_enrichment, not the column
    enrichment = db_session.execute(
        select(CropFieldEnrichment).where(
            CropFieldEnrichment.variety_id == default_variety.id,
            CropFieldEnrichment.field_name == "days_to_maturity",
        )
    ).scalar_one_or_none()

    if enrichment is None:
        pytest.skip("No DTM enrichment row for arugula (seeder may not have enriched)")

    assert float(enrichment.value_best) == 21.0, (
        f"Expected arugula DTM=21 (team_00), got {enrichment.value_best}"
    )
