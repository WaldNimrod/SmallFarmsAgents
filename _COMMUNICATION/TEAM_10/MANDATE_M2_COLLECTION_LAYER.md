# Mandate — Team 10: M2 Collection Layer
**From:** Team 100 (Architecture)  
**Date:** 2026-03-30  
**Milestone:** M2 — Collection Layer  
**Gate:** G2  
**Dependency:** Gate G1 must be formally open (Team 50 sign-off) before writing any code  
**Priority:** Critical — all normalizer and aggregation work depends on this

---

## M2 Scope

M2 implements the data acquisition pipeline: fetch raw HTML/JSON from sources,
store them as `raw_assets` on the filesystem, extract raw product/price rows,
and persist them as `raw_extracted_items` in PostgreSQL.

**No normalization in M2.** `normalized_observations` remains empty after M2.

**Deliverables checklist:**
- `CollectorEngine` + `BaseCollector` (retry, timeout, checksum dedup, DB write)
- Three collectors: `EasyFarmCollector`, `StandaloneHTMLCollector`, `GovtBenchmarkCollector`
- `ParserEngine` (dispatcher keyed on `normalizer_type`)
- Three parsers: `EasyFarmCatalogParser`, `SimpleProductGridParser`, `OfficialWholesaleParser`
- `IngestionRunner` CLI: `python -m organic_market_agent.scheduler.run_ingestion`
- `tests/test_collectors.py` — 8+ tests
- `tests/test_parsers.py` — 8+ tests

---

## Architecture Overview

```
IngestionRunner
  │
  ├─ creates IngestionRun (DB)
  └─ for each active Source with fetch_profile:
       └─ CollectorEngine.fetch(source, profile)
            ├─ httpx GET with timeout + retry (from profile.retry_policy_json)
            ├─ checksum SHA-256 → dedup check (raw_assets table)
            ├─ save raw bytes to filesystem → RAW_FILES_ROOT/{source_code}/{date}/
            ├─ writes RawAsset (DB)
            ├─ writes SourceFetchRun (DB) with status=success|failed
            └─ if success → ParserEngine.parse(raw_asset, source, profile)
                  ├─ dispatch by normalizer_type
                  └─ writes RawExtractedItem[] (DB)
```

**Critical rules:**
- All HTTP via `httpx` (async not required for M2 — synchronous is fine)
- Never hardcode URLs in collector code — read from `source_fetch_profiles.entry_url`
- Never hardcode product names in parser code — output raw strings only
- `price_amount` is never parsed in M2 — it stays as raw text in `raw_price_text`
- All exceptions are caught, logged, and result in `SourceFetchRun.status = 'failed'`

---

## Step 1: Project Structure Additions

Add the following files (do not modify M1 files except `__init__.py` stubs):

```
organic_market_agent/
  collectors/
    __init__.py          # (already exists — add exports)
    base.py              # BaseCollector ABC
    engine.py            # CollectorEngine
    easyfarm.py          # EasyFarmCollector
    html_page.py         # StandaloneHTMLCollector
    govt_benchmark.py    # GovtBenchmarkCollector

  parsers/
    __init__.py          # (already exists — add exports)
    base.py              # BaseParser ABC
    engine.py            # ParserEngine dispatcher
    easyfarm_catalog.py  # EasyFarmCatalogParser
    simple_product_grid.py
    official_wholesale.py

  scheduler/
    __init__.py          # (already exists)
    run_ingestion.py     # CLI entrypoint (__main__ module)

tests/
  test_collectors.py
  test_parsers.py
```

---

## Step 2: Exceptions

File: `organic_market_agent/utils/exceptions.py`

```python
class MyFarmAgentsError(Exception):
    """Base exception for all organic_market_agent errors."""


class CollectorError(MyFarmAgentsError):
    """Raised when HTTP fetch fails unrecoverably."""


class ParserError(MyFarmAgentsError):
    """Raised when a parser cannot extract items from a raw asset."""


class DuplicateAssetError(MyFarmAgentsError):
    """Raised when the same checksum already exists in raw_assets."""
```

Add to `organic_market_agent/utils/__init__.py`:
```python
from organic_market_agent.utils.exceptions import (
    MyFarmAgentsError,
    CollectorError,
    ParserError,
    DuplicateAssetError,
)
```

---

## Step 3: BaseCollector

File: `organic_market_agent/collectors/base.py`

