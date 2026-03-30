"""Top unresolvable raw strings — GET /unresolved, GET /unresolved/<raw_name>"""
from __future__ import annotations

import difflib
from urllib.parse import quote, unquote

import sqlalchemy as sa
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import Product, ProductAlias

bp = Blueprint("unresolved", __name__)


@bp.route("/unresolved")
def unresolved_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT COALESCE(rei.raw_product_name, '') AS raw_product_name,
                   COUNT(*)                            AS cnt,
                   COUNT(DISTINCT sfr.source_id)       AS source_cnt,
                   STRING_AGG(DISTINCT s.code, ', ' ORDER BY s.code) AS source_codes,
                   MAX(rei.extracted_at)               AS last_seen
            FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.extraction_status = 'unresolvable'
              AND rei.is_quarantined = false
            GROUP BY rei.raw_product_name
            ORDER BY cnt DESC
            LIMIT 200
            """
        )
    ).all()
    items = [
        {
            "raw_product_name": r[0],
            "count": int(r[1]),
            "source_cnt": int(r[2]),
            "source_codes": r[3] or "",
            "last_seen": r[4].strftime("%Y-%m-%d") if r[4] else "—",
            "url_encoded": quote(r[0], safe=""),
        }
        for r in rows
    ]
    return render_template("admin/unresolved.html", items=items)


@bp.route("/unresolved/<path:raw_name_encoded>")
def unresolved_detail(raw_name_encoded: str):
    session = g.db_session
    raw_name = unquote(raw_name_encoded)

    # All occurrences of this raw name (non-quarantined, unresolvable)
    occurrences = session.execute(
        text(
            """
            SELECT rei.raw_price_text, rei.raw_unit_text, rei.unresolvable_reason,
                   rei.extracted_at, s.code AS src_code, s.name AS src_name
            FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.extraction_status = 'unresolvable'
              AND rei.is_quarantined = false
              AND COALESCE(rei.raw_product_name, '') = :rname
            ORDER BY rei.extracted_at DESC
            LIMIT 100
            """
        ),
        {"rname": raw_name},
    ).all()

    if not occurrences:
        abort(404)

    occ_out = [
        {
            "raw_price": r[0] or "—",
            "raw_unit": r[1] or "—",
            "reason": r[2] or "—",
            "extracted_at": r[3].strftime("%Y-%m-%d %H:%M") if r[3] else "—",
            "src_code": r[4],
            "src_name": r[5],
        }
        for r in occurrences
    ]

    # Summary stats
    total_count = len(occ_out)
    distinct_sources = len({o["src_code"] for o in occ_out})
    unique_reasons = list({o["reason"] for o in occ_out if o["reason"] != "—"})

    # Closest existing aliases (for normalizer improvement hints)
    alias_rows = session.execute(
        text(
            """
            SELECT pa.alias_text, p.canonical_name_he, p.code
            FROM product_aliases pa
            JOIN products p ON p.id = pa.product_id
            WHERE pa.is_active = true
            ORDER BY pa.alias_text
            """
        )
    ).all()

    # Use difflib to find closest matches
    all_aliases = [(r[0], r[1], r[2]) for r in alias_rows]
    alias_texts = [a[0] for a in all_aliases]
    close_matches = difflib.get_close_matches(raw_name, alias_texts, n=5, cutoff=0.3)
    # Also check substring containment
    substr_matches = [
        a for a in all_aliases
        if (raw_name in a[0] or a[0] in raw_name) and a[0] not in close_matches
    ][:3]

    alias_suggestions = []
    for m in close_matches:
        for alias_text, canonical, code in all_aliases:
            if alias_text == m:
                alias_suggestions.append(
                    {"alias": alias_text, "canonical": canonical, "code": code, "match_type": "דמיון"}
                )
                break
    for alias_text, canonical, code in substr_matches:
        alias_suggestions.append(
            {"alias": alias_text, "canonical": canonical, "code": code, "match_type": "כלול"}
        )

    all_products = session.execute(
        sa.select(Product.code, Product.canonical_name_he)
        .where(Product.is_active.is_(True))
        .order_by(Product.display_order, Product.code)
    ).all()
    all_products_out = [{"code": r[0], "name": r[1]} for r in all_products]
    raw_encoded = quote(raw_name, safe="")

    return render_template(
        "admin/unresolved_detail.html",
        raw_name=raw_name,
        raw_encoded=raw_encoded,
        occurrences=occ_out,
        total_count=total_count,
        distinct_sources=distinct_sources,
        unique_reasons=unique_reasons,
        alias_suggestions=alias_suggestions,
        all_products=all_products_out,
    )


@bp.route("/unresolved/<path:raw_name_encoded>/add_alias", methods=["POST"])
@login_required
def add_alias(raw_name_encoded: str):
    session = g.db_session
    raw_name = unquote(raw_name_encoded)
    product_code = (request.form.get("product_code") or "").strip()
    if not product_code:
        flash("יש לבחור מוצר.", "danger")
        return redirect(url_for("unresolved.unresolved_detail", raw_name_encoded=raw_name_encoded))
    prod = session.execute(sa.select(Product).where(Product.code == product_code)).scalar_one_or_none()
    if not prod:
        flash("מוצר לא נמצא.", "danger")
        return redirect(url_for("unresolved.unresolved_detail", raw_name_encoded=raw_name_encoded))
    norm = raw_name.strip().lower()
    pa = ProductAlias(
        product_id=prod.id,
        alias_text=raw_name[:200],
        alias_text_normalized=norm[:200],
        source_id=None,
        is_active=True,
    )
    session.add(pa)
    try:
        session.flush()
        audit_write(
            session,
            "create_alias",
            "product_alias",
            entity_id=pa.id,
            after={"alias_text": raw_name, "product_code": product_code, "from_unresolved": True},
        )
        session.commit()
        flash("אליאס נוסף בהצלחה", "success")
    except IntegrityError:
        session.rollback()
        flash("אליאס כפול או התנגשות.", "danger")
    return redirect(url_for("unresolved.unresolved_detail", raw_name_encoded=raw_name_encoded))
