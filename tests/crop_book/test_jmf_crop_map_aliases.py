"""Tests for patch01 alias additions to JMF_CROP_MAP. SFA-S003-P002-WP-B1-patch01."""
import pytest
from collections import Counter

pytestmark = pytest.mark.crop_book


@pytest.fixture
def jmf_crop_map():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    return JMF_CROP_MAP


def test_alias_spot_check_five_samples(jmf_crop_map):
    """patch01: 5 sample new aliases resolve to the expected crops.name_he values."""
    expected = {
        "Brussel Sprouts":          "כרוב ניצנים",   # typo variant
        "Pak Choi":                 "פאק צ'וי",       # synonym
        "Swiss Chard":              "מנגולד",          # synonym
        "Greenhouse Cherry Tomato": "עגבנייה",         # tomato variant
        "Eggplant  (Feld)":         "חציל",            # field-qualifier literal (double space)
    }
    for key, expected_value in expected.items():
        assert key in jmf_crop_map, f"Alias key {key!r} missing from JMF_CROP_MAP"
        assert jmf_crop_map[key] == expected_value, (
            f"Alias {key!r}: expected {expected_value!r}, got {jmf_crop_map[key]!r}"
        )


def test_alias_entry_count_grew_by_34(jmf_crop_map):
    """patch01: total entry count is exactly 86 (52 baseline + 34 aliases)."""
    baseline = 52
    added = 34
    expected_total = baseline + added
    assert len(jmf_crop_map) == expected_total, (
        f"Expected {expected_total} entries (baseline {baseline} + {added} aliases), "
        f"got {len(jmf_crop_map)}"
    )


def test_hebrew_value_collision_set_has_25_pairs(jmf_crop_map):
    """patch01: Hebrew-value-collision-set has exactly 25 duplicate-target pairs/groups."""
    counts = Counter(jmf_crop_map.values())
    duplicate_targets = {v for v, c in counts.items() if c > 1}
    assert len(duplicate_targets) == 25, (
        f"Expected 25 Hebrew values appearing >1 time, found {len(duplicate_targets)}: "
        f"{sorted(duplicate_targets)}"
    )
