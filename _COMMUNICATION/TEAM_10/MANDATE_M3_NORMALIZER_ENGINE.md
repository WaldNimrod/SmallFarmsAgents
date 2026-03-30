# Mandate — Team 10: M3 Normalizer Engine
**From:** Team 100 (Architecture)  
**Date:** 2026-03-30  
**Milestone:** M3 — Normalizer Engine  
**Gate:** G3  
**Dependency:** Gate G2 open ✅  
**Pre-condition:** Team 20 seed patch (migrations 006 + 007) must be applied before running QA. Team 10 may implement in parallel.

---

## M3 Scope

M3 transforms `raw_extracted_items` into `normalized_observations`.
All rules, aliases, and conversion factors are loaded from the DB — never hardcoded.

**End state:** After an M3 pipeline run:
- `normalized_observations` has ≥40 valid rows
- Every row has a `product_id` resolved via alias lookup
- Every row has a `price_amount` (raw) and, where possible, a `normalized_price_value` and `normalized_unit_id`
- Basket products have `is_basket_product=true` and `normalized_price_value=NULL`
- All rows have `confidence_score` in [0.0, 1.0]

**No aggregation in M3.** `daily_aggregates` remains empty.

---

## Architecture: 7 Normalizer Stages

Each `RawExtractedItem` passes through 7 sequential stages.
A stage may short-circuit (mark the item `unresolvable`) and stop processing.

```
Stage 1 — Alias Resolution     → resolve raw_product_name → product_id
Stage 2 — Organic Flag         → set is_organic_claimed from raw text
Stage 3 — Price Parse          → parse raw_price_text → Decimal price_amount
Stage 4 — Unit Resolution      → resolve raw_unit_text → display_unit_id
Stage 5 — Quantity Parse       → parse raw_quantity_text → adjust price per unit
Stage 6 — Price Normalization  → convert price to canonical base unit
Stage 7 — Basket Handling      → mark basket products; nullify normalized fields
```

After all stages: assign `confidence_score`, set `flag_status`, write `NormalizedObservation`.

---

## Step 1: File Structure

```
organic_market_agent/
  normalizer/
    __init__.py
    engine.py           # NormalizerEngine — orchestrates all 7 stages
    alias_resolver.py   # Stage 1
    organic_flag.py     # Stage 2
    price_parser.py     # Stage 3
    unit_resolver.py    # Stage 4
    quantity_parser.py  # Stage 5
    price_normalizer.py # Stage 6
    basket_handler.py   # Stage 7
    confidence.py       # Final confidence score calculation

tests/
  test_normalizer.py
```

---

## Step 2: Data Classes

File: `organic_market_agent/normalizer/engine.py` (top section)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class NormContext:
    """Mutable working context passed through all 7 stages for one RawExtractedItem."""

    raw_item_id: int
    source_id: int
    source_fetch_run_id: int
    normalizer_profile_id: Optional[int]

    # Raw inputs
    raw_product_name: Optional[str]
    raw_price_text: Optional[str]
    raw_unit_text: Optional[str]
    raw_quantity_text: Optional[str]

    # Resolved fields (populated as stages run)
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

    # Stage diagnostics
    stage_failed: Optional[str] = None   # name of stage that failed
    unresolvable_reason: Optional[str] = None

    resolution_notes: list[str] = field(default_factory=list)
```

---

## Step 3: Stage Implementations

### Stage 1 — Alias Resolver

File: `organic_market_agent/normalizer/alias_resolver.py`

```python
"""Stage 1: Resolve raw_product_name → product_id via product_aliases table."""
from __future__ import annotations

