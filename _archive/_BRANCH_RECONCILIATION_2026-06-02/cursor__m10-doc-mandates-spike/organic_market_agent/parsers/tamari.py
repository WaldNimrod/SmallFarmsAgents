"""Parser for shop.tamari-farm.co.il — SRC028 (Next.js Rexail payload; HTML grid fallback)."""

from __future__ import annotations

from typing import Any, Optional

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.rexail import RexailParser
from organic_market_agent.parsers.selector_catalog import merge_selector_profile, parse_selector_catalog_grid

_DEFAULTS: dict[str, str] = {
    "product_card": "li.product, div.product",
    "name": "h2.woocommerce-loop-product__title, h2, h3",
    "price": "span.price, .amount, .woocommerce-Price-amount",
}


class TamariParser(BaseParser):
    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._rexail = RexailParser(selector_overrides)
        self._sel = merge_selector_profile(_DEFAULTS, selector_overrides)

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        items = self._rexail.parse(content, charset_hint)
        if items:
            for it in items:
                pl = dict(it.raw_payload_json or {})
                pl["parser"] = "tamari"
                it.raw_payload_json = pl
            return items
        return parse_selector_catalog_grid(content, self._sel, charset_hint)
