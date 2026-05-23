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
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("avg_yield_per_bed_m")
    assert policy.blend_strategy == "weighted_mean"
    assert policy.multi_year_op_mean is True


def test_documented_price_uses_latest_op() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("documented_price")
    assert policy.blend_strategy == "latest_op"


def test_in_row_spacing_uses_hard_winner() -> None:
    from organic_market_agent.crop_book.field_policy import get_field_policy

    policy = get_field_policy("in_row_spacing_cm")
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
