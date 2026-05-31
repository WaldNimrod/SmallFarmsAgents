"""ספר גידולים — Flask Blueprint: 3 read-only routes."""
from __future__ import annotations

from flask import Blueprint, abort, g, jsonify, render_template, request
from sqlalchemy.orm import joinedload

from organic_market_agent.crop_book.models import (
    Crop,
    CropConversionGroup,
    CropVariety,
    CropVarietySourceValue,
)

crop_book_bp = Blueprint(
    "crop_book",
    __name__,
    template_folder="templates",
    url_prefix="/crop-book",
)

# ---------------------------------------------------------------------------
# Category display mapping (DB value → Hebrew label)
# ---------------------------------------------------------------------------
CATEGORY_LABELS: dict[str, str] = {
    "vegetables": "ירקות",
    "herbs": "עשבי תיבול",
    "baby": "בייבי / מיקרו",
    "legumes": "קטניות",
    "fruits": "פירות",
    "fruit_trees": "עצי פרי",
    "grains": "דגנים",
    "cover_crops": "גידולי כיסוי",
}

# Ordered list for tabs (value, label)
CATEGORY_TABS: list[tuple[str, str]] = [
    ("", "כל הגידולים"),
    ("vegetables", "ירקות"),
    ("herbs", "עשבי תיבול"),
    ("fruits", "פירות"),
    ("legumes", "קטניות"),
    ("fruit_trees", "עצי פרי"),
    ("grains", "דגנים"),
    ("cover_crops", "גידולי כיסוי"),
]

# Season token mapping (substring match → display)
SEASON_TOKENS: list[tuple[list[str], str, str]] = [
    (["קיץ", "summer"], "summer", "☀️"),
    (["אביב", "spring"], "spring", "🌸"),
    (["חורף", "winter"], "winter", "🌧"),
    (["סתיו", "fall", "autumn"], "fall", "💨"),
]


def _detect_seasons(planting_season: str | None) -> dict[str, bool]:
    """Return dict of season_key → bool (True = active)."""
    text = (planting_season or "").lower()
    result: dict[str, bool] = {}
    for tokens, key, _emoji in SEASON_TOKENS:
        result[key] = any(t.lower() in text for t in tokens)
    return result


def _variety_attr(variety: CropVariety | None, attribute_name: str) -> str | None:
    """Read value_canonical from crop_attribute for a given attribute_name.

    WP-CB-MIG: categoricals (planting_season, etc.) moved from CropVariety columns
    to the crop_attribute table. Returns None gracefully if absent.
    """
    if variety is None:
        return None
    for attr in (variety.attributes or []):
        if attr.attribute_name == attribute_name:
            return attr.value_canonical
    return None


def _variety_enrichment(variety: CropVariety | None, field_name: str) -> int | None:
    """Read value_best (as int) from crop_field_enrichment for a given field_name.

    WP-CB-MIG: numeric facts (days_to_maturity, harvest_window_max_days, etc.) moved
    from CropVariety columns to crop_field_enrichment. Returns None gracefully if absent.
    """
    if variety is None:
        return None
    for enr in (variety.enrichments or []):
        if enr.field_name == field_name:
            return int(enr.value_best) if enr.value_best is not None else None
    return None


