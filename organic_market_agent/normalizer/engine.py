"""NormalizerEngine — runs all 7 stages for each RawExtractedItem."""
from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import (
    CatalogScopeSkipRule,
    NormalizedObservation,
    RawExtractedItem,
    Source,
    SourceFetchRun,
)
from . import (
    alias_resolver,
    basket_handler,
    confidence as confidence_mod,
    organic_flag,
    price_normalizer,
    price_parser,
    quantity_parser,
    scope_skip,
    unit_resolver,
)
from .context import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

STAGES = [
    ("scope_skip", scope_skip.run),
    ("alias", alias_resolver.run),
    ("organic_flag", organic_flag.run),
    ("price_parse", price_parser.run),
    ("unit_resolve", unit_resolver.run),
    ("qty_parse", quantity_parser.run),
    ("price_norm", price_normalizer.run),
    ("basket", basket_handler.run),
]

BLOCKING_STAGES = frozenset({"alias", "price_parse"})


class NormalizerEngine:
    """Normalizes all pending RawExtractedItems."""

    def run(
        self,
        session: Session,
        ingestion_run_id: int | None = None,
        source_id: int | None = None,
    ) -> dict[str, int]:
        """Normalize pending raw_extracted_items with extraction_status='extracted'."""
        stmt = (
            sa.select(RawExtractedItem)
            .join(SourceFetchRun, RawExtractedItem.source_fetch_run_id == SourceFetchRun.id)
            .where(RawExtractedItem.extraction_status == "extracted")
            .where(RawExtractedItem.is_quarantined.is_(False))
            .order_by(RawExtractedItem.id)
        )
        if ingestion_run_id is not None:
            stmt = stmt.where(SourceFetchRun.ingestion_run_id == ingestion_run_id)
        if source_id is not None:
            stmt = stmt.where(SourceFetchRun.source_id == source_id)

        items = list(session.scalars(stmt).unique().all())

        rules_tuple = tuple(
            session.scalars(
                sa.select(CatalogScopeSkipRule)
                .where(CatalogScopeSkipRule.is_active.is_(True))
                .order_by(CatalogScopeSkipRule.display_order)
            ).all()
        )

        counts = {"resolved": 0, "unresolvable": 0, "skipped": 0, "scope_skipped": 0}

        for item in items:
            fetch_run = session.get(SourceFetchRun, item.source_fetch_run_id)
            if not fetch_run:
                counts["skipped"] += 1
                continue

            src = session.get(Source, fetch_run.source_id)
            if not src:
                counts["skipped"] += 1
                continue

            ctx = NormContext(
                raw_item_id=item.id,
                source_id=fetch_run.source_id,
                source_fetch_run_id=item.source_fetch_run_id,
                normalizer_profile_id=item.normalizer_profile_id,
                raw_product_name=item.raw_product_name,
                raw_price_text=item.raw_price_text,
                raw_unit_text=item.raw_unit_text,
                raw_quantity_text=item.raw_quantity_text,
                raw_payload_json=item.raw_payload_json,
                market_scope=src.market_scope,
                sales_channel=src.sales_channel,
                is_benchmark=(src.market_scope == "benchmark"),
                catalog_scope_skip_rules=rules_tuple,
            )

            for _stage_name, stage_fn in STAGES:
                ctx = stage_fn(ctx, session)
                if ctx.stage_failed == scope_skip.STAGE:
                    break
                if ctx.stage_failed in BLOCKING_STAGES:
                    break

            if ctx.stage_failed == scope_skip.STAGE:
                item.extraction_status = "ignored"
                item.ignore_reason_code = "approved_scope_skip"
                item.unresolvable_reason = (ctx.unresolvable_reason or "")[:500]
                counts["scope_skipped"] += 1
                continue

            if ctx.stage_failed in BLOCKING_STAGES:
                item.extraction_status = "unresolvable"
                item.unresolvable_reason = (ctx.unresolvable_reason or "")[:500]
                counts["unresolvable"] += 1
                continue

            if ctx.product_id is None or ctx.price_amount is None or ctx.display_unit_id is None:
                item.extraction_status = "unresolvable"
                item.unresolvable_reason = (
                    ctx.unresolvable_reason or "missing product_id, price, or display_unit after stages"
                )[:500]
                counts["unresolvable"] += 1
                continue

            ctx.confidence_score = confidence_mod.calculate(ctx)
            obs = NormalizedObservation(
                source_id=ctx.source_id,
                source_fetch_run_id=ctx.source_fetch_run_id,
                raw_extracted_item_id=ctx.raw_item_id,
                product_id=ctx.product_id,
                market_scope=ctx.market_scope,
                sales_channel=ctx.sales_channel,
                is_benchmark=ctx.is_benchmark,
                is_basket_product=ctx.is_basket_product,
                is_organic_claimed=ctx.is_organic_claimed,
                price_amount=ctx.price_amount,
                currency_code=ctx.currency_code,
                display_unit_id=ctx.display_unit_id,
                normalized_price_value=ctx.normalized_price_value,
                normalized_unit_id=ctx.normalized_unit_id,
                normalization_method=ctx.normalization_method,
                confidence_score=ctx.confidence_score,
                flag_status=ctx.flag_status,
                flag_reason=ctx.flag_reason,
                observed_at=datetime.now(timezone.utc),
            )
            session.add(obs)
            item.extraction_status = "normalized"
            counts["resolved"] += 1

        session.commit()
        logger.info(
            "NormalizerEngine complete: resolved=%d unresolvable=%d scope_skipped=%d skipped=%d",
            counts["resolved"],
            counts["unresolvable"],
            counts["scope_skipped"],
            counts["skipped"],
        )
        return counts