```python
"""Abstract base for all source collectors."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from organic_market_agent.models import RawAsset, SourceFetchRun
from organic_market_agent.utils.checksum import sha256_bytes
from organic_market_agent.utils.config import config
from organic_market_agent.utils.exceptions import CollectorError, DuplicateAssetError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class FetchResult:
    """Container for a successful HTTP fetch."""

    def __init__(
        self,
        source_code: str,
        url: str,
        content: bytes,
        http_status: int,
        file_type: str,
        storage_path: Path,
        checksum: str,
    ) -> None:
        self.source_code = source_code
        self.url = url
        self.content = content
        self.http_status = http_status
        self.file_type = file_type
        self.storage_path = storage_path
        self.checksum = checksum
        self.fetched_at: datetime = datetime.now(timezone.utc)


class BaseCollector(ABC):
    """Base class for all collectors.

    Subclasses must implement `fetch_content` to return raw bytes
    and the file type string ('html', 'json', etc.).
    """

    def __init__(self, source_id: int, source_code: str, profile: dict) -> None:
        self.source_id = source_id
        self.source_code = source_code
        self.profile = profile  # SourceFetchProfile as dict
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                timeout=self.profile.get("timeout_seconds", 30),
                follow_redirects=True,
                headers=self.profile.get("request_headers_json") or {},
            )
        return self._client

    @abstractmethod
    def fetch_content(self, url: str) -> tuple[bytes, str]:
        """Return (raw_bytes, file_type).

        file_type must be one of: 'html', 'json', 'pdf', 'rss', 'text', 'other'
        """

    def fetch(
        self,
        session: Session,
        ingestion_run_id: int,
        fetch_run: SourceFetchRun,
    ) -> Optional[RawAsset]:
        """Execute fetch with retry, dedup, and DB write.

        Returns RawAsset on success, None on failure.
        Updates fetch_run.status in-place (caller must commit).
        """
        url = self.profile["entry_url"]
        retry_policy = self.profile.get("retry_policy_json") or {
            "max_retries": 2,
            "backoff_seconds": 60,
        }
        max_retries: int = retry_policy.get("max_retries", 2)
        backoff: int = retry_policy.get("backoff_seconds", 60)

        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                content, file_type = self.fetch_content(url)
                break
            except (httpx.HTTPError, CollectorError) as exc:
                last_error = exc
                logger.warning(
                    "Fetch attempt %d/%d failed for source=%s: %s",
                    attempt + 1,
                    max_retries + 1,
                    self.source_code,
                    exc,
                )
                if attempt < max_retries:
                    time.sleep(backoff)
        else:
            fetch_run.status = "failed"
            fetch_run.error_message = str(last_error)
            fetch_run.finished_at = datetime.now(timezone.utc)
            logger.error("Source %s failed after %d retries", self.source_code, max_retries)
            return None

        checksum = sha256_bytes(content)

        # Dedup: if this exact asset was already collected, skip
        existing = session.execute(
            __import__("sqlalchemy").select(RawAsset).where(
                RawAsset.checksum_sha256 == checksum,
                RawAsset.source_id == self.source_id,
            )
        ).scalar_one_or_none()

        if existing is not None:
            fetch_run.status = "skipped"
            fetch_run.finished_at = datetime.now(timezone.utc)
            logger.info("Source %s: duplicate asset, skipping", self.source_code)
            raise DuplicateAssetError(f"Duplicate checksum {checksum} for source {self.source_code}")

        # Persist to filesystem
        storage_path = self._save_to_disk(content, file_type)

        # Write RawAsset
        raw_asset = RawAsset(
            source_id=self.source_id,
            source_fetch_run_id=fetch_run.id,
            storage_path=str(storage_path),
            file_type=file_type,
            checksum_sha256=checksum,
            bytes_size=len(content),
        )
        session.add(raw_asset)
        session.flush()  # get raw_asset.id without committing

        fetch_run.raw_asset_id = raw_asset.id
        fetch_run.status = "success"
        fetch_run.http_status = 200
        fetch_run.bytes_fetched = len(content)
        fetch_run.finished_at = datetime.now(timezone.utc)

        logger.info(
            "Source %s: fetched %d bytes, checksum=%s",
            self.source_code,
            len(content),
            checksum[:12],
        )
        return raw_asset

    def _save_to_disk(self, content: bytes, file_type: str) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dest_dir = config.RAW_FILES_ROOT / self.source_code / today
        dest_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
        dest_path = dest_dir / f"{self.source_code}_{timestamp}.{file_type}"
        dest_path.write_bytes(content)
        return dest_path

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
```

---

## Step 4: Concrete Collectors

### 4.1 EasyFarmCollector

File: `organic_market_agent/collectors/easyfarm.py`

EasyFarm sources serve their catalog as a single HTML page or a paginated
JSON endpoint depending on the `fetch_mode` in the profile.

