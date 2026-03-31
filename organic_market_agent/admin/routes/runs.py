"""Ingestion runs list, detail, and background pipeline trigger."""
from __future__ import annotations

import json
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
from organic_market_agent.scheduler.pipeline_cancel import request_cancel
from organic_market_agent.scheduler.reconcile import reconcile_stale_running_runs
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
                    WHERE pa.ingestion_run_id = ir.id) AS alert_count,
                   ir.progress_json
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
                "progress": r[10] if isinstance(r[10], dict) else None,
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
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unresolvable,
                   sfr.http_status,
                   sfr.error_message,
                   sfr.finished_at,
                   sfr.retry_count
            FROM source_fetch_runs sfr
            JOIN sources s ON s.id = sfr.source_id
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE sfr.ingestion_run_id = :rid
            GROUP BY s.id, s.code, s.name, sfr.status, sfr.id,
                     sfr.http_status, sfr.error_message, sfr.finished_at, sfr.retry_count
            ORDER BY s.code, sfr.id
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
            "http_status": r[6],
            "error_message": (r[7] or "").strip() or None,
            "fetch_finished_at": r[8],
            "retry_count": int(r[9] or 0),
        }
        for r in rows
    ]
    sfr_count = int(
        session.execute(
            text(
                "SELECT COUNT(*) FROM source_fetch_runs WHERE ingestion_run_id = :rid"
            ),
            {"rid": run_id},
        ).scalar_one()
        or 0
    )

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

    log_rows = session.execute(
        text(
            """
            SELECT id, level, module, message, created_at, extra_json
            FROM log_entries
            WHERE ingestion_run_id = :rid
            ORDER BY created_at DESC
            LIMIT 100
            """
        ),
        {"rid": run_id},
    ).all()
    run_logs = [
        {
            "id": r[0],
            "level": r[1],
            "module": r[2],
            "message": r[3],
            "created_at": r[4],
            "extra_json": (
                json.dumps(r[5], ensure_ascii=False, default=str) if r[5] is not None else None
            ),
        }
        for r in log_rows
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
    run_status_he = _IR_STATUS_HE.get(run.status, run.status)
    return render_template(
        "admin/run_detail.html",
        run=run,
        per_source=per_source,
        alerts=alerts,
        duration_secs=duration_secs,
        run_fetch_segments=run_fetch_segments,
        alert_level_segments=alert_level_segments,
        run_status_he=run_status_he,
        sfr_status_he=_SFR_STATUS_HE,
        sfr_count=sfr_count,
        run_logs=run_logs,
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

    if not pairs:
        if source_code:
            flash(
                f"לא נמצא מקור פעיל עם קוד «{source_code}» ופרופיל איסוף פעיל — לא נוצרה הרצה. "
                "בדקו שהמקור והפרופיל פעילים ברשימת המקורות.",
                "warning",
            )
        else:
            flash(
                "אין מקורות פעילים עם פרופיל איסוף — לא נוצרה הרצה.",
                "warning",
            )
        return redirect(url_for("runs.runs_list"))

    sched = session.scalars(
        sa.select(SchedulerConfig).order_by(SchedulerConfig.id).limit(1).with_for_update()
    ).first()
    retry_attempts = sched.retry_attempts if sched is not None else 2

    n_running = int(
        session.scalar(
            sa.select(sa.func.count()).select_from(IngestionRun).where(IngestionRun.status == "running")
        )
        or 0
    )
    if n_running > 0:
        flash(
            "כבר קיימת הרצה פעילה (סטטוס «רץ»). המתן לסיום או עצור אותה לפני הפעלה חדשה.",
            "danger",
        )
        return redirect(url_for("runs.runs_list"))

    run_notes = f"single_source:{source_code}" if source_code else None
    run = IngestionRun(
        run_type="manual",
        triggered_by="admin",
        status="running",
        started_at=datetime.now(timezone.utc),
        sources_total=sources_total,
        sources_succeeded=0,
        sources_failed=0,
        community_sources_succeeded=0,
        notes=run_notes,
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


@bp.route("/runs/stop-active", methods=["POST"])
@login_required
def runs_stop_active():
    """Mark all running ingestion runs failed; signal cooperative cancel for in-process threads."""
    session = g.db_session
    running_ids = list(
        session.scalars(
            sa.select(IngestionRun.id).where(IngestionRun.status == "running").order_by(IngestionRun.id)
        ).all()
    )
    for rid in running_ids:
        request_cancel(rid)
    if not running_ids:
        flash("אין הרצות במצב «רץ» לעצירה.", "info")
        return redirect(url_for("runs.runs_list"))

    reconcile_stale_running_runs(
        session,
        reason_code="admin_stop_all",
        message_prefix="Admin stopped active ingestion run(s) (stop-all).",
        create_summary_alert=True,
    )
    audit_write(
        session,
        "stop_active_runs",
        "ingestion_run",
        entity_id=None,
        after={"run_ids": running_ids, "count": len(running_ids)},
    )
    session.commit()
    flash(
        f"סומנו {len(running_ids)} הרצה/ות כנכשלות ונשלח אות ביטול לתהליכים פעילים באותו שרת. "
        "אם הופעל כפתור בזמן שהצינור רץ באותו תהליך, הוא אמור להיפסק בין שלבים.",
        "warning",
    )
    return redirect(url_for("runs.runs_list"))
