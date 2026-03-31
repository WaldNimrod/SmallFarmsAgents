"""Mark pipeline alerts read (M6) + list page and JSON export for agent handoff."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from flask import Blueprint, Response, abort, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text

from organic_market_agent.models import PipelineAlert

bp = Blueprint("alerts", __name__)

_READ_ALERTS_LIMIT = 100


def _alert_row_dict(row: tuple) -> dict:
    rid, level, message, created_at, ingestion_run_id, is_read = row
    return {
        "id": int(rid),
        "level": level,
        "message": message,
        "created_at": created_at.isoformat() if created_at else None,
        "ingestion_run_id": int(ingestion_run_id) if ingestion_run_id is not None else None,
        "is_read": bool(is_read),
    }


@bp.route("/alerts")
def alerts_list():
    """Pipeline alerts: unread (active) and optional last N read rows."""
    session = g.db_session
    show_read = request.args.get("show_read") == "1"

    unread_rows = session.execute(
        text(
            """
            SELECT id, level, message, created_at, ingestion_run_id, is_read
            FROM pipeline_alerts
            WHERE is_read = false
            ORDER BY created_at DESC
            """
        )
    ).all()

    read_rows: list[tuple] = []
    if show_read:
        read_rows = session.execute(
            text(
                """
                SELECT id, level, message, created_at, ingestion_run_id, is_read
                FROM pipeline_alerts
                WHERE is_read = true
                ORDER BY created_at DESC
                LIMIT :lim
                """
            ),
            {"lim": _READ_ALERTS_LIMIT},
        ).all()

    unread_alerts = [_alert_row_dict(r) for r in unread_rows]
    read_alerts = [_alert_row_dict(r) for r in read_rows]

    return render_template(
        "admin/alerts.html",
        unread_alerts=unread_alerts,
        read_alerts=read_alerts,
        show_read=show_read,
        read_limit=_READ_ALERTS_LIMIT,
    )


@bp.route("/alerts/export.json")
@login_required
def alerts_export_json():
    """JSON bundle for external agents (unread by default)."""
    session = g.db_session
    scope = (request.args.get("scope") or "unread").strip().lower()
    if scope == "read":
        rows = session.execute(
            text(
                """
                SELECT id, level, message, created_at, ingestion_run_id, is_read
                FROM pipeline_alerts
                WHERE is_read = true
                ORDER BY created_at DESC
                LIMIT :lim
                """
            ),
            {"lim": _READ_ALERTS_LIMIT},
        ).all()
    elif scope == "all":
        rows = session.execute(
            text(
                """
                SELECT id, level, message, created_at, ingestion_run_id, is_read
                FROM pipeline_alerts
                ORDER BY created_at DESC
                LIMIT 500
                """
            )
        ).all()
    else:
        scope = "unread"
        rows = session.execute(
            text(
                """
                SELECT id, level, message, created_at, ingestion_run_id, is_read
                FROM pipeline_alerts
                WHERE is_read = false
                ORDER BY created_at DESC
                """
            )
        ).all()

    alerts = [_alert_row_dict(r) for r in rows]
    payload = {
        "schema": "pipeline_alerts_export_v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "scope": scope,
        "count": len(alerts),
        "alerts": alerts,
    }
    fn = f"pipeline_alerts_{scope}.json"
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str),
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@bp.route("/alerts/<int:alert_id>/read", methods=["POST"])
@login_required
def alert_mark_read(alert_id: int):
    session = g.db_session
    row = session.get(PipelineAlert, alert_id)
    if row is None:
        abort(404)
    row.is_read = True
    session.commit()
    return redirect(request.referrer or url_for("alerts.alerts_list"))


@bp.route("/alerts/read-all", methods=["POST"])
@login_required
def alerts_mark_all_read():
    session = g.db_session
    session.execute(text("UPDATE pipeline_alerts SET is_read = true WHERE is_read = false"))
    session.commit()
    return redirect(request.referrer or url_for("alerts.alerts_list"))
