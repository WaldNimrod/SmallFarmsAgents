"""Admin maintenance actions (baseline snapshot, catalog re-normalize) — no CLI required."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from flask import Blueprint, flash, g, redirect, url_for
from flask_login import login_required

from organic_market_agent.admin.audit import audit_write
from organic_market_agent.admin.baseline_metrics import write_baseline_snapshot_file
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.maintenance.catalog_renormalize import run_catalog_renormalize
from organic_market_agent.models import PipelineAlert
from organic_market_agent.utils.logging_setup import get_logger

bp = Blueprint("maintenance", __name__)
_logger = get_logger(__name__)


def _catalog_renormalize_bg() -> None:
    try:
        stats = run_catalog_renormalize()
        parts = [
            f"requeued={stats.unresolvable_requeued}",
            f"normalized={stats.normalizer_resolved}",
            f"still_unresolvable={stats.normalizer_unresolvable}",
            f"aggregate_date={stats.aggregate_date.isoformat()}",
            f"publish_ok={stats.publish_ok}",
        ]
        if stats.publish_error:
            parts.append(f"publish_error={stats.publish_error!r}")
        level = "warning" if (stats.publish_error or not stats.publish_ok) else "info"
        msg = "[MAINTENANCE:catalog_renormalize] " + ", ".join(parts)
        with SessionFactory() as s:
            s.add(PipelineAlert(level=level, message=msg, ingestion_run_id=None))
            s.commit()
    except Exception as exc:  # noqa: BLE001 — surface any failure as alert + log
        _logger.exception("catalog_renormalize background job failed")
        with SessionFactory() as s:
            s.add(
                PipelineAlert(
                    level="error",
                    message=f"[MAINTENANCE:catalog_renormalize] failed: {exc}",
                    ingestion_run_id=None,
                )
            )
            s.commit()


@bp.route("/maintenance/save-baseline", methods=["POST"])
@login_required
def save_baseline():
    session = g.db_session
    try:
        path = write_baseline_snapshot_file(session)
    except OSError as exc:
        flash(f"שמירת בסיס נכשלה: {exc}", "danger")
        return redirect(url_for("dashboard.index"))
    audit_write(
        session,
        "save_normalizer_baseline",
        "file",
        entity_id=None,
        after={"path": str(path)},
    )
    session.commit()
    flash(f"נשמר קובץ בסיס להשוואה: {path.name}", "success")
    return redirect(url_for("dashboard.index"))


@bp.route("/maintenance/catalog-renormalize", methods=["POST"])
@login_required
def catalog_renormalize_start():
    session = g.db_session
    audit_write(
        session,
        "trigger_catalog_renormalize",
        "maintenance",
        entity_id=None,
        after={"started_at": datetime.now(timezone.utc).isoformat()},
    )
    session.commit()
    thread = threading.Thread(target=_catalog_renormalize_bg, daemon=True)
    thread.start()
    flash(
        "נרמול קטלוג הופעל ברקע (שורות «לא ניתן» הוחזרו לתור). "
        "סיום יופיע בהתראות — אין צורך להריץ סקריפט מהטרמינל.",
        "success",
    )
    return redirect(url_for("dashboard.index"))