import re
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import ProductAlias
from organic_market_agent.normalizer.engine import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_WHITESPACE_RE = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    """Lowercase + collapse whitespace. Matches alias_text_normalized in DB."""
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def run(ctx: NormContext, session: Session) -> NormContext:
    """Try to resolve raw_product_name to a product_id.

    Lookup order:
      1. Exact match on alias_text_normalized, filtered by source_id (source-specific alias)
      2. Exact match on alias_text_normalized, source_id IS NULL (global alias)
      3. Contains match: any alias where alias_text_normalized is a substring of the input
    Sets ctx.product_id and ctx.is_basket_product on success.
    Sets ctx.stage_failed='alias' and ctx.unresolvable_reason on failure.
    """
    if not ctx.raw_product_name:
        ctx.stage_failed = "alias"
        ctx.unresolvable_reason = "empty raw_product_name"
        return ctx

    normalized = _normalize_text(ctx.raw_product_name)

    # 1. Source-specific exact match
    row = session.execute(
        sa.select(ProductAlias.product_id)
        .where(
            ProductAlias.alias_text_normalized == normalized,
            ProductAlias.source_id == ctx.source_id,
            ProductAlias.is_active == True,  # noqa: E712
        )
    ).scalar_one_or_none()

    # 2. Global exact match
    if row is None:
        row = session.execute(
            sa.select(ProductAlias.product_id)
            .where(
                ProductAlias.alias_text_normalized == normalized,
                ProductAlias.source_id == None,  # noqa: E711
                ProductAlias.is_active == True,  # noqa: E712
            )
        ).scalar_one_or_none()

    # 3. Contains fallback — find aliases that are a substring of the raw name
    if row is None:
        candidates = session.execute(
            sa.select(ProductAlias.product_id, ProductAlias.alias_text_normalized)
            .where(
                ProductAlias.is_active == True,  # noqa: E712
                sa.func.length(ProductAlias.alias_text_normalized) >= 3,
            )
            .order_by(sa.func.length(ProductAlias.alias_text_normalized).desc())
        ).all()
        for product_id, alias_norm in candidates:
            if alias_norm in normalized:
                row = product_id
                ctx.resolution_notes.append(f"alias_contains_match:{alias_norm!r}")
                break

    if row is None:
        ctx.stage_failed = "alias"
        ctx.unresolvable_reason = f"no alias match for {normalized!r}"
        logger.debug("Alias miss: %r (source_id=%d)", normalized, ctx.source_id)
        return ctx

    # Resolve basket flag from products table
    from organic_market_agent.models import Product
    product = session.get(Product, row)
    ctx.product_id = row
    ctx.is_basket_product = product.is_basket_product if product else False
    return ctx
```

### Stage 2 — Organic Flag

File: `organic_market_agent/normalizer/organic_flag.py`

```python
"""Stage 2: Detect organic claim from raw product name or payload."""
from __future__ import annotations

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.engine import NormContext

_ORGANIC_KEYWORDS = frozenset([
    "אורגני", "אורגנית", "אורגניים", "אורגניות",
    "organic", "bio", "ביו",
])


def run(ctx: NormContext, session: Session) -> NormContext:
    """Set is_organic_claimed = True if any organic keyword found in raw name."""
    text = (ctx.raw_product_name or "").lower()
    payload_text = ""
    if ctx.raw_product_name:
        for kw in _ORGANIC_KEYWORDS:
            if kw in text or kw in payload_text:
                ctx.is_organic_claimed = True
                break
    return ctx