```python
"""Collector for sources with platform_family='easyfarm'."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class EasyFarmCollector(BaseCollector):
    """Fetches EasyFarm-platform catalog pages (HTML or JSON)."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        fetch_mode = self.profile.get("fetch_mode", "html_page")
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"EasyFarm fetch failed: {exc}") from exc

        if fetch_mode == "json_endpoint":
            return response.content, "json"
        return response.content, "html"
```

### 4.2 StandaloneHTMLCollector

File: `organic_market_agent/collectors/html_page.py`

Generic collector for any HTML page (SRC008, SRC009 — standalone farm web pages).

```python
"""Generic HTML page collector."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class StandaloneHTMLCollector(BaseCollector):
    """Fetches a single HTML page."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"HTML fetch failed: {exc}") from exc
        return response.content, "html"
```

### 4.3 GovtBenchmarkCollector

File: `organic_market_agent/collectors/govt_benchmark.py`

Government wholesale price endpoint (SRC015). Typically a JSON endpoint
or CSV download. Reads `fetch_mode` from profile.

```python
"""Government / official benchmark source collector."""
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.utils.exceptions import CollectorError


class GovtBenchmarkCollector(BaseCollector):
    """Fetches official wholesale price data from government endpoints."""

    def fetch_content(self, url: str) -> tuple[bytes, str]:
        fetch_mode = self.profile.get("fetch_mode", "json_endpoint")
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except Exception as exc:
            raise CollectorError(f"GovtBenchmark fetch failed: {exc}") from exc

        if fetch_mode == "json_endpoint":
            return response.content, "json"
        return response.content, "text"
```

---

## Step 5: CollectorEngine

File: `organic_market_agent/collectors/engine.py`

The engine selects the right collector class based on `platform_family`
and `fetch_mode` from the source's fetch profile.

```python
"""CollectorEngine — selects and runs the correct collector for a source."""
from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.models import RawAsset, Source, SourceFetchProfile, SourceFetchRun
from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
from organic_market_agent.utils.exceptions import DuplicateAssetError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Mapping: (platform_family, fetch_mode) → collector class
# Rules (evaluated in order):
#   1. platform_family='easyfarm' → EasyFarmCollector regardless of fetch_mode
#   2. fetch_mode='json_endpoint' with no platform_family → GovtBenchmarkCollector
#   3. default → StandaloneHTMLCollector
_PLATFORM_MAP: dict[str, type[BaseCollector]] = {
    "easyfarm": EasyFarmCollector,
}

_FETCH_MODE_MAP: dict[str, type[BaseCollector]] = {
    "json_endpoint": GovtBenchmarkCollector,
    "html_page": StandaloneHTMLCollector,
    "directory_page": StandaloneHTMLCollector,
}


def _select_collector(profile: SourceFetchProfile) -> type[BaseCollector]:
    if profile.platform_family and profile.platform_family in _PLATFORM_MAP:
        return _PLATFORM_MAP[profile.platform_family]
    return _FETCH_MODE_MAP.get(profile.fetch_mode, StandaloneHTMLCollector)


class CollectorEngine:
    """Orchestrates fetch for a single source within an ingestion run."""

    def run(
        self,
        session: Session,
        ingestion_run_id: int,
        source: Source,
        profile: SourceFetchProfile,
    ) -> tuple[Optional[RawAsset], str]:
        """Fetch and persist one source.

        Returns (raw_asset_or_None, final_status).
        final_status is one of: 'success', 'failed', 'skipped'.
        """
        fetch_run = SourceFetchRun(
            ingestion_run_id=ingestion_run_id,
            source_id=source.id,
            fetch_profile_id=profile.id,
            status="running",
        )
        session.add(fetch_run)
        session.flush()

        profile_dict = {
            "entry_url": profile.entry_url,
            "fetch_mode": profile.fetch_mode,
            "platform_family": profile.platform_family,
            "timeout_seconds": profile.timeout_seconds,
            "retry_policy_json": profile.retry_policy_json,
            "request_headers_json": profile.request_headers_json,
        }

        collector_cls = _select_collector(profile)
        collector = collector_cls(
            source_id=source.id,
            source_code=source.code,
            profile=profile_dict,
        )

        raw_asset: Optional[RawAsset] = None
        try:
            raw_asset = collector.fetch(session, ingestion_run_id, fetch_run)
        except DuplicateAssetError:
            pass  # fetch_run already set to 'skipped' by base class
        finally:
            collector.close()

        return raw_asset, fetch_run.status
```

---

## Step 6: BaseParser

