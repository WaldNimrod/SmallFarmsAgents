"""Ingestion runs list, detail, and background pipeline trigger."""
from __future__ import annotations

import threading
from collections import Counter
from functools import partial

import sqlalchemy as sa
from datetime import datetime, timezone

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import text

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import IngestionRun, SchedulerConfig
from organic_market_agent.scheduler.pipeline import run_pipeline
from organic_market_agent.scheduler.run_ingestion import _get_active_sources_with_profiles

bp = Blueprint("runs", __name__)

_IR_STATUS_HE = {
    "running": "רץ",
    "completed": "הושלם",
    "partial": "חלקי",
    "failed": "נכשל",
}

_SFR_STATUS_HE = {
    "success": "הצלחה",
    "failed": "נכשל",
    "running": "רץ",
    "skipped": "דולג",
    "timeout": "פג זמן",
}


@bp.route("/runs")
def runs_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT id, run_type, status, started_at, finished_at,
                   sources_total, sources_succeeded, sources_failed, community_sources_succeeded,
                   (SELECT COUNT(*) FROM pipeline_alerts pa
                    WHERE pa.ingestion_run_id = ir.id) AS alert_count
            FROM ingestion_runs ir
            ORDER BY id DESC
            LIMIT 50
            """
        )
    ).all()
    items = []
    any_running = False
    for r in rows:
        started_at, finished_at = r[3], r[4]
        duration_secs = None
        if started_at is not None and finished_at is not None:
            duration_secs = int((finished_at - started_at).total_seconds())
        st = r[2]
        if st == "running":
            any_running = True
        items.append(
            {
                "id": r[0],
                "run_type": r[1],
                "status": st,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_secs": duration_secs,
                "sources_total": r[5],
                "sources_succeeded": r[6],
                "sources_failed": r[7],
                "community_sources_succeeded": r[8],
                "alert_count": int(r[9] or 0),
            }
        )
    st_counter = Counter(i["status"] for i in items)
    run_status_segments = [
        (_IR_STATUS_HE.get(st, st), st_counter[st]) for st in sorted(st_counter.keys())
    ]
    total_runs = int(
        session.execute(text("SELECT COUNT(*) FROM ingestion_runs")).scalar_one() or 0
    )
    seen_ids: set[int] = set()
    trigger_sources: list[dict[str, str]] = []
    for src, _prof in _get_active_sources_with_profiles(session):
        if src.id in seen_ids:
            continue
        seen_ids.add(src.id)
        trigger_sources.append({"code": src.code, "name": src.name or src.code})
    return render_template(
        "admin/runs.html",
        items=items,
        any_running=any_running,
        run_status_segments=run_status_segments,
        runs_total=total_runs,
        trigger_sources=trigger_sources,
    )


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
    alert_rows = session.execute(
        text(
            """
            SELECT id, level, message, created_at
            FROM pipeline_alerts
            WHERE ingestion_run_id = :rid
            ORDER BY created_at ASC
            """
        ),
        {"rid": run_id},
    ).all()
    alerts = [
        {"id": a[0], "level": a[1], "message": a[2], "created_at": a[3]} for a in alert_rows
    ]
    al_c = Counter(a["level"] for a in alerts)
    alert_level_segments = [(lvl, al_c[lvl]) for lvl in sorted(al_c.keys())]
    duration_secs = None
    if run.started_at is not None and run.finished_at is not None:
        duration_secs = int((run.finished_at - run.started_at).total_seconds())
    fr = Counter(p["status"] for p in per_source)
    run_fetch_segments = [
        (_SFR_STATUS_HE.get(st, st), fr[st]) for st in sorted(fr.keys())
    ]
    return render_template(
        "admin/run_detail.html",
        run=run,
        per_source=per_source,
        alerts=alerts,
        duration_secs=duration_secs,
        run_fetch_segments=run_fetch_segments,
        alert_level_segments=alert_level_segments,
    )


@bp.route("/runs/trigger", methods=["POST"])
@login_required
def runs_trigger():
    session = g.db_session
    raw_code = (request.form.get("source_code") or "").strip()
    source_code = raw_code or None
    skip_normalize = request.form.get("skip_normalize") == "on"
    skip_publish = request.form.get("skip_publish") == "on"

    pairs = _get_active_sources_with_profiles(session)
    if source_code:
        pairs = [(s, p) for s, p in pairs if s.code == source_code]
    sources_total = len(pairs)

    sched = session.scalars(sa.select(SchedulerConfig).limit(1)).first()
    retry_attempts = sched.retry_attempts if sched is not None else 2

    run = IngestionRun(
        run_type="manual",
        triggered_by="admin",
        status="running",
        started_at=datetime.now(timezone.utc),
        sources_total=sources_total,
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
        after={
            "ingestion_run_id": rid,
            "source_code": source_code,
            "skip_normalize": skip_normalize,
            "skip_publish": skip_publish,
        },
    )
    session.commit()

    target = partial(
        run_pipeline,
        rid,
        source_code=source_code,
        skip_normalize=skip_normalize,
        skip_publish=skip_publish,
        retry_attempts=retry_attempts,
    )
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    flash("הרצה הופעלה ברקע.", "success")
    return redirect(url_for("runs.runs_list"))
