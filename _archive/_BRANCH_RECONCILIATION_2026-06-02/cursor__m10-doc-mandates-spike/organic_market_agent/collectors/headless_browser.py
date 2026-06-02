"""Headless Chromium collector — renders JS-heavy pages (Playwright)."""

from __future__ import annotations

import os
import time
from typing import Any

from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.config import config
from organic_market_agent.utils.exceptions import CollectorError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class HeadlessBrowserCollector(BaseCollector):
    """Fetches HTML after client-side rendering via Playwright.

    Profile keys (optional):
    - selector_profile.wait_for: CSS selector to wait for after navigation (default: ``main``).
    - selector_profile.post_load_delay_ms: extra wait after domcontentloaded (default: 0).
    - selector_profile.headless_scroll_passes: scroll to bottom this many times (default: 0).
    - selector_profile.headless_scroll_pause_ms: pause between scroll passes (default: 1200).
    - selector_profile.headless_merge_urls: extra URLs to load in the same browser context; body
      HTML fragments are concatenated so parsers (e.g. Sellio) see a merged DOM.
    """

    def _selector_profile(self) -> dict[str, Any]:
        sp = self.profile.get("selector_profile")
        return sp if isinstance(sp, dict) else {}

    def _playwright_context_kwargs(self) -> dict[str, Any]:
        """Optional browser context from ``selector_profile`` (user agent, locale, headers)."""
        sp = self._selector_profile()
        kwargs: dict[str, Any] = {}
        ua = sp.get("user_agent")
        if isinstance(ua, str) and ua.strip():
            kwargs["user_agent"] = ua.strip()
        loc = sp.get("locale")
        if isinstance(loc, str) and loc.strip():
            kwargs["locale"] = loc.strip()
        tz = sp.get("timezone_id")
        if isinstance(tz, str) and tz.strip():
            kwargs["timezone_id"] = tz.strip()
        eh = sp.get("extra_http_headers")
        if isinstance(eh, dict) and eh:
            kwargs["extra_http_headers"] = {str(k): str(v) for k, v in eh.items()}
        return kwargs

    @staticmethod
    def _e2e_cache_bust_url(url: str) -> str:
        """Append unique query param when ``RUN_MYPIPS_E2E`` is set (integration tests)."""
        if os.environ.get("RUN_MYPIPS_E2E", "").lower() not in ("1", "true", "yes"):
            return url
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}_oma_e2e={int(time.time() * 1000)}"

    def _prepare_page(self, page: Any, url: str) -> None:
        """Navigate and wait for content. Subclasses may override (e.g. mypips popups/tabs)."""
        timeout_ms = config.PLAYWRIGHT_TIMEOUT_MS
        page.set_default_timeout(timeout_ms)
        sp = self._selector_profile()
        post_delay = int(sp.get("post_load_delay_ms", 0) or 0)
        wait_for = (sp.get("wait_for") or "main").strip() or "main"

        goto_wu = (sp.get("goto_wait_until") or "domcontentloaded").strip()
        if goto_wu not in ("load", "domcontentloaded", "commit", "networkidle"):
            goto_wu = "domcontentloaded"
        page.goto(url, wait_until=goto_wu, timeout=timeout_ms)
        if post_delay > 0:
            page.wait_for_timeout(post_delay)
        try:
            page.wait_for_selector(wait_for, timeout=timeout_ms, state="attached")
        except Exception as exc:
            logger.warning(
                "HeadlessBrowserCollector: wait_for selector %r timed out for %s: %s",
                wait_for,
                self.source_code,
                exc,
            )
        scroll_passes = int(sp.get("headless_scroll_passes", 0) or 0)
        scroll_pause = int(sp.get("headless_scroll_pause_ms", 1200) or 1200)
        for _ in range(max(0, scroll_passes)):
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            except Exception:
                break
            page.wait_for_timeout(max(100, scroll_pause))

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CollectorError(
                "Playwright is not installed. Run: pip install playwright && playwright install chromium"
            ) from exc

        headless = config.PLAYWRIGHT_HEADLESS
        timeout_ms = config.PLAYWRIGHT_TIMEOUT_MS
        url = self._e2e_cache_bust_url(url)
        sp = self._selector_profile()
        merge_raw = sp.get("headless_merge_urls") or []
        if isinstance(merge_raw, str):
            merge_list = [merge_raw]
        elif isinstance(merge_raw, list):
            merge_list = [u for u in merge_raw if isinstance(u, str) and u.strip()]
        else:
            merge_list = []

        urls: list[str] = []
        for u in [url] + merge_list:
            bust = self._e2e_cache_bust_url(u.strip())
            if bust not in urls:
                urls.append(bust)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                ctx_kwargs = self._playwright_context_kwargs()
                context = browser.new_context(**ctx_kwargs) if ctx_kwargs else browser.new_context()
                try:
                    page = context.new_page()
                    if len(urls) == 1:
                        self._prepare_page(page, urls[0])
                        html_out = page.content()
                    else:
                        fragments: list[str] = []
                        for idx, u in enumerate(urls):
                            self._prepare_page(page, u)
                            inner = page.evaluate(
                                "() => (document.body && document.body.innerHTML) || ''"
                            )
                            fragments.append(
                                f'<div data-oma-headless-merge="{idx}">{inner}</div>'
                            )
                        html_out = (
                            "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head><body>"
                            + "".join(fragments)
                            + "</body></html>"
                        )
                    self._last_http_status = 200
                    return html_out.encode("utf-8"), "html"
                finally:
                    context.close()
                    browser.close()
        except CollectorError:
            raise
        except Exception as exc:
            raise CollectorError(f"Headless browser fetch failed for {self.source_code}: {exc}") from exc

    def close(self) -> None:
        """No persistent httpx client required; Playwright closes per fetch."""
        super().close()
