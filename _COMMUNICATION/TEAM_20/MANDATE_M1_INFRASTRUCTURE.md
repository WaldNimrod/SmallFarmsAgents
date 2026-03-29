# מנדט — צוות 20: M1 Local Foundation
**מאת:** צוות 100 (ארכיטקטורה)  
**תאריך:** 2026-03-29  
**שלב:** M1 — Local Foundation  
**שער:** G1  
**עדיפות:** קריטית — כל שאר הפיתוח תלוי בזה

---

## סקירת M1

M1 הוא תשתית מקומית טהורה. אין collectors, parsers, normalizer — רק:
- Python project skeleton
- PostgreSQL + Alembic + כל 23 טבלאות
- SQLAlchemy models
- Seed data (יחידות, מוצרים, מקורות, aliases)
- Utils בסיסי (logging, config, checksum, db_check)

**תוצאה:** `python -m smallfarms.db.check` → PASS. `pytest tests/` → PASS.

---

## שלב 0: התקנת סביבה מקומית

### 0.1 בדיקת PostgreSQL

```bash
# בדוק אם PostgreSQL מותקן
psql --version

# אם לא מותקן — macOS:
brew install postgresql@15
brew services start postgresql@15
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 0.2 יצירת DB ומשתמש

```bash
# יצירת DB
createdb smallfarms_local

# יצירת משתמש ייעודי
createuser smallfarms_app
psql postgres -c "GRANT ALL ON DATABASE smallfarms_local TO smallfarms_app;"
psql smallfarms_local -c "GRANT ALL ON SCHEMA public TO smallfarms_app;"
psql smallfarms_local -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO smallfarms_app;"
psql smallfarms_local -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO smallfarms_app;"

# בדיקת חיבור
psql postgresql://smallfarms_app@localhost/smallfarms_local -c "SELECT version();"
```

### 0.3 הגדרת `.env`

```bash
# /Users/nimrod/Documents/SmallFarmsAgents/.env
DATABASE_URL=postgresql://smallfarms_app@localhost/smallfarms_local
RAW_FILES_ROOT=/Users/nimrod/Documents/SmallFarmsAgents/raw_files
LOG_LEVEL=INFO
ENVIRONMENT=local
```

### 0.4 הגדרת Python venv

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

---

## שלב 1: מבנה הפרויקט

### 1.1 צור את מבנה התיקיות

```bash
mkdir -p smallfarms/{collectors,parsers,normalizer,aggregator,qa,publisher/templates,admin/{routes,templates,static},models,db/versions,scheduler,utils,tests}
```

### 1.2 `requirements.txt`

```
# Core
sqlalchemy[postgresql]>=2.0.0,<3.0
alembic>=1.13.0,<2.0
psycopg2-binary>=2.9.0,<3.0
python-dotenv>=1.0.0,<2.0

# CLI
click>=8.1.0,<9.0

# HTTP (needed from M2 — included here for full skeleton)
httpx>=0.27.0,<1.0
beautifulsoup4>=4.12.0,<5.0
lxml>=5.2.0,<6.0

# Web (needed from M5 — included here for full skeleton)
flask>=3.0.0,<4.0
jinja2>=3.1.0,<4.0
flask-login>=0.6.0,<1.0
passlib[bcrypt]>=1.7.0,<2.0

# Publish (needed from M7 — included here for full skeleton)
ftputil>=5.0.0,<6.0
paramiko>=3.4.0,<4.0

# Utils
python-dateutil>=2.9.0,<3.0

# Testing
pytest>=8.0.0,<9.0
pytest-cov>=5.0.0,<6.0

# Code quality (dev)
black>=24.0.0,<25.0
ruff>=0.4.0,<1.0
```

### 1.3 `__init__.py` files

כל תיקיה ב-`smallfarms/` חייבת `__init__.py` ריק.

```bash
find smallfarms -type d | xargs -I {} touch {}/__init__.py
```

### 1.4 `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "smallfarms"
version = "0.1.0"
requires-python = ">=3.11"

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

## שלב 2: Config + Utils

### 2.1 `smallfarms/utils/config.py`

```python
"""
Central config loader — reads from environment variables / .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


class Config:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    RAW_FILES_ROOT: Path = Path(os.getenv("RAW_FILES_ROOT", "/tmp/smallfarms_raw"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    EMAIL_SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST", "")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", 587))
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    EMAIL_TO: str = os.getenv("EMAIL_TO", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create required local directories if they don't exist."""
        cls.RAW_FILES_ROOT.mkdir(parents=True, exist_ok=True)
        (cls.RAW_FILES_ROOT / "artifacts").mkdir(parents=True, exist_ok=True)


config = Config()
```

