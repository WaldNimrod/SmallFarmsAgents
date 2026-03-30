# Mandate — Team 20: M1 Local Foundation
**From:** Team 100 (Architecture)  
**Date:** 2026-03-29  
**Milestone:** M1 — Local Foundation  
**Gate:** G1  
**Priority:** Critical — all downstream milestones depend on this

---

## M1 Scope

M1 is pure infrastructure. No collectors, parsers, normalizer, or admin UI.
Deliverables only:
- Python project skeleton (`organic_market_agent/` package)
- PostgreSQL + Alembic + all 23 tables
- SQLAlchemy 2.x models
- Seed data (units, products, sources, aliases)
- Utils: logging, config, checksum, db health check

**Success criterion:** `python -m organic_market_agent.db.check` → PASS.
`pytest tests/` → all PASS.

---

## Step 0: Local Environment Setup

> **Stack update (2026-03-30):** PostgreSQL runs via Docker only.
> Homebrew PostgreSQL has been removed. Do NOT use `brew install postgresql`.

### 0.1 Start PostgreSQL via Docker

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# Option A — fresh install (creates oma-postgres on port 5433):
docker-compose up -d
docker-compose ps   # verify: oma-postgres is Up and healthy

# Option B — use existing oma-g2-ev container (already has G2 data, port 55435):
docker ps | grep oma   # verify it is running
```

Verify connectivity:
```bash
# Option A
docker exec oma-postgres psql -U oma -d organic_market_agent -c "SELECT version();"

# Option B
docker exec oma-g2-ev psql -U oma -d organic -c "SELECT version();"
```

### 0.2 Database setup (Option A — fresh container only)

For the `oma-postgres` docker-compose container, the `POSTGRES_USER`, `POSTGRES_DB`,
and `POSTGRES_PASSWORD` are already created by the Docker image on first start.
**No `createdb` or `createuser` needed.**

Then run migrations:
```bash
alembic upgrade head
python -m organic_market_agent.db.check
```

### 0.3 Create `.env` File

```bash
# Copy example and set DATABASE_URL for your container:
cp .env.example .env
```

Edit `.env`:
```bash
# For oma-g2-ev (current dev DB — G2 data intact):
DATABASE_URL=postgresql://oma:t@localhost:55435/organic

# OR for fresh oma-postgres (docker-compose):
DATABASE_URL=postgresql://oma:oma@localhost:5433/organic_market_agent

RAW_FILES_ROOT=/Users/nimrod/Documents/SmallFarmsAgents/raw_files
LOG_LEVEL=INFO
ENVIRONMENT=local
```

### 0.4 Python venv

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

## Step 1: Project Structure

### 1.1 Create Directory Tree

```bash
mkdir -p organic_market_agent/{collectors,parsers,normalizer,aggregator,qa}
mkdir -p organic_market_agent/{publisher/templates,admin/{routes,templates,static}}
mkdir -p organic_market_agent/{models,db/versions,scheduler,utils}
mkdir -p tests/upress_validation
```

### 1.2 Create `__init__.py` in Every Directory

```bash
find organic_market_agent -type d | xargs -I {} touch {}/__init__.py
touch tests/__init__.py
```

### 1.3 `requirements.txt`

```
# Core DB
sqlalchemy>=2.0.0,<3.0
alembic>=1.13.0,<2.0
psycopg2-binary>=2.9.0,<3.0
python-dotenv>=1.0.0,<2.0

# CLI
click>=8.1.0,<9.0

# HTTP (M2+)
httpx>=0.27.0,<1.0
beautifulsoup4>=4.12.0,<5.0
lxml>=5.2.0,<6.0

# Web (M5+)
flask>=3.0.0,<4.0
jinja2>=3.1.0,<4.0
flask-login>=0.6.0,<1.0
passlib[bcrypt]>=1.7.0,<2.0

# Publish (M7+)
ftputil>=5.0.0,<6.0
paramiko>=3.4.0,<4.0

# Utils
python-dateutil>=2.9.0,<3.0

# Testing
pytest>=8.0.0,<9.0
pytest-cov>=5.0.0,<6.0

# Code quality
black>=24.0.0,<25.0
ruff>=0.4.0,<1.0
```

### 1.4 `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "organic-market-agent"
version = "0.1.0"
requires-python = ">=3.11"
description = "OrganicMarketAgent — community organic vegetable price index (MyFarmAgents)"

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 1.5 `.gitignore`

```
.env
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
raw_files/
*.log
dist/
build/
*.egg-info/
```

---

## Step 2: Config + Utils

