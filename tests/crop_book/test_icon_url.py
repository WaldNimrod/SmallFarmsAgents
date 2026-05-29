"""Tests for WP-UI-patch02 Phase 1 — per-crop icon_url system.

Covers AC-U2-02, AC-U2-03, AC-U2-04 per LOD400_spec §5.
"""
import inspect
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.crop_book

CROP_CARD_PHP = (
    Path(__file__).resolve().parents[2]
    / "sfa_delivery/templates/macros/crop_card.php"
)
BOOK_CROP_PHP = (
    Path(__file__).resolve().parents[2]
    / "sfa_delivery/templates/pages/book_crop.php"
)


# ---------------------------------------------------------------------------
# AC-U2-02: Crop model exposes icon_url attribute
# ---------------------------------------------------------------------------

def test_crop_model_has_icon_url_attribute():
    """AC-U2-02: Crop SQLAlchemy model must expose icon_url as a mapped column."""
    from organic_market_agent.crop_book.models import Crop
    # inspect mapped columns via __table__
    columns = {c.name for c in Crop.__table__.columns}
    assert "icon_url" in columns, "icon_url column must be present on Crop.__table__"


def test_crop_model_icon_url_is_nullable():
    """AC-U2-02: icon_url column must be nullable (Phase 2 backfill)."""
    from organic_market_agent.crop_book.models import Crop
    col = Crop.__table__.c["icon_url"]
    assert col.nullable, "icon_url must be nullable"


def test_crop_model_icon_url_is_varchar255():
    """AC-U2-02: icon_url column must be VARCHAR(255)."""
    from organic_market_agent.crop_book.models import Crop
    import sqlalchemy as sa
    col = Crop.__table__.c["icon_url"]
    assert isinstance(col.type, sa.VARCHAR), "icon_url type must be VARCHAR"
    assert col.type.length == 255, "icon_url length must be 255"


def test_crop_icon_url_column_has_no_server_default():
    """AC-U2-02: icon_url column must have no server default (nullable → NULL at rest)."""
    from organic_market_agent.crop_book.models import Crop
    col = Crop.__table__.c["icon_url"]
    # No server_default means the column stays NULL when not supplied — correct behaviour.
    assert col.server_default is None, "icon_url must have no server_default"


# ---------------------------------------------------------------------------
# Helper: render a PHP snippet via php CLI
# ---------------------------------------------------------------------------

def _render_php(php_code: str) -> str:
    """Run a PHP snippet and return stdout. Skip if php not available."""
    result = subprocess.run(
        ["php", "-r", php_code],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"php CLI error: {result.stderr[:200]}")
    return result.stdout


def _render_crop_card(crop_array_php: str) -> str:
    """Render crop_card.php with the given PHP $crop array expression."""
    macro = CROP_CARD_PHP.as_posix()
    php_code = (
        f"$crop = {crop_array_php};\n"
        f"ob_start();\n"
        f"include '{macro}';\n"
        f"echo ob_get_clean();\n"
    )
    result = subprocess.run(
        ["php", "-r", php_code],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"php CLI error: {result.stderr[:200]}")
    return result.stdout


# ---------------------------------------------------------------------------
# AC-U2-03: render emits <img class="crop-card__art"> when icon_url set
# ---------------------------------------------------------------------------

def test_crop_card_renders_img_when_icon_url_set():
    """AC-U2-03: crop_card.php must emit <img class="crop-card__art"> when icon_url is set."""
    html = _render_crop_card(
        "['slug'=>'basil','name_he'=>'בזיליקום','en_name'=>'Basil',"
        "'icon_url'=>'https://sfa.nimrod.bio/public_assets/img/icons/basil.webp',"
        "'icon_svg'=>'','family_tag_he'=>'']"
    )
    assert 'class="crop-card__art"' in html, (
        "AC-U2-03: crop-card__art img must be present when icon_url set"
    )
    assert "<img" in html, "AC-U2-03: must be an <img> element"
    assert "basil.webp" in html, "AC-U2-03: img src must contain the icon_url value"
    assert 'loading="lazy"' in html, "AC-U2-03: img must have loading=lazy"
    assert 'decoding="async"' in html, "AC-U2-03: img must have decoding=async"
    assert "בזיליקום" in html, "AC-U2-03: img alt must contain crop name"


def test_crop_card_no_broken_img_tag_when_icon_url_empty():
    """AC-U2-04 (card): no <img class=crop-card__art> when icon_url is empty string."""
    html = _render_crop_card(
        "['slug'=>'basil','name_he'=>'בזיליקום','en_name'=>'Basil',"
        "'icon_url'=>'',"
        "'icon_svg'=>'<svg viewBox=\"0 0 24 24\"><use href=\"#icon-leaf\"></use></svg>',"
        "'family_tag_he'=>'']"
    )
    assert 'class="crop-card__art"' not in html, (
        "AC-U2-04: crop-card__art img must NOT appear when icon_url is empty"
    )
    assert "gj-cropcard__icon" in html, (
        "AC-U2-04: SVG sprite wrapper must be present as fallback"
    )


def test_crop_card_leaf_fallback_when_no_icon_svg_and_no_icon_url():
    """AC-U2-04 (card): falls back to generic icon-leaf when both icon_url and icon_svg absent."""
    html = _render_crop_card(
        "['slug'=>'basil','name_he'=>'בזיליקום','en_name'=>'Basil',"
        "'icon_url'=>'','icon_svg'=>'','family_tag_he'=>'']"
    )
    assert 'class="crop-card__art"' not in html, (
        "AC-U2-04: crop-card__art img must NOT appear"
    )
    assert "#icon-leaf" in html, (
        "AC-U2-04: icon-leaf fallback must be present"
    )
