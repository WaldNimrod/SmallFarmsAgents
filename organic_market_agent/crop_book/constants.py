"""ספר גידולים — shared enums, name-mapping tables, and team_00 overrides.

All map keys reflect Tend CSV raw values exactly (case-sensitive).
All DB enum values are English per LOD400 v2.0.0 §3 AC-01.
"""

from __future__ import annotations

TEND_CROP_MAP: dict[str, str] = {
    "Anise Hyssop": "אזוב מצוי",
    "Artichokes": "ארטישוק",
    "Arugula": "ארוגולה",
    "Basil": "בזיל",
    "Bay": "דפנה",
    "Beans: Bush & Pole": "שעועית",
    "Beets": "סלק",
    "Broccoli": "ברוקולי",
    "Cabbage": "כרוב",
    "Carrots": "גזר",
    "Celery": "סלרי",
    "Chard": "מנגולד",
    "Chinese Lantern": "פנס סיני",
    "Chives": "עירית",
    "Cilantro": "כוסברה",
    "Cress": "גרגר נחלים",
    "Cucumbers": "מלפפון",
    "Dill": "שמיר",
    "Eggplant": "חציל",
    "Fennel": "שומר",
    "Garlic": "שום",
    "Hibiscus": "היביסקוס",
    "Jerusalem Artichokes": "ארטישוק ירושלמי",
    "Jicama": "ג'יקמה",
    "Kale": "קייל",
    "Kohlrabi": "קולורבי",
    "Leeks": "כרישה",
    "Lemon Balm": "לימון בלם",
    "Lemon Verbena": "לימון ורבנה",
    "Lettuce": "חסה",
    "Lettuce: Salad Mix": "תערובת סלט",
    "Lovage": "לובסטייה",
    "Melons": "מלון",
    "Mint": "נענע",
    "New Zealand Spinach": "תרד ניו-זילנד",
    "Onions: Scallions": "בצל ירוק",
    "Oranges": "תפוז",
    "Pac Choi (Bok Choy)": "פאק צ'וי",
    "Parsley": "פטרוזיליה",
    "Peas": "אפונה",
    "Peppers": "פלפל",
    "Radishes": "צנונית",
    "Sage": "מרווה",
    "Spinach": "תרד",
    "Strawberry": "תות שדה",
    "Summer Squash": "קישוא",
    "Tarragon": "טרגון",
    "Thyme": "טימין",
    "Tomatoes": "עגבנייה",
    "Turmeric": "כורכום",
    "Turnips": "לפת",
    "Winter Squash": "דלעת",
}

TEND_FAMILY_MAP: dict[str, str] = {
    "Aizoaceae": "Aizoaceae",
    "Amaranthaceae": "Amaranthaceae",
    "Amaryllidaceae": "Amaryllidaceae",
    "Apiaceae": "Apiaceae",
    "Asparagaceae": "Asparagaceae",
    "Asteraceae": "Asteraceae",
    "Brassicaceae": "Brassicaceae",
    "Bromeliaceae": "Bromeliaceae",
    "Compositae": "Asteraceae",
    "Cucurbitaceae": "Cucurbitaceae",
    "Fabaceae": "Fabaceae",
    "Lamiaceae": "Lamiaceae",
    "Lauraceae": "Lauraceae",
    "Malvaceae": "Malvaceae",
    "Poaceae": "Poaceae",
    "Polygonaceae": "Polygonaceae",
    "Rosaceae": "Rosaceae",
    "Rutaceae": "Rutaceae",
    "Solanaceae": "Solanaceae",
    "Verbenaceae": "Verbenaceae",
    "Zingiberaceae": "Zingiberaceae",
}

CATEGORY_MAP: dict[str, str] = {
    "Vegetables": "vegetables",
    "Herbs": "herbs",
    "Baby": "baby",
    "Legumes": "legumes",
    "Berries": "fruits",
    "Trees": "fruit_trees",
    "Cover Crops & Farm Seed": "cover_crops",
    "Grain": "grains",
    "Grains": "grains",
    "Fruits": "fruits",
    "Fruit Trees": "fruit_trees",
}

