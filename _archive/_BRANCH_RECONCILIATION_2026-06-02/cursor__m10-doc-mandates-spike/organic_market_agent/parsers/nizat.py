"""Parser for Nizat (ASP.NET) product grid — SRC025."""

from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_DEFAULT_SELECTORS: dict[str, str] = {
    "product_card": ".productcubecontainer",
    "name": ".productcubepname",
    "price": ".productcubeprice",
}

_PRICE_RE = re.compile(r"[\d.,]+")


class NizatParser(BaseParser):
    """Extracts product cubes from nizat.com category HTML."""

    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        raw = selector_overrides or {}
        self._sel = {**_DEFAULT_SELECTORS, **{k: str(v) for k, v in raw.items() if k in _DEFAULT_SELECTORS}}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        enc = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
        except Exception as exc:
            raise ParserError(f"NizatParser: HTML parse error: {exc}") from exc

        cards = soup.select(self._sel["product_card"])
        if not cards:
            logger.warning("NizatParser: no cards for selector %r", self._sel["product_card"])
            return []

        out: list[RawItem] = []
        for card in cards:
            ne = card.select_one(self._sel["name"])
            pe = card.select_one(self._sel["price"])
            if not ne or not pe:
                continue
            name = ne.get_text(" ", strip=True)
            price_txt = pe.get_text(" ", strip=True)
            if not name or not price_txt:
                continue
            m = _PRICE_RE.search(price_txt.replace(",", ""))
            raw_price = m.group(0) if m else price_txt
            unit = None
            if "ק" in price_txt and "ג" in price_txt:
                unit = 'לק"ג'
            elif "יח" in price_txt:
                unit = "ליחידה"
            out.append(
                RawItem(
                    raw_product_name=name[:500],
                    raw_price_text=raw_price,
                    raw_unit_text=unit,
                    raw_quantity_text=None,
                    raw_payload_json={"parser": "nizat", "price_line": price_txt[:200]},
                )
            )
        return out
