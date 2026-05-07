"""WP004 — Mobile UI Parity: HTML structure assertions.

Validates:
- AC-01: viewport meta present and correct
- AC-02: dir="rtl" and lang="he" on wrapper/html; <bdi> used for currency
- AC-03: filter bar present with nav/role=tablist, aria-label on buttons, min-target >= 44px via CSS class
- AC-07: stale-banner class and dq-box structure present in body fragment

These tests operate purely on the static template files (no DB, no render pipeline).
They are always collected — DB-dependent tests are skipped via conftest pg_session fixture.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "organic_market_agent" / "publisher" / "templates"
STATIC = REPO_ROOT / "organic_market_agent" / "publisher" / "static"

PUBLIC_REPORT_HTML = TEMPLATES / "public_report.html"
PUBLIC_REPORT_BODY = TEMPLATES / "public_report_body.html"
SFAGENT_CSS = STATIC / "sfagent-base.css"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def full_html() -> str:
    return PUBLIC_REPORT_HTML.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def body_html() -> str:
    return PUBLIC_REPORT_BODY.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def base_css() -> str:
    return SFAGENT_CSS.read_text(encoding="utf-8")


# ── AC-01: Viewport meta ──────────────────────────────────────────────────────

class TestAC01Viewport:
    """AC-01: Viewport correctness — meta tag must be present and correct."""

    def test_full_html_has_viewport_meta(self, full_html: str) -> None:
        """public_report.html must have <meta name="viewport" ...>."""
        assert 'name="viewport"' in full_html, (
            "Missing <meta name='viewport'> in public_report.html"
        )

    def test_full_html_viewport_has_width_device_width(self, full_html: str) -> None:
        """Viewport must set width=device-width."""
        assert "width=device-width" in full_html, (
            "Viewport meta missing width=device-width in public_report.html"
        )

    def test_full_html_viewport_has_initial_scale(self, full_html: str) -> None:
        """Viewport must set initial-scale=1."""
        assert "initial-scale=1" in full_html, (
            "Viewport meta missing initial-scale=1 in public_report.html"
        )

    def test_full_html_viewport_fit_cover(self, full_html: str) -> None:
        """WP004: viewport-fit=cover for safe-area insets (notched phones)."""
        assert "viewport-fit=cover" in full_html, (
            "Viewport meta missing viewport-fit=cover in public_report.html"
        )

    def test_body_fragment_has_no_viewport_meta(self, body_html: str) -> None:
        """Body fragment must NOT contain <meta name='viewport'> — it's a WP embed."""
        assert 'name="viewport"' not in body_html, (
            "public_report_body.html must not contain a viewport meta tag "
            "(it is a WordPress shortcode fragment, not a standalone page)"
        )

    def test_css_has_mobile_breakpoint_375(self, base_css: str) -> None:
        """CSS must have a media query targeting narrow viewports (≤414px covers 375)."""
        assert "max-width: 414px" in base_css or "max-width:414px" in base_css, (
            "sfagent-base.css missing 375/414px mobile breakpoint"
        )

    def test_css_has_tablet_breakpoint_768(self, base_css: str) -> None:
        """CSS must have a media query targeting tablet (641–900px covers 768)."""
        assert "641px" in base_css or "768px" in base_css, (
            "sfagent-base.css missing tablet breakpoint for 768px"
        )

    def test_css_no_100vw_on_container(self, base_css: str) -> None:
        """Containers must not use max-width: 100vw (RTL overflow trap, LOD400 §5)."""
        # Allow 100vw in comments or calc() but not as direct container rule
        lines_with_vw = [
            ln for ln in base_css.splitlines()
            if "100vw" in ln and not ln.strip().startswith("/*") and "calc(" not in ln
        ]
        assert len(lines_with_vw) == 0, (
            f"Found max-width: 100vw usage (RTL overflow trap): {lines_with_vw}"
        )


# ── AC-02: RTL Hebrew ─────────────────────────────────────────────────────────

