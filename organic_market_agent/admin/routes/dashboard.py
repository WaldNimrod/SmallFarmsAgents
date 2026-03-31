"""Dashboard KPIs — GET /"""
from __future__ import annotations

import json

import sqlalchemy as sa
from flask import Blueprint, g, render_template
from sqlalchemy import text

from organic_market_agent.db.session import engine
from organic_market_agent.models import IngestionRun, NormalizedObservation, Product, Source

bp = Blueprint("dashboard", __name__)


def _database_url_display() -> str:
    """Sanitized DB URL for confirming admin and CLI use the same target."""
    try:
        return engine.url.render_as_string(hide_password=True)
    except Exception:
        return "(unavailable)"


def _json_chart_resolution(session):
    rows = session.execute(
        text(
            """
            SELECT
                ir.finished_at::date AS day,
                COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized') AS resolved,
                COUNT(rei.id) AS total
            FROM ingestion_runs ir
            LEFT JOIN source_fetch_runs sfr ON sfr.ingestion_run_id = ir.id
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE ir.finished_at >= now() - interval '14 days'
              AND ir.status IN ('completed','partial')
            GROUP BY day
            ORDER BY day
            """
        )
    ).all()
    data = []
    for r in rows:
        day = r[0]
        data.append(
            {
                "day": day.isoformat() if hasattr(day, "isoformat") else str(day),
                "resolved": int(r[1] or 0),
                "total": int(r[2] or 0),
            }
        )
    return json.dumps(data)


def _json_chart_sources(session):
    rows = session.execute(
        text(
            """
            SELECT id, started_at::date AS day, sources_succeeded, sources_failed, status
            FROM ingestion_runs
            WHERE started_at >= now() - interval '14 days'
            ORDER BY started_at
            """
        )
    ).all()
    data = []
    for r in rows:
        day = r[1]
        data.append(
            {
                "id": int(r[0]),
                "day": day.isoformat() if hasattr(day, "isoformat") else str(day),
                "sources_succeeded": int(r[2] or 0),
                "sources_failed": int(r[3] or 0),
                "status": r[4],
            }
        )
    return json.dumps(data)


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
    total_products_active = session.execute(
        sa.select(sa.func.count()).select_from(Product).where(Product.is_active.is_(True))
    ).scalar_one()
    total_products_all = session.execute(
        sa.select(sa.func.count()).select_from(Product)
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

    chart_resolution_json = _json_chart_resolution(session)
    chart_sources_json = _json_chart_sources(session)

    alert_rows = session.execute(
        text(
            """
            SELECT id, level, message, created_at, ingestion_run_id
            FROM pipeline_alerts
            WHERE is_read = false
            ORDER BY
              CASE level
                WHEN 'error' THEN 0
                WHEN 'warning' THEN 1
                ELSE 2
              END,
              created_at DESC
            LIMIT 10
            """
        )
    ).all()
    unread_alerts = [
        {
            "id": a[0],
            "level": a[1],
            "message": a[2],
            "created_at": a[3],
            "ingestion_run_id": a[4],
        }
        for a in alert_rows
    ]

    return render_template(
        "admin/dashboard.html",
        active_sources=active_sources,
        products_covered=products_covered,
        total_products_catalog=total_products_active,
        total_products_all=total_products_all,
        total_observations=total_obs,
        last_run=last_run,
        resolution_pct=resolution_pct,
        chart_resolution_json=chart_resolution_json,
        chart_sources_json=chart_sources_json,
        unread_alerts=unread_alerts,
        database_url_display=_database_url_display(),
    )
