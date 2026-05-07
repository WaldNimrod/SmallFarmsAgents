"""
Resolve CSA basket item → PRD025 (small), PRD026 (medium), or PRD027 (large).

Tier assignment policy (ARCH-20260406-CQ-MASTER §3.7.2, BINDING):
  Small  (PRD025): 5–8  items OR ₪80–130
  Medium (PRD026): 9–13 items OR ₪130–180   [default fallback]
  Large  (PRD027): 14+  items OR ₪170–250

Resolution order:
  1. Item count from csa_context_json (explicit item list or item_count field)
  2. Price-based range if no item count available
  3. Default PRD026 (medium) if neither available

Special cases:
  - item_count < 5: not a valid basket → return None (caller scope-skips)
  - Both count and price available: count takes priority
"""
from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import Product
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Tier ranges (BINDING — ARCH-20260406-CQ-MASTER §3.7.2)
_ITEM_COUNT_TIERS = [
    (5, 8, "PRD025"),  # small
    (9, 13, "PRD026"),  # medium
    (14, 9999, "PRD027"),  # large
]

_PRICE_TIERS = [
    (Decimal("80"), Decimal("130"), "PRD025"),
    (Decimal("130"), Decimal("180"), "PRD026"),
    (Decimal("170"), Decimal("250"), "PRD027"),
]

_DEFAULT_TIER_CODE = "PRD026"
_NOTE_DEFAULT = "basket_tier_default_medium"
_NOTE_BY_COUNT = "basket_tier_by_item_count"
_NOTE_BY_PRICE = "basket_tier_by_price"
_NOTE_TOO_SMALL = "basket_too_small"
_NOTE_OVERSIZED = "basket_tier_oversized_default_large"


def _extract_item_count(csa_context_json: Optional[str]) -> Optional[int]:
    """
    Parse item count from csa_context JSON field.

    Supported formats:
      {"item_count": 10, ...}
      {"contents": ["item1", "item2", ...], ...}
      {"contents": "5 מוצרים", ...}  -- extract first integer

    Returns None if unparseable.
    """
    if not csa_context_json:
        return None
    try:
        data = json.loads(csa_context_json)
    except (json.JSONDecodeError, TypeError):
        # Try treating as plain-text line count (legacy format)
        lines = [l.strip() for l in str(csa_context_json).splitlines() if l.strip()]
        return len(lines) if len(lines) >= 2 else None

    if "item_count" in data and isinstance(data["item_count"], int):
        return data["item_count"]

    contents = data.get("contents")
    if isinstance(contents, list):
        return len(contents)
    if isinstance(contents, str):
        match = re.search(r"\d+", contents)
        if match:
            return int(match.group())

    return None


def _tier_by_count(count: int) -> Optional[str]:
    """Map item count to product code. Returns None if count < 5 (scope-skip signal)."""
    if count < 5:
        return None  # caller should add _NOTE_TOO_SMALL
    for low, high, code in _ITEM_COUNT_TIERS:
        if low <= count <= high:
            return code
    # count >= 14 already caught by last range; this handles edge case
    return "PRD027"


def _tier_by_price(price: Optional[Decimal]) -> Optional[str]:
    """Map price to product code using price range guidance."""
    if price is None or price <= 0:
        return None
    for low, high, code in _PRICE_TIERS:
        if low <= price <= high:
            return code
    if price < Decimal("80"):
        return None  # too cheap — likely not a full basket
    if price > Decimal("250"):
        return "PRD027"  # large basket, above defined range
    return None


def resolve_basket_tier(
    csa_context_json: Optional[str],
    price_amount: Optional[Decimal],
    session: Session,
) -> tuple[Optional[str], str]:
    """
    Determine basket tier product code.

    Returns:
        (product_code, resolution_note)
        product_code: PRD025/PRD026/PRD027 or None if basket is too small / invalid
        resolution_note: string to append to ctx.resolution_notes

    ``session`` is reserved for future DB-backed resolution; currently unused.
    """
    _ = session
    count = _extract_item_count(csa_context_json)

    if count is not None:
        if count < 5:
            return (None, _NOTE_TOO_SMALL)
        if count > 9999:
            return ("PRD027", _NOTE_OVERSIZED)
        code = _tier_by_count(count)
        return (code, _NOTE_BY_COUNT)

    # No item count — fall back to price
    price_code = _tier_by_price(price_amount)
    if price_code is not None:
        if (
            price_amount is not None
            and price_amount > Decimal("250")
            and price_code == "PRD027"
        ):
            return (price_code, _NOTE_OVERSIZED)
        return (price_code, _NOTE_BY_PRICE)

    # Default fallback
    return (_DEFAULT_TIER_CODE, _NOTE_DEFAULT)


def run(ctx: NormContext, session: Session) -> NormContext:
    """
    Stage entry point: assign basket tier (product_id) based on csa_context and price.
    Called from basket_handler.run() when is_basket_product = True.
    """
    csa_context_raw = None
    if ctx.raw_payload_json:
        try:
            payload = (
                json.loads(ctx.raw_payload_json)
                if isinstance(ctx.raw_payload_json, str)
                else ctx.raw_payload_json
            )
            csa_context_raw = payload.get("csa_context") if isinstance(payload, dict) else None
        except (json.JSONDecodeError, TypeError):
            pass

    # Normalizer may attach dict; resolver expects JSON string or legacy multiline text
    if csa_context_raw is not None and not isinstance(csa_context_raw, str):
        try:
            csa_context_json = json.dumps(csa_context_raw)
        except (TypeError, ValueError):
            csa_context_json = None
    else:
        csa_context_json = csa_context_raw

    product_code, note = resolve_basket_tier(
        csa_context_json=csa_context_json,
        price_amount=ctx.price_amount,
        session=session,
    )

    ctx.resolution_notes.append(note)

    if product_code is None:
        logger.debug(
            "basket_tier_resolver: no tier assigned (%s), keeping alias product_id=%s",
            note,
            ctx.product_id,
        )
        return ctx

    product_id = session.execute(
        sa.select(Product.id).where(Product.code == product_code, Product.is_active.is_(True))
    ).scalar_one_or_none()

    if product_id is None:
        logger.warning("basket_tier_resolver: product_code %s not found in DB", product_code)
        return ctx

    if ctx.product_id != product_id:
        logger.info(
            "basket_tier_resolver: reassigning product %s → %s (%s)",
            ctx.product_id,
            product_id,
            product_code,
        )
        ctx.product_id = product_id

    return ctx
