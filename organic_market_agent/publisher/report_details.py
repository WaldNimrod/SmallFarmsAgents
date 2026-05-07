"""M13: product ``details`` for publish JSON v3 — variants, price_series, CSA merge (privacy-safe)."""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from organic_market_agent.models import Product

# Caps per Team 100 ARCH-20260404-M13-APPROVED-PENDING-PRE
PRICE_SERIES_DAILY_MAX = 30
PRICE_SERIES_WEEKLY_MAX = 12
PRICE_SERIES_MIN_POINTS = 3
REPORT_JSON_SOFT_LIMIT_BYTES = 512_000
TRUNCATE_SERIES_TO = 15


def apply_soft_json_size_limit_to_payload(payload: dict[str, Any], logger: Any = None) -> None:
    """If serialized JSON exceeds soft limit, trim ``price_series`` to last TRUNCATE_SERIES_TO points (in-place)."""
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(raw) <= REPORT_JSON_SOFT_LIMIT_BYTES:
        return
    for p in payload.get("products") or []:
        det = p.get("details")
        if not isinstance(det, dict):
            continue
        ps = det.get("price_series")
        if isinstance(ps, list) and len(ps) > TRUNCATE_SERIES_TO:
            det["price_series"] = ps[-TRUNCATE_SERIES_TO :]
    if logger:
        raw2 = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        logger.warning(
            "Publish JSON exceeded %s bytes after publish build; trimmed price_series to %s points: now %s bytes",
            REPORT_JSON_SOFT_LIMIT_BYTES,
            TRUNCATE_SERIES_TO,
            len(raw2),
        )

# Substrings that must not appear in generalized CSA text (privacy + G11 audit overlap)
_FARM_IDENT_BLOCKLIST = (
    "חוות שורשים",
    "משק אורגני",
    "משק יוסף",
    "קיימא",
    "עץ השדה",
    "ניצת הדובדבן",
    "ערן אורגני",
    "טמרי",
    "רעות",
    "טבע שוק",
    "havatshorashim",
    "meshekorgani",
    "meshek-yosef",
    "mypips.app",
)

_SRC_CODE_PATTERN = re.compile(r"SRC\d{3}", re.IGNORECASE)
_URL_PATTERN = re.compile(r"https?://\S+")
# Strip phone numbers from generalized CSA text (privacy — no contact / traceability in public JSON).
_PHONE_IL_PATTERN = re.compile(
    r"(?:\+972|00972)[-\s]?\d{1,2}[-\s]?\d{3}[-\s]?\d{4}|"
    r"\b05\d[-\s]?\d{3}[-\s]?\d{4}\b|"
    r"\b0[2-4]\d[-\s]?\d{3}[-\s]?\d{4}\b",
    re.IGNORECASE,
)


def resolve_details_variant(
    *,
    category: str,
    is_basket_product: bool,
    market_scope: str,
    display_buckets: set[str | None],
) -> str:
    """Approved mapping from M13 architectural approval."""
    if is_basket_product and category == "baskets":
        return "basket_csa"
    if "store" in display_buckets:
        return "store_retail"
    if market_scope == "benchmark":
        return "chain_benchmark"
    return "grower_price_grid"


def _sanitize_public_text(s: str | None) -> str | None:
    if not s or not str(s).strip():
        return None
    t = str(s).strip()
    for block in _FARM_IDENT_BLOCKLIST:
        t = t.replace(block, "")
    t = _SRC_CODE_PATTERN.sub("", t)
    t = _URL_PATTERN.sub("", t)
    t = _PHONE_IL_PATTERN.sub("", t)
    t = " ".join(t.split())
    return t[:1200] if t else None


def _median_float(vals: list[Decimal]) -> float:
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2:
        v = s[mid]
    else:
        v = (s[mid - 1] + s[mid]) / 2
    return float(Decimal(str(v)).quantize(Decimal("0.0001")))


