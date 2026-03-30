"""Dashboard KPIs — GET /"""
from __future__ import annotations

import sqlalchemy as sa
from flask import Blueprint, g, render_template

from organic_market_agent.models import IngestionRun, NormalizedObservation, Product, Source

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    session = g.db_session
    active_sources = session.execute(
        sa.select(sa.func.count()).select_from(Source).where(Source.is_active.is_(True))
    ).scalar_one()
    products_covered = session.execute(
        sa.select(sa.func.count(sa.distinct(NormalizedObservation.product_id))).select_from(
            NormalizedObservation
        )
    ).scalar_one()
    total_obs = session.execute(
        sa.select(sa.func.count()).select_from(NormalizedObservation)
    ).scalar_one()
    last_run = session.execute(sa.select(sa.func.max(IngestionRun.finished_at))).scalar_one()
    total_products = session.execute(
        sa.select(sa.func.count()).select_from(Product).where(Product.is_active.is_(True))
    ).scalar_one()

    res = session.execute(
        sa.text(
            """
            SELECT
              COUNT(*) FILTER (WHERE extraction_status = 'normalized') AS norm_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unres_cnt
            FROM raw_extracted_items
            """
        )
    ).one()
    norm_cnt, unres_cnt = int(res[0] or 0), int(res[1] or 0)
    denom = norm_cnt + unres_cnt
    resolution_pct = round(100.0 * norm_cnt / denom, 1) if denom else 0.0

    return render_template(
        "admin/dashboard.html",
        active_sources=active_sources,
        products_covered=products_covered,
        total_products_catalog=total_products,
        total_observations=total_obs,
        last_run=last_run,
        resolution_pct=resolution_pct,
    )