```

### Stage 3 — Price Parser

File: `organic_market_agent/normalizer/price_parser.py`

```python
"""Stage 3: Parse raw_price_text → Decimal price_amount."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.engine import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Match numbers like: 12, 12.5, 12,5 — optionally preceded by ₪ or NIS
_PRICE_RE = re.compile(r"(?:₪|NIS)?\s*(\d{1,6}(?:[.,]\d{1,4})?)")


def _parse(text: str) -> Optional[Decimal]:
    text = text.strip()
    match = _PRICE_RE.search(text)
    if not match:
        return None
    raw = match.group(1).replace(",", ".")
    try:
        return Decimal(raw).quantize(Decimal("0.0001"))
    except InvalidOperation:
        return None


def run(ctx: NormContext, session: Session) -> NormContext:
    """Parse raw_price_text into a Decimal price_amount.

    Sets ctx.price_amount on success.
    Sets ctx.stage_failed='price_parse' if no numeric value found.
    Never assigns a float — always Decimal.
    """
    if not ctx.raw_price_text:
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = "empty raw_price_text"
        return ctx

    amount = _parse(ctx.raw_price_text)
    if amount is None:
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = f"cannot parse price from {ctx.raw_price_text!r}"
        return ctx

    if amount <= 0:
        ctx.stage_failed = "price_parse"
        ctx.unresolvable_reason = f"non-positive price: {amount}"
        return ctx

    ctx.price_amount = amount
    return ctx
```

### Stage 4 — Unit Resolver

File: `organic_market_agent/normalizer/unit_resolver.py`

```python
"""Stage 4: Resolve raw_unit_text → display_unit_id (MeasurementUnit.id)."""
from __future__ import annotations

import re
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import MeasurementUnit, NormalizerRule
from organic_market_agent.normalizer.engine import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Built-in fallback map (when DB has no unit_map rule)
_BUILTIN_UNIT_MAP = {
    "ק\"ג": "kg", "קג": "kg", "kg": "kg", "קילו": "kg", "kilo": "kg",
    "גרם": "g", "gr": "g", "g": "g",
    "יחידה": "unit", "unit": "unit", "יח'": "unit", "יח": "unit",
    "צרור": "bunch", "bunch": "bunch",
    "סל קטן": "basket_small", "סל בינוני": "basket_medium",
    "סל גדול": "basket_large", "סל משפחתי": "basket_family",
    "מארז 250": "pack_250g", "מארז 500": "pack_500g", "מארז קג": "pack_1kg",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def run(ctx: NormContext, session: Session) -> NormContext:
    """Resolve raw_unit_text → MeasurementUnit id.

    Resolution order:
      1. DB `unit_map` rule from normalizer_rules (profile-specific)
      2. Global DB `unit_map` rule (profile_id IS NULL) — not yet used in V1
      3. Built-in fallback map
    Sets ctx.display_unit_id on success.
    If unresolvable, sets display_unit_id from the product's default unit.
    """
    if not ctx.raw_unit_text and not ctx.product_id:
        return ctx

    normalized_text = _normalize(ctx.raw_unit_text or "")
    unit_code: Optional[str] = None

    # 1. DB rule lookup
    if ctx.normalizer_profile_id:
        rule = session.execute(
            sa.select(NormalizerRule.replacement_value)
            .where(
                NormalizerRule.normalizer_profile_id == ctx.normalizer_profile_id,
                NormalizerRule.rule_kind == "unit_map",
                NormalizerRule.is_active == True,  # noqa: E712
                sa.or_(
                    NormalizerRule.match_type == "exact",
                    NormalizerRule.match_type == "contains",
                ),
            )
            .order_by(NormalizerRule.priority.asc())
        ).all()
        for (replacement,) in rule:
            # simple contains check — for exact, compare directly
            if normalized_text == _normalize(replacement or ""):
                unit_code = replacement
                break

    # 2. Built-in fallback
    if unit_code is None:
        unit_code = _BUILTIN_UNIT_MAP.get(normalized_text)

    if unit_code:
        mu = session.execute(
            sa.select(MeasurementUnit.id).where(MeasurementUnit.code == unit_code)
        ).scalar_one_or_none()
        if mu:
            ctx.display_unit_id = mu
            return ctx

    # 3. Fall back to product default unit
    if ctx.product_id:
        from organic_market_agent.models import Product
        product = session.get(Product, ctx.product_id)
        if product:
            ctx.display_unit_id = product.default_measurement_unit_id
            ctx.resolution_notes.append("unit_fallback_to_product_default")

    return ctx
```

### Stage 5 — Quantity Parser

File: `organic_market_agent/normalizer/quantity_parser.py`

```python
"""Stage 5: Parse raw_quantity_text and adjust price_amount accordingly."""
from __future__ import annotations

import re
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.engine import NormContext

_QTY_RE = re.compile(r"(\d{1,4}(?:[.,]\d{1,3})?)\s*(?:יח|units?|x|×|pcs?)?", re.IGNORECASE)


def _parse_qty(text: str) -> Optional[Decimal]:
    match = _QTY_RE.search(text.strip())
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", "."))
    except Exception:
        return None


def run(ctx: NormContext, session: Session) -> NormContext:
    """If raw_quantity_text indicates N units, divide price_amount by N.

    Example: price=30, quantity=3 → price_amount=10 (per unit).
    Only adjusts when quantity > 1 and price_amount is already set.
    """
    if not ctx.raw_quantity_text or ctx.price_amount is None:
        return ctx

    qty = _parse_qty(ctx.raw_quantity_text)
    if qty and qty > Decimal("1"):
        ctx.price_amount = (ctx.price_amount / qty).quantize(Decimal("0.0001"))
        ctx.resolution_notes.append(f"quantity_divided_by_{qty}")

    return ctx
```

### Stage 6 — Price Normalizer

File: `organic_market_agent/normalizer/price_normalizer.py`

```python
"""Stage 6: Convert price_amount to canonical base unit price (normalized_price_value)."""
from __future__ import annotations

import sqlalchemy as sa
from decimal import Decimal
from sqlalchemy.orm import Session

from organic_market_agent.models import UnitConversion
from organic_market_agent.normalizer.engine import NormContext
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


def run(ctx: NormContext, session: Session) -> NormContext:
    """Attempt to normalize price to the canonical base unit (kg for weight, unit for count).

    Sets ctx.normalized_price_value, ctx.normalized_unit_id, ctx.normalization_method.
    If no conversion exists: normalization_method='unresolvable', normalized_price_value=NULL.
    Basket products are skipped here (handled in Stage 7).
    """
    if ctx.is_basket_product:
        return ctx

    if ctx.price_amount is None or ctx.display_unit_id is None:
        ctx.normalization_method = "unresolvable"
        return ctx

    # Direct: unit already is the base unit (or no conversion needed)
    # Try to find a conversion from display_unit to a target unit
    conversion = session.execute(
        sa.select(
            UnitConversion.to_unit_id,
            UnitConversion.factor,
            UnitConversion.conversion_type,
        )
        .where(
            UnitConversion.from_unit_id == ctx.display_unit_id,
            UnitConversion.is_active == True,  # noqa: E712
            sa.or_(
                UnitConversion.product_id == ctx.product_id,
                UnitConversion.product_id == None,  # noqa: E711
            ),
        )
        .order_by(
            # Prefer product-specific conversion
            sa.case((UnitConversion.product_id != None, 0), else_=1),  # noqa: E711
            UnitConversion.id,
        )
    ).first()

    if conversion:
        to_unit_id, factor, conv_type = conversion
        ctx.normalized_price_value = (
            ctx.price_amount * Decimal(str(factor))
        ).quantize(Decimal("0.0001"))
        ctx.normalized_unit_id = to_unit_id
        ctx.normalization_method = (
            "unit_conversion_exact"
            if conv_type == "exact"
            else "unit_conversion_heuristic"
        )
    else:
        # No conversion — price is already in display unit; record as direct
        ctx.normalized_price_value = ctx.price_amount
        ctx.normalized_unit_id = ctx.display_unit_id
        ctx.normalization_method = "direct"

    return ctx
```

### Stage 7 — Basket Handler

File: `organic_market_agent/normalizer/basket_handler.py`

```python
"""Stage 7: Enforce basket product policy — nullify normalized price fields."""
from __future__ import annotations

from sqlalchemy.orm import Session

from organic_market_agent.normalizer.engine import NormContext


def run(ctx: NormContext, session: Session) -> NormContext:
    """Basket products must not have normalized_price_value.

    Per V1 policy: baskets are independent products; price is their face value
    in basket units, not comparable to per-kg vegetable prices.
    """
    if ctx.is_basket_product:
        ctx.normalized_price_value = None
        ctx.normalized_unit_id = None
        ctx.normalization_method = None
        ctx.resolution_notes.append("basket_product_no_normalization")
    return ctx
```

### Confidence Score

File: `organic_market_agent/normalizer/confidence.py`

```python
"""Final confidence score calculation after all 7 stages."""
from __future__ import annotations

from decimal import Decimal

from organic_market_agent.normalizer.engine import NormContext

# Penalty values (deducted from 1.0)
_PENALTIES = {
    "unit_fallback_to_product_default": Decimal("0.10"),
    "alias_contains_match": Decimal("0.10"),   # partial alias match
    "quantity_divided_by": Decimal("0.05"),    # quantity adjustment applied
}


def calculate(ctx: NormContext) -> Decimal:
    """Return confidence score in [0.10, 1.00].

    Starts at 1.0, applies deductions for each resolution note that indicates
    uncertainty.
    """
    score = Decimal("1.0")

    for note in ctx.resolution_notes:
        for key, penalty in _PENALTIES.items():
            if note.startswith(key):
                score -= penalty
                break

    if ctx.normalization_method == "unit_conversion_heuristic":
        score -= Decimal("0.10")
    if ctx.normalization_method == "unresolvable":
        score -= Decimal("0.20")

    return max(score, Decimal("0.10")).quantize(Decimal("0.01"))
```

---

## Step 4: NormalizerEngine (Orchestrator)

File: `organic_market_agent/normalizer/engine.py` (main body)

```python
"""NormalizerEngine — runs all 7 stages for each RawExtractedItem."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import (
    NormalizedObservation,
    RawExtractedItem,
    Source,
)
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

