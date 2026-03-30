"""Pytest setup — env defaults before package imports that read config."""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Load .env from project root first (contains DATABASE_URL for dev Docker DB).
# override=False means: only set vars that are NOT already in the environment.
_project_root = Path(__file__).resolve().parents[1]
load_dotenv(_project_root / ".env", override=False)

# Fallback if .env is absent (CI or fresh clone): use docker-compose DB (port 5433).
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://oma:oma@127.0.0.1:5433/organic_market_agent",
)


@pytest.fixture
def db_session():
    """PostgreSQL session for integration assertions (M5 admin tests)."""
    from organic_market_agent.db.session import SessionFactory, engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not available for admin integration tests")

    session = SessionFactory()
    yield session
    session.close()


@pytest.fixture
def admin_app():
    from organic_market_agent.admin import create_app

    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(admin_app):
    return admin_app.test_client()


def admin_login(cl, email: str = "admin@local", password: str = "admin"):
    """POST login; returns response (typically 302)."""
    return cl.post("/auth/login", data={"email": email, "password": password}, follow_redirects=False)


@pytest.fixture
def logged_in_client(client, db_session):
    """Client with session cookie after successful login (skips if no admin user)."""
    from sqlalchemy import select

    from organic_market_agent.models.users import User

    u = db_session.execute(select(User).where(User.email == "admin@local")).scalar_one_or_none()
    if u is None:
        pytest.skip("admin@local user missing — run alembic upgrade through 015")
    r = admin_login(client)
    if r.status_code not in (302, 303):
        pytest.skip("Admin login failed (wrong password or DB user)")
    return client