class TestAC02RTLHebrew:
    """AC-02: RTL Hebrew preserved — dir, lang, bdi."""

    def test_full_html_has_dir_rtl(self, full_html: str) -> None:
        """public_report.html <html> must have dir='rtl'."""
        assert 'dir="rtl"' in full_html, (
            "Missing dir='rtl' in public_report.html"
        )

    def test_full_html_has_lang_he(self, full_html: str) -> None:
        """public_report.html <html> must have lang='he'."""
        assert 'lang="he"' in full_html, (
            "Missing lang='he' in public_report.html"
        )

    def test_body_fragment_wrapper_has_dir_rtl(self, body_html: str) -> None:
        """Body fragment wrapper div must have dir='rtl'."""
        assert 'dir="rtl"' in body_html, (
            "Missing dir='rtl' on wrapper in public_report_body.html"
        )

    def test_body_fragment_wrapper_has_lang_he(self, body_html: str) -> None:
        """Body fragment wrapper div must have lang='he'."""
        assert 'lang="he"' in body_html, (
            "Missing lang='he' on wrapper in public_report_body.html"
        )

    def test_body_fragment_uses_bdi_for_currency(self, body_html: str) -> None:
        """Currency values must use <bdi> for LTR isolation in RTL flow (AC-02)."""
        assert "<bdi>" in body_html, (
            "No <bdi> elements found in public_report_body.html — "
            "price values must be wrapped in <bdi> for RTL/LTR isolation"
        )

    def test_body_fragment_bdi_used_with_price_main(self, body_html: str) -> None:
        """price-main spans should contain <bdi> for currency isolation."""
        # Check that price-main is paired with bdi (may be inside or outside)
        assert re.search(r'price-main[^>]*>.*?<bdi>|<bdi>.*?price-main', body_html, re.DOTALL), (
            "price-main values should use <bdi> for currency LTR isolation"
        )

    def test_css_bdi_rule_present(self, base_css: str) -> None:
        """CSS must have .sfagent bdi rule for unicode-bidi isolation."""
        assert ".sfagent bdi" in base_css, (
            "sfagent-base.css missing .sfagent bdi unicode-bidi rule"
        )

    def test_css_hebrew_text_no_forced_ellipsis(self, base_css: str) -> None:
        """Hebrew column labels must not use text-overflow: ellipsis (LOD400 §5)."""
        # Check that product-name and card row dt don't have text-overflow: ellipsis
        # We look for the rule in the WP004 section specifically
        wp004_section = base_css[base_css.find("WP004"):]
        # The spec says prefer wrap — ellipsis should not appear in WP004 product-name rules
        product_name_block = re.search(
            r'\.product-name.*?(?=\n\n|\Z)', wp004_section, re.DOTALL
        )
        if product_name_block:
            assert "text-overflow: ellipsis" not in product_name_block.group(), (
                "product-name should not use text-overflow: ellipsis on RTL text (LOD400 §5)"
            )


# ── AC-03: Filter bar ─────────────────────────────────────────────────────────