File: `organic_market_agent/parsers/base.py`

```python
"""Abstract base for all parsers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RawItem:
    """A single extracted row from a raw asset before normalization."""

    raw_product_name: Optional[str]
    raw_price_text: Optional[str]
    raw_unit_text: Optional[str]
    raw_quantity_text: Optional[str]
    raw_payload_json: dict = field(default_factory=dict)


class BaseParser(ABC):
    """Abstract parser.

    Subclasses receive raw bytes and return a list of RawItem.
    parsers must NOT normalize, resolve aliases, or convert units.
    """

    @abstractmethod
    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        """Extract raw items from raw bytes.

        Raises ParserError if content is completely unparseable.
        Returns empty list if content is valid but contains no product rows.
        """
```

---

## Step 7: Concrete Parsers

### 7.1 EasyFarmCatalogParser

File: `organic_market_agent/parsers/easyfarm_catalog.py`

EasyFarm pages render product catalogs as structured HTML with consistent
CSS class names. The `selector_profile` JSONB column in `source_fetch_profiles`
may override default selectors.

```python
"""Parser for EasyFarm platform catalog pages."""
from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Default CSS selectors for EasyFarm catalog layout.
# Override by populating source_fetch_profiles.selector_profile in the DB.
DEFAULT_SELECTORS = {
    "product_row": "div.product-item, li.product-item, tr.product-row",
    "name": ".product-name, .item-title, h3",
    "price": ".product-price, .item-price, .price",
    "unit": ".product-unit, .item-unit, .unit",
    "quantity": ".product-quantity, .item-quantity, .qty",
}


class EasyFarmCatalogParser(BaseParser):
    """Parses EasyFarm HTML catalog pages."""

    def __init__(self, selector_overrides: Optional[dict] = None) -> None:
        self._selectors = {**DEFAULT_SELECTORS, **(selector_overrides or {})}

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        encoding = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
        except Exception as exc:
            raise ParserError(f"EasyFarmCatalogParser: HTML parse error: {exc}") from exc

        rows = soup.select(self._selectors["product_row"])
        if not rows:
            logger.warning("EasyFarmCatalogParser: no product rows found")
            return []

        items: list[RawItem] = []
        for row in rows:
            name_el = row.select_one(self._selectors["name"])
            price_el = row.select_one(self._selectors["price"])
            unit_el = row.select_one(self._selectors["unit"])
            qty_el = row.select_one(self._selectors["quantity"])

            items.append(
                RawItem(
                    raw_product_name=name_el.get_text(strip=True) if name_el else None,
                    raw_price_text=price_el.get_text(strip=True) if price_el else None,
                    raw_unit_text=unit_el.get_text(strip=True) if unit_el else None,
                    raw_quantity_text=qty_el.get_text(strip=True) if qty_el else None,
                    raw_payload_json={},
                )
            )

        logger.info("EasyFarmCatalogParser: extracted %d items", len(items))
        return items
```

### 7.2 SimpleProductGridParser

File: `organic_market_agent/parsers/simple_product_grid.py`

For standalone farm websites that list products in a simple grid or table.

```python
"""Parser for simple standalone HTML product tables/grids."""
from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class SimpleProductGridParser(BaseParser):
    """Heuristic parser for simple product listings.

    Strategy:
      1. Look for <table> rows with price-like content (contains ₪ or digits).
      2. Fall back to <div>/<li> elements that contain both a name and a price pattern.
    """

    _PRICE_RE = re.compile(r"[\d]+[.,]?[\d]*")

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        encoding = charset_hint or "utf-8"
        try:
            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
        except Exception as exc:
            raise ParserError(f"SimpleProductGridParser: HTML parse error: {exc}") from exc

        items = self._try_table(soup) or self._try_list(soup)
        logger.info("SimpleProductGridParser: extracted %d items", len(items))
        return items

    def _try_table(self, soup: BeautifulSoup) -> list[RawItem]:
        items: list[RawItem] = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 2:
                    continue
                price_cells = [c for c in cells if self._PRICE_RE.search(c)]
                if not price_cells:
                    continue
                items.append(
                    RawItem(
                        raw_product_name=cells[0],
                        raw_price_text=price_cells[0],
                        raw_unit_text=cells[2] if len(cells) > 2 else None,
                        raw_quantity_text=None,
                        raw_payload_json={"cells": cells},
                    )
                )
        return items

    def _try_list(self, soup: BeautifulSoup) -> list[RawItem]:
        items: list[RawItem] = []
        for el in soup.find_all(["li", "div", "article"]):
            text = el.get_text(separator=" ", strip=True)
            if self._PRICE_RE.search(text) and len(text) > 5:
                items.append(
                    RawItem(
                        raw_product_name=text[:200],
                        raw_price_text=None,
                        raw_unit_text=None,
                        raw_quantity_text=None,
                        raw_payload_json={"raw_text": text[:500]},
                    )
                )
        return items
```

