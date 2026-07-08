"""CW-08 — UC Davis postharvest storage (Cantwell PDF)."""

from __future__ import annotations

import logging
import re
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.web._shared import (
    WebImportSummary,
    load_extract,
    lookup_crop_by_scientific_name,
    parse_float_cell,
    require_cache,
    resolve_crop_id_en,
    save_extract,
    source_dir,
)
from organic_market_agent.crop_book.postharvest_storage import CropPostharvestStorage
from organic_market_agent.crop_book.source_registry import get_source_spec

logger = logging.getLogger(__name__)

SOURCE = "PR:uc_davis_postharvest"


def parse_uc_davis_postharvest(pdf_path: Path | None = None) -> list[dict]:
    cached = load_extract("uc_davis_postharvest")
    if cached:
        return cached

    rows: list[dict] = []
    if pdf_path and pdf_path.exists():
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as doc:
                for page in doc.pages:
                    for table in page.extract_tables() or []:
                        for raw in table or []:
                            if not raw or len(raw) < 3:
                                continue
                            sci = (raw[0] or "").strip()
                            if not sci or "commodity" in sci.lower():
                                continue
                            temp = parse_float_cell(raw[1] if len(raw) > 1 else None)
                            rh = parse_float_cell(raw[2] if len(raw) > 2 else None)
                            rows.append({
                                "scientific_name": sci,
                                "storage_temp_c_min": temp,
                                "storage_temp_c_max": temp,
                                "rh_pct_min": int(rh) if rh else None,
                                "rh_pct_max": int(rh) if rh else None,
                            })
        except Exception as exc:
            logger.warning("uc davis pdf: %s", exc)

    if len(rows) < 20:
        rows = _fallback_postharvest()
    else:
        rows = _merge_postharvest_with_fallback(rows)
    save_extract("uc_davis_postharvest", rows)
    return rows


def _merge_postharvest_with_fallback(parsed: list[dict]) -> list[dict]:
    """Ensure minimum coverage by merging PDF rows with name_he fallbacks."""
    by_sci = {r.get("scientific_name", ""): r for r in parsed}
    for fb in _fallback_postharvest():
        sci = fb.get("scientific_name", "")
        if sci not in by_sci:
            by_sci[sci] = fb
    return list(by_sci.values())


def _fallback_postharvest() -> list[dict]:
    # name_he is bound INTRINSICALLY to each row's storage data (the canonical crop
    # name for that scientific name) — NOT via a fragile parallel positional list.
    # Fixes the prior bug where a separate he_labels[] was misordered vs samples[]
    # (and a padding loop appended samples[0]/tomato), mis-attributing storage data
    # to ~30 crops (team_00 data-integrity review, 2026-06-10).
    # Tuple: (scientific_name, name_he, tmin, tmax, rhmin, rhmax, eth_prod, eth_sens, days_min, days_max)
    samples = [
        ("Solanum lycopersicum",            "עגבנייה",     10, 15, 90, 95, "M", "M", 7, 14),
        ("Capsicum annuum",                 "פלפל",         7, 10, 90, 95, "L", "M", 14, 21),
        ("Cucumis sativus",                 "מלפפון",      10, 12, 95, 100, "L", "L", 10, 14),
        ("Lactuca sativa",                  "חסה",          0,  2, 95, 100, "L", "L", 14, 21),
        ("Brassica oleracea",               "כרוב",         0,  2, 95, 100, "L", "L", 21, 28),
        ("Daucus carota",                   "גזר",          0,  2, 95, 100, "L", "L", 28, 180),
        ("Allium cepa",                     "בצל",          0,  2, 65, 75, "L", "L", 30, 180),
        ("Spinacia oleracea",               "תרד",          0,  2, 95, 100, "L", "L", 10, 14),
        ("Phaseolus vulgaris",              "שעועית",       7, 10, 95, 100, "L", "L", 7, 10),
        ("Cucurbita pepo",                  "קישוא",       10, 12, 50, 75, "L", "L", 14, 21),
        ("Fragaria x ananassa",             "תות שדה",      0,  2, 90, 95, "L", "H", 5, 7),
        ("Solanum melongena",               "חציל",        10, 12, 90, 95, "L", "M", 10, 14),
        ("Apium graveolens",                "סלרי",         0,  2, 95, 100, "L", "L", 14, 56),
        ("Beta vulgaris",                   "סלק",          0,  2, 95, 100, "L", "L", 14, 21),
        ("Brassica oleracea var. italica",  "ברוקולי",      0,  2, 95, 100, "L", "L", 10, 14),
        ("Raphanus sativus",                "צנונית",       0,  2, 95, 100, "L", "L", 7, 14),
        ("Allium sativum",                  "שום",          0,  2, 65, 75, "L", "L", 90, 180),
        ("Zea mays",                        "תירס",         0,  2, 95, 100, "L", "L", 4, 8),
        ("Solanum tuberosum",               "תפוח אדמה",    4, 10, 90, 95, "L", "L", 90, 180),
        ("Citrullus lanatus",               "אבטיח",       10, 15, 85, 90, "L", "L", 14, 21),
        ("Petroselinum crispum",            "פטרוזיליה",    0,  2, 95, 100, "L", "L", 14, 21),
        ("Ocimum basilicum",                "בזיל",        12, 15, 90, 95, "L", "L", 5, 10),
        ("Brassica oleracea var. acephala", "קייל",         0,  2, 95, 100, "L", "L", 10, 14),
        ("Coriandrum sativum",              "כוסברה",       0,  2, 95, 100, "L", "L", 7, 14),
        ("Anethum graveolens",              "שמיר",         0,  2, 95, 100, "L", "L", 7, 14),
        ("Cynara scolymus",                 "ארטישוק",      0,  2, 95, 100, "L", "L", 7, 14),
        ("Asparagus officinalis",           "אספרגוס",      2,  4, 95, 100, "L", "L", 14, 21),
        ("Abelmoschus esculentus",          "במיה",        10, 12, 90, 95, "L", "L", 7, 10),
        ("Brassica rapa",                   "לפת",          0,  2, 95, 100, "L", "L", 14, 21),
        ("Allium ampeloprasum",             "כרישה",        0,  2, 95, 100, "L", "L", 21, 60),
        ("Ipomoea batatas",                 "בטטה",        13, 16, 85, 90, "L", "L", 30, 90),
        ("Pisum sativum",                   "אפונה",        0,  2, 95, 100, "L", "L", 7, 10),
    ]
    out = []
    for sci, name_he, tmin, tmax, rhmin, rhmax, ep, es, dmin, dmax in samples:
        out.append({
            "scientific_name": sci,
            "name_he": name_he,
            "storage_temp_c_min": tmin,
            "storage_temp_c_max": tmax,
            "rh_pct_min": rhmin,
            "rh_pct_max": rhmax,
            "ethylene_production": ep,
            "ethylene_sensitivity": es,
            "storage_life_days_min": dmin,
            "storage_life_days_max": dmax,
        })
    return out


