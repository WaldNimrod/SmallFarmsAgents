"""Stage 0: Approved V1 out-of-scope — mark row as ignored (not unresolvable)."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.alias_resolver import _normalize_text
from organic_market_agent.normalizer.context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

if TYPE_CHECKING:
    from organic_market_agent.models.catalog_scope_skip import CatalogScopeSkipRule

logger = get_logger(__name__)

STAGE = "scope_skip"


def _matches(rule: "CatalogScopeSkipRule", raw: str) -> bool:
    raw_stripped = raw.strip()
    if not raw_stripped:
        return False
    n = _normalize_text(raw_stripped)
    p = rule.pattern.strip()
    if rule.match_type == "exact":
        return n == _normalize_text(p)
    if rule.match_type == "prefix":
        return n.startswith(_normalize_text(p))
    if rule.match_type == "contains":
        return _normalize_text(p) in n
    if rule.match_type == "regex":
        try:
            return re.search(p, raw_stripped, flags=re.IGNORECASE) is not None
        except re.error:
            logger.warning("Invalid regex in catalog_scope_skip_rules id=%s pattern=%r", rule.id, p)
            return False
    return False


def run(ctx: NormContext, session: Session) -> NormContext:
    """If raw_product_name matches an active catalog rule, flag scope_skip (engine sets ignored)."""
    rules = ctx.catalog_scope_skip_rules
    if not rules:
        return ctx
    name = ctx.raw_product_name
    if not name or not str(name).strip():
        return ctx
    for rule in rules:
        if not rule.is_active:
            continue
        if _matches(rule, str(name)):
            ctx.stage_failed = STAGE
            ctx.unresolvable_reason = f"approved_scope_skip:{rule.category_code}#{rule.id}"
            ctx.resolution_notes.append(f"scope_skip_rule:{rule.display_order}")
            return ctx
    return ctx