HARVEST_UNIT_MAP: dict[str, str] = {
    "kg": "kg",
    "Kilograms": "kg",
    "Kilogram": "kg",
    "Grams": "kg",
    "g": "kg",
    "bn": "bunch",
    "Bunches": "bunch",
    "Bunch": "bunch",
    "hd": "head",
    "Heads": "head",
    "Head": "head",
    "cs": "case",
    "Cases": "case",
    "Case": "case",
    "ea": "unit",
    "Each": "unit",
    "Units": "unit",
    "seedling": "seedling",
    "Seedling": "seedling",
    "Seedlings": "seedling",
}

GROWTH_CYCLE_MAP: dict[str, str] = {
    "Annual": "annual",
    "Biennial": "biennial",
    "Perennial": "perennial",
    "Primocane": "perennial",
}

PLANTING_METHOD_MAP: dict[str, str] = {
    "Direct Sow": "direct_sow",
    "Drill Sow": "direct_sow",
    "Greenhouse Sow": "greenhouse_transplant",
    "Transplant": "transplant",
    "Transplant from Purchased": "purchase",
    "Plant": "transplant",
    "Cutting": "cutting",
}

HARVEST_STAGE_MAP: dict[str, str] = {
    "Full-Size": "full_size",
    "Full-Size Root": "full_size",
    "Head": "head",
    "Mini Head": "head",
    "Baby Leaf": "baby_leaf",
    "Baby Leaf Greens": "baby_leaf",
    "Microgreen": "baby_leaf",
    "Plant sale": "plant_sale",
    "Plant Sale": "plant_sale",
    "Early": "full_size",
    "Ripe": "full_size",
    "Leaf": "full_size",
    "Fresh": "full_size",
    "Scapes": "full_size",
    "Bulb": "full_size",
    "Coriander": "full_size",
}

TEAM00_DTM_OVERRIDES: dict[str, int] = {
    "ארוגולה": 21,
}

OUTLIER_CROPS: set[str] = {
    "ארוגולה",
    "תערובת סלט",
    "גרגר נחלים",
    "קייל",
    "מנגולד",
    "תרד",
    "תרד ניו-זילנד",
}

# ---------------------------------------------------------------------------
# JMF MasterClass crop-name map (SFA-S003-P002-WP-B1 LOD400 §5)
# ---------------------------------------------------------------------------
# Maps the English crop-name strings used in JMF CROP CHART / CROP ASSOCIATED
# TASKS / DIRECT SEEDING / NURSERY / CULTIVARS sheets to the canonical
# Hebrew `crops.name_he` values already populated by WP-A.
# On miss (importer encounters a JMF crop not in this map): log WARN and skip
# the row — same convention as TEND_CROP_MAP miss handling in tend.py.
#
# Maintenance: when a new JMF crop appears, append here; do NOT branch on it
# elsewhere. The 52 entries below cover all 52 CROP CHART rows in the
# 2018-edition MasterClass workbook (PROGRAM_BRIEF §1). Spot-check the count
# at test time (test_jmf_crop_map.py — AC-04).