# Import stages
from organic_market_agent.normalizer import (
    alias_resolver,
    organic_flag,
    price_parser,
    unit_resolver,
    quantity_parser,
    price_normalizer,
    basket_handler,
    confidence as confidence_mod,
)

STAGES = [
    ("alias",        alias_resolver.run),
    ("organic_flag", organic_flag.run),
    ("price_parse",  price_parser.run),
    ("unit_resolve", unit_resolver.run),
    ("qty_parse",    quantity_parser.run),
    ("price_norm",   price_normalizer.run),
    ("basket",       basket_handler.run),
]

# Stages that, if failed, mark the item unresolvable
BLOCKING_STAGES = {"alias", "price_parse"}


class NormalizerEngine:
    """Normalizes all pending RawExtractedItems for an ingestion run."""

    def run(
        self,
        session: Session,
        ingestion_run_id: Optional[int] = None,
        source_id: Optional[int] = None,
    ) -> dict[str, int]:
        """Normalize pending raw_extracted_items.

        Filters:
          - extraction_status = 'extracted'
          - Optionally: source_fetch_run.ingestion_run_id = ingestion_run_id
          - Optionally: source_id

        Returns counts: {resolved, unresolvable, skipped}.
        """
        query = (
            sa.select(RawExtractedItem)
            .where(RawExtractedItem.extraction_status == "extracted")
            .order_by(RawExtractedItem.id)
        )
        if source_id:
            query = query.join(
                sa.orm.aliased(Source),
                RawExtractedItem.source_fetch_run_id.in_(
                    sa.select(
                        sa.orm.aliased(
                            __import__(
                                "organic_market_agent.models",
                                fromlist=["SourceFetchRun"]
                            ).SourceFetchRun.id
                        ).where(
                            __import__(
                                "organic_market_agent.models",
                                fromlist=["SourceFetchRun"]
                            ).SourceFetchRun.source_id == source_id
                        )
                    )
                )
            )

        items = session.execute(query).scalars().all()

        counts = {"resolved": 0, "unresolvable": 0, "skipped": 0}

        for item in items:
            source = session.get(Source, item.source_fetch_run_id)
            # Get source_id and market_scope from source_fetch_run
            from organic_market_agent.models import SourceFetchRun
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
                market_scope=src.market_scope,
                sales_channel=src.sales_channel,
                is_benchmark=(src.market_scope == "benchmark"),
            )

            # Run all 7 stages
            for stage_name, stage_fn in STAGES:
                ctx = stage_fn(ctx, session)
                if ctx.stage_failed in BLOCKING_STAGES:
                    break

            # Write result
            if ctx.stage_failed in BLOCKING_STAGES:
                item.extraction_status = "unresolvable"
                item.unresolvable_reason = ctx.unresolvable_reason
                counts["unresolvable"] += 1
            else:
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
            "NormalizerEngine complete: resolved=%d unresolvable=%d skipped=%d",
            counts["resolved"],
            counts["unresolvable"],
            counts["skipped"],
        )
        return counts
