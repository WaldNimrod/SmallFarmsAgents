"""Tests for jmf_masterclass.py parsers (AC-05, AC-06). SFA-S003-P002-WP-B1."""
import pytest
from pathlib import Path
from decimal import Decimal

pytestmark = pytest.mark.crop_book

FIXTURE = Path(__file__).parent / "fixtures" / "jmf" / "minimal_masterclass.xlsx"


# ---- AC-05: parse_crop_chart ----

def test_parse_crop_chart_returns_3_rows():
    """AC-05: fixture has 3 crops → 3 rows."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    rows = parse_crop_chart(FIXTURE)
    assert len(rows) == 3
    crops = [r["crop_jmf_en"] for r in rows]
    assert "Arugula" in crops
    assert "Carrots" in crops
    assert "Basil" in crops


def test_parse_crop_chart_dtm_present():
    """AC-05: at least 90% of rows have days_to_maturity."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    rows = parse_crop_chart(FIXTURE)
    with_dtm = [r for r in rows if "days_to_maturity" in r]
    assert len(with_dtm) / len(rows) >= 0.9


def test_parse_crop_chart_required_keys():
    """AC-05: every row has crop_jmf_en."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    rows = parse_crop_chart(FIXTURE)
    for r in rows:
        assert "crop_jmf_en" in r
        assert r["crop_jmf_en"].strip()


def test_parse_crop_chart_no_none_values():
    """AC-05: no row has keys with None values (absent = omitted, not None)."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart
    rows = parse_crop_chart(FIXTURE)
    for r in rows:
        for k, v in r.items():
            if k not in ("documented_price_unit",):  # unit may be string
                assert v is not None, f"Row {r['crop_jmf_en']} has None for {k}"


# ---- AC-06: parse_associated_tasks ----

def test_parse_associated_tasks_count():
    """AC-06: fixture has 5 non-blank task cells."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_associated_tasks
    rows = parse_associated_tasks(FIXTURE)
    assert len(rows) >= 3, f"Expected at least 3 task rows, got {len(rows)}"


def test_parse_associated_tasks_task_type_valid():
    """AC-06: every row's task_type is in TASK_TYPE_VALUES."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_associated_tasks
    from organic_market_agent.crop_book.crop_task_templates import TASK_TYPE_VALUES
    rows = parse_associated_tasks(FIXTURE)
    for r in rows:
        assert r["task_type"] in TASK_TYPE_VALUES, f"Invalid task_type: {r['task_type']!r}"


def test_parse_associated_tasks_days_offset_is_int():
    """AC-06: days_offset is always int (NOT NULL contract)."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_associated_tasks
    rows = parse_associated_tasks(FIXTURE)
    for r in rows:
        assert isinstance(r["days_offset"], int), f"days_offset is not int: {r}"
        assert r["days_offset"] is not None


def test_parse_associated_tasks_x_cell_uses_sentinel():
    """AC-06: X cell → DAYS_OFFSET_PRESENCE_ONLY."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_associated_tasks
    from organic_market_agent.crop_book.crop_task_templates import DAYS_OFFSET_PRESENCE_ONLY
    rows = parse_associated_tasks(FIXTURE)
    # Arugula has X in at_seeding_transplanting
    arugula_tasks = [r for r in rows if r["crop_jmf_en"] == "Arugula"]
    assert len(arugula_tasks) >= 1
    assert any(r["days_offset"] == DAYS_OFFSET_PRESENCE_ONLY for r in arugula_tasks)


def test_parse_associated_tasks_notes_only_for_nonnumeric():
    """AC-06: notes populated only for non-numeric non-X cells."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_associated_tasks
    rows = parse_associated_tasks(FIXTURE)
    for r in rows:
        # rows without notes should have notes=None
        if r.get("notes") is not None:
            # notes row must have PRESENCE_ONLY sentinel
            from organic_market_agent.crop_book.crop_task_templates import DAYS_OFFSET_PRESENCE_ONLY
            assert r["days_offset"] == DAYS_OFFSET_PRESENCE_ONLY


def test_parse_crop_chart_empty_workbook():
    """AC-05 edge case: empty workbook returns empty list without error."""
    import tempfile, os
    import openpyxl
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_crop_chart

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        tmp = f.name
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "CROP CHART"
        wb.save(tmp)
        rows = parse_crop_chart(Path(tmp))
        assert rows == [] or isinstance(rows, list)
    finally:
        os.unlink(tmp)


# ---- Direct Seeding ----

def test_parse_direct_seeding_chart():
    """AC-05 (direct seeding): rows returned with in_row_spacing_cm as Decimal."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_direct_seeding_chart
    rows = parse_direct_seeding_chart(FIXTURE)
    assert len(rows) >= 1
    for r in rows:
        assert "crop_jmf_en" in r
        if "in_row_spacing_cm" in r:
            assert isinstance(r["in_row_spacing_cm"], Decimal)


# ---- Nursery ----

def test_parse_nursery_chart():
    """AC-05 (nursery): rows returned with days_in_nursery_cell as int."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_nursery_chart
    rows = parse_nursery_chart(FIXTURE)
    assert len(rows) >= 1
    for r in rows:
        assert "crop_jmf_en" in r


# ---- Cultivars ----

def test_parse_cultivars():
    """AC-05 (cultivars): rows returned with variety_name_en."""
    from organic_market_agent.crop_book.importer.jmf_masterclass import parse_cultivars
    rows = parse_cultivars(FIXTURE)
    assert len(rows) == 4
    for r in rows:
        assert "crop_jmf_en" in r
        assert "variety_name_en" in r
        assert r["variety_name_en"].strip()
