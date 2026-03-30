"""M4 read-only admin monitoring dashboard (Flask)."""
from __future__ import annotations

from pathlib import Path

from flask import Flask, g

from organic_market_agent.admin.routes import dashboard, products, sources, unresolved
from organic_market_agent.db.session import SessionFactory


def create_app() -> Flask:
    base = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        template_folder=str(base / "templates"),
        static_folder=None,
    )

    @app.before_request
    def _open_session() -> None:
        g.db_session = SessionFactory()

    @app.teardown_request
    def _close_session(exc: BaseException | None) -> None:
        sess = g.pop("db_session", None)
        if sess is not None:
            sess.close()

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(sources.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(unresolved.bp)

    return app
