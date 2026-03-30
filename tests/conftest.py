"""Pytest setup — env defaults before package imports that read config."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root first (contains DATABASE_URL for dev Docker DB).
# override=False means: only set vars that are NOT already in the environment.
_project_root = Path(__file__).resolve().parents[1]
load_dotenv(_project_root / ".env", override=False)

# Fallback if .env is absent (CI or fresh clone): use docker-compose DB (port 5433).
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://oma:oma@127.0.0.1:5433/organic_market_agent",
)
