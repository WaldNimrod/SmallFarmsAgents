"""Smoke tests for M10.3 static parsers."""

from __future__ import annotations

import json

from organic_market_agent.parsers.eranorgani import EranorganiParser
from organic_market_agent.parsers.nizat import NizatParser
from organic_market_agent.parsers.rexail import RexailParser
from organic_market_agent.parsers.tamari import TamariParser


def test_nizat_parser_extracts_cube() -> None:
    html = """
    <html><body>
    <div class="productcubecontainer">
      <div class="productcubepname">\u05e2\u05d2\u05d1\u05e0\u05d9\u05d4 \u05e9\u05e8\u05d9</div>
      <div class="productcubeprice">&#8362;12.00 \u05dc\u05e7"\u05d2</div>
    </div>
    </body></html>
    """.encode("utf-8")
    items = NizatParser().parse(html)
    assert len(items) == 1
    assert items[0].raw_product_name
    assert items[0].raw_price_text


def test_rexail_parser_next_data() -> None:
    payload = {
        "props": {
            "pageProps": {
                "catalog": {
                    "products": [
                        {"name": "Test Veg", "price": "18.5"},
                    ]
                }
            }
        }
    }
    html = (
        '<html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(payload)
        + "</script></html>"
    ).encode("utf-8")
    items = RexailParser().parse(html)
    assert len(items) == 1
    assert items[0].raw_product_name == "Test Veg"


def test_rexail_parser_store_products_by_category() -> None:
    payload = {
        "props": {
            "pageProps": {
                "initialReduxState": {
                    "storeProduct": {
                        "storeProductsByCategoryId": {
                            "1": [
                                {
                                    "secondaryName": "Test \nVeg",
                                    "price": 12.5,
                                    "product": {
                                        "primaryQuantityUnit": {"name": '\u05e7"\u05d2'}
                                    },
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
    html = (
        '<html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(payload)
        + "</script></html>"
    ).encode("utf-8")
    items = RexailParser().parse(html)
    assert len(items) == 1
    assert items[0].raw_product_name == "Test Veg"
    assert items[0].raw_price_text == "12.5"
    assert items[0].raw_unit_text


def test_eranorgani_parser_selector_grid() -> None:
    html = """
    <html><body>
    <div class="product-box text-center">
      <h4>\u05d7\u05e1\u05d4 \u05d0\u05d5\u05e8\u05d2\u05e0\u05d9</h4>
      <div class="price-box">9.90 &#8362; ~\u05d9\u05d7\u05d9\u05d3\u05d4</div>
    </div>
    </body></html>
    """.encode("utf-8")
    items = EranorganiParser().parse(html)
    assert len(items) >= 1


def test_tamari_parser_selector_grid() -> None:
    html = """
    <html><body>
    <li class="product">
      <h2 class="woocommerce-loop-product__title">\u05d1\u05e6\u05dc</h2>
      <span class="price">&#8362;5</span>
    </li>
    </body></html>
    """.encode("utf-8")
    items = TamariParser().parse(html)
    assert len(items) >= 1