JMF_CROP_MAP: dict[str, str] = {
    # ---- Brassicas ----
    "Arugula":            "ארוגולה",
    "Bok Choy":           "פאק צ'וי",
    "Broccoli":           "ברוקולי",
    "Brussels Sprouts":   "כרוב ניצנים",
    "Cabbage":            "כרוב",
    "Cauliflower":        "כרובית",
    "Kale":               "קייל",
    "Kohlrabi":           "קולורבי",
    "Radishes":           "צנונית",
    "Turnips":            "לפת",
    # ---- Greens / Salads ----
    "Chard":              "מנגולד",
    "Cress":              "גרגר נחלים",
    "Endive":             "אנדיב",
    "Lettuce":            "חסה",
    # ─── BEGIN patch03 taxonomy corrections (2026-05-25) ───
    # Per team_00 DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md.
    # 11 value changes; introduces 5 new baseline crops.name_he values
    # (עלי בייבי, עגבניית שרי, עגבניות מורשת, מלפפון חממה, כרוב סיני).
    # Net effect on duplicate-target allowlist: 25 → 24 groups.
    # patch06: Mesclun + Salad Mix (cultivar-level) removed; New Zealand Spinach kept.
    "New Zealand Spinach": "תרד ניו-זילנד",
    "Spinach":            "תרד",
    # ---- Alliums ----
    "Garlic":             "שום",
    "Leeks":              "כרישה",
    "Onions":             "בצל",
    "Scallions":          "בצל ירוק",
    "Shallots":           "בצלצלי שאלוט",   # patch02 (team_00 DECISION 2026-05-25 §Q4): pure transliteration "שאלוט" replaced with "shallot small-onions" hybrid
    # ---- Roots / Tubers ----
    "Beets":              "סלק",
    "Carrots":            "גזר",
    "Celery Root":        "סלרי שורש",
    "Jerusalem Artichokes": "ארטישוק ירושלמי",
    "Parsnips":           "שורש פטרוזילה",   # patch02 (team_00 DECISION 2026-05-25 §Q4): "גזר לבן" was colloquial; replaced with botanically accurate "parsley root"
    "Potatoes":           "תפוח אדמה",
    "Rutabaga":           "רוטבגה",   # phonetic transliteration (team_00 directive 2026-05-25; prior value was a hallucination, NOT a real Hebrew word)
    "Sweet Potatoes":     "בטטה",
    # ---- Solanaceae ----
    "Eggplant":           "חציל",
    "Peppers":            "פלפל",
    "Tomatillos":         "תומאטיו",
    "Tomatoes":           "עגבנייה",
    # ---- Cucurbits ----
    "Cucumbers":          "מלפפון",
    "Melons":             "מלון",
    "Summer Squash":      "קישוא",
    "Watermelons":        "אבטיח",
    "Winter Squash":      "דלעת",
    # patch06: Zucchini (cultivar) removed — variety data in crop_varieties
    # ---- Legumes ----
    "Beans (Bush)":       "שעועית שיחית",
    "Beans (Pole)":       "שעועית מטפסת",
    "Fava Beans":         "פול",
    "Peas":               "אפונה",
    "Snow Peas":          "אפונת שלג",
    # ---- Herbs ----
    "Basil":              "בזיליקום",
    "Celery":             "סלרי",
    "Cilantro":           "כוסברה",
    "Dill":               "שמיר",
    "Fennel":             "שומר",
    "Parsley":            "פטרוזיליה",
    # ─── BEGIN patch04 single-baseline addition (2026-05-25) ───
    "Ginger":             "ג'ינג'ר",   # team_00 DECISION_WP-B1-patch04-patch06 §2.5: Baby Ginger from MasterClass sheet 050. Cultivars (Baby variant) → crop_varieties.
    # ─── END patch04 single-baseline addition ───

    # ─── BEGIN patch01 alias additions (2026-05-25) ───
    # Maps farm-specific JMF MasterClass workbook variants to the same
    # crops.name_he as the canonical baseline keys. After this patch,
    # ~42/50 live-workbook crops map cleanly; the remaining 8 require
    # new crops.name_he rows and are out-of-scope for patch01.
    # Maintenance rule: when a new variant appears in any future
    # JMF workbook edition, append here — NEVER branch on the
    # English label elsewhere in the codebase.

    # ── Typo / spelling variants (5 removed by patch06 — edition suffixes and typos) ──

    # ── Synonyms / alternative English names ──
    "Pak Choi":                     "פאק צ'וי",     # Bok Choy synonym (matches existing TEND_CROP_MAP value)
    "Coriander":                    "כוסברה",       # Cilantro (Coriander = same plant)
    "Swiss Chard":                  "מנגולד",       # Chard with explicit Swiss qualifier
    "Watermelon":                   "אבטיח",        # Watermelons singular
    "Potato":                       "תפוח אדמה",    # Potatoes singular
    # patch06: Fresh Carrots (cultivar qualifier) removed — variety data in crop_varieties

    # ── Storage / season qualifiers (same species, marketed differently) ──
    # patch06: Storage Onion, Leek Storage, Leek Summer removed (cultivar-level qualifiers)
    "Green Onion":                  "בצל ירוק",     # Scallions synonym (matches TEND_CROP_MAP)

    # ── Pepper variants ──
    # patch06: Bell Pepper (cultivar) removed — variety data in crop_varieties
    "Hot Pepper":                   "פלפל חריף",    # Peppers (hot variant) — patch03: split from פלפל umbrella

    # ── Tomato variants (all Solanum lycopersicum at species level) ──
    # patch06: Roma Tomato (cultivar) removed — variety data in crop_varieties
    "Greenhouse Cherry Tomato":     "עגבניית שרי",  # protected-culture cherry — patch03: split from עגבנייה umbrella
    "Greenhouse Heirloom Tomato":   "עגבניות מורשת", # protected-culture heirloom — patch03: split from עגבנייה umbrella

    # ── Cucumber variants ──
    # patch06: Greenhouse English Cucumber + Greenhouse Libanese Cucumber removed (cultivars)
    # Greenhouse Libanese Cucumber removal also implicitly reverts patch03 §1.3 anomaly

    # ── Cabbage variants ──
    # patch06: Fall Cabbage, Savoy Cabbage, Summer Cabbage removed (season/cultivar qualifiers)
    "Chinese Cabbage":              "כרוב סיני",    # patch03: split from כרוב umbrella

    # ── Lettuce variants ──
    # patch06: Salanova Lettuce + Sucrine removed (cultivar-level variants)

    # ── Brassica & misc variants ──
    # patch06: Baby kale, Cauliflower / Romanesco, Hakurei Turnip, Mini Celery Root,
    # Mini Fennel, Winter Radish removed (cultivar/size qualifiers → crop_varieties)

    # ── Field-qualifier variants removed by patch06 (Eggplant  (Feld) — typo/artifact) ──
    # ─── END patch01 alias additions ───

    # ─── patch06 (2026-05-25): 22 cultivars + 5 typos removed per DECISION §3.
    # Variants now live in crop_varieties (populated by patch04). The MAP is
    # now baselines-only (53 baselines + 6 synonyms + 1 Ginger = 60 entries).
}
# Total: 60 entries (53 baselines + 6 synonyms + 1 Ginger from patch04).
# patch06 removed 27 entries (22 cultivars + 5 typos). Maintenance rule: when a new JMF MasterClass edition
# adds or renames a crop, append/edit an entry here only — never branch on
# JMF names elsewhere in the codebase. On runtime miss (JMF row whose
# English label is not a key), the importer logs WARN with the unmapped
# label and skips that row (same convention as TEND_CROP_MAP miss handling
# in tend.py). Test AC-01 enforces `len(JMF_CROP_MAP) == 60`.