### 7.3 OfficialWholesaleParser

File: `organic_market_agent/parsers/official_wholesale.py`

Government wholesale price data arrives as JSON. The schema varies by
endpoint — use `raw_payload_json` to capture the full row for the normalizer.

```python
"""Parser for official/government wholesale price JSON endpoints."""
from __future__ import annotations

import json
from typing import Optional

from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Common key names in government JSON payloads. The normalizer resolves these
# via DB rules — the parser only captures raw values.
_NAME_KEYS = ("product_name", "name", "item", "commodity", "productName", "שם_מוצר", "מוצר")
_PRICE_KEYS = ("price", "avg_price", "price_nis", "מחיר", "מחיר_ממוצע")
_UNIT_KEYS = ("unit", "unit_type", "יחידה", "unit_name")
_QTY_KEYS = ("quantity", "qty", "weight", "כמות")


def _find_key(row: dict, candidates: tuple[str, ...]) -> Optional[str]:
    for k in candidates:
        if k in row:
            return str(row[k])
    return None


class OfficialWholesaleParser(BaseParser):
    """Parses JSON arrays from government wholesale price APIs."""

    def parse(self, content: bytes, charset_hint: Optional[str] = None) -> list[RawItem]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ParserError(f"OfficialWholesaleParser: invalid JSON: {exc}") from exc

        # Unwrap common envelope shapes: {"data": [...]} or {"results": [...]} or [...]
        if isinstance(data, dict):
            for key in ("data", "results", "items", "products", "rows"):
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break

        if not isinstance(data, list):
            raise ParserError("OfficialWholesaleParser: expected a JSON array")

        items: list[RawItem] = []
        for row in data:
            if not isinstance(row, dict):
                continue
            items.append(
                RawItem(
                    raw_product_name=_find_key(row, _NAME_KEYS),
                    raw_price_text=_find_key(row, _PRICE_KEYS),
                    raw_unit_text=_find_key(row, _UNIT_KEYS),
                    raw_quantity_text=_find_key(row, _QTY_KEYS),
                    raw_payload_json=row,
                )
            )

        logger.info("OfficialWholesaleParser: extracted %d items", len(items))
        return items
```

---

## Step 8: ParserEngine

File: `organic_market_agent/parsers/engine.py`

```python
"""ParserEngine — dispatches to the correct parser and writes RawExtractedItems."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.models import NormalizerProfile, RawAsset, RawExtractedItem, Source
from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.easyfarm_catalog import EasyFarmCatalogParser
from organic_market_agent.parsers.simple_product_grid import SimpleProductGridParser
from organic_market_agent.parsers.official_wholesale import OfficialWholesaleParser
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PARSER_MAP: dict[str, type[BaseParser]] = {
    "easyfarm_catalog": EasyFarmCatalogParser,
    "simple_product_grid": SimpleProductGridParser,
    "basket_only": SimpleProductGridParser,  # same heuristic for M2
    "official_wholesale": OfficialWholesaleParser,
    "retail_benchmark": OfficialWholesaleParser,
}


class ParserEngine:
    """Selects and runs the correct parser for a raw asset."""

    def run(
        self,
        session: Session,
        raw_asset: RawAsset,
        source: Source,
        normalizer_type: str,
        charset_hint: Optional[str] = None,
        selector_overrides: Optional[dict] = None,
    ) -> int:
        """Parse raw_asset and write RawExtractedItems.

        Returns the count of items written.
        """
        parser_cls = _PARSER_MAP.get(normalizer_type)
        if parser_cls is None:
            logger.warning(
                "No parser for normalizer_type=%r (source=%s). Skipping.",
                normalizer_type,
                source.code,
            )
            return 0

        # Instantiate parser (EasyFarmCatalogParser accepts selector_overrides)
        if parser_cls is EasyFarmCatalogParser:
            parser: BaseParser = EasyFarmCatalogParser(selector_overrides)
        else:
            parser = parser_cls()

        content = Path(raw_asset.storage_path).read_bytes()

        try:
            raw_items: list[RawItem] = parser.parse(content, charset_hint=charset_hint)
        except ParserError as exc:
            logger.error(
                "Parser error for source=%s raw_asset=%d: %s",
                source.code,
                raw_asset.id,
                exc,
            )
            return 0

        # Resolve normalizer_profile_id from DB
        np_row = session.execute(
            __import__("sqlalchemy").select(NormalizerProfile.id).where(
                NormalizerProfile.source_id == source.id,
                NormalizerProfile.normalizer_type == normalizer_type,
                NormalizerProfile.is_active == True,  # noqa: E712
            )
        ).scalar_one_or_none()

        db_items: list[RawExtractedItem] = [
            RawExtractedItem(
                source_fetch_run_id=raw_asset.source_fetch_run_id,
                raw_asset_id=raw_asset.id,
                normalizer_profile_id=np_row,
                raw_product_name=item.raw_product_name,
                raw_price_text=item.raw_price_text,
                raw_unit_text=item.raw_unit_text,
                raw_quantity_text=item.raw_quantity_text,
                raw_payload_json=item.raw_payload_json,
                extraction_status="extracted",
            )
            for item in raw_items
        ]

        session.add_all(db_items)
        logger.info(
            "ParserEngine: wrote %d raw_extracted_items for source=%s",
            len(db_items),
            source.code,
        )
        return len(db_items)
```

