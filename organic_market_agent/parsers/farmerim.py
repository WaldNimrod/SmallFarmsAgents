"""Parser for Farmerim (OpenCart-based) product catalog pages."""
from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

DEFAULT_SELECTORS = {
    "product_card": "div.product-thumb",
    "name": "h4 a",
    "price": "p.price",
}

_UNIT_RE = re.compile(
    r"[₪\d.,\s]+"
    r"(לק[\"״]ג|לקילו|ליחידה|למארז|ל\s*\d*\s*ק[\"״.]?ג"
    r"|לאריזה|לחבילה|לצרור|לבקבוק|לצנצנת|לשקית|ליח['\'])",
    re.UNICODE,
)


class FarmerimParser(BaseParser):
    """Parses Farmerim / OpenCart HTML product listing pages.

    Targets ``div.product-thumb`` cards. Each card contains a product name
    inside ``h4 > a`` and one or more ``p.price`` elements. The first
    ``p.price`` without a ``span.price-new`` child holds the base price;
    the one *with* ``span.price-new`` is a promotional bundle price.
    """

    def __init__(self, selector_overrides: Optional[dict] = None) -> None:
        self._selectors = {**DEFAULT_SELECTORS, **(selector_overrides or {})}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        encoding = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
        except Exception as exc:
            raise ParserError(f"FarmerimParser: HTML parse error: {exc}") from exc

        cards = soup.select(self._selectors["product_card"])
        if not cards:
            logger.warning("FarmerimParser: no product cards found with selector %r",
                           self._selectors["product_card"])
            return []

        items: list[RawItem] = []
        seen_hrefs: set[str] = set()

        for card in cards:
            name_el = card.select_one(self._selectors["name"])
            if name_el is None:
                continue

            raw_name = name_el.get_text(strip=True)
            if not raw_name:
                continue

            href = name_el.get("href", "")
            if href in seen_hrefs:
                continue
            if href:
                seen_hrefs.add(href)

            base_price_text: Optional[str] = None
            unit_text: Optional[str] = None

            for price_el in card.select(self._selectors["price"]):
                if price_el.select_one("span.price-new"):
                    continue
                base_price_text = price_el.get_text(strip=True)
                break

            if not base_price_text:
                continue

            m = _UNIT_RE.search(base_price_text)
            if m:
                unit_text = m.group(1).strip()

            items.append(
                RawItem(
                    raw_product_name=raw_name[:200],
                    raw_price_text=base_price_text[:80],
                    raw_unit_text=unit_text,
                    raw_quantity_text=None,
                    raw_payload_json={"href": href} if href else {},
                )
            )

        logger.info("FarmerimParser: extracted %d items (%d cards, %d deduped)",
                     len(items), len(cards), len(cards) - len(items))
        return items
