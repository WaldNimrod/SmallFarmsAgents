"""Tests for calculators.py — WP-CB-1 AC-05/AC-06 / LOD400 §5.

≥ 30 tests; ≥ 2 per calculator; at least one edge case per calculator.
All numeric results are verified against the §5 formulas.
"""
from __future__ import annotations

import math
from datetime import date, timedelta

import pytest


# ===========================================================================
# #1 — seed_quantity_to_buy
# ===========================================================================

def test_seed_qty_happy_path() -> None:
    from organic_market_agent.crop_book.calculators import seed_quantity_to_buy, SeedQtyResult

    result = seed_quantity_to_buy(
        rows_per_bed=4,
        in_row_spacing_cm=25.0,
        seeds_per_gram=200.0,
        bed_length_m=10.0,
        seeds_per_hole=1,
        germination_rate=0.90,
        oversow=1.10,
    )
    plants = round((10.0 * 100 / 25.0) * 4 * 1)  # 160
    seeds = math.ceil(plants / 0.90 * 1.10)
    grams = round(seeds / 200.0, 2)
    assert result.plants == plants
    assert result.seeds == seeds
    assert abs(result.grams - grams) < 1e-9


def test_seed_qty_multi_seed_per_hole() -> None:
    from organic_market_agent.crop_book.calculators import seed_quantity_to_buy

    result = seed_quantity_to_buy(
        rows_per_bed=2,
        in_row_spacing_cm=30.0,
        seeds_per_gram=10.0,
        bed_length_m=5.0,
        seeds_per_hole=3,
        germination_rate=0.85,
        oversow=1.10,
    )
    plants = round((5.0 * 100 / 30.0) * 2 * 3)
    seeds = math.ceil(plants / 0.85 * 1.10)
    grams = round(seeds / 10.0, 2)
    assert result.plants == plants
    assert result.seeds == seeds
    assert abs(result.grams - grams) < 1e-9


def test_seed_qty_raises_on_none_seeds_per_gram() -> None:
    from organic_market_agent.crop_book.calculators import seed_quantity_to_buy, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        seed_quantity_to_buy(
            rows_per_bed=4,
            in_row_spacing_cm=25.0,
            seeds_per_gram=None,
            bed_length_m=10.0,
        )
    assert exc.value.missing_field == "seeds_per_gram"


# ===========================================================================
# #2 — transplants_needed
# ===========================================================================

def test_transplants_needed_basic() -> None:
    from organic_market_agent.crop_book.calculators import transplants_needed

    result = transplants_needed(rows_per_bed=4, in_row_spacing_cm=25.0, bed_length_m=10.0)
    expected = round((10.0 * 100 / 25.0) * 4)
    assert result == expected


def test_transplants_needed_single_row() -> None:
    from organic_market_agent.crop_book.calculators import transplants_needed

    result = transplants_needed(rows_per_bed=1, in_row_spacing_cm=50.0, bed_length_m=30.0)
    assert result == round((30.0 * 100 / 50.0) * 1)  # 60


# ===========================================================================
# #3 — nursery_trays_and_sow_date
# ===========================================================================

def test_nursery_trays_basic() -> None:
    from organic_market_agent.crop_book.calculators import nursery_trays_and_sow_date

    field_date = date(2026, 3, 1)
    result = nursery_trays_and_sow_date(
        plants=200,
        days_in_nursery=21,
        field_set_date=field_date,
        tray_cells=128,
        oversow=1.10,
    )
    expected_trays = math.ceil(200 * 1.10 / 128)
    expected_sow = field_date - timedelta(days=21)
    assert result.trays == expected_trays
    assert result.tray_sow_date == expected_sow


def test_nursery_trays_raises_on_none_days() -> None:
    from organic_market_agent.crop_book.calculators import nursery_trays_and_sow_date, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        nursery_trays_and_sow_date(
            plants=100,
            days_in_nursery=None,
            field_set_date=date(2026, 4, 1),
        )
    assert exc.value.missing_field == "days_in_nursery_cell"


