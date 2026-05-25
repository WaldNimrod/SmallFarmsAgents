"""Tests for tend_overlay idempotency.

SFA-S003-P002-WP-B3 LOD400 §9. Covers AC-12.
"""
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book

FIXTURE_DIR = Path("tests/crop_book/fixtures/tend_2022")


@pytest.fixture(scope="module")
def idempotency_engine():
    """SQLite in-memory engine with all tables + pre-seeded crops."""
    from sqlalchemy import create_engine
    from organic_market_agent.db.base import Base
    import organic_market_agent.models  # noqa: F401
    import organic_market_agent.crop_book.enrichment_models  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate  # noqa: F401
    from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat  # noqa: F401
    from organic_market_agent.crop_book.models import CropFamily, Crop

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    CropHarvestStat.__table__.create(engine, checkfirst=True)

    from sqlalchemy.orm import Session
    with Session(engine) as session:
        fam = CropFamily(scientific_name="Apiaceae", name_he="סלריים")
        session.add(fam)
        session.flush()
        for name_he, name_en in [
            ("עגבנייה", "Tomatoes"),
            ("גזר", "Carrots"),
            ("סלק", "Beets"),
        ]:
            if not session.query(Crop).filter_by(name_he=name_he).first():
                session.add(Crop(name_he=name_he, name_en=name_en,
                                 category="vegetables", family_id=fam.id))
        session.commit()
    return engine


def test_ac12_twice_import_same_row_count(idempotency_engine):
    """AC-12: running import_tend_overlay twice produces same row counts."""
    from sqlalchemy.orm import Session
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate
    from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    # First import (dry_run=False commits)
    with Session(idempotency_engine) as session:
        import_tend_overlay(session, FIXTURE_DIR, year=2022, dry_run=False)

    # Count rows after first import
    with Session(idempotency_engine) as session:
        task_count_1 = session.query(CropTaskTemplate).filter_by(source="Tend_2022").count()
        harvest_count_1 = session.query(CropHarvestStat).filter_by(source="Tend_2022").count()
        sv_count_1 = session.query(CropVarietySourceValue).filter_by(source="Tend_2022").count()

    # Second import — should upsert (no new rows)
    with Session(idempotency_engine) as session:
        import_tend_overlay(session, FIXTURE_DIR, year=2022, dry_run=False)

    # Count rows after second import
    with Session(idempotency_engine) as session:
        task_count_2 = session.query(CropTaskTemplate).filter_by(source="Tend_2022").count()
        harvest_count_2 = session.query(CropHarvestStat).filter_by(source="Tend_2022").count()
        sv_count_2 = session.query(CropVarietySourceValue).filter_by(source="Tend_2022").count()

    assert task_count_1 == task_count_2, (
        f"Task template count changed: {task_count_1} → {task_count_2}"
    )
    assert harvest_count_1 == harvest_count_2, (
        f"Harvest stat count changed: {harvest_count_1} → {harvest_count_2}"
    )
    assert sv_count_1 == sv_count_2, (
        f"Source value count changed: {sv_count_1} → {sv_count_2}"
    )
