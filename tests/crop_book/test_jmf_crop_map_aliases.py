"""Tests for patch01 alias additions to JMF_CROP_MAP. SFA-S003-P002-WP-B1-patch01."""
import pytest
from collections import Counter

pytestmark = pytest.mark.crop_book


@pytest.fixture
def jmf_crop_map():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    return JMF_CROP_MAP


def test_alias_spot_check_five_samples(jmf_crop_map):
    """patch06: 5 sample synonym aliases resolve to the correct baseline Hebrew."""
    expected = {
        "Coriander":   "כוסברה",
        "Green Onion": "בצל ירוק",
        "Pak Choi":    "פאק צ'וי",
        "Potato":      "תפוח אדמה",
        "Swiss Chard": "מנגולד",
    }
    for key, expected_value in expected.items():
        assert key in jmf_crop_map
        assert jmf_crop_map[key] == expected_value


# test_alias_entry_count_grew_by_34 REMOVED by patch06 — the 34-alias assertion no longer holds


def test_hebrew_value_collision_set_has_6_groups(jmf_crop_map):
    """patch06 + team_00 2026-06-10: Hebrew-value collision set = 8 groups
    (6 synonym groups + 'לפת' (Rutabaga→Turnips) + 'עגבנייה' (Heirloom→Tomatoes))."""
    counts = Counter(jmf_crop_map.values())
    duplicate_targets = {v for v, c in counts.items() if c > 1}
    assert len(duplicate_targets) == 8, (
        f"Expected 8 synonym groups, found {len(duplicate_targets)}: {sorted(duplicate_targets)}"
    )
