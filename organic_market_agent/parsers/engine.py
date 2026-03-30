"""ParserEngine — dispatches to the correct parser and writes RawExtractedItems."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from organic_market_agent.models import NormalizerProfile, RawAsset, RawExtractedItem, Source
from organic_market_agent.parsers.base import BaseParser, RawItem
from organic_market_agent.parsers.easyfarm_catalog import EasyFarmCatalogParser
from organic_market_agent.parsers.official_wholesale import OfficialWholesaleParser
from organic_market_agent.parsers.simple_product_grid import SimpleProductGridParser
from organic_market_agent.utils.exceptions import ParserError
from organic_market_agent.utils.log_persist import persist_error_log
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_PARSER_MAP: dict[str, type[BaseParser]] = {
    "easyfarm_catalog": EasyFarmCatalogParser,
    "simple_product_grid": SimpleProductGridParser,
    "basket_only": SimpleProductGridParser,
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
        ingestion_run_id: Optional[int] = None,
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

        # Warn when ingesting from non-price_grid sources (informational — does not skip)
        try:
            if getattr(source, "source_tier", None) in ("discovery", "basket"):
                logger.warning(
                    "Source %s has tier='%s' — extracted items will be quarantined "
                    "and skipped by the normalizer",
                    source.code,
                    source.source_tier,
                )
        except Exception:
            pass  # source_tier not yet available (pre-migration 013)

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
            persist_error_log(
                session,
                module="parsers.engine",
                message=f"Parser error for {source.code} raw_asset={raw_asset.id}: {exc}",
                ingestion_run_id=ingestion_run_id,
                entity_type="raw_asset",
                entity_id=raw_asset.id,
                extra={"source_code": source.code, "normalizer_type": normalizer_type},
            )
            return 0

        np_row = session.execute(
            select(NormalizerProfile.id).where(
                NormalizerProfile.source_id == source.id,
                NormalizerProfile.normalizer_type == normalizer_type,
                NormalizerProfile.is_active.is_(True),
            )
        ).scalar_one_or_none()

        valid_items = [
            item for item in raw_items if item.raw_product_name and item.raw_price_text
        ]
        skipped_count = len(raw_items) - len(valid_items)
        if skipped_count:
            logger.warning(
                "ParserEngine: skipped %d incomplete items (no name or price) for source=%s",
                skipped_count,
                source.code,
            )

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
            for item in valid_items
        ]

        session.add_all(db_items)
        logger.info(
            "ParserEngine: wrote %d raw_extracted_items for source=%s (%d skipped)",
            len(db_items),
            source.code,
            skipped_count,
        )
        return len(db_items)
