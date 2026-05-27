"""WP-C3 tests — FRANCHI seed catalog importer (L06 sheet 2)."""

from __future__ import annotations

import openpyxl
import pytest
from pathlib import Path

pytestmark = pytest.mark.crop_book


@pytest.fixture
def db_session():
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
        for he, en in [("חסה", "Lettuce"), ("קישוא", "Zucchini"), ("פלפל חריף", "Hot Pepper"),
                       ("דלעת", "Squash"), ("סלק", "Beet"), ("בזיל", "Basil"),
                       ("שמיר", "Dill"), ("פטרוזיליה", "Parsley"), ("פטרוזיליה שורש", "Parsley Root"),
                       ("רוקט", "Arugula"), ("מנגולד", "Chard"), ("צנונית", "Radish")]:
            session.add(Crop(name_he=he, name_en=en, category="vegetables", family_id=fam.id))
        session.flush()
        yield session


@pytest.fixture
def franchi_xlsx(tmp_path):
    """Create a FRANCHI-like XLSX fixture with 27 variety rows."""
    path = tmp_path / "L06_test.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "גיליון1"
    # Create the second sheet גיליון2
    ws2 = wb.create_sheet("גיליון2")
    ws2.append(["מין", "זן", "קוד", "אריזה", "כמות"])
    varieties = [
        ("חסה", "LETTUCE BIONDA (78-4)", "(78-4)", "שקית", 1),
        ("חסה", "LETTUCE BIONDA RICCIOLINA", "(78-1)", "שקית", 1),
        ("חסה", "LETTUCE GENTILINA (78-28)", "(78-28)", "שקית", 1),
        ("חסה", "LETTUCE RESISTENTE (79-18)", "(79-18)", "שקית", 1),
        ("חסה", "LETTUCE REGINA D'ESTATE (79-15B)", "(79-15B)", "שקית", 1),
        ("חסה", "LETTUCE MARAVILLA (79-72)", "(79-72)", "שקית", 1),
        ("חסה", "LETTUCE LOLLO ROSSA (78-17)", "(78-17)", "שקית", 1),
        ("קישוא", "ZUCCHINI GOLD RUSH (146-45)", "(146-45)", "שקית", 1),
        ("קישוא", "ZUCCHINI CUSTARD (146-49)", "(146-49)", "שקית", 1),
        ("קישוא", "ZUCHETTA SERPENT (146-43)", "(146-43)", "שקית", 1),
        ("פלפל חריף", "PEPPER PADRON (97-38)", "(97-38)", "שקית", 1),
        ("דלעת", "WINTER SQUASH LUNGA (145-12)", "(145-12)", "שקית", 1),
        ("סלק", "BEET CHIOGGIA (11-13)", "(11-13)", "שקית", 1),
        ("בזיל", "BASIL BOLLOSO (13-8)", "(13-8)", "שקית", 1),
        ("בזיל", "BASIL ITALIANO (13-2B)", "(13-2B)", "שקית", 1),
        ("שמיר", "Dill (7-1)", "(7-1)", "שקית", 1),
        ("פטרוזיליה", "Parsley Gigante (108-2B)", "(108-2B)", "שקית", 1),
        ("פטרוזיליה", "Parsley Nano (108-3)", "(108-3)", "שקית", 1),
        ("פטרוזיליה שורש", "Parsley Root Berliner (108-4)", "(108-4)", "שקית", 1),
        ("רוקט", "Arugula Selvatica (115-5B)", "(115-5B)", "שקית", 1),
        ("רוקט", "Arugula Olive Leaf", "(115-4)", "שקית", 1),
        ("רוקט", "Arugula Cultivated (115-1B)", "(115-1B)", "שקית", 1),
        ("רוקט", "Arugula Ortolani (115-3)", "(115-3)", "שקית", 1),
        ("מנגולד", "Chard Verde (14-3B)", "(14-3B)", "שקית", 1),
        ("צנונית", "Radish Gaudry 2", "(112-3)", "שקית", 1),
        ("צנונית", "Radish Zlata", "(112-36)", "שקית", 1),
        ("צנונית", "Radish Flamboyant 3", "(112-25)", "שקית", 1),
    ]
    for v in varieties:
        ws2.append(list(v))
    wb.save(path)
    return path


def test_franchi_rows_upserted(db_session, franchi_xlsx):
    """FRANCHI importer upserts all 27 variety provider rows."""
    from organic_market_agent.crop_book.importer.israeli.franchi_catalog_importer import import_all
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    summary = import_all(db_session, xlsx_path=franchi_xlsx)

    rows = db_session.query(CropVarietySourceValue).filter_by(
        field_name="variety_provider", source="OP:FRANCHI_catalog"
    ).all()
    assert len(rows) >= 7, f"Expected ≥7 variety rows (fixture crops), got {len(rows)}"
    assert summary.rows_parsed >= 25, f"Expected ≥25 rows parsed from fixture XLSX, got {summary.rows_parsed}"
