"""Unit tests for parsers — purely in-memory where possible, no live HTTP."""
from __future__ import annotations

import json

import pytest

from organic_market_agent.parsers.easyfarm_catalog import DEFAULT_SELECTORS, EasyFarmCatalogParser
from organic_market_agent.parsers.official_wholesale import OfficialWholesaleParser
from organic_market_agent.parsers.simple_product_grid import SimpleProductGridParser
from organic_market_agent.utils.exceptions import ParserError

EASYFARM_HTML = """
<html><body>
  <div class="product-item">
    <span class="product-name">עגבניות שרי</span>
    <span class="product-price">18</span>
    <span class="product-unit">ק"ג</span>
  </div>
  <div class="product-item">
    <span class="product-name">מלפפון</span>
    <span class="product-price">12</span>
    <span class="product-unit">ק"ג</span>
  </div>
</body></html>
""".encode("utf-8")


def test_easyfarm_extracts_two_items():
    parser = EasyFarmCatalogParser()
    items = parser.parse(EASYFARM_HTML)
    assert len(items) == 2
    assert items[0].raw_price_text == "18"


def test_easyfarm_empty_page_returns_empty_list():
    parser = EasyFarmCatalogParser()
    items = parser.parse(b"<html><body></body></html>")
    assert items == []


def test_easyfarm_selector_override_merges_defaults():
    override = {"product_row": "div.product-item"}
    parser = EasyFarmCatalogParser(selector_overrides=override)
    assert parser._selectors["product_row"] == "div.product-item"
    assert parser._selectors["name"] == DEFAULT_SELECTORS["name"]


TABLE_HTML = """
<html><body>
<table>
  <tr><td>גזר</td><td>8 ₪/ק"ג</td><td>ק"ג</td></tr>
  <tr><td>תפוח אדמה</td><td>5 ₪/ק"ג</td><td>ק"ג</td></tr>
</table>
</body></html>
""".encode("utf-8")


def test_simple_grid_table_extracts_items():
    parser = SimpleProductGridParser()
    items = parser.parse(TABLE_HTML)
    assert len(items) == 2


def test_simple_grid_no_prices_returns_empty():
    parser = SimpleProductGridParser()
    items = parser.parse(b"<html><body><p>hello world</p></body></html>")
    assert items == []


LIST_HTML = b"""
<html><body>
<ul>
  <li>Organic carrots 12 NIS per kg</li>
</ul>
</body></html>
"""


def test_simple_grid_list_fallback_extracts():
    parser = SimpleProductGridParser()
    items = parser.parse(LIST_HTML)
    assert len(items) >= 1
    assert "carrots" in (items[0].raw_product_name or "").lower()


GOVT_JSON = json.dumps(
    [
        {"product_name": "עגבניה", "price": "15.5", "unit": 'ק"ג'},
        {"product_name": "פלפל", "price": "22.0", "unit": 'ק"ג'},
    ],
    ensure_ascii=False,
).encode("utf-8")

GOVT_JSON_WRAPPED = json.dumps(
    {"data": [{"product_name": "בצל", "price": "6.0"}]},
    ensure_ascii=False,
).encode("utf-8")


def test_official_wholesale_parses_array():
    parser = OfficialWholesaleParser()
    items = parser.parse(GOVT_JSON)
    assert len(items) == 2
    assert items[0].raw_price_text == "15.5"


def test_official_wholesale_unwraps_envelope():
    parser = OfficialWholesaleParser()
    items = parser.parse(GOVT_JSON_WRAPPED)
    assert len(items) == 1


def test_official_wholesale_raises_on_invalid_json():
    parser = OfficialWholesaleParser()
    with pytest.raises(ParserError):
        parser.parse(b"not json")


def test_official_wholesale_raises_on_non_list_payload():
    parser = OfficialWholesaleParser()
    payload = json.dumps({"not_an_array": True}).encode()
    with pytest.raises(ParserError, match="expected a JSON array"):
        parser.parse(payload)
