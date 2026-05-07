"""Ingestion runs list, detail, and background pipeline trigger."""
from __future__ import annotations

import json
import threading
from collections import Counter
from datetime import datetime, timezone
from functools import partial
from typing import Any

import sqlalchemy as sa
from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for
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

_SORT_ACTIVE_SENTINEL = "999999999"  # table sort: running jobs last on ascending duration


def _started_at_short(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    u = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return u.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M") + " UTC"


def _duration_human(secs: int) -> str:
    if secs < 60:
        return f"{secs} שנ׳"
    if secs < 3600:
        m, s = divmod(secs, 60)
        return f"{m} דק׳ {s} שנ׳" if s else f"{m} דק׳"
    h, r = divmod(secs, 3600)
    m = r // 60
    return f"{h} שע׳ {m} דק׳" if m else f"{h} שע׳"


def _duration_cell(
    status: str, started_at: datetime | None, finished_at: datetime | None
) -> tuple[str, str]:
    """(display_text, data-sort-value for sortable table)."""
    if status == "running" and finished_at is None:
        return "פעיל", _SORT_ACTIVE_SENTINEL
    if started_at is None or finished_at is None:
        return "—", ""
    secs = max(0, int((finished_at - started_at).total_seconds()))
    return _duration_human(secs), str(secs)


def _health_tier(
    status: str,
    sources_failed: int,
    sources_total: int,
    raw_items: int,
) -> str:
    if status == "failed":
        return "danger"
    if status == "running":
        return "info"
    if status == "partial" or (sources_total > 0 and sources_failed > 0):
        return "warning"
    if status == "completed" and sources_total == 0 and raw_items == 0:
        return "secondary"
    return "success"


def _health_summary_he(
    status: str,
    sources_total: int,
    sources_succeeded: int,
    sources_failed: int,
    sfr_count: int,
    raw_items: int,
    normalized_items: int,
) -> str:
    parts = [
        f"סטטוס {status}",
        f"מקורות בתכנון {sources_total}",
        f"ריצות fetch {sfr_count}",
        f"הצלחו/נכשלו {sources_succeeded}/{sources_failed}",
        f"פריטים גולמיים {raw_items}",
        f"נורמלו {normalized_items}",
    ]
    return " · ".join(parts)


def _run_ingestion_row_dict(run: IngestionRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "run_type": run.run_type,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "sources_total": run.sources_total,
        "sources_succeeded": run.sources_succeeded,
        "sources_failed": run.sources_failed,
        "community_sources_succeeded": run.community_sources_succeeded,
        "triggered_by": run.triggered_by,
        "notes": run.notes,
        "progress_json": run.progress_json,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }


def _executive_lead_he(
    run: IngestionRun,
    sfr_count: int,
    raw_total: int,
    norm_total: int,
) -> str:
    prog = run.progress_json if isinstance(run.progress_json, dict) else {}
    phase = prog.get("phase") or "—"
    if run.status == "running":
        return f"הריצה פעילה כרגע. שלב צינור אחרון שנרשם: {phase}."
    if sfr_count == 0 and (run.sources_total or 0) > 0:
        return (
            "לא נרשמה אף ריצת fetch למקור — כנראה שהצינור לא הגיע ל־CollectorEngine "
            "או שבוצעה רק שלבים מחוץ לאיסוף (למשל CLI ללא יצירת SFR)."
        )
    if run.status == "failed":
        return "הריצה מסומנת כנכשלת — עיינו בהתראות צינור וביומן הטכני למטה."
    if run.status == "partial":
        return (
            f"הריצה חלקית: {run.sources_failed} מקורות נכשלו מתוך {run.sources_total} בתכנון, "
            f"{raw_total} פריטים גולמיים, {norm_total} נורמלו."
        )
    if raw_total == 0 and (run.sources_total or 0) > 0:
        return (
            "אין פריטים גולמיים שנשמרו — ייתכן דילוג על נכס כפול, כשל fetch, או מקור ללא תוכן שנפרס."
        )
    return (
        f"סיכום: {norm_total} פריטים נורמלו מתוך {raw_total} גולמיים; "
        f"{sfr_count} ריצות fetch; מקורות בתכנון {run.sources_total}, הצליחו {run.sources_succeeded}."
    )


def _collect_run_export(session, run_id: int) -> dict[str, Any]:
    run = session.get(IngestionRun, run_id)
    if not run:
        return {}
    rows = session.execute(
        text(
            """
            SELECT s.id, sfr.id, s.code, s.name, sfr.status,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status != 'ignored') AS items,
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
            "source_id": int(r[0]),
            "source_fetch_run_id": int(r[1]),
            "code": r[2],
            "name": r[3],
            "status": r[4],
            "items": int(r[5] or 0),
            "resolved": int(r[6] or 0),
            "unresolvable": int(r[7] or 0),
            "http_status": r[8],
            "error_message": (r[9] or "").strip() or None,
            "fetch_finished_at": r[10].isoformat() if r[10] else None,
            "retry_count": int(r[11] or 0),
        }
        for r in rows
    ]
    tot = session.execute(
        text(
            """
            SELECT COUNT(rei.id) FILTER (WHERE rei.extraction_status != 'ignored'),
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized')
            FROM source_fetch_runs sfr
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE sfr.ingestion_run_id = :rid
            """
        ),
        {"rid": run_id},
    ).one()
    raw_total, norm_total = int(tot[0] or 0), int(tot[1] or 0)
    sfr_count = int(
        session.execute(
            text("SELECT COUNT(*) FROM source_fetch_runs WHERE ingestion_run_id = :rid"),
            {"rid": run_id},
        ).scalar_one()
        or 0
    )
    alert_rows = session.execute(
        text(
            """
            SELECT id, level, message, created_at, is_read
            FROM pipeline_alerts
            WHERE ingestion_run_id = :rid
            ORDER BY created_at ASC
            """
        ),
        {"rid": run_id},
    ).all()
    alerts = [
        {
            "id": a[0],
            "level": a[1],
            "message": a[2],
            "created_at": a[3].isoformat() if a[3] else None,
            "is_read": bool(a[4]),
        }
        for a in alert_rows
    ]
    log_rows = session.execute(
        text(
            """
            SELECT id, level, module, message, created_at, extra_json
            FROM log_entries
            WHERE ingestion_run_id = :rid
            ORDER BY created_at DESC
            LIMIT 200
            """
        ),
        {"rid": run_id},
    ).all()
    logs = [
        {
            "id": lr[0],
            "level": lr[1],
            "module": lr[2],
            "message": lr[3],
            "created_at": lr[4].isoformat() if lr[4] else None,
            "extra_json": lr[5],
        }
        for lr in log_rows
    ]
    return {
        "ingestion_run": _run_ingestion_row_dict(run),
        "totals": {
            "source_fetch_runs": sfr_count,
            "raw_extracted_items": raw_total,
            "normalized_items": norm_total,
        },
        "source_fetch_runs": per_source,
        "pipeline_alerts": alerts,
        "log_entries": logs,
    }


@bp.route("/runs")
def runs_list():
    session = g.db_session
    rows = session.execute(
        text(
            """
            SELECT ir.id, ir.run_type, ir.status, ir.started_at, ir.finished_at,
                   ir.sources_total, ir.sources_succeeded, ir.sources_failed,
                   ir.community_sources_succeeded,
                   ir.progress_json,
                   (SELECT COUNT(*) FROM pipeline_alerts pa
                    WHERE pa.ingestion_run_id = ir.id) AS alert_count,
                   (SELECT COUNT(*) FROM pipeline_alerts pa
                    WHERE pa.ingestion_run_id = ir.id AND pa.level = 'error') AS alert_error_count,
                   (SELECT COUNT(*) FROM pipeline_alerts pa
                    WHERE pa.ingestion_run_id = ir.id AND pa.level = 'warning') AS alert_warning_count,
                   (SELECT COUNT(*) FROM source_fetch_runs sfr
                    WHERE sfr.ingestion_run_id = ir.id) AS sfr_count,
                   (SELECT COUNT(rei.id) FROM source_fetch_runs sfr
                    JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
                    WHERE sfr.ingestion_run_id = ir.id
                      AND rei.extraction_status != 'ignored') AS raw_items_count,
                   (SELECT COUNT(rei.id) FROM source_fetch_runs sfr
                    JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
                    WHERE sfr.ingestion_run_id = ir.id
                      AND rei.extraction_status = 'normalized') AS normalized_items_count,
                   (SELECT STRING_AGG(line, '; ' ORDER BY line)
                    FROM (
                        SELECT DISTINCT TRIM(s.code || ' — ' || COALESCE(s.name, '')) AS line
                        FROM source_fetch_runs sfr2
                        JOIN sources s ON s.id = sfr2.source_id
                        WHERE sfr2.ingestion_run_id = ir.id
                    ) u) AS sources_agg,
                   ir.triggered_by,
                   ir.notes
            FROM ingestion_runs ir
            ORDER BY ir.id DESC
            LIMIT 50
            """
        )
    ).all()
    items = []
    any_running = False
    for r in rows:
        started_at, finished_at = r[3], r[4]
        st = r[2]
        if st == "running":
            any_running = True
        dur_label, dur_sort = _duration_cell(st, started_at, finished_at)
        src_total = int(r[5] or 0)
        src_ok = int(r[6] or 0)
        src_fail = int(r[7] or 0)
        community_ok = int(r[8] or 0)
        prog = r[9]
        alert_ct = int(r[10] or 0)
        alert_err = int(r[11] or 0)
        alert_warn = int(r[12] or 0)
        sfr_ct = int(r[13] or 0)
        raw_ct = int(r[14] or 0)
        norm_ct = int(r[15] or 0)
        agg = (r[16] or "") or ""
        if len(agg) > 220:
            agg = agg[:217] + "…"
        triggered_by = r[17] or "—"
        notes = (r[18] or "").strip()
        items.append(
            {
                "id": r[0],
                "run_type": r[1],
                "status": st,
                "triggered_by": triggered_by,
                "notes": notes,
                "started_at": started_at,
                "started_at_short": _started_at_short(started_at),
                "finished_at": finished_at,
                "duration_display": dur_label,
                "duration_sort_value": dur_sort,
                "sources_total": src_total,
                "sources_succeeded": src_ok,
                "sources_failed": src_fail,
                "community_sources_succeeded": community_ok,
                "alert_count": alert_ct,
                "alert_error_count": alert_err,
                "alert_warning_count": alert_warn,
                "sfr_count": sfr_ct,
                "raw_items_count": raw_ct,
                "normalized_items_count": norm_ct,
                "sources_agg": agg,
                "health_tier": _health_tier(st, src_fail, src_total, raw_ct),
                "health_line": f"{raw_ct} פעילים · {norm_ct} נורמלו",
                "health_summary": _health_summary_he(
                    st, src_total, src_ok, src_fail, sfr_ct, raw_ct, norm_ct
                ),
                "progress": prog if isinstance(prog, dict) else None,
            }
        )
    st_counter = Counter(i["status"] for i in items)
    run_status_segments = [
        (_IR_STATUS_HE.get(st, st), st_counter[st]) for st in sorted(st_counter.keys())
    ]
    total_runs = int(
        session.execute(text("SELECT COUNT(*) FROM ingestion_runs")).scalar_one() or 0
    )
    stale_running_count = int(
        session.execute(
            text(
                "SELECT COUNT(*) FROM ingestion_runs "
                "WHERE status = 'running' "
                "AND started_at < NOW() - INTERVAL '30 minutes'"
            )
        ).scalar_one() or 0
    )
    last_success_row = session.execute(
        text(
            "SELECT started_at FROM ingestion_runs "
            "WHERE status IN ('completed', 'partial') AND sources_succeeded > 0 "
            "ORDER BY id DESC LIMIT 1"
        )
    ).first()
    last_success_at = _started_at_short(last_success_row[0]) if last_success_row else "—"
    real_runs_total = int(
        session.execute(
            text(
                "SELECT COUNT(*) FROM ingestion_runs "
                "WHERE triggered_by != 'test' AND sources_total > 0"
            )
        ).scalar_one() or 0
    )
    real_runs_ok = int(
        session.execute(
            text(
                "SELECT COUNT(*) FROM ingestion_runs "
                "WHERE triggered_by != 'test' AND sources_succeeded > 0"
            )
        ).scalar_one() or 0
    )
    success_rate = f"{real_runs_ok}/{real_runs_total}" if real_runs_total else "—"
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
        stale_running_count=stale_running_count,
        last_success_at=last_success_at,
        success_rate=success_rate,
    )


@bp.route("/runs/<int:run_id>/export.json")
@login_required
def run_export_json(run_id: int):
    """Structured JSON for manager analysis (items capped in log_entries)."""
    payload = _collect_run_export(g.db_session, run_id)
    if not payload:
        abort(404)
    return Response(
        json.dumps(payload, ensure_ascii=False, default=str),
        mimetype="application/json; charset=utf-8",
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
            SELECT s.id, sfr.id, s.code, s.name, sfr.status,
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status != 'ignored') AS items,
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
            "source_id": int(r[0]),
            "source_fetch_run_id": int(r[1]),
            "code": r[2],
            "name": r[3],
            "status": r[4],
            "items": int(r[5] or 0),
            "resolved": int(r[6] or 0),
            "unresolvable": int(r[7] or 0),
            "http_status": r[8],
            "error_message": (r[9] or "").strip() or None,
            "fetch_finished_at": r[10],
            "retry_count": int(r[11] or 0),
        }
        for r in rows
    ]
    tot_row = session.execute(
        text(
            """
            SELECT COUNT(rei.id) FILTER (WHERE rei.extraction_status != 'ignored'),
                   COUNT(rei.id) FILTER (WHERE rei.extraction_status = 'normalized')
            FROM source_fetch_runs sfr
            LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
            WHERE sfr.ingestion_run_id = :rid
            """
        ),
        {"rid": run_id},
    ).one()
    raw_items_total = int(tot_row[0] or 0)
    normalized_items_total = int(tot_row[1] or 0)
    sfr_count = int(
        session.execute(
            text(
                "SELECT COUNT(*) FROM source_fetch_runs WHERE ingestion_run_id = :rid"
            ),
            {"rid": run_id},
        ).scalar_one()
        or 0
    )
    executive_lead = _executive_lead_he(run, sfr_count, raw_items_total, normalized_items_total)
    # One row per source: retries create multiple SFR rows with the same source_id.
    failed_by_source: dict[int, dict[str, Any]] = {}
    for p in per_source:
        st = str(p.get("status") or "").strip().lower()
        if st != "failed":
            continue
        sid = int(p["source_id"])
        prev = failed_by_source.get(sid)
        if prev is None or int(p["source_fetch_run_id"]) > int(prev["source_fetch_run_id"]):
            failed_by_source[sid] = p
    failed_fetch_rows = list(failed_by_source.values())
    failed_fetch_rows.sort(key=lambda x: (x.get("code") or ""))
    if failed_fetch_rows:
        parts: list[str] = []
        for p in failed_fetch_rows:
            code = p.get("code") or "?"
            nm = (p.get("name") or "").strip()
            tail = f" ({nm})" if nm else ""
            parts.append(f"«{code}»{tail} — SFR #{p.get('source_fetch_run_id', '?')}")
        executive_lead = (
            executive_lead
            + " כשל איסוף (fetch) בפועל עבור: "
            + " · ".join(parts)
            + "."
        )
    executive_tier = _health_tier(
        run.status, run.sources_failed, run.sources_total, raw_items_total
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
    duration_display, _ = _duration_cell(run.status, run.started_at, run.finished_at)
    fr = Counter(p["status"] for p in per_source)
    run_fetch_segments = [
        (_SFR_STATUS_HE.get(st, st), fr[st]) for st in sorted(fr.keys())
    ]
    run_status_he = _IR_STATUS_HE.get(run.status, run.status)
    return render_template(
        "admin/run_detail.html",
        run=run,
        per_source=per_source,
        failed_fetch_rows=failed_fetch_rows,
        alerts=alerts,
        duration_secs=duration_secs,
        duration_display=duration_display,
        run_fetch_segments=run_fetch_segments,
        alert_level_segments=alert_level_segments,
        run_status_he=run_status_he,
        sfr_status_he=_SFR_STATUS_HE,
        sfr_count=sfr_count,
        run_logs=run_logs,
        executive_lead=executive_lead,
        executive_tier=executive_tier,
        raw_items_total=raw_items_total,
        normalized_items_total=normalized_items_total,
        started_at_short=_started_at_short(run.started_at),
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


@bp.route("/runs/reconcile-stale", methods=["POST"])
@login_required
def runs_reconcile_stale():
    """Manually mark stale running rows as failed (replaces the old auto-reconcile on page load)."""
    session = g.db_session
    affected = reconcile_stale_running_runs(
        session,
        reason_code="admin_manual_reconcile",
        create_summary_alert=True,
    )
    audit_write(
        session,
        "manual_reconcile",
        "ingestion_run",
        entity_id=None,
        after={"affected": affected},
    )
    session.commit()
    if affected:
        flash(f"סומנו {len(affected)} הרצה/ות ישנות כנכשלות.", "warning")
    else:
        flash("אין הרצות ישנות לניקוי.", "info")
    return redirect(url_for("runs.runs_list"))


@bp.route("/runs/upload-now", methods=["POST"])
@login_required
def runs_upload_now():
    """Manually push existing publish artifacts to uPress via WP REST (primary) or FTPS fallback."""
    from pathlib import Path as _Path

    from organic_market_agent.publisher.upload_dispatch import (
        NoUploadConfigured,
        dispatch_upload,
    )

    output_dir = _Path("output/public")
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        flash("לא נמצא manifest.json — יש להפעיל ריצת צינור מלאה לפני דחיפה לשרת.", "danger")
        return redirect(url_for("runs.runs_list"))

    try:
        result = dispatch_upload(output_dir)
    except NoUploadConfigured:
        flash(
            "לא הוגדרה שיטת העלאה — הגדר UPRESS_WP_APP_USER/PASS לממשק WP REST, "
            "או UPRESS_FALLBACK_FTPS=1 + פרטי FTPS.",
            "danger",
        )
        return redirect(url_for("runs.runs_list"))
    except Exception as exc:
        flash(f"שגיאת העלאה: {exc}", "danger")
        return redirect(url_for("runs.runs_list"))

    session = g.db_session
    audit_write(
        session,
        "manual_upload",
        "publish",
        entity_id=None,
        after={
            "protocol": result.protocol_used,
            "success_count": result.success_count,
            "total_count": result.total_count,
            "errors": result.errors,
            "success": result.success,
        },
    )
    session.commit()

    if result.success:
        flash(f"הועלו {result.success_count} קבצים/נכסים לשרת בהצלחה ({result.protocol_used}).", "success")
    else:
        err_detail = "; ".join(result.errors) if result.errors else "ראו לוגים"
        flash(
            f"העלאה חלקית: {result.success_count} הצליחו, "
            f"{result.total_count - result.success_count} נכשלו — {err_detail}",
            "danger",
        )
    return redirect(url_for("runs.runs_list"))
