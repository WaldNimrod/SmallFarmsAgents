"""M5 admin app: monitoring + authenticated writes."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, g

from organic_market_agent.admin.auth import login_manager
from organic_market_agent.admin.routes import (
    aliases,
    alerts,
    audit_pages,
    auth,
    dashboard,
    diagnostics,
    maintenance,
    products,
    qa_flags,
    rules,
    runs,
    scheduler,
    scope_skip_catalog,
    sources,
    unresolved,
)
from sqlalchemy import text

from organic_market_agent.db.session import SessionFactory
from organic_market_agent.scheduler.reconcile import reconcile_stale_running_runs
from organic_market_agent.utils.logging_setup import get_logger

_logger = get_logger(__name__)


def create_app() -> Flask:
    base = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(base / "templates"),
        static_folder=str(base / "static"),
        static_url_path="/static",
    )
    app.secret_key = os.environ.get("ADMIN_SECRET_KEY", "dev-secret-change-me")

    login_manager.init_app(app)

    _reconcile_runs_once = False

    @app.before_request
    def _reconcile_stale_runs_on_startup() -> None:
        nonlocal _reconcile_runs_once
        if _reconcile_runs_once:
            return
        _reconcile_runs_once = True
        try:
            with SessionFactory() as s:
                reconcile_stale_running_runs(
                    s,
                    reason_code="process_restart",
                    create_summary_alert=True,
                )
                s.commit()
        except Exception:
            _logger.exception("admin startup: reconcile_stale_running_runs failed")

    @app.before_request
    def _open_session() -> None:
        g.db_session = SessionFactory()
        try:
            g.unread_alert_count = int(
                g.db_session.execute(
                    text("SELECT COUNT(*) FROM pipeline_alerts WHERE is_read = false")
                ).scalar_one()
            )
            g.unread_severity_alert_count = int(
                g.db_session.execute(
                    text(
                        "SELECT COUNT(*) FROM pipeline_alerts "
                        "WHERE is_read = false AND level IN ('error', 'warning')"
                    )
                ).scalar_one()
            )
        except Exception:
            g.unread_alert_count = 0
            g.unread_severity_alert_count = 0

    @app.teardown_request
    def _close_session(exc: BaseException | None) -> None:
        sess = g.pop("db_session", None)
        if sess is not None:
            if exc is not None:
                sess.rollback()
            sess.close()

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(sources.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(unresolved.bp)
    app.register_blueprint(aliases.bp)
    app.register_blueprint(rules.bp)
    app.register_blueprint(runs.bp)
    app.register_blueprint(scheduler.bp)
    app.register_blueprint(alerts.bp)
    app.register_blueprint(qa_flags.bp)
    app.register_blueprint(audit_pages.bp)
    app.register_blueprint(diagnostics.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(scope_skip_catalog.bp)

    return app
