"""Product suggestions + pending aliases — quick-approval queues."""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import (
    PendingProductAlias,
    Product,
    ProductAlias,
    ProductCatalogSuggestion,
    Source,
)

bp = Blueprint("catalog_inbox", __name__, url_prefix="/catalog")


def _norm_alias(s: str) -> str:
    import re

    return re.sub(r"\s+", " ", s.strip().lower())


@bp.route("/suggestions")
def suggestions_list():
    session = g.db_session
    status = (request.args.get("status") or "pending").strip()
    if status not in ("pending", "approved", "rejected", "all"):
        status = "pending"
    q = sa.select(ProductCatalogSuggestion).order_by(ProductCatalogSuggestion.created_at.desc())
    if status != "all":
        q = q.where(ProductCatalogSuggestion.status == status)
    rows = list(session.scalars(q).all())
    return render_template(
        "admin/catalog_suggestions_list.html",
        suggestions=rows,
        filter_status=status,
    )


@bp.route("/suggestions/new", methods=["GET", "POST"])
@login_required
def suggestions_new():
    session = g.db_session
    if request.method == "POST":
        name = (request.form.get("canonical_name_he") or "").strip()
        code = (request.form.get("proposed_code") or "").strip() or None
        notes = (request.form.get("notes") or "").strip() or None
        if not name:
            flash("Canonical Hebrew name is required.", "danger")
            return redirect(url_for("catalog_inbox.suggestions_new"))
        row = ProductCatalogSuggestion(
            canonical_name_he=name[:200],
            proposed_code=code[:32] if code else None,
            notes=notes,
            status="pending",
        )
        session.add(row)
        session.commit()
        flash("Suggestion saved as pending.", "success")
        return redirect(url_for("catalog_inbox.suggestions_list"))
    return render_template("admin/catalog_suggestions_new.html")


@bp.route("/suggestions/<int:sid>/status", methods=["POST"])
@login_required
def suggestions_set_status(sid: int):
    session = g.db_session
    new_status = (request.form.get("status") or "").strip()
    if new_status not in ("approved", "rejected", "pending"):
        flash("Invalid status.", "danger")
        return redirect(url_for("catalog_inbox.suggestions_list"))
    row = session.get(ProductCatalogSuggestion, sid)
    if not row:
        abort(404)
    row.status = new_status
    session.commit()
    flash(f"Suggestion #{sid} → {new_status}.", "success")
    return redirect(url_for("catalog_inbox.suggestions_list", status="all"))


@bp.route("/pending-aliases")
def pending_aliases_list():
    session = g.db_session
    status = (request.args.get("status") or "pending").strip()
    if status not in ("pending", "approved", "rejected", "all"):
        status = "pending"
    q = (
        sa.select(PendingProductAlias, Product.code, Product.canonical_name_he)
        .join(Product, PendingProductAlias.product_id == Product.id)
        .order_by(PendingProductAlias.created_at.desc())
    )
    if status != "all":
        q = q.where(PendingProductAlias.status == status)
    rows_raw = session.execute(q).all()
    rows = [
        {
            "row": r[0],
            "product_code": r[1],
            "product_name_he": r[2],
        }
        for r in rows_raw
    ]
    products_for_select = session.execute(
        sa.select(Product.code, Product.canonical_name_he)
        .where(Product.is_active.is_(True))
        .order_by(Product.canonical_name_he)
    ).all()
    sources_for_select = session.execute(
        sa.select(Source.id, Source.code, Source.name).where(Source.is_active.is_(True)).order_by(Source.code)
    ).all()
    return render_template(
        "admin/pending_aliases_list.html",
        items=rows,
        filter_status=status,
        products_for_select=products_for_select,
        sources_for_select=sources_for_select,
    )


@bp.route("/pending-aliases/new", methods=["POST"])
@login_required
def pending_aliases_new():
    session = g.db_session
    alias_text = (request.form.get("alias_text") or "").strip()
    product_code = (request.form.get("product_code") or "").strip()
    notes = (request.form.get("notes") or "").strip() or None
    src_raw = (request.form.get("source_id") or "").strip()
    source_id = int(src_raw) if src_raw.isdigit() else None
    if not alias_text or not product_code:
        flash("Alias text and product are required.", "danger")
        return redirect(url_for("catalog_inbox.pending_aliases_list"))
    prod = session.execute(sa.select(Product).where(Product.code == product_code)).scalar_one_or_none()
    if not prod:
        flash("Product code not found.", "danger")
        return redirect(url_for("catalog_inbox.pending_aliases_list"))
    norm = _norm_alias(alias_text)[:200]
    row = PendingProductAlias(
        product_id=prod.id,
        alias_text=alias_text[:200],
        alias_text_normalized=norm,
        source_id=source_id,
        status="pending",
        notes=notes,
    )
    session.add(row)
    try:
        session.commit()
        flash("Pending alias created.", "success")
    except IntegrityError:
        session.rollback()
        flash("Could not create pending row (duplicate?).", "danger")
    return redirect(url_for("catalog_inbox.pending_aliases_list"))


@bp.route("/pending-aliases/<int:aid>/approve", methods=["POST"])
@login_required
def pending_aliases_approve(aid: int):
    session = g.db_session
    pending = session.get(PendingProductAlias, aid)
    if not pending or pending.status != "pending":
        flash("Not found or not pending.", "danger")
        return redirect(url_for("catalog_inbox.pending_aliases_list"))
    pa = ProductAlias(
        product_id=pending.product_id,
        alias_text=pending.alias_text,
        alias_text_normalized=pending.alias_text_normalized,
        source_id=pending.source_id,
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
            after={
                "alias_text": pending.alias_text,
                "from_pending_id": pending.id,
            },
        )
        pending.status = "approved"
        pending.reviewed_at = datetime.now(timezone.utc)
        session.commit()
        flash(
            "Alias approved and inserted. Run: python3 -m organic_market_agent catalog_renormalize",
            "success",
        )
    except IntegrityError:
        session.rollback()
        flash("Alias already exists (unique conflict).", "danger")
    return redirect(url_for("catalog_inbox.pending_aliases_list", status="all"))


@bp.route("/pending-aliases/<int:aid>/reject", methods=["POST"])
@login_required
def pending_aliases_reject(aid: int):
    session = g.db_session
    pending = session.get(PendingProductAlias, aid)
    if not pending or pending.status != "pending":
        flash("Not found or not pending.", "danger")
        return redirect(url_for("catalog_inbox.pending_aliases_list"))
    pending.status = "rejected"
    pending.reviewed_at = datetime.now(timezone.utc)
    session.commit()
    flash("Pending alias rejected.", "info")
    return redirect(url_for("catalog_inbox.pending_aliases_list", status="all"))
