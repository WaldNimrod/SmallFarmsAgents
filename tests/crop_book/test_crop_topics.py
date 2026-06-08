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
        """AC-02 (revised — WP-CB-UI-REDESIGN, team_190 L-GATE_V PASS 2026-06-08):
        book_crop.php no longer carries a flat 13-key $topics array. The redesign
        replaced the Simple/Full/Deep depth IA with the mockup's lifecycle spine
        (מתי→איך→טיפול→יבול) over <details class="topic"> universal drill-down cards,
        which regroup the same crop data into stages rather than mirroring CROP_TOPICS
        1:1. The Python CROP_TOPICS taxonomy remains the data/canon SSoT (verified by
        the other tests in this class); this test now asserts the new UI structure
        exists instead of the retired flat-array ordered parity.
        """
        if not BOOK_CROP_PHP.exists():
            pytest.skip("book_crop.php not found — skipping PHP structure check")

        php_text = BOOK_CROP_PHP.read_text(encoding="utf-8")

        # The flat keyed $topics array is intentionally gone.
        legacy_array = re.findall(r"\['key'\s*=>\s*'([^']+)'\s*,\s*'icon'", php_text)
        assert not legacy_array, (
            "book_crop.php still carries the legacy flat $topics array; the redesign "
            "(WP-CB-UI-REDESIGN) replaced it with the lifecycle-spine drill-down."
        )

        # The new IA must be present: lifecycle spine + stage sections + .topic cards.
        for marker in ('stagenav', 'class="stage"', 'class="topic"'):
            assert marker in php_text, (
                f"book_crop.php must render the redesigned lifecycle IA — missing {marker!r}."
            )

        # CROP_TOPICS stays the canon SSoT (membership/order checked by the sibling tests).
        assert len(TOPIC_KEYS) == 13

    def test_pest_topic_present(self):
        """WI-9 / AC-10: pest topic exists at index 8 (0-based)."""
        assert CROP_TOPICS[8]["key"] == "pest"
        assert CROP_TOPICS[8]["label_he"] == "מזיקים ומחלות"
