"""Parser for rendered mypips.app product catalog HTML."""

from __future__ import annotations

import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PRICE_RE = re.compile(r"[\d.,]+")
_SHEKEL = ("₪", "ש״ח", "ש\"ח", "NIS")
_HEADING_TAGS = ("h2", "h3", "h4", "h5", "h6")


class MypipsParser(BaseParser):
    """Extract product rows from post-Playwright mypips DOM.

    Primary path: each ``div.pips-card-content`` card — title from first heading
    without a currency marker, price from first element containing ₪/NIS.
    Fallback: legacy spike path (iterate ``h6`` titles) when no cards match.
    """

    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._overrides = selector_overrides or {}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        enc = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
        except Exception as exc:
            raise ParserError(f"MypipsParser: HTML parse error: {exc}") from exc

        seen: set[tuple[str, str]] = set()
        out: list[RawItem] = []

        card_sel = self._overrides.get("card_selector") or "div.pips-card-content"
        for card in soup.select(card_sel):
            item = self._extract_from_card(card)
            if item is None:
                continue
            name, raw_price = item
            key = (name[:500], raw_price)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                RawItem(
                    raw_product_name=name[:500],
                    raw_price_text=raw_price,
                    raw_unit_text=None,
                    raw_quantity_text=None,
                    raw_payload_json={"parser": "mypips", "path": "card"},
                )
            )

        if not out:
            out = self._parse_legacy_h6(soup, seen)

        if not out and not self._overrides.get("skip_loose_price_scan"):
            out = self._parse_price_anchor_blocks(soup, seen)

        if not out:
            logger.warning("MypipsParser: no product rows extracted")
        return out

    def _parse_price_anchor_blocks(self, soup: Any, seen: set[tuple[str, str]]) -> list[RawItem]:
        """Last resort for storefronts without ``pips-card-content`` (variant MUI layouts).

        Walk text nodes containing a currency marker; climb to a small block ancestor and
        pair with the first heading in that subtree that does not itself look like a price.
        Skips ``header`` / ``nav`` / ``footer`` regions to reduce menu noise.
        """
        out: list[RawItem] = []
        for text_node in soup.find_all(string=True):
            if not text_node or not str(text_node).strip():
                continue
            chunk = str(text_node).strip()
            if not any(s in chunk for s in _SHEKEL):
                continue
            m = _PRICE_RE.search(chunk.replace(",", ""))
            if not m:
                continue
            raw_price = m.group(0)
            parent = getattr(text_node, "parent", None)
            if parent is None:
                continue
            # Ignore huge blobs (script/style or whole-page dumps)
            if len(parent.get_text(" ", strip=True)) > 350:
                continue

            block: Any = parent
            for _ in range(12):
                if block is None:
                    break
                if block.name in ("header", "nav", "footer", "script", "style"):
                    block = None
                    break
                name: str | None = None
                for ht in _HEADING_TAGS:
                    for h in block.find_all(ht):
                        t = h.get_text(" ", strip=True)
                        if not t or len(t) < 2:
                            continue
                        if any(s in t for s in _SHEKEL):
                            continue
                        name = t[:500]
                        break
                    if name:
                        break
                if name:
                    key = (name, raw_price)
                    if key in seen:
                        break
                    seen.add(key)
                    out.append(
                        RawItem(
                            raw_product_name=name,
                            raw_price_text=raw_price,
                            raw_unit_text=None,
                            raw_quantity_text=None,
                            raw_payload_json={"parser": "mypips", "path": "price_anchor"},
                        )
                    )
                    break
                block = block.parent
        return out

    def _extract_from_card(self, card: Any) -> Optional[tuple[str, str]]:
        price_text = self._find_price_in_card(card, None)
        if not price_text:
            return None
        m = _PRICE_RE.search(price_text.replace(",", ""))
        raw_price = m.group(0) if m else price_text.strip()
        if not raw_price:
            return None

        price_el = self._first_price_element(card)
        for tag in card.find_all(_HEADING_TAGS):
            if price_el is not None and tag is price_el:
                continue
            t = tag.get_text(" ", strip=True)
            if not t or len(t) < 2:
                continue
            if any(s in t for s in _SHEKEL):
                continue
            return (t[:500], raw_price)

        # No heading title: use strong / first line without currency
        for tag in card.find_all(["strong", "b"]):
            t = tag.get_text(" ", strip=True)
            if not t or len(t) < 2 or any(s in t for s in _SHEKEL):
                continue
            return (t[:500], raw_price)

        return None

    def _first_price_element(self, card: Any) -> Any:
        for tag in card.find_all(["h5", "h4", "h3", "h2", "h6", "span", "p", "div"]):
            text = tag.get_text(" ", strip=True)
            if any(s in text for s in _SHEKEL):
                return tag
        return None

    def _parse_legacy_h6(self, soup: Any, seen: set[tuple[str, str]]) -> list[RawItem]:
        title_sel = self._overrides.get("title_selector") or "main h6, h6"
        candidates = soup.select(title_sel)
        if not candidates:
            candidates = soup.find_all("h6")

        out: list[RawItem] = []
        for h6 in candidates:
            name = h6.get_text(" ", strip=True)
            if not name or len(name) < 2:
                continue

            card = self._find_product_card(h6)
            price_text = self._find_price_in_card(card, h6)
            if not price_text:
                continue

            m = _PRICE_RE.search(price_text.replace(",", ""))
            raw_price = m.group(0) if m else price_text.strip()
            key = (name[:500], raw_price)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                RawItem(
                    raw_product_name=name[:500],
                    raw_price_text=raw_price,
                    raw_unit_text=None,
                    raw_quantity_text=None,
                    raw_payload_json={"parser": "mypips", "path": "legacy_h6"},
                )
            )
        return out

    def _find_product_card(self, title_el: Any) -> Any:
        """Ascend to mypips product card root (``div.pips-card-content``)."""
        el: Any = title_el
        for _ in range(12):
            if el is None:
                break
            cls = el.get("class") or []
            if isinstance(cls, list) and "pips-card-content" in cls:
                return el
            el = el.parent
        return title_el.find_parent(["article", "div", "li"]) or title_el.parent

    def _find_price_in_card(self, card: Any, title_el: Any) -> Optional[str]:
        if card is None:
            return None
        for tag in card.find_all(["h5", "h4", "span", "p", "div", "h3", "h2", "h6"]):
            if title_el is not None and tag is title_el:
                continue
            text = tag.get_text(" ", strip=True)
            if any(s in text for s in _SHEKEL):
                return text
        return None