# ---------------------------------------------------------------------------
# Tend overlay — task-type mapping + whitelist (SFA-S003-P002-WP-B3 LOD400 §6)
# ---------------------------------------------------------------------------
# team_00 confirmed whitelist on 2026-05-25 (Option B — 11 categories =
# 9 baseline + Trellis + Fertilize & Amend = 758/798 rows = 95.0% coverage).
# Source-of-truth analysis: TASKS.CSV row distribution captured in
# _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md
# (filed alongside the L-GATE_S R1 mandate per advisory #3 protocol).

TEND_TASK_WHITELIST: frozenset[str] = frozenset({
    # ── Original 9 (PROGRAM_BRIEF §4) ──
    "Transplant",            # 234 rows
    "Greenhouse Sow",        # 143 rows
    "Direct Sow",            # 124 rows
    "Weed",                  #  78 rows
    "Row Cover & Mulch",     #  55 rows
    "Stale Bed",             #  42 rows
    "Pest & Disease",        #  27 rows
    "Potting up",            #  16 rows
    "Thin",                  #   7 rows
    # ── Added by team_00 Option-B decision (2026-05-25) ──
    "Trellis",               #  13 rows
    "Fertilize & Amend",     #  13 rows
})

TEND_TASK_BLACKLIST: frozenset[str] = frozenset({
    "Maintenance",            #  6 rows — non-template
    "Irrigate",               #  3 rows — non-template (per-event)
    "Seed Cleaning",          #  2 rows — back-office
    "Drill Sow",              #  1 row  — single occurrence
    "השלמות שתילה",            #  4 rows — gap-fill (not template)
    "ריכוז שעות",              #  1 row  — labor-tracking artifact
    "הידרופוניקה",             #  1 row  — single occurrence
    "Cultivation & Tillage",  #  6 rows — single-crop (Carrots only); 0.75% coverage value
    "Prune",                  #  6 rows — low volume; overlaps `hand_weed` semantically
    "Greenhouse Activity",    # 16 rows — mixed content (mostly השלמות gap-fills)
})

