"""Unit tests for MypipsParser (no Playwright)."""

from __future__ import annotations

from organic_market_agent.parsers.mypips import MypipsParser


def _card(name: str, price: str) -> str:
    return (
        f'<div class="pips-card-content">'
        f'<h6 class="MuiTypography-h6">{name}</h6>'
        f'<h5 class="MuiTypography-h5">{price}</h5>'
        f"</div>"
    )


def test_mypips_parser_single_card() -> None:
    html = f"<html><body>{_card('עגבנייה שרי', '₪12.5')}</body></html>".encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 1
    assert items[0].raw_product_name == "עגבנייה שרי"
    assert items[0].raw_price_text == "12.5"


def test_mypips_parser_multiple_cards() -> None:
    html = (
        "<html><body>"
        + _card("בננה", "₪9.9")
        + _card("מלפפון", "₪6")
        + "</body></html>"
    ).encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 2


def test_mypips_parser_dedupes_same_name_price() -> None:
    frag = _card("חסה", "₪8")
    html = f"<html><body>{frag}{frag}</body></html>".encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 1


def test_mypips_parser_skips_title_without_price() -> None:
    html = (
        '<html><body><div class="pips-card-content">'
        '<h6>ללא מחיר</h6><span>טקסט</span></div></body></html>'
    ).encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 0


def test_mypips_parser_empty_shell() -> None:
    html = b"<html><body><div id='root'></div></body></html>"
    items = MypipsParser().parse(html)
    assert len(items) == 0


def test_mypips_parser_nis_abbreviation() -> None:
    html = (
        "<html><body>"
        + _card("דלעת", "NIS 4.5")
        + "</body></html>"
    ).encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 1
    assert items[0].raw_price_text == "4.5"


def test_mypips_parser_h5_title_price_in_span() -> None:
    """Some storefronts use h5 for product name and a sibling span for ₪ price."""
    html = (
        '<html><body><div class="pips-card-content">'
        '<h5 class="MuiTypography-h5">מלפפון בייבי אורגני</h5>'
        '<span class="price">₪ 7.90</span>'
        "</div></body></html>"
    ).encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 1
    assert "מלפפון" in items[0].raw_product_name
    assert items[0].raw_price_text == "7.90"


def test_mypips_parser_price_anchor_fallback_without_pips_class() -> None:
    """Stores without div.pips-card-content still expose heading + currency sibling."""
    html = (
        '<html><body><main>'
        '<div class="MuiGrid-item"><h6>גזר אורגני</h6><span>₪ 4.50</span></div>'
        '<div class="MuiGrid-item"><h6>סלק</h6><span>₪ 3.00</span></div>'
        "</main></body></html>"
    ).encode("utf-8")
    items = MypipsParser().parse(html)
    assert len(items) == 2
    names = {i.raw_product_name for i in items}
    assert "גזר אורגני" in names
    assert "סלק" in names


def test_mypips_parser_custom_card_selector_override() -> None:
    html = (
        '<html><body><div class="custom-pips-card pips-card-content">'
        "<h6>שום</h6><h5>₪3</h5>"
        "</div></body></html>"
    ).encode("utf-8")
    items = MypipsParser({"card_selector": "div.custom-pips-card"}).parse(html)
    assert len(items) == 1
    assert items[0].raw_product_name == "שום"