### 2.2 `smallfarms/utils/logging_setup.py`

```python
"""
Structured logging setup for SmallFarms.
All modules import `get_logger` from here.
"""
import logging
import sys
from smallfarms.utils.config import config


def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a logger for the given module.
    Format: YYYY-MM-DD HH:MM:SS LEVEL module message
    """
    logger = logging.getLogger(f"smallfarms.{module_name}")
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

### 2.3 `smallfarms/utils/checksum.py`

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

### 2.4 `smallfarms/utils/__init__.py`

```python
from smallfarms.utils.config import config
from smallfarms.utils.logging_setup import get_logger
from smallfarms.utils.checksum import sha256_of_bytes, sha256_of_file

__all__ = ["config", "get_logger", "sha256_of_bytes", "sha256_of_file"]
```

---

## שלב 3: DB Layer

### 3.1 `smallfarms/db/__init__.py`

```python
from smallfarms.db.session import get_session, engine
from smallfarms.db.base import Base

__all__ = ["get_session", "engine", "Base"]
```

### 3.2 `smallfarms/db/base.py`

```python
"""SQLAlchemy declarative base shared by all models."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

### 3.3 `smallfarms/db/session.py`

```python
"""DB engine and session factory."""
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from smallfarms.utils.config import config
from smallfarms.utils.logging_setup import get_logger

logger = get_logger("db.session")

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,          # reconnect on stale connections
    pool_size=5,
    max_overflow=10,
)

SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session() -> Session:
    """Context manager for DB sessions with automatic commit/rollback."""
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

---

## שלב 4: SQLAlchemy Models

### 4.1 `smallfarms/models/base.py`

```python
"""Shared mixins for all models."""
from datetime import datetime, timezone
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from smallfarms.db.base import Base  # noqa: F401 — re-exported


class TimestampMixin:
    """created_at + updated_at auto-managed columns."""
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

### 4.2 `smallfarms/models/measurement.py`

```python
"""measurement_units and unit_conversions tables."""
from decimal import Decimal
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, CheckConstraint, TIMESTAMP, Numeric, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from smallfarms.db.base import Base
from datetime import datetime


class MeasurementUnit(Base):
    __tablename__ = "measurement_units"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(VARCHAR(30), nullable=False, unique=True)
    name_he: Mapped[str] = mapped_column(VARCHAR(60), nullable=False)
    unit_type: Mapped[str] = mapped_column(
        VARCHAR(20), nullable=False,
        # CHECK constraint enforced at DB level — not repeated here for brevity
    )
    is_normalizable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    conversions_from: Mapped[list["UnitConversion"]] = relationship(
        "UnitConversion", foreign_keys="UnitConversion.from_unit_id", back_populates="from_unit"
    )
    conversions_to: Mapped[list["UnitConversion"]] = relationship(
        "UnitConversion", foreign_keys="UnitConversion.to_unit_id", back_populates="to_unit"
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

    from_unit: Mapped["MeasurementUnit"] = relationship(
        "MeasurementUnit", foreign_keys=[from_unit_id], back_populates="conversions_from"
    )
    to_unit: Mapped["MeasurementUnit"] = relationship(
        "MeasurementUnit", foreign_keys=[to_unit_id], back_populates="conversions_to"
    )
```

### 4.3 `smallfarms/models/products.py`

```python
"""products, product_aliases, product_variants, product_merges tables."""
from decimal import Decimal
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Numeric, Text, ForeignKey, Integer, UniqueConstraint, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from smallfarms.db.base import Base
from datetime import datetime


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

    default_unit: Mapped["MeasurementUnit"] = relationship(  # type: ignore[name-defined]
        "MeasurementUnit", foreign_keys=[default_measurement_unit_id]
    )
    aliases: Mapped[list["ProductAlias"]] = relationship(
        "ProductAlias", back_populates="product"
    )

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
    confidence: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=Decimal("1.0"))
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

### 4.4 `smallfarms/models/sources.py`

```python
"""sources and source_fetch_profiles tables."""
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, UniqueConstraint, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from smallfarms.db.base import Base
from datetime import datetime


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
        JSONB, nullable=False, default={"max_retries": 2, "backoff_seconds": 60}
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

### 4.5 `smallfarms/models/normalizer.py`

```python
"""normalizer_profiles and normalizer_rules tables."""
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from smallfarms.db.base import Base
from datetime import datetime


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

    profile: Mapped["NormalizerProfile"] = relationship("NormalizerProfile", back_populates="rules")
```

### 4.6 `smallfarms/models/runs.py`

```python
"""ingestion_runs, source_fetch_runs, raw_assets, raw_extracted_items tables."""
from decimal import Decimal
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, Numeric, CHAR, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from smallfarms.db.base import Base
from datetime import datetime


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
    raw_asset_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("raw_assets.id"), nullable=True
    )
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
    extraction_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=False, default="extracted")
    unresolvable_reason: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### 4.7 `smallfarms/models/observations.py`

```python
"""normalized_observations and observation_flags tables."""
from decimal import Decimal
from typing import Optional
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Text, ForeignKey, Numeric, CHAR, func
from sqlalchemy.orm import Mapped, mapped_column
from smallfarms.db.base import Base
from datetime import datetime


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
    normalized_price_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
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
```

### 4.8 `smallfarms/models/aggregates.py`

```python
"""daily_aggregates and weekly_snapshots tables."""
from decimal import Decimal
from typing import Optional
from datetime import datetime, date
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Numeric, ForeignKey, Date, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from smallfarms.db.base import Base


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

### 4.9 `smallfarms/models/publishing.py`

```python
"""publish_runs and publish_artifacts tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, CHAR, func
from sqlalchemy.orm import Mapped, mapped_column
from smallfarms.db.base import Base


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
    upload_status: Mapped[str] = mapped_column(VARCHAR(20), nullable=True, default="pending")
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
```

### 4.10 `smallfarms/models/users.py`

```python
"""users, audit_log, log_entries tables."""
from typing import Optional
from datetime import datetime
from sqlalchemy import VARCHAR, Boolean, TIMESTAMP, Integer, Text, ForeignKey, JSONB, func
from sqlalchemy.orm import Mapped, mapped_column
from smallfarms.db.base import Base


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

