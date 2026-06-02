"""Unit tests for CSA basket parsers (M10.5)."""

from __future__ import annotations

from organic_market_agent.parsers.csa_basket import CsaBasketParser


def test_csa_havat_shorashim_extracts_three_baskets() -> None:
    html = """
    <html><body>
    <p>מחירים וגדלים</p>
    <p>סל קטן</p>
    <p>סל גדול</p>
    <h1><span>₪ 120</span></h1>
    <p>מחיר</p>
    <h1><span>₪ 140</span></h1>
    <p>חדש! סל סטודנטים*</p>
    <h1><span>₪ 90</span></h1>
    </body></html>
    """
    p = CsaBasketParser({"csa_site": "havat_shorashim"})
    items = p.parse(html.encode("utf-8"), "utf-8")
    by_name = {i.raw_product_name: i.raw_price_text for i in items}
    assert by_name.get("סל קטן") == "120"
    assert by_name.get("סל גדול") == "140"
    assert by_name.get("סל סטודנטים") == "90"
    for it in items:
        assert it.raw_payload_json.get("parser") == "csa_basket"
        assert "csa_context" in it.raw_payload_json


def test_csa_meshek_organi_two_baskets() -> None:
    html = """
    <html><body>
    <p>סל ירקות אורגני משפחתי עולה 165 ש"ח וסל ירקות אורגני בסיסי עולה 125 ש"ח</p>
    <p>סל ירקות אורגני משפחתי יכיל 14 סוגי ירקות.</p>
    <p>סל ירקות אורגני בסיסי יכיל 10 סוגי ירקות.</p>
    <p>משלוח חינם</p>
    </body></html>
    """
    p = CsaBasketParser({"csa_site": "meshek_organi"})
    items = p.parse(html.encode("utf-8"), "utf-8")
    names = {i.raw_product_name for i in items}
    assert "סל ירקות אורגני משפחתי" in names
    assert "סל ירקות אורגני בסיסי" in names
    prices = {i.raw_product_name: i.raw_price_text for i in items}
    assert prices["סל ירקות אורגני משפחתי"] == "165"
    assert prices["סל ירקות אורגני בסיסי"] == "125"


def test_csa_meshek_organi_decodes_html_entities_for_shekel() -> None:
    """Wix pages may emit ש&quot;ח — html.unescape must yield ש\"ח for regex match."""
    html = """
    <html><body>
    <p>סל ירקות אורגני משפחתי עולה 165 ש&quot;ח וסל ירקות אורגני בסיסי עולה 125 ש&quot;ח</p>
    <p>סל ירקות אורגני משפחתי יכיל 14 סוגי ירקות.</p>
    <p>סל ירקות אורגני בסיסי יכיל 10 סוגי ירקות.</p>
    </body></html>
    """
    p = CsaBasketParser({"csa_site": "meshek_organi"})
    items = p.parse(html.encode("utf-8"), "utf-8")
    prices = {i.raw_product_name: i.raw_price_text for i in items}
    assert prices["סל ירקות אורגני משפחתי"] == "165"
    assert prices["סל ירקות אורגני בסיסי"] == "125"


def test_csa_meshek_yosef_returns_empty() -> None:
    html = "<html><body><p>דמי משלוח 30 ש\"ח</p></body></html>"
    p = CsaBasketParser({"csa_site": "meshek_yosef"})
    assert p.parse(html.encode("utf-8"), "utf-8") == []


def test_csa_unknown_site_empty() -> None:
    p = CsaBasketParser({"csa_site": "unknown"})
    assert p.parse(b"<html></html>", "utf-8") == []


def test_csa_shekel_line_baskets_multi_match() -> None:
    html = """
    <html><body>
    <p>מבצע: סל ירקות אורגני גדול עולה 210 ש"ח ומיד אחריו סל ירקות אורגני זוגי 180 ש"ח.</p>
    <p>משלוח בתיאום מראש</p>
    </body></html>
    """
    p = CsaBasketParser(
        {"csa_site": "shekel_line_baskets", "shekel_require_organic": True}
    )
    items = p.parse(html.encode("utf-8"), "utf-8")
    prices = {i.raw_product_name: i.raw_price_text for i in items}
    assert prices.get("סל ירקות אורגני גדול עולה") == "210"
    assert prices.get("סל ירקות אורגני זוגי") == "180"
    for it in items:
        assert it.raw_payload_json.get("csa_site") == "shekel_line_baskets"
        assert "csa_context" in it.raw_payload_json


def test_csa_shekel_line_baskets_require_organic_filters() -> None:
    html = """
    <html><body>
    <p>סל פירות 99 ש"ח וסל ירקות אורגני 120 ש"ח</p>
    </body></html>
    """
    p = CsaBasketParser(
        {"csa_site": "shekel_line_baskets", "shekel_require_organic": True}
    )
    items = p.parse(html.encode("utf-8"), "utf-8")
    assert len(items) == 1
    assert items[0].raw_price_text == "120"
    assert "אורגני" in items[0].raw_product_name