### `organic_market_agent/utils/config.py`

```python
"""
Central config loader.
All settings come from environment variables loaded from .env at project root.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


class Config:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    RAW_FILES_ROOT: Path = Path(os.getenv("RAW_FILES_ROOT", "/tmp/organic_market_agent_raw"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    EMAIL_SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST", "")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", 587))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.RAW_FILES_ROOT.mkdir(parents=True, exist_ok=True)
        (cls.RAW_FILES_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


config = Config()
```

### `organic_market_agent/utils/logging_setup.py`

```python
"""
Structured logging setup.
All modules import get_logger from here.
"""
import logging
import sys
from organic_market_agent.utils.config import config


def get_logger(module_name: str) -> logging.Logger:
    """Returns a configured logger for the given module name."""
    logger = logging.getLogger(f"organic_market_agent.{module_name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
        logger.propagate = False
    return logger
```

### `organic_market_agent/utils/checksum.py`

```python
"""SHA-256 checksum utilities for raw asset deduplication."""
import hashlib
from pathlib import Path


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
```

### `organic_market_agent/utils/__init__.py`

```python
from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger
from organic_market_agent.utils.checksum import sha256_of_bytes, sha256_of_file

__all__ = ["config", "get_logger", "sha256_of_bytes", "sha256_of_file"]
```

---

## Step 3: DB Layer

### `organic_market_agent/db/base.py`

```python
"""SQLAlchemy declarative base shared by all models."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

### `organic_market_agent/db/session.py`

```python
"""DB engine and session factory."""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from organic_market_agent.utils.config import config
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger("db.session")

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session() -> Session:
    """Context manager providing a transactional DB session."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### `organic_market_agent/db/__init__.py`

```python
from organic_market_agent.db.session import get_session, engine
from organic_market_agent.db.base import Base

__all__ = ["get_session", "engine", "Base"]
```

---

## Step 4: SQLAlchemy Models

> All models use SQLAlchemy 2.x Mapped/mapped_column style.
> All timestamps are `TIMESTAMP(timezone=True)`.
> All prices are `Numeric(12, 4)` — never `float`.

### `organic_market_agent/models/measurement.py`

```python
"""measurement_units and unit_conversions tables."""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Numeric, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base


class MeasurementUnit(Base):
    __tablename__ = "measurement_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, unique=True)
    name_he: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    unit_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    is_normalizable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<MeasurementUnit code={self.code!r}>"


class UnitConversion(Base):
    __tablename__ = "unit_conversions"
    __table_args__ = (
        UniqueConstraint("from_unit_id", "to_unit_id", "product_id", name="uq_unit_conversion"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    to_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    factor: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    conversion_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/products.py`

```python
"""products, product_aliases, product_variants, product_merges tables."""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    VARCHAR, Boolean, TIMESTAMP, Numeric, Text, Integer,
    ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, unique=True)
    canonical_name_he: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    category: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    default_measurement_unit_id: Mapped[int] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=False
    )
    is_organic_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_basket_product: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    seasonality_notes: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    aliases: Mapped[list["ProductAlias"]] = relationship("ProductAlias", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product code={self.code!r} name={self.canonical_name_he!r}>"


class ProductAlias(Base):
    __tablename__ = "product_aliases"
    __table_args__ = (
        UniqueConstraint("alias_text_normalized", "source_id", name="uq_alias_text_source"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    alias_text: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    alias_text_normalized: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    normalizer_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=True
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, default=Decimal("1.0")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="aliases")


class ProductMerge(Base):
    __tablename__ = "product_merges"
    __table_args__ = (
        UniqueConstraint("source_product_id", name="uq_product_merge"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    target_product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    merged_by: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/sources.py`

```python
"""sources and source_fetch_profiles tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    source_group: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="candidate")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    legal_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    legal_review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    fetch_profiles: Mapped[list["SourceFetchProfile"]] = relationship(
        "SourceFetchProfile", back_populates="source"
    )

    def __repr__(self) -> str:
        return f"<Source code={self.code!r} name={self.name!r}>"


class SourceFetchProfile(Base):
    __tablename__ = "source_fetch_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    platform_family: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    fetch_mode: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    entry_url: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    http_method: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, default="GET")
    request_headers_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    schedule_kind: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="daily")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    retry_policy_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False,
        default={"max_retries": 2, "backoff_seconds": 60}
    )
    is_public_access: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    charset_hint: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    selector_profile: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    source: Mapped["Source"] = relationship("Source", back_populates="fetch_profiles")
