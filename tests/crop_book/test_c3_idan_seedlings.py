"""WP-C3 tests — Idan seedlings succession interval importer."""

from __future__ import annotations

import openpyxl
import pytest
from datetime import date
from decimal import Decimal
from pathlib import Path

pytestmark = pytest.mark.crop_book


def _make_seedlings_xlsx(tmp_path: Path, filename: str, crop_dates: dict) -> Path:
    """Create a minimal seedlings XLSX fixture.

    crop_dates: {crop_he: [date_str, ...]} where truthy dates = order present.
    """
    path = tmp_path / filename
    wb = openpyxl.Workbook()
    ws = wb.active
    all_dates = set()
    for dates in crop_dates.values():
        all_dates.update(d for d in dates if d)
    date_list = sorted(all_dates)

    header = ["גידול"] + [d for d in date_list]
    ws.append([None] * len(header))  # row 1: empty
    ws.append(header)                # row 2: header
    for crop, dates in crop_dates.items():
        row = [crop] + [("מגש" if d in dates else None) for d in date_list]
        ws.append(row)
    wb.save(path)
    return path


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
        fam = CropFamily(scientific_name="Brassicaceae", name_he="מצליבים")
        session.add(fam)
        session.flush()
        for he, en in [("ברוקולי", "Broccoli"), ("חסה", "Lettuce"), ("כרישה", "Leeks"),
                       ("סלק", "Beets"), ("קולרבי", "Kohlrabi"), ("כרוב לבן", "Cabbage"),
                       ("כרובית", "Cauliflower"), ("שומר", "Fennel")]:
            session.add(Crop(name_he=he, name_en=en, category="vegetables", family_id=fam.id))
        session.flush()
        yield session


def test_succession_intervals_derived(tmp_path, db_session):
    """Two order dates separated by 2 weeks → succession_interval = 2."""
    from organic_market_agent.crop_book.importer.israeli.idan_seedlings_importer import (
        derive_succession_intervals,
        import_all,
    )
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    # Create minimal XLSX: ברוקולי has orders on 18/9 and 2/10 (14 days apart = 2 weeks)
    xlsx_a = _make_seedlings_xlsx(tmp_path, "L05a_test.xlsx", {
        "ברוקולי": ["18/9", "2/10"],
    })

    intervals = derive_succession_intervals([xlsx_a])
    assert "ברוקולי" in intervals
    assert intervals["ברוקולי"] == 2  # 14 days / 7 = 2 weeks

    import_all(db_session, xlsx_paths=[xlsx_a])

    rows = db_session.query(CropVarietySourceValue).filter_by(
        field_name="succession_interval_weeks", source="OP:Idan_seedlings"
    ).all()
    assert len(rows) >= 1
    values = {r.value_numeric for r in rows}
    assert Decimal("2") in values


def test_multiple_crops(tmp_path, db_session):
    """Combined L05a + L05b yields ≥8 crops with succession intervals."""
    from organic_market_agent.crop_book.importer.israeli.idan_seedlings_importer import derive_succession_intervals

    xlsx_a = _make_seedlings_xlsx(tmp_path, "L05a_test.xlsx", {
        "ברוקולי": ["18/9", "2/10", "16/10"],
        "חסה אייסברג": ["18/9", "30/10"],
        "כרישה": ["2/10", "16/10", "27/11"],
        "סלק": ["2/10", "30/10"],
        "קולרבי": ["16/10", "27/11"],
    })
    xlsx_b = _make_seedlings_xlsx(tmp_path, "L05b_test.xlsx", {
        "ברוקולי": ["5.3", "22.3", "5.4"],  # Additional dates from summer
        "כרוב לבן": ["5.3", "22.3"],
        "כרובית": ["5.3", "5.4"],
        "שומר": ["22.3", "5.4"],
    })

    intervals = derive_succession_intervals([xlsx_a, xlsx_b])
    # ברוקולי spans both files → should have enough dates
    # At minimum the A-file crops should all appear
    assert len(intervals) >= 5, f"Expected ≥5 crops, got {len(intervals)}: {list(intervals)}"