def test_nursery_trays_exact_fit_no_leftover() -> None:
    """128 plants * 1.0 oversow / 128 cells = exactly 1 tray."""
    from organic_market_agent.crop_book.calculators import nursery_trays_and_sow_date

    result = nursery_trays_and_sow_date(
        plants=128,
        days_in_nursery=14,
        field_set_date=date(2026, 5, 1),
        tray_cells=128,
        oversow=1.0,
    )
    assert result.trays == 1


# ===========================================================================
# #4 — sowing_date_from_harvest
# ===========================================================================

def test_sowing_date_transplant() -> None:
    from organic_market_agent.crop_book.calculators import sowing_date_from_harvest

    target = date(2026, 6, 1)
    result = sowing_date_from_harvest(
        target_harvest=target,
        days_to_maturity=60,
        planting_method="transplant",
        days_in_nursery=21,
    )
    expected_sow = target - timedelta(days=60 + 21)
    expected_field = expected_sow + timedelta(days=21)
    assert result.sow_date == expected_sow
    assert result.field_set_date == expected_field


def test_sowing_date_direct_sow() -> None:
    from organic_market_agent.crop_book.calculators import sowing_date_from_harvest

    target = date(2026, 8, 15)
    result = sowing_date_from_harvest(
        target_harvest=target,
        days_to_maturity=45,
        planting_method="direct_sow",
        days_in_nursery=None,
    )
    assert result.sow_date == target - timedelta(days=45)
    assert result.field_set_date is None


def test_sowing_date_raises_on_none_dtm() -> None:
    from organic_market_agent.crop_book.calculators import sowing_date_from_harvest, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        sowing_date_from_harvest(
            target_harvest=date(2026, 6, 1),
            days_to_maturity=None,
            planting_method="direct_sow",
            days_in_nursery=None,
        )
    assert exc.value.missing_field == "days_to_maturity"


def test_sowing_date_transplant_raises_on_none_nursery() -> None:
    from organic_market_agent.crop_book.calculators import sowing_date_from_harvest, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        sowing_date_from_harvest(
            target_harvest=date(2026, 6, 1),
            days_to_maturity=60,
            planting_method="transplant",
            days_in_nursery=None,
        )
    assert exc.value.missing_field == "days_in_nursery_cell"


# ===========================================================================
# #5 — harvest_window_from_sowing
# ===========================================================================

def test_harvest_window_transplant() -> None:
    from organic_market_agent.crop_book.calculators import harvest_window_from_sowing

    sow = date(2026, 2, 1)
    result = harvest_window_from_sowing(
        sow_date=sow,
        days_to_maturity=60,
        harvest_window_max_days=14,
        planting_method="transplant",
        days_in_nursery=21,
    )
    start = sow + timedelta(days=21 + 60)
    end = start + timedelta(days=14)
    assert result.harvest_start == start
    assert result.harvest_end == end


def test_harvest_window_direct_sow() -> None:
    from organic_market_agent.crop_book.calculators import harvest_window_from_sowing

    sow = date(2026, 4, 1)
    result = harvest_window_from_sowing(
        sow_date=sow,
        days_to_maturity=45,
        harvest_window_max_days=21,
        planting_method="direct_sow",
        days_in_nursery=None,
    )
    start = sow + timedelta(days=45)
    end = start + timedelta(days=21)
    assert result.harvest_start == start
    assert result.harvest_end == end


def test_harvest_window_raises_on_none_window() -> None:
    from organic_market_agent.crop_book.calculators import harvest_window_from_sowing, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        harvest_window_from_sowing(
            sow_date=date(2026, 4, 1),
            days_to_maturity=45,
            harvest_window_max_days=None,
            planting_method="direct_sow",
            days_in_nursery=None,
        )
    assert exc.value.missing_field == "harvest_window_max_days"


# ===========================================================================
# #6 — succession_schedule
# ===========================================================================

def test_succession_schedule_num_successions() -> None:
    from organic_market_agent.crop_book.calculators import succession_schedule

    first = date(2026, 3, 1)
    dates = succession_schedule(
        first_sow=first,
        succession_interval_weeks=2,
        num_successions=4,
    )
    assert len(dates) == 4
    assert dates[0] == first
    assert dates[1] == first + timedelta(weeks=2)
    assert dates[3] == first + timedelta(weeks=6)


