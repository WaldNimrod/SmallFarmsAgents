"""Tests for WP-CB-MIG2 field_registry entries (WI-8b / AC-17)."""
import pytest

from organic_market_agent.crop_book.canon.field_registry import (
    FIELD_REGISTRY,
    ALIAS_MAP,
    get_canonical,
)


class TestMig2FieldRegistry:
    """AC-17: FIELD_REGISTRY registers every §16 field."""

    # T5 columns
    def test_seeder_settings_registered(self):
        meta = FIELD_REGISTRY["seeder_settings"]
        assert meta.field_type == "T5"
        assert meta.layer == "column"
        assert meta.canonical == "seeder_settings"

    def test_seeder_model_alias_registered(self):
        meta = FIELD_REGISTRY["seeder_model"]
        assert meta.canonical == "seeder"
        assert meta.disposition == "ALIAS"

    def test_seeder_model_in_alias_map(self):
        """get_canonical('seeder_model') resolves to 'seeder'."""
        assert get_canonical("seeder_model") == "seeder"

    # T1 enrichment facts
    def test_drip_lines_per_bed_t1(self):
        meta = FIELD_REGISTRY["drip_lines_per_bed"]
        assert meta.field_type == "T1"
        assert meta.layer == "enrichment"
        assert meta.unit == "count"

    def test_labor_rate_harvest_t1(self):
        meta = FIELD_REGISTRY["labor_rate_harvest"]
        assert meta.field_type == "T1"
        assert meta.unit == "units_per_hr"

    def test_labor_rate_wash_t1(self):
        meta = FIELD_REGISTRY["labor_rate_wash"]
        assert meta.field_type == "T1"
        assert meta.unit == "units_per_hr"

    def test_plantings_per_season_t1(self):
        meta = FIELD_REGISTRY["plantings_per_season"]
        assert meta.field_type == "T1"
        assert meta.unit == "count"

    def test_harvest_weeks_span_t1(self):
        meta = FIELD_REGISTRY["harvest_weeks_span"]
        assert meta.field_type == "T1"
        assert meta.unit == "weeks"

    # T2/T3 crop_attribute
    def test_irrigation_type_t2(self):
        meta = FIELD_REGISTRY["irrigation_type"]
        assert meta.field_type == "T2"
        assert meta.layer == "crop_attribute"

    def test_root_depth_class_t2(self):
        meta = FIELD_REGISTRY["root_depth_class"]
        assert meta.field_type == "T2"
        assert meta.layer == "crop_attribute"

    def test_needs_summer_shade_t2(self):
        meta = FIELD_REGISTRY["needs_summer_shade"]
        assert meta.field_type == "T2"
        assert meta.layer == "crop_attribute"

    def test_unit_size_t2(self):
        meta = FIELD_REGISTRY["unit_size"]
        assert meta.field_type == "T2"
        assert meta.layer == "crop_attribute"

    def test_common_pests_t3(self):
        meta = FIELD_REGISTRY["common_pests"]
        assert meta.field_type == "T3"
        assert meta.layer == "crop_attribute"

    def test_foliar_feeding_program_t2(self):
        meta = FIELD_REGISTRY["foliar_feeding_program"]
        assert meta.field_type == "T2"
        assert meta.layer == "crop_attribute"

    # Aliases
    def test_sale_unit_alias_to_harvest_unit(self):
        """AC-05 / D-MIG2-1: sale_unit → harvest_unit via ALIAS."""
        meta = FIELD_REGISTRY["sale_unit"]
        assert meta.canonical == "harvest_unit"
        assert meta.disposition == "ALIAS"
        assert get_canonical("sale_unit") == "harvest_unit"

    def test_sale_unit_in_alias_map(self):
        assert ALIAS_MAP.get("sale_unit") == "harvest_unit"

    def test_seeder_model_alias_map(self):
        assert ALIAS_MAP.get("seeder_model") == "seeder"

    def test_get_canonical_sale_unit(self):
        """AC-05 / AC-17: get_canonical resolves sale_unit → harvest_unit."""
        assert get_canonical("sale_unit") == "harvest_unit"

    def test_get_canonical_seeder_model(self):
        """AC-17: get_canonical resolves seeder_model → seeder."""
        assert get_canonical("seeder_model") == "seeder"

    def test_no_resolver_entry_needed_for_aliases(self):
        """D-MIG2-1: aliases should NOT have their own resolver entries (verified by convention)."""
        # sale_unit and seeder_model are aliases — they must not appear in _SOURCE_VALUES_ATTRS
        from organic_market_agent.crop_book.importer.attribute_resolver import _SOURCE_VALUES_ATTRS
        assert "sale_unit" not in _SOURCE_VALUES_ATTRS, \
            "sale_unit should be an alias, not a resolver entry"
        assert "seeder_model" not in _SOURCE_VALUES_ATTRS, \
            "seeder_model should be an alias, not a resolver entry"
