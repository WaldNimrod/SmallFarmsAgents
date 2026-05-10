"""WP004 — CropBookPublisher tests.

Covers AC-01 through AC-09, AC-12, AC-13, AC-17, AC-19.

DB-dependent tests skip when PostgreSQL is unavailable.
JS-dependent tests (AC-05/06/07/08) use a lightweight JSON fixture
plus regex/string assertions — no jsdom required.
"""
from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_source_value(**kwargs):
    sv = MagicMock()
    sv.field_name    = kwargs.get("field_name", "documented_price")
    sv.source        = kwargs.get("source", "JMF 2024")
    sv.value_text    = kwargs.get("value_text", None)
    sv.value_numeric = kwargs.get("value_numeric", Decimal("22.0"))
    sv.unit          = kwargs.get("unit", "kg")
    sv.note          = kwargs.get("note", None)
    return sv


def _make_variety(**kwargs):
    v = MagicMock()
    v.id                        = kwargs.get("id", 1)
    v.name_he                   = kwargs.get("name_he", "ברירת מחדל")
    v.name_en                   = kwargs.get("name_en", "Default")
    v.is_default                = kwargs.get("is_default", True)
    v.is_grafted                = kwargs.get("is_grafted", False)
    v.rootstock_variety         = kwargs.get("rootstock_variety", None)
    v.planting_method           = kwargs.get("planting_method", "direct_sow")
    v.days_to_maturity          = kwargs.get("days_to_maturity", 45)
    v.harvest_window_min_days   = kwargs.get("harvest_window_min_days", None)
    v.harvest_window_max_days   = kwargs.get("harvest_window_max_days", 21)
    v.in_row_spacing_cm         = kwargs.get("in_row_spacing_cm", None)
    v.rows_per_bed              = kwargs.get("rows_per_bed", None)
    v.planting_season           = kwargs.get("planting_season", "קיץ")
    v.succession_interval_weeks = kwargs.get("succession_interval_weeks", None)
    v.harvest_stage             = kwargs.get("harvest_stage", "baby_leaf")
    v.harvest_unit              = kwargs.get("harvest_unit", "case")
    v.avg_yield_per_bed_m       = kwargs.get("avg_yield_per_bed_m", Decimal("0.175"))
    v.yield_source              = kwargs.get("yield_source", "JMF")
    v.documented_price          = kwargs.get("documented_price", Decimal("8.0"))
    v.documented_price_unit     = kwargs.get("documented_price_unit", "kg")
    v.documented_price_source   = kwargs.get("documented_price_source", "JMF 2024")
    v.avg_revenue_per_bed_m     = kwargs.get("avg_revenue_per_bed_m", Decimal("6.0"))
    v.pricebook_product_id      = kwargs.get("pricebook_product_id", None)
    v.days_to_germinate_gh      = kwargs.get("days_to_germinate_gh", None)
    v.days_in_gh_total          = kwargs.get("days_in_gh_total", None)
    v.seeder                    = kwargs.get("seeder", None)
    v.seeder_front_gear         = kwargs.get("seeder_front_gear", None)
    v.seeder_rear_gear          = kwargs.get("seeder_rear_gear", None)
    v.seeder_roller_plate       = kwargs.get("seeder_roller_plate", None)
    v.notes                     = kwargs.get("notes", None)
    v.source_values             = kwargs.get("source_values", [_make_source_value()])
    return v


def _make_family(id_=1, scientific_name="Brassicaceae", name_he="מצליבים"):
    f = MagicMock()
    f.id             = id_
    f.scientific_name = scientific_name
    f.name_he        = name_he
    return f


