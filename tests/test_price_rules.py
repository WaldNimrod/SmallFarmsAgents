"""Unit tests for aggregator price dispersion rules."""
from __future__ import annotations

from decimal import Decimal

from organic_market_agent.aggregator.price_rules import (
    multi_source_sigma_blocks_publish,
    price_rules_allow_publish,
    two_source_spread_blocks_publish,
)


def test_two_source_spread_blocks_over_100_percent():
    assert two_source_spread_blocks_publish(Decimal("10"), Decimal("25")) is True
    assert two_source_spread_blocks_publish(Decimal("10"), Decimal("30")) is True


def test_two_source_spread_allows_at_or_below_100_percent():
    assert two_source_spread_blocks_publish(Decimal("10"), Decimal("20")) is False
    assert two_source_spread_blocks_publish(Decimal("10"), Decimal("14")) is False


def test_two_source_non_positive_min_does_not_block():
    assert two_source_spread_blocks_publish(Decimal("0"), Decimal("10")) is False


def test_multi_source_sigma_flags_extreme_outlier():
    # Six tight prices and one high outlier → |60 - mean| > 2σ
    avgs = [Decimal("10")] * 5 + [Decimal("60")]
    assert multi_source_sigma_blocks_publish(avgs) is True


def test_multi_source_sigma_allows_close_cluster():
    assert multi_source_sigma_blocks_publish([Decimal("10"), Decimal("11"), Decimal("12")]) is False


def test_price_rules_allow_publish_two_sources():
    a = {1: Decimal("10"), 2: Decimal("14")}
    ok, code = price_rules_allow_publish(a)
    assert ok is True
    assert code is None


def test_price_rules_block_two_sources_wide_spread():
    a = {1: Decimal("10"), 2: Decimal("30")}
    ok, code = price_rules_allow_publish(a)
    assert ok is False
    assert code == "two_source_price_spread_gt_100pct"


def test_price_rules_block_multi_source_sigma():
    avgs = {i: Decimal("10") for i in range(1, 6)}
    avgs[6] = Decimal("60")
    ok, code = price_rules_allow_publish(avgs)
    assert ok is False
    assert code == "multi_source_outlier_gt_2sigma"
