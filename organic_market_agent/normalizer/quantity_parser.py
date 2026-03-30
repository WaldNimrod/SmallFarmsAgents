"""Stage 5: Parse raw_quantity_text and adjust price_amount accordingly."""
from __future__ import annotations

import re
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.context import NormContext

_QTY_RE = re.compile(
    r"(\d{1,4}(?:[.,]\d{1,3})?)\s*(?:יח|units?|x|×|pcs?)?",
    re.IGNORECASE,
)


def _parse_qty(text: str) -> Optional[Decimal]:
    match = _QTY_RE.search(text.strip())
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", "."))
    except Exception:
        return None


def run(ctx: NormContext, session: Session) -> NormContext:
    """If raw_quantity_text indicates N units, divide price_amount by N."""
    if not ctx.raw_quantity_text or ctx.price_amount is None:
        return ctx

    qty = _parse_qty(ctx.raw_quantity_text)
    if qty and qty > Decimal("1"):
        ctx.price_amount = (ctx.price_amount / qty).quantize(Decimal("0.0001"))
        ctx.resolution_notes.append("quantity_divided_by")

    return ctx
