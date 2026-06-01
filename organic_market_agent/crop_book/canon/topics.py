"""Canon §15 — Canonical 13-topic taxonomy for crop knowledge.

CROP_TOPICS: ordered list of dicts with keys: key, label_he, label_en
    SSoT for both schema field-grouping and UI section ordering.

This constant must match the PHP topic array in
    sfa_delivery/templates/pages/book_crop.php  (~L257).

A parity test (tests/crop_book/test_crop_topics.py) asserts the two stay
in sync — any UI edit must be mirrored here and vice versa.
"""
from __future__ import annotations

from typing import TypedDict


class TopicEntry(TypedDict):
    key: str
    label_he: str
    label_en: str


# Ordered 13-topic list (Canon §15, Amendment v1.3.0)
CROP_TOPICS: list[TopicEntry] = [
    {"key": "varieties",  "label_he": "זנים",            "label_en": "Varieties"},
    {"key": "spacing",    "label_he": "מרווח ופריסה",    "label_en": "Spacing & layout"},
    {"key": "equipment",  "label_he": "ציוד וכיוונון",   "label_en": "Equipment & tuning"},
    {"key": "soil",       "label_he": "קרקע ודישון",     "label_en": "Soil & fertilization"},
    {"key": "bedprep",    "label_he": "הכנת ערוגה",      "label_en": "Bed preparation"},
    {"key": "sowing",     "label_he": "זריעה/שתילה",     "label_en": "Sowing / transplanting"},
    {"key": "irrigation", "label_he": "השקיה",            "label_en": "Irrigation"},
    {"key": "care",       "label_he": "טיפוח ועישוב",    "label_en": "Care & weeding"},
    {"key": "pest",       "label_he": "מזיקים ומחלות",   "label_en": "Pests & diseases"},
    {"key": "harvest",    "label_he": "קציר",             "label_en": "Harvest"},
    {"key": "storage",    "label_he": "שטיפה ואחסון",    "label_en": "Washing & storage"},
    {"key": "succession", "label_he": "רצף וחברה",       "label_en": "Succession & companions"},
    {"key": "yield_inc",  "label_he": "יבול/הכנסה",      "label_en": "Yield / revenue"},
]

# Flat ordered key list — useful for ordering / indexing
TOPIC_KEYS: list[str] = [t["key"] for t in CROP_TOPICS]

# Map key → entry (for O(1) lookup by key)
TOPIC_BY_KEY: dict[str, TopicEntry] = {t["key"]: t for t in CROP_TOPICS}