class TestAC03FilterBar:
    """AC-03: Source-type filter bar — wrap-friendly, 44px targets, accessible."""

    def test_body_fragment_has_filter_nav(self, body_html: str) -> None:
        """Filter bar must use <nav> element (LOD400 §7 unit test spec)."""
        assert "<nav" in body_html, (
            "Missing <nav> element for filter bar in public_report_body.html"
        )

    def test_body_fragment_filter_has_role_tablist(self, body_html: str) -> None:
        """Filter nav must have role='tablist' (LOD400 §7)."""
        assert 'role="tablist"' in body_html, (
            "Filter bar missing role='tablist' in public_report_body.html"
        )

    def test_body_fragment_filter_has_aria_label_on_nav(self, body_html: str) -> None:
        """Filter nav must have aria-label for screen readers."""
        # The nav element itself must have an aria-label
        nav_match = re.search(r'<nav[^>]*>', body_html)
        assert nav_match is not None, "No <nav> found"
        nav_tag = nav_match.group()
        assert "aria-label" in nav_tag, (
            f"Filter <nav> missing aria-label: {nav_tag}"
        )

    def test_body_fragment_filter_buttons_have_aria_label(self, body_html: str) -> None:
        """Each filter button must have aria-label (AC-03 accessible names)."""
        filter_buttons = re.findall(r'<button[^>]*class="sfa-filter-btn[^"]*"[^>]*>', body_html)
        assert len(filter_buttons) >= 4, (
            f"Expected at least 4 filter buttons, found {len(filter_buttons)}"
        )
        for btn in filter_buttons:
            assert "aria-label" in btn, (
                f"Filter button missing aria-label: {btn}"
            )

    def test_body_fragment_filter_buttons_have_role_tab(self, body_html: str) -> None:
        """Filter buttons must have role='tab' (matches tablist parent)."""
        filter_buttons = re.findall(r'<button[^>]*class="sfa-filter-btn[^"]*"[^>]*>', body_html)
        for btn in filter_buttons:
            assert 'role="tab"' in btn, (
                f"Filter button missing role='tab': {btn}"
            )

    def test_body_fragment_filter_has_all_four_options(self, body_html: str) -> None:
        """Filter bar must have all four source-type options: הכל, מגדלים, חנויות, רשתות."""
        for label in ("הכל", "מגדלים", "חנויות", "רשתות"):
            assert label in body_html, (
                f"Filter bar missing option: {label}"
            )

    def test_body_fragment_filter_default_active(self, body_html: str) -> None:
        """Default filter (הכל) must have aria-selected='true' and is-active class."""
        assert 'aria-selected="true"' in body_html, (
            "No filter button has aria-selected='true' (default active state missing)"
        )
        assert "is-active" in body_html, (
            "No filter button has is-active class (visible active state missing)"
        )

    def test_css_filter_btn_min_height_44(self, base_css: str) -> None:
        """sfa-filter-btn must have min-height: 44px (WCAG 2.5.5 / iOS HIG)."""
        assert "min-height: 44px" in base_css, (
            "sfagent-base.css missing min-height: 44px for sfa-filter-btn (AC-03)"
        )

    def test_css_filter_btn_min_width_44(self, base_css: str) -> None:
        """sfa-filter-btn must have min-width: 44px."""
        assert "min-width: 44px" in base_css, (
            "sfagent-base.css missing min-width: 44px for sfa-filter-btn (AC-03)"
        )

    def test_css_filter_bar_flex_wrap(self, base_css: str) -> None:
        """sfa-filter-bar must use flex-wrap: wrap for narrow screens."""
        assert "flex-wrap: wrap" in base_css, (
            "sfagent-base.css missing flex-wrap: wrap on sfa-filter-bar"
        )

    def test_css_filter_btn_active_state_without_hover(self, base_css: str) -> None:
        """Active state must use background + font-weight (visible without hover)."""
        # Check is-active rule exists with background
        is_active_idx = base_css.find(".is-active")
        assert is_active_idx != -1, "Missing .is-active rule in CSS"
        is_active_block = base_css[is_active_idx:is_active_idx + 200]
        assert "background" in is_active_block, (
            ".is-active rule must set background color for active state"
        )
        assert "font-weight" in is_active_block, (
            ".is-active rule must set font-weight for active state"
        )


# ── AC-04: Data table readable ────────────────────────────────────────────────

class TestAC04DataTable:
    """AC-04: Data table readable — mobile cards, product name visible."""

    def test_body_fragment_has_mobile_cards(self, body_html: str) -> None:
        """Mobile card layout must be present in body fragment."""
        assert "sfa-report-mobile-cards" in body_html, (
            "Missing sfa-report-mobile-cards in public_report_body.html"
        )

    def test_body_fragment_has_product_card(self, body_html: str) -> None:
        """sfa-product-card must be present for mobile stacked layout."""
        assert "sfa-product-card" in body_html, (
            "Missing sfa-product-card in public_report_body.html"
        )

    def test_body_fragment_product_card_has_head(self, body_html: str) -> None:
        """Product card head (name + unit) must be present."""
        assert "sfa-product-card__head" in body_html, (
            "Missing sfa-product-card__head in public_report_body.html"
        )

    def test_body_fragment_product_card_has_stats(self, body_html: str) -> None:
        """Product card stats (dl with metrics) must be present."""
        assert "sfa-product-card__stats" in body_html, (
            "Missing sfa-product-card__stats in public_report_body.html"
        )

    def test_css_mobile_cards_display_none_desktop(self, base_css: str) -> None:
        """Mobile cards must be display:none on desktop (sfa-report-mobile-cards)."""
        # Outside media query, sfa-report-mobile-cards: display: none
        outside_mq = base_css[:base_css.find("@media")]
        assert "sfa-report-mobile-cards" in outside_mq and "display: none" in outside_mq, (
            "sfa-report-mobile-cards must have display:none outside media query (desktop)"
        )

    def test_css_font_size_min_14px(self, base_css: str) -> None:
        """Mobile font must be at minimum 14px per AC-01 requirement."""
        # clamp(14px, ...) or clamp(0.875rem, ...) should appear in mobile section
        assert "14px" in base_css or "0.875rem" in base_css, (
            "CSS missing explicit 14px minimum font size for mobile (AC-01)"
        )


# ── AC-07: Stale banner + DQ block ───────────────────────────────────────────

