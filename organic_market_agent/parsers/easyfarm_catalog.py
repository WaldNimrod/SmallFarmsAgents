"""Parser for EasyFarm platform catalog pages."""
from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

DEFAULT_SELECTORS = {
    "product_row": "div.product-item, li.product-item, tr.product-row",
    "name": ".product-name, .item-title, h3",
    "price": ".product-price, .item-price, .price",
    "unit": ".product-unit, .item-unit, .unit",
    "quantity": ".product-quantity, .item-quantity, .qty",
}


class EasyFarmCatalogParser(BaseParser):
    """Parses EasyFarm HTML catalog pages."""

    def __init__(self, selector_overrides: Optional[dict] = None) -> None:
        self._selectors = {**DEFAULT_SELECTORS, **(selector_overrides or {})}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        encoding = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
        except Exception as exc:
            raise ParserError(f"EasyFarmCatalogParser: HTML parse error: {exc}") from exc

        rows = soup.select(self._selectors["product_row"])
        if not rows:
            logger.warning("EasyFarmCatalogParser: no product rows found")
            return []

        items: list[RawItem] = []
        for row in rows:
            name_el = row.select_one(self._selectors["name"]) if self._selectors.get("name") else None
            price_el = row.select_one(self._selectors["price"]) if self._selectors.get("price") else None
            unit_sel = self._selectors.get("unit")
            qty_sel = self._selectors.get("quantity")
            unit_el = row.select_one(unit_sel) if unit_sel else None
            qty_el = row.select_one(qty_sel) if qty_sel else None

            raw_product_name = name_el.get_text(strip=True) if name_el else None
            raw_price_text = price_el.get_text(strip=True) if price_el else None

            # Skip rows with no product name or no price — they are extraction failures.
            if not raw_product_name or not raw_price_text:
                continue

            items.append(
                RawItem(
                    raw_product_name=raw_product_name,
                    raw_price_text=raw_price_text,
                    raw_unit_text=unit_el.get_text(strip=True) if unit_el else None,
                    raw_quantity_text=qty_el.get_text(strip=True) if qty_el else None,
                    raw_payload_json={},
                )
            )

        logger.info("EasyFarmCatalogParser: extracted %d items", len(items))
        return items