def test_succession_schedule_season_end() -> None:
    from organic_market_agent.crop_book.calculators import succession_schedule

    first = date(2026, 3, 1)
    season_end = date(2026, 4, 15)
    dates = succession_schedule(
        first_sow=first,
        succession_interval_weeks=2,
        season_end=season_end,
    )
    assert all(d <= season_end for d in dates)
    assert dates[-1] <= season_end
    # next would be > season_end
    assert dates[-1] + timedelta(weeks=2) > season_end


def test_succession_raises_on_none_interval() -> None:
    from organic_market_agent.crop_book.calculators import succession_schedule, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        succession_schedule(
            first_sow=date(2026, 3, 1),
            succession_interval_weeks=None,
            num_successions=3,
        )
    assert exc.value.missing_field == "succession_interval_weeks"


def test_succession_raises_without_count_or_end() -> None:
    from organic_market_agent.crop_book.calculators import succession_schedule

    with pytest.raises(ValueError):
        succession_schedule(
            first_sow=date(2026, 3, 1),
            succession_interval_weeks=2,
        )


# ===========================================================================
# #7 — beds_for_target_yield
# ===========================================================================

def test_beds_for_target_yield_basic() -> None:
    from organic_market_agent.crop_book.calculators import beds_for_target_yield

    result = beds_for_target_yield(
        target_kg=300.0,
        avg_yield_per_bed_m=2.0,
        std_bed_length_m=30.0,
    )
    assert result.bed_meters == 150.0
    assert result.beds == 5.0


def test_beds_for_target_yield_raises_on_none() -> None:
    from organic_market_agent.crop_book.calculators import beds_for_target_yield, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        beds_for_target_yield(target_kg=100.0, avg_yield_per_bed_m=None)
    assert exc.value.missing_field == "avg_yield_per_bed_m"


def test_beds_for_target_yield_raises_on_zero() -> None:
    from organic_market_agent.crop_book.calculators import beds_for_target_yield, CalcUnavailable

    with pytest.raises(CalcUnavailable):
        beds_for_target_yield(target_kg=100.0, avg_yield_per_bed_m=0)


# ===========================================================================
# #8 — expected_yield
# ===========================================================================

def test_expected_yield_basic() -> None:
    from organic_market_agent.crop_book.calculators import expected_yield

    result = expected_yield(avg_yield_per_bed_m=1.5, bed_length_m=20.0)
    assert abs(result - 30.0) < 1e-9


def test_expected_yield_fractional() -> None:
    from organic_market_agent.crop_book.calculators import expected_yield

    result = expected_yield(avg_yield_per_bed_m=0.175, bed_length_m=10.0)
    assert abs(result - 1.75) < 1e-9


# ===========================================================================
# #9 — expected_revenue
# ===========================================================================

def test_expected_revenue_per_kg_price() -> None:
    from organic_market_agent.crop_book.calculators import expected_revenue

    result = expected_revenue(
        avg_yield_per_bed_m=2.0,
        bed_length_m=10.0,
        documented_price=15.0,
        documented_price_unit="kg",
    )
    assert abs(result.yield_kg - 20.0) < 1e-9
    assert abs(result.revenue - 300.0) < 1e-9


def test_expected_revenue_raises_on_none_price() -> None:
    from organic_market_agent.crop_book.calculators import expected_revenue, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        expected_revenue(
            avg_yield_per_bed_m=2.0,
            bed_length_m=10.0,
            documented_price=None,
            documented_price_unit="kg",
        )
    assert exc.value.missing_field == "documented_price"


def test_expected_revenue_non_kg_unit_without_conversion() -> None:
    from organic_market_agent.crop_book.calculators import expected_revenue, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        expected_revenue(
            avg_yield_per_bed_m=2.0,
            bed_length_m=10.0,
            documented_price=8.0,
            documented_price_unit="bunch",
            kg_per_unit=None,
        )
    assert exc.value.missing_field == "conversion"