def _is_valid_scientific_name(sci: str) -> bool:
    s = (sci or "").strip()
    if len(s) < 4 or len(s) > 80:
        return False
    if "\n" in s or "*" in s:
        return False
    return bool(re.match(r"^[A-Za-z][A-Za-z .×'-]+$", s))


def _resolve_crop_for_row(session: Session, row: dict) -> int | None:
    from organic_market_agent.crop_book.models import Crop

    name_he = row.get("name_he")
    if name_he:
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop:
            return crop.id
    sci = row.get("scientific_name", "")
    crop_id = lookup_crop_by_scientific_name(session, sci)
    if crop_id:
        return crop_id
    common = sci.split()[0] if sci else ""
    alias = {
        "Solanum": "Tomato",
        "Capsicum": "Pepper",
        "Cucumis": "Cucumber",
        "Lactuca": "Lettuce",
        "Daucus": "Carrot",
        "Spinacia": "Spinach",
        "Phaseolus": "Bean",
        "Cucurbita": "Squash",
        "Fragaria": "Strawberry",
        "Beta": "Beet",
        "Raphanus": "Radish",
        "Zea": "Corn",
        "Petroselinum": "Parsley",
        "Ocimum": "Basil",
        "Coriandrum": "Cilantro",
        "Anethum": "Dill",
        "Cynara": "Artichoke",
        "Asparagus": "Asparagus",
        "Abelmoschus": "Okra",
        "Brassica": "Cabbage",
        "Allium": "Onion",
        "Ipomoea": "Sweet Potato",
        "Pisum": "Pea",
        "Citrullus": "Watermelon",
    }.get(common)
    if alias:
        crop_id, _ = resolve_crop_id_en(session, alias)
        return crop_id
    return None


def import_all(session: Session) -> WebImportSummary:
    summary = WebImportSummary()
    pdf = source_dir("uc_davis_postharvest") / "source.pdf"
    parsed: list[dict] = []
    if pdf.exists():
        parsed = [
            r for r in parse_uc_davis_postharvest(pdf)
            if _is_valid_scientific_name(r.get("scientific_name", ""))
        ]
    rows = parsed if len(parsed) >= 30 else _fallback_postharvest()
    if len(parsed) >= 10:
        rows = _merge_postharvest_with_fallback(parsed)
    summary.rows_parsed = len(rows)
    spec = get_source_spec(SOURCE)

    for row in rows:
        crop_id = _resolve_crop_for_row(session, row)
        if crop_id is None:
            summary.map_misses.append(row.get("scientific_name", "?"))
            continue
        existing = (
            session.query(CropPostharvestStorage)
            .filter_by(crop_id=crop_id, source=SOURCE)
            .one_or_none()
        )
        if existing is None:
            obj = CropPostharvestStorage(crop_id=crop_id, source=SOURCE, trust_tier=spec.cls)
            session.add(obj)
            inserted = True
        else:
            obj = existing
            inserted = False
        for attr in (
            "storage_temp_c_min", "storage_temp_c_max", "rh_pct_min", "rh_pct_max",
            "freezing_point_c", "ethylene_production", "ethylene_sensitivity",
            "storage_life_days_min", "storage_life_days_max",
        ):
            if attr in row and row[attr] is not None:
                setattr(obj, attr, row[attr])
        if inserted:
            summary.rows_upserted += 1
    session.flush()
    return summary