---

## Step 9: IngestionRunner

File: `organic_market_agent/scheduler/run_ingestion.py`

This file is the CLI entrypoint: `python -m organic_market_agent.scheduler.run_ingestion`

```python
"""IngestionRunner CLI — run a full ingestion cycle."""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import click
import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.collectors.engine import CollectorEngine
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.models import (
    IngestionRun,
    NormalizerProfile,
    Source,
    SourceFetchProfile,
)
from organic_market_agent.parsers.engine import ParserEngine
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

collector_engine = CollectorEngine()
parser_engine = ParserEngine()


def _get_active_sources_with_profiles(session: Session) -> list[tuple[Source, SourceFetchProfile]]:
    rows = session.execute(
        sa.select(Source, SourceFetchProfile)
        .join(SourceFetchProfile, SourceFetchProfile.source_id == Source.id)
        .where(Source.is_active == True)  # noqa: E712
        .where(SourceFetchProfile.is_active == True)  # noqa: E712
        .order_by(Source.priority.asc())
    ).all()
    return [(r[0], r[1]) for r in rows]


def _get_normalizer_type(session: Session, source_id: int) -> str | None:
    return session.execute(
        sa.select(NormalizerProfile.normalizer_type).where(
            NormalizerProfile.source_id == source_id,
            NormalizerProfile.is_active == True,  # noqa: E712
        )
    ).scalar_one_or_none()


@click.command()
@click.option("--run-type", default="daily", type=click.Choice(["daily", "manual", "retry"]))
@click.option("--source-code", default=None, help="Run a single source by code (for debugging)")
def run_ingestion(run_type: str, source_code: str | None) -> None:
    """Execute a full (or single-source) ingestion run."""
    with SessionFactory() as session:
        pairs = _get_active_sources_with_profiles(session)
        if source_code:
            pairs = [(s, p) for s, p in pairs if s.code == source_code]
            if not pairs:
                click.echo(f"No active source with code={source_code!r}", err=True)
                sys.exit(1)

        ingestion_run = IngestionRun(
            run_type=run_type,
            triggered_by="cli",
            sources_total=len(pairs),
        )
        session.add(ingestion_run)
        session.flush()

        succeeded = 0
        failed = 0
        community_succeeded = 0

        for source, profile in pairs:
            raw_asset, status = collector_engine.run(
                session, ingestion_run.id, source, profile
            )

            if status == "success" and raw_asset is not None:
                normalizer_type = _get_normalizer_type(session, source.id)
                if normalizer_type:
                    parser_engine.run(
                        session,
                        raw_asset,
                        source,
                        normalizer_type,
                        charset_hint=profile.charset_hint,
                        selector_overrides=profile.selector_profile,
                    )
                succeeded += 1
                if source.market_scope == "community":
                    community_succeeded += 1
            elif status == "failed":
                failed += 1

        ingestion_run.sources_succeeded = succeeded
        ingestion_run.sources_failed = failed
        ingestion_run.community_sources_succeeded = community_succeeded
        ingestion_run.finished_at = datetime.now(timezone.utc)
        ingestion_run.status = (
            "completed" if failed == 0 else ("partial" if succeeded > 0 else "failed")
        )
        session.commit()

        click.echo(
            f"IngestionRun #{ingestion_run.id}: "
            f"status={ingestion_run.status} "
            f"succeeded={succeeded} failed={failed} "
            f"community_ok={community_succeeded}"
        )


if __name__ == "__main__":
    run_ingestion()
```

