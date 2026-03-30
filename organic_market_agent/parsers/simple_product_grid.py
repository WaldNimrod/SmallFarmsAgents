"""Parser for simple standalone HTML product tables/grids."""
from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class SimpleProductGridParser(BaseParser):
    """Heuristic parser for simple product listings.

    Strategy:
      1. Look for <table> rows with price-like content (contains digits).
      2. Fall back to <div>/<li> elements that contain both a name and a price pattern.
    """

    _PRICE_RE = re.compile(r"[\d]+[.,]?[\d]*")

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        encoding = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
        except Exception as exc:
            raise ParserError(f"SimpleProductGridParser: HTML parse error: {exc}") from exc

        items = self._try_table(soup) or self._try_list(soup)
        logger.info("SimpleProductGridParser: extracted %d items", len(items))
        return items

    def _try_table(self, soup: BeautifulSoup) -> list[RawItem]:
        items: list[RawItem] = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 2:
                    continue
                price_cells = [c for c in cells if self._PRICE_RE.search(c)]
                if not price_cells:
                    continue
                items.append(
                    RawItem(
                        raw_product_name=cells[0],
                        raw_price_text=price_cells[0],
                        raw_unit_text=cells[2] if len(cells) > 2 else None,
                        raw_quantity_text=None,
                        raw_payload_json={"cells": cells},
                    )
                )
        return items

    def _try_list(self, soup: BeautifulSoup) -> list[RawItem]:
        items: list[RawItem] = []
        for el in soup.find_all(["li", "div", "article"]):
            text = el.get_text(separator=" ", strip=True)
            if self._PRICE_RE.search(text) and len(text) > 5:
                items.append(
                    RawItem(
                        raw_product_name=text[:200],
                        raw_price_text=None,
                        raw_unit_text=None,
                        raw_quantity_text=None,
                        raw_payload_json={"raw_text": text[:500]},
                    )
                )
        return items
