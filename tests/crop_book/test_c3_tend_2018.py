"""WP-C3 tests — Tend 2018 ingestion (CROP_PLAN + no harvest stats)."""

from __future__ import annotations

import csv
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book


@pytest.fixture
def tend_dir_2018(tmp_path):
    """Create minimal Tend 2018 CSVs matching expected schema."""
    # TASKS.CSV — minimal
    with open(tmp_path / "Tend_2018_TASKS.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Task Type", "Method", "Sub-method", "Plantings Assigned", "Date", "Completed Date"])
        w.writerow(["Transplant", "Transplant", "", "Arugula 12/04/2018", "12/04/2018", "12/04/2018"])

    # GREENHOUSE_PLAN.CSV — minimal
    with open(tmp_path / "Tend_2018_GREENHOUSE_PLAN.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Plantings Name", "Crop", "GH Sow Date", "Days In Greenhouse", "Days to 1st potting up"])
        w.writerow(["Arugula 12/04/2018", "Arugula", "01/01/2018", "68", ""])

    # HARVESTS.CSV — header only (0 data rows)
    with open(tmp_path / "Tend_2018_HARVESTS.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Planting Name", "Crop", "Amount", "Unit", "Outlet Type", "Outlet Name", "Harvest Stage", "Final Harvest"])

    return tmp_path


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, Crop, CropFamily, CropVariety
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    CropTaskTemplate.__table__.create(engine, checkfirst=True)
    Session = sessionmaker(engine)
    with Session() as session:
        fam = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
        session.add(fam)
        session.flush()
        session.add(Crop(name_he="ארוגולה", name_en="Arugula", category="vegetables", family_id=fam.id))
        session.flush()
        yield session


def test_tend_2018_crop_plan_ingest(db_session, tend_dir_2018):
    """import_tend_overlay for year=2018 processes GREENHOUSE_PLAN without errors."""
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay

    summary = import_tend_overlay(db_session, tend_dir_2018, year=2018, dry_run=False)
    # Should not raise; source_value or task rows may be 0 if crop not in TEND_CROP_MAP
    assert summary.year == 2018
    assert summary.harvest_stat_rows_upserted == 0  # HARVESTS=0


def test_tend_2018_no_harvest_stats(db_session, tend_dir_2018):
    """Empty HARVESTS CSV produces 0 harvest_stat rows."""
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay

    try:
        from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat
        CropHarvestStat.__table__.create(db_session.get_bind(), checkfirst=True)
    except Exception:
        pass

    summary = import_tend_overlay(db_session, tend_dir_2018, year=2018, dry_run=False)
    assert summary.harvest_stat_rows_upserted == 0
    assert summary.harvests_aggregated == 0
