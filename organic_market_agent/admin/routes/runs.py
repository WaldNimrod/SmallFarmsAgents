"""Ingestion runs list, detail, and background pipeline trigger."""
from __future__ import annotations

import threading

from flask import Blueprint, abort, flash, g, redirect, render_template, url_for
from flask_login import login_required
from sqlalchemy import text

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import IngestionRun
from organic_market_agent.scheduler.pipeline import run_pipeline

bp = Blueprint("runs", __name__)


@bp.route("/runs")
def runs_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT id, run_type, status, started_at, finished_at,
                   sources_total, sources_succeeded, sources_failed, community_sources_succeeded
            FROM ingestion_runs
            ORDER BY id DESC
            LIMIT 20
            """
        )
    ).all()
    items = [
        {
            "id": r[0],
            "run_type": r[1],
            "status": r[2],
            "started_at": r[3],
            "finished_at": r[4],
            "sources_total": r[5],
            "sources_succeeded": r[6],
            "sources_failed": r[7],
            "community_sources_succeeded": r[8],
        }
        for r in rows
    ]
    return render_template("admin/runs.html", items=items)


@bp.route("/runs/<int:run_id>")
def run_detail(run_id: int):
    session = g.db_session
    run = session.get(IngestionRun, run_id)
    if not run:
        abort(404)
    rows = session.execute(
        text(
            """
            SELECT s.code, s.name, sfr.status,
                   COUNT(rei.id) AS items,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized') AS resolved,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unresolvable
            FROM source_fetch_runs sfr
            JOIN sources s ON s.id = sfr.source_id
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE sfr.ingestion_run_id = :rid
            GROUP BY s.id, s.code, s.name, sfr.status, sfr.id
            ORDER BY s.code
            """
        ),
        {"rid": run_id},
    ).all()
    per_source = [
        {
            "code": r[0],
            "name": r[1],
            "status": r[2],
            "items": int(r[3] or 0),
            "resolved": int(r[4] or 0),
            "unresolvable": int(r[5] or 0),
        }
        for r in rows
    ]
    return render_template("admin/run_detail.html", run=run, per_source=per_source)


@bp.route("/runs/trigger", methods=["POST"])
@login_required
def runs_trigger():
    session = g.db_session
    run = IngestionRun(
        run_type="manual",
        triggered_by="admin",
        status="running",
        sources_total=0,
        sources_succeeded=0,
        sources_failed=0,
        community_sources_succeeded=0,
    )
    session.add(run)
    session.flush()
    rid = run.id
    audit_write(
        session,
        "trigger_run",
        "ingestion_run",
        entity_id=rid,
        after={"ingestion_run_id": rid},
    )
    session.commit()

    thread = threading.Thread(target=run_pipeline, args=(rid,), daemon=True)
    thread.start()
    flash("הרצה הופעלה ברקע.", "success")
    return redirect(url_for("runs.runs_list"))