class TestAC07StaleBannerDQ:
    """AC-07: Stale banner and data-quality block visible on mobile."""

    def test_body_fragment_has_stale_banner_class(self, body_html: str) -> None:
        """Body fragment must have sfa-stale-banner class (conditional on stale_banner)."""
        assert "sfa-stale-banner" in body_html, (
            "Missing sfa-stale-banner in public_report_body.html"
        )

    def test_body_fragment_stale_banner_conditional(self, body_html: str) -> None:
        """Stale banner must be conditional on stale_banner template variable."""
        assert "{% if stale_banner %}" in body_html, (
            "Stale banner must be wrapped in {% if stale_banner %} conditional"
        )

    def test_body_fragment_has_dq_box(self, body_html: str) -> None:
        """Data-quality transparency block must be present (id=sfagent-dq-box)."""
        assert "sfagent-dq-box" in body_html, (
            "Missing sfagent-dq-box (data-quality block) in public_report_body.html"
        )

    def test_body_fragment_dq_conditional(self, body_html: str) -> None:
        """DQ block must be conditional on data_quality variable."""
        assert "{% if data_quality %}" in body_html, (
            "DQ block must be wrapped in {% if data_quality %} conditional"
        )

    def test_css_stale_banner_has_border(self, base_css: str) -> None:
        """Stale banner must have a colored border for visibility (AC-07)."""
        stale_idx = base_css.find(".sfa-stale-banner")
        assert stale_idx != -1, "Missing .sfa-stale-banner rule in CSS"
        stale_block = base_css[stale_idx:stale_idx + 300]
        assert "border" in stale_block, (
            ".sfa-stale-banner must have a border for visual prominence"
        )

    def test_full_html_has_stale_banner_conditional(self, full_html: str) -> None:
        """Full-page template must also have conditional stale banner."""
        assert "stale_banner" in full_html, (
            "Stale banner variable missing from public_report.html"
        )

    def test_css_stale_banner_no_overflow_hidden(self, base_css: str) -> None:
        """Stale banner must not be clipped by overflow:hidden on mobile."""
        stale_idx = base_css.find(".sfa-stale-banner")
        if stale_idx != -1:
            stale_block = base_css[stale_idx:stale_idx + 400]
            assert "overflow: hidden" not in stale_block, (
                ".sfa-stale-banner must not have overflow:hidden (blocks visibility)"
            )


# ── AC-05 / AC-06: Lighthouse + Cross-device (builder artefacts) ─────────────

class TestAC05AC06BuilderArtefacts:
    """AC-05/AC-06: Builder-side checks for Lighthouse + cross-device prerequisites."""

    def test_full_html_has_theme_color_meta(self, full_html: str) -> None:
        """theme-color meta tag improves mobile browser chrome (Lighthouse SEO)."""
        assert 'name="theme-color"' in full_html, (
            "Missing <meta name='theme-color'> in public_report.html (helps Lighthouse SEO)"
        )

    def test_no_external_cdn_in_css(self, base_css: str) -> None:
        """sfagent-base.css must not load from external CDN (Iron Rule §6.8)."""
        assert "@import url('https://fonts.googleapis" not in base_css, (
            "sfagent-base.css must not use Google Fonts CDN import (no external CDN rule)"
        )

    def test_no_external_cdn_in_full_html(self, full_html: str) -> None:
        """public_report.html must not link to Google Fonts CDN (Iron Rule §6.8)."""
        assert "fonts.googleapis.com" not in full_html, (
            "public_report.html must not reference Google Fonts CDN"
        )

    def test_full_html_system_ui_font_stack(self, full_html: str) -> None:
        """Font stack in public_report.html must include system-ui fallback."""
        assert "system-ui" in full_html, (
            "public_report.html missing system-ui fallback font (no external CDN rule)"
        )

    def test_css_system_ui_font_stack(self, base_css: str) -> None:
        """sfagent-base.css must include system-ui in font-family stack."""
        assert "system-ui" in base_css, (
            "sfagent-base.css missing system-ui fallback (no external CDN rule)"
        )

    def test_css_has_safe_area_insets(self, base_css: str) -> None:
        """CSS must use env(safe-area-inset-*) for notched phone support."""
        assert "safe-area-inset" in base_css, (
            "sfagent-base.css missing env(safe-area-inset-*) rules for notched phones"
        )

    def test_full_html_has_safe_area_insets(self, full_html: str) -> None:
        """public_report.html inline CSS must include safe-area-inset rules."""
        assert "safe-area-inset" in full_html, (
            "public_report.html missing env(safe-area-inset-*) for notched phones"
        )
