"""CollectorEngine — selects and runs the correct collector for a source."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.collectors.base import BaseCollector
from organic_market_agent.collectors.easyfarm import EasyFarmCollector
from organic_market_agent.collectors.govt_benchmark import GovtBenchmarkCollector
from organic_market_agent.collectors.html_page import StandaloneHTMLCollector
from organic_market_agent.models import RawAsset, Source, SourceFetchProfile, SourceFetchRun
from organic_market_agent.utils.exceptions import DuplicateAssetError
from organic_market_agent.utils.log_persist import persist_error_log
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

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
        final_status is one of: 'success', 'failed', 'skipped', 'running'.
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
            pass
        except Exception as exc:
            logger.exception("Unexpected collector error for source=%s", source.code)
            fetch_run.status = "failed"
            fetch_run.error_message = str(exc)
            fetch_run.finished_at = datetime.now(timezone.utc)
            persist_error_log(
                session,
                module="collectors.engine",
                message=f"Unexpected collector error for {source.code}: {exc}",
                ingestion_run_id=ingestion_run_id,
                entity_type="source",
                entity_id=source.id,
                extra={"source_code": source.code},
            )
        finally:
            collector.close()

        return raw_asset, fetch_run.status
