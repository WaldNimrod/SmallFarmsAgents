"""Stage 3: Parse raw_price_text → Decimal price_amount."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PRICE_RE = re.compile(
    r"(?:₪|NIS)?\s*(\d{1,6}(?:[.,]\d{1,4})?)",
    re.IGNORECASE,
)
# Digits followed by common ILS suffixes (e.g. "18 שח", "12 ש״ח")
_PRICE_RE_SUFFIX = re.compile(
    r"(\d{1,6}(?:[.,]\d{1,4})?)\s*(?:שקלים?|ש[\"׳']?\s*ח|שח\b|₪|nis\b)",
    re.IGNORECASE,
)


def _parse(text: str) -> Optional[Decimal]:
    text = text.strip()

    def _from_group1(match: re.Match[str]) -> Optional[Decimal]:
        raw = match.group(1).replace(",", ".")
        try:
            return Decimal(raw).quantize(Decimal("0.0001"))
        except InvalidOperation:
            return None

    m = _PRICE_RE.search(text)
    if m:
        got = _from_group1(m)
        if got is not None:
            return got
    m2 = _PRICE_RE_SUFFIX.search(text)
    if m2:
        return _from_group1(m2)
    return None


def run(ctx: NormContext, session: Session) -> NormContext:
    """Parse raw_price_text into Decimal price_amount."""
    if not ctx.raw_price_text or not str(ctx.raw_price_text).strip():
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = "empty raw_price_text"
        return ctx

    amount = _parse(str(ctx.raw_price_text))
    if amount is None:
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = f"cannot parse price from {ctx.raw_price_text!r}"
        return ctx

    if amount <= 0:
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = f"non-positive price: {amount}"
        return ctx

    ctx.price_amount = amount
    return ctx
