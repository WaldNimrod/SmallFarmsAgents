"""Slug generation strips display annotations leaked into name_en (audit follow-up).

Ensures messy English crop names produce clean URLs:
  "Beans (default: Pole/Climbing)" → "beans", "Onions: Scallions" → "scallions".
"""
import pytest

pytestmark = pytest.mark.crop_book

from organic_market_agent.publisher.sfa_ingest_push import _slugify


@pytest.mark.parametrize("name_en,expected", [
    ("Beans (default: Pole/Climbing)", "beans"),
    ("Pac Choi (Bok Choy)", "pac-choi"),
    ("Onions: Scallions", "scallions"),
    ("Lettuce: Salad Mix", "salad-mix"),
    ("Lettuce", "lettuce"),       # unaffected
    ("Peppers", "peppers"),       # unaffected
    ("Summer Squash", "summer-squash"),
])
def test_slugify_strips_annotations(name_en, expected):
    assert _slugify(name_en, fallback="x") == expected


def test_slugify_empty_falls_back():
    assert _slugify("", fallback="fb") == "fb"
    assert _slugify(None, fallback="fb") == "fb"
