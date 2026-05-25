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
    "Mesclun":            "עלי בייבי",
    "New Zealand Spinach": "תרד ניו-זילנד",
    "Salad Mix":          "עלי בייבי",
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
    "Zucchini":           "קישוא",   # cultivar of קישוא; cultivar-level distinction lives in crop_varieties
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

    # ─── BEGIN patch01 alias additions (2026-05-25) ───
    # Maps farm-specific JMF MasterClass workbook variants to the same
    # crops.name_he as the canonical baseline keys. After this patch,
    # ~42/50 live-workbook crops map cleanly; the remaining 8 require
    # new crops.name_he rows and are out-of-scope for patch01.
    # Maintenance rule: when a new variant appears in any future
    # JMF workbook edition, append here — NEVER branch on the
    # English label elsewhere in the codebase.

    # ── Typo / spelling variants ──
    "Brussel Sprouts":              "כרוב ניצנים",   # Brussels Sprouts (singular-l typo)
    "Raddish":                      "צנונית",       # Radishes (double-d typo)
    "Spinach TR":                   "תרד",          # Spinach (edition suffix)
    "Spinarch SD":                  "תרד",          # Spinach (edition typo + suffix)

    # ── Synonyms / alternative English names ──
    "Pak Choi":                     "פאק צ'וי",     # Bok Choy synonym (matches existing TEND_CROP_MAP value)
    "Coriander":                    "כוסברה",       # Cilantro (Coriander = same plant)
    "Swiss Chard":                  "מנגולד",       # Chard with explicit Swiss qualifier
    "Watermelon":                   "אבטיח",        # Watermelons singular
    "Potato":                       "תפוח אדמה",    # Potatoes singular
    "Fresh Carrots":                "גזר",          # Carrots with freshness qualifier

    # ── Storage / season qualifiers (same species, marketed differently) ──
    "Storage Onion":                "בצל",          # Onions for storage
    "Green Onion":                  "בצל ירוק",     # Scallions synonym (matches TEND_CROP_MAP)
    "Leek Storage":                 "כרישה",        # Leeks (storage cultivar)
    "Leek Summer":                  "כרישה",        # Leeks (summer cultivar)

    # ── Pepper variants ──
    "Bell Pepper":                  "פלפל",         # Peppers (bell variant — same species at crops.name_he level)
    "Hot Pepper":                   "פלפל חריף",    # Peppers (hot variant) — patch03: split from פלפל umbrella

    # ── Tomato variants (all Solanum lycopersicum at species level) ──
    "Roma Tomato":                  "עגבנייה",      # paste cultivar
    "Greenhouse Cherry Tomato":     "עגבניית שרי",  # protected-culture cherry — patch03: split from עגבנייה umbrella
    "Greenhouse Heirloom Tomato":   "עגבניות מורשת", # protected-culture heirloom — patch03: split from עגבנייה umbrella

    # ── Cucumber variants ──
    "Greenhouse English Cucumber":  "מלפפון",       # protected-culture long
    "Greenhouse Libanese Cucumber": "מלפפון חממה",  # protected-culture Lebanese — patch03: split from מלפפון umbrella (note: workbook spelling preserved)

    # ── Cabbage variants ──
    "Fall Cabbage":                 "כרוב",
    "Savoy Cabbage":                "כרוב",
    "Summer Cabbage":               "כרוב",
    "Chinese Cabbage":              "כרוב סיני",    # patch03: split from כרוב umbrella

    # ── Lettuce variants ──
    "Salanova Lettuce":             "חסה",
    "Sucrine":                      "חסה",

    # ── Brassica & misc variants ──
    "Baby kale":                    "עלי בייבי",    # patch03: split from קייל umbrella
    "Cauliflower / Romanesco":      "כרובית",       # workbook literal preserves the "/" (parser already substring-matches; this is the EXACT cell label)
    "Hakurei Turnip":               "לפת",
    "Mini Celery Root":             "סלרי שורש",
    "Mini Fennel":                  "שומר",
    "Winter Radish":                "צנונית",

    # ── Field-qualifier variants (preserved workbook literals — no parser-side normalization) ──
    "Eggplant  (Feld)":             "חציל",         # workbook literal: double space + (Feld) field qualifier. See §4 AC-04.1 rationale for why this is a literal alias rather than a parser change.
    # ─── END patch01 alias additions ───
}
# Total: 86 entries (52 baseline + 34 patch01 aliases). Maintenance rule: when a new JMF MasterClass edition
# adds or renames a crop, append/edit an entry here only — never branch on
# JMF names elsewhere in the codebase. On runtime miss (JMF row whose
# English label is not a key), the importer logs WARN with the unmapped
# label and skips that row (same convention as TEND_CROP_MAP miss handling
# in tend.py). Test AC-01 enforces `len(JMF_CROP_MAP) == 86`.

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
