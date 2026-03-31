"""Dashboard KPIs — GET /"""
from __future__ import annotations

import json

import sqlalchemy as sa
from flask import Blueprint, g, render_template
from sqlalchemy import text

from organic_market_agent.admin.baseline_metrics import (
    compute_normalizer_snapshot,
    diff_against_baseline,
    load_baseline_json,
    resolve_baseline_path,
)
from organic_market_agent.db.session import engine
from organic_market_agent.models import IngestionRun, NormalizedObservation, Product, Source
from organic_market_agent.utils.data_quality_snapshot import compute_raw_pipeline_counts

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


def _json_chart_unres_7d(session):
    rows = session.execute(
        text(
            """
            SELECT (rei.extracted_at AT TIME ZONE 'UTC')::date AS day,
                   COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
                   COUNT(*) AS total
            FROM raw_extracted_items rei
            WHERE (rei.extracted_at AT TIME ZONE 'UTC')::date >=
                  (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - interval '6 days'
              AND (rei.extracted_at AT TIME ZONE 'UTC')::date <=
                  (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
            GROUP BY day
            ORDER BY day
            """
        )
    ).all()
    data = []
    for r in rows:
        day = r[0]
        u, t = int(r[1] or 0), int(r[2] or 0)
        data.append(
            {
                "day": day.isoformat() if hasattr(day, "isoformat") else str(day),
                "unresolvable": u,
                "total": t,
                "rate_pct": round(100.0 * u / t, 1) if t else 0.0,
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
              COUNT(*) FILTER (WHERE extraction_status = 'unresolvable') AS unres_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'extracted') AS ext_cnt,
              COUNT(*) FILTER (WHERE extraction_status = 'ignored') AS ign_cnt
            FROM raw_extracted_items
            """
        )
    ).one()
    norm_cnt = int(res[0] or 0)
    unres_cnt = int(res[1] or 0)
    ext_cnt = int(res[2] or 0)
    ign_cnt = int(res[3] or 0)
    denom = norm_cnt + unres_cnt
    resolution_pct = round(100.0 * norm_cnt / denom, 1) if denom else 0.0

    rolling_src_7d = int(
        session.execute(
            text(
                """
                SELECT COUNT(DISTINCT no.source_id)
                FROM normalized_observations no
                LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
                WHERE (no.observed_at AT TIME ZONE 'UTC')::date >=
                      (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date - interval '6 days'
                  AND (no.observed_at AT TIME ZONE 'UTC')::date <=
                      (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')::date
                  AND no.market_scope = 'community'
                  AND no.flag_status = 'ok'
                  AND (rei.id IS NULL OR rei.is_quarantined IS NOT TRUE)
                """
            )
        ).scalar_one()
        or 0
    )

    top_unres_src = session.execute(
        text(
            """
            SELECT s.code,
                   COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable')::int AS u
            FROM raw_extracted_items rei
            JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.extracted_at >= now() - interval '30 days'
            GROUP BY s.code
            HAVING COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') > 0
            ORDER BY u DESC
            LIMIT 3
            """
        )
    ).all()

    snapshot_now = compute_normalizer_snapshot(session)
    baseline_file = load_baseline_json(resolve_baseline_path())
    baseline_diff = diff_against_baseline(snapshot_now, baseline_file) if baseline_file else None
    data_quality_snapshot = compute_raw_pipeline_counts(session)

    chart_resolution_json = _json_chart_resolution(session)
    chart_sources_json = _json_chart_sources(session)
    chart_unres_7d_json = _json_chart_unres_7d(session)

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
        rei_normalized=norm_cnt,
        rei_unresolvable=unres_cnt,
        rei_extracted_pending=ext_cnt,
        rei_ignored=ign_cnt,
        rolling_community_sources_7d=rolling_src_7d,
        top_unresolvable_sources=top_unres_src,
        baseline_diff=baseline_diff,
        baseline_path_hint=str(resolve_baseline_path()),
        chart_resolution_json=chart_resolution_json,
        chart_sources_json=chart_sources_json,
        chart_unres_7d_json=chart_unres_7d_json,
        unread_alerts=unread_alerts,
        data_quality_snapshot=data_quality_snapshot,
        database_url_display=_database_url_display(),
    )
