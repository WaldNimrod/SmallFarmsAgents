"""MypipsCollector — Playwright-based collector for mypips.app storefronts.

MyPIPS stores render their product catalog via Firestore + React/MUI into the DOM.
Standard HTTP fetchers get the SPA shell only (no product data), so we use
Playwright headless Chromium to wait for the Firestore render to complete.

URL pattern:
    Store home:    https://mypips.app/{handle}
    Products page: https://mypips.app/{handle}/products  ← preferred for extraction

Usage (standalone smoke):
    from organic_market_agent.collectors.mypips import MypipsCollector
    c = MypipsCollector(handle="mashtelatharoe")
    items = c.fetch_products()

AC-07: anatiyot gets includeOrganic=true query param appended to URL.
"""
from __future__ import annotations

import re
from typing import Any

from playwright.sync_api import Page, sync_playwright

from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Base URL template: mypips.app (not mypips.co.il/shop which is a Wix 404)
MYPIPS_BASE = "https://mypips.app/{handle}/products"
MYPIPS_HOME = "https://mypips.app/{handle}"

# Handles that require includeOrganic=true (AC-07)
ANATIYOT_HANDLES = {"anatiyot"}

# Playwright wait timeout (ms) — Firestore stores can be slow to hydrate
_PAGE_TIMEOUT_MS = 30_000
_NETWORK_IDLE_TIMEOUT_MS = 20_000

# Hebrew "store closed" indicators
_CLOSED_PHRASES = (
    "החנות סגורה",
    "הזמנות סגורות",
    "לא זמין להזמנה",
    "בית עסק זה אינו פעיל",
    "store is closed",
)


def _build_shop_url(handle: str, include_organic: bool = False) -> str:
    url = MYPIPS_BASE.format(handle=handle)
    if include_organic:
        url += ("&" if "?" in url else "?") + "includeOrganic=true"
    return url


def _is_store_closed(page: Page) -> bool:
    """Return True if the page signals the store is closed / inactive."""
    try:
        content = page.content()
        for phrase in _CLOSED_PHRASES:
            if phrase in content:
                return True
    except Exception:
        pass
    return False


