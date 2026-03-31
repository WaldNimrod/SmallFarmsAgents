"""Price dispersion rules for daily aggregate publish eligibility (per Nimrod / Team 100).

- Exactly two distinct sources: if relative spread between their *per-source average* prices
  exceeds 100% ((max-min)/min > 1), the aggregate must not publish.
- Three or more sources: if any per-source average lies more than 2 sample standard
  deviations from the mean of those averages, the aggregate must not publish.

Publisher already filters ``DailyAggregate.meets_publish_threshold``; these rules tighten that flag.
"""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Sequence

# Relative spread (max-min)/min; above 1.0 means more than 100% gap vs the cheaper source.
TWO_SOURCE_MAX_RELATIVE_SPREAD = Decimal("1.0")

# Outlier if |avg_i - mean| > k * sample_stddev across per-source averages.
MULTI_SOURCE_SIGMA_MULTIPLIER = Decimal("2")


def two_source_spread_blocks_publish(min_price: Decimal, max_price: Decimal) -> bool:
    """True if the two representative prices should block public display (>100% spread)."""
    if min_price <= 0:
        return False
    return (max_price - min_price) / min_price > TWO_SOURCE_MAX_RELATIVE_SPREAD


def multi_source_sigma_blocks_publish(per_source_averages: Sequence[Decimal]) -> bool:
    """True if any per-source average is more than 2σ from the mean (n >= 3)."""
    vals = [Decimal(v) for v in per_source_averages]
    n = len(vals)
    if n < 3:
        return False
    mean = sum(vals) / n
    if n < 2:
        return False
    variance = sum((x - mean) ** 2 for x in vals) / Decimal(n - 1)
    if variance <= 0:
        return False
    std = Decimal(str(math.sqrt(float(variance))))
    if std == 0:
        return False
    k = MULTI_SOURCE_SIGMA_MULTIPLIER
    return any(abs(x - mean) > k * std for x in vals)


def price_rules_allow_publish(per_source_averages: dict[int, Decimal]) -> tuple[bool, str | None]:
    """Return (allowed_for_price_rules, suppression_code_or_none).

    ``per_source_averages`` maps ``source_id -> average price`` for one aggregate bucket.
    """
    if len(per_source_averages) < 2:
        return True, None

    avgs = list(per_source_averages.values())
    mn, mx = min(avgs), max(avgs)

    if len(per_source_averages) == 2:
        if two_source_spread_blocks_publish(mn, mx):
            return False, "two_source_price_spread_gt_100pct"
        return True, None

    if multi_source_sigma_blocks_publish(avgs):
        return False, "multi_source_outlier_gt_2sigma"

    return True, None