---

## Step 10: Tests

### `tests/test_collectors.py`

```python
"""Unit tests for collectors (no live HTTP — use httpx mock)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
from organic_market_agent.collectors.engine import CollectorEngine, _select_collector
from organic_market_agent.utils.exceptions import CollectorError


# --- Fixtures ---

def _make_profile(fetch_mode="html_page", platform_family=None):
    return {
        "entry_url": "http://example.com/catalog",
        "fetch_mode": fetch_mode,
        "platform_family": platform_family,
        "timeout_seconds": 10,
        "retry_policy_json": {"max_retries": 0, "backoff_seconds": 0},
        "request_headers_json": None,
    }


# --- Collector selection ---

def test_select_collector_easyfarm():
    profile = MagicMock(platform_family="easyfarm", fetch_mode="html_page")
    assert _select_collector(profile) is EasyFarmCollector


def test_select_collector_json_endpoint():
    profile = MagicMock(platform_family=None, fetch_mode="json_endpoint")
    assert _select_collector(profile) is GovtBenchmarkCollector


def test_select_collector_html_default():
    profile = MagicMock(platform_family=None, fetch_mode="html_page")
    assert _select_collector(profile) is StandaloneHTMLCollector


# --- EasyFarmCollector ---

def test_easyfarm_fetch_html_success(tmp_path, monkeypatch):
    monkeypatch.setattr("organic_market_agent.utils.config.config.RAW_FILES_ROOT", tmp_path)
    collector = EasyFarmCollector(1, "SRC002", _make_profile("html_page", "easyfarm"))
    mock_response = MagicMock(content=b"<html>ok</html>", status_code=200)
    mock_response.raise_for_status = MagicMock()
    with patch.object(collector, "client") as mock_client:
        mock_client.get.return_value = mock_response
        content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "html"
    assert content == b"<html>ok</html>"


def test_easyfarm_fetch_raises_on_http_error(monkeypatch):
    import httpx
    collector = EasyFarmCollector(1, "SRC002", _make_profile("html_page", "easyfarm"))
    with patch.object(collector, "client") as mock_client:
        mock_client.get.side_effect = httpx.ConnectError("timeout")
        with pytest.raises(CollectorError):
            collector.fetch_content("http://example.com")


# --- StandaloneHTMLCollector ---

def test_html_collector_returns_html(monkeypatch):
    collector = StandaloneHTMLCollector(2, "SRC008", _make_profile())
    mock_response = MagicMock(content=b"<html>page</html>", status_code=200)
    mock_response.raise_for_status = MagicMock()
    with patch.object(collector, "client") as mock_client:
        mock_client.get.return_value = mock_response
        content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "html"


# --- GovtBenchmarkCollector ---

def test_govt_collector_returns_json(monkeypatch):
    collector = GovtBenchmarkCollector(3, "SRC015", _make_profile("json_endpoint"))
    mock_response = MagicMock(content=b'[{"name":"tomato"}]', status_code=200)
    mock_response.raise_for_status = MagicMock()
    with patch.object(collector, "client") as mock_client:
        mock_client.get.return_value = mock_response
        content, file_type = collector.fetch_content("http://example.com")
    assert file_type == "json"
```

### `tests/test_parsers.py`