def _extract_products_from_page(page: Page) -> list[dict[str, Any]]:
    """Extract products from mypips.app React/Firestore DOM.

    Strategy 1: pips-card-content / bordered-card class selectors (primary — verified live)
    Strategy 2: JSON-LD Product markup
    Strategy 3: Text-fallback — Hebrew text near price patterns
    """
    products: list[dict[str, Any]] = []

    # Strategy 1: MyPIPS React card DOM (primary — verified against live stores 2026-05-07)
    try:
        dom_products = page.evaluate("""() => {
            // Primary: .pips-card-content inside .bordered-card (live DOM pattern)
            const cards = Array.from(document.querySelectorAll('.bordered-card, [class*="pips-card"]'));
            if (cards.length > 0) {
                return cards.map(card => {
                    const text = card.innerText || '';
                    const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                    // Lines pattern: [product_name, store_name?, description?, order_btn?, price, unit]
                    const name = lines[0] || '';
                    // Price: lines containing ₪ or followed by unit
                    let price = null;
                    let unit = '';
                    for (let i = 0; i < lines.length; i++) {
                        const l = lines[i];
                        if (l.includes('₪')) {
                            price = l.replace(/[^0-9.,]/g, '').trim();
                            // unit is next line or same line after ₪
                            const unitMatch = text.match(/₪[\\d.,]+\\s*(.{1,20})/);
                            if (unitMatch) unit = unitMatch[1].trim();
                            break;
                        }
                    }
                    // Availability
                    const avail = lines.some(l =>
                        l.includes('הרשמו') || l.includes('התחברו') || l.includes('הוסף לסל')
                    ) ? 'available' : 'unknown';

                    return { name, price, unit, availability: avail, source: 'dom-pips-card' };
                }).filter(p => p.name && p.name.length > 1);
            }

            // Fallback: generic product-card / product-item selectors
            const genericCards = Array.from(document.querySelectorAll(
                '[class*="product-card"], [class*="item-card"], [class*="product-item"], [data-product-id]'
            ));
            return genericCards.map(card => {
                const nameEl = card.querySelector('[class*="name"], [class*="title"], h2, h3, h4, strong');
                const priceEl = card.querySelector('[class*="price"], [class*="amount"]');
                const unitEl = card.querySelector('[class*="unit"], [class*="weight"]');
                const availEl = card.querySelector('[class*="avail"], [class*="stock"], [class*="order"]');
                return {
                    name: nameEl ? nameEl.innerText.trim() : '',
                    price: priceEl ? priceEl.innerText.trim() : null,
                    unit: unitEl ? unitEl.innerText.trim() : '',
                    availability: availEl ? availEl.innerText.trim() : '',
                    source: 'dom-generic',
                };
            }).filter(p => p.name);
        }""")
        if dom_products:
            products.extend(dom_products)
    except Exception as exc:
        logger.debug("DOM card extraction failed: %s", exc)

    if products:
        return products

    # Strategy 2: JSON-LD Product markup
    try:
        ld_products = page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
            const out = [];
            for (const s of scripts) {
                try {
                    const d = JSON.parse(s.textContent);
                    const items = Array.isArray(d) ? d : (d['@graph'] ? d['@graph'] : [d]);
                    for (const item of items) {
                        if (!item || (item['@type'] !== 'Product' && !item.offers)) continue;
                        const offers = Array.isArray(item.offers) ? item.offers[0] : (item.offers || {});
                        out.push({
                            name: item.name || '',
                            price: String(offers.price || item.price || ''),
                            unit: item.unitText || item.unit || '',
                            availability: offers.availability || '',
                            source: 'json-ld',
                        });
                    }
                } catch {}
            }
            return out.filter(p => p.name);
        }""")
        if ld_products:
            products.extend(ld_products)
    except Exception as exc:
        logger.debug("JSON-LD extraction failed: %s", exc)

    if products:
        return products

    # Strategy 3: text fallback — Hebrew text near price patterns
    try:
        text_products = page.evaluate("""() => {
            const PRICE_RE = /\\d+(\\.\\d+)?\\s*(₪|ש"ח|שקל)/;
            const paras = Array.from(document.querySelectorAll('p, span, div, li'));
            const out = [];
            for (const el of paras) {
                const t = el.innerText ? el.innerText.trim() : '';
                if (!t || t.length > 200) continue;
                if (/[\\u0590-\\u05FF]/.test(t) && PRICE_RE.test(t)) {
                    out.push({ name: t, price: null, unit: '', availability: '', source: 'text-fallback' });
                }
            }
            return out.slice(0, 50);
        }""")
        if text_products:
            products.extend(text_products)
    except Exception as exc:
        logger.debug("Text fallback extraction failed: %s", exc)

    return products


class MypipsCollector:
    """Playwright-based collector for mypips.app storefronts.

    This class is intentionally standalone (not extending BaseCollector) because:
    - BaseCollector assumes HTTP fetch → raw bytes → file storage pipeline
    - MyPIPS requires Playwright headless rendering → structured extraction
    - Integration with the ingestion pipeline (SourceFetchRun, RawAsset) is Phase 3

    Phase 2 contract: fetch_products() returns list[dict] with keys:
        name, price, unit, availability, source
    """

    def __init__(
        self,
        handle: str,
        session: Any = None,
        config: Any = None,
        headless: bool = True,
        timeout_ms: int = _PAGE_TIMEOUT_MS,
    ) -> None:
        self.handle = handle
        self.session = session
        self.config = config
        self.headless = headless
        self.timeout_ms = timeout_ms
        include_organic = handle in ANATIYOT_HANDLES
        self.shop_url = _build_shop_url(handle, include_organic=include_organic)

    def fetch_products(self) -> list[dict[str, Any]]:
        """Navigate to the store products page, wait for Firestore render, extract products.

        Returns empty list if store is closed or no products found.
        """
        logger.info("MypipsCollector: fetching handle=%r url=%s", self.handle, self.shop_url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            try:
                page = browser.new_page()
                page.set_default_timeout(self.timeout_ms)

                try:
                    page.goto(self.shop_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                    # Wait for network idle so Firestore has time to hydrate
                    page.wait_for_load_state("networkidle", timeout=_NETWORK_IDLE_TIMEOUT_MS)
                except Exception as exc:
                    logger.warning("Navigation timeout/error for %r: %s", self.handle, exc)
                    # Proceed anyway — partial renders may still have data

                if _is_store_closed(page):
                    logger.info("Store %r is closed; returning empty catalog", self.handle)
                    return []

                products = _extract_products_from_page(page)
                logger.info(
                    "MypipsCollector: handle=%r extracted %d products", self.handle, len(products)
                )
                return products
            finally:
                browser.close()

    def save_fixture(self, fixture_dir: str) -> str:
        """Capture page HTML to a fixture file for offline testing.

        Returns the path of the written fixture.
        """
        import os
        os.makedirs(fixture_dir, exist_ok=True)
        fixture_path = os.path.join(fixture_dir, f"{self.handle}.html")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            try:
                page = browser.new_page()
                page.set_default_timeout(self.timeout_ms)
                page.goto(self.shop_url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=_NETWORK_IDLE_TIMEOUT_MS)
                except Exception:
                    pass
                html = page.content()
                with open(fixture_path, "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("Saved fixture: %s (%d bytes)", fixture_path, len(html))
                return fixture_path
            finally:
                browser.close()
