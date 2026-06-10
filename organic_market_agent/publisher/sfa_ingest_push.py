"""SFA delivery-tier publisher push (WP-4 light).

Reads canonical Postgres on waldhomeserver (or local dev mirror), transforms
rows into the ingest API contract (documentation/03-data-and-schema/sfa-mysql-mirror.md),
HMAC-SHA256-signs the payload, POSTs to ``$SFA_INGEST_URL``.

Replaces ``wp_upload.py`` for the new delivery tier (sfa.nimrod.bio).

Env (from ``.env``):
- ``DATABASE_URL`` — Postgres canonical
- ``SFA_INGEST_URL`` — e.g. ``https://sfa.nimrod.bio/api/v1/ingest``
- ``SFA_INGEST_HMAC_SECRET`` — base64 32-byte shared secret (must match server)

Usage::

    python -m organic_market_agent.publisher.sfa_ingest_push
    python -m organic_market_agent.publisher.sfa_ingest_push --table crops --dry-run
    python -m organic_market_agent.publisher.sfa_ingest_push --limit 5

Idempotency: a per-push key ``"{table}_{YYYYMMDD-HHMMSS}_{seq}"`` is generated;
re-running with the same key (same minute, same table) returns ``{duplicate: true}``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import hmac
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

from organic_market_agent.crop_book.canon.field_registry import FIELD_REGISTRY

logger = logging.getLogger("sfa_ingest_push")

# ---------------------------------------------------------------------------


@dataclass
class PushConfig:
    db_url: str
    ingest_url: str
    hmac_secret: str
    timeout_s: int = 30
    batch_size: int = 50  # rows per POST


def _load_config() -> PushConfig:
    load_dotenv()
    missing = [
        k for k in ("DATABASE_URL", "SFA_INGEST_URL", "SFA_INGEST_HMAC_SECRET")
        if not os.environ.get(k)
    ]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")
    return PushConfig(
        db_url=os.environ["DATABASE_URL"],
        ingest_url=os.environ["SFA_INGEST_URL"],
        hmac_secret=os.environ["SFA_INGEST_HMAC_SECRET"],
    )


# ---------------------------------------------------------------------------
# Transformers — Postgres canonical → MySQL ingest payload
# ---------------------------------------------------------------------------


def _fetch_crops(conn) -> list[dict[str, Any]]:
    """One row per crop. payload_json carries everything not at top-level."""
    sql = """
        SELECT c.id, c.name_he, c.name_en, c.scientific_name,
               c.family_id, f.name_he AS family_name_he,
               f.scientific_name AS family_scientific_name,
               c.category, c.growth_cycle, c.harvest_unit_default,
               c.first_fruit_year, c.description, c.oma_product_id
        FROM crops c
        LEFT JOIN crop_families f ON f.id = c.family_id
        ORDER BY c.id
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    crops = cur.fetchall()

    # Aggregate variety DTM ranges to populate dtm_min/dtm_max on crops.
    # days_to_maturity was DROPPED from crop_varieties by migration 059 — it is now a
    # T1 reconciled fact in crop_field_enrichment (Canon §7.1). Read it from there.
    var_sql = """
        SELECT cv.crop_id,
               MIN(NULLIF(cfe.value_best, 0))::int AS dtm_min,
               MAX(NULLIF(cfe.value_best, 0))::int AS dtm_max,
               COUNT(DISTINCT cv.id) AS variety_count
        FROM crop_varieties cv
        LEFT JOIN crop_field_enrichment cfe
          ON cfe.variety_id = cv.id AND cfe.field_name = 'days_to_maturity'
        GROUP BY cv.crop_id
    """
    cur.execute(var_sql)
    dtm_by_crop = {r["crop_id"]: r for r in cur.fetchall()}

    # --- bulk enrichment queries (one per table, grouped by crop_id) ---

    # planting calendar
    cur.execute("""
        SELECT crop_id, activity_type, season, region,
               month_jan, month_feb, month_mar, month_apr,
               month_may, month_jun, month_jul, month_aug,
               month_sep, month_oct, month_nov, month_dec, notes
        FROM crop_planting_calendar
        ORDER BY crop_id, id
    """)
    calendar_by_crop: dict[int, list[dict[str, Any]]] = {}
    for row in cur.fetchall():
        cid = row["crop_id"]
        calendar_by_crop.setdefault(cid, []).append({
            "activity_type": row["activity_type"],
            "season": row["season"],
            "region": row["region"],
            "months": [
                bool(row["month_jan"]), bool(row["month_feb"]), bool(row["month_mar"]),
                bool(row["month_apr"]), bool(row["month_may"]), bool(row["month_jun"]),
                bool(row["month_jul"]), bool(row["month_aug"]), bool(row["month_sep"]),
                bool(row["month_oct"]), bool(row["month_nov"]), bool(row["month_dec"]),
            ],
            "notes": row["notes"],
        })

    # agronomy: crop-level median via PERCENTILE_CONT (one query for all crops)
    agronomy_whitelist_sql = ",".join(f"'{f}'" for f in _AGRONOMY_FIELD_WHITELIST)
    cur.execute(f"""
        SELECT cv.crop_id,
               cfe.field_name,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cfe.value_best) AS median_val
        FROM crop_varieties cv
        JOIN crop_field_enrichment cfe ON cfe.variety_id = cv.id
        WHERE cfe.field_name IN ({agronomy_whitelist_sql})
          AND cfe.value_best IS NOT NULL
        GROUP BY cv.crop_id, cfe.field_name
    """)
    agronomy_by_crop: dict[int, dict[str, float]] = {}
    for row in cur.fetchall():
        cid = row["crop_id"]
        agronomy_by_crop.setdefault(cid, {})[row["field_name"]] = float(row["median_val"])

    # harvest stats
    cur.execute("""
        SELECT crop_id, season, year,
               first_harvest_week, peak_harvest_week, last_harvest_week,
               yield_per_bed_min, yield_per_bed_median, yield_per_bed_max,
               yield_unit
        FROM crop_harvest_stats
        ORDER BY crop_id, year, season
    """)
    harvest_by_crop: dict[int, list[dict[str, Any]]] = {}
    for row in cur.fetchall():
        cid = row["crop_id"]
        entry: dict[str, Any] = {
            "season": row["season"],
            "year": row["year"],
            "weeks": {
                "first": row["first_harvest_week"],
                "peak": row["peak_harvest_week"],
                "last": row["last_harvest_week"],
            },
            "yield_per_bed": {
                "min": float(row["yield_per_bed_min"]) if row["yield_per_bed_min"] is not None else None,
                "median": float(row["yield_per_bed_median"]) if row["yield_per_bed_median"] is not None else None,
                "max": float(row["yield_per_bed_max"]) if row["yield_per_bed_max"] is not None else None,
            },
            "unit": row["yield_unit"],
        }
        harvest_by_crop.setdefault(cid, []).append(entry)

    # postharvest storage (one representative row per crop — first by id)
    cur.execute("""
        SELECT DISTINCT ON (crop_id)
               crop_id,
               storage_temp_c_min, storage_temp_c_max,
               rh_pct_min, rh_pct_max,
               ethylene_production, ethylene_sensitivity,
               storage_life_days_min, storage_life_days_max,
               notes
        FROM crop_postharvest_storage
        ORDER BY crop_id, id
    """)
    storage_by_crop: dict[int, dict[str, Any]] = {}
    for row in cur.fetchall():
        storage_by_crop[row["crop_id"]] = {
            "temp": {
                "min": float(row["storage_temp_c_min"]) if row["storage_temp_c_min"] is not None else None,
                "max": float(row["storage_temp_c_max"]) if row["storage_temp_c_max"] is not None else None,
            },
            "rh": {
                "min": row["rh_pct_min"],
                "max": row["rh_pct_max"],
            },
            "ethylene_production": row["ethylene_production"],
            "ethylene_sensitivity": row["ethylene_sensitivity"],
            "life_days": {
                "min": row["storage_life_days_min"],
                "max": row["storage_life_days_max"],
            },
            "notes": row["notes"],
        }

    # companion matrix — fetch all pairs + resolve names in one join
    cur.execute("""
        SELECT cm.crop_a_id, cm.crop_b_id, cm.compatibility, cm.notes,
               ca.name_he AS a_name_he, ca.name_en AS a_name_en,
               cb.name_he AS b_name_he, cb.name_en AS b_name_en
        FROM crop_companion_matrix cm
        JOIN crops ca ON ca.id = cm.crop_a_id
        JOIN crops cb ON cb.id = cm.crop_b_id
    """)
    companions_by_crop: dict[int, list[dict[str, Any]]] = {}
    for row in cur.fetchall():
        aid, bid = row["crop_a_id"], row["crop_b_id"]
        # for crop_a: partner is b
        partner_b = {
            "slug": _slugify(row["b_name_en"] or row["b_name_he"], fallback=f"crop-{bid}"),
            "name_he": row["b_name_he"],
            "compatibility": row["compatibility"],
            "notes": row["notes"],
        }
        companions_by_crop.setdefault(aid, []).append(partner_b)
        # for crop_b: partner is a
        partner_a = {
            "slug": _slugify(row["a_name_en"] or row["a_name_he"], fallback=f"crop-{aid}"),
            "name_he": row["a_name_he"],
            "compatibility": row["compatibility"],
            "notes": row["notes"],
        }
        companions_by_crop.setdefault(bid, []).append(partner_a)

    # NOTE: the internal crop-knowledge narrative table is INTENTIONALLY NOT
    # read here. Per LOD400 WP-B2 §3.1 OPERATIVE LICENSING INVARIANT (binding),
    # it holds copyrighted JMF MasterClass fair-use snippets licensed for
    # INTERNAL farm-operator use only — no publisher file may query it and no
    # upload payload may include its content (Prohibitions §3.1.1 #1 & #2).
    # The `is_internal_farm_use_only` flag is a farm-internal subdivision, NOT a
    # publication license. Enforced by test_ni_publisher_isolation.py (AC-21b).

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out = []
    for c in crops:
        cid = c["id"]
        dtm = dtm_by_crop.get(cid, {})
        season = _season_from_growth_cycle(c.get("growth_cycle"))

        # build identity block
        identity: dict[str, Any] = {}
        if c.get("category"):
            identity["category"] = c["category"]
        if c.get("growth_cycle"):
            identity["growth_cycle"] = c["growth_cycle"]
        if c.get("harvest_unit_default"):
            identity["harvest_unit_default"] = c["harvest_unit_default"]
        if c.get("first_fruit_year") is not None:
            identity["first_fruit_year"] = c["first_fruit_year"]
        family_block: dict[str, Any] = {}
        if c.get("family_name_he"):
            family_block["name_he"] = c["family_name_he"]
        if c.get("family_scientific_name"):
            family_block["scientific_name"] = c["family_scientific_name"]
        if family_block:
            identity["family"] = family_block

        payload_extras: dict[str, Any] = {
            "schema_version": 1,
            "name_en": c.get("name_en"),
            "growth_cycle": c.get("growth_cycle"),
            "harvest_unit_default": c.get("harvest_unit_default"),
            "first_fruit_year": c.get("first_fruit_year"),
            "description_md": c.get("description") or "",
            "oma_product_id": c.get("oma_product_id"),
            "variety_count": dtm.get("variety_count") or 0,
            "identity": identity,
            "calendar": calendar_by_crop.get(cid, []),
            "agronomy": agronomy_by_crop.get(cid, {}),
            "harvest": harvest_by_crop.get(cid, []),
            "storage": storage_by_crop.get(cid),
            "companions": companions_by_crop.get(cid, []),
            # "notes" deliberately omitted — internal crop-knowledge narrative is
            # internal-only per LOD400 WP-B2 §3.1 licensing invariant (see above).
        }
        out.append({
            "id": cid,
            "slug": _slugify(c["name_en"] or c["name_he"], fallback=f"crop-{cid}"),
            "hebrew_name": c["name_he"],
            "scientific_name": c.get("scientific_name"),
            "family_id": c.get("family_id"),
            "family_name_he": c.get("family_name_he"),
            "category": c.get("category"),
            "season": season,
            "dtm_min": dtm.get("dtm_min"),
            "dtm_max": dtm.get("dtm_max"),
            "last_pushed_at": now,
            "payload_json": payload_extras,
        })
    return out


