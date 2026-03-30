"""Pytest setup — env defaults before package imports that read config."""
import os

# Importing organic_market_agent.utils (via utils.checksum, etc.) loads config.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://organic_market_agent:organic_market_agent@127.0.0.1:5432/organic_market_agent_test",
)