```

### `organic_market_agent/models/normalizer.py`

```python
"""normalizer_profiles and normalizer_rules tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base


class NormalizerProfile(Base):
    __tablename__ = "normalizer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    normalizer_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    version: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="1.0")
    config_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    rules: Mapped[list["NormalizerRule"]] = relationship(
        "NormalizerRule", back_populates="profile"
    )


class NormalizerRule(Base):
    __tablename__ = "normalizer_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    normalizer_profile_id: Mapped[int] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=False
    )
    rule_kind: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    match_pattern: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    match_type: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, default="exact")
    replacement_value: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    extra_params_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, default="system")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profile: Mapped["NormalizerProfile"] = relationship(
        "NormalizerProfile", back_populates="rules"
    )
```

### `organic_market_agent/models/runs.py`

```python
"""ingestion_runs, source_fetch_runs, raw_assets, raw_extracted_items tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, CHAR, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="daily")
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="running")
    sources_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sources_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sources_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    community_sources_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    triggered_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, default="cron")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    source_fetch_runs: Mapped[list["SourceFetchRun"]] = relationship(
        "SourceFetchRun", back_populates="ingestion_run"
    )


class SourceFetchRun(Base):
    __tablename__ = "source_fetch_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[int] = mapped_column(ForeignKey("ingestion_runs.id"), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    fetch_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("source_fetch_profiles.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="running")
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bytes_fetched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("raw_assets.id"), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    ingestion_run: Mapped["IngestionRun"] = relationship(
        "IngestionRun", back_populates="source_fetch_runs"
    )


class RawAsset(Base):
    __tablename__ = "raw_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    storage_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    file_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    bytes_size: Mapped[int] = mapped_column(Integer, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class RawExtractedItem(Base):
    __tablename__ = "raw_extracted_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    raw_asset_id: Mapped[int] = mapped_column(ForeignKey("raw_assets.id"), nullable=False)
    normalizer_profile_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalizer_profiles.id"), nullable=True
    )
    raw_product_name: Mapped[Optional[str]] = mapped_column(VARCHAR(300), nullable=True)
    raw_price_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_unit_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_quantity_text: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    raw_payload_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    extraction_status: Mapped[str] = mapped_column(
        VARCHAR(20), nullable=False, default="extracted"
    )
    unresolvable_reason: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/observations.py`

```python
"""normalized_observations and observation_flags tables."""
from decimal import Decimal
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Text, ForeignKey, Numeric, CHAR, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from organic_market_agent.db.base import Base


class NormalizedObservation(Base):
    __tablename__ = "normalized_observations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source_fetch_run_id: Mapped[int] = mapped_column(
        ForeignKey("source_fetch_runs.id"), nullable=False
    )
    raw_extracted_item_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("raw_extracted_items.id"), nullable=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_variant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_variants.id"), nullable=True
    )
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[str] = mapped_column(VARCHAR(30), nullable=False)
    is_benchmark: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_basket_product: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_organic_claimed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="ILS")
    display_unit_id: Mapped[int] = mapped_column(ForeignKey("measurement_units.id"), nullable=False)
    normalized_price_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    normalized_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    normalization_method: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), nullable=False, default=Decimal("1.0")
    )
    flag_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="ok")
    flag_reason: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class ObservationFlag(Base):
    __tablename__ = "observation_flags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    observation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("normalized_observations.id"), nullable=True
    )
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"), nullable=True)
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    flag_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="single")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/aggregates.py`

```python
"""daily_aggregates and weekly_snapshots tables."""
from decimal import Decimal
from typing import Optional
from datetime import datetime, date
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Numeric, ForeignKey, Date, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from organic_market_agent.db.base import Base