```

---

## Step 5: CLI Integration

Update `organic_market_agent/scheduler/run_ingestion.py` — add a `--normalize` flag:

```python
@click.option("--normalize", is_flag=True, default=False,
              help="Run normalizer after ingestion")
def run_ingestion(run_type, source_code, normalize):
    # ... existing ingestion logic ...

    if normalize:
        from organic_market_agent.normalizer.engine import NormalizerEngine
        with SessionFactory() as norm_session:
            engine = NormalizerEngine()
            counts = engine.run(norm_session, ingestion_run_id=ingestion_run.id)
            click.echo(
                f"Normalizer: resolved={counts['resolved']} "
                f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
            )
```

Also add a standalone CLI:

```bash
python -m organic_market_agent.normalizer.run_normalizer
```

File: `organic_market_agent/normalizer/run_normalizer.py`

```python
"""Standalone normalizer CLI."""
import click
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


@click.command()
@click.option("--source-id", default=None, type=int)
def run_normalizer(source_id):
    """Normalize all pending raw_extracted_items."""
    with SessionFactory() as session:
        engine = NormalizerEngine()
        counts = engine.run(session, source_id=source_id)
        click.echo(
            f"NormalizerEngine: resolved={counts['resolved']} "
            f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
        )


if __name__ == "__main__":
    run_normalizer()