def _week_key(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


_OBS_FOR_SERIES_SQL = text(
    """
    SELECT
        (no.observed_at AT TIME ZONE 'UTC')::date AS obs_day,
        COALESCE(no.normalized_price_value, no.price_amount) AS price
    FROM normalized_observations no
    LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
    WHERE no.product_id = :pid
      AND no.market_scope = :ms
      AND no.sales_channel = :sc
      AND (no.observed_at AT TIME ZONE 'UTC')::date BETWEEN :d_start AND :d_end
      AND no.flag_status = 'ok'
      AND (rei.id IS NULL OR rei.is_quarantined IS NOT TRUE)
    """
)


def compute_price_series(
    session: Session,
    *,
    product_id: int,
    market_scope: str,
    sales_channel: str,
    report_date: date,
    weekly: bool,
) -> list[dict[str, Any]]:
    """Daily median (30d) or weekly median (12w); empty if < PRICE_SERIES_MIN_POINTS."""
    if weekly:
        d_end = report_date
        d_start = report_date - timedelta(days=7 * PRICE_SERIES_WEEKLY_MAX - 1)
        max_keys = PRICE_SERIES_WEEKLY_MAX
    else:
        d_end = report_date
        d_start = report_date - timedelta(days=PRICE_SERIES_DAILY_MAX - 1)
        max_keys = PRICE_SERIES_DAILY_MAX

    rows = session.execute(
        _OBS_FOR_SERIES_SQL,
        {
            "pid": product_id,
            "ms": market_scope,
            "sc": sales_channel,
            "d_start": d_start,
            "d_end": d_end,
        },
    ).all()

    if weekly:
        buckets: dict[str, list[Decimal]] = defaultdict(list)
        for r in rows:
            day_d = r[0]
            if day_d is None:
                continue
            buckets[_week_key(day_d)].append(Decimal(str(r[1])))
        sorted_keys = sorted(buckets.keys())[-max_keys:]
        series = [{"d": k, "v": _median_float(buckets[k])} for k in sorted_keys]
    else:
        buckets = defaultdict(list)
        for r in rows:
            day_d = r[0]
            if day_d is None:
                continue
            buckets[day_d].append(Decimal(str(r[1])))
        sorted_days = sorted(buckets.keys())[-max_keys:]
        series = [
            {"d": day.isoformat(), "v": _median_float(buckets[day])} for day in sorted_days
        ]

    # Drop non-finite values (defense in depth for JSON / charts)
    clean: list[dict[str, Any]] = []
    for pt in series:
        v = pt["v"]
        if not math.isfinite(v):
            continue
        clean.append(pt)

    if len(clean) < PRICE_SERIES_MIN_POINTS:
        return []
    return clean


_CSA_PAYLOADS_SQL = text(
    """
    SELECT DISTINCT ON (no.source_id)
        rei.raw_payload_json
    FROM normalized_observations no
    JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
    WHERE no.product_id = :pid
      AND no.market_scope = :ms
      AND no.sales_channel = :sc
      AND (no.observed_at AT TIME ZONE 'UTC')::date BETWEEN :d_start AND :d_end
      AND no.flag_status = 'ok'
    ORDER BY no.source_id, no.observed_at DESC
    """
)


def merge_csa_details_for_bucket(
    session: Session,
    *,
    product_id: int,
    market_scope: str,
    sales_channel: str,
    d_start: date,
    d_end: date,
) -> dict[str, Any] | None:
    """Merge csa_context from latest REI per source; privacy-safe generalized fields."""
    rows = session.execute(
        _CSA_PAYLOADS_SQL,
        {
            "pid": product_id,
            "ms": market_scope,
            "sc": sales_channel,
            "d_start": d_start,
            "d_end": d_end,
        },
    ).all()

    contents_candidates: list[str] = []
    cadence_candidates: list[str] = []
    incomplete_any = False

    for (payload,) in rows:
        if not payload or not isinstance(payload, dict):
            continue
        ctx = payload.get("csa_context")
        if not isinstance(ctx, dict):
            continue
        raw_c = ctx.get("contents_summary")
        raw_cd = ctx.get("cadence_or_delivery_note")
        sc = _sanitize_public_text(raw_c if isinstance(raw_c, str) else None)
        sd = _sanitize_public_text(raw_cd if isinstance(raw_cd, str) else None)
        if sc:
            contents_candidates.append(sc)
        if sd:
            cadence_candidates.append(sd)
        ci = ctx.get("context_incomplete")
        if ci is True:
            incomplete_any = True

    if not contents_candidates and not cadence_candidates and not incomplete_any:
        return None

    best_c = max(contents_candidates, key=len) if contents_candidates else None
    best_d = max(cadence_candidates, key=len) if cadence_candidates else None

    out: dict[str, Any] = {
        "contents_summary_generalized": best_c,
        "cadence_note": best_d,
        "context_incomplete": incomplete_any or (not best_c and not best_d),
    }
    return out


def build_details_object(
    session: Session,
    *,
    product: Product,
    market_scope: str,
    sales_channel: str,
    distinct_sources: int,
    display_buckets: set[str | None],
    report_date: date,
    rolling_window_start: date,
    rolling_window_end: date,
) -> dict[str, Any]:
    """Full ``details`` object for one published product row."""
    variant = resolve_details_variant(
        category=product.category,
        is_basket_product=bool(product.is_basket_product),
        market_scope=market_scope,
        display_buckets=display_buckets,
    )
    weekly = variant == "basket_csa"
    price_series = compute_price_series(
        session,
        product_id=int(product.id),
        market_scope=market_scope,
        sales_channel=sales_channel,
        report_date=report_date,
        weekly=weekly,
    )

    csa_block: dict[str, Any] | None = None
    if variant == "basket_csa":
        csa_block = merge_csa_details_for_bucket(
            session,
            product_id=int(product.id),
            market_scope=market_scope,
            sales_channel=sales_channel,
            d_start=rolling_window_start,
            d_end=rolling_window_end,
        )

    store_block: dict[str, Any] | None = None
    if variant == "store_retail":
        store_block = {
            "organic_catalog_note": "מחירים מקטלוג מוצרים אורגניים בחנות, לפי תצוגת האתר.",
        }

    benchmark_block: dict[str, Any] | None = None
    if variant == "chain_benchmark":
        benchmark_block = {
            "disclaimer": "נתוני השוואה — לא מחירי קהילה ישירים.",
        }

    details: dict[str, Any] = {
        "details_variant": variant,
        "source_count": int(distinct_sources),
        "price_series": price_series,
        "csa": csa_block,
        "store": store_block,
        "benchmark": benchmark_block,
    }
    return details
