"""Tests for JMF_CROP_MAP (AC-01..AC-04.1). SFA-S003-P002-WP-B1 + WP-B1-patch01."""
import pytest
from collections import Counter
from pathlib import Path

pytestmark = pytest.mark.crop_book

FIXTURE_XLSX = Path(__file__).parent / "fixtures" / "jmf" / "minimal_masterclass.xlsx"


@pytest.fixture
def jmf_crop_map():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    return JMF_CROP_MAP


def test_jmf_crop_map_count(jmf_crop_map):
    """AC-01 (patch04): exactly 87 entries (52 baseline + 34 aliases + 1 Ginger)."""
    assert len(jmf_crop_map) == 87, f"Expected 87 entries, got {len(jmf_crop_map)}"


def test_jmf_crop_map_keys_unique_and_nonempty(jmf_crop_map):
    """AC-03: every key is a unique non-empty ASCII English string."""
    keys = list(jmf_crop_map.keys())
    assert len(keys) == len(set(keys)), "Duplicate keys found"
    for k in keys:
        assert k and k.strip(), f"Empty key found: {k!r}"
        assert k.isascii(), f"Non-ASCII key: {k!r}"


def test_jmf_crop_map_values_nonempty_hebrew(jmf_crop_map):
    """AC-03: every value is a non-empty string (Hebrew)."""
    for k, v in jmf_crop_map.items():
        assert v and v.strip(), f"Empty value for key {k!r}"


def test_jmf_crop_map_duplicate_target_allowlist(jmf_crop_map):
    """AC-03 (patch03): exactly 24 by-design duplicate Hebrew-target groups
    per LOD400 v1.0.0 §3.4 + DECISION_WP-B1-patch03_TAXONOMY §3."""
    counts = Counter(jmf_crop_map.values())
    duplicates = {
        v: sorted([k for k, mv in jmf_crop_map.items() if mv == v])
        for v, c in counts.items() if c > 1
    }
    assert duplicates == {
        # ── NEW patch03 group ──
        "עלי בייבי":     ["Baby kale", "Mesclun", "Salad Mix"],

        # ── Baseline pairs from WP-B1 (Mesclun/Salad Mix תערובת סלט group disappeared) ──
        "קישוא":          ["Summer Squash", "Zucchini"],

        # ── patch01 typo / synonym / qualifier groups (mostly unchanged) ──
        "כרוב ניצנים":    ["Brussel Sprouts", "Brussels Sprouts"],
        "פאק צ'וי":       ["Bok Choy", "Pak Choi"],
        "כוסברה":         ["Cilantro", "Coriander"],
        "מנגולד":         ["Chard", "Swiss Chard"],
        "אבטיח":          ["Watermelon", "Watermelons"],
        "תפוח אדמה":      ["Potato", "Potatoes"],
        "גזר":            ["Carrots", "Fresh Carrots"],
        "בצל":            ["Onions", "Storage Onion"],
        "בצל ירוק":       ["Green Onion", "Scallions"],
        "כרישה":          ["Leek Storage", "Leek Summer", "Leeks"],

        # ── Shrunk groups (patch03 splits removed members) ──
        "פלפל":           ["Bell Pepper", "Peppers"],                       # was 3; Hot Pepper left
        "עגבנייה":        ["Roma Tomato", "Tomatoes"],                       # was 4; Cherry + Heirloom left
        "מלפפון":         ["Cucumbers", "Greenhouse English Cucumber"],     # was 3; Libanese key left
        "כרוב":           ["Cabbage", "Fall Cabbage", "Savoy Cabbage",
                           "Summer Cabbage"],                                # was 5; Chinese left

        # ── Unchanged patch01 groups ──
        "חסה":            ["Lettuce", "Salanova Lettuce", "Sucrine"],
        "צנונית":         ["Raddish", "Radishes", "Winter Radish"],
        "תרד":            ["Spinach", "Spinach TR", "Spinarch SD"],
        "כרובית":         ["Cauliflower", "Cauliflower / Romanesco"],
        "לפת":            ["Hakurei Turnip", "Turnips"],
        "סלרי שורש":      ["Celery Root", "Mini Celery Root"],
        "שומר":           ["Fennel", "Mini Fennel"],
        "חציל":           ["Eggplant", "Eggplant  (Feld)"],
    }, f"unexpected Hebrew-value duplicates: {duplicates}"


def test_jmf_crop_map_hebrew_roundtrip(jmf_crop_map):
    """AC-03 R-02: Hebrew values survive repr() → eval() roundtrip (encoding check)."""
    for k, v in list(jmf_crop_map.items())[:5]:
        # eval(repr(v)) should equal v — proves UTF-8 encoding is intact
        assert eval(repr(v)) == v, f"Hebrew roundtrip failed for key {k!r}: {v!r}"


