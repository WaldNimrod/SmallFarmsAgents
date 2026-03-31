"""Read-only catalog of approved V1 scope-skip rules (numbered)."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from flask import Blueprint, Response, g, render_template
from flask_login import login_required
from sqlalchemy import select

from organic_market_agent.models import CatalogScopeSkipRule

bp = Blueprint("scope_skip_catalog", __name__)


@bp.route("/catalog/scope-skip")
def scope_skip_list():
    session = g.db_session
    rows = list(
        session.scalars(
            select(CatalogScopeSkipRule).order_by(CatalogScopeSkipRule.display_order)
        ).all()
    )
    return render_template("admin/scope_skip_catalog.html", rules=rows)


@bp.route("/catalog/scope-skip/export.json")
@login_required
def scope_skip_export_json():
    session = g.db_session
    rows = list(
        session.scalars(
            select(CatalogScopeSkipRule).order_by(CatalogScopeSkipRule.display_order)
        ).all()
    )
    payload = {
        "schema": "catalog_scope_skip_rules_export_v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "rules": [
            {
                "id": r.id,
                "display_order": r.display_order,
                "category_code": r.category_code,
                "match_type": r.match_type,
                "pattern": r.pattern,
                "notes": r.notes,
                "future_product_code": r.future_product_code,
                "is_active": r.is_active,
            }
            for r in rows
        ],
    }
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="catalog_scope_skip_rules.json"'},
    )