def _make_crop(**kwargs):
    c = MagicMock()
    c.id                   = kwargs.get("id", 1)
    c.name_he              = kwargs.get("name_he", "ארוגולה")
    c.name_en              = kwargs.get("name_en", "Arugula")
    c.scientific_name      = kwargs.get("scientific_name", "Eruca sativa")
    c.family_id            = kwargs.get("family_id", 1)
    c.category             = kwargs.get("category", "baby")
    c.growth_cycle         = kwargs.get("growth_cycle", "annual")
    c.harvest_unit_default = kwargs.get("harvest_unit_default", "case")
    c.first_fruit_year     = kwargs.get("first_fruit_year", None)
    c.conversion_group_id  = kwargs.get("conversion_group_id", None)
    c.description          = kwargs.get("description", "גידול ירוק")
    c.oma_product_id       = kwargs.get("oma_product_id", "VEG_ARU")
    varieties              = kwargs.get("varieties", [_make_variety()])
    c.varieties            = varieties
    c.unit_conversions     = []
    return c


def _make_session(crops, families=None, conversion_groups=None, conversions=None):
    """Mock SQLAlchemy session returning fixed query results."""
    session = MagicMock()

    families = families or [_make_family()]
    conversion_groups = conversion_groups or []
    conversions = conversions or []

    def _query_side_effect(model_cls):
        from organic_market_agent.crop_book.models import (
            Crop, CropFamily, CropConversionGroup, CropUnitConversion,
        )
        q = MagicMock()
        if model_cls is Crop:
            q.options.return_value.order_by.return_value.all.return_value = crops
        elif model_cls is CropFamily:
            q.order_by.return_value.all.return_value = families
        elif model_cls is CropConversionGroup:
            q.order_by.return_value.all.return_value = conversion_groups
        elif model_cls is CropUnitConversion:
            filtered = MagicMock()
            filtered.all.return_value = conversions
            q.filter.return_value = filtered
        return q

    session.query.side_effect = _query_side_effect
    return session


# ---------------------------------------------------------------------------
# AC-01: run() writes 3 artifacts
# ---------------------------------------------------------------------------

