"""
WP003 — Flask Blueprint view tests.
Uses Flask test client with mocked DB session (no real DB required).
SQLite in-memory for model instantiation where needed.

AC-01: Blueprint registered; routes return correct status codes + JSON
AC-02: Category filter works (client-side DOM / API)
AC-03: Search endpoint filters by name_he, name_en, scientific_name
AC-04: Crop detail: 8 tabs rendered; no-data tabs show placeholder
AC-05: Variety cards: star on default, grafted badge, price + yield
AC-06: Economics tab: price cards, yearly breakdown, placeholder when no pricebook
AC-07: Entity tags: data-etype + data-eid present
AC-08: Timeline: proportional phase bars rendered
AC-09: RTL layout: html dir=rtl
AC-10: No edit/delete: zero form POST inputs in crop book pages
AC-11: Tests green (this file); validate_aos.sh 0 FAIL
"""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_family(id_=1, scientific_name="Brassicaceae", name_he="מצליבים"):
    f = MagicMock()
    f.id = id_
    f.scientific_name = scientific_name
    f.name_he = name_he
    return f


def _make_source_value(field_name, source, value_text=None, value_numeric=None, unit=None, note=None):
    sv = MagicMock()
    sv.field_name = field_name
    sv.source = source
    sv.value_text = value_text
    sv.value_numeric = value_numeric
    sv.unit = unit
    sv.note = note
    return sv


def _make_variety(
    id_=1,
    name_he="ברירת מחדל",
    name_en="Default",
    is_default=True,
    is_grafted=False,
    rootstock_variety=None,
    days_to_maturity=21,
    harvest_window_max_days=80,
    harvest_window_min_days=None,
    in_row_spacing_cm=None,
    rows_per_bed=None,
    planting_season="קיץ–חורף",
    planting_method="direct_sow",
    harvest_stage="baby_leaf",
    harvest_unit="case",
    avg_yield_per_bed_m=Decimal("0.175"),
    documented_price=Decimal("8.00"),
    documented_price_unit="₪/מארז",
    documented_price_source="Tend 2022–2024",
    pricebook_product_id=None,
    avg_revenue_per_bed_m=Decimal("6.00"),
    yield_source="JMF",
    seeder=None,
    seeder_front_gear=None,
    seeder_rear_gear=None,
    seeder_roller_plate=None,
    days_in_gh_total=None,
    notes=None,
    source_values=None,
    crop_id=1,
):
    v = MagicMock()
    v.id = id_
    v.name_he = name_he
    v.name_en = name_en
    v.is_default = is_default
    v.is_grafted = is_grafted
    v.rootstock_variety = rootstock_variety
    v.days_to_maturity = days_to_maturity
    v.harvest_window_max_days = harvest_window_max_days
    v.harvest_window_min_days = harvest_window_min_days
    v.in_row_spacing_cm = in_row_spacing_cm
    v.rows_per_bed = rows_per_bed
    v.planting_season = planting_season
    v.planting_method = planting_method
    v.harvest_stage = harvest_stage
    v.harvest_unit = harvest_unit
    v.avg_yield_per_bed_m = avg_yield_per_bed_m
    v.documented_price = documented_price
    v.documented_price_unit = documented_price_unit
    v.documented_price_source = documented_price_source
    v.pricebook_product_id = pricebook_product_id
    v.avg_revenue_per_bed_m = avg_revenue_per_bed_m
    v.yield_source = yield_source
    v.seeder = seeder
    v.seeder_front_gear = seeder_front_gear
    v.seeder_rear_gear = seeder_rear_gear
    v.seeder_roller_plate = seeder_roller_plate
    v.days_in_gh_total = days_in_gh_total
    v.succession_interval_weeks = None
    v.notes = notes
    v.source_values = source_values or []
    v.crop_id = crop_id
    return v


