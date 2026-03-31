"""Mark pipeline alerts read (M6)."""
from __future__ import annotations

from flask import Blueprint, abort, g, redirect, request, url_for
from flask_login import login_required
from sqlalchemy import text

from organic_market_agent.models import PipelineAlert

bp = Blueprint("alerts", __name__)


@bp.route("/alerts/<int:alert_id>/read", methods=["POST"])
@login_required
def alert_mark_read(alert_id: int):
    session = g.db_session
    row = session.get(PipelineAlert, alert_id)
    if row is None:
        abort(404)
    row.is_read = True
    session.commit()
    return redirect(request.referrer or url_for("dashboard.index"))


@bp.route("/alerts/read-all", methods=["POST"])
@login_required
def alerts_mark_all_read():
    session = g.db_session
    session.execute(text("UPDATE pipeline_alerts SET is_read = true WHERE is_read = false"))
    session.commit()
    return redirect(url_for("dashboard.index"))
