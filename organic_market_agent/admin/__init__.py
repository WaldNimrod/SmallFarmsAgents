"""M5 admin app: monitoring + authenticated writes."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, g

from organic_market_agent.admin.auth import login_manager
from organic_market_agent.admin.routes import (
    aliases,
    audit_pages,
    auth,
    dashboard,
    products,
    qa_flags,
    rules,
    runs,
    sources,
    unresolved,
)
from organic_market_agent.db.session import SessionFactory


def create_app() -> Flask:
    base = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(base / "templates"),
        static_folder=None,
    )
    app.secret_key = os.environ.get("ADMIN_SECRET_KEY", "dev-secret-change-me")

    login_manager.init_app(app)

    @app.before_request
    def _open_session() -> None:
        g.db_session = SessionFactory()

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
    app.register_blueprint(qa_flags.bp)
    app.register_blueprint(audit_pages.bp)

    return app