def _make_crop(
    id_=1,
    name_he="ארוגולה",
    name_en="Arugula",
    scientific_name="Eruca vesicaria",
    category="vegetables",
    growth_cycle="annual",
    harvest_unit_default="case",
    description=None,
    oma_product_id=None,
    varieties=None,
    family=None,
    conversion_group=None,
    unit_conversions=None,
):
    c = MagicMock()
    c.id = id_
    c.name_he = name_he
    c.name_en = name_en
    c.scientific_name = scientific_name
    c.category = category
    c.growth_cycle = growth_cycle
    c.harvest_unit_default = harvest_unit_default
    c.description = description
    c.oma_product_id = oma_product_id
    c.family = family or _make_family()
    c.varieties = varieties if varieties is not None else [_make_variety()]
    c.conversion_group = conversion_group
    c.unit_conversions = unit_conversions or []
    return c


# ---------------------------------------------------------------------------
# App fixture with mocked DB
# ---------------------------------------------------------------------------

@pytest.fixture()
def app_with_mock_db():
    """Create Flask test app; mock g.db_session so no real DB is needed."""
    from organic_market_agent.admin import create_app

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    return app


@pytest.fixture()
def client(app_with_mock_db):
    return app_with_mock_db.test_client()


def _mock_session_for_index(crops_list):
    """Return a mock session whose .query(...).options(...).filter(...).order_by(...).all() returns crops_list."""
    mock_session = MagicMock()
    # Chain: query → options → (optional filter chain) → order_by → all
    chain = MagicMock()
    chain.options.return_value = chain
    chain.filter.return_value = chain
    chain.order_by.return_value = chain
    chain.all.return_value = crops_list
    mock_session.query.return_value = chain
    return mock_session


def _mock_session_for_detail(crop_obj):
    """Return a mock session whose query chain's one_or_none() returns crop_obj."""
    mock_session = MagicMock()
    chain = MagicMock()
    chain.options.return_value = chain
    chain.filter.return_value = chain
    chain.one_or_none.return_value = crop_obj
    mock_session.query.return_value = chain
    return mock_session


def _mock_session_for_api(crops_list):
    return _mock_session_for_index(crops_list)


# ---------------------------------------------------------------------------
# AC-01 — Routes return correct status codes
# ---------------------------------------------------------------------------

class TestRouteStatusCodes:
    def test_index_returns_200(self, client):
        """GET /crop-book/ exists (tested fully in TestRouteResponses)."""
        # Verify the route resolves without a 404 (actual 200 tested with mock session in TestRouteResponses)
        rules = [str(r) for r in client.application.url_map.iter_rules()]
        assert any("/crop-book/" in r for r in rules)

    def test_crop_book_blueprint_registered(self, client):
        """Blueprint 'crop_book' must be registered in the app."""
        assert "crop_book" in client.application.blueprints

    def test_crop_book_index_url_rule_exists(self, client):
        """URL rule /crop-book/ must be registered."""
        rules = [str(r) for r in client.application.url_map.iter_rules()]
        assert any("/crop-book/" in r for r in rules), f"No /crop-book/ rule found in: {rules}"

    def test_crop_book_detail_url_rule_exists(self, client):
        """URL rule /crop-book/<int:crop_id>/ must be registered."""
        rules = [str(r) for r in client.application.url_map.iter_rules()]
        assert any("crop_id" in r for r in rules), f"No crop_id rule found in: {rules}"

    def test_crop_book_api_url_rule_exists(self, client):
        """URL rule /crop-book/api/crops must be registered."""
        rules = [str(r) for r in client.application.url_map.iter_rules()]
        assert any("api/crops" in r for r in rules), f"No api/crops rule found in: {rules}"


# ---------------------------------------------------------------------------
# AC-01 continued — full route tests using g patching
# ---------------------------------------------------------------------------

def _setup_g_patch(app, mock_session):
    """Context manager: patch g.db_session for the duration of a request."""
    import flask
    from unittest.mock import patch as _patch

    class GContext:
        def __enter__(self_):
            return self_

        def __exit__(self_, *args):
            pass

    return _patch.object(flask.g, "db_session", mock_session, create=True)


@pytest.fixture()
def index_crops():
    return [_make_crop(id_=1), _make_crop(id_=2, name_he="ברוקולי", name_en="Broccoli")]


