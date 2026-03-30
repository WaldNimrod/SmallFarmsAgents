"""Final confidence score calculation after all 7 stages."""
from __future__ import annotations

from decimal import Decimal

from organic_market_agent.normalizer.context import NormContext

_PENALTIES = {
    "unit_fallback_to_product_default": Decimal("0.10"),
    "alias_contains_match": Decimal("0.10"),
    "quantity_divided_by": Decimal("0.05"),
}


def calculate(ctx: NormContext) -> Decimal:
    """Return confidence in [0.10, 1.00]."""
    score = Decimal("1.0")

    for note in ctx.resolution_notes:
        for key, penalty in _PENALTIES.items():
            if note.startswith(key):
                score -= penalty
                break

    if ctx.normalization_method == "unit_conversion_heuristic":
        score -= Decimal("0.10")
    if ctx.normalization_method == "unresolvable":
        score -= Decimal("0.20")

    return max(score, Decimal("0.10")).quantize(Decimal("0.01"))
