"""Pure-function calculators for Crop Book v1 — SFA-S003-P004-WP-CB-1.

All 14 calculators are pure functions: no DB, no I/O, no globals, no network.
Required book values (from crop_field_enrichment.value_best) are passed in by
the caller.  AssumptionFields and user inputs have explicit defaults and never
raise CalcUnavailable.

Each calculator raises CalcUnavailable(<field_name>) when a required BOOK value
is None.  Result dataclasses are frozen.

Reference: LOD400 §5, Calculator Catalog §2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# Shared exception
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CalcUnavailable(Exception):
    """Raised when a required book value is None (field has no value_best)."""
    missing_field: str

    def __str__(self) -> str:
        return f"CalcUnavailable: required field '{self.missing_field}' is None"


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SeedQtyResult:
    plants: int
    seeds: int
    grams: float


@dataclass(frozen=True)
class NurseryTrayResult:
    trays: int
    tray_sow_date: date


@dataclass(frozen=True)
class SowingDateResult:
    sow_date: date
    field_set_date: Optional[date]


@dataclass(frozen=True)
class HarvestWindowResult:
    harvest_start: date
    harvest_end: date


@dataclass(frozen=True)
class BedsForYieldResult:
    bed_meters: float
    beds: float


@dataclass(frozen=True)
class RevenueResult:
    yield_kg: float
    revenue: float


@dataclass(frozen=True)
class PlantPopulationResult:
    plants_per_m2: float
    grid: tuple  # (rows_per_bed, plants_per_row)


@dataclass(frozen=True)
class FrostWindowResult:
    earliest_plant: date
    latest_plant: date


@dataclass(frozen=True)
class FertilizerResult:
    n_kg: float
    p_kg: Optional[float]
    k_kg: Optional[float]
    compost_kg: float


@dataclass(frozen=True)
class CropEconomics:
    crop_id: int
    name_he: str
    avg_yield_per_bed_m: Optional[float]
    documented_price: Optional[float]
    documented_price_unit: str
    kg_per_unit: Optional[float]
    seed_cost_per_m: Optional[float] = None


@dataclass(frozen=True)
class CropRank:
    crop_id: int
    name_he: str
    revenue_per_m: float
    margin_per_m: float
    total_revenue: Optional[float]
    total_margin: Optional[float]


@dataclass(frozen=True)
class ProfitComparisonResult:
    ranked: list  # list[CropRank], sorted by margin_per_m desc
    skipped: list  # list[CropEconomics] — excluded due to missing yield/price


@dataclass(frozen=True)
class SeedCostResult:
    packs: Optional[int]
    cost: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_transplant(planting_method: str) -> bool:
    """True if the planting method is a transplant/greenhouse operation."""
    pm = planting_method.lower()
    return pm.startswith("transplant") or pm.startswith("greenhouse")


def _price_per_kg(
    documented_price: float,
    documented_price_unit: str,
    kg_per_unit: Optional[float],
) -> float:
    """Convert documented_price to ILS/kg regardless of unit."""
    unit = documented_price_unit.lower()
    if unit in ("kg", "kilogram", "ק\"ג", "קג"):
        return documented_price
    # Non-kg unit requires conversion
    if kg_per_unit is None or kg_per_unit == 0:
        raise CalcUnavailable("conversion")
    return documented_price / kg_per_unit


# ---------------------------------------------------------------------------
# Calculator #1 — Seed quantity to buy
# ---------------------------------------------------------------------------

def seed_quantity_to_buy(
    *,
    rows_per_bed: int,
    in_row_spacing_cm: float,
    seeds_per_gram: Optional[float],
    bed_length_m: float,
    seeds_per_hole: int = 1,
    germination_rate: float = 0.90,
    oversow: float = 1.10,
) -> SeedQtyResult:
    """Calculate seeds and grams to buy for a bed.

    Book values:    rows_per_bed, in_row_spacing_cm, seeds_per_gram (required)
    AssumptionFields: germination_rate (0.90), oversow (1.10)
    User inputs:    bed_length_m, seeds_per_hole

    Raises CalcUnavailable("seeds_per_gram") if seeds_per_gram is None.
    """
    if seeds_per_gram is None:
        raise CalcUnavailable("seeds_per_gram")
    if germination_rate <= 0 or germination_rate > 1:
        raise ValueError(f"germination_rate must be in (0,1], got {germination_rate}")
    if in_row_spacing_cm <= 0:
        raise ValueError(f"in_row_spacing_cm must be > 0, got {in_row_spacing_cm}")

    plants = round((bed_length_m * 100 / in_row_spacing_cm) * rows_per_bed * seeds_per_hole)
    seeds = math.ceil(plants / germination_rate * oversow)
    grams = round(seeds / seeds_per_gram, 2)
    return SeedQtyResult(plants=plants, seeds=seeds, grams=grams)


# ---------------------------------------------------------------------------
# Calculator #2 — Transplants / seedlings needed
# ---------------------------------------------------------------------------

def transplants_needed(
    *,
    rows_per_bed: int,
    in_row_spacing_cm: float,
    bed_length_m: float,
) -> int:
    """Number of transplants needed for a bed.

    Book values:  rows_per_bed, in_row_spacing_cm
    User inputs:  bed_length_m
    """
    return round((bed_length_m * 100 / in_row_spacing_cm) * rows_per_bed)


# ---------------------------------------------------------------------------
# Calculator #3 — Nursery trays + sow date
# ---------------------------------------------------------------------------

def nursery_trays_and_sow_date(
    *,
    plants: int,
    days_in_nursery: Optional[int],
    field_set_date: date,
    tray_cells: int = 128,
    oversow: float = 1.10,
) -> NurseryTrayResult:
    """Number of trays and when to start them.

    Book values:      days_in_nursery (required)
    AssumptionFields: tray_cells (by nursery_tray_type, default 128), oversow (1.10)
    User inputs:      plants (from #2), field_set_date

    Raises CalcUnavailable("days_in_nursery_cell") if days_in_nursery is None.
    """
    if days_in_nursery is None:
        raise CalcUnavailable("days_in_nursery_cell")

    trays = math.ceil(plants * oversow / tray_cells)
    tray_sow_date = field_set_date - timedelta(days=days_in_nursery)
    return NurseryTrayResult(trays=trays, tray_sow_date=tray_sow_date)


# ---------------------------------------------------------------------------
# Calculator #4 — Sowing date (back-calc from harvest)
# ---------------------------------------------------------------------------

def sowing_date_from_harvest(
    *,
    target_harvest: date,
    days_to_maturity: Optional[int],
    planting_method: str,
    days_in_nursery: Optional[int],
) -> SowingDateResult:
    """Back-calculate when to sow from a target harvest date.

    Book values:  days_to_maturity (required), planting_method, days_in_nursery
    User inputs:  target_harvest

    Raises CalcUnavailable("days_to_maturity") if days_to_maturity is None.
    Raises CalcUnavailable("days_in_nursery_cell") if transplant and days_in_nursery is None.
    """
    if days_to_maturity is None:
        raise CalcUnavailable("days_to_maturity")

    if _is_transplant(planting_method):
        if days_in_nursery is None:
            raise CalcUnavailable("days_in_nursery_cell")
        sow_date = target_harvest - timedelta(days=days_to_maturity + days_in_nursery)
        field_set_date = sow_date + timedelta(days=days_in_nursery)
    else:
        sow_date = target_harvest - timedelta(days=days_to_maturity)
        field_set_date = None

    return SowingDateResult(sow_date=sow_date, field_set_date=field_set_date)


# ---------------------------------------------------------------------------
# Calculator #5 — Harvest date + window (forward from sow date)
# ---------------------------------------------------------------------------

def harvest_window_from_sowing(
    *,
    sow_date: date,
    days_to_maturity: int,
    harvest_window_max_days: Optional[int],
    planting_method: str,
    days_in_nursery: Optional[int],
) -> HarvestWindowResult:
    """Forward-calculate the harvest window from a sowing date.

    Book values:  days_to_maturity, harvest_window_max_days (required), planting_method, days_in_nursery
    User inputs:  sow_date

    Raises CalcUnavailable("harvest_window_max_days") if it is None.
    """
    if harvest_window_max_days is None:
        raise CalcUnavailable("harvest_window_max_days")

    nursery_days = 0
    if _is_transplant(planting_method) and days_in_nursery is not None:
        nursery_days = days_in_nursery

    harvest_start = sow_date + timedelta(days=nursery_days + days_to_maturity)
    harvest_end = harvest_start + timedelta(days=harvest_window_max_days)
    return HarvestWindowResult(harvest_start=harvest_start, harvest_end=harvest_end)


# ---------------------------------------------------------------------------
# Calculator #6 — Succession schedule
# ---------------------------------------------------------------------------

def succession_schedule(
    *,
    first_sow: date,
    succession_interval_weeks: Optional[int],
    num_successions: Optional[int] = None,
    season_end: Optional[date] = None,
    planting_season: Optional[str] = None,
) -> list:
    """Generate a list of sowing dates for succession planting.

    Book values:  succession_interval_weeks (required), planting_season (optional clamping)
    User inputs:  first_sow, num_successions or season_end (at least one required)

    Raises CalcUnavailable("succession_interval_weeks") if it is None.
    Raises ValueError if neither num_successions nor season_end is given.
    """
    if succession_interval_weeks is None:
        raise CalcUnavailable("succession_interval_weeks")
    if num_successions is None and season_end is None:
        raise ValueError("Must provide num_successions or season_end")

    interval_days = succession_interval_weeks * 7

    if num_successions is not None:
        dates = [first_sow + timedelta(days=n * interval_days) for n in range(num_successions)]
    else:
        # Generate until > season_end
        dates = []
        n = 0
        while True:
            d = first_sow + timedelta(days=n * interval_days)
            if d > season_end:
                break
            dates.append(d)
            n += 1

    # planting_season clamping: if provided as "YYYY-MM-DD:YYYY-MM-DD" format, clamp
    # (basic implementation; UI may provide richer constraints)
    # For v1, planting_season is informational text — no clamping applied here.
    # A future version may parse structured season bounds.

    return dates


# ---------------------------------------------------------------------------
# Calculator #7 — Beds / bed-meters for a target yield
# ---------------------------------------------------------------------------

def beds_for_target_yield(
    *,
    target_kg: float,
    avg_yield_per_bed_m: Optional[float],
    std_bed_length_m: float = 30.0,
) -> BedsForYieldResult:
    """How many bed-meters and beds needed to hit a target yield.

    Book values:      avg_yield_per_bed_m (required)
    AssumptionFields: std_bed_length_m (30 m)
    User inputs:      target_kg

    Raises CalcUnavailable("avg_yield_per_bed_m") if None or zero.
    """
    if avg_yield_per_bed_m is None or avg_yield_per_bed_m == 0:
        raise CalcUnavailable("avg_yield_per_bed_m")

    bed_meters = target_kg / avg_yield_per_bed_m
    beds = bed_meters / std_bed_length_m
    return BedsForYieldResult(bed_meters=bed_meters, beds=beds)


# ---------------------------------------------------------------------------
# Calculator #8 — Expected yield from an area
# ---------------------------------------------------------------------------

def expected_yield(
    *,
    avg_yield_per_bed_m: float,
    bed_length_m: float,
) -> float:
    """Expected yield (kg) from a bed of given length.

    Book values:  avg_yield_per_bed_m
    User inputs:  bed_length_m
    """
    return avg_yield_per_bed_m * bed_length_m


# ---------------------------------------------------------------------------
# Calculator #9 — Expected revenue
# ---------------------------------------------------------------------------

def expected_revenue(
    *,
    avg_yield_per_bed_m: float,
    bed_length_m: float,
    documented_price: Optional[float],
    documented_price_unit: str,
    kg_per_unit: Optional[float] = None,
) -> RevenueResult:
    """Expected revenue from a bed.

    Book values:  avg_yield_per_bed_m, documented_price (required), documented_price_unit,
                  kg_per_unit (required for non-kg units)
    User inputs:  bed_length_m

    Raises CalcUnavailable("documented_price") if None.
    Raises CalcUnavailable("conversion") for non-kg unit without kg_per_unit.
    """
    if documented_price is None:
        raise CalcUnavailable("documented_price")

    yield_kg = avg_yield_per_bed_m * bed_length_m
    price_per_kg = _price_per_kg(documented_price, documented_price_unit, kg_per_unit)
    revenue = yield_kg * price_per_kg
    return RevenueResult(yield_kg=yield_kg, revenue=revenue)


# ---------------------------------------------------------------------------
# Calculator #10 — Plant population / spacing layout
# ---------------------------------------------------------------------------

def plant_population(
    *,
    rows_per_bed: int,
    in_row_spacing_cm: float,
    bed_width_m: float = 0.80,
) -> PlantPopulationResult:
    """Plant density and visual grid for a bed.

    Book values:      rows_per_bed, in_row_spacing_cm
    AssumptionFields: bed_width_m (0.80 m)
    """
    plants_per_m2 = (rows_per_bed / bed_width_m) * (100 / in_row_spacing_cm)
    grid = (rows_per_bed, round(100 / in_row_spacing_cm))
    return PlantPopulationResult(plants_per_m2=plants_per_m2, grid=grid)


# ---------------------------------------------------------------------------
# Calculator #11 — Frost / planting window
# ---------------------------------------------------------------------------

def frost_planting_window(
    *,
    last_frost: date,
    first_frost: date,
    frost_tolerance_class: Optional[str],
    days_to_maturity: Optional[int],
    hardiness_offset_days: Optional[int] = None,
) -> FrostWindowResult:
    """Safe planting window based on frost dates and crop hardiness.

    Book values:      frost_tolerance_class, days_to_maturity (required)
    AssumptionFields: hardiness_offset (by class, from HARDINESS_OFFSET table)
    User inputs:      last_frost, first_frost

    Raises CalcUnavailable("days_to_maturity") if None.
    """
    if days_to_maturity is None:
        raise CalcUnavailable("days_to_maturity")

    # Resolve offset: explicit override > table lookup > conservative default 0
    if hardiness_offset_days is not None:
        offset = hardiness_offset_days
    else:
        from organic_market_agent.crop_book.assumptions import get_hardiness_offset
        offset = get_hardiness_offset(frost_tolerance_class)

    earliest_plant = last_frost - timedelta(days=offset)
    latest_plant = first_frost - timedelta(days=days_to_maturity)
    return FrostWindowResult(earliest_plant=earliest_plant, latest_plant=latest_plant)


# ---------------------------------------------------------------------------
# Calculator #12 — Fertilizer / compost rate
# ---------------------------------------------------------------------------

def fertilizer_compost_rate(
    *,
    nutrient_removal_n_kg_ha: Optional[float],
    nutrient_removal_p_kg_ha: Optional[float],
    nutrient_removal_k_kg_ha: Optional[float],
    area_m2: float,
    compost_N_pct: float = 0.015,
    application_efficiency: float = 0.50,
) -> FertilizerResult:
    """Compost and nutrient quantities needed for an area.

    Book values:      nutrient_removal_n_kg_ha (required), p and k (optional, informational)
    AssumptionFields: compost_N_pct (0.015), application_efficiency (0.50)
    User inputs:      area_m2

    Raises CalcUnavailable("nutrient_removal_n_kg_ha") if None.
    """
    if nutrient_removal_n_kg_ha is None:
        raise CalcUnavailable("nutrient_removal_n_kg_ha")

    area_ha = area_m2 / 10_000
    n_kg = nutrient_removal_n_kg_ha * area_ha
    compost_kg = n_kg / (compost_N_pct * application_efficiency)
    p_kg = nutrient_removal_p_kg_ha * area_ha if nutrient_removal_p_kg_ha is not None else None
    k_kg = nutrient_removal_k_kg_ha * area_ha if nutrient_removal_k_kg_ha is not None else None

    return FertilizerResult(n_kg=n_kg, p_kg=p_kg, k_kg=k_kg, compost_kg=compost_kg)


# ---------------------------------------------------------------------------
# Calculator #13 — Crop profit comparison
# ---------------------------------------------------------------------------

def crop_profit_comparison(
    crops: list,  # list[CropEconomics]
    *,
    bed_meters: Optional[float] = None,
) -> ProfitComparisonResult:
    """Rank crops by profit margin per bed-meter.

    Book values:  avg_yield_per_bed_m, documented_price (+unit) per crop
    User inputs:  bed_meters (optional — if given, total revenue/margin is computed)

    Crops with missing yield or price are excluded and returned in `skipped`.
    """
    ranked = []
    skipped = []

    for crop in crops:
        try:
            if crop.avg_yield_per_bed_m is None or crop.avg_yield_per_bed_m == 0:
                skipped.append(crop)
                continue
            if crop.documented_price is None:
                skipped.append(crop)
                continue

            price_per_kg = _price_per_kg(
                crop.documented_price,
                crop.documented_price_unit,
                crop.kg_per_unit,
            )
            revenue_per_m = crop.avg_yield_per_bed_m * price_per_kg
            seed_cost = crop.seed_cost_per_m or 0.0
            margin_per_m = revenue_per_m - seed_cost

            total_revenue = revenue_per_m * bed_meters if bed_meters is not None else None
            total_margin = margin_per_m * bed_meters if bed_meters is not None else None

            ranked.append(CropRank(
                crop_id=crop.crop_id,
                name_he=crop.name_he,
                revenue_per_m=revenue_per_m,
                margin_per_m=margin_per_m,
                total_revenue=total_revenue,
                total_margin=total_margin,
            ))
        except CalcUnavailable:
            skipped.append(crop)

    ranked.sort(key=lambda r: r.margin_per_m, reverse=True)
    return ProfitComparisonResult(ranked=ranked, skipped=skipped)


# ---------------------------------------------------------------------------
# Calculator #14 — Seed / input cost
# ---------------------------------------------------------------------------

def seed_input_cost(
    *,
    grams_needed: float,
    seed_price_per_g: Optional[float] = None,
    pack_price: Optional[float] = None,
    grams_per_pack: Optional[float] = None,
) -> SeedCostResult:
    """Calculate seed cost.

    User inputs: grams_needed, EITHER seed_price_per_g OR (pack_price + grams_per_pack)

    Raises ValueError if neither pricing mode is available.
    """
    if seed_price_per_g is not None:
        cost = grams_needed * seed_price_per_g
        return SeedCostResult(packs=None, cost=cost)
    elif pack_price is not None and grams_per_pack is not None:
        packs = math.ceil(grams_needed / grams_per_pack)
        cost = packs * pack_price
        return SeedCostResult(packs=packs, cost=cost)
    else:
        raise ValueError(
            "seed_input_cost requires either seed_price_per_g or "
            "(pack_price + grams_per_pack)"
        )