def test_jmf_crop_map_miss_not_in_map():
    """Miss handling: a crop not in JMF_CROP_MAP should not be looked up without KeyError."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    miss = JMF_CROP_MAP.get("NonExistentCrop2026")
    assert miss is None, "get() on miss should return None"


def test_jmf_crop_map_fixture_crops_mapped():
    """Fixture crops (Arugula, Carrots, Basil) are all in JMF_CROP_MAP."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    for crop in ["Arugula", "Carrots", "Basil"]:
        assert crop in JMF_CROP_MAP, f"{crop!r} not in JMF_CROP_MAP"


# ─── patch01 additions ───────────────────────────────────────────────────────

def test_ac02_rutabaga_value_corrected(jmf_crop_map):
    """AC-02a (patch01): Rutabaga value is 'רוטבגה' (phonetic transliteration)."""
    assert jmf_crop_map["Rutabaga"] == "רוטבגה", (
        f"Expected 'רוטבגה', got {jmf_crop_map['Rutabaga']!r}"
    )


def test_ac02_old_rutabaga_value_absent():
    """AC-02b (patch01): hallucinated value 'ברוקקואר' must not appear in constants.py."""
    constants_path = Path(__file__).parents[2] / "organic_market_agent" / "crop_book" / "constants.py"
    content = constants_path.read_text(encoding="utf-8")
    assert "ברוקקואר" not in content, "Hallucinated Rutabaga value 'ברוקקואר' still present in constants.py"


def test_ac04_1_eggplant_feld_literal_alias(jmf_crop_map):
    """AC-04.1 (patch01): 'Eggplant  (Feld)' (double-space literal) is a key mapping to 'חציל'."""
    assert "Eggplant  (Feld)" in jmf_crop_map, "'Eggplant  (Feld)' literal alias missing from JMF_CROP_MAP"
    assert jmf_crop_map["Eggplant  (Feld)"] == "חציל", (
        f"Expected 'חציל', got {jmf_crop_map['Eggplant  (Feld)']!r}"
    )


def test_ac03_duplicate_group_count(jmf_crop_map):
    """AC-03 (patch03): exactly 24 Hebrew values appear more than once."""
    counts = Counter(jmf_crop_map.values())
    dup_count = sum(1 for c in counts.values() if c > 1)
    assert dup_count == 24, f"Expected 24 duplicate-target groups, got {dup_count}"


# ─── patch02 regression tests (DECISION 2026-05-25 §Q4) ───

def test_parsnips_value_post_patch02():
    """patch02 (DECISION 2026-05-25 §Q4): Parsnips Hebrew is 'שורש פטרוזילה'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Parsnips"] == "שורש פטרוזילה", (
        f"Parsnips Hebrew value drifted from DECISION §Q4. "
        f"Got: {JMF_CROP_MAP['Parsnips']!r}"
    )
    # Negative — the old colloquial value must NOT be present
    assert "גזר לבן" not in JMF_CROP_MAP.values(), (
        "Stale 'גזר לבן' value found in JMF_CROP_MAP — patch02 not applied?"
    )


def test_shallots_value_post_patch02():
    """patch02 (DECISION 2026-05-25 §Q4): Shallots Hebrew is 'בצלצלי שאלוט'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Shallots"] == "בצלצלי שאלוט", (
        f"Shallots Hebrew value drifted from DECISION §Q4. "
        f"Got: {JMF_CROP_MAP['Shallots']!r}"
    )
    # Negative — the pure-transliteration value must NOT be the lone match anymore
    assert JMF_CROP_MAP["Shallots"] != "שאלוט", (
        "Shallots still uses pure transliteration; patch02 not applied"
    )


# ─── patch03 regression tests (DECISION_WP-B1-patch03_TAXONOMY_2026-05-25) ───

def test_mesclun_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Mesclun"] == "עלי בייבי"


def test_salad_mix_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Salad Mix"] == "עלי בייבי"


def test_baby_kale_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Baby kale"] == "עלי בייבי"


def test_cherry_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Cherry Tomato"] == "עגבניית שרי"


def test_heirloom_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Heirloom Tomato"] == "עגבניות מורשת"


def test_lebanese_cucumber_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Libanese Cucumber"] == "מלפפון חממה"


def test_chinese_cabbage_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Chinese Cabbage"] == "כרוב סיני"


def test_hot_pepper_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Hot Pepper"] == "פלפל חריף"


def test_beans_bush_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Beans (Bush)"] == "שעועית שיחית"


def test_snow_peas_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Snow Peas"] == "אפונת שלג"


def test_basil_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Basil"] == "בזיליקום"


# ─── patch04 regression tests (DECISION_WP-B1-patch04-patch06 §2.5) ───

def test_ginger_baseline_post_patch04():
    """patch04 (DECISION §2.5): Ginger Hebrew is 'ג'ינג'ר'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"
    assert "ג'ינג'ר" in JMF_CROP_MAP.values()
