"""Parser for eranorgani.co.il — SRC027 (selector-driven grid)."""

from __future__ import annotations

from typing import Any, Optional

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.selector_catalog import merge_selector_profile, parse_selector_catalog_grid

_DEFAULTS: dict[str, str] = {
    "product_card": "div.product-box",
    "name": "h3, h4, .product-title",
    "price": ".price-box",
}


class EranorganiParser(BaseParser):
    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._sel = merge_selector_profile(_DEFAULTS, selector_overrides)

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        return parse_selector_catalog_grid(content, self._sel, charset_hint)
