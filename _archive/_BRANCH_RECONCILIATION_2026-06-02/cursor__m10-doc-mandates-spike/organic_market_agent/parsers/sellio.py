"""Sellio storefront HTML (e.g. Teva Shuk) — grid from rendered ``title`` attributes + optional organic filter."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.rexail import RexailParser
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_TITLE_PRICE = re.compile(r"^(.+?)\s+([\d.]+)\s*₪\s*$")


def _is_organic_display_name(name: str) -> bool:
    if any(x in name for x in ("אורגני", "אורגנית", "אורגניים")):
        return True
    return "organic" in name.lower()


class SellioParser(BaseParser):
    """Parses client-rendered Sellio grids; falls back to ``__NEXT_DATA__`` like Rexail."""

    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._sel = selector_overrides or {}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        enc = charset_hint or "utf-8"
        organic_only = bool(self._sel.get("sellio_organic_only", False))

        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
        except Exception as exc:
            raise ParserError(f"SellioParser: HTML parse error: {exc}") from exc

        script = soup.select_one("script#__NEXT_DATA__")
        if script and script.string:
            try:
                root = json.loads(script.string)
            except json.JSONDecodeError:
                root = None
            if root:
                rex = RexailParser(self._sel)
                items = rex.parse(content, charset_hint=charset_hint)
                if items:
                    return _filter_organic(items, organic_only)

        items = _parse_title_grid(soup, organic_only)
        if items:
            return items

        logger.warning("SellioParser: no products from __NEXT_DATA__ or title grid")
        return []


def _filter_organic(items: list[RawItem], organic_only: bool) -> list[RawItem]:
    if not organic_only:
        return items
    return [it for it in items if it.raw_product_name and _is_organic_display_name(it.raw_product_name)]


def _parse_title_grid(soup: BeautifulSoup, organic_only: bool) -> list[RawItem]:
    out: list[RawItem] = []
    seen: set[tuple[str, str]] = set()
    for a in soup.find_all("a", title=True):
        title = (a.get("title") or "").strip()
        if "₪" not in title:
            continue
        m = _TITLE_PRICE.match(title)
        if not m:
            continue
        name = m.group(1).strip()
        price = m.group(2).strip()
        if organic_only and not _is_organic_display_name(name):
            continue
        key = (name[:200], price)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            RawItem(
                raw_product_name=name[:500],
                raw_price_text=price,
                raw_unit_text=None,
                raw_quantity_text=None,
                raw_payload_json={
                    "parser": "sellio",
                    "sellio_organic_only": organic_only,
                },
            )
        )
    return out
