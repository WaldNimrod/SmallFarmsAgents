"""Parser for Rexail / Next.js stores — __NEXT_DATA__ JSON (SRC026, similar sites)."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PRICE_RE = re.compile(r"[\d.,]+")


def _extract_store_products_by_category(root: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Rexail / Next.js: flat list from Redux storeProduct.storeProductsByCategoryId."""
    try:
        page_props = root["props"]["pageProps"]
        irs = page_props["initialReduxState"]
        by_cat = irs["storeProduct"]["storeProductsByCategoryId"]
    except (KeyError, TypeError):
        return None
    if not isinstance(by_cat, dict):
        return None
    out: list[dict[str, Any]] = []
    for _cat_id, rows in by_cat.items():
        if not isinstance(rows, list):
            continue
        for p in rows:
            if isinstance(p, dict) and "price" in p:
                out.append(p)
    return out or None


def _product_row_display_name(p: dict[str, Any]) -> Optional[str]:
    """Name from Rexail store product row (Hebrew + English lines)."""
    secondary = _pick_str(p, "secondaryName")
    if secondary:
        return " ".join(secondary.split())
    full = _pick_str(p, "fullName")
    if full:
        # Often 'Hebrew\\nEnglish, organic' — take first line for cleaner matching
        first_line = full.split("\n", 1)[0].strip()
        if first_line:
            return " ".join(first_line.split())
    prod = p.get("product")
    if isinstance(prod, dict):
        ml = prod.get("multiLang")
        if isinstance(ml, dict):
            he = ml.get("he")
            if isinstance(he, dict):
                hn = he.get("name")
                if isinstance(hn, str) and hn.strip():
                    return " ".join(hn.split())
        pn = prod.get("name")
        if isinstance(pn, str) and pn.strip():
            return " ".join(pn.split())
    return None


def _product_row_unit(p: dict[str, Any]) -> Optional[str]:
    prod = p.get("product")
    if not isinstance(prod, dict):
        return None
    u = prod.get("primaryQuantityUnit")
    if isinstance(u, dict):
        un = u.get("name")
        if isinstance(un, str) and un.strip():
            return un.strip()
    return None


def _deep_find_products(obj: Any) -> list[dict[str, Any]] | None:
    """Return first list of dicts that look like product rows."""
    if isinstance(obj, dict):
        for key in ("products", "items", "catalog", "lines"):
            v = obj.get(key)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                if any(x for x in ("name", "title", "productName") if x in v[0]):
                    return v
        for v in obj.values():
            found = _deep_find_products(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for x in obj:
            found = _deep_find_products(x)
            if found is not None:
                return found
    return None


def _pick_str(d: dict[str, Any], *keys: str) -> Optional[str]:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _pick_price(d: dict[str, Any]) -> Optional[str]:
    for k in ("price", "salePrice", "regularPrice", "finalPrice", "amount"):
        v = d.get(k)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            nested = v.get("amount") or v.get("value")
            if nested is not None:
                return str(nested)
    return None


class RexailParser(BaseParser):
    """Parses embedded Next.js payload for product-like dicts."""

    def __init__(self, selector_overrides: Optional[dict[str, Any]] = None) -> None:
        self._overrides = selector_overrides or {}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        enc = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=enc)
        except Exception as exc:
            raise ParserError(f"RexailParser: HTML parse error: {exc}") from exc

        script = soup.select_one('script#__NEXT_DATA__')
        if not script or not script.string:
            logger.warning("RexailParser: missing __NEXT_DATA__ script")
            return []

        try:
            root = json.loads(script.string)
        except json.JSONDecodeError as exc:
            raise ParserError(f"RexailParser: invalid __NEXT_DATA__ JSON: {exc}") from exc

        products = _extract_store_products_by_category(root) or _deep_find_products(root)
        if not products:
            logger.warning("RexailParser: no product list located in JSON tree")
            return []

        out: list[RawItem] = []
        for p in products:
            if not isinstance(p, dict):
                continue
            name = _product_row_display_name(p) or _pick_str(
                p, "name", "title", "productName", "heName", "displayName"
            )
            price_raw = _pick_price(p)
            if not name or not price_raw:
                continue
            m = _PRICE_RE.search(str(price_raw).replace(",", ""))
            raw_price = m.group(0) if m else str(price_raw)
            unit = _product_row_unit(p)
            out.append(
                RawItem(
                    raw_product_name=name[:500],
                    raw_price_text=raw_price,
                    raw_unit_text=unit,
                    raw_quantity_text=None,
                    raw_payload_json={"parser": "rexail"},
                )
            )
        return out
