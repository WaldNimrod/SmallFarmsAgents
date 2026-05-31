"""Tests for crop_book.canon.derive — T4 computed accessors."""
import pytest
from decimal import Decimal

from organic_market_agent.crop_book.canon.derive import (
    yield_per_m2,
    p2o5_from_p,
    k2o_from_k,
    plants_per_m2,
    revenue_per_bed_m,
    BED_WIDTH_DEFAULT_M,
)


class TestYieldPerM2:
    """AC-05: yield_per_m2 = yield_per_bed_m / bed_width_m."""

    def test_default_bed_width(self):
        result = yield_per_m2(4.0)
        assert abs(result - 4.0 / 0.8) < 1e-9

    def test_custom_bed_width(self):
        result = yield_per_m2(4.0, bed_width_m=1.0)
        assert abs(result - 4.0) < 1e-9

    def test_none_returns_none(self):
        assert yield_per_m2(None) is None

    def test_zero_bed_width_returns_none(self):
        assert yield_per_m2(10.0, bed_width_m=0) is None

    def test_decimal_input(self):
        result = yield_per_m2(Decimal("3.2"))
        assert result is not None
        assert abs(result - 3.2 / 0.8) < 1e-9

    def test_bed_width_default_is_0_8(self):
        assert BED_WIDTH_DEFAULT_M == 0.8


class TestOxideFromElemental:
    """AC-05: P2O5 = P × 2.29, K2O = K × 1.205."""

    def test_p2o5_factor(self):
        result = p2o5_from_p(100.0)
        assert abs(result - 229.0) < 1e-9

    def test_p2o5_none(self):
        assert p2o5_from_p(None) is None

    def test_p2o5_decimal(self):
        result = p2o5_from_p(Decimal("50"))
        assert abs(result - 50 * 2.29) < 1e-9

    def test_k2o_factor(self):
        result = k2o_from_k(100.0)
        assert abs(result - 120.5) < 1e-9

    def test_k2o_none(self):
        assert k2o_from_k(None) is None

    def test_k2o_decimal(self):
        result = k2o_from_k(Decimal("80"))
        assert abs(result - 80 * 1.205) < 1e-9


class TestPlantsPerM2:
    """AC-05: plants_per_m2 from rows/spacing/bed_width."""

    def test_basic_calculation(self):
        # 4 rows, 25 cm spacing, 0.8 m bed
        # plants_per_bed_m = 4 × (100/25) = 16
        # plants_per_m2 = 16 / 0.8 = 20
        result = plants_per_m2(4, 25, bed_width_m=0.8)
        assert abs(result - 20.0) < 1e-9

    def test_none_rows_returns_none(self):
        assert plants_per_m2(None, 25) is None

    def test_none_spacing_returns_none(self):
        assert plants_per_m2(4, None) is None

    def test_zero_spacing_returns_none(self):
        assert plants_per_m2(4, 0) is None

    def test_decimal_inputs(self):
        result = plants_per_m2(Decimal("4"), Decimal("25"))
        assert result is not None
        assert abs(result - 20.0) < 1e-9


class TestRevenuePerBedM:
    """AC-05: revenue_per_bed_m = yield × price."""

    def test_basic(self):
        assert revenue_per_bed_m(5.0, 10.0) == pytest.approx(50.0)

    def test_none_yield_returns_none(self):
        assert revenue_per_bed_m(None, 10.0) is None

    def test_none_price_returns_none(self):
        assert revenue_per_bed_m(5.0, None) is None

    def test_decimal_inputs(self):
        result = revenue_per_bed_m(Decimal("5.0"), Decimal("10.0"))
        assert abs(result - 50.0) < 1e-9
