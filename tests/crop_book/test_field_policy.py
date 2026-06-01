"""Tests for field_policy.py — SFA-S003-P002-WP-A LOD400 §17 Step 10."""

from __future__ import annotations


def test_days_to_maturity_uses_weighted_mean() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("days_to_maturity")
    assert policy.blend_strategy == "weighted_mean"


def test_days_to_maturity_has_dtm_domain_fn() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("days_to_maturity")
    assert policy.outlier.domain_fn is not None
    # domain_fn returns True for leaf crops with value < 20
    from organic_market_agent.crop_book.constants import OUTLIER_CROPS
    leaf = next(iter(OUTLIER_CROPS))
    assert policy.outlier.domain_fn(leaf, 5.0) is True   # leaf + < 20 → outlier
    assert policy.outlier.domain_fn(leaf, 35.0) is False  # leaf but >= 20 → not outlier
    assert policy.outlier.domain_fn("עגבניה", 5.0) is False  # non-leaf → not outlier


def test_avg_yield_uses_weighted_mean_and_multi_year_op() -> None:
    # WI-6 / AC-07: key renamed avg_yield_per_bed_m → yield_per_bed_m
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("yield_per_bed_m")
    assert policy.blend_strategy == "weighted_mean"
    assert policy.multi_year_op_mean is True


def test_documented_price_uses_latest_op() -> None:
    # WI-6 / AC-07: key renamed documented_price → price_documented
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("price_documented")
    assert policy.blend_strategy == "latest_op"


def test_in_row_spacing_uses_hard_winner() -> None:
    # WI-6 / AC-07: key renamed in_row_spacing_cm → spacing_in_row_cm
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("spacing_in_row_cm")
    assert policy.blend_strategy == "hard_winner"


def test_unknown_field_returns_default_policy() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy, _DEFAULT_POLICY

    policy = get_field_policy("totally_unknown_field_xyz")
    assert policy is _DEFAULT_POLICY
    assert policy.blend_strategy == "hard_winner"


def test_default_policy_includes_all_classes() -> None:
    from organic_market_agent.crop_book.field_policy import _DEFAULT_POLICY

    for cls in ("EX", "NI", "PR", "OP", "MK", "WB", "UC"):
        assert cls in _DEFAULT_POLICY.trust_order, f"{cls} missing from default trust_order"


def test_rows_per_bed_no_multi_year() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("rows_per_bed")
    assert policy.multi_year_op_mean is False


# ---------------------------------------------------------------------------
# WP-CB-1: new fields (LOD400 §3.1)
# ---------------------------------------------------------------------------

def test_days_in_nursery_cell_present_in_field_policy() -> None:
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY

    assert "days_in_nursery_cell" in FIELD_POLICY, "days_in_nursery_cell missing from FIELD_POLICY"


def test_days_in_nursery_cell_weighted_mean_z35() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("days_in_nursery_cell")
    assert policy.blend_strategy == "weighted_mean"
    assert policy.trust_order == ("EX", "NI", "PR", "OP")
    assert policy.outlier.z_threshold == 3.5


def test_succession_interval_weeks_present_in_field_policy() -> None:
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY

    assert "succession_interval_weeks" in FIELD_POLICY, "succession_interval_weeks missing from FIELD_POLICY"


def test_succession_interval_weeks_hard_winner() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("succession_interval_weeks")
    assert policy.blend_strategy == "hard_winner"
    assert policy.trust_order == ("EX", "NI", "PR", "OP")


def test_get_field_policy_returns_days_in_nursery_cell() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy, FIELD_POLICY

    policy = get_field_policy("days_in_nursery_cell")
    assert policy is FIELD_POLICY["days_in_nursery_cell"]


def test_get_field_policy_returns_succession_interval_weeks() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy, FIELD_POLICY

    policy = get_field_policy("succession_interval_weeks")
    assert policy is FIELD_POLICY["succession_interval_weeks"]


# ---------------------------------------------------------------------------
# WP-CB-MIG2 WI-6: renamed keys absent + new canonical keys present (AC-07)
# ---------------------------------------------------------------------------

def test_old_keys_removed_from_field_policy() -> None:
    """WI-6 / AC-07: old keys must NOT exist in FIELD_POLICY after rename."""
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY
    assert "avg_yield_per_bed_m" not in FIELD_POLICY, \
        "avg_yield_per_bed_m should be removed (renamed to yield_per_bed_m)"
    assert "documented_price" not in FIELD_POLICY, \
        "documented_price should be removed (renamed to price_documented)"
    assert "in_row_spacing_cm" not in FIELD_POLICY, \
        "in_row_spacing_cm should be removed (renamed to spacing_in_row_cm)"
    assert "planting_season" not in FIELD_POLICY, \
        "planting_season must be REMOVED from FIELD_POLICY (T2 attribute, not T1)"


def test_new_canonical_keys_in_field_policy() -> None:
    """WI-6 / AC-07: canonical keys must be in FIELD_POLICY."""
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY
    assert "yield_per_bed_m" in FIELD_POLICY
    assert "price_documented" in FIELD_POLICY
    assert "spacing_in_row_cm" in FIELD_POLICY


# ---------------------------------------------------------------------------
# WP-CB-MIG2 WI-5: new T1 fact policies (AC-06)
# ---------------------------------------------------------------------------

def test_drip_lines_per_bed_in_field_policy() -> None:
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY
    assert "drip_lines_per_bed" in FIELD_POLICY


def test_labor_rate_harvest_weighted_mean() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy
    policy = get_field_policy("labor_rate_harvest")
    assert policy.blend_strategy == "weighted_mean"


def test_labor_rate_wash_weighted_mean() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy
    policy = get_field_policy("labor_rate_wash")
    assert policy.blend_strategy == "weighted_mean"


def test_plantings_per_season_hard_winner() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy
    policy = get_field_policy("plantings_per_season")
    assert policy.blend_strategy == "hard_winner"


def test_harvest_weeks_span_in_field_policy() -> None:
    from organic_market_agent.crop_book.field_policy import FIELD_POLICY
    assert "harvest_weeks_span" in FIELD_POLICY
