"""Tests for assumptions.py — WP-CB-1 AC-03 / LOD400 §4."""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# ASSUMPTIONS registry
# ---------------------------------------------------------------------------

def test_all_8_keys_present() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    expected_keys = {
        "germination_rate",
        "bed_width",
        "oversow",
        "std_bed_length_m",
        "compost_N_pct",
        "application_efficiency",
        "rotation_gap_seasons",
    }
    # 7 scalar assumptions — tray_cells + hardiness_offset are module-level dicts
    # The dispatch calls them "8 keys"; tray_cells is TRAY_CELLS, hardiness_offset
    # is HARDINESS_OFFSET — both confirmed present in separate tests below.
    assert expected_keys <= set(ASSUMPTIONS.keys()), (
        f"Missing keys: {expected_keys - set(ASSUMPTIONS.keys())}"
    )


def test_germination_rate_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["germination_rate"]
    assert a.default == 0.90
    assert a.unit == "fraction"


def test_bed_width_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["bed_width"]
    assert a.default == 0.80
    assert a.unit == "m"


def test_oversow_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["oversow"]
    assert a.default == 1.10


def test_std_bed_length_m_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["std_bed_length_m"]
    assert a.default == 30.0
    assert a.unit == "m"


def test_compost_n_pct_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["compost_N_pct"]
    assert abs(a.default - 0.015) < 1e-9


def test_application_efficiency_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["application_efficiency"]
    assert a.default == 0.50


def test_rotation_gap_seasons_default() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["rotation_gap_seasons"]
    assert a.default == 3
    assert a.unit == "seasons"


# ---------------------------------------------------------------------------
# post_url requirements (AC-03)
# ---------------------------------------------------------------------------

def test_germination_rate_has_non_null_post_url() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["germination_rate"]
    assert a.post_url is not None, "germination_rate must have a non-null post_url"
    assert "nimrod.bio" in a.post_url


def test_bed_width_has_non_null_post_url() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    a = ASSUMPTIONS["bed_width"]
    assert a.post_url is not None, "bed_width must have a non-null post_url"
    assert "nimrod.bio" in a.post_url


def test_others_have_null_post_url() -> None:
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS

    # These are the 5 scalar assumptions that should NOT have post_url yet
    no_url_keys = {"oversow", "std_bed_length_m", "compost_N_pct", "application_efficiency", "rotation_gap_seasons"}
    for k in no_url_keys:
        assert ASSUMPTIONS[k].post_url is None, f"{k} should have post_url=None (not yet published)"


# ---------------------------------------------------------------------------
# get_assumption helper
# ---------------------------------------------------------------------------

def test_get_assumption_returns_default() -> None:
    from organic_market_agent.crop_book.assumptions import get_assumption

    val = get_assumption("germination_rate")
    assert val == 0.90


def test_get_assumption_honors_override() -> None:
    from organic_market_agent.crop_book.assumptions import get_assumption

    val = get_assumption("germination_rate", override=0.75)
    assert val == 0.75


def test_get_assumption_none_override_uses_default() -> None:
    from organic_market_agent.crop_book.assumptions import get_assumption

    val = get_assumption("bed_width", override=None)
    assert val == 0.80


def test_get_assumption_zero_override_is_honored() -> None:
    """0.0 is a valid override (not None) — should be returned, not treated as falsy."""
    from organic_market_agent.crop_book.assumptions import get_assumption

    val = get_assumption("germination_rate", override=0.0)
    assert val == 0.0


# ---------------------------------------------------------------------------
# TRAY_CELLS lookup table
# ---------------------------------------------------------------------------

def test_tray_cells_table_exists() -> None:
    from organic_market_agent.crop_book.assumptions import TRAY_CELLS

    assert isinstance(TRAY_CELLS, dict)
    assert len(TRAY_CELLS) >= 4


def test_tray_cells_known_types() -> None:
    from organic_market_agent.crop_book.assumptions import TRAY_CELLS

    assert TRAY_CELLS["128"] == 128
    assert TRAY_CELLS["200"] == 200
    assert TRAY_CELLS["72"] == 72


def test_get_tray_cells_default() -> None:
    from organic_market_agent.crop_book.assumptions import get_tray_cells

    assert get_tray_cells(None) == 128
    assert get_tray_cells("unknown_type") == 128


def test_get_tray_cells_known() -> None:
    from organic_market_agent.crop_book.assumptions import get_tray_cells

    assert get_tray_cells("200") == 200


def test_get_tray_cells_override() -> None:
    from organic_market_agent.crop_book.assumptions import get_tray_cells

    assert get_tray_cells("128", override=50) == 50


# ---------------------------------------------------------------------------
# HARDINESS_OFFSET lookup table
# ---------------------------------------------------------------------------

def test_hardiness_offset_table_exists() -> None:
    from organic_market_agent.crop_book.assumptions import HARDINESS_OFFSET

    assert isinstance(HARDINESS_OFFSET, dict)
    assert None in HARDINESS_OFFSET


def test_hardiness_offset_classes() -> None:
    from organic_market_agent.crop_book.assumptions import HARDINESS_OFFSET

    assert HARDINESS_OFFSET["very_hardy"] == 28
    assert HARDINESS_OFFSET["hardy"] == 28
    assert HARDINESS_OFFSET["semi_hardy"] == 14
    assert HARDINESS_OFFSET["tender"] == 0
    assert HARDINESS_OFFSET["very_tender"] == -14
    assert HARDINESS_OFFSET["warm"] == -14
    assert HARDINESS_OFFSET[None] == 0


def test_get_hardiness_offset_known() -> None:
    from organic_market_agent.crop_book.assumptions import get_hardiness_offset

    assert get_hardiness_offset("very_hardy") == 28
    assert get_hardiness_offset("tender") == 0


def test_get_hardiness_offset_unknown_class() -> None:
    from organic_market_agent.crop_book.assumptions import get_hardiness_offset

    # Unknown class falls back to 0 (conservative)
    assert get_hardiness_offset("unknown_class") == 0


def test_get_hardiness_offset_override() -> None:
    from organic_market_agent.crop_book.assumptions import get_hardiness_offset

    assert get_hardiness_offset("very_hardy", override=7) == 7