def test_expected_revenue_non_kg_unit_with_conversion() -> None:
    from organic_market_agent.crop_book.calculators import expected_revenue

    # 1 bunch = 0.25 kg → 8 ILS/bunch = 32 ILS/kg
    result = expected_revenue(
        avg_yield_per_bed_m=2.0,
        bed_length_m=10.0,
        documented_price=8.0,
        documented_price_unit="bunch",
        kg_per_unit=0.25,
    )
    price_per_kg = 8.0 / 0.25  # 32
    expected_revenue_val = 20.0 * price_per_kg  # 640
    assert abs(result.revenue - expected_revenue_val) < 1e-6


# ===========================================================================
# #10 — plant_population
# ===========================================================================

def test_plant_population_basic() -> None:
    from organic_market_agent.crop_book.calculators import plant_population

    result = plant_population(rows_per_bed=4, in_row_spacing_cm=25.0, bed_width_m=0.80)
    plants_per_m2 = (4 / 0.80) * (100 / 25.0)  # 5.0 * 4.0 = 20
    assert abs(result.plants_per_m2 - plants_per_m2) < 1e-9
    assert result.grid == (4, round(100 / 25.0))  # (4, 4)


def test_plant_population_assumption_default() -> None:
    from organic_market_agent.crop_book.calculators import plant_population

    result_explicit = plant_population(rows_per_bed=3, in_row_spacing_cm=30.0, bed_width_m=0.80)
    result_default = plant_population(rows_per_bed=3, in_row_spacing_cm=30.0)
    assert abs(result_explicit.plants_per_m2 - result_default.plants_per_m2) < 1e-9


# ===========================================================================
# #11 — frost_planting_window
# ===========================================================================

def test_frost_window_very_hardy() -> None:
    from organic_market_agent.crop_book.calculators import frost_planting_window

    last_frost = date(2026, 3, 15)
    first_frost = date(2026, 11, 1)
    result = frost_planting_window(
        last_frost=last_frost,
        first_frost=first_frost,
        frost_tolerance_class="very_hardy",
        days_to_maturity=60,
    )
    # very_hardy offset = 28 (plant 28 days before last frost)
    assert result.earliest_plant == last_frost - timedelta(days=28)
    assert result.latest_plant == first_frost - timedelta(days=60)


def test_frost_window_raises_on_none_dtm() -> None:
    from organic_market_agent.crop_book.calculators import frost_planting_window, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        frost_planting_window(
            last_frost=date(2026, 3, 15),
            first_frost=date(2026, 11, 1),
            frost_tolerance_class="tender",
            days_to_maturity=None,
        )
    assert exc.value.missing_field == "days_to_maturity"


def test_frost_window_explicit_override() -> None:
    from organic_market_agent.crop_book.calculators import frost_planting_window

    last_frost = date(2026, 3, 15)
    first_frost = date(2026, 11, 1)
    result = frost_planting_window(
        last_frost=last_frost,
        first_frost=first_frost,
        frost_tolerance_class="tender",
        days_to_maturity=45,
        hardiness_offset_days=7,
    )
    assert result.earliest_plant == last_frost - timedelta(days=7)


# ===========================================================================
# #12 — fertilizer_compost_rate
# ===========================================================================

def test_fertilizer_basic() -> None:
    from organic_market_agent.crop_book.calculators import fertilizer_compost_rate

    result = fertilizer_compost_rate(
        nutrient_removal_n_kg_ha=100.0,
        nutrient_removal_p_kg_ha=40.0,
        nutrient_removal_k_kg_ha=80.0,
        area_m2=500.0,
        compost_N_pct=0.015,
        application_efficiency=0.50,
    )
    area_ha = 500.0 / 10_000  # 0.05
    n_kg = 100.0 * area_ha  # 5.0
    compost_kg = n_kg / (0.015 * 0.50)  # 666.67
    p_kg = 40.0 * area_ha
    k_kg = 80.0 * area_ha
    assert abs(result.n_kg - n_kg) < 1e-6
    assert abs(result.compost_kg - compost_kg) < 1e-3
    assert abs(result.p_kg - p_kg) < 1e-6
    assert abs(result.k_kg - k_kg) < 1e-6


