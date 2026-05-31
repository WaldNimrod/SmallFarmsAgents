"""Tests for crop_book.canon.enums — ENUM_TOKENS + ENUM_COLLAPSE + canonicalize_enum()."""
import pytest

from organic_market_agent.crop_book.canon.enums import (
    canonicalize_enum,
    parse_month_list,
    ENUM_TOKENS,
    ENUM_COLLAPSE,
    OPEN_VOCAB_ATTRS,
)


class TestCanonicalizeEnum:
    """AC-01 / AC-03: enum collapse + closed-enum validation."""

    # --- planting_method ---
    def test_direct_sow_to_direct_seed(self):
        """Canon §6.3 collapse: direct_sow → direct_seed."""
        assert canonicalize_enum("planting_method", "direct_sow") == "direct_seed"

    def test_planting_method_canonical_passthrough(self):
        for val in ("direct_seed", "transplant", "seed_tuber", "slip", "cutting"):
            assert canonicalize_enum("planting_method", val) == val

    # --- frost_tolerance_class ---
    def test_semi_hardy_to_half_hardy(self):
        """Canon §6.3 + R2 errata: semi_hardy → half_hardy."""
        assert canonicalize_enum("frost_tolerance_class", "semi_hardy") == "half_hardy"

    def test_half_hardy_hyphen_to_underscore(self):
        """Canon §6.3 R2 errata: half-hardy (hyphen) → half_hardy."""
        assert canonicalize_enum("frost_tolerance_class", "half-hardy") == "half_hardy"

    def test_frost_tolerance_canonical_passthrough(self):
        for val in ("hardy", "half_hardy", "tender", "very_tender"):
            assert canonicalize_enum("frost_tolerance_class", val) == val

    # --- storage_ethylene_sensitivity ---
    def test_ethylene_sensitivity_canonical(self):
        for val in ("none", "low", "medium", "high"):
            assert canonicalize_enum("storage_ethylene_sensitivity", val) == val

    # --- harvest_unit / harvest_stage ---
    def test_harvest_unit_canonical(self):
        for val in ("kg", "bunch", "head", "case", "unit", "seedling"):
            assert canonicalize_enum("harvest_unit", val) == val

    def test_harvest_stage_canonical(self):
        for val in ("full_size", "baby_leaf", "head", "plant_sale", "seed"):
            assert canonicalize_enum("harvest_stage", val) == val

    # --- None / blank ---
    def test_none_returns_none(self):
        assert canonicalize_enum("planting_method", None) is None
        assert canonicalize_enum("frost_tolerance_class", None) is None

    def test_blank_returns_none(self):
        assert canonicalize_enum("planting_method", "") is None
        assert canonicalize_enum("planting_method", "  ") is None

    # --- Open-vocab (F-190-MIG-04 / AC-03) ---
    def test_open_vocab_not_restricted(self):
        """variety_provider and rootstock_variety accept free text."""
        result = canonicalize_enum("variety_provider", "FRANCHI SEEDS Ltd.")
        assert result is not None  # just normalized, not rejected
        assert isinstance(result, str)

    def test_open_vocab_normalize_case_and_whitespace(self):
        raw = "  FRANCHI   SEEDS  LTD.  "
        result = canonicalize_enum("variety_provider", raw)
        assert result is not None
        assert "  " not in result  # no double spaces
        assert result == result.strip()

    def test_open_vocab_attrs_set(self):
        assert "variety_provider" in OPEN_VOCAB_ATTRS
        assert "rootstock_variety" in OPEN_VOCAB_ATTRS
        assert "planting_method" not in OPEN_VOCAB_ATTRS

    # --- ENUM_TOKENS sanity ---
    def test_enum_tokens_all_expected(self):
        assert "planting_method" in ENUM_TOKENS
        assert "frost_tolerance_class" in ENUM_TOKENS
        assert "harvest_unit" in ENUM_TOKENS
        assert "harvest_stage" in ENUM_TOKENS
        assert "storage_ethylene_sensitivity" in ENUM_TOKENS
        # open-vocab not in ENUM_TOKENS
        assert "variety_provider" not in ENUM_TOKENS
        assert "rootstock_variety" not in ENUM_TOKENS


class TestParseMonthList:
    """Month CSV → int array (Canon §6.3)."""

    def test_basic_csv(self):
        assert parse_month_list("2,3,5") == [2, 3, 5]

    def test_sorted_deduped(self):
        assert parse_month_list("5,3,3,1") == [1, 3, 5]

    def test_none_returns_none(self):
        assert parse_month_list(None) is None

    def test_blank_returns_none(self):
        assert parse_month_list("") is None

    def test_full_year(self):
        result = parse_month_list("1,2,3,4,5,6,7,8,9,10,11,12")
        assert result == list(range(1, 13))

    def test_drops_out_of_range(self):
        result = parse_month_list("0,1,12,13")
        assert result == [1, 12]

    def test_real_world_value(self):
        """Values from the actual DB."""
        assert parse_month_list("1,2,9,10,11,12") == [1, 2, 9, 10, 11, 12]
        assert parse_month_list("1,2,3,4,5,9,10,11,12") == [1, 2, 3, 4, 5, 9, 10, 11, 12]