### 4.11 `smallfarms/models/__init__.py`

```python
"""Import all models so Alembic autogenerate can detect them."""
from smallfarms.models.measurement import MeasurementUnit, UnitConversion
from smallfarms.models.products import Product, ProductAlias, ProductMerge
from smallfarms.models.sources import Source, SourceFetchProfile
from smallfarms.models.normalizer import NormalizerProfile, NormalizerRule
from smallfarms.models.runs import IngestionRun, SourceFetchRun, RawAsset, RawExtractedItem
from smallfarms.models.observations import NormalizedObservation
from smallfarms.models.aggregates import DailyAggregate
from smallfarms.models.publishing import PublishRun, PublishArtifact
from smallfarms.models.users import User, AuditLog, LogEntry

__all__ = [
    "MeasurementUnit", "UnitConversion",
    "Product", "ProductAlias", "ProductMerge",
    "Source", "SourceFetchProfile",
    "NormalizerProfile", "NormalizerRule",
    "IngestionRun", "SourceFetchRun", "RawAsset", "RawExtractedItem",
    "NormalizedObservation",
    "DailyAggregate",
    "PublishRun", "PublishArtifact",
    "User", "AuditLog", "LogEntry",
]
```

---

## שלב 5: Alembic Migrations

### 5.1 הגדרת `alembic.ini`

```ini
[alembic]
script_location = smallfarms/db
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

### 5.2 `smallfarms/db/env.py` (Alembic env)

```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from pathlib import Path

# Load .env
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

# Replace placeholder with actual DB URL
from alembic.config import Config as AlembicConfig
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic sees them
import smallfarms.models  # noqa: F401
from smallfarms.db.base import Base
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

### 5.3 רשימת Migrations — 5 revisions

```
smallfarms/db/versions/
  001_initial_schema.py       # כל 23 טבלאות + 2 views + indexes
  002_seed_units.py           # 11 measurement_units + 4 unit_conversions
  003_seed_products.py        # 29 products (PRD001–PRD029)
  004_seed_sources.py         # 20 sources + fetch_profiles ראשוניים
  005_seed_aliases.py         # product_aliases מ-PRODUCT_CATALOG_V1.md
```

**עקרון קריטי לכל migration:**
```python
def upgrade() -> None:
    # כתוב כאן
    pass

def downgrade() -> None:
    # חייב להיות הפוך מ-upgrade
    pass
```

### 5.4 Migration 001 — Initial Schema (template)

```python
"""001_initial_schema

Revision ID: 001
Revises:
Create Date: 2026-03-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # measurement_units
    op.create_table(
        'measurement_units',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('code', sa.VARCHAR(30), nullable=False, unique=True),
        sa.Column('name_he', sa.VARCHAR(60), nullable=False),
        sa.Column('unit_type', sa.VARCHAR(20), nullable=False),
        sa.Column('is_normalizable', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "unit_type IN ('weight','count','bundle','basket','pack')",
            name='chk_mu_unit_type'
        ),
    )
    op.create_index('idx_measurement_units_code', 'measurement_units', ['code'])

    # Continue with all 23 tables in dependency order:
    # products, sources → unit_conversions, product_aliases, product_variants,
    # product_merges, source_fetch_profiles, normalizer_profiles, normalizer_rules,
    # ingestion_runs, source_fetch_runs, raw_assets (with FK alter),
    # raw_extracted_items, normalized_observations, observation_flags,
    # daily_aggregates, weekly_snapshots, publish_runs, publish_artifacts,
    # users, audit_log, log_entries
    # ... (complete per DATABASE_SCHEMA_SPEC_HE.md)


def downgrade() -> None:
    # Drop in reverse order (FK-safe)
    op.drop_table('log_entries')
    op.drop_table('audit_log')
    op.drop_table('users')
    # ... (all 23 tables in reverse)
    op.drop_table('measurement_units')
```