def test_fertilizer_raises_on_none_n() -> None:
    from organic_market_agent.crop_book.calculators import fertilizer_compost_rate, CalcUnavailable

    with pytest.raises(CalcUnavailable) as exc:
        fertilizer_compost_rate(
            nutrient_removal_n_kg_ha=None,
            nutrient_removal_p_kg_ha=None,
            nutrient_removal_k_kg_ha=None,
            area_m2=100.0,
        )
    assert exc.value.missing_field == "nutrient_removal_n_kg_ha"


def test_fertilizer_optional_p_k_none() -> None:
    from organic_market_agent.crop_book.calculators import fertilizer_compost_rate

    result = fertilizer_compost_rate(
        nutrient_removal_n_kg_ha=80.0,
        nutrient_removal_p_kg_ha=None,
        nutrient_removal_k_kg_ha=None,
        area_m2=1000.0,
    )
    assert result.p_kg is None
    assert result.k_kg is None
    assert result.compost_kg > 0


# ===========================================================================
# #13 — crop_profit_comparison
# ===========================================================================

def test_profit_comparison_basic() -> None:
    from organic_market_agent.crop_book.calculators import (
        crop_profit_comparison,
        CropEconomics,
    )

    crops = [
        CropEconomics(1, "עגבנייה", 3.0, 8.0, "kg", None, seed_cost_per_m=0.5),
        CropEconomics(2, "מלפפון", 4.0, 6.0, "kg", None, seed_cost_per_m=0.3),
    ]
    result = crop_profit_comparison(crops)
    assert len(result.ranked) == 2
    assert len(result.skipped) == 0
    # margin: עגבנייה = 3*8 - 0.5 = 23.5; מלפפון = 4*6 - 0.3 = 23.7
    assert result.ranked[0].name_he == "מלפפון"


def test_profit_comparison_skips_missing_price() -> None:
    from organic_market_agent.crop_book.calculators import (
        crop_profit_comparison,
        CropEconomics,
    )

    crops = [
        CropEconomics(1, "עגבנייה", 3.0, 8.0, "kg", None),
        CropEconomics(2, "חסה", 2.0, None, "kg", None),  # no price
    ]
    result = crop_profit_comparison(crops)
    assert len(result.ranked) == 1
    assert len(result.skipped) == 1
    assert result.skipped[0].name_he == "חסה"


def test_profit_comparison_with_bed_meters() -> None:
    from organic_market_agent.crop_book.calculators import (
        crop_profit_comparison,
        CropEconomics,
    )

    crops = [CropEconomics(1, "כרפס", 2.0, 10.0, "kg", None)]
    result = crop_profit_comparison(crops, bed_meters=30.0)
    assert result.ranked[0].total_revenue == 2.0 * 10.0 * 30.0


# ===========================================================================
# #14 — seed_input_cost
# ===========================================================================

def test_seed_cost_per_gram() -> None:
    from organic_market_agent.crop_book.calculators import seed_input_cost

    result = seed_input_cost(grams_needed=5.0, seed_price_per_g=2.0)
    assert result.packs is None
    assert abs(result.cost - 10.0) < 1e-9


def test_seed_cost_by_pack() -> None:
    from organic_market_agent.crop_book.calculators import seed_input_cost

    result = seed_input_cost(grams_needed=7.5, pack_price=12.0, grams_per_pack=5.0)
    packs = math.ceil(7.5 / 5.0)  # 2
    assert result.packs == packs
    assert abs(result.cost - packs * 12.0) < 1e-9


def test_seed_cost_raises_without_pricing() -> None:
    from organic_market_agent.crop_book.calculators import seed_input_cost

    with pytest.raises(ValueError):
        seed_input_cost(grams_needed=5.0)


# ===========================================================================
# CalcUnavailable is a proper exception
# ===========================================================================

def test_calc_unavailable_is_exception() -> None:
    from organic_market_agent.crop_book.calculators import CalcUnavailable

    exc = CalcUnavailable("some_field")
    assert isinstance(exc, Exception)
    assert exc.missing_field == "some_field"
    assert "some_field" in str(exc)
