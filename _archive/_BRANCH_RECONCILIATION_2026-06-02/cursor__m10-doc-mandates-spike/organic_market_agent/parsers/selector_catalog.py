"""Generic BeautifulSoup grid parser driven by selector_profile JSON (M10.3)."""

from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PRICE_RE = re.compile(r"[\d.,]+")


def merge_selector_profile(
    defaults: dict[str, str], overrides: Optional[dict[str, Any]]
) -> dict[str, str]:
    base = dict(defaults)
    if overrides:
        for k in ("product_card", "name", "price"):
            if k in overrides and overrides[k]:
                base[k] = str(overrides[k])
    return base


def parse_selector_catalog_grid(
    content: bytes, selectors: dict[str, str], charset_hint: Optional[str]
) -> list[RawItem]:
    enc = charset_hint or "utf-8"
    try:
        soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
    except Exception as exc:
        raise ParserError(f"SelectorCatalogParser: HTML parse error: {exc}") from exc

    cards = soup.select(selectors["product_card"])
    if not cards:
        logger.warning(
            "parse_selector_catalog_grid: no cards for selector %r", selectors["product_card"]
        )
        return []

    out: list[RawItem] = []
    for card in cards:
        ne = card.select_one(selectors["name"])
        pe = card.select_one(selectors["price"])
        if not ne or not pe:
            continue
        name = ne.get_text(" ", strip=True)
        price_txt = pe.get_text(" ", strip=True)
        if not name or not price_txt:
            continue
        m = _PRICE_RE.search(price_txt.replace(",", ""))
        raw_price = m.group(0) if m else price_txt
        out.append(
            RawItem(
                raw_product_name=name[:500],
                raw_price_text=raw_price,
                raw_unit_text=None,
                raw_quantity_text=None,
                raw_payload_json={"parser": "selector_catalog"},
            )
        )
    return out


