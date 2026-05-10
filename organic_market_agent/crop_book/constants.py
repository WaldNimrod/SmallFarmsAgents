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