# WP-CB-MIG AC-06/AC-07: canonical field names (Phase 5 renames applied).
# Old names → canonical:
#   in_row_spacing_cm    → spacing_in_row_cm
#   yield_per_m2_kg      → removed (T4 derived, not stored)
#   nutrient_removal_*_kg_ha → *_kg_per_ha
#   seeds_per_gram       → seeds_per_g
#   days_in_gh_total     → days_in_nursery
_AGRONOMY_FIELD_WHITELIST = (
    "days_to_maturity",
    "germination_temp_c_min",
    "germination_temp_c_opt",
    "germination_temp_c_max",
    "spacing_in_row_cm",          # was: in_row_spacing_cm
    "rows_per_bed",
    "soil_ph_target",
    "storage_temp_c_min",
    "storage_temp_c_max",
    "storage_life_days",
    "yield_per_bed_m",            # was: avg_yield_per_bed_m (canonical yield)
    "nutrient_removal_n_kg_per_ha",  # was: nutrient_removal_n_kg_ha
    "nutrient_removal_p_kg_per_ha",  # was: nutrient_removal_p_kg_ha
    "nutrient_removal_k_kg_per_ha",  # was: nutrient_removal_k_kg_ha
    "harvest_window_max_days",
    "seeds_per_g",                # was: seeds_per_gram
    # WP-CB-1 additions (LOD400 §3.3 / Schema §3.1–§3.2)
    "days_in_nursery_cell",
    "succession_interval_weeks",
    "days_in_nursery",            # was: days_in_gh_total (AC-07 / Canon §7.1)
    "price_documented",           # was: documented_price
    # WP-CB-MIG2 T1 additions (AC-08 / Canon §16, Amendment v1.3.0)
    "drip_lines_per_bed",         # irrigation count
    "labor_rate_harvest",         # harvest labor rate (units_per_hr)
    "labor_rate_wash",            # wash labor rate (units_per_hr)
    "plantings_per_season",       # succession count
    "harvest_weeks_span",         # succession weeks
)

