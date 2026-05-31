"""Canon §6.4 / T4 computed accessors — never stored, computed on read.

All functions accept canonical field values (T1 enrichment value_best) and
return a computed T4 value.  They do NOT read from the DB.

Bed width is the AssumptionField (0.8 m default, user-adjustable).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional


# Bed-width assumption default (Canon §6.4 / AssumptionField)
BED_WIDTH_DEFAULT_M: float = 0.8


# ---------------------------------------------------------------------------
# T4 computed accessors
# ---------------------------------------------------------------------------

def yield_per_m2(
    yield_per_bed_m: float | Decimal | None,
    bed_width_m: float = BED_WIDTH_DEFAULT_M,
) -> Optional[float]:
    """T4: yield per m² = yield_per_bed_m / bed_width_m.

    Canon §6.4: yield_per_m2 = yield_per_bed_m / bed_width (AssumptionField 0.8).
    Returns None if yield_per_bed_m is None or bed_width_m is 0.
    """
    if yield_per_bed_m is None:
        return None
    bw = float(bed_width_m)
    if bw == 0:
        return None
    return float(yield_per_bed_m) / bw


def p2o5_from_p(
    p_kg_per_ha: float | Decimal | None,
) -> Optional[float]:
    """T4: P2O5 = P × 2.29 (Canon §6.4).

    Returns None if p_kg_per_ha is None.
    """
    if p_kg_per_ha is None:
        return None
    return float(p_kg_per_ha) * 2.29


def k2o_from_k(
    k_kg_per_ha: float | Decimal | None,
) -> Optional[float]:
    """T4: K2O = K × 1.205 (Canon §6.4).

    Returns None if k_kg_per_ha is None.
    """
    if k_kg_per_ha is None:
        return None
    return float(k_kg_per_ha) * 1.205


def plants_per_m2(
    rows_per_bed: float | Decimal | None,
    spacing_in_row_cm: float | Decimal | None,
    bed_width_m: float = BED_WIDTH_DEFAULT_M,
) -> Optional[float]:
    """T4: plants_per_m2 = rows_per_bed × (100 / spacing_in_row_cm) / bed_width_m.

    Canon §6.4: plants_per_m2 from rows/spacing/bed_width.
    spacing_in_row_cm is the in-row spacing in centimeters.
    Returns None if any required input is None or zero.
    """
    if rows_per_bed is None or spacing_in_row_cm is None:
        return None
    r = float(rows_per_bed)
    s_cm = float(spacing_in_row_cm)
    bw = float(bed_width_m)
    if s_cm <= 0 or bw <= 0:
        return None
    # plants per linear bed-meter = rows × (100 / spacing_cm)
    # plants per m² = plants_per_bed_m / bed_width
    plants_per_bed_m = r * (100.0 / s_cm)
    return plants_per_bed_m / bw


def revenue_per_bed_m(
    yield_per_bed_m_val: float | Decimal | None,
    price: float | Decimal | None,
) -> Optional[float]:
    """T4: revenue_per_bed_m = yield_per_bed_m × price.

    Canon §6.4.
    Returns None if either input is None.
    """
    if yield_per_bed_m_val is None or price is None:
        return None
    return float(yield_per_bed_m_val) * float(price)
