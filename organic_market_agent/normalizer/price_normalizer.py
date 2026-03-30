"""Stage 6: Convert price_amount to canonical base unit price (normalized_price_value)."""
from __future__ import annotations

from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import UnitConversion
from organic_market_agent.normalizer.context import NormContext


def run(ctx: NormContext, session: Session) -> NormContext:
    """Set normalized_price_value / normalized_unit_id / normalization_method."""
    if ctx.is_basket_product:
        return ctx

    if ctx.price_amount is None or ctx.display_unit_id is None:
        ctx.normalization_method = "unresolvable"
        return ctx

    conversion = session.execute(
        sa.select(
            UnitConversion.to_unit_id,
            UnitConversion.factor,
            UnitConversion.conversion_type,
        )
        .where(
            UnitConversion.from_unit_id == ctx.display_unit_id,
            UnitConversion.is_active.is_(True),
            sa.or_(
                UnitConversion.product_id == ctx.product_id,
                UnitConversion.product_id.is_(None),
            ),
        )
        .order_by(
            sa.case((UnitConversion.product_id.isnot(None), 0), else_=1),
            UnitConversion.id,
        )
    ).first()

    if conversion:
        to_unit_id, factor, conv_type = conversion
        ctx.normalized_price_value = (ctx.price_amount * Decimal(str(factor))).quantize(
            Decimal("0.0001")
        )
        ctx.normalized_unit_id = to_unit_id
        if conv_type == "exact":
            ctx.normalization_method = "unit_conversion_exact"
        else:
            ctx.normalization_method = "unit_conversion_heuristic"
    else:
        ctx.normalized_price_value = ctx.price_amount
        ctx.normalized_unit_id = ctx.display_unit_id
        ctx.normalization_method = "direct"

    return ctx
