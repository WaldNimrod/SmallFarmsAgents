"""Normalizer working context for one RawExtractedItem."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from organic_market_agent.models.catalog_scope_skip import CatalogScopeSkipRule


@dataclass
class NormContext:
    """Mutable working context passed through all 7 stages for one RawExtractedItem."""

    raw_item_id: int
    source_id: int
    source_fetch_run_id: int
    normalizer_profile_id: Optional[int]

    raw_product_name: Optional[str]
    raw_price_text: Optional[str]
    raw_unit_text: Optional[str]
    raw_quantity_text: Optional[str]
    raw_payload_json: Optional[dict[str, Any]] = None

    product_id: Optional[int] = None
    product_variant_id: Optional[int] = None
    is_basket_product: bool = False
    is_organic_claimed: bool = False
    is_benchmark: bool = False
    market_scope: str = "community"
    sales_channel: str = "community_direct"

    price_amount: Optional[Decimal] = None
    currency_code: str = "ILS"
    display_unit_id: Optional[int] = None
    normalized_price_value: Optional[Decimal] = None
    normalized_unit_id: Optional[int] = None
    normalization_method: Optional[str] = None

    confidence_score: Decimal = Decimal("1.0")
    flag_status: str = "ok"
    flag_reason: Optional[str] = None

    stage_failed: Optional[str] = None
    unresolvable_reason: Optional[str] = None

    # Populated by NormalizerEngine; ordered by display_order (first match wins).
    catalog_scope_skip_rules: tuple["CatalogScopeSkipRule", ...] | None = None

    resolution_notes: list[str] = field(default_factory=list)