class DailyAggregate(Base):
    __tablename__ = "daily_aggregates"
    __table_args__ = (
        UniqueConstraint(
            "aggregate_date", "product_id", "market_scope", "sales_channel",
            name="uq_daily_aggregate"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aggregate_date: Mapped[date] = mapped_column(Date, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    market_scope: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    sales_channel: Mapped[Optional[str]] = mapped_column(VARCHAR(30), nullable=True)
    is_basket_aggregate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    distinct_sources: Mapped[int] = mapped_column(Integer, nullable=False)
    min_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    unweighted_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    weighted_avg_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    median_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    stddev_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    normalized_unit_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("measurement_units.id"), nullable=True
    )
    meets_publish_threshold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_observed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/publishing.py`

```python
"""publish_runs and publish_artifacts tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, CHAR, func
from sqlalchemy.orm import Mapped, mapped_column
from organic_market_agent.db.base import Base


class PublishRun(Base):
    __tablename__ = "publish_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ingestion_runs.id"), nullable=True
    )
    run_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="auto")
    build_started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    build_finished_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    upload_started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    upload_finished_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="building")
    artifact_version: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_last_good: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    products_included: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    community_products: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    benchmark_products: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, default="auto")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class PublishArtifact(Base):
    __tablename__ = "publish_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    publish_run_id: Mapped[int] = mapped_column(ForeignKey("publish_runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    local_path: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(CHAR(64), nullable=False)
    bytes_size: Mapped[int] = mapped_column(Integer, nullable=False)
    remote_path: Mapped[Optional[str]] = mapped_column(VARCHAR(500), nullable=True)
    upload_status: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True, default="pending")
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/users.py`

```python
"""users, audit_log, log_entries tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column
from organic_market_agent.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(VARCHAR(100), nullable=True)
    role: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False, default="system")
    action: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class LogEntry(Base):
    __tablename__ = "log_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    module: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ingestion_runs.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### `organic_market_agent/models/__init__.py`

```python
"""Import all models so Alembic autogenerate detects them."""
from organic_market_agent.models.measurement import MeasurementUnit, UnitConversion
from organic_market_agent.models.products import Product, ProductAlias, ProductMerge
from organic_market_agent.models.sources import Source, SourceFetchProfile
from organic_market_agent.models.normalizer import NormalizerProfile, NormalizerRule
from organic_market_agent.models.runs import IngestionRun, SourceFetchRun, RawAsset, RawExtractedItem
from organic_market_agent.models.observations import NormalizedObservation, ObservationFlag
from organic_market_agent.models.aggregates import DailyAggregate
from organic_market_agent.models.publishing import PublishRun, PublishArtifact
from organic_market_agent.models.users import User, AuditLog, LogEntry

__all__ = [
    "MeasurementUnit", "UnitConversion",
    "Product", "ProductAlias", "ProductMerge",
    "Source", "SourceFetchProfile",
    "NormalizerProfile", "NormalizerRule",
    "IngestionRun", "SourceFetchRun", "RawAsset", "RawExtractedItem",
    "NormalizedObservation", "ObservationFlag",
    "DailyAggregate",
    "PublishRun", "PublishArtifact",
    "User", "AuditLog", "LogEntry",
]
```

---

## Step 5: Alembic Migrations

### `alembic.ini`

```ini
[alembic]
script_location = organic_market_agent/db
sqlalchemy.url = %(DATABASE_URL)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### `organic_market_agent/db/env.py`

```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import organic_market_agent.models  # noqa: F401 — registers all models
from organic_market_agent.db.base import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Migration Revisions — 5 Files

```
organic_market_agent/db/versions/
  001_initial_schema.py     # All 23 tables + 2 views + all indexes
  002_seed_units.py         # 11 measurement_units + 4 unit_conversions
  003_seed_products.py      # 29 products (PRD001–PRD029)
  004_seed_sources.py       # 20 sources + initial fetch_profiles
  005_seed_aliases.py       # product_aliases from PRODUCT_CATALOG_V1.md
```

**Critical rule for every migration:**
```python
def upgrade() -> None:
    # forward migration
    pass

def downgrade() -> None:
    # must exactly reverse upgrade — tested before submitting
    pass
```

**001 revision structure** (implement in FK-dependency order):
1. `measurement_units` → `products` → `sources`
2. `unit_conversions`, `product_aliases`, `product_variants`, `product_merges`
3. `source_fetch_profiles`
4. `normalizer_profiles` → `normalizer_rules`
5. `ingestion_runs` → `source_fetch_runs` → `raw_assets`
6. Add FK `source_fetch_runs.raw_asset_id → raw_assets.id` via `ALTER TABLE`
7. `raw_extracted_items`
8. `normalized_observations` → `observation_flags`
9. `daily_aggregates` → `weekly_snapshots`
10. `publish_runs` → `publish_artifacts`
11. `users` → `audit_log` → `log_entries`
12. `CREATE VIEW public_market_view` and `CREATE VIEW admin_observations_view`

Full SQL for each table: `docs/DATABASE_SCHEMA_SPEC_HE.md`

---

## Step 6: DB Health Check CLI

### `organic_market_agent/db/check.py`

```python
"""
DB Health Check CLI.
Usage: python -m organic_market_agent.db.check
Exit code: 0 = PASS, 1 = FAIL
"""
import sys
from sqlalchemy import text, inspect
from organic_market_agent.db.session import engine

REQUIRED_TABLES = [
    "measurement_units", "unit_conversions",
    "products", "product_aliases", "product_variants", "product_merges",
    "sources", "source_fetch_profiles",
    "normalizer_profiles", "normalizer_rules",
    "ingestion_runs", "source_fetch_runs",
    "raw_assets", "raw_extracted_items",
    "normalized_observations", "observation_flags",
    "daily_aggregates", "weekly_snapshots",
    "publish_runs", "publish_artifacts",
    "users", "audit_log", "log_entries",
]

REQUIRED_COUNTS = {
    "measurement_units": 11,
    "products": 29,
    "sources": 20,
}


def check() -> bool:
    all_pass = True
    insp = inspect(engine)
    existing = set(insp.get_table_names())

    print("OrganicMarketAgent — DB Health Check")
    print("=" * 50)

    for table in REQUIRED_TABLES:
        if table in existing:
            print(f"  OK  {table}")
        else:
            print(f"  MISSING  {table}")
            all_pass = False

    with engine.connect() as conn:
        for table, min_count in REQUIRED_COUNTS.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = "OK" if count >= min_count else "FAIL"
            print(f"  {status}  {table}: {count} rows (expected >= {min_count})")
            if count < min_count:
                all_pass = False

    print("=" * 50)
    print(f"RESULT: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    sys.exit(0 if check() else 1)
```

---

## Step 7: Tests

### `tests/test_db_health.py`

```python
"""
DB health tests — Gate G1 acceptance criteria.
Requires a running PostgreSQL DB with applied Alembic migrations.
"""
import pytest
from sqlalchemy import text, inspect
from organic_market_agent.db.session import engine
from organic_market_agent.db.check import REQUIRED_TABLES, REQUIRED_COUNTS, check


def test_all_required_tables_exist():
    insp = inspect(engine)
    existing = set(insp.get_table_names())
    missing = [t for t in REQUIRED_TABLES if t not in existing]
    assert not missing, f"Missing tables: {missing}"


def test_seed_data_counts():
    with engine.connect() as conn:
        for table, min_count in REQUIRED_COUNTS.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            assert count >= min_count, (
                f"{table}: expected >= {min_count} rows, got {count}"
            )


def test_products_have_aliases():
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT COUNT(DISTINCT product_id) FROM product_aliases "
                "WHERE is_active = true"
            )
        )
        count = result.scalar()
        assert count >= 10, f"Expected aliases for >= 10 products, got {count}"


def test_all_products_have_valid_unit():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM products p
            WHERE p.is_active = true
              AND NOT EXISTS (
                SELECT 1 FROM measurement_units mu
                WHERE mu.id = p.default_measurement_unit_id
              )
        """))
        count = result.scalar()
        assert count == 0, f"{count} products have a missing or invalid default unit"


def test_no_float_price_columns():
    """Verify no price columns are stored as float (must be NUMERIC)."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name IN ('normalized_observations', 'daily_aggregates')
              AND column_name LIKE '%price%'
              AND data_type = 'double precision'
        """))
        floats = result.fetchall()
        assert not floats, f"Found float price columns: {floats}"


def test_all_timestamp_columns_are_timestamptz():
    """All *_at columns must be TIMESTAMPTZ (timezone-aware)."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND column_name LIKE '%_at'
              AND data_type = 'timestamp without time zone'
        """))
        naive = result.fetchall()
        assert not naive, f"Found naive (non-timezone) timestamp columns: {naive}"


def test_check_cli_passes():
    assert check() is True
```

---

## Gate G1 — Submission

After completing all steps, file a report at:
`_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_M1_COMPLETE_TEAM20.md`

```markdown
# Team 20 — M1 Local Foundation Complete
**Date:** YYYY-MM-DD
**Milestone:** M1 / Gate G1
**Status:** COMPLETE

## python -m organic_market_agent.db.check output
[paste output here]

## pytest tests/test_db_health.py -v output
[paste output here]

## Deliverables Checklist
- [ ] organic_market_agent/ package (all submodules with __init__.py)
- [ ] requirements.txt, pyproject.toml, .gitignore
- [ ] utils/: config.py, logging_setup.py, checksum.py
- [ ] db/: base.py, session.py, env.py (Alembic), alembic.ini
- [ ] models/: 10 model files + __init__.py
- [ ] db/versions/: 5 migration revisions (001–005)
- [ ] Seed data: 11 units, 4 conversions, 29 products, 20 sources, aliases
- [ ] tests/test_db_health.py — all 7 tests PASS

## Requesting Team 50 sign-off on Gate G1.
```
