"""Scheduler config and fetch-run cleanup (M6)."""
from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import select, text

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.models import SchedulerConfig

bp = Blueprint("scheduler", __name__)


def _get_config(session) -> SchedulerConfig | None:
    return session.scalars(select(SchedulerConfig).order_by(SchedulerConfig.id).limit(1)).first()


@bp.route("/scheduler")
@login_required
def scheduler_page():
    session = g.db_session
    cfg = _get_config(session)
    if cfg is None:
        flash("חסרה שורת הגדרות תזמון.", "danger")
        return redirect(url_for("dashboard.index"))
    return render_template("admin/scheduler.html", cfg=cfg)


@bp.route("/scheduler/update", methods=["POST"])
@login_required
def scheduler_update():
    session = g.db_session
    cfg = _get_config(session)
    if cfg is None:
        flash("חסרה שורת הגדרות תזמון.", "danger")
        return redirect(url_for("dashboard.index"))

    try:
        run_hour = int(request.form.get("run_hour", "6"))
        run_minute = int(request.form.get("run_minute", "0"))
        retry_attempts = int(request.form.get("retry_attempts", "2"))
        cleanup_after_days = int(request.form.get("cleanup_after_days", "90"))
    except (TypeError, ValueError):
        flash("ערכים לא תקינים.", "danger")
        return redirect(url_for("scheduler.scheduler_page"))

    cleanup_enabled = request.form.get("cleanup_enabled") == "on"
    upload_enabled = request.form.get("upload_enabled") == "on"

    if not (0 <= run_hour <= 23):
        flash("שעה חייבת להיות 0–23.", "danger")
        return redirect(url_for("scheduler.scheduler_page"))
    if not (0 <= run_minute <= 59):
        flash("דקה חייבת להיות 0–59.", "danger")
        return redirect(url_for("scheduler.scheduler_page"))
    if not (0 <= retry_attempts <= 10):
        flash("ניסיונות חוזרים: 0–10.", "danger")
        return redirect(url_for("scheduler.scheduler_page"))
    if cleanup_after_days < 7:
        flash("ימי ניקוי: לפחות 7.", "danger")
        return redirect(url_for("scheduler.scheduler_page"))

    before = {
        "run_hour": cfg.run_hour,
        "run_minute": cfg.run_minute,
        "retry_attempts": cfg.retry_attempts,
        "cleanup_enabled": cfg.cleanup_enabled,
        "cleanup_after_days": cfg.cleanup_after_days,
        "upload_enabled": cfg.upload_enabled,
    }
    cfg.run_hour = run_hour
    cfg.run_minute = run_minute
    cfg.retry_attempts = retry_attempts
    cfg.cleanup_enabled = cleanup_enabled
    cfg.cleanup_after_days = cleanup_after_days
    cfg.upload_enabled = upload_enabled
    cfg.updated_at = datetime.now(timezone.utc)

    audit_write(
        session,
        "update_scheduler",
        "scheduler_config",
        entity_id=cfg.id,
        before=before,
        after={
            "run_hour": run_hour,
            "run_minute": run_minute,
            "retry_attempts": retry_attempts,
            "cleanup_enabled": cleanup_enabled,
            "cleanup_after_days": cleanup_after_days,
            "upload_enabled": upload_enabled,
        },
    )
    session.commit()
    flash("הגדרות תזמון נשמרו.", "success")
    return redirect(url_for("scheduler.scheduler_page"))


@bp.route("/scheduler/toggle", methods=["POST"])
@login_required
def scheduler_toggle():
    session = g.db_session
    cfg = _get_config(session)
    if cfg is None:
        flash("חסרה שורת הגדרות תזמון.", "danger")
        return redirect(url_for("dashboard.index"))

    prev = cfg.is_enabled
    cfg.is_enabled = not cfg.is_enabled
    cfg.updated_at = datetime.now(timezone.utc)
    audit_write(
        session,
        "toggle_scheduler",
        "scheduler_config",
        entity_id=cfg.id,
        before={"is_enabled": prev},
        after={"is_enabled": cfg.is_enabled},
    )
    session.commit()
    flash("מצב תזמון עודכן.", "success")
    return redirect(url_for("scheduler.scheduler_page"))


@bp.route("/scheduler/run-cleanup", methods=["POST"])
@login_required
def scheduler_run_cleanup():
    session = g.db_session
    cfg = _get_config(session)
    if cfg is None:
        flash("חסרה שורת הגדרות תזמון.", "danger")
        return redirect(url_for("dashboard.index"))

    days = cfg.cleanup_after_days
    result = session.execute(
        text(
            """
            WITH deleted AS (
                DELETE FROM source_fetch_runs
                WHERE started_at < now() - make_interval(days => :days)
                  AND ingestion_run_id IN (
                      SELECT id FROM ingestion_runs
                      WHERE status IN ('completed', 'partial', 'failed')
                  )
                RETURNING id
            )
            SELECT COUNT(*) AS n FROM deleted
            """
        ),
        {"days": days},
    )
    n = int(result.scalar_one() or 0)

    cfg.cleanup_last_run = datetime.now(timezone.utc)
    cfg.updated_at = cfg.cleanup_last_run
    audit_write(
        session,
        "run_cleanup",
        "scheduler_config",
        entity_id=cfg.id,
        after={"deleted_source_fetch_runs": n, "days": days},
    )
    session.commit()
    flash(f"נוקו {n} רשומות.", "success")
    return redirect(url_for("scheduler.scheduler_page"))
