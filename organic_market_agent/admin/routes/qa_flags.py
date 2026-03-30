"""Read-only QA observation flags."""
from __future__ import annotations

from flask import Blueprint, g, render_template
from sqlalchemy import text

bp = Blueprint("qa_flags", __name__)


@bp.route("/qa_flags")
def qa_flags_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT of.created_at, p.code AS product_code, p.canonical_name_he,
                   s.code AS source_code, of.flag_type, of.reason,
                   COALESCE(no.normalized_price_value, no.price_amount) AS price,
                   of.is_active
            FROM observation_flags of
            LEFT JOIN products p ON p.id = of.product_id
            LEFT JOIN sources s ON s.id = of.source_id
            LEFT JOIN normalized_observations no ON no.id = of.observation_id
            ORDER BY of.created_at DESC
            LIMIT 200
            """
        )
    ).all()
    items = [
        {
            "created_at": r[0],
            "product_code": r[1],
            "canonical_name_he": r[2],
            "source_code": r[3],
            "flag_type": r[4],
            "reason": r[5],
            "price": float(r[6]) if r[6] is not None else None,
            "is_active": r[7],
        }
        for r in rows
    ]
    return render_template("admin/qa_flags.html", items=items)
