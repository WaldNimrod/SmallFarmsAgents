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
    """patch06: 60 entries (53 baselines + 6 synonyms + 1 Ginger from patch04)."""
    assert len(jmf_crop_map) == 60, f"Expected 60, got {len(jmf_crop_map)}"


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
    """patch06 + team_00 2026-06-10: 6 synonym-pair duplicate-target groups PLUS
    'לפת' (Turnips), which Rutabaga now resolves to (no separate 'רוטבגה' crop)."""
    counts = Counter(jmf_crop_map.values())
    duplicates = {
        v: sorted([k for k, mv in jmf_crop_map.items() if mv == v])
        for v, c in counts.items() if c > 1
    }
    assert duplicates == {
        "פאק צ'וי":    ["Bok Choy", "Pak Choi"],
        "מנגולד":      ["Chard", "Swiss Chard"],
        "בצל ירוק":    ["Green Onion", "Scallions"],
        "תפוח אדמה":   ["Potato", "Potatoes"],
        "אבטיח":       ["Watermelon", "Watermelons"],
        "כוסברה":      ["Cilantro", "Coriander"],
        "לפת":         ["Rutabaga", "Turnips"],
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
    """team_00 2026-06-10: Rutabaga resolves to canonical 'לפת' (Turnips) — no
    separate 'רוטבגה' crop is minted (supersedes the patch01 transliteration)."""
    assert jmf_crop_map["Rutabaga"] == "לפת", (
        f"Expected 'לפת', got {jmf_crop_map['Rutabaga']!r}"
    )
    assert "רוטבגה" not in jmf_crop_map.values(), (
        "Non-canonical 'רוטבגה' must not be a JMF_CROP_MAP target"
    )


def test_ac02_old_rutabaga_value_absent():
    """AC-02b (patch01): hallucinated value 'ברוקקואר' must not appear in constants.py."""
    constants_path = Path(__file__).parents[2] / "organic_market_agent" / "crop_book" / "constants.py"
    content = constants_path.read_text(encoding="utf-8")
    assert "ברוקקואר" not in content, "Hallucinated Rutabaga value 'ברוקקואר' still present in constants.py"


def test_ac03_duplicate_group_count(jmf_crop_map):
    """patch06 + team_00 2026-06-10: exactly 7 Hebrew values appear more than once
    (6 synonyms + 'לפת' now shared by Turnips and Rutabaga, which resolves to the
    canonical Turnips crop)."""
    counts = Counter(jmf_crop_map.values())
    dup_count = sum(1 for c in counts.values() if c > 1)
    assert dup_count == 7, f"Expected 7 duplicate-target groups, got {dup_count}"


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

def test_cherry_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Cherry Tomato"] == "עגבניית שרי"


def test_heirloom_tomato_value_post_patch03():
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Greenhouse Heirloom Tomato"] == "עגבניות מורשת"


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
    """team_00 2026-06-10: Basil resolves to canonical 'בזיל' (matches
    TEND_CROP_MAP) — no separate 'בזיליקום' crop is minted."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Basil"] == "בזיל"
    assert "בזיליקום" not in JMF_CROP_MAP.values(), (
        "Non-canonical 'בזיליקום' must not be a JMF_CROP_MAP target"
    )


# ─── patch04 regression tests (DECISION_WP-B1-patch04-patch06 §2.5) ───

def test_ginger_baseline_post_patch04():
    """patch04 (DECISION §2.5): Ginger Hebrew is 'ג'ינג'ר'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"
    assert "ג'ינג'ר" in JMF_CROP_MAP.values()


# ─── patch06 regression tests (DECISION 2026-05-25 §3) ───

def test_no_cultivar_keys_in_map_post_patch06():
    """patch06: 22 cultivar keys removed from JMF_CROP_MAP (now in crop_varieties)."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    removed_cultivars = {
        "Baby kale", "Bell Pepper", "Cauliflower / Romanesco", "Fall Cabbage",
        "Fresh Carrots", "Greenhouse English Cucumber", "Greenhouse Libanese Cucumber",
        "Hakurei Turnip", "Leek Storage", "Leek Summer", "Mesclun",
        "Mini Celery Root", "Mini Fennel", "Roma Tomato", "Salad Mix",
        "Salanova Lettuce", "Savoy Cabbage", "Storage Onion", "Sucrine",
        "Summer Cabbage", "Winter Radish", "Zucchini",
    }
    for k in removed_cultivars:
        assert k not in JMF_CROP_MAP, f"Cultivar key {k!r} still in MAP — patch06 incomplete"


def test_no_typo_keys_in_map_post_patch06():
    """patch06: 5 workbook typo keys removed from JMF_CROP_MAP."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    removed_typos = {"Brussel Sprouts", "Eggplant  (Feld)", "Raddish", "Spinach TR", "Spinarch SD"}
    for k in removed_typos:
        assert k not in JMF_CROP_MAP, f"Typo key {k!r} still in MAP — patch06 incomplete"


def test_six_synonym_groups_exact():
    """patch06 + team_00 2026-06-10: the duplicate-target groups are 6 pure synonym
    pairs PLUS 'לפת' (Turnips), which Rutabaga now resolves to (no separate crop)."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    from collections import Counter
    counts = Counter(JMF_CROP_MAP.values())
    duplicates = {v for v, c in counts.items() if c > 1}
    assert duplicates == {"פאק צ'וי", "מנגולד", "בצל ירוק", "תפוח אדמה", "אבטיח", "כוסברה", "לפת"}
