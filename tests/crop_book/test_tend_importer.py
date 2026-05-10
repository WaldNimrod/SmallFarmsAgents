"""AC-07 — Tend CSV importer unit tests. No DB or file system required."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch


_CROP_PLAN_HEADERS = (
    "Category,Family Name,Crop,Crop Type,Variety,Planting Method,Harvest Stage,"
    "GH Sow Date,Days to 1st potting up,1st Potting up date,Days to 2nd Potting up,"
    "2nd Potting up date,Days to 3rd Potting up,3rd Potting up date,Days In Greenhouse,"
    "Field Sowing Planting Date,DTM,Harvest Window,First Harvest,Last Harvest,"
    "Planting Amount,Location,In-Row Spacing,In-Row Spacing Unit,Rows Per Bed,# Of Flats,"
    "Flat/pot type,Seeds per cell,Estimated loss,Total Transplants,Total Seed Needed,"
    "Average seed weight,Average seed weight unit,Total Weight Needed,Total Weight Needed Unit,"
    "Extra Seed %,Seed spec,1st Potting up flat/pot type,1st Potting up plants per cell/pot,"
    "1st Potting up # of flats/pots,2nd Potting up flat/pot type,2nd Potting up plants per cell/pot,"
    "2nd Potting up # of flats/pots,3rd Potting up flat/pot type,3rd Potting up plants per cell/pot,"
    "3rd Potting up # of flats/pots,Harvest Unit,Avg Yield Rate,Avg. Sales Price,Est. Yield,"
    "Est. Revenue,Est. Rev./unit,Growing Cycle,Rootstock,Harvest Season,First Fruiting Year,"
    "Between row spacing,Notes,Seeder,Front gear,Rear gear,Roller plate"
)


def _make_csv(rows: list[str]) -> io.StringIO:
    content = _CROP_PLAN_HEADERS + "\n" + "\n".join(rows)
    return io.StringIO(content)


def _arugula_row(
    variety: str = "Arugula",
    dtm: str = "21",
    harvest_window: str = "80",
    harvest_unit: str = "Cases",
    category: str = "Vegetables",
    family: str = "Brassicaceae",
    planting_method: str = "Direct Sow",
    harvest_stage: str = "Baby Leaf",
    rootstock: str = "",
    avg_yield: str = "0.175",
    avg_price: str = "8.00",
    growing_cycle: str = "Annual",
    in_row_spacing: str = "0.15",
    rows_per_bed: str = "8",
) -> str:
    fields = {
        "Category": category,
        "Family Name": family,
        "Crop": "Arugula",
        "Crop Type": "",
        "Variety": variety,
        "Planting Method": planting_method,
        "Harvest Stage": harvest_stage,
        "DTM": dtm,
        "Harvest Window": harvest_window,
        "In-Row Spacing": in_row_spacing,
        "In-Row Spacing Unit": "cm",
        "Rows Per Bed": rows_per_bed,
        "Harvest Unit": harvest_unit,
        "Avg Yield Rate": avg_yield,
        "Avg. Sales Price": avg_price,
        "Growing Cycle": growing_cycle,
        "Rootstock": rootstock,
        "Days In Greenhouse": "",
        "Seeder": "Jang JP-1",
        "Front gear": "14",
        "Rear gear": "9",
        "Roller plate": "X-24",
        "First Fruiting Year": "",
    }
    headers = _CROP_PLAN_HEADERS.split(",")
    return ",".join(str(fields.get(h, "")) for h in headers)


def test_parse_arugula_basic_fields() -> None:
    from organic_market_agent.crop_book.importer.tend import parse_crop_plan

    csv_data = _make_csv([_arugula_row()])
    with patch("builtins.open", return_value=csv_data):
        with patch.object(Path, "open", return_value=csv_data):
            rows = parse_crop_plan(Path("/fake/CROP_PLAN.CSV"), year="2022")

    assert len(rows) == 1
    row = rows[0]
    assert row["name_he"] == "ארוגולה"
    assert row["category"] == "vegetables"
    assert row["harvest_unit"] == "case"
    assert row["harvest_stage"] == "baby_leaf"
    assert row["planting_method"] == "direct_sow"
    assert row["days_to_maturity"] == 21
    assert row["harvest_window_max_days"] == 80
    assert row["source"] == "Tend_2022"


def test_parse_arugula_spacing() -> None:
    from organic_market_agent.crop_book.importer.tend import parse_crop_plan

    csv_data = _make_csv([_arugula_row(in_row_spacing="0.15")])
    with patch.object(Path, "open", return_value=csv_data):
        rows = parse_crop_plan(Path("/fake/CROP_PLAN.CSV"), year="2022")

    assert rows[0]["in_row_spacing_cm"] is not None
    from decimal import Decimal
    assert abs(rows[0]["in_row_spacing_cm"] - Decimal("0.15")) < Decimal("0.001")


def test_parse_grafted_variety() -> None:
    from organic_market_agent.crop_book.importer.tend import parse_crop_plan

    tomato_row = _arugula_row(rootstock="Beaufort")
    tomato_csv = io.StringIO(
        _CROP_PLAN_HEADERS.replace("Arugula", "Arugula") + "\n"
    )
    csv_data = _make_csv([_arugula_row(rootstock="Beaufort")])
    with patch.object(Path, "open", return_value=csv_data):
        rows = parse_crop_plan(Path("/fake/CROP_PLAN.CSV"), year="2022")

    assert rows[0]["is_grafted"] is True
    assert rows[0]["rootstock_variety"] == "Beaufort"


def test_unknown_crop_skipped_with_warning() -> None:
    import logging

    from organic_market_agent.crop_book.importer.tend import parse_crop_plan

    headers = _CROP_PLAN_HEADERS
    unknown_row = ",".join(
        "UnknownCropXYZ" if h == "Crop" else ("Vegetables" if h == "Category" else "")
        for h in headers.split(",")
    )
    csv_data = io.StringIO(headers + "\n" + unknown_row)
    with patch.object(Path, "open", return_value=csv_data):
        with patch("organic_market_agent.crop_book.importer.tend.logger") as mock_log:
            rows = parse_crop_plan(Path("/fake/CROP_PLAN.CSV"), year="2022")
            mock_log.warning.assert_called()

    assert rows == []


def test_harvest_unit_map_covers_valid_enum() -> None:
    from organic_market_agent.crop_book.constants import HARVEST_UNIT_MAP

    valid_enum = {"kg", "bunch", "head", "case", "unit", "seedling"}
    for raw, mapped in HARVEST_UNIT_MAP.items():
        assert mapped in valid_enum, (
            f"HARVEST_UNIT_MAP[{raw!r}] = {mapped!r} is not a valid DB enum value"
        )


def test_category_map_covers_valid_enum() -> None:
    from organic_market_agent.crop_book.constants import CATEGORY_MAP

    valid_enum = {
        "vegetables", "herbs", "baby", "legumes", "fruits", "fruit_trees", "grains", "cover_crops"
    }
    for raw, mapped in CATEGORY_MAP.items():
        assert mapped in valid_enum, (
            f"CATEGORY_MAP[{raw!r}] = {mapped!r} is not a valid DB enum value"
        )


def test_five_pilot_crops_in_tend_map() -> None:
    from organic_market_agent.crop_book.constants import TEND_CROP_MAP

    for crop_en in ("Arugula", "Broccoli", "Tomatoes", "Basil", "Carrots"):
        assert crop_en in TEND_CROP_MAP, f"{crop_en!r} missing from TEND_CROP_MAP"


def test_team00_dtm_override_arugula() -> None:
    from organic_market_agent.crop_book.constants import TEAM00_DTM_OVERRIDES

    assert "ארוגולה" in TEAM00_DTM_OVERRIDES
    assert TEAM00_DTM_OVERRIDES["ארוגולה"] == 21
