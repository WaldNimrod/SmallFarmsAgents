"""Product aliases list and create (M5)."""
from __future__ import annotations

import sqlalchemy as sa
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import Product, ProductAlias, Source

bp = Blueprint("aliases", __name__)


@bp.route("/aliases")
def alias_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT pa.id, pa.alias_text, p.code, p.canonical_name_he,
                   COALESCE(s.code, 'גלובלי') AS scope, pa.created_at
            FROM product_aliases pa
            JOIN products p ON p.id = pa.product_id
            LEFT JOIN sources s ON s.id = pa.source_id
            WHERE pa.is_active = true
            ORDER BY pa.alias_text
            LIMIT 500
            """
        )
    ).all()
    items = [
        {
            "id": r[0],
            "alias_text": r[1],
            "product_code": r[2],
            "canonical_name_he": r[3],
            "scope": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]
    return render_template("admin/aliases.html", items=items)


@bp.route("/aliases/new", methods=["GET", "POST"])
@login_required
def alias_new():
    session = g.db_session
    products = session.execute(
        sa.select(Product.code, Product.canonical_name_he)
        .where(Product.is_active.is_(True))
        .order_by(Product.display_order, Product.code)
    ).all()
    product_rows = [{"code": r[0], "name": r[1]} for r in products]
    src_rows = session.execute(
        sa.select(Source.id, Source.code, Source.name)
        .where(Source.is_active.is_(True))
        .order_by(Source.code)
    ).all()
    sources_opts = [{"id": r[0], "code": r[1], "name": r[2]} for r in src_rows]

    if request.method == "POST":
        code = (request.form.get("product_code") or "").strip()
        alias_text = (request.form.get("alias_text") or "").strip()
        sid_raw = request.form.get("source_id") or ""
        source_id = int(sid_raw) if sid_raw.isdigit() else None
        if not code or not alias_text:
            flash("יש למלא קוד מוצר וטקסט אליאס.", "danger")
            return render_template(
                "admin/alias_new.html", products=product_rows, sources=sources_opts
            )
        prod = session.execute(sa.select(Product).where(Product.code == code)).scalar_one_or_none()
        if not prod:
            flash("מוצר לא נמצא.", "danger")
            return render_template(
                "admin/alias_new.html", products=product_rows, sources=sources_opts
            )
        norm = alias_text.strip().lower()
        pa = ProductAlias(
            product_id=prod.id,
            alias_text=alias_text[:200],
            alias_text_normalized=norm[:200],
            source_id=source_id,
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
                after={"alias_text": alias_text, "product_code": code},
            )
            session.commit()
            flash("אליאס נוצר בהצלחה.", "success")
            return redirect(url_for("aliases.alias_list"))
        except IntegrityError:
            session.rollback()
            flash("אליאס כפול או התנגשות ייחודיות.", "danger")
            return render_template(
                "admin/alias_new.html", products=product_rows, sources=sources_opts
            )

    return render_template("admin/alias_new.html", products=product_rows, sources=sources_opts)


@bp.route("/aliases/<int:alias_id>/disable", methods=["POST"])
@login_required
def alias_disable(alias_id: int):
    session = g.db_session
    pa = session.get(ProductAlias, alias_id)
    if not pa:
        flash("אליאס לא נמצא.", "danger")
        return redirect(url_for("aliases.alias_list"))
    before = {"is_active": pa.is_active, "alias_text": pa.alias_text}
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
    return redirect(url_for("aliases.alias_list"))
