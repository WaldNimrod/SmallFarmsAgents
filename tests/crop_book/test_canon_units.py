"""Tests for crop_book.canon.units — UNIT_VARIANT_MAP + normalize_unit()."""
import pytest

from organic_market_agent.crop_book.canon.units import (
    normalize_unit,
    ALL_CANONICAL_UNITS,
    UNIT_VARIANT_MAP,
)


class TestNormalizeUnit:
    """AC-01 / AC-02: normalize_unit() returns canonical strings."""

    def test_celsius_variants_to_celsius(self):
        for field in ("germination_temp_c_min", "germination_temp_c_opt",
                      "germination_temp_c_max", "storage_temp_c_min", "storage_temp_c_max"):
            assert normalize_unit(field, "celsius") == "°C"
            assert normalize_unit(field, "C") == "°C"
            assert normalize_unit(field, "°C") == "°C"
            assert normalize_unit(field, None) == "°C"

    def test_bare_kg_yield_to_kg_per_bed_m(self):
        """Canon §6.1 errata F-190-CB0-03: bare 'kg' on yield field → kg_per_bed_m."""
        assert normalize_unit("avg_yield_per_bed_m", "kg") == "kg_per_bed_m"
        assert normalize_unit("avg_yield_per_bed_m", "kg/m") == "kg_per_bed_m"
        assert normalize_unit("avg_yield_per_bed_m", None) == "kg_per_bed_m"

    def test_rows_to_count(self):
        assert normalize_unit("rows_per_bed", "rows") == "count"
        assert normalize_unit("rows_per_bed", None) == "count"
        assert normalize_unit("rows_per_bed", "") == "count"
        assert normalize_unit("rows_per_bed", "count") == "count"

    def test_ph_blank_to_ph(self):
        assert normalize_unit("soil_ph_target", None) == "pH"
        assert normalize_unit("soil_ph_target", "") == "pH"
        assert normalize_unit("soil_ph_target", "pH") == "pH"
        assert normalize_unit("soil_ph_liming_threshold", None) == "pH"

    def test_kg_per_ha_nutrients(self):
        for f in ("nutrient_removal_n_kg_ha", "nutrient_removal_p_kg_ha",
                  "nutrient_removal_k_kg_ha", "nutrient_removal_ca_kg_ha",
                  "nutrient_removal_mg_kg_ha"):
            assert normalize_unit(f, "kg/ha") == "kg_per_ha"
            assert normalize_unit(f, "kg_per_ha") == "kg_per_ha"

    def test_seeds_per_g(self):
        assert normalize_unit("seeds_per_gram", "seeds/g") == "seeds_per_g"
        assert normalize_unit("seeds_per_gram", "seeds_per_g") == "seeds_per_g"

    def test_price_qualifier_preserved(self):
        assert normalize_unit("documented_price", "ILS/kg") == "ILS_per_kg"
        assert normalize_unit("documented_price", "ILS/bunch") == "ILS_per_bunch"
        assert normalize_unit("documented_price", "ILS/unit") == "ILS_per_unit"

    def test_pct_from_percent(self):
        assert normalize_unit("storage_rh_pct_min", "%") == "pct"
        assert normalize_unit("storage_rh_pct_max", "%") == "pct"

    def test_unknown_field_passthrough(self):
        """Unknown fields return unit unchanged."""
        assert normalize_unit("unknown_field", "some_unit") == "some_unit"
        assert normalize_unit("unknown_field", None) == ""

    def test_canonical_units_valid_set(self):
        """ALL_CANONICAL_UNITS contains the expected units."""
        assert "°C" in ALL_CANONICAL_UNITS
        assert "kg_per_bed_m" in ALL_CANONICAL_UNITS
        assert "kg_per_ha" in ALL_CANONICAL_UNITS
        assert "seeds_per_g" in ALL_CANONICAL_UNITS
        assert "pct" in ALL_CANONICAL_UNITS
        assert "count" in ALL_CANONICAL_UNITS

    def test_idempotent(self):
        """Applying normalize_unit twice returns same result."""
        for field, unit in [
            ("germination_temp_c_min", "celsius"),
            ("avg_yield_per_bed_m", "kg"),
            ("rows_per_bed", "rows"),
            ("soil_ph_target", None),
        ]:
            first = normalize_unit(field, unit)
            second = normalize_unit(field, first)
            assert first == second, f"Not idempotent for ({field!r}, {unit!r})"
