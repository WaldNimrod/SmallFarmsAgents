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

    # Aggregate variety DTM ranges to populate dtm_min/dtm_max on crops
    var_sql = """
        SELECT crop_id,
               MIN(NULLIF(days_to_maturity,0)) AS dtm_min,
               MAX(NULLIF(days_to_maturity,0)) AS dtm_max,
               COUNT(*) AS variety_count
        FROM crop_varieties
        GROUP BY crop_id
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

    # knowledge notes — public only (is_internal_farm_use_only = FALSE), HARD GATE
    cur.execute("""
        SELECT crop_id, note_type, body_text, trust_tier
        FROM crop_knowledge_notes
        WHERE is_internal_farm_use_only = FALSE
        ORDER BY crop_id, id
    """)
    notes_by_crop: dict[int, list[dict[str, Any]]] = {}
    for row in cur.fetchall():
        cid = row["crop_id"]
        notes_by_crop.setdefault(cid, []).append({
            "note_type": row["note_type"],
            "body_text": row["body_text"],
            "trust_tier": row["trust_tier"],
        })

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
            "notes": notes_by_crop.get(cid, []),  # public-only; empty until public notes exist
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


_AGRONOMY_FIELD_WHITELIST = (
    "days_to_maturity",
    "germination_temp_c_min",
    "germination_temp_c_opt",
    "germination_temp_c_max",
    "in_row_spacing_cm",
    "rows_per_bed",
    "soil_ph_target",
    "storage_temp_c_min",
    "storage_temp_c_max",
    "storage_life_days",
    "yield_per_m2_kg",
    "nutrient_removal_n_kg_ha",
    "nutrient_removal_p_kg_ha",
    "nutrient_removal_k_kg_ha",
    "harvest_window_max_days",
    "seeds_per_gram",
    # WP-CB-1 additions (LOD400 §3.3 / Schema §3.1–§3.2)
    "days_in_nursery_cell",
    "succession_interval_weeks",
)

# Confidence threshold τ for field_state classification (Gap-Fill Plan §2).
# VALIDATED: winning_source_class in {EX, NI} OR confidence_score >= τ
# UNVALIDATED: row exists but below threshold or low-trust source class
# MISSING: no crop_field_enrichment row for the field
_FIELD_STATE_TAU = 0.40
_HIGH_TRUST_CLASSES = {"EX", "NI"}


def _fetch_crop_varieties(conn) -> list[dict[str, Any]]:
    sql = """
        SELECT id, crop_id, name_he, name_en, is_default,
               days_to_maturity, harvest_window_min_days, harvest_window_max_days,
               in_row_spacing_cm, planting_method, planting_season,
               harvest_unit, documented_price, documented_price_unit,
               documented_price_source, notes
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
        agronomy = agronomy_by_variety.get(vid, {})

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

        payload: dict[str, Any] = {
            "schema_version": 1,
            "name_en": v.get("name_en"),
            "is_default": bool(v.get("is_default")),
            "days_to_maturity": v.get("days_to_maturity"),
            "harvest_window_min_days": v.get("harvest_window_min_days"),
            "harvest_window_max_days": v.get("harvest_window_max_days"),
            "in_row_spacing_cm": v.get("in_row_spacing_cm"),
            "planting_method": v.get("planting_method"),
            "planting_season": v.get("planting_season"),
            "harvest_unit": v.get("harvest_unit"),
            "documented_price": float(v["documented_price"]) if v.get("documented_price") is not None else None,
            "documented_price_unit": v.get("documented_price_unit"),
            "documented_price_source": v.get("documented_price_source"),
            "notes": v.get("notes"),
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


def _slugify(value: str | None, *, fallback: str) -> str:
    if not value:
        return fallback
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


def _push_table(
    cfg: PushConfig, conn, table: str, *,
    limit: int | None, dry_run: bool,
) -> dict[str, Any]:
    fetchers = {
        "crops": _fetch_crops,
        "crop_varieties": _fetch_crop_varieties,
        "products": _fetch_products,
        "cover_crops": _fetch_cover_crops,
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
    parser.add_argument("--table", choices=("crops", "crop_varieties", "products", "cover_crops", "all"),
                        default="all", help="Which table to push")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit rows per table (for testing)")
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

    conn = psycopg2.connect(cfg.db_url)
    try:
        tables = ["crops", "crop_varieties", "products", "cover_crops"] if args.table == "all" else [args.table]
        for tbl in tables:
            res = _push_table(cfg, conn, tbl, limit=args.limit, dry_run=args.dry_run)
            print(json.dumps(res, ensure_ascii=False, default=str, indent=2))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
