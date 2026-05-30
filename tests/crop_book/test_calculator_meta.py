"""Tests for calculator_meta.py — WP-CB-1 AC-07/AC-08 / LOD400 §5.

AC-07: required_book_fields map equals Catalog §6.
AC-08: calc_enabled correctly reflects MISSING vs UNVALIDATED/VALIDATED.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Hard-coded expected map from Calculator Catalog §6
# ---------------------------------------------------------------------------

_EXPECTED_REQUIRED_BOOK_FIELDS: dict[int, list[str]] = {
    1: ["rows_per_bed", "in_row_spacing_cm", "seeds_per_gram"],
    2: ["rows_per_bed", "in_row_spacing_cm"],
    3: ["days_in_nursery_cell"],
    4: ["days_to_maturity", "planting_method"],
    5: ["days_to_maturity", "harvest_window_max_days", "planting_method"],
    6: ["succession_interval_weeks"],
    7: ["avg_yield_per_bed_m"],
    8: ["avg_yield_per_bed_m"],
    9: ["avg_yield_per_bed_m", "documented_price", "documented_price_unit"],
    10: ["rows_per_bed", "in_row_spacing_cm"],
    11: ["days_to_maturity", "frost_tolerance_class"],
    12: ["nutrient_removal_n_kg_ha"],
    13: ["avg_yield_per_bed_m", "documented_price"],
    14: [],
}


def test_required_book_fields_map_equals_catalog() -> None:
    """AC-07: required_book_fields in CALCULATOR_META must equal the Catalog §6 map."""
    from organic_market_agent.crop_book.calculator_meta import CALCULATOR_META

    for calc_id, expected_fields in _EXPECTED_REQUIRED_BOOK_FIELDS.items():
        actual = set(CALCULATOR_META[calc_id]["required_book_fields"])
        expected = set(expected_fields)
        assert actual == expected, (
            f"Calc #{calc_id} required_book_fields mismatch: "
            f"got {actual}, expected {expected}"
        )


def test_all_14_calcs_present() -> None:
    from organic_market_agent.crop_book.calculator_meta import CALCULATOR_META

    assert set(CALCULATOR_META.keys()) == set(range(1, 15))


def test_audience_values_valid() -> None:
    from organic_market_agent.crop_book.calculator_meta import CALCULATOR_META

    valid_audiences = {"G", "F", "B"}
    for calc_id, meta in CALCULATOR_META.items():
        assert meta["audience"] in valid_audiences, (
            f"Calc #{calc_id} has invalid audience '{meta['audience']}'"
        )


# ---------------------------------------------------------------------------
# calc_enabled: enabled/disabled state (AC-08)
# ---------------------------------------------------------------------------

def test_calc_enabled_all_validated() -> None:
    """Calc is enabled when all required book fields are VALIDATED."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    field_state = {
        "rows_per_bed": "VALIDATED",
        "in_row_spacing_cm": "VALIDATED",
        "seeds_per_gram": "VALIDATED",
    }
    assert calc_enabled(1, field_state) is True


def test_calc_enabled_all_unvalidated() -> None:
    """Calc is enabled (flagged) when fields are UNVALIDATED — not disabled."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    field_state = {
        "rows_per_bed": "UNVALIDATED",
        "in_row_spacing_cm": "UNVALIDATED",
        "seeds_per_gram": "UNVALIDATED",
    }
    assert calc_enabled(1, field_state) is True


def test_calc_disabled_when_required_field_missing() -> None:
    """AC-08: Calc is disabled iff a required book field is MISSING."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    field_state = {
        "rows_per_bed": "VALIDATED",
        "in_row_spacing_cm": "VALIDATED",
        "seeds_per_gram": "MISSING",  # ← makes calc #1 disabled
    }
    assert calc_enabled(1, field_state) is False


def test_calc_disabled_when_field_absent_from_state() -> None:
    """Fields absent from field_state dict are treated as MISSING."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    field_state = {
        "rows_per_bed": "VALIDATED",
        # in_row_spacing_cm not present → treated as MISSING
    }
    assert calc_enabled(2, field_state) is False


def test_calc_14_always_enabled() -> None:
    """Calc #14 has no required book fields → always enabled."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    assert calc_enabled(14, {}) is True
    assert calc_enabled(14, {"anything": "MISSING"}) is True


def test_calc_enabled_succession_missing() -> None:
    """Calc #6 (succession_schedule) disabled when succession_interval_weeks MISSING."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled

    field_state_missing = {"succession_interval_weeks": "MISSING"}
    field_state_unvalidated = {"succession_interval_weeks": "UNVALIDATED"}
    field_state_validated = {"succession_interval_weeks": "VALIDATED"}

    assert calc_enabled(6, field_state_missing) is False
    assert calc_enabled(6, field_state_unvalidated) is True
    assert calc_enabled(6, field_state_validated) is True


def test_calc_enabled_synthetic_field_state_all_calcs() -> None:
    """AC-08: Verify enabled/disabled across a synthetic field_state for all 14 calcs."""
    from organic_market_agent.crop_book.calculator_meta import calc_enabled, CALCULATOR_META

    # All mandatory fields VALIDATED → all calcs enabled
    all_fields = set()
    for meta in CALCULATOR_META.values():
        all_fields.update(meta["required_book_fields"])
    validated_state = {f: "VALIDATED" for f in all_fields}
    for calc_id in range(1, 15):
        assert calc_enabled(calc_id, validated_state) is True, f"Calc #{calc_id} should be enabled"

    # All mandatory fields MISSING → calcs with required fields disabled
    missing_state = {f: "MISSING" for f in all_fields}
    for calc_id in range(1, 15):
        meta = CALCULATOR_META[calc_id]
        if meta["required_book_fields"]:
            assert calc_enabled(calc_id, missing_state) is False, (
                f"Calc #{calc_id} should be disabled when fields missing"
            )
        else:
            assert calc_enabled(calc_id, missing_state) is True, (
                f"Calc #{calc_id} (no required fields) should still be enabled"
            )