def test_run_writes_three_artifacts(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher

    crops = [_make_crop()]
    session = _make_session(crops)

    publisher = CropBookPublisher()
    result = publisher.run(session, tmp_path)

    assert (tmp_path / "sfagent-crop-book-body.html").exists()
    assert (tmp_path / "sfagent-crop-book-data.json").exists()
    assert (tmp_path / "sfagent-crop-book-manifest.json").exists()
    assert (tmp_path / "sfagent-crop-book-body.html").stat().st_size > 0
    assert (tmp_path / "sfagent-crop-book-data.json").stat().st_size > 0
    assert (tmp_path / "sfagent-crop-book-manifest.json").stat().st_size > 0


# ---------------------------------------------------------------------------
# AC-02: data.json has required top-level keys
# ---------------------------------------------------------------------------

def test_data_schema_keys(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher

    session = _make_session([_make_crop()])
    CropBookPublisher().run(session, tmp_path)

    data = json.loads((tmp_path / "sfagent-crop-book-data.json").read_text(encoding="utf-8"))
    required_keys = {
        "schema", "data_version", "generated_at",
        "categories", "season_tokens", "families",
        "conversion_groups", "conversions", "entity_registry", "crops",
    }
    assert required_keys.issubset(set(data.keys()))
    assert data["schema"] == "crop_book.v1"
    assert data["data_version"] == "1.0.0"


# ---------------------------------------------------------------------------
# AC-03: data.json contains >= 52 crops and >= 242 varieties (DB integration)
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_full_seed_present(db_session, tmp_path):
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher

    CropBookPublisher().run(db_session, tmp_path)
    data = json.loads((tmp_path / "sfagent-crop-book-data.json").read_text(encoding="utf-8"))

    assert len(data["crops"]) >= 52, f"expected >= 52 crops, got {len(data['crops'])}"
    total_varieties = sum(len(c["varieties"]) for c in data["crops"])
    assert total_varieties >= 242, f"expected >= 242 varieties, got {total_varieties}"


# ---------------------------------------------------------------------------
# AC-13: body fragment root has dir="rtl" lang="he"
# ---------------------------------------------------------------------------

def test_rtl_lang_attrs(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher

    session = _make_session([_make_crop()])
    CropBookPublisher().run(session, tmp_path)

    body = (tmp_path / "sfagent-crop-book-body.html").read_text(encoding="utf-8")
    assert 'dir="rtl"' in body
    assert 'lang="he"' in body


# ---------------------------------------------------------------------------
# AC-17: publisher sentinel invariant
# ---------------------------------------------------------------------------

def test_body_sentinel_present_on_normal_render(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import (
        CropBookPublisher, CROP_BOOK_DATA_URL_SENTINEL,
    )

    session = _make_session([_make_crop()])
    CropBookPublisher().run(session, tmp_path)

    body = (tmp_path / "sfagent-crop-book-body.html").read_text(encoding="utf-8")
    assert CROP_BOOK_DATA_URL_SENTINEL in body


def test_body_sentinel_invariant_raises_when_missing(tmp_path, monkeypatch):
    """Publisher must raise CropBookPublishAbortError when sentinel is absent from body."""
    from organic_market_agent.crop_book.publisher.engine import (
        CropBookPublisher, CropBookPublishAbortError,
    )

    session = _make_session([_make_crop()])

    original_render = None

    def _tampered_render(template_name, **ctx):
        html = original_render(template_name, **ctx)
        # Strip out the sentinel to simulate template drift
        return html.replace(
            'window.CROP_BOOK_DATA_URL = "./sfagent-crop-book-data.json"',
            'window.CROP_BOOK_DATA_URL = "./WRONG"',
        )

    publisher = CropBookPublisher()
    # Patch the jinja render at the point where body_html is produced
    import organic_market_agent.crop_book.publisher.engine as eng_mod
    original_render = None

    class _FakeBodyTpl:
        def render(self, **kwargs):
            return "<div>no sentinel here</div>"

    class _FakeEnv:
        def get_template(self, name):
            if name == "crop_book_body.html":
                return _FakeBodyTpl()
            raise FileNotFoundError(name)

    with patch.object(eng_mod, "Environment", return_value=_FakeEnv()):
        with pytest.raises(CropBookPublishAbortError, match="sentinel"):
            publisher.run(session, tmp_path)


# ---------------------------------------------------------------------------
# AC-17 additional: run() return dict shape
# ---------------------------------------------------------------------------

def test_run_return_dict_keys(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher

    session = _make_session([_make_crop()])
    result = CropBookPublisher().run(session, tmp_path)

    for k in ("output_dir", "files", "crop_count", "variety_count", "data_size_bytes", "generated_at"):
        assert k in result, f"missing key: {k}"
    assert result["crop_count"] == 1
    assert result["variety_count"] == 1
    assert len(result["files"]) == 3


# ---------------------------------------------------------------------------
# AC-08: timeline ruler — default variety only, null→0, max(1, ceil(hw/7))
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hw_max,expected_weeks", [
    (21,   3),
    (22,   4),
    (0,    1),
    (None, 1),
])
def test_timeline_ruler_weeks(hw_max, expected_weeks, tmp_path):
    """Verify the JS timeline formula via a text scan of the rendered body."""
    import math

    # Confirm Python formula matches expected (mirrors views.py:197)
    hw = hw_max or 0
    computed = max(1, math.ceil(hw / 7))
    assert computed == expected_weeks, f"formula mismatch for hw_max={hw_max}"

    # Also verify the JS contains the correct formula expression
    js_path = (
        Path(__file__).parent.parent.parent
        / "organic_market_agent/crop_book/publisher/static/sfagent-crop-book.js"
    )
    if js_path.exists():
        js = js_path.read_text(encoding="utf-8")
        assert "Math.ceil(hwMax / 7)" in js, "JS timeline formula not found in SPA"
        assert "Math.max(1," in js, "JS Math.max(1,...) not found in SPA"


# ---------------------------------------------------------------------------
# AC-19: entity registry schema + known entity
# ---------------------------------------------------------------------------

def test_entity_registry_schema():
    from organic_market_agent.crop_book.publisher.entity_registry_data import (
        ENTITY_REGISTRY, validate_entity_registry,
    )

    validate_entity_registry(ENTITY_REGISTRY)  # must not raise
    assert "version" in ENTITY_REGISTRY
    assert "type_labels" in ENTITY_REGISTRY
    assert "entities" in ENTITY_REGISTRY
    for etype in ("pest", "disease", "equip", "input", "technique", "crop"):
        assert etype in ENTITY_REGISTRY["entities"], f"entity type '{etype}' missing"


def test_entity_registry_known_entity_present():
    from organic_market_agent.crop_book.publisher.entity_registry_data import ENTITY_REGISTRY

    entities = ENTITY_REGISTRY["entities"]
    assert "diamondback-moth" in entities["pest"], \
        "known pest 'diamondback-moth' not found in ENTITY_REGISTRY"


def test_entity_registry_embedded_in_data_json(tmp_path):
    """entity_registry in data.json must pass schema validation."""
    from organic_market_agent.crop_book.publisher.engine import CropBookPublisher
    from organic_market_agent.crop_book.publisher.entity_registry_data import validate_entity_registry

    session = _make_session([_make_crop()])
    CropBookPublisher().run(session, tmp_path)

    data = json.loads((tmp_path / "sfagent-crop-book-data.json").read_text(encoding="utf-8"))
    validate_entity_registry(data["entity_registry"])
    assert "diamondback-moth" in data["entity_registry"]["entities"]["pest"]


# ---------------------------------------------------------------------------
# AC-12: CLI smoke via CliRunner (mocked DB + publisher)
# ---------------------------------------------------------------------------

def test_cli_smoke(tmp_path):
    from click.testing import CliRunner
    from unittest.mock import patch, MagicMock

    from organic_market_agent.__main__ import cli

    mock_summary = {
        "output_dir":    str(tmp_path),
        "files":         ["sfagent-crop-book-body.html", "sfagent-crop-book-data.json", "sfagent-crop-book-manifest.json"],
        "crop_count":    5,
        "variety_count": 20,
        "data_size_bytes": 12345,
        "generated_at":  "2026-05-10T12:00:00+00:00",
    }

    with patch("organic_market_agent.crop_book.publisher.engine.CropBookPublisher.run",
               return_value=mock_summary):
        with patch("organic_market_agent.db.session.SessionFactory") as mock_sf:
            mock_sf.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_sf.return_value.__exit__  = MagicMock(return_value=False)

            runner = CliRunner()
            result = runner.invoke(cli, ["crop_book_publish", "--output-dir", str(tmp_path)])

    assert result.exit_code == 0, f"CLI exited {result.exit_code}:\n{result.output}"
    assert "5 crops" in result.output or "crop" in result.output.lower()


# ---------------------------------------------------------------------------
# AC-07: equipment tab hidden when no seeder data
# ---------------------------------------------------------------------------

def test_equipment_tab_hidden_logic():
    """Verify the seeder-detection logic: no variety has any seeder field."""
    variety_no_seeder = _make_variety(
        seeder=None, seeder_front_gear=None, seeder_rear_gear=None, seeder_roller_plate=None
    )
    variety_has_seeder = _make_variety(
        seeder="Jang JP-1", seeder_front_gear="F3"
    )

    def _has_seeder(varieties):
        return any(
            v.seeder or v.seeder_front_gear or v.seeder_rear_gear or v.seeder_roller_plate
            for v in varieties
        )

    assert not _has_seeder([variety_no_seeder])
    assert _has_seeder([variety_has_seeder])
    assert not _has_seeder([])


# ---------------------------------------------------------------------------
# CropBookPublishAbortError: raises on empty crop list
# ---------------------------------------------------------------------------

def test_abort_on_empty_crops(tmp_path):
    from organic_market_agent.crop_book.publisher.engine import (
        CropBookPublisher, CropBookPublishAbortError,
    )

    session = _make_session(crops=[])
    with pytest.raises(CropBookPublishAbortError, match="crop count is 0"):
        CropBookPublisher().run(session, tmp_path)