def _crop_to_dict(crop: Crop) -> dict:
    """Serialize a Crop (with default_variety) to JSON-safe dict for /api/crops."""
    default_var: CropVariety | None = next(
        (v for v in (crop.varieties or []) if v.is_default), None
    ) or (crop.varieties[0] if crop.varieties else None)

    # WP-CB-MIG: planting_season moved to crop_attribute table
    planting_season = _variety_attr(default_var, "planting_season")
    seasons_active = _detect_seasons(planting_season)
    active_season_keys = [k for k, v in seasons_active.items() if v]

    # WP-CB-MIG: days_to_maturity moved to crop_field_enrichment table
    dtm_min = _variety_enrichment(default_var, "days_to_maturity")

    return {
        "id": crop.id,
        "name_he": crop.name_he,
        "name_en": crop.name_en or "",
        "scientific_name": crop.scientific_name or "",
        "family_scientific": crop.family.scientific_name if crop.family else "",
        "family_he": crop.family.name_he if crop.family else "",
        "category": crop.category,
        "category_label": CATEGORY_LABELS.get(crop.category, crop.category),
        "harvest_unit_default": crop.harvest_unit_default or "",
        "variety_count": len(crop.varieties) if crop.varieties else 0,
        "seasons": active_season_keys,
        "dtm_min": dtm_min,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@crop_book_bp.route("/")
def index():
    """Main crop grid with category tabs and search bar."""
    session = g.db_session
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()

    query = (
        session.query(Crop)
        .options(
            joinedload(Crop.family),
            joinedload(Crop.varieties),
        )
    )

    if category:
        query = query.filter(Crop.category == category)

    if q:
        like = f"%{q}%"
        query = query.filter(
            Crop.name_he.ilike(like)
            | Crop.name_en.ilike(like)
            | Crop.scientific_name.ilike(like)
        )

    crops = query.order_by(Crop.name_he).all()

    return render_template(
        "crop_book/index.html",
        crops=crops,
        category_tabs=CATEGORY_TABS,
        category_labels=CATEGORY_LABELS,
        active_category=category,
        search_query=q,
        season_tokens=SEASON_TOKENS,
        detect_seasons=_detect_seasons,
    )


@crop_book_bp.route("/<int:crop_id>/")
def crop_detail(crop_id: int):
    """Full crop detail page with 8 tabs."""
    session = g.db_session

    crop = (
        session.query(Crop)
        .options(
            joinedload(Crop.family),
            joinedload(Crop.varieties).joinedload(CropVariety.source_values),
            joinedload(Crop.conversion_group).joinedload(
                CropConversionGroup.conversions
            ),
        )
        .filter(Crop.id == crop_id)
        .one_or_none()
    )

    if crop is None:
        abort(404)

    # Determine default variety (first is_default=True, else first variety)
    default_var: CropVariety | None = next(
        (v for v in crop.varieties if v.is_default), None
    ) or (crop.varieties[0] if crop.varieties else None)

    # Check if ציוד tab should be shown (at least one seeder field non-null)
    has_seeder = any(
        v.seeder or v.seeder_front_gear or v.seeder_rear_gear or v.seeder_roller_plate
        for v in crop.varieties
    )

    # Collect source values for default variety (for כלכלה + מקורות tabs)
    price_source_values: list[CropVarietySourceValue] = []
    if default_var:
        price_source_values = [
            sv for sv in default_var.source_values
            if sv.field_name == "documented_price"
        ]

    # All source values for מקורות tab grouped by source
    sources_by_field: dict[str, dict[str, str]] = {}
    all_sources: set[str] = set()
    if default_var:
        for sv in default_var.source_values:
            all_sources.add(sv.source)
            if sv.field_name not in sources_by_field:
                sources_by_field[sv.field_name] = {}
            sources_by_field[sv.field_name][sv.source] = sv.value_text or (
                str(sv.value_numeric) if sv.value_numeric is not None else "—"
            )
    sorted_sources = sorted(all_sources)

    # Season detection for default variety
    # WP-CB-MIG: planting_season moved to crop_attribute table
    planting_season = _variety_attr(default_var, "planting_season")
    seasons = _detect_seasons(planting_season)

    # Timeline calculations
    # WP-CB-MIG: days_to_maturity, harvest_window_max_days, days_in_gh_total moved
    # to crop_field_enrichment (canonical field names: days_to_maturity,
    # harvest_window_max_days, days_in_nursery)
    dtm = _variety_enrichment(default_var, "days_to_maturity") or 0
    hw_max = _variety_enrichment(default_var, "harvest_window_max_days") or 0
    gh_total = _variety_enrichment(default_var, "days_in_nursery") or 0
    timeline_data = None
    if default_var and (dtm or hw_max):
        total_days = dtm + hw_max
        total_weeks = max(1, -(-hw_max // 7))  # ruler: harvest_window only (LOD400 §3.9)

        def pct(days: int) -> float:
            return round(100.0 * days / max(total_days, 1), 1)

        phases = []
        if gh_total > 0:
            phases.append({"label": "הכנה / חממה", "color": "#78909c", "pct": pct(gh_total)})
        grow_days = dtm - gh_total
        if grow_days > 0:
            phases.append({"label": "גידול", "color": "#43a047", "pct": pct(grow_days)})
        if hw_max > 0:
            phases.append({"label": "חלון קציר", "color": "#fb8c00", "pct": pct(hw_max)})

        timeline_data = {
            "total_weeks": total_weeks,
            "phases": phases,
            "dtm": dtm,
            "hw_max": hw_max,
        }

    return render_template(
        "crop_book/crop.html",
        crop=crop,
        default_var=default_var,
        has_seeder=has_seeder,
        price_source_values=price_source_values,
        sources_by_field=sources_by_field,
        sorted_sources=sorted_sources,
        seasons=seasons,
        season_tokens=SEASON_TOKENS,
        timeline_data=timeline_data,
        category_labels=CATEGORY_LABELS,
        detect_seasons=_detect_seasons,
    )


@crop_book_bp.route("/api/crops")
def api_crops():
    """JSON endpoint for client-side search/filter."""
    session = g.db_session

    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    seasons = request.args.getlist("season")
    dtm_max_str = request.args.get("dtm_max", "").strip()

    from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment
    from organic_market_agent.crop_book.attribute_models import CropAttribute as _CropAttr

    query = (
        session.query(Crop)
        .options(
            joinedload(Crop.family),
            # WP-CB-MIG: load attributes + enrichments (categoricals + numeric facts
            # moved out of CropVariety columns into these tables)
            joinedload(Crop.varieties).joinedload(CropVariety.attributes),
            joinedload(Crop.varieties).joinedload(CropVariety.enrichments),
        )
    )

    if category:
        query = query.filter(Crop.category == category)

    if q:
        like = f"%{q}%"
        query = query.filter(
            Crop.name_he.ilike(like)
            | Crop.name_en.ilike(like)
            | Crop.scientific_name.ilike(like)
        )

    crops = query.order_by(Crop.name_he).all()

    # Apply Python-side filters that require variety data
    results = []
    for crop in crops:
        default_var: CropVariety | None = next(
            (v for v in (crop.varieties or []) if v.is_default), None
        ) or (crop.varieties[0] if crop.varieties else None)

        # DTM filter
        # WP-CB-MIG: days_to_maturity moved to crop_field_enrichment
        if dtm_max_str:
            try:
                dtm_max = int(dtm_max_str)
                dtm = _variety_enrichment(default_var, "days_to_maturity")
                if dtm is None or dtm > dtm_max:
                    continue
            except ValueError:
                pass

        # Season filter — OR logic: crop must match at least one selected season
        # WP-CB-MIG: planting_season moved to crop_attribute table
        if seasons:
            season_map = {
                "summer": ["קיץ", "summer"],
                "spring": ["אביב", "spring"],
                "winter": ["חורף", "winter"],
                "fall": ["סתיו", "fall", "autumn"],
            }
            planting = (_variety_attr(default_var, "planting_season") or "")

            def _matches_any_season(sel_seasons: list[str]) -> bool:
                for s in sel_seasons:
                    tokens = season_map.get(s, [s])
                    if any(t.lower() in planting.lower() for t in tokens):
                        return True
                return False

            if not _matches_any_season(seasons):
                continue

        results.append(_crop_to_dict(crop))

    return jsonify(results)
