"""Stage 7: Enforce basket product policy — nullify normalized price fields."""
from __future__ import annotations

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.context import NormContext


def run(ctx: NormContext, session: Session) -> NormContext:
    """Basket products must not have normalized_price_value (V1 policy)."""
    if ctx.is_basket_product:
        ctx.normalized_price_value = None
        ctx.normalized_unit_id = None
        ctx.normalization_method = None
        ctx.resolution_notes.append("basket_product_no_normalization")
    return ctx