# Tend label → JMF task_type enum value mapping.
# Some Tend rows require Method/Sub-method inspection to disambiguate
# (e.g., Weed → hand_weed vs flextine; Row Cover & Mulch → net_row_cover
# vs straw_mulch_topdress). See parse_tasks_templates() in tend_overlay.py.
TEND_TASK_TYPE_MAP: dict[str, str] = {
    # ── Direct 1-to-1 mappings ──
    "Direct Sow":          "at_seeding_transplanting",   # timing_anchor=seeding
    "Transplant":          "at_seeding_transplanting",   # timing_anchor=transplanting
    "Greenhouse Sow":      "nursery_seed",               # NEW B3
    "Stale Bed":           "stale_seed_bed",
    "Pest & Disease":      "pest_spray",                 # NEW B3
    "Potting up":          "potting_up",                 # NEW B3
    "Thin":                "thinning",                   # NEW B3
    "Trellis":             "trellis",                    # NEW B3
    "Fertilize & Amend":   "fertilize",                  # NEW B3
    # ── Method-disambiguated mappings (importer §7.4 logic) ──
    # "Weed"               → "hand_weed" (default; reclassify if Method=Flextine)
    # "Row Cover & Mulch"  → "net_row_cover" (default; reclassify if Sub-method=Mulch/Straw)
}
# Note: "Weed" and "Row Cover & Mulch" are NOT direct keys in this dict —
# their mapping happens in tend_overlay.py with Method/Sub-method inspection.
# Whitelist controls inclusion; this map controls task_type assignment.

