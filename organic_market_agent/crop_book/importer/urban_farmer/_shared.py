"""Shared helpers for urban_farmer importers (Curtis Stone — WP-C3)."""

from __future__ import annotations

from pathlib import Path

from organic_market_agent.crop_book.importer.israeli._shared import ImportSummary  # noqa: F401

_REPO_ROOT = Path(__file__).resolve().parents[4]
URBAN_FARMER_DIR = _REPO_ROOT / "data" / "external_sources" / "urban_farmer"
CURTIS_OCR_DIR = _REPO_ROOT / "data" / "external_sources" / "extracted" / "curtis_ocr"

# Curtis Stone English crop name → canonical Hebrew (IL DB name)
CURTIS_CROP_MAP: dict[str, str] = {
    "Arugula": "ארוגולה",
    "Basil": "בזיל",
    "Beet Greens": "סלק",         # closest match in DB
    "Broccoli": "ברוקולי",
    "Carrots (baby)": "גזר",
    "Hakurei": "לפת",             # Hakurei turnip
    "Kale": "קייל",
    "Lettuce (Salanova)": "חסה",
    "Lettuce Mix": "חסה",
    "Mustard": "ארוגולה",         # mustard greens — closest substitute
    "Peppers (Interplanted)": "פלפל",
    "Radish": "צנונית",
    "Red Russian Kale": "קייל",
    "Spinach": "תרד",
    "Tatsoi": "חסה",              # Asian green — treat as leafy
    "Tomatoes (Cherry)": "עגבנייה",
}