```python
"""Unit tests for parsers — purely in-memory, no DB."""
from __future__ import annotations

import json

import pytest

from organic_market_agent.parsers.easyfarm_catalog import EasyFarmCatalogParser
from organic_market_agent.parsers.simple_product_grid import SimpleProductGridParser
from organic_market_agent.parsers.official_wholesale import OfficialWholesaleParser
from organic_market_agent.utils.exceptions import ParserError

# --- EasyFarmCatalogParser ---

EASYFARM_HTML = b"""
<html><body>
  <div class="product-item">
    <span class="product-name">עגבניות שרי</span>
    <span class="product-price">18</span>
    <span class="product-unit">ק"ג</span>
  </div>
  <div class="product-item">
    <span class="product-name">מלפפון</span>
    <span class="product-price">12</span>
    <span class="product-unit">ק"ג</span>
  </div>
</body></html>
"""


def test_easyfarm_extracts_two_items():
    parser = EasyFarmCatalogParser()
    items = parser.parse(EASYFARM_HTML)
    assert len(items) == 2
    assert items[0].raw_product_name == 'עגבניות שרי'
    assert items[0].raw_price_text == '18'


def test_easyfarm_empty_page_returns_empty_list():
    parser = EasyFarmCatalogParser()
    items = parser.parse(b"<html><body></body></html>")
    assert items == []


# --- SimpleProductGridParser ---

TABLE_HTML = b"""
<html><body>
<table>
  <tr><td>גזר</td><td>8 ₪/ק"ג</td><td>ק"ג</td></tr>
  <tr><td>תפוח אדמה</td><td>5 ₪/ק"ג</td><td>ק"ג</td></tr>
</table>
</body></html>
"""


def test_simple_grid_table_extracts_items():
    parser = SimpleProductGridParser()
    items = parser.parse(TABLE_HTML)
    assert len(items) == 2
    assert items[0].raw_product_name == 'גזר'


def test_simple_grid_no_prices_returns_empty():
    parser = SimpleProductGridParser()
    items = parser.parse(b"<html><body><p>hello world</p></body></html>")
    assert items == []


# --- OfficialWholesaleParser ---

GOVT_JSON = json.dumps([
    {"product_name": "עגבניה", "price": "15.5", "unit": "ק\"ג"},
    {"product_name": "פלפל", "price": "22.0", "unit": "ק\"ג"},
]).encode()

GOVT_JSON_WRAPPED = json.dumps({"data": [
    {"product_name": "בצל", "price": "6.0"},
]}).encode()


def test_official_wholesale_parses_array():
    parser = OfficialWholesaleParser()
    items = parser.parse(GOVT_JSON)
    assert len(items) == 2
    assert items[0].raw_product_name == 'עגבניה'
    assert items[0].raw_price_text == '15.5'


def test_official_wholesale_unwraps_envelope():
    parser = OfficialWholesaleParser()
    items = parser.parse(GOVT_JSON_WRAPPED)
    assert len(items) == 1
    assert items[0].raw_product_name == 'בצל'


def test_official_wholesale_raises_on_invalid_json():
    parser = OfficialWholesaleParser()
    with pytest.raises(ParserError):
        parser.parse(b"not json")
```

---

## Step 11: `__init__.py` Exports

Update `organic_market_agent/collectors/__init__.py`:
```python
from organic_market_agent.collectors.base import BaseCollector, FetchResult
from organic_market_agent.collectors.engine import CollectorEngine
from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
```

Update `organic_market_agent/parsers/__init__.py`:
```python
from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.engine import ParserEngine
from organic_market_agent.parsers.easyfarm_catalog import EasyFarmCatalogParser
from organic_market_agent.parsers.simple_product_grid import SimpleProductGridParser
from organic_market_agent.parsers.official_wholesale import OfficialWholesaleParser
```

---

## Step 12: Checksum Utility Update

The existing `utils/checksum.py` likely only has `sha256_file`. Add:

```python
def sha256_bytes(content: bytes) -> str:
    """Return hex SHA-256 of in-memory bytes."""
    import hashlib
    return hashlib.sha256(content).hexdigest()
```

If `sha256_bytes` already exists, skip.

---

## Critical Rules for Team 10

1. **No live HTTP in tests** — use `unittest.mock.patch` or `pytest-httpx`.
2. **No product name logic in parsers** — parsers output raw strings only.
3. **No `Decimal` conversions in M2** — `price_amount` stays as `raw_price_text` (string).
4. **Never read `SOURCE_MAP_MASTER_HE.md` to decide what URL to use** — read from `source_fetch_profiles.entry_url` in the DB.
5. **All `is_active=True` filtering** — only fetch active sources with active profiles.
6. **Idempotency** — re-running on the same day must not create duplicate raw_assets (checksum dedup enforces this).
7. **One `IngestionRun` per execution** — never create multiple runs in one CLI call.
8. **Collector failures are non-fatal** — one source failure must not abort other sources.

---

## Gate G2 — Submission Checklist

Submit `_COMMUNICATION/TEAM_10/reports/{date}_M2_COMPLETE_TEAM10.md` with:

```
## Environment
- Python version: X.X.X (must be 3.11+)
- PostgreSQL version: X.X (direct install, no Docker)

## Output: python -m organic_market_agent.scheduler.run_ingestion --run-type manual
(paste full output)

## Output: pytest tests/test_collectors.py tests/test_parsers.py -v
(paste full output — all tests must PASS)

## DB Counts after run
- ingestion_runs: N rows
- source_fetch_runs: N rows (success=X, failed=Y, skipped=Z)
- raw_assets: N rows
- raw_extracted_items: N rows (must be >= 50)

## Dedup verification
(describe: second run, same sources → source_fetch_runs.status='skipped', no new raw_assets)

## Delta Report (if any deviations from this mandate)
```

Team 50 will validate G2 against this mandate and `docs/PIPELINE_ALGORITHMS_HE.md`.
