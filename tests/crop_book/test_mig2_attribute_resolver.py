"""Tests for MIG2 attribute resolver entries (WI-3 / AC-04)."""
import pytest

from organic_market_agent.crop_book.importer.attribute_resolver import (
    _SOURCE_VALUES_ATTRS,
    _canonicalize_value,
)


class TestMig2AttributeResolverEntries:
    """AC-04: New T2/T3 attrs in _SOURCE_VALUES_ATTRS."""

    def test_irrigation_type_in_source_values_attrs(self):
        assert "irrigation_type" in _SOURCE_VALUES_ATTRS
        assert _SOURCE_VALUES_ATTRS["irrigation_type"] == "irrigation_type"

    def test_root_depth_class_in_source_values_attrs(self):
        assert "root_depth_class" in _SOURCE_VALUES_ATTRS

    def test_needs_summer_shade_in_source_values_attrs(self):
        assert "needs_summer_shade" in _SOURCE_VALUES_ATTRS

    def test_common_pests_in_source_values_attrs(self):
        """T3 list attr."""
        assert "common_pests" in _SOURCE_VALUES_ATTRS

    def test_foliar_feeding_program_in_source_values_attrs(self):
        assert "foliar_feeding_program" in _SOURCE_VALUES_ATTRS

    def test_unit_size_in_source_values_attrs(self):
        assert "unit_size" in _SOURCE_VALUES_ATTRS

    def test_sale_unit_not_in_source_values_attrs(self):
        """AC-05: sale_unit is an alias — no resolver entry."""
        assert "sale_unit" not in _SOURCE_VALUES_ATTRS

    def test_seeder_model_not_in_source_values_attrs(self):
        """D-MIG2-2: seeder_model is an alias — no resolver entry."""
        assert "seeder_model" not in _SOURCE_VALUES_ATTRS


class TestMig2AttributeCanonicalization:
    """AC-03/AC-04: canonicalize_value for new attrs."""

    def test_irrigation_type_drip(self):
        assert _canonicalize_value("irrigation_type", "drip") == "drip"

    def test_irrigation_type_invalid(self):
        """Out-of-set → returned (but DQ-logged); value passes through."""
        result = _canonicalize_value("irrigation_type", "flood")
        assert result == "flood"  # passes through; DQ logged

    def test_root_depth_class_deep(self):
        assert _canonicalize_value("root_depth_class", "deep") == "deep"

    def test_needs_summer_shade_none(self):
        assert _canonicalize_value("needs_summer_shade", "none") == "none"

    def test_needs_summer_shade_shade_30(self):
        assert _canonicalize_value("needs_summer_shade", "shade_30") == "shade_30"
        assert _canonicalize_value("needs_summer_shade", "30%") == "shade_30"

    def test_common_pests_returns_list(self):
        """T3 open-vocab: common_pests → list via parse_list_attr."""
        result = _canonicalize_value("common_pests", "aphids, whitefly, mites")
        assert isinstance(result, list)
        assert "aphids" in result
        assert "whitefly" in result

    def test_common_pests_none_returns_none(self):
        assert _canonicalize_value("common_pests", None) is None

    def test_foliar_feeding_program_open_vocab(self):
        result = _canonicalize_value("foliar_feeding_program", "  COMPOST TEA  ")
        assert result == "compost tea"

    def test_unit_size_open_vocab(self):
        result = _canonicalize_value("unit_size", "  6-7 Stems  ")
        assert result == "6-7 stems"
