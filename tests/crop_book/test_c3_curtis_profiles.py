"""WP-C3 tests — Curtis Stone L40 master chart importer."""

from __future__ import annotations

import openpyxl
import pytest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

pytestmark = pytest.mark.crop_book


@pytest.fixture
def db_session(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from organic_market_agent.crop_book.models import Base, Crop, CropFamily, CropVariety
    from organic_market_agent.crop_book import enrichment_models as _em  # noqa: F401

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    with Session() as session:
        fam = CropFamily(scientific_name="Asteraceae", name_he="מורכבים")
        session.add(fam)
        session.flush()
        # Seed crops that appear in Curtis L40
        crops = [
            ("ארוגולה", "Arugula"),
            ("תרד", "Spinach"),
            ("קייל", "Kale"),
            ("פלפל", "Peppers"),
            ("עגבנייה", "Tomatoes"),
            ("גזר", "Carrots"),
            ("בזיל", "Basil"),
            ("צנונית", "Radish"),
            ("חסה", "Lettuce"),
        ]
        for he, en in crops:
            crop = Crop(name_he=he, name_en=en, category="vegetables", family_id=fam.id)
            session.add(crop)
        session.flush()
        yield session


@pytest.fixture
def mock_xlsx(tmp_path):
    """Create a minimal L40-like XLSX fixture."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet 1 - Master Chart-1"
    ws.append([
        "Crop", "Avg DTM from seed date", "Available for harvest", "Crop Type",
        "CVR5/5", "Quick or Steady", "DS/TR", "Bed Size", "Walkway width",
        "When to DS", "When to TRN", "Last Field Plant Date", "Last GH Plant Date",
        "Jang Roller", "EW Plate", "Rows/Bed", "TRN in row spacing inches",
        "Cell flat", "# days in cell", "Plugs/25' bed", "Plants/Foot",
        "Seed per 25' bed ML", "Seed per row foot ML", "Seed per 25' bed Grm",
        "Oz's", "Avg Yield/25' bed total", "Avg Yield/ Cut", "Avg Yield/ Ft.", "Notes",
    ])
    ws.append(["Arugula", 35, "early spring", "greens", 5, "Q", "ds", 25, '6"', "May 15", None, None, None, "YYJ24", "-", 9, None, None, None, None, None, None, None, None, None, 30, None, None, "notes"])
    ws.append(["Spinach", 40, "spring", "greens", 4, "S", "ds", 25, '6"', "Mar-Sep", None, None, None, "-", "-", 4, None, None, None, None, None, None, None, None, None, 25, None, None, None])
    ws.append(["Kale", 60, "summer", "greens", 4, "S", "tr", 25, '6"', None, "Mar-Aug", None, None, "-", "-", 3, 12, None, None, None, None, None, None, None, None, 20, None, None, None])
    path = tmp_path / "L40_test.xlsx"
    wb.save(path)
    return path


def test_parse_dtm_row(db_session, mock_xlsx):
    """L40 importer upserts days_to_maturity for known crops."""
    from organic_market_agent.crop_book.importer.urban_farmer.curtis_profiles_importer import import_all
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    summary = import_all(db_session, xlsx_path=mock_xlsx)
    assert summary.rows_upserted >= 1

    sv_rows = db_session.query(CropVarietySourceValue).filter_by(
        field_name="days_to_maturity", source="OP:CurtisStone"
    ).all()
    assert len(sv_rows) >= 1
    dtm_values = {r.value_numeric for r in sv_rows}
    assert Decimal("35") in dtm_values  # Arugula DTM


def test_parse_planting_method(db_session, mock_xlsx):
    """DS/TR column maps to correct planting_method values."""
    from organic_market_agent.crop_book.importer.urban_farmer.curtis_profiles_importer import import_all
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    import_all(db_session, xlsx_path=mock_xlsx)

    pm_rows = db_session.query(CropVarietySourceValue).filter_by(
        field_name="planting_method", source="OP:CurtisStone"
    ).all()
    pm_values = {r.value_text for r in pm_rows}
    # Arugula and Spinach are 'ds' → direct_sow; Kale is 'tr' → transplant
    assert "direct_sow" in pm_values
    assert "transplant" in pm_values


def test_idempotency(db_session, mock_xlsx):
    """Running import_all twice produces same row count."""
    from organic_market_agent.crop_book.importer.urban_farmer.curtis_profiles_importer import import_all
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    import_all(db_session, xlsx_path=mock_xlsx)
    count_first = db_session.query(CropVarietySourceValue).filter_by(source="OP:CurtisStone").count()

    import_all(db_session, xlsx_path=mock_xlsx)
    count_second = db_session.query(CropVarietySourceValue).filter_by(source="OP:CurtisStone").count()

    assert count_first == count_second, "Second run should not add duplicate rows"
