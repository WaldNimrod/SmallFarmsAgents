"""Tests for canon/topics.py and PHP parity (WI-1 / AC-02)."""
import re
from pathlib import Path

import pytest

from organic_market_agent.crop_book.canon.topics import (
    CROP_TOPICS,
    TOPIC_KEYS,
    TOPIC_BY_KEY,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOK_CROP_PHP = REPO_ROOT / "sfa_delivery" / "templates" / "pages" / "book_crop.php"


class TestCropTopics:
    def test_crop_topics_length(self):
        assert len(CROP_TOPICS) == 13, f"Expected 13 topics, got {len(CROP_TOPICS)}"

    def test_crop_topics_keys_ordered(self):
        expected = [
            "varieties", "spacing", "equipment", "soil", "bedprep",
            "sowing", "irrigation", "care", "pest", "harvest",
            "storage", "succession", "yield_inc",
        ]
        assert TOPIC_KEYS == expected

    def test_all_topics_have_required_keys(self):
        for t in CROP_TOPICS:
            assert "key" in t
            assert "label_he" in t
            assert "label_en" in t

    def test_topic_by_key_lookup(self):
        assert TOPIC_BY_KEY["pest"]["label_en"] == "Pests & diseases"
        assert TOPIC_BY_KEY["yield_inc"]["label_he"] == "יבול/הכנסה"

    def test_php_parity(self):
        """AC-02: PHP topic array in book_crop.php must match CROP_TOPICS keys."""
        if not BOOK_CROP_PHP.exists():
            pytest.skip("book_crop.php not found — skipping PHP parity check")

        php_text = BOOK_CROP_PHP.read_text(encoding="utf-8")

        # Extract ONLY the 13-topic $topics array keys. Topic entries are uniquely
        # identified by a following 'icon' key — this excludes other arrays in the
        # template that also use 'key'=> (e.g. the quick-facts field array L185-188,
        # which has no 'icon'). Order is preserved (re.findall is left-to-right).
        php_keys = re.findall(r"\['key'\s*=>\s*'([^']+)'\s*,\s*'icon'", php_text)

        if not php_keys:
            pytest.fail("Could not extract topic keys from book_crop.php $topics array")

        # Strict ordered parity — the schema SSoT (CROP_TOPICS) and the UI must agree
        # on both membership AND order.
        assert TOPIC_KEYS == php_keys, (
            f"PHP topic keys do not match CROP_TOPICS (ordered).\n"
            f"  Python: {TOPIC_KEYS}\n"
            f"  PHP:    {php_keys}"
        )

    def test_pest_topic_present(self):
        """WI-9 / AC-10: pest topic exists at index 8 (0-based)."""
        assert CROP_TOPICS[8]["key"] == "pest"
        assert CROP_TOPICS[8]["label_he"] == "מזיקים ומחלות"
