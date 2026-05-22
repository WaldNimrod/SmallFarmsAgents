"""Canonical entity registry — Python-owned SSoT for the SPA entity data.

Imported by CropBookPublisher at publish time and embedded in the data JSON.
No JS file parsing. No regex. No eval.

F-190-WP004-01 remediation: Python module replaces the JS-file extraction approach.
"""

ENTITY_REGISTRY: dict = {
    "version": "1.0.0",
    "type_labels": {
        "pest":      "מזיק",
        "disease":   "מחלה",
        "equip":     "ציוד",
        "input":     "תשומה",
        "technique": "טכניקה",
        "crop":      "גידול",
    },
    "entities": {
        "pest": {
            "diamondback-moth": {"nameHe": "עש יהלום",      "nameEn": "Diamondback moth"},
            "aphid":            {"nameHe": "כנימת עלים",    "nameEn": "Aphid"},
            "whitefly":         {"nameHe": "זבוב לבן",      "nameEn": "Whitefly"},
            "spider-mite":      {"nameHe": "קרדית עכביש",   "nameEn": "Spider mite"},
            "flea-beetle":      {"nameHe": "חיפושית פרעוש", "nameEn": "Flea beetle"},
            "thrips":           {"nameHe": "טריפס",          "nameEn": "Thrips"},
            "caterpillar":      {"nameHe": "זחל",            "nameEn": "Caterpillar"},
        },
        "disease": {
            "downy-mildew":   {"nameHe": "אבקת שפם",    "nameEn": "Downy mildew"},
            "powdery-mildew": {"nameHe": "אבקת אמיתית", "nameEn": "Powdery mildew"},
            "botrytis":       {"nameHe": "בוטריטיס",    "nameEn": "Botrytis"},
            "fusarium":       {"nameHe": "פוזריום",      "nameEn": "Fusarium"},
            "alternaria":     {"nameHe": "אלטרנריה",    "nameEn": "Alternaria"},
        },
        "equip": {
            "jang-jp1":   {"nameHe": "מזרע Jang JP-1", "nameEn": "Jang JP-1 seeder"},
            "paper-pot":  {"nameHe": "פפר פוט",         "nameEn": "Paper pot transplanter"},
            "broadfork":  {"nameHe": "ברודפורק",        "nameEn": "Broadfork"},
        },
        "input": {
            "compost":          {"nameHe": "קומפוסט",       "nameEn": "Compost"},
            "fish-emulsion":    {"nameHe": "תמצית דגים",    "nameEn": "Fish emulsion"},
            "insect-netting":   {"nameHe": "רשת חרקים",     "nameEn": "Insect netting"},
            "row-cover":        {"nameHe": "כיסוי שורה",    "nameEn": "Row cover"},
            "drip-irrigation":  {"nameHe": "השקיה בטפטוף", "nameEn": "Drip irrigation"},
        },
        "technique": {
            "succession-planting": {"nameHe": "זריעת רצף",   "nameEn": "Succession planting"},
            "transplanting":       {"nameHe": "שתילה",        "nameEn": "Transplanting"},
            "direct-seeding":      {"nameHe": "זריעה ישירה", "nameEn": "Direct seeding"},
            "grafting":            {"nameHe": "הרכבה",        "nameEn": "Grafting"},
            "pinching":            {"nameHe": "קיטום",        "nameEn": "Pinching"},
            "soil-blocking":       {"nameHe": "בלוק אדמה",   "nameEn": "Soil blocking"},
        },
        "crop": {
            "arugula": {"nameHe": "ארוגולה", "nameEn": "Arugula"},
            "tomato":  {"nameHe": "עגבנייה", "nameEn": "Tomato"},
            "basil":   {"nameHe": "בזיל",    "nameEn": "Basil"},
            "lettuce": {"nameHe": "חסה",     "nameEn": "Lettuce"},
        },
    },
}

_REQUIRED_TOP_KEYS = {"version", "type_labels", "entities"}
_REQUIRED_ENTITY_TYPES = {"pest", "disease", "equip", "input", "technique", "crop"}


def validate_entity_registry(registry: dict) -> None:
    """Validate ENTITY_REGISTRY schema. Raises ValueError on failure."""
    missing_top = _REQUIRED_TOP_KEYS - set(registry.keys())
    if missing_top:
        raise ValueError(f"ENTITY_REGISTRY missing top-level keys: {missing_top}")
    if not isinstance(registry.get("entities"), dict):
        raise ValueError("ENTITY_REGISTRY['entities'] must be a dict")
    missing_types = _REQUIRED_ENTITY_TYPES - set(registry["entities"].keys())
    if missing_types:
        raise ValueError(f"ENTITY_REGISTRY['entities'] missing entity types: {missing_types}")
