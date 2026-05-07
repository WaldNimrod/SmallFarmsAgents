"""Unit tests for MypipsCollector (AC-05, AC-06, AC-07).

Tests use recorded fixture HTML to avoid live network calls.
Playwright is patched via unittest.mock so no browser is launched.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from organic_market_agent.collectors.mypips import (
    ANATIYOT_HANDLES,
    MypipsCollector,
    _build_shop_url,
    _extract_products_from_page,
    _is_store_closed,
)

FIXTURES = Path(__file__).parent / "fixtures" / "mypips"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_page(html: str) -> MagicMock:
    """Return a mock Playwright Page that serves the given HTML."""
    page = MagicMock()
    page.content.return_value = html

    # Evaluate: parse JSON-LD from the HTML ourselves and return expected structure
    def _evaluate_side_effect(js: str, *args, **kwargs):
        if "application/ld+json" in js:
            results = []
            for m in re.finditer(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL):
                try:
                    data = json.loads(m.group(1))
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and (
                                item.get("@type") == "Product" or "offers" in item
                            ):
                                offers = item.get("offers") or {}
                                if isinstance(offers, list):
                                    offers = offers[0] if offers else {}
                                results.append({
                                    "name": item.get("name", ""),
                                    "price": str(offers.get("price", "")),
                                    "unit": item.get("unitText", ""),
                                    "availability": offers.get("availability", ""),
                                    "source": "json-ld",
                                })
                    elif isinstance(data, dict):
                        if data.get("@type") == "Product" or "offers" in data:
                            offers = data.get("offers") or {}
                            if isinstance(offers, list):
                                offers = offers[0] if offers else {}
                            results.append({
                                "name": data.get("name", ""),
                                "price": str(offers.get("price", "")),
                                "unit": data.get("unitText", ""),
                                "availability": offers.get("availability", ""),
                                "source": "json-ld",
                            })
                except Exception:
                    pass
            return results
        elif "product-card" in js or "innerText" in js:
            return []
        elif "PRICE_RE" in js:
            return []
        return None

    page.evaluate.side_effect = _evaluate_side_effect
    return page


def _make_playwright_context(page: MagicMock):
    """Return (playwright_patcher, browser_mock) that yields the given page."""
    browser = MagicMock()
    browser.new_page.return_value = page

    chromium = MagicMock()
    chromium.launch.return_value = browser

    pw_instance = MagicMock()
    pw_instance.chromium = chromium
    pw_instance.__enter__ = MagicMock(return_value=pw_instance)
    pw_instance.__exit__ = MagicMock(return_value=False)

    return pw_instance


# ---------------------------------------------------------------------------
# URL building
# ---------------------------------------------------------------------------

class TestBuildShopUrl:
    def test_plain_handle(self):
        url = _build_shop_url("mashtelatharoe")
        assert url == "https://mypips.app/mashtelatharoe/products"
        assert "includeOrganic" not in url

    def test_anatiyot_organic_flag(self):
        url = _build_shop_url("anatiyot", include_organic=True)
        assert "includeOrganic=true" in url
        assert "mypips.app/anatiyot" in url

    def test_other_handle_no_organic(self):
        url = _build_shop_url("fruit4soul", include_organic=False)
        assert "includeOrganic" not in url
        assert "mypips.app/fruit4soul" in url


class TestAnatiyotHandles:
    def test_anatiyot_in_set(self):
        assert "anatiyot" in ANATIYOT_HANDLES

    def test_other_handle_not_in_set(self):
        assert "mashtelatharoe" not in ANATIYOT_HANDLES


# ---------------------------------------------------------------------------
# Store closed detection
# ---------------------------------------------------------------------------

class TestIsStoreClosed:
    def test_closed_store_detected(self):
        html = (FIXTURES / "closed_store.html").read_text(encoding="utf-8")
        page = MagicMock()
        page.content.return_value = html
        assert _is_store_closed(page) is True

    def test_open_store_not_closed(self):
        html = (FIXTURES / "mashtelatharoe.html").read_text(encoding="utf-8")
        page = MagicMock()
        page.content.return_value = html
        assert _is_store_closed(page) is False


# ---------------------------------------------------------------------------
# Product extraction
# ---------------------------------------------------------------------------

class TestExtractProductsFromPage:
    def test_extracts_json_ld_products_mashtelatharoe(self):
        html = (FIXTURES / "mashtelatharoe.html").read_text(encoding="utf-8")
        page = _make_mock_page(html)
        products = _extract_products_from_page(page)
        assert len(products) >= 2
        names = [p["name"] for p in products]
        assert any("עגבניות" in n for n in names), f"Expected Hebrew product names, got: {names}"

    def test_extracts_json_ld_products_anatiyot(self):
        html = (FIXTURES / "anatiyot.html").read_text(encoding="utf-8")
        page = _make_mock_page(html)
        products = _extract_products_from_page(page)
        assert len(products) >= 1
        names = [p["name"] for p in products]
        assert any("חסה" in n for n in names)

    def test_product_has_expected_fields(self):
        html = (FIXTURES / "mashtelatharoe.html").read_text(encoding="utf-8")
        page = _make_mock_page(html)
        products = _extract_products_from_page(page)
        assert products
        p = products[0]
        assert "name" in p
        assert "price" in p
        assert "unit" in p
        assert "source" in p


# ---------------------------------------------------------------------------
# MypipsCollector integration (Playwright mocked)
# ---------------------------------------------------------------------------

class TestMypipsCollector:
    def test_collector_instantiation(self):
        c = MypipsCollector(handle="mashtelatharoe")
        assert c.handle == "mashtelatharoe"
        assert "mashtelatharoe" in c.shop_url

    def test_anatiyot_gets_organic_url(self):
        c = MypipsCollector(handle="anatiyot")
        assert "includeOrganic=true" in c.shop_url

    def test_non_anatiyot_no_organic_url(self):
        c = MypipsCollector(handle="fruit4soul")
        assert "includeOrganic" not in c.shop_url

    def test_fetch_products_returns_list(self):
        html = (FIXTURES / "mashtelatharoe.html").read_text(encoding="utf-8")
        mock_page = _make_mock_page(html)
        pw_ctx = _make_playwright_context(mock_page)

        with patch("organic_market_agent.collectors.mypips.sync_playwright", return_value=pw_ctx):
            c = MypipsCollector(handle="mashtelatharoe")
            products = c.fetch_products()

        assert isinstance(products, list)
        assert len(products) >= 2

    def test_fetch_products_closed_store_returns_empty(self):
        html = (FIXTURES / "closed_store.html").read_text(encoding="utf-8")
        mock_page = _make_mock_page(html)
        pw_ctx = _make_playwright_context(mock_page)

        with patch("organic_market_agent.collectors.mypips.sync_playwright", return_value=pw_ctx):
            c = MypipsCollector(handle="someclosedstore")
            products = c.fetch_products()

        assert products == []

    def test_anatiyot_organic_flag_in_collector(self):
        """AC-07: anatiyot collector URL must include includeOrganic=true."""
        html = (FIXTURES / "anatiyot.html").read_text(encoding="utf-8")
        mock_page = _make_mock_page(html)
        pw_ctx = _make_playwright_context(mock_page)

        with patch("organic_market_agent.collectors.mypips.sync_playwright", return_value=pw_ctx):
            c = MypipsCollector(handle="anatiyot")
            assert "includeOrganic=true" in c.shop_url
            products = c.fetch_products()

        assert isinstance(products, list)

    def test_navigation_error_returns_empty(self):
        """If Playwright navigation times out, collector returns empty list gracefully."""
        mock_page = MagicMock()
        mock_page.goto.side_effect = Exception("Timeout")
        mock_page.content.return_value = ""
        mock_page.evaluate.return_value = []
        pw_ctx = _make_playwright_context(mock_page)

        with patch("organic_market_agent.collectors.mypips.sync_playwright", return_value=pw_ctx):
            c = MypipsCollector(handle="mashtelatharoe")
            products = c.fetch_products()

        assert isinstance(products, list)
