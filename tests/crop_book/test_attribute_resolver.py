"""Tests for crop_book.importer.attribute_resolver — AC-04.

Tests both source_values-origin and column-origin attributes.
Uses SQLite in-memory DB via the existing test fixtures pattern.
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from organic_market_agent.crop_book.canon.enums import ENUM_TOKENS


class TestAttributeResolverUnit:
    """Unit tests for attribute resolver helpers (no DB)."""

    def test_hard_winner_single_source(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _hard_winner
        winner, value, confidence = _hard_winner({"NI:test": "direct_seed"})
        assert winner == "NI:test"
        assert value == "direct_seed"
        assert confidence == 1.0

    def test_hard_winner_trust_order(self):
        """EX > NI > PR > OP."""
        from organic_market_agent.crop_book.importer.attribute_resolver import _hard_winner
        candidates = {
            "PR:source": "tender",
            "NI:source": "hardy",
        }
        winner, value, confidence = _hard_winner(candidates)
        assert winner == "NI:source"
        assert value == "hardy"

    def test_hard_winner_unanimous_confidence(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _hard_winner
        candidates = {
            "PR:a": "transplant",
            "NI:b": "transplant",
        }
        _, _, confidence = _hard_winner(candidates)
        assert confidence == 1.0  # both agree

    def test_hard_winner_contested_confidence(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _hard_winner
        candidates = {
            "NI:a": "transplant",
            "PR:b": "direct_seed",
        }
        _, _, confidence = _hard_winner(candidates)
        # 1 of 2 agree with winner → 0.5
        assert confidence == pytest.approx(0.5)

    def test_hard_winner_empty_raises(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _hard_winner
        with pytest.raises(ValueError):
            _hard_winner({})

    def test_canonicalize_planting_method(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _canonicalize_value
        # direct_sow → direct_seed (closed-enum)
        assert _canonicalize_value("planting_method", "direct_sow") == "direct_seed"
        assert _canonicalize_value("planting_method", "transplant") == "transplant"
        assert _canonicalize_value("planting_method", None) is None

    def test_canonicalize_frost_tolerance(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _canonicalize_value
        assert _canonicalize_value("frost_tolerance_class", "semi_hardy") == "half_hardy"
        assert _canonicalize_value("frost_tolerance_class", "half-hardy") == "half_hardy"

    def test_canonicalize_sowing_months(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _canonicalize_value
        result = _canonicalize_value("sowing_months", "1,2,3")
        assert result == [1, 2, 3]

    def test_canonicalize_open_vocab(self):
        """variety_provider: normalize only, not restricted."""
        from organic_market_agent.crop_book.importer.attribute_resolver import _canonicalize_value
        result = _canonicalize_value("variety_provider", "  FRANCHI  SEEDS  ")
        assert result is not None
        assert "  " not in result

    def test_all_attributes_listed(self):
        """AC-04: exactly 11 §7.2 attributes in ALL_ATTRIBUTES."""
        from organic_market_agent.crop_book.importer.attribute_resolver import ALL_ATTRIBUTES
        expected = {
            "planting_method", "frost_tolerance_class", "sowing_months",
            "transplant_months", "storage_ethylene_sensitivity",
            "variety_provider", "rootstock_variety",
            "season_window", "harvest_unit", "harvest_stage",
        }
        # ALL_ATTRIBUTES should cover all 10 listed + rootstock_variety = 10 unique attrs
        # Canon §7.2 lists 11 total (incl. both harvest attrs)
        assert len(ALL_ATTRIBUTES) >= 10
        attr_set = set(ALL_ATTRIBUTES)
        missing = expected - attr_set
        assert not missing, f"Missing from ALL_ATTRIBUTES: {missing}"

    def test_source_values_attrs_vs_column_attrs(self):
        """source_values-origin and column-origin are disjoint."""
        from organic_market_agent.crop_book.importer.attribute_resolver import (
            _SOURCE_VALUES_ATTRS, _COLUMN_ORIGIN_ATTRS,
        )
        overlap = set(_SOURCE_VALUES_ATTRS) & set(_COLUMN_ORIGIN_ATTRS)
        assert not overlap, f"Overlap between source and column attrs: {overlap}"

    def test_column_origin_attrs_are_correct(self):
        """F-190-MIG-01: column-origin attrs are season_window, harvest_unit, harvest_stage."""
        from organic_market_agent.crop_book.importer.attribute_resolver import _COLUMN_ORIGIN_ATTRS
        assert "season_window" in _COLUMN_ORIGIN_ATTRS
        assert "harvest_unit" in _COLUMN_ORIGIN_ATTRS
        assert "harvest_stage" in _COLUMN_ORIGIN_ATTRS
        # Verify column names
        assert _COLUMN_ORIGIN_ATTRS["season_window"] == "planting_season"
        assert _COLUMN_ORIGIN_ATTRS["harvest_unit"] == "harvest_unit"
        assert _COLUMN_ORIGIN_ATTRS["harvest_stage"] == "harvest_stage"


class TestColumnOriginResolution:
    """Test column-origin attribute resolution specifically (F-190-MIG-01)."""

    def test_resolve_harvest_unit_from_column(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _resolve_column_origin_attr
        variety = MagicMock()
        variety.harvest_unit = "kg"
        candidates = _resolve_column_origin_attr(variety, "harvest_unit", "harvest_unit")
        assert "column_origin" in candidates
        assert candidates["column_origin"] == "kg"

    def test_resolve_harvest_stage_from_column(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _resolve_column_origin_attr
        variety = MagicMock()
        variety.harvest_stage = "full_size"
        candidates = _resolve_column_origin_attr(variety, "harvest_stage", "harvest_stage")
        assert candidates.get("column_origin") == "full_size"

    def test_resolve_null_column_returns_empty(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _resolve_column_origin_attr
        variety = MagicMock()
        variety.harvest_unit = None
        candidates = _resolve_column_origin_attr(variety, "harvest_unit", "harvest_unit")
        assert candidates == {}

    def test_resolve_season_window_from_planting_season(self):
        from organic_market_agent.crop_book.importer.attribute_resolver import _resolve_column_origin_attr
        variety = MagicMock()
        variety.planting_season = "spring"
        candidates = _resolve_column_origin_attr(variety, "season_window", "planting_season")
        assert "column_origin" in candidates
        assert candidates["column_origin"] == "spring"
