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

    now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    out = []
    for c in crops:
        dtm = dtm_by_crop.get(c["id"], {})
        season = _season_from_growth_cycle(c.get("growth_cycle"))
        payload_extras = {
            "schema_version": 1,
            "name_en": c.get("name_en"),
            "growth_cycle": c.get("growth_cycle"),
            "harvest_unit_default": c.get("harvest_unit_default"),
            "first_fruit_year": c.get("first_fruit_year"),
            "description_md": c.get("description") or "",
            "oma_product_id": c.get("oma_product_id"),
            "variety_count": dtm.get("variety_count") or 0,
        }
        out.append({
            "id": c["id"],
            "slug": _slugify(c["name_en"] or c["name_he"], fallback=f"crop-{c['id']}"),
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
)


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

    # Fetch enrichment data for all varieties in one query (LOD400 §2)
    placeholders = ",".join(["%s"] * len(_AGRONOMY_FIELD_WHITELIST))
    enrich_sql = f"""
        SELECT variety_id, field_name, value_best
        FROM crop_field_enrichment
        WHERE field_name IN ({placeholders})
    """
    cur.execute(enrich_sql, _AGRONOMY_FIELD_WHITELIST)
    agronomy_by_variety: dict[int, dict[str, float]] = {}
    for er in cur.fetchall():
        vid = er["variety_id"]
        if vid not in agronomy_by_variety:
            agronomy_by_variety[vid] = {}
        if er["value_best"] is not None:
            agronomy_by_variety[vid][er["field_name"]] = float(er["value_best"])

    out = []
    for v in rows:
        agronomy = agronomy_by_variety.get(v["id"], {})
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
        out.append({
            "id": v["id"],
            "crop_id": v["crop_id"],
            "name": v["name_he"] or v["name_en"] or f"variety-{v['id']}",
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
    parser.add_argument("--table", choices=("crops", "crop_varieties", "products", "all"),
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
        tables = ["crops", "crop_varieties", "products"] if args.table == "all" else [args.table]
        for tbl in tables:
            res = _push_table(cfg, conn, tbl, limit=args.limit, dry_run=args.dry_run)
            print(json.dumps(res, ensure_ascii=False, default=str, indent=2))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
