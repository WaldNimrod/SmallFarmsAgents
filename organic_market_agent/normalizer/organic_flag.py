"""Stage 2: Detect organic claim from raw product name or payload."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.context import NormContext

_ORGANIC_KEYWORDS = frozenset(
    [
        "אורגני",
        "אורגנית",
        "אורגניים",
        "אורגניות",
        "organic",
        "bio",
        "ביו",
    ]
)


def _payload_text(payload: dict[str, Any] | None) -> str:
    if not payload:
        return ""
    try:
        return json.dumps(payload, ensure_ascii=False).lower()
    except (TypeError, ValueError):
        return ""


def run(ctx: NormContext, session: Session) -> NormContext:
    """Set is_organic_claimed if any organic keyword appears in name or payload."""
    text = (ctx.raw_product_name or "").lower()
    blob = _payload_text(ctx.raw_payload_json)
    combined = f"{text} {blob}"
    for kw in _ORGANIC_KEYWORDS:
        if kw in combined:
            ctx.is_organic_claimed = True
            break
    return ctx