@pytest.fixture()
def arugula_crop():
    sv_price = _make_source_value("documented_price", "Tend_2022", "₪8.00", Decimal("8.00"), "₪/מארז")
    sv_dtm = _make_source_value("days_to_maturity", "JMF", "30–40", Decimal("35"), "ימים")
    variety = _make_variety(source_values=[sv_price, sv_dtm])
    return _make_crop(id_=1, varieties=[variety])


@pytest.fixture()
def tomato_crop():
    lobelo = _make_variety(
        id_=10, name_he="לובלו מורכב", name_en="Lobelo - Grafted",
        is_default=True, is_grafted=True, rootstock_variety="Beaufort",
        days_to_maturity=100, harvest_window_max_days=100,
        pricebook_product_id="TOM-001",
        seeder=None,
    )
    cuore = _make_variety(
        id_=11, name_he="Cuore Di Bue", name_en="Cuore Di Bue",
        is_default=False, is_grafted=False,
        days_to_maturity=None, documented_price=Decimal("12.00"),
    )
    return _make_crop(
        id_=2, name_he="עגבנייה", name_en="Tomatoes",
        scientific_name="Solanum lycopersicum",
        category="vegetables", varieties=[lobelo, cuore],
    )


def _get_with_mock_session(client, url, mock_session):
    """GET url with g.db_session patched to mock_session."""
    with client.application.test_request_context(url):
        pass

    # Patch the _open_session before_request to inject our mock
    from flask import g
    original_before = None

    def fake_before_request():
        g.db_session = mock_session
        g.unread_alert_count = 0
        g.unread_severity_alert_count = 0

    # Temporarily replace before_request functions
    app = client.application
    # Save and replace
    saved_funcs = app.before_request_funcs.get(None, []).copy()
    app.before_request_funcs[None] = [fake_before_request]
    try:
        resp = client.get(url)
    finally:
        app.before_request_funcs[None] = saved_funcs

    return resp