---

## שלב 6: DB Health Check CLI

### `smallfarms/db/check.py`

```python
"""
DB Health Check CLI.
Run: python -m smallfarms.db.check
Exit code 0 = PASS, 1 = FAIL
"""
import sys
from sqlalchemy import text, inspect
from smallfarms.db.session import engine
from smallfarms.utils.logging_setup import get_logger

logger = get_logger("db.check")

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
    """Returns True if all checks pass."""
    all_pass = True
    insp = inspect(engine)
    existing = set(insp.get_table_names())

    print("SmallFarms DB Health Check")
    print("=" * 50)

    # 1. Tables
    for table in REQUIRED_TABLES:
        if table in existing:
            print(f"  ✅ Table: {table}")
        else:
            print(f"  ❌ MISSING: {table}")
            all_pass = False

    # 2. Row counts
    with engine.connect() as conn:
        for table, min_count in REQUIRED_COUNTS.items():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            if count >= min_count:
                print(f"  ✅ {table}: {count} rows (expected >= {min_count})")
            else:
                print(f"  ❌ {table}: {count} rows (expected >= {min_count})")
                all_pass = False

    print("=" * 50)
    if all_pass:
        print("RESULT: ✅ PASS — DB is healthy")
    else:
        print("RESULT: ❌ FAIL — see errors above")

    return all_pass


if __name__ == "__main__":
    ok = check()
    sys.exit(0 if ok else 1)
```

---

## שלב 7: Tests

### `tests/test_db_health.py`

```python
"""
Tests for DB health — gate G1.
Requires a running PostgreSQL DB with applied migrations.
"""
import pytest
from sqlalchemy import text, inspect
from smallfarms.db.session import engine
from smallfarms.db.check import REQUIRED_TABLES, REQUIRED_COUNTS, check


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
            text("SELECT COUNT(DISTINCT product_id) FROM product_aliases WHERE is_active = true")
        )
        count = result.scalar()
        assert count >= 10, f"Expected aliases for >= 10 products, got {count}"


def test_all_products_have_active_unit():
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
        assert count == 0, f"{count} products have missing/invalid default unit"


def test_check_cli_passes():
    assert check() is True


def test_no_float_prices():
    """Verify numeric columns are NUMERIC (not FLOAT) — schema enforcement test."""
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


def test_all_timestamps_are_timestamptz():
    """All timestamp columns must be TIMESTAMPTZ (timezone-aware)."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND (column_name LIKE '%_at' OR column_name = 'aggregate_date')
              AND data_type = 'timestamp without time zone'
        """))
        naive = result.fetchall()
        # aggregate_date is DATE type — excluded by data_type filter
        assert not naive, f"Found naive timestamps: {naive}"
```

---

## Gate G1 — הגשת אישור

לאחר השלמת כל השלבים, כתוב דוח ב:
`_COMMUNICATION/TEAM_20/reports/2026-MM-DD_M1_COMPLETE_TEAM20.md`

```markdown
# Team 20 — M1 Local Foundation Complete
**תאריך:** YYYY-MM-DD
**שלב:** M1 / שער G1
**סטטוס:** ✅ הושלם

## פלט python -m smallfarms.db.check
[הדבק את הפלט כאן]

## פלט pytest tests/test_db_health.py -v
[הדבק את הפלט כאן]

## תוצרים שנוצרו
- [ ] smallfarms/ package structure (כל submodules)
- [ ] requirements.txt
- [ ] pyproject.toml
- [ ] .gitignore
- [ ] smallfarms/utils/ (config, logging, checksum)
- [ ] smallfarms/db/ (session, base, alembic env)
- [ ] smallfarms/models/ (כל 10 קבצים)
- [ ] 5 Alembic revisions (001–005)
- [ ] Seed data: 11 units, 4 conversions, 29 products, 20 sources, aliases
- [ ] tests/test_db_health.py — PASS

## בקשה לפתיחת שער G1
מתבקשת צוות 50 לבצע QA ולאשר שער G1.
```
