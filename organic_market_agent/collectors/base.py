"""Abstract base for all source collectors."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from organic_market_agent.models import RawAsset, SourceFetchRun
from organic_market_agent.utils.checksum import sha256_bytes
from organic_market_agent.utils.config import config
from organic_market_agent.utils.exceptions import CollectorError, DuplicateAssetError
from organic_market_agent.utils.log_persist import persist_error_log
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

    def __init__(self, source_id: int, source_code: str, profile: dict[str, Any]) -> None:
        self.source_id = source_id
        self.source_code = source_code
        self.profile = profile
        self._client: Optional[httpx.Client] = None
        self._last_http_status: Optional[int] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            headers = self.profile.get("request_headers_json") or {}
            if not isinstance(headers, dict):
                headers = {}
            self._client = httpx.Client(
                timeout=self.profile.get("timeout_seconds", 30),
                follow_redirects=True,
                headers=headers,
            )
        return self._client

    @abstractmethod
    def fetch_content(self, url: str) -> tuple[bytes, str]:
        """Return (raw_bytes, file_type).

        file_type must be one of: 'html', 'json', 'pdf', 'rss', 'text', 'other'
        Subclasses should set self._last_http_status from the HTTP response.
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
            self._last_http_status = None
            try:
                content, file_type = self.fetch_content(url)
                break
            except (httpx.HTTPError, CollectorError) as exc:
                last_error = exc
                fetch_run.retry_count = attempt
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
            persist_error_log(
                session,
                module="collectors.base",
                message=f"Collector failed for {self.source_code}: {last_error}",
                ingestion_run_id=ingestion_run_id,
                entity_type="source",
                entity_id=self.source_id,
                extra={"source_code": self.source_code, "url": url},
            )
            return None

        checksum = sha256_bytes(content)

        existing = session.execute(
            select(RawAsset).where(
                RawAsset.checksum_sha256 == checksum,
                RawAsset.source_id == self.source_id,
            )
        ).scalar_one_or_none()

        if existing is not None:
            fetch_run.status = "skipped"
            fetch_run.finished_at = datetime.now(timezone.utc)
            logger.info("Source %s: duplicate asset, skipping", self.source_code)
            raise DuplicateAssetError(f"Duplicate checksum {checksum} for source {self.source_code}")

        storage_path = self._save_to_disk(content, file_type)

        raw_asset = RawAsset(
            source_id=self.source_id,
            source_fetch_run_id=fetch_run.id,
            storage_path=str(storage_path),
            file_type=file_type,
            checksum_sha256=checksum,
            bytes_size=len(content),
        )
        session.add(raw_asset)
        session.flush()

        fetch_run.raw_asset_id = raw_asset.id
        fetch_run.status = "success"
        fetch_run.http_status = self._last_http_status if self._last_http_status is not None else 200
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