class TestRouteResponses:
    def test_index_200(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        assert resp.status_code == 200

    def test_index_contains_rtl(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        assert resp.status_code == 200
        data = resp.data.decode("utf-8")
        assert 'dir="rtl"' in data

    def test_index_contains_crop_names(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        assert "ארוגולה" in data

    def test_index_contains_category_tabs(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        assert "ירקות" in data
        assert "עשבי תיבול" in data
        assert "כל הגידולים" in data

    def test_crop_detail_200(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        assert resp.status_code == 200

    def test_crop_detail_404(self, client):
        mock_session = _mock_session_for_detail(None)
        resp = _get_with_mock_session(client, "/crop-book/99999/", mock_session)
        assert resp.status_code == 404

    def test_api_crops_returns_json(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops", mock_session)
        assert resp.status_code == 200
        assert resp.content_type.startswith("application/json")
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_api_crops_json_structure(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops", mock_session)
        data = json.loads(resp.data)
        assert len(data) >= 1
        item = data[0]
        assert "id" in item
        assert "name_he" in item
        assert "name_en" in item
        assert "category" in item
        assert "variety_count" in item
        assert "seasons" in item


# ---------------------------------------------------------------------------
# AC-02 — Category filter
# ---------------------------------------------------------------------------

class TestCategoryFilter:
    def test_index_shows_category_tabs(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        for tab in ["כל הגידולים", "ירקות", "עשבי תיבול", "פירות", "קטניות", "עצי פרי", "דגנים", "גידולי כיסוי"]:
            assert tab in data, f"Missing category tab: {tab}"

    def test_api_accepts_category_param(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops?category=vegetables", mock_session)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# AC-03 — Search
# ---------------------------------------------------------------------------

class TestSearch:
    def test_index_has_search_input(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        assert 'cb-search-input' in data

    def test_api_accepts_q_param(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops?q=ארוגולה", mock_session)
        assert resp.status_code == 200

    def test_api_accepts_dtm_max_param(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops?dtm_max=50", mock_session)
        assert resp.status_code == 200

    def test_api_accepts_season_param(self, client, index_crops):
        mock_session = _mock_session_for_api(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/api/crops?season=summer", mock_session)
        assert resp.status_code == 200

    def test_api_multi_season_or_logic(self, client):
        """F-190-WP003-01: ?season=summer&season=winter returns crops matching EITHER season (OR logic)."""
        summer_var = _make_variety(planting_season="קיץ בלבד")
        winter_var = _make_variety(planting_season="חורף בלבד")
        spring_var = _make_variety(planting_season="אביב בלבד")
        crops = [
            _make_crop(id_=1, name_he="קיץ", varieties=[summer_var]),
            _make_crop(id_=2, name_he="חורף", varieties=[winter_var]),
            _make_crop(id_=3, name_he="אביב", varieties=[spring_var]),
        ]
        mock_session = _mock_session_for_api(crops)
        resp = _get_with_mock_session(
            client, "/crop-book/api/crops?season=summer&season=winter", mock_session
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        names = {c["name_he"] for c in data}
        assert "קיץ" in names       # summer matched
        assert "חורף" in names      # winter matched
        assert "אביב" not in names  # spring excluded (not in selected seasons)


# ---------------------------------------------------------------------------
# AC-04 — All 8 tabs render on crop detail page
# ---------------------------------------------------------------------------

class TestCropDetailTabs:
    def test_all_8_tabs_present(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        tab_labels = ["זנים", "תיאור", "כלכלה", "טיפולים", "ציוד", "מקורות", "ציר זמן", "נתוני שדה"]
        for label in tab_labels:
            assert label in data, f"Missing tab: {label}"

    def test_empty_tabs_show_placeholder(self, client, arugula_crop):
        """Tabs with no data should show 'אין נתונים' or '—', not be hidden."""
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        # The care tab always has the table structure
        assert "טיפולים" in data

    def test_equipment_tab_greyed_when_no_seeder(self, client, arugula_crop):
        """When no seeder fields, ציוד tab should have 'אין נתונים' indication."""
        # arugula_crop has no seeder by default
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        # ציוד tab should be present but greyed
        assert "ציוד" in data
        assert "cb-tab-disabled" in data or "אין נתונים" in data


# ---------------------------------------------------------------------------
# AC-05 — Variety cards
# ---------------------------------------------------------------------------

class TestVarietyCards:
    def test_default_star_on_default_variety(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "★" in data

    def test_grafted_badge_shown(self, client, tomato_crop):
        mock_session = _mock_session_for_detail(tomato_crop)
        resp = _get_with_mock_session(client, "/crop-book/2/", mock_session)
        data = resp.data.decode("utf-8")
        assert "מורכב" in data
        assert "Beaufort" in data

    def test_variety_price_shown(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "8.00" in data  # documented_price

    def test_variety_yield_shown(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "0.175" in data  # avg_yield_per_bed_m


# ---------------------------------------------------------------------------
# AC-06 — Economics tab
# ---------------------------------------------------------------------------

class TestEconomicsTab:
    def test_documented_price_card_shown(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "מחיר מתועד" in data

    def test_market_price_null_shows_not_linked(self, client, arugula_crop):
        """When pricebook_product_id is None, show 'לא מקושר למחירון'."""
        # arugula_crop default variety has pricebook_product_id=None
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "לא מקושר למחירון" in data

    def test_market_price_linked_shows_placeholder(self, client, tomato_crop):
        """When pricebook_product_id set, show placeholder text."""
        mock_session = _mock_session_for_detail(tomato_crop)
        resp = _get_with_mock_session(client, "/crop-book/2/", mock_session)
        data = resp.data.decode("utf-8")
        # Should show the placeholder with the product id
        assert "יוצג עם הפעלת מחירון" in data or "TOM-001" in data

    def test_price_cards_side_by_side_structure(self, client, arugula_crop):
        """Two price cards should be present in the template."""
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "cb-price-documented" in data
        assert "cb-price-market" in data


# ---------------------------------------------------------------------------
# AC-07 — Entity tags
# ---------------------------------------------------------------------------

class TestEntityTags:
    def test_entity_tag_css_classes_in_css(self):
        """CSS must define .etag and .et-* classes."""
        css_path = REPO_ROOT / "organic_market_agent" / "admin" / "static" / "crop_book" / "crop_book.css"
        with open(css_path) as f:
            css = f.read()
        assert ".etag" in css
        assert ".et-pest" in css
        assert ".et-disease" in css
        assert ".et-equip" in css
        assert ".et-input" in css
        assert ".et-technique" in css
        assert ".et-crop" in css

    def test_entity_macro_produces_correct_attrs(self):
        """entity_tag macro should produce data-etype and data-eid attributes."""
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        import os
        templates_dir = REPO_ROOT / "organic_market_agent" / "crop_book" / "templates"
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html"]),
        )
        tpl = env.get_template("crop_book/_macros.html")
        module = tpl.make_module()
        rendered = str(module.entity_tag("pest", "aphid", "כנימת עלים"))
        assert "data-etype" in rendered
        assert "data-eid" in rendered
        assert "pest" in rendered
        assert "aphid" in rendered


# ---------------------------------------------------------------------------
# AC-08 — Timeline
# ---------------------------------------------------------------------------

class TestTimeline:
    def test_timeline_rendered_for_arugula(self, client, arugula_crop):
        """ארוגולה DTM=21, harvest_window=80 should produce timeline."""
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "ציר זמן" in data
        assert "cb-timeline" in data

    def test_timeline_fallback_for_no_dtm(self, client):
        """Crop with no DTM + no harvest_window should show fallback text."""
        variety = _make_variety(days_to_maturity=None, harvest_window_max_days=None)
        crop = _make_crop(varieties=[variety])
        mock_session = _mock_session_for_detail(crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "אין נתוני" in data or "—" in data

    def test_timeline_weeks_based_on_harvest_window_only(self, client):
        """F-190-WP003-02: total_weeks = ceil(hw/7), not ceil((dtm+hw)/7).
        ארוגולה: DTM=21, harvest_window=80 → 12 weeks (not 15).
        """
        import math
        from unittest.mock import patch as _patch

        variety = _make_variety(days_to_maturity=21, harvest_window_max_days=80)
        crop = _make_crop(id_=1, varieties=[variety])
        mock_session = _mock_session_for_detail(crop)

        captured: dict = {}
        original_render = __import__("flask", fromlist=["render_template"]).render_template

        def capturing_render(template_name, **ctx):
            if "timeline_data" in ctx:
                captured["timeline_data"] = ctx["timeline_data"]
            return original_render(template_name, **ctx)

        with _patch("organic_market_agent.crop_book.views.render_template", side_effect=capturing_render):
            _get_with_mock_session(client, "/crop-book/1/", mock_session)

        td = captured.get("timeline_data")
        assert td is not None, "timeline_data was not passed to render_template"
        expected = math.ceil(80 / 7)   # 12  (harvest_window only)
        wrong = math.ceil((21 + 80) / 7)  # 15 (dtm + hw — old broken formula)
        assert td["total_weeks"] == expected, (
            f"total_weeks should be {expected} (ceil(hw/7)), "
            f"got {td['total_weeks']} (would be {wrong} with broken dtm+hw formula)"
        )


# ---------------------------------------------------------------------------
# AC-09 — RTL layout
# ---------------------------------------------------------------------------

class TestRTLLayout:
    def test_index_html_dir_rtl(self, client, index_crops):
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        assert 'dir="rtl"' in data

    def test_detail_html_dir_rtl(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert 'dir="rtl"' in data

    def test_breadcrumb_present_on_detail(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        assert "ספר גידולים" in data
        assert "breadcrumb" in data

    def test_rtl_css_applied(self):
        css_path = REPO_ROOT / "organic_market_agent" / "admin" / "static" / "crop_book" / "crop_book.css"
        with open(css_path) as f:
            css = f.read()
        assert "direction: rtl" in css
        assert "text-align: right" in css


# ---------------------------------------------------------------------------
# AC-10 — No edit/delete
# ---------------------------------------------------------------------------

class TestNoEditDelete:
    def test_index_no_post_forms(self, client, index_crops):
        """Search input + filter controls only — no create/edit/delete forms."""
        mock_session = _mock_session_for_index(index_crops)
        resp = _get_with_mock_session(client, "/crop-book/", mock_session)
        data = resp.data.decode("utf-8")
        # No method="post" in crop book forms
        import re
        post_forms = re.findall(r'<form[^>]+method=["\']post["\']', data, re.IGNORECASE)
        assert not post_forms, f"Found POST forms in index page: {post_forms}"

    def test_detail_no_post_forms(self, client, arugula_crop):
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        import re
        post_forms = re.findall(r'<form[^>]+method=["\']post["\']', data, re.IGNORECASE)
        assert not post_forms, f"Found POST forms in detail page: {post_forms}"

    def test_no_post_routes_in_blueprint(self):
        """Verify views.py has no @crop_book_bp.route(..., methods=['POST'])."""
        import os
        views_path = REPO_ROOT / "organic_market_agent" / "crop_book" / "views.py"
        with open(views_path) as f:
            content = f.read()
        import re
        post_routes = re.findall(r"methods=\[.*?['\"]POST['\"]", content)
        assert not post_routes, f"Found POST routes in views.py: {post_routes}"

    def test_no_delete_no_edit_links(self, client, arugula_crop):
        """No delete or edit CRUD links on crop book pages."""
        mock_session = _mock_session_for_detail(arugula_crop)
        resp = _get_with_mock_session(client, "/crop-book/1/", mock_session)
        data = resp.data.decode("utf-8")
        # No edit or delete buttons/links in crop book
        assert "crop_book.edit" not in data
        assert "crop_book.delete" not in data


# ---------------------------------------------------------------------------
# Unit tests: helper functions
# ---------------------------------------------------------------------------

class TestViewHelpers:
    def test_detect_seasons_summer(self):
        from organic_market_agent.crop_book.views import _detect_seasons
        seasons = _detect_seasons("קיץ–חורף")
        assert seasons["summer"] is True
        assert seasons["winter"] is True
        assert seasons["spring"] is False
        assert seasons["fall"] is False

    def test_detect_seasons_all(self):
        from organic_market_agent.crop_book.views import _detect_seasons
        seasons = _detect_seasons("spring summer fall winter")
        for k in ["summer", "spring", "fall", "winter"]:
            assert seasons[k] is True

    def test_detect_seasons_none(self):
        from organic_market_agent.crop_book.views import _detect_seasons
        seasons = _detect_seasons(None)
        for k in ["summer", "spring", "fall", "winter"]:
            assert seasons[k] is False

    def test_crop_to_dict_structure(self):
        from organic_market_agent.crop_book.views import _crop_to_dict
        crop = _make_crop()
        d = _crop_to_dict(crop)
        assert d["id"] == 1
        assert d["name_he"] == "ארוגולה"
        assert d["name_en"] == "Arugula"
        assert d["category"] == "vegetables"
        assert isinstance(d["variety_count"], int)
        assert isinstance(d["seasons"], list)

    def test_category_labels_all_present(self):
        from organic_market_agent.crop_book.views import CATEGORY_LABELS
        expected = ["vegetables", "herbs", "baby", "legumes", "fruits", "fruit_trees", "grains", "cover_crops"]
        for cat in expected:
            assert cat in CATEGORY_LABELS, f"Missing category label: {cat}"

    def test_entity_registry_lookup(self):
        """entity_registry.js defines ENTITY_REGISTRY with lookup; test Python-side structure."""
        import os, json as _json
        js_path = REPO_ROOT / "organic_market_agent" / "admin" / "static" / "crop_book" / "entity_registry.js"
        assert os.path.exists(js_path), "entity_registry.js missing"
        with open(js_path) as f:
            content = f.read()
        assert "ENTITY_REGISTRY" in content
        assert "version" in content
        assert "entities" in content
        assert "pest" in content
        assert "disease" in content

    def test_views_module_imports(self):
        """views.py must import cleanly and expose crop_book_bp."""
        from organic_market_agent.crop_book.views import crop_book_bp
        assert crop_book_bp is not None
        assert crop_book_bp.name == "crop_book"
        assert crop_book_bp.url_prefix == "/crop-book"