# ---------------------------------------------------------------------------
# Israeli source Hebrew → crops.name_he (SFA-S003-P002-WP-C1 LOD400 §4.6)
# ---------------------------------------------------------------------------
IL_CROP_MAP: dict[str, str] = {
    "ארוגולה": "ארוגולה",
    "רוקט/אורגולה": "ארוגולה",
    "רוקט/ארוגולה": "ארוגולה",
    "אבטיח": "אבטיח",
    "אדום": "חסה",
    "איסברג": "חסה",
    "אלפלפא": "תלתן",  # alfalfa — not in baseline; will skip at DB lookup
    "אפונה": "אפונה",
    "ארטישוק": "ארטישוק",
    "ארטישוק (קנרס תר')": "ארטישוק",
    "ארטישוק\u00a0(קנרס תר')": "ארטישוק",
    "ארטישוק ירושלמי": "ארטישוק ירושלמי",
    "אספרגוס": "סלרי",  # closest baseline proxy
    "בוטנים": "שעועית",
    "בטטה": "בטטה",
    "במיה": "במיה",
    "בצל": "בצל",
    "בצל יבש": "בצל",
    "בצל ירוק": "בצל ירוק",
    "בצלים": "בצל",
    "בזיל": "בזיל",
    "בזיליקום": "בזיליקום",
    "בזיליקום (ריחן)": "בזיליקום",
    "ברוקולי": "ברוקולי",
    "גזר": "גזר",
    "גזר לבן": "גזר",
    "דלורית": "דלעת",
    "דלעת": "דלעת",
    "זוקיני": "קישוא",
    "חיטה": "חיטה",
    "חמניה": "חמניה",
    "חסה": "חסה",
    "חסה ערבית": "חסה",
    "חסה אייסברג": "חסה",
    "חציל": "חציל",
    "חריף": "פלפל",
    "כוסברה": "כוסברה",
    "כרוב": "כרוב",
    "כרוב אדום": "כרוב",
    "כרוב לבן": "כרוב",
    "כרוב ניצנים": "כרוב",
    "כרוב סיני": "כרוב",
    "כרובית": "כרובית",
    "כרישה": "כרישה",
    "כרישה (כרתי,לוף)": "כרישה",
    "כרישה\u00a0(כרתי,לוף)": "כרישה",
    "לבן": "חסה",
    "לוביה": "שעועית",
    "לימה": "שעועית",
    "לפת": "לפת",
    "מטפסת": "שעועית מטפסת",
    "מלון": "מלון",
    "מלפפון": "מלפפון",
    "מנגולד": "מנגולד",
    "מנגולד (סלק עלים)": "מנגולד",
    "מצרי": "חסה",
    "מתוק": "פלפל",
    "סילקה (מנגולד)": "מנגולד",
    "סילקה\u00a0(מנגולד)": "מנגולד",
    "סלק": "סלק",
    "סלק עלים": "מנגולד",
    "סלרי": "סלרי",
    "סלרי עלים": "סלרי",
    "סלרי עלים (כרפס)": "סלרי",
    "סלרי עלים\u00a0(כרפס)": "סלרי",
    "סלרי שורש": "סלרי",
    "סלרי שורש (כרפס)": "סלרי",
    "סלרי שורש\u00a0(כרפס)": "סלרי",
    "עגבניה": "עגבנייה",
    "עגבנית": "עגבנייה",
    "עגבנית צ'רי": "עגבניית שרי",
    "עולש (ציקוריה)": "ציקוריה",
    "עולש\u00a0(ציקוריה)": "ציקוריה",
    "עלים": "חסה",
    "פול": "פול",
    "פטרוזיליה": "פטרוזיליה",
    "פטרוזליה": "פטרוזיליה",
    "פלפל": "פלפל",
    "פלפל חריף": "פלפל",
    "פלפל מתוק": "פלפל",
    "ציקוריה": "ציקוריה",
    "צנון": "צנונית",
    "צנונית": "צנונית",
    "צנון/צנונית": "צנונית",
    "קולורבי": "קולורבי",
    "קולרבי": "קולורבי",
    "קייל": "קייל",
    "קישוא": "קישוא",
    "ראש": "חסה",
    "שום": "שום",
    "שומר": "שומר",
    "שעועית": "שעועית",
    "שעועית ירוקה": "שעועית",
    "שורש": "גזר",
    "תות שדה": "תות שדה",
    "תירס": "תירס",
    "תירס מתוק": "תירס",
    "תפוח אדמה": "תפוח אדמה",
    "תפוחי אדמה": "תפוח אדמה",
    'תפו"א': "תפוח אדמה",
    "תרד": "תרד",
    "תרד טורקי": "תרד",
    "תרד טורקי/בלאדי": "תרד",
    "תרד ניו-זילandi": "תרד ניו-זילנד",
    "תרד ניו-זילנד": "תרד ניו-זילנד",
    "אדממה": "אדממה",
    "ירוק": "חסה",
    "מסולסלת": "חסה",
    "שומשום": "שומשום",
    "סויה": "סויה",
    "חימצה (חומוס)": "חומוס",
    "חימצה\u00a0(חומוס)": "חומוס",
    "חומוס": "חומוס",
    "תבלינים": "תבלינים",
}


