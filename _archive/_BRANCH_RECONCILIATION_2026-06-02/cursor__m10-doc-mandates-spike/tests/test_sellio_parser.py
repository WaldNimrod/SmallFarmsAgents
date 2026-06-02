"""Unit tests for Sellio / Teva-style title-grid parser (M10.5)."""

from __future__ import annotations

from organic_market_agent.parsers.sellio import SellioParser


def _fixture_grid() -> bytes:
    return """
    <html><body>
    <a href="#" title="עגבניה אורגנית 12.5₪" onclick="product_details(1)">x</a>
    <a href="#" title="פסטה רגילה 9.9₪" onclick="product_details(2)">x</a>
    <a href="#" title="פסטה כוסמין אורגנית – השדה 19.9₪" onclick="product_details(3)">x</a>
    </body></html>
    """.encode(
        "utf-8"
    )


def test_sellio_parses_title_prices() -> None:
    p = SellioParser({})
    items = p.parse(_fixture_grid(), "utf-8")
    names = {i.raw_product_name for i in items}
    assert "עגבניה אורגנית" in names
    assert "פסטה רגילה" in names


def test_sellio_organic_only_filters_conventional() -> None:
    p = SellioParser({"sellio_organic_only": True})
    items = p.parse(_fixture_grid(), "utf-8")
    names = {i.raw_product_name for i in items}
    assert "עגבניה אורגנית" in names
    assert "פסטה כוסמין אורגנית – השדה" in names
    assert "פסטה רגילה" not in names


def test_sellio_organic_detects_english() -> None:
    html = '<html><body><a title="Organic tomato 5.5₪" href="#">x</a></body></html>'.encode(
        "utf-8"
    )
    p = SellioParser({"sellio_organic_only": True})
    items = p.parse(html, "utf-8")
    assert len(items) == 1
    assert "Organic tomato" in items[0].raw_product_name


def test_sellio_skips_malformed_title() -> None:
    html = b'<html><body><a title="no price here" href="#">x</a></body></html>'
    assert SellioParser({}).parse(html, "utf-8") == []


def test_sellio_dedupes_duplicate_titles() -> None:
    html = """
    <html><body>
    <a title="חסה אורגנית 8₪" href="#">1</a>
    <a title="חסה אורגנית 8₪" href="#">2</a>
    </body></html>
    """.encode("utf-8")
    items = SellioParser({}).parse(html, "utf-8")
    assert len(items) == 1
