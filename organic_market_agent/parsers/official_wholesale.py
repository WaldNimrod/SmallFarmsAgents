"""Parser for official/government wholesale price JSON endpoints."""
from __future__ import annotations

import json
from typing import Optional

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_NAME_KEYS = ("product_name", "name", "item", "commodity", "productName", "שם_מוצר", "מוצר")
_PRICE_KEYS = ("price", "avg_price", "price_nis", "מחיר", "מחיר_ממוצע")
_UNIT_KEYS = ("unit", "unit_type", "יחידה", "unit_name")
_QTY_KEYS = ("quantity", "qty", "weight", "כמות")


def _find_key(row: dict, candidates: tuple[str, ...]) -> Optional[str]:
    for k in candidates:
        if k in row:
            val = row[k]
            if val is None:
                return None
            return str(val)
    return None


class OfficialWholesaleParser(BaseParser):
    """Parses JSON arrays from government wholesale price APIs."""

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        _ = charset_hint
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ParserError(f"OfficialWholesaleParser: invalid JSON: {exc}") from exc

        if isinstance(data, dict):
            for key in ("data", "results", "items", "products", "rows"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break

        if not isinstance(data, list):
            raise ParserError("OfficialWholesaleParser: expected a JSON array")

        items: list[RawItem] = []
        for row in data:
            if not isinstance(row, dict):
                continue
            items.append(
                RawItem(
                    raw_product_name=_find_key(row, _NAME_KEYS),
                    raw_price_text=_find_key(row, _PRICE_KEYS),
                    raw_unit_text=_find_key(row, _UNIT_KEYS),
                    raw_quantity_text=_find_key(row, _QTY_KEYS),
                    raw_payload_json=dict(row),
                )
            )

        logger.info("OfficialWholesaleParser: extracted %d items", len(items))
        return items
