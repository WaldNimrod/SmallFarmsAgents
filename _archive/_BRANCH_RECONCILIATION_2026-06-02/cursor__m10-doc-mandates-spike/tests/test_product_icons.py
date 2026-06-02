"""Publisher product icon mapping (IconPark outline, vendored SVG)."""
from __future__ import annotations

from organic_market_agent.publisher.product_icons import (
    DEFAULT_SLUG,
    augment_publish_product,
    icon_href,
    icon_slug_for_product_code,
)


def test_icon_slug_for_product_code_known() -> None:
    assert icon_slug_for_product_code("PRD013") == "carrot"


def test_icon_slug_for_product_code_unknown() -> None:
    assert icon_slug_for_product_code("PRD999") == DEFAULT_SLUG
    assert icon_slug_for_product_code("") == DEFAULT_SLUG


def test_augment_publish_product_mutates_row() -> None:
    row = {"product_id": "PRD001", "canonical_name_he": "עגבנייה"}
    augment_publish_product(row)
    assert row["icon_slug"] == "tomato"
    assert row["icon_path"] == icon_href("tomato")


def test_icon_href_shape() -> None:
    assert icon_href("leaf") == "icons/iconpark/leaf.svg"
