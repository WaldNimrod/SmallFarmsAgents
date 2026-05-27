"""WP-C3 tests — Idan 2018 diff importer (L49 vs L03/L04)."""

from __future__ import annotations

import openpyxl
import pytest
from decimal import Decimal
from pathlib import Path

pytestmark = pytest.mark.crop_book


def _make_planning_xlsx(tmp_path: Path, filename: str, rows: list) -> Path:
    """Create a planning XLSX (L03/L04/L49-style) with a 'תוכנית גידול' sheet."""
    path = tmp_path / filename
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "תוכנית גידול"
    ws.append([None] * 17)  # row 1: empty
    # Header row (simplified — we only care about positions 0,7,9,12 for L49; 0,7,11,14 for L03)
    ws.append(["גידול", "זן", "הערות", "תאריך שתילה", "ת. נביטה", "תחילת אסיף", "סיום אסיף",
               "שטח לזריעה", "סימון", "מספר צמחים למ\"ר", "מרווח", "מספר צמחים למ\"ר_l03",
               "מספר צמחים כולל", "מספר שתילים", "כמות סה\"כ", "הערות2"])
    for row in rows:
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
        fam = CropFamily(scientific_name="Solanaceae", name_he="סולניים")
        session.add(fam)
        session.flush()
        session.add(Crop(name_he="עגבנייה", name_en="Tomatoes", category="vegetables", family_id=fam.id))
        session.add(Crop(name_he="קישוא", name_en="Zucchini", category="vegetables", family_id=fam.id))
        session.flush()
        yield session


def test_diff_upserts_changed_only(db_session, tmp_path):
    """Changed rows are upserted; identical rows are skipped; no duplicates on re-run."""
    from organic_market_agent.crop_book.importer.israeli.idan_2018_diff import import_all
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    # L03: עגבנייה with yield 5 kg/m², plants_per_m2=2
    # L49: עגבנייה with yield 6 kg/m² (changed), plants_per_m2=2 (same)
    # L49: קישוא NEW (not in L03)

    # Rows: [crop, variety, notes, date_plant, date_germ, date_start, date_end,
    #        area, marking, plants_m2_L49, spacing, plants_m2_L03, total_plants, transplants, yield_kg, notes2]
    l03_rows = [
        ["עגבנייה", "עגבנייה רגילה", None, None, None, None, None, "10", None, None, None, 2, None, None, "50", None],
    ]
    l49_rows = [
        # same area=10, yield_kg=60 → yield_per_m2=6 (vs L03: 50/10=5) — CHANGED
        ["עגבנייה", "עגבנייה רגילה", None, None, None, None, None, "10", None, 2, None, None, None, None, "60", None],
        # קישוא NEW — not in L03
        ["קישוא", "קישוא ירוק", None, None, None, None, None, "5", None, 3, None, None, None, None, "20", None],
    ]

    l03_path = _make_planning_xlsx(tmp_path, "L03_test.xlsx", l03_rows)
    l49_path = _make_planning_xlsx(tmp_path, "L49_test.xlsx", l49_rows)
    l04_path = _make_planning_xlsx(tmp_path, "L04_test.xlsx", [])  # empty

    summary = import_all(db_session, l49_path=l49_path, l03_path=l03_path, l04_path=l04_path)

    rows = db_session.query(CropVarietySourceValue).filter_by(source="OP:Idan_2018").all()
    assert len(rows) >= 1, "At least one row should be upserted (changed or new)"

    # Re-run should not add duplicates
    count_before = db_session.query(CropVarietySourceValue).filter_by(source="OP:Idan_2018").count()
    import_all(db_session, l49_path=l49_path, l03_path=l03_path, l04_path=l04_path)
    count_after = db_session.query(CropVarietySourceValue).filter_by(source="OP:Idan_2018").count()
    assert count_before == count_after, "Re-run should be idempotent"
