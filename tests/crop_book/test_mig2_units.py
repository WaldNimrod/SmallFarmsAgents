"""Tests for MIG2 units registry (WI-5b / AC-06b)."""
import pytest

from organic_market_agent.crop_book.canon.units import (
    UNIT_REGISTRY,
    UNIT_VARIANT_MAP,
    ALL_CANONICAL_UNITS,
    normalize_unit,
)


class TestMig2UnitsRegistry:
    """AC-06b: every new T1 field's unit ∈ UNIT_REGISTRY."""

    def test_labor_rate_dimension_in_registry(self):
        """WI-5b: labor_rate dimension added with canonical 'units_per_hr'."""
        assert "labor_rate" in UNIT_REGISTRY
        assert UNIT_REGISTRY["labor_rate"] == "units_per_hr"

    def test_units_per_hr_in_all_canonical_units(self):
        assert "units_per_hr" in ALL_CANONICAL_UNITS

    def test_t1_fields_have_registry_units(self):
        """Each new T1 field resolves to a known canonical unit."""
        field_expected = {
            "drip_lines_per_bed": "count",
            "plantings_per_season": "count",
            "harvest_weeks_span": "weeks",
            "labor_rate_harvest": "units_per_hr",
            "labor_rate_wash": "units_per_hr",
        }
        for field, expected_unit in field_expected.items():
            assert expected_unit in ALL_CANONICAL_UNITS, \
                f"unit {expected_unit!r} for field {field!r} not in ALL_CANONICAL_UNITS"

    def test_normalize_unit_labor_rate(self):
        assert normalize_unit("labor_rate_harvest", "units_per_hr") == "units_per_hr"
        assert normalize_unit("labor_rate_harvest", "units/hr") == "units_per_hr"
        assert normalize_unit("labor_rate_wash", None) == "units_per_hr"

    def test_normalize_unit_drip_lines(self):
        assert normalize_unit("drip_lines_per_bed", "count") == "count"
        assert normalize_unit("drip_lines_per_bed", None) == "count"

    def test_normalize_unit_harvest_weeks_span(self):
        assert normalize_unit("harvest_weeks_span", "weeks") == "weeks"
        assert normalize_unit("harvest_weeks_span", None) == "weeks"

    def test_normalize_unit_plantings_per_season(self):
        assert normalize_unit("plantings_per_season", "count") == "count"
        assert normalize_unit("plantings_per_season", None) == "count"

    def test_mig2_fields_in_unit_variant_map(self):
        """All new T1 fields have per-field variant maps."""
        for field in ("drip_lines_per_bed", "plantings_per_season",
                      "harvest_weeks_span", "labor_rate_harvest", "labor_rate_wash"):
            assert field in UNIT_VARIANT_MAP, f"{field!r} missing from UNIT_VARIANT_MAP"
