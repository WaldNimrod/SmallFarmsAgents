"""Stage 1: Resolve raw_product_name → product_id via product_aliases table."""
from __future__ import annotations

import re

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import Product, ProductAlias
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    """Lowercase + collapse whitespace. Matches alias_text_normalized in DB."""
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def run(ctx: NormContext, session: Session) -> NormContext:
    """Resolve raw_product_name to a product_id.

    Lookup order:
      1. Exact match on alias_text_normalized, filtered by source_id
      2. Exact match on alias_text_normalized, source_id IS NULL (global alias)
      3. Contains: alias_text_normalized substring of input (longest alias first)
    """
    if not ctx.raw_product_name or not ctx.raw_product_name.strip():
        ctx.stage_failed = "alias"
        ctx.unresolvable_reason = "empty raw_product_name"
        return ctx

    normalized = _normalize_text(ctx.raw_product_name)

    row = session.execute(
        sa.select(ProductAlias.product_id).where(
            ProductAlias.alias_text_normalized == normalized,
            ProductAlias.source_id == ctx.source_id,
            ProductAlias.is_active.is_(True),
        )
    ).scalar_one_or_none()

    if row is None:
        row = session.execute(
            sa.select(ProductAlias.product_id).where(
                ProductAlias.alias_text_normalized == normalized,
                ProductAlias.source_id.is_(None),
                ProductAlias.is_active.is_(True),
            )
        ).scalar_one_or_none()

    if row is None:
        candidates = session.execute(
            sa.select(ProductAlias.product_id, ProductAlias.alias_text_normalized)
            .where(
                ProductAlias.is_active.is_(True),
                sa.func.length(ProductAlias.alias_text_normalized) >= 3,
            )
            .order_by(sa.func.length(ProductAlias.alias_text_normalized).desc())
        ).all()
        for product_id, alias_norm in candidates:
            if alias_norm and alias_norm in normalized:
                row = product_id
                ctx.resolution_notes.append(f"alias_contains_match:{alias_norm!r}")
                break

    if row is None:
        ctx.stage_failed = "alias"
        ctx.unresolvable_reason = f"no alias match for {normalized!r}"
        logger.debug("Alias miss: %r (source_id=%d)", normalized, ctx.source_id)
        return ctx

    product = session.get(Product, row)
    ctx.product_id = row
    ctx.is_basket_product = bool(product.is_basket_product) if product else False
    return ctx