# WP-CB-MIG2 T2/T3 attributes to emit in the agronomy payload block (AC-08b).
# These are read from crop_attribute (not crop_field_enrichment) and mirrored
# into payload["agronomy"] alongside the T1 numeric facts.
# sale_unit rides on harvest_unit (alias D-MIG2-1 — no separate attr entry).
_CATEGORICAL_ATTRS_WHITELIST = (
    "planting_method",
    "harvest_unit",
    "harvest_stage",
    "frost_tolerance_class",
    "sowing_months",
    "transplant_months",
    "season_window",
    # WP-CB-MIG2 additions
    "irrigation_type",
    "root_depth_class",
    "needs_summer_shade",
    "unit_size",
    "common_pests",
    "foliar_feeding_program",
)

# Confidence threshold τ for field_state classification (Gap-Fill Plan §2).
# VALIDATED: winning_source_class in {EX, NI} OR confidence_score >= τ
# UNVALIDATED: row exists but below threshold or low-trust source class
# MISSING: no crop_field_enrichment row for the field
_FIELD_STATE_TAU = 0.40
_HIGH_TRUST_CLASSES = {"EX", "NI"}


def _fetch_crop_varieties(conn) -> list[dict[str, Any]]:
    # WP-CB-MIG AC-06/AC-07: identity columns only (T1/T2 facts read from enrichment/crop_attribute).
    # Dropped columns (§7.4): days_to_maturity, in_row_spacing_cm, planting_method,
    # planting_season, harvest_unit, documented_price*, harvest_window_*.
    # After migration 059 these are gone; use enrichment + crop_attribute read path.
    sql = """
        SELECT id, crop_id, name_he, name_en, is_default, notes
        FROM crop_varieties
        WHERE name_he IS NOT NULL OR name_en IS NOT NULL
        ORDER BY id
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()

    # Fetch enrichment data for all varieties in one query (LOD400 §2 / WP-CB-1 §3.3)
    # Include confidence_score and winning_source_class for field_state computation.
    placeholders = ",".join(["%s"] * len(_AGRONOMY_FIELD_WHITELIST))
    enrich_sql = f"""
        SELECT variety_id, field_name, value_best, confidence_score, winning_source_class
        FROM crop_field_enrichment
        WHERE field_name IN ({placeholders})
    """
    cur.execute(enrich_sql, _AGRONOMY_FIELD_WHITELIST)

    # enrichment_meta: variety_id -> field_name -> {value, confidence, source_class}
    enrichment_meta: dict[int, dict[str, dict[str, Any]]] = {}
    agronomy_by_variety: dict[int, dict[str, float]] = {}
    for er in cur.fetchall():
        vid = er["variety_id"]
        fname = er["field_name"]
        if vid not in enrichment_meta:
            enrichment_meta[vid] = {}
        enrichment_meta[vid][fname] = {
            "value_best": er["value_best"],
            "confidence_score": er["confidence_score"],
            "winning_source_class": er["winning_source_class"],
        }
        if vid not in agronomy_by_variety:
            agronomy_by_variety[vid] = {}
        if er["value_best"] is not None:
            agronomy_by_variety[vid][fname] = float(er["value_best"])

    # WP-CB-MIG2 AC-08b: fetch T2/T3 attributes from crop_attribute.
    # These mirror how planting_method / harvest_unit are already delivered.
    cat_attr_placeholders = ",".join(["%s"] * len(_CATEGORICAL_ATTRS_WHITELIST))
    cat_attr_sql = f"""
        SELECT variety_id, attribute_name, value_canonical, value_list
        FROM crop_attribute
        WHERE attribute_name IN ({cat_attr_placeholders})
    """
    cur.execute(cat_attr_sql, _CATEGORICAL_ATTRS_WHITELIST)
    categorical_by_variety: dict[int, dict[str, Any]] = {}
    for ca in cur.fetchall():
        vid = ca["variety_id"]
        aname = ca["attribute_name"]
        if vid not in categorical_by_variety:
            categorical_by_variety[vid] = {}
        # value_list (jsonb) takes precedence for T3 attrs; otherwise use value_canonical
        val = ca["value_list"] if ca["value_list"] is not None else ca["value_canonical"]
        if val is not None:
            categorical_by_variety[vid][aname] = val

    # Serialize ASSUMPTIONS registry once for embedding in each variety payload.
    # WP-CB-1 AC-09: deliver the ASSUMPTIONS registry to the delivery tier.
    from organic_market_agent.crop_book.assumptions import ASSUMPTIONS as _ASSUMPTIONS_REGISTRY
    assumptions_payload = {
        k: {
            "key": a.key,
            "default": a.default,
            "unit": a.unit,
            "explainer_he": a.explainer_he,
            "post_url": a.post_url,
        }
        for k, a in _ASSUMPTIONS_REGISTRY.items()
    }

    out = []
    for v in rows:
        vid = v["id"]
        # T1 numeric agronomy
        agronomy: dict[str, Any] = dict(agronomy_by_variety.get(vid, {}))

        # WP-CB-MIG2 AC-08b: merge T2/T3 categoricals into the agronomy block.
        # Mirrors how planting_method / harvest_unit already delivered.
        cat_attrs = categorical_by_variety.get(vid, {})
        if cat_attrs:
            agronomy.update(cat_attrs)

        # Compute per-field field_state for the whitelist fields (Gap-Fill Plan §2).
        meta_for_variety = enrichment_meta.get(vid, {})
        field_state: dict[str, str] = {}
        for fname in _AGRONOMY_FIELD_WHITELIST:
            if fname not in meta_for_variety:
                field_state[fname] = "MISSING"
            else:
                em = meta_for_variety[fname]
                src_class = em["winning_source_class"] or ""
                score = float(em["confidence_score"]) if em["confidence_score"] is not None else 0.0
                if src_class in _HIGH_TRUST_CLASSES or score >= _FIELD_STATE_TAU:
                    field_state[fname] = "VALIDATED"
                else:
                    field_state[fname] = "UNVALIDATED"
        # Add field_state for categorical attrs
        for aname in _CATEGORICAL_ATTRS_WHITELIST:
            val = cat_attrs.get(aname)
            if val is not None and val != "" and val != []:
                field_state[aname] = "VALIDATED"
            else:
                field_state[aname] = "MISSING"

        # WP-CB-MIG AC-06/AC-07: identity columns only; numeric facts from enrichment,
        # categoricals from crop_attribute (via agronomy block — AC-08b).
        payload: dict[str, Any] = {
            "schema_version": 1,
            "name_en": v.get("name_en"),
            "is_default": bool(v.get("is_default")),
            "notes": v.get("notes"),
            # T1 numeric facts + T2/T3 categoricals all in agronomy block.
        }
        if agronomy:
            payload["agronomy"] = agronomy
        # WP-CB-1 AC-09: embed field_state map and ASSUMPTIONS registry (additive)
        payload["field_state"] = field_state
        payload["assumptions"] = assumptions_payload
        out.append({
            "id": vid,
            "crop_id": v["crop_id"],
            "name": v["name_he"] or v["name_en"] or f"variety-{vid}",
            "payload_json": payload,
        })
    return out


def _fetch_products(conn) -> list[dict[str, Any]]:
    sql = """
        SELECT p.id, p.code, p.canonical_name_he, p.category,
               u.code AS unit_symbol,
               p.is_organic_required, p.is_basket_product,
               p.seasonality_notes, p.is_active
        FROM products p
        LEFT JOIN measurement_units u ON u.id = p.default_measurement_unit_id
        WHERE p.is_active = TRUE
        ORDER BY p.id
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()

    # Best-effort latest price via daily_aggregates
    cur.execute("""
        SELECT DISTINCT ON (product_id)
               product_id, aggregate_date,
               COALESCE(weighted_avg_price, unweighted_avg_price, median_price) AS price
        FROM daily_aggregates
        WHERE aggregate_date >= CURRENT_DATE - INTERVAL '90 days'
        ORDER BY product_id, aggregate_date DESC
    """)
    price_by_product: dict[int, dict[str, Any]] = {}
    for r in cur.fetchall():
        price_by_product[r["product_id"]] = {
            "price": float(r["price"]) if r["price"] is not None else None,
            "date": r["aggregate_date"],
        }

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    today = _dt.date.today()
    out = []
    for p in rows:
        price_info = price_by_product.get(p["id"], {})
        price_date = price_info.get("date")
        freshness = (today - price_date).days if price_date else None
        out.append({
            "id": p["id"],
            "slug": _slugify(p["code"] or p["canonical_name_he"], fallback=f"product-{p['id']}"),
            "hebrew_name": p["canonical_name_he"],
            "category": p.get("category"),
            "unit": p.get("unit_symbol"),
            "last_price": price_info.get("price"),
            "last_price_date": price_date.isoformat() if price_date else None,
            "freshness_days": freshness,
            "last_pushed_at": now,
            "payload_json": {
                "schema_version": 1,
                "code": p.get("code"),
                "is_organic_required": bool(p.get("is_organic_required")),
                "is_basket_product": bool(p.get("is_basket_product")),
                "seasonality_notes": p.get("seasonality_notes"),
            },
        })
    return out