def resolve_il_crop(name_he: str) -> str | None:
    """Map a Hebrew crop label from Israeli sources to canonical crops.name_he."""
    key = (name_he or "").strip()
    if not key:
        return None
    if key in IL_CROP_MAP:
        return IL_CROP_MAP[key]
    normalized = key.replace("\u00a0", " ")
    if normalized in IL_CROP_MAP:
        return IL_CROP_MAP[normalized]
    return None


# ---------------------------------------------------------------------------
# English extension-source → crops.name_he (SFA-S003-P002-WP-C4 LOD400 §4)
# ---------------------------------------------------------------------------
EN_CROP_MAP: dict[str, str] = {
    **{k: v for k, v in TEND_CROP_MAP.items()},
    # Common extension aliases (singular/plural, shortened labels)
    "Tomato": "עגבנייה",
    "Tomatoes": "עגבנייה",
    "Pepper": "פלפל",
    "Peppers": "פלפל",
    "Sweet Pepper": "פלפל",
    "Hot Pepper": "פלפל",
    "Bean": "שעועית",
    "Beans": "שעועית",
    "Bush Bean": "שעועית",
    "Pole Bean": "שעועית",
    "Cucumber": "מלפפון",
    "Cucumbers": "מלפפון",
    "Squash": "קישוא",
    "Summer Squash": "קישוא",
    "Winter Squash": "דלעת",
    "Melon": "מלון",
    "Melons": "מלון",
    "Watermelon": "אבטיח",
    "Onion": "בצל",
    "Onions": "בצל",
    "Garlic": "שום",
    "Carrot": "גזר",
    "Carrots": "גזר",
    "Beet": "סלק",
    "Beets": "סלק",
    "Broccoli": "ברוקולי",
    "Cabbage": "כרוב",
    "Cauliflower": "כרובית",
    "Kale": "קייל",
    "Lettuce": "חסה",
    "Spinach": "תרד",
    "Swiss Chard": "מנגולד",
    "Chard": "מנגולד",
    "Eggplant": "חציל",
    "Pea": "אפונה",
    "Peas": "אפונה",
    "Radish": "צנונית",
    "Radishes": "צנונית",
    "Turnip": "לפת",
    "Turnips": "לפת",
    "Leek": "כרישה",
    "Leeks": "כרישה",
    "Celery": "סלרי",
    "Parsley": "פטרוזיליה",
    "Cilantro": "כוסברה",
    "Coriander": "כוסברה",
    "Dill": "שמיר",
    "Basil": "בזיל",
    "Mint": "נענע",
    "Sage": "מרווה",
    "Thyme": "טימין",
    "Arugula": "ארוגולה",
    "Rocket": "ארוגולה",
    "Okra": "במיה",
    "Asparagus": "סלרי",
    "Artichoke": "ארטישוק",
    "Potato": "תפוח אדמה",
    "Potatoes": "תפוח אדמה",
    "Sweet Potato": "בטטה",
    "Corn": "תירס",
    "Sweet Corn": "תירס",
    "Strawberry": "תות שדה",
    "Strawberries": "תות שדה",
    "Pak Choi": "פאק צ'וי",
    "Bok Choy": "פאק צ'וי",
    "Kohlrabi": "קולורבי",
    "Fennel": "שומר",
    "Ginger": "ג'ינג'ר",
    "Turmeric": "כורכום",
}


def resolve_en_crop(name_en: str) -> str | None:
    """Map an English crop label from web extension sources to canonical name_he."""
    key = (name_en or "").strip()
    if not key:
        return None
    if key in EN_CROP_MAP:
        return EN_CROP_MAP[key]
    lower = key.lower()
    for src, dst in EN_CROP_MAP.items():
        if src.lower() == lower:
            return dst
    return None