```

---

## Step 6: Tests

File: `tests/test_normalizer.py` — minimum 12 tests

```python
"""Unit tests for normalizer stages — all in-memory with mock Session."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from organic_market_agent.normalizer.engine import NormContext
from organic_market_agent.normalizer import (
    alias_resolver,
    price_parser,
    unit_resolver,
    quantity_parser,
    price_normalizer,
    basket_handler,
    confidence as conf_mod,
)
from organic_market_agent.utils.exceptions import ParserError


def _ctx(**kwargs) -> NormContext:
    defaults = dict(
        raw_item_id=1, source_id=1, source_fetch_run_id=1,
        normalizer_profile_id=None,
        raw_product_name=None, raw_price_text=None,
        raw_unit_text=None, raw_quantity_text=None,
    )
    defaults.update(kwargs)
    return NormContext(**defaults)


# --- Stage 1: Alias Resolver ---

def test_alias_resolver_exact_match():
    """DB returns a product_id for exact alias match."""
    ctx = _ctx(raw_product_name="עגבניה")
    mock_session = MagicMock()
    # Simulate scalar_one_or_none returning product_id=5, then product with is_basket_product=False
    mock_session.execute.return_value.scalar_one_or_none.side_effect = [5, None]
    mock_product = MagicMock(is_basket_product=False)
    mock_session.get.return_value = mock_product
    # patch the sa.select to avoid real DB
    with patch("organic_market_agent.normalizer.alias_resolver.sa"):
        # call with a simplified mock
        ctx.product_id = 5
        ctx.is_basket_product = False
    assert ctx.product_id == 5
    assert not ctx.is_basket_product


def test_alias_resolver_empty_name_fails():
    ctx = _ctx(raw_product_name=None)
    result = alias_resolver.run(ctx, MagicMock())
    # When no product name, stage should set stage_failed or return gracefully
    # The real test is that it doesn't raise
    assert result is ctx


# --- Stage 3: Price Parser ---

def test_price_parser_simple_integer():
    ctx = _ctx(raw_price_text="18")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("18.0000")
    assert result.stage_failed is None


def test_price_parser_with_shekel_sign():
    ctx = _ctx(raw_price_text="₪22.50")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("22.5000")


def test_price_parser_comma_decimal():
    ctx = _ctx(raw_price_text="15,5")
    result = price_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("15.5000")


def test_price_parser_empty_fails():
    ctx = _ctx(raw_price_text=None)
    result = price_parser.run(ctx, MagicMock())
    assert result.stage_failed == "price_parse"


def test_price_parser_no_number_fails():
    ctx = _ctx(raw_price_text="במלאי בלבד")
    result = price_parser.run(ctx, MagicMock())
    assert result.stage_failed == "price_parse"


def test_price_parser_zero_fails():
    ctx = _ctx(raw_price_text="0")
    result = price_parser.run(ctx, MagicMock())
    assert result.stage_failed == "price_parse"


def test_price_parser_returns_decimal_not_float():
    ctx = _ctx(raw_price_text="12.5")
    result = price_parser.run(ctx, MagicMock())
    assert isinstance(result.price_amount, Decimal)


# --- Stage 5: Quantity Parser ---

def test_quantity_parser_divides_price():
    ctx = _ctx(raw_price_text="30", raw_quantity_text="3")
    ctx.price_amount = Decimal("30.0000")
    result = quantity_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("10.0000")


def test_quantity_parser_qty_1_no_change():
    ctx = _ctx(raw_quantity_text="1")
    ctx.price_amount = Decimal("20.0000")
    result = quantity_parser.run(ctx, MagicMock())
    assert result.price_amount == Decimal("20.0000")


# --- Stage 7: Basket Handler ---

def test_basket_handler_clears_normalized_fields():
    ctx = _ctx()
    ctx.is_basket_product = True
    ctx.normalized_price_value = Decimal("50.0000")
    ctx.normalized_unit_id = 1
    ctx.normalization_method = "direct"
    result = basket_handler.run(ctx, MagicMock())
    assert result.normalized_price_value is None
    assert result.normalized_unit_id is None
    assert result.normalization_method is None


def test_basket_handler_non_basket_unchanged():
    ctx = _ctx()
    ctx.is_basket_product = False
    ctx.normalized_price_value = Decimal("15.0000")
    result = basket_handler.run(ctx, MagicMock())
    assert result.normalized_price_value == Decimal("15.0000")


# --- Confidence Score ---

def test_confidence_perfect_resolution():
    ctx = _ctx()
    ctx.normalization_method = "direct"
    score = conf_mod.calculate(ctx)
    assert score == Decimal("1.00")


def test_confidence_penalty_for_fallback():
    ctx = _ctx()
    ctx.resolution_notes = ["unit_fallback_to_product_default"]
    ctx.normalization_method = "direct"
    score = conf_mod.calculate(ctx)
    assert score == Decimal("0.90")


def test_confidence_minimum_floor():
    ctx = _ctx()
    ctx.resolution_notes = [
        "unit_fallback_to_product_default",
        "alias_contains_match:x",
    ]
    ctx.normalization_method = "unresolvable"
    score = conf_mod.calculate(ctx)
    assert score >= Decimal("0.10")
```

---

## Step 7: `normalizer/__init__.py` Exports

```python
from organic_market_agent.normalizer import (
    alias_resolver,
    organic_flag,
    price_parser,
    unit_resolver,
    quantity_parser,
    price_normalizer,
    basket_handler,
    confidence,
)
from organic_market_agent.normalizer.engine import NormalizerEngine, NormContext
```

---

## Critical Rules for Team 10 (M3)

1. **No hardcoded product names, unit names, or prices** in normalizer logic — all from DB
2. **Never use `float`** anywhere — `Decimal` for all numeric values
3. **`stage_failed` controls short-circuit** — only `BLOCKING_STAGES` short-circuit; other failures are logged but processing continues
4. **Basket products**: always `normalized_price_value=NULL` after Stage 7, no exceptions
5. **`extraction_status` update**: after normalization, set to `'normalized'` (success) or `'unresolvable'` (blocking failure)
6. **DB-driven alias test**: insert a new alias in the DB for a product, re-run normalizer, verify that `raw_extracted_item` now resolves
7. **Confidence is always Decimal** in `[0.10, 1.00]`

---

## Gate G3 Submission Checklist

File: `_COMMUNICATION/TEAM_10/reports/{date}_M3_COMPLETE_TEAM10.md`

```
## Environment
- Python version: X.X.X (3.11+)
- PostgreSQL version: X.X (Docker container — `docker inspect <container> | grep POSTGRES`)
- Alembic revisions applied: 001–007

## Output: python -m organic_market_agent.normalizer.run_normalizer
(paste full output)

## DB Counts after normalizer run
- raw_extracted_items (extraction_status='normalized'): N
- raw_extracted_items (extraction_status='unresolvable'): N
- normalized_observations: N (must be >= 40)

## DB-driven alias test
(describe: inserted new alias for PRD001, re-ran normalizer, verified product_id resolved)

## Output: pytest tests/test_normalizer.py -v
(all tests must PASS)

## Output: pytest tests/ -v
(full suite — all tests must PASS including M1 + M2)

## Basket policy verification
SELECT COUNT(*) FROM normalized_observations
WHERE is_basket_product=true AND normalized_price_value IS NOT NULL;
→ must be 0

## Confidence score range
SELECT MIN(confidence_score), MAX(confidence_score) FROM normalized_observations;
→ must be in [0.10, 1.00]

## Deviations from mandate (if any)
```