def _fetch_cover_crops(conn) -> list[dict[str, Any]]:
    """One row per cover crop. Global reference list (no crop_id FK)."""
    sql = """
        SELECT id, name_he, name_en, category,
               sow_window, total_days_garden, germination_temp_c_min,
               survives_winter, hardiness_zone, inoculum, notes
        FROM crop_cover_crops
        ORDER BY id
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out = []
    for r in rows:
        payload: dict[str, Any] = {"schema_version": 1}
        if r.get("sow_window"):
            payload["sow_window"] = r["sow_window"]
        if r.get("inoculum"):
            payload["inoculum"] = r["inoculum"]
        if r.get("notes"):
            payload["notes"] = r["notes"]
        if r.get("total_days_garden") is not None:
            payload["total_days_garden"] = r["total_days_garden"]
        if r.get("germination_temp_c_min") is not None:
            payload["germination_temp_c_min"] = float(r["germination_temp_c_min"])
        if r.get("survives_winter") is not None:
            payload["survives_winter"] = bool(r["survives_winter"])
        if r.get("hardiness_zone") is not None:
            payload["hardiness_zone"] = r["hardiness_zone"]
        out.append({
            "id": r["id"],
            "slug": _slugify(r.get("name_en") or r.get("name_he"), fallback=f"cover-crop-{r['id']}"),
            "name_he": r.get("name_he"),
            "name_en": r.get("name_en"),
            "category": r.get("category"),
            "last_pushed_at": now,
            "payload_json": payload,
        })
    return out


# ---------------------------------------------------------------------------
# WP-CB-DATA WI-4: crop-level enrichment + attribute fetchers
# ---------------------------------------------------------------------------

# SQL fragment reused by both crop-level fetchers.
# Resolves the representative variety per crop:
#   1. is_default = TRUE variety if any
#   2. Else first by COALESCE(name_he, name_en, 'variety-'||id) ASC, id ASC
#      — matches the publisher push name in _fetch_crop_varieties L511 and the
#        CropBookViewController L264/L289-300 consumer fallback (LOD400 §2.1, INFO-2)
_REPRESENTATIVE_VARIETY_CTE = """
WITH rep AS (
    SELECT id AS variety_id, crop_id,
           ROW_NUMBER() OVER (
               PARTITION BY crop_id
               ORDER BY is_default DESC,
                        COALESCE(name_he, name_en, 'variety-' || id::text) ASC,
                        id ASC
           ) AS rn
    FROM crop_varieties
)
"""


def _fetch_crop_field_enrichment(conn) -> list[dict[str, Any]]:
    """Crop-level enrichment mirror rows (WP-CB-DATA LOD400 §3 WI-4).

    For each crop, picks the representative variety (is_default first, then
    first-by-name fallback), reads crop_field_enrichment rows in
    _AGRONOMY_FIELD_WHITELIST, and emits one row per (crop_id, field_name)
    with unit from FIELD_REGISTRY and field_state stamped via existing τ/class
    constants.  Logs the count of crops with no default variety.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Count crops that have no is_default variety (data-hygiene signal, LOD §2.1).
    cur.execute("""
        SELECT COUNT(DISTINCT crop_id) AS no_default_count
        FROM crop_varieties
        WHERE crop_id NOT IN (
            SELECT DISTINCT crop_id FROM crop_varieties WHERE is_default = TRUE
        )
    """)
    count_row = cur.fetchone()
    no_default_count = count_row["no_default_count"] if count_row else 0
    if no_default_count:
        logger.info(
            "crop_field_enrichment: %d crops have no default variety — using first-by-name fallback",
            no_default_count,
        )

    # Window query: pick rn=1 variety per crop (is_default DESC, then first-by-name)
    # and join to crop_field_enrichment for the whitelist fields.
    whitelist_placeholders = ",".join(["%s"] * len(_AGRONOMY_FIELD_WHITELIST))
    cur.execute(f"""
        {_REPRESENTATIVE_VARIETY_CTE}
        SELECT rep.crop_id,
               cfe.field_name,
               cfe.value_best,
               cfe.confidence_score,
               cfe.winning_source_class
        FROM rep
        JOIN crop_field_enrichment cfe ON cfe.variety_id = rep.variety_id
        WHERE rep.rn = 1
          AND cfe.field_name IN ({whitelist_placeholders})
        ORDER BY rep.crop_id, cfe.field_name
    """, _AGRONOMY_FIELD_WHITELIST)
    enrichment_rows = cur.fetchall()

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out: list[dict[str, Any]] = []
    for er in enrichment_rows:
        fname = er["field_name"]
        score_raw = er["confidence_score"]
        score = float(score_raw) if score_raw is not None else 0.0
        src_class = er["winning_source_class"] or ""

        if src_class in _HIGH_TRUST_CLASSES or score >= _FIELD_STATE_TAU:
            field_state = "VALIDATED"
        else:
            field_state = "UNVALIDATED"

        unit = FIELD_REGISTRY[fname].unit if fname in FIELD_REGISTRY else None

        out.append({
            "crop_id": er["crop_id"],
            "field_name": fname,
            "value_best": float(er["value_best"]) if er["value_best"] is not None else None,
            "unit": unit,  # None → SQL NULL via json_encode NULL path
            "field_state": field_state,
            "winning_source_class": src_class or None,
            "confidence_score": score_raw,
            "last_pushed_at": now,
        })
    return out


