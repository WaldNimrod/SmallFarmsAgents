"""Stage 4: Resolve raw_unit_text → display_unit_id (MeasurementUnit.id)."""
from __future__ import annotations

import re
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import MeasurementUnit, NormalizerRule, Product
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_BUILTIN_UNIT_MAP = {
    'ק"ג': "kg",
    "קג": "kg",
    "kg": "kg",
    "קילו": "kg",
    "kilo": "kg",
    "גרם": "g",
    "gr": "g",
    "g": "g",
    "יחידה": "unit",
    "unit": "unit",
    "יח'": "unit",
    "יח": "unit",
    "צרור": "bunch",
    "bunch": "bunch",
    "סל קטן": "basket_small",
    "סל בינוני": "basket_medium",
    "סל גדול": "basket_large",
    "סל משפחתי": "basket_family",
    "מארז 250": "pack_250g",
    "מארז 500": "pack_500g",
    "מארז קג": "pack_1kg",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _rule_matches(normalized_input: str, pattern: str, match_type: str) -> bool:
    pat_norm = _normalize(pattern)
    if match_type == "exact":
        return normalized_input == pat_norm
    if match_type == "contains":
        return pat_norm in normalized_input if pat_norm else False
    if match_type == "prefix":
        return normalized_input.startswith(pat_norm) if pat_norm else False
    if match_type == "regex":
        try:
            return re.search(pattern, normalized_input, re.IGNORECASE) is not None
        except re.error:
            logger.warning("Invalid regex in normalizer_rules: %r", pattern)
            return False
    return False


def run(ctx: NormContext, session: Session) -> NormContext:
    """Resolve raw_unit_text → MeasurementUnit id (DB rules, then built-in, then product default)."""
    if not ctx.product_id:
        return ctx

    normalized_text = _normalize(ctx.raw_unit_text or "")
    unit_code: Optional[str] = None

    if ctx.normalizer_profile_id:
        rules = session.execute(
            sa.select(
                NormalizerRule.match_pattern,
                NormalizerRule.match_type,
                NormalizerRule.replacement_value,
            )
            .where(
                NormalizerRule.normalizer_profile_id == ctx.normalizer_profile_id,
                NormalizerRule.rule_kind == "unit_map",
                NormalizerRule.is_active.is_(True),
            )
            .order_by(NormalizerRule.priority.asc(), NormalizerRule.id.asc())
        ).all()

        for match_pattern, match_type, replacement_value in rules:
            if not match_pattern:
                continue
            if _rule_matches(normalized_text, match_pattern, match_type):
                unit_code = (replacement_value or match_pattern).strip()
                if unit_code:
                    break

    if unit_code is None and normalized_text:
        unit_code = _BUILTIN_UNIT_MAP.get(normalized_text)

    if unit_code:
        mu_id = session.execute(
            sa.select(MeasurementUnit.id).where(MeasurementUnit.code == unit_code)
        ).scalar_one_or_none()
        if mu_id:
            ctx.display_unit_id = mu_id
            return ctx

    product = session.get(Product, ctx.product_id)
    if product and product.default_measurement_unit_id:
        ctx.display_unit_id = product.default_measurement_unit_id
        ctx.resolution_notes.append("unit_fallback_to_product_default")

    return ctx
