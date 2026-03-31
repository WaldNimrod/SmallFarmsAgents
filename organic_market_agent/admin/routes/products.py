"""Product catalog — GET /products, GET /products/<code>"""
from __future__ import annotations

from collections import Counter

import sqlalchemy as sa
from flask import Blueprint, abort, flash, g, redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import text
from urllib.parse import quote

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import Product, ProductAlias

bp = Blueprint("products", __name__)


@bp.route("/products")
def product_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT p.code, p.canonical_name_he, p.is_active,
                   mu.name_he AS default_unit,
                   MAX(no.observed_at)  AS last_seen,
                   COUNT(no.id)         AS obs_count,
                   AVG(COALESCE(no.normalized_price_value, no.price_amount)) AS avg_price,
                   COUNT(DISTINCT no.source_id) AS sources_count
            FROM products p
            LEFT JOIN measurement_units mu ON mu.id = p.default_measurement_unit_id
            LEFT JOIN normalized_observations no ON no.product_id = p.id
            GROUP BY p.id, p.code, p.canonical_name_he, p.is_active, mu.name_he,
                     p.display_order
            ORDER BY p.display_order, p.code
            LIMIT 200
            """
        )
    ).all()
    products = [
        {
            "code": r[0],
            "canonical_name_he": r[1],
            "is_active": r[2],
            "default_unit": r[3] or "—",
            "last_seen": r[4].strftime("%Y-%m-%d") if r[4] else None,
            "obs_count": int(r[5] or 0),
            "avg_price": round(float(r[6]), 2) if r[6] else None,
            "sources_count": int(r[7] or 0),
        }
        for r in rows
    ]
    total_products = int(
        session.execute(text("SELECT COUNT(*) FROM products")).scalar_one() or 0
    )
    products_db_active = int(
        session.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = true")
        ).scalar_one()
        or 0
    )
    products_db_inactive = int(
        session.execute(
            text("SELECT COUNT(*) FROM products WHERE is_active = false")
        ).scalar_one()
        or 0
    )
    return render_template(
        "admin/products.html",
        products=products,
        products_total=total_products,
        products_db_active=products_db_active,
        products_db_inactive=products_db_inactive,
    )


@bp.route("/products/<code>")
def product_detail(code: str):
    session = g.db_session
    prod = session.execute(
        sa.select(Product).where(Product.code == code)
    ).scalar_one_or_none()
    if not prod:
        abort(404)

    # ── Summary stats ────────────────────────────────────────────────────────
    stats = session.execute(
        text("""
            SELECT
              COUNT(no.id)                                                           AS total_obs,
              COUNT(DISTINCT no.source_id)                                          AS distinct_sources,
              MIN(COALESCE(no.normalized_price_value, no.price_amount))             AS min_price,
              MAX(COALESCE(no.normalized_price_value, no.price_amount))             AS max_price,
              AVG(COALESCE(no.normalized_price_value, no.price_amount))             AS avg_price,
              PERCENTILE_CONT(0.5) WITHIN GROUP (
                ORDER BY COALESCE(no.normalized_price_value, no.price_amount))      AS median_price,
              STDDEV(COALESCE(no.normalized_price_value, no.price_amount))          AS stddev_price,
              MAX(no.observed_at)                                                    AS last_seen,
              MIN(no.observed_at)                                                    AS first_seen,
              mu.name_he                                                             AS unit
            FROM normalized_observations no
            LEFT JOIN measurement_units mu ON mu.id = no.display_unit_id
            WHERE no.product_id = :pid
            GROUP BY mu.name_he
            ORDER BY total_obs DESC
            LIMIT 1
        """),
        {"pid": prod.id},
    ).one_or_none()

    summary = None
    if stats:
        summary = {
            "total_obs":     int(stats[0] or 0),
            "distinct_srcs": int(stats[1] or 0),
            "min_price":     round(float(stats[2]), 2) if stats[2] else None,
            "max_price":     round(float(stats[3]), 2) if stats[3] else None,
            "avg_price":     round(float(stats[4]), 2) if stats[4] else None,
            "median_price":  round(float(stats[5]), 2) if stats[5] else None,
            "stddev_price":  round(float(stats[6]), 2) if stats[6] else None,
            "last_seen":     stats[7].strftime("%Y-%m-%d %H:%M") if stats[7] else "—",
            "first_seen":    stats[8].strftime("%Y-%m-%d %H:%M") if stats[8] else "—",
            "unit":          stats[9] or "—",
        }

    # ── Per-source breakdown ─────────────────────────────────────────────────
    per_source = session.execute(
        text("""
            SELECT s.code, s.name, s.source_tier,
                   COUNT(no.id)                                                      AS obs_count,
                   MIN(COALESCE(no.normalized_price_value, no.price_amount))         AS min_price,
                   MAX(COALESCE(no.normalized_price_value, no.price_amount))         AS max_price,
                   AVG(COALESCE(no.normalized_price_value, no.price_amount))         AS avg_price,
                   MAX(no.observed_at)                                               AS last_seen,
                   mu.name_he                                                        AS unit
            FROM normalized_observations no
            JOIN sources s ON s.id = no.source_id
            LEFT JOIN measurement_units mu ON mu.id = no.display_unit_id
            WHERE no.product_id = :pid
            GROUP BY s.id, s.code, s.name, s.source_tier, mu.name_he
            ORDER BY obs_count DESC
        """),
        {"pid": prod.id},
    ).all()

    sources_out = [
        {
            "code":      r[0],
            "name":      r[1],
            "tier":      r[2],
            "obs_count": int(r[3] or 0),
            "min_price": round(float(r[4]), 2) if r[4] else None,
            "max_price": round(float(r[5]), 2) if r[5] else None,
            "avg_price": round(float(r[6]), 2) if r[6] else None,
            "last_seen": r[7].strftime("%Y-%m-%d") if r[7] else "—",
            "unit":      r[8] or "—",
        }
        for r in per_source
    ]

    # ── Last 50 observations ─────────────────────────────────────────────────
    recent_obs = session.execute(
        text("""
            SELECT no.observed_at,
                   s.code                                                           AS src_code,
                   s.name                                                           AS src_name,
                   COALESCE(no.normalized_price_value, no.price_amount)            AS price,
                   mu_d.name_he                                                     AS display_unit,
                   no.flag_status,
                   no.confidence_score,
                   rei.raw_product_name,
                   rei.raw_price_text,
                   rei.raw_unit_text,
                   rei.raw_quantity_text
            FROM normalized_observations no
            JOIN sources s ON s.id = no.source_id
            LEFT JOIN measurement_units mu_d ON mu_d.id = no.display_unit_id
            LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
            WHERE no.product_id = :pid
            ORDER BY no.observed_at DESC
            LIMIT 50
        """),
        {"pid": prod.id},
    ).all()

    obs_out = [
        {
            "observed_at":    r[0].strftime("%Y-%m-%d %H:%M") if r[0] else "—",
            "src_code":       r[1],
            "src_name":       r[2],
            "price":          round(float(r[3]), 2) if r[3] else None,
            "display_unit":   r[4] or "—",
            "flag_status":    r[5] or "—",
            "confidence":     round(float(r[6]), 2) if r[6] else None,
            "raw_name":       r[7] or "—",
            "raw_price":      r[8] or "—",
            "raw_unit":       r[9] or "—",
            "raw_qty":        r[10] or "—",
        }
        for r in recent_obs
    ]

    # ── Active aliases ───────────────────────────────────────────────────────
    aliases = session.execute(
        text("""
            SELECT pa.id, pa.alias_text,
                   COALESCE(s.code, 'גלובלי') AS scope
            FROM product_aliases pa
            LEFT JOIN sources s ON s.id = pa.source_id
            WHERE pa.product_id = :pid AND pa.is_active = true
            ORDER BY pa.alias_text
        """),
        {"pid": prod.id},
    ).all()

    aliases_out = [{"id": r[0], "text": r[1], "scope": r[2]} for r in aliases]

    # ── Unresolvable raw strings that look similar (potential missing aliases) ──
    similar_unresolved = session.execute(
        text("""
            SELECT COALESCE(rei.raw_product_name, '') AS raw_name,
                   COUNT(*)                           AS cnt,
                   STRING_AGG(DISTINCT s.code, ', ' ORDER BY s.code) AS src_codes
            FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.extraction_status = 'unresolvable'
              AND rei.is_quarantined = false
              AND (
                    rei.raw_product_name ILIKE '%' || :name_part || '%'
                    OR :name_part ILIKE '%' || COALESCE(rei.raw_product_name,'') || '%'
              )
            GROUP BY rei.raw_product_name
            ORDER BY cnt DESC
            LIMIT 20
        """),
        {"name_part": prod.canonical_name_he},
    ).all()

    unresolved_similar = [
        {"raw_name": r[0], "count": int(r[1]), "src_codes": r[2] or "",
         "url_encoded": quote(r[0], safe="")}
        for r in similar_unresolved
    ]

    obs_flag_counts = Counter(o["flag_status"] for o in obs_out)
    obs_flag_segments = [(k, obs_flag_counts[k]) for k in sorted(obs_flag_counts.keys())]

    tier_c = Counter((s["tier"] or "—") for s in sources_out)
    sources_tier_segments = [(k, tier_c[k]) for k in sorted(tier_c.keys(), key=str)]

    scope_c = Counter(a["scope"] for a in aliases_out)
    aliases_scope_segments = [(k, scope_c[k]) for k in sorted(scope_c.keys(), key=str)]

    return render_template(
        "admin/product_detail.html",
        prod=prod,
        summary=summary,
        sources_out=sources_out,
        obs_out=obs_out,
        aliases_out=aliases_out,
        unresolved_similar=unresolved_similar,
        obs_flag_segments=obs_flag_segments,
        sources_tier_segments=sources_tier_segments,
        aliases_scope_segments=aliases_scope_segments,
    )


@bp.route("/products/<code>/disable_alias/<int:alias_id>", methods=["POST"])
@login_required
def disable_alias(code: str, alias_id: int):
    session = g.db_session
    prod = session.execute(sa.select(Product).where(Product.code == code)).scalar_one_or_none()
    if not prod:
        abort(404)
    pa = session.get(ProductAlias, alias_id)
    if not pa or pa.product_id != prod.id:
        flash("אליאס לא נמצא למוצר זה.", "danger")
        return redirect(url_for("products.product_detail", code=code))
    before = {"is_active": pa.is_active}
    pa.is_active = False
    audit_write(
        session,
        "disable_alias",
        "product_alias",
        entity_id=pa.id,
        before=before,
        after={"is_active": False},
    )
    session.commit()
    flash("האליאס הושבת.", "success")
    return redirect(url_for("products.product_detail", code=code))