def _fetch_crop_attribute(conn) -> list[dict[str, Any]]:
    """Crop-level attribute mirror rows (WP-CB-DATA LOD400 §3 WI-4).

    For each crop, picks the representative variety (same rule as
    _fetch_crop_field_enrichment), reads crop_attribute rows in
    _CATEGORICAL_ATTRS_WHITELIST, maps attribute_name → attribute_key,
    and emits one row per (crop_id, attribute_key).  value_list (jsonb list)
    is JSON-encoded when present; otherwise value_canonical is used.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cat_placeholders = ",".join(["%s"] * len(_CATEGORICAL_ATTRS_WHITELIST))
    cur.execute(f"""
        {_REPRESENTATIVE_VARIETY_CTE}
        SELECT rep.crop_id,
               ca.attribute_name,
               ca.value_canonical,
               ca.value_list
        FROM rep
        JOIN crop_attribute ca ON ca.variety_id = rep.variety_id
        WHERE rep.rn = 1
          AND ca.attribute_name IN ({cat_placeholders})
        ORDER BY rep.crop_id, ca.attribute_name
    """, _CATEGORICAL_ATTRS_WHITELIST)
    attr_rows = cur.fetchall()

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out: list[dict[str, Any]] = []
    for ar in attr_rows:
        value_list_raw = ar["value_list"]
        value_canonical = ar["value_canonical"]

        # value_list (jsonb list) takes precedence over value_canonical.
        # psycopg2 returns jsonb as Python list already; encode to JSON string
        # for the push payload (IngestController stores it in JSON column).
        if value_list_raw is not None:
            value_list_json = json.dumps(value_list_raw, ensure_ascii=False)
            field_state = "VALIDATED"
        elif value_canonical:
            value_list_json = None
            field_state = "VALIDATED"
        else:
            value_list_json = None
            field_state = "MISSING"

        out.append({
            "crop_id": ar["crop_id"],
            "attribute_key": ar["attribute_name"],  # attribute_name → attribute_key
            "value_canonical": value_canonical,
            "value_list": value_list_json,
            "field_state": field_state,
            "last_pushed_at": now,
        })
    return out


def _fetch_crop_content(conn) -> list[dict[str, Any]]:
    """Crop-level narrative-content canonical mirror rows (WP-CB-CONTENT).

    One row per (crop_id, content_type) — the consolidated canonical body (Normal mode).
    field_state is stamped via the existing τ/class constants so the delivery tier gates
    rendering consistently with the enrichment/attribute mirrors.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT crop_id, content_type, text_md,
               winning_source_class, confidence_score
        FROM crop_content
        ORDER BY crop_id, content_type
    """)
    rows = cur.fetchall()

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out: list[dict[str, Any]] = []
    for r in rows:
        score_raw = r["confidence_score"]
        score = float(score_raw) if score_raw is not None else 0.0
        src_class = r["winning_source_class"] or ""
        if src_class in _HIGH_TRUST_CLASSES or score >= _FIELD_STATE_TAU:
            field_state = "VALIDATED"
        else:
            field_state = "UNVALIDATED"
        out.append({
            "crop_id": r["crop_id"],
            "content_type": r["content_type"],
            "text_md": r["text_md"],
            "winning_source_class": src_class or None,
            "confidence_score": score_raw,
            "field_state": field_state,
            "last_pushed_at": now,
        })
    return out


def _fetch_crop_content_source(conn) -> list[dict[str, Any]]:
    """Per-source narrative variants (Deep mode), denormalized with crop_id + content_type.

    JOINed to crop_content so each variant carries (crop_id, content_type, source_label) —
    the delivery mirror is keyed by those (crop-scoped), not the Postgres surrogate content_id.
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT cc.crop_id, cc.content_type,
               ccs.source_label, ccs.source_class,
               ccs.raw_text_md, ccs.source_url, ccs.display_order
        FROM crop_content_source ccs
        JOIN crop_content cc ON cc.id = ccs.content_id
        ORDER BY cc.crop_id, cc.content_type, ccs.display_order, ccs.source_label
    """)
    rows = cur.fetchall()

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append({
            "crop_id": r["crop_id"],
            "content_type": r["content_type"],
            "source_label": r["source_label"],
            "source_class": r["source_class"],
            "raw_text_md": r["raw_text_md"],
            "source_url": r["source_url"],
            "display_order": r["display_order"],
            "last_pushed_at": now,
        })
    return out


# ---------------------------------------------------------------------------


def _slugify(value: str | None, *, fallback: str) -> str:
    if not value:
        return fallback
    # Pre-clean display annotations leaked into name_en so the slug is the real crop name:
    #   "Beans (default: Pole/Climbing)" → "beans" · "Pac Choi (Bok Choy)" → "pac-choi"
    #   "Onions: Scallions" → "scallions" · "Lettuce: Salad Mix" → "salad-mix"
    import re as _re
    cleaned = _re.sub(r"\([^)]*\)", " ", value)          # drop parenthetical annotations
    if ":" in cleaned:
        cleaned = cleaned.rsplit(":", 1)[-1]             # take the part after a category colon prefix
    value = cleaned.strip() or value
    s = value.strip().lower()
    out_chars: list[str] = []
    for ch in s:
        if ch.isalnum():
            out_chars.append(ch)
        elif ch in " -_/":
            out_chars.append("-")
    slug = "".join(out_chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:80] or fallback


def _season_from_growth_cycle(cycle: str | None) -> str | None:
    if not cycle:
        return None
    mapping = {
        "annual": "annual",
        "perennial": "year-round",
        "biennial": "biennial",
    }
    return mapping.get(cycle, cycle)


# ---------------------------------------------------------------------------


def _sign(body: bytes, secret: str) -> str:
    sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


def _push_batch(
    cfg: PushConfig,
    table: str,
    rows: list[dict[str, Any]],
    idempotency_key: str,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "table": table,
        "operation": "upsert",
        "idempotency_key": idempotency_key,
        "rows": rows,
    }
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    sig = _sign(body, cfg.hmac_secret)
    if dry_run:
        return {
            "dry_run": True, "table": table, "rows": len(rows),
            "key": idempotency_key, "body_bytes": len(body),
        }
    r = requests.post(
        cfg.ingest_url,
        data=body,
        headers={"Content-Type": "application/json", "X-SFA-Auth": sig},
        timeout=cfg.timeout_s,
    )
    try:
        return {"http_status": r.status_code, **r.json()}
    except Exception:
        return {"http_status": r.status_code, "body": r.text[:300]}


def _row_crop_id(row: dict[str, Any]) -> Any:
    """Crop identity for a fetched row: crop-keyed tables carry 'crop_id';
    the crops table itself carries 'id'."""
    return row["crop_id"] if "crop_id" in row else row.get("id")


def _push_table(
    cfg: PushConfig, conn, table: str, *,
    limit: int | None, dry_run: bool, allowed_crop_ids: set[int] | None = None,
) -> dict[str, Any]:
    fetchers = {
        "crops": _fetch_crops,
        "crop_varieties": _fetch_crop_varieties,
        "products": _fetch_products,
        "cover_crops": _fetch_cover_crops,
        "crop_field_enrichment": _fetch_crop_field_enrichment,
        "crop_attribute": _fetch_crop_attribute,
        "crop_content": _fetch_crop_content,
        "crop_content_source": _fetch_crop_content_source,
    }
    if table not in fetchers:
        raise SystemExit(f"Unknown table: {table}")
    try:
        rows = fetchers[table](conn)
    except psycopg2.errors.UndefinedTable as e:
        # Source schema not provisioned (e.g. crop_book migrations not applied
        # on this Postgres instance). Skip cleanly — don't break the daily cron.
        conn.rollback()
        logger.warning("source schema missing for %s; skipping. (%s)", table, str(e)[:120])
        return {"table": table, "skipped": "source_schema_missing"}
    if allowed_crop_ids is not None:
        # Scoped push (e.g. WP-CB-SRC-SWEEP): only rows for the allow-listed crops.
        rows = [r for r in rows if _row_crop_id(r) in allowed_crop_ids]
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return {"table": table, "rows": 0, "skipped": "empty"}

    ts = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    results = []
    for batch_no, start in enumerate(range(0, len(rows), cfg.batch_size), start=1):
        chunk = rows[start:start + cfg.batch_size]
        key = f"{table}_{ts}_{batch_no:03d}"
        res = _push_batch(cfg, table, chunk, key, dry_run=dry_run)
        results.append({"key": key, "rows_in_batch": len(chunk), "result": res})
        logger.info("push %s batch=%d size=%d -> %s", table, batch_no, len(chunk), res)
    return {"table": table, "total_rows": len(rows), "batches": results}


# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Push canonical data to sfa.nimrod.bio ingest API")
    parser.add_argument(
        "--table",
        choices=(
            "crops", "crop_varieties", "products", "cover_crops",
            "crop_field_enrichment", "crop_attribute",
            "crop_content", "crop_content_source", "all",
        ),
        default="all",
        help="Which table to push",
    )
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit rows per table (for testing)")
    parser.add_argument("--slugs", default=None,
                        help="Comma-separated crop slugs — scope the push to only these crops "
                             "(crop-keyed tables only). Ambiguous slugs (duplicate name_en) "
                             "raise an error; use --crop-ids to disambiguate.")
    parser.add_argument("--crop-ids", default=None, dest="crop_ids",
                        help="Comma-separated crop_ids — unambiguous scope for the push "
                             "(crop-keyed tables only). Used for scoped deploys (e.g. WP-CB-SRC-SWEEP). "
                             "Takes precedence over --slugs.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build payloads but don't POST")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    cfg = _load_config()
    logger.info("Target: %s", cfg.ingest_url)

    # Crop-keyed tables that a scoped (--crop-ids/--slugs) push may target.
    # products/cover_crops are NOT crop-keyed and are excluded from scoped pushes.
    CROP_KEYED = {"crops", "crop_varieties", "crop_field_enrichment",
                  "crop_attribute", "crop_content", "crop_content_source"}

    conn = psycopg2.connect(cfg.db_url)
    try:
        allowed_crop_ids: set[int] | None = None
        if args.crop_ids:
            allowed_crop_ids = {int(x) for x in args.crop_ids.split(",") if x.strip()}
        elif args.slugs:
            want = {s.strip() for s in args.slugs.split(",") if s.strip()}
            # slug -> [ids]; name_en duplicates (e.g. a duplicate crop) make a slug ambiguous.
            slug_to_ids: dict[str, list[int]] = {}
            for r in _fetch_crops(conn):
                slug_to_ids.setdefault(r["slug"], []).append(r["id"])
            unknown = want - set(slug_to_ids)
            if unknown:
                raise SystemExit(f"--slugs: unknown crop slug(s): {sorted(unknown)}")
            ambiguous = {s: slug_to_ids[s] for s in want if len(slug_to_ids[s]) > 1}
            if ambiguous:
                raise SystemExit(
                    f"--slugs: ambiguous slug(s) map to multiple crop_ids: {ambiguous}. "
                    f"Use --crop-ids to disambiguate.")
            allowed_crop_ids = {slug_to_ids[s][0] for s in want}

        if allowed_crop_ids is not None:
            logger.info("Scoped push: %d crop(s) -> crop_ids %s",
                        len(allowed_crop_ids), sorted(allowed_crop_ids))

        if args.table == "all":
            tables = (sorted(CROP_KEYED) if allowed_crop_ids is not None
                      else ["crops", "crop_varieties", "products", "cover_crops",
                            "crop_field_enrichment", "crop_attribute",
                            "crop_content", "crop_content_source"])
        else:
            if allowed_crop_ids is not None and args.table not in CROP_KEYED:
                raise SystemExit(f"--crop-ids/--slugs scoping only applies to crop-keyed tables: {sorted(CROP_KEYED)}")
            tables = [args.table]
        for tbl in tables:
            res = _push_table(cfg, conn, tbl, limit=args.limit, dry_run=args.dry_run,
                              allowed_crop_ids=allowed_crop_ids)
            print(json.dumps(res, ensure_ascii=False, default=str, indent=2))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
