"""Tests for MIG2 enums (WI-2 / AC-03)."""
import pytest

from organic_market_agent.crop_book.canon.enums import (
    canonicalize_enum,
    ENUM_TOKENS,
    OPEN_VOCAB_ATTRS,
    parse_list_attr,
)


class TestMig2ClosedEnums:
    """AC-03: New closed enums in ENUM_TOKENS; out-of-set tokens rejected."""

    # --- irrigation_type ---
    def test_irrigation_type_tokens_in_registry(self):
        assert "irrigation_type" in ENUM_TOKENS
        assert ENUM_TOKENS["irrigation_type"] == frozenset({"drip", "sprinkler", "mixed"})

    def test_irrigation_type_canonical_passthrough(self):
        for val in ("drip", "sprinkler", "mixed"):
            assert canonicalize_enum("irrigation_type", val) == val

    def test_irrigation_type_alias_normalization(self):
        assert canonicalize_enum("irrigation_type", "drip_irrigation") == "drip"
        assert canonicalize_enum("irrigation_type", "sprinkler_irrigation") == "sprinkler"

    def test_irrigation_type_out_of_set_logs_warning(self, caplog):
        """Out-of-set tokens are logged as DQ warnings (not hard-rejected by function)."""
        import logging
        with caplog.at_level(logging.WARNING):
            result = canonicalize_enum("irrigation_type", "flood")
        # Result is returned (caller decides), but warning is logged
        assert "flood" in str(result) or result == "flood"
        # Check warning was logged
        assert any("DQ" in r.message or "flood" in r.message for r in caplog.records)

    # --- root_depth_class ---
    def test_root_depth_class_tokens_in_registry(self):
        assert "root_depth_class" in ENUM_TOKENS
        assert ENUM_TOKENS["root_depth_class"] == frozenset({"shallow", "medium", "deep"})

    def test_root_depth_class_canonical_passthrough(self):
        for val in ("shallow", "medium", "deep"):
            assert canonicalize_enum("root_depth_class", val) == val

    # --- needs_summer_shade ---
    def test_needs_summer_shade_tokens_in_registry(self):
        assert "needs_summer_shade" in ENUM_TOKENS
        assert ENUM_TOKENS["needs_summer_shade"] == frozenset({
            "none", "shade_30", "shade_40", "shade_50"
        })

    def test_needs_summer_shade_canonical_passthrough(self):
        for val in ("none", "shade_30", "shade_40", "shade_50"):
            assert canonicalize_enum("needs_summer_shade", val) == val

    def test_needs_summer_shade_pct_normalization(self):
        """Percent variants collapse to shade_XX."""
        assert canonicalize_enum("needs_summer_shade", "30%") == "shade_30"
        assert canonicalize_enum("needs_summer_shade", "40%") == "shade_40"
        assert canonicalize_enum("needs_summer_shade", "50%") == "shade_50"


class TestMig2OpenVocabAttrs:
    """AC-03: Open-vocab attrs normalize but do not restrict."""

    def test_open_vocab_attrs_registered(self):
        for attr in ("common_pests", "foliar_feeding_program", "unit_size"):
            assert attr in OPEN_VOCAB_ATTRS, f"{attr!r} missing from OPEN_VOCAB_ATTRS"

    def test_common_pests_normalizes(self):
        """Common pests: open-vocab, processed via parse_list_attr."""
        result = parse_list_attr("  Aphids, Whitefly , Mites  ", "common_pests")
        assert result is not None
        assert "aphids" in result
        assert "whitefly" in result
        assert "mites" in result

    def test_common_pests_dedup(self):
        result = parse_list_attr("aphids, aphids, whitefly", "common_pests")
        assert result is not None
        assert result.count("aphids") == 1

    def test_parse_list_attr_returns_none_on_blank(self):
        assert parse_list_attr(None, "common_pests") is None
        assert parse_list_attr("", "common_pests") is None
        assert parse_list_attr("  ,  ,  ", "common_pests") is None

    def test_unit_size_free_text(self):
        """unit_size: accepts free text, normalizes only."""
        result = canonicalize_enum("unit_size", "  6-7 STEMS  ")
        assert result == "6-7 stems"

    def test_foliar_feeding_program_free_text(self):
        result = canonicalize_enum("foliar_feeding_program", "  Weekly BioStimulant  ")
        assert result == "weekly biostimulant"

    def test_sale_unit_not_in_open_vocab_or_enum_tokens(self):
        """D-MIG2-1: sale_unit has NO enum entry (it's a FieldRegistry alias to harvest_unit)."""
        assert "sale_unit" not in ENUM_TOKENS
        assert "sale_unit" not in OPEN_VOCAB_ATTRS
