"""Rolling 7-day UTC community index for public publish (latest quote per source per bucket)."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Callable

from sqlalchemy import text
from sqlalchemy.orm import Session

from organic_market_agent.aggregator.price_rules import price_rules_allow_publish
from organic_market_agent.models import MeasurementUnit, Product
from organic_market_agent.publisher.report_details import build_details_object

INDEX_WINDOW_DAYS = 7

# Latest row per (product, source, sales_channel) in window — used to build per-segment views.
_LATEST_PER_SOURCE_SQL = text(
    """
    SELECT DISTINCT ON (
        no.product_id, no.market_scope, no.sales_channel, no.source_id
    )
        no.product_id,
        no.market_scope,
        no.sales_channel,
        no.source_id,
        COALESCE(no.normalized_price_value, no.price_amount) AS price,
        no.observed_at,
        COALESCE(no.normalized_unit_id, no.display_unit_id) AS norm_unit_id,
        s.display_bucket
    FROM normalized_observations no
    LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
    JOIN sources s ON s.id = no.source_id
    WHERE (no.observed_at AT TIME ZONE 'UTC')::date BETWEEN :d_start AND :d_end
      AND no.market_scope = 'community'
      AND no.flag_status = 'ok'
      AND (rei.id IS NULL OR rei.is_quarantined IS NOT TRUE)
    ORDER BY
        no.product_id,
        no.market_scope,
        no.sales_channel,
        no.source_id,
        no.observed_at DESC,
        no.id ASC
    """
)

_COUNT_SOURCES_WINDOW_SQL = text(
    """
    SELECT COUNT(DISTINCT no.source_id)
    FROM normalized_observations no
    LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
    WHERE (no.observed_at AT TIME ZONE 'UTC')::date BETWEEN :d_start AND :d_end
      AND no.market_scope = 'community'
      AND no.flag_status = 'ok'
      AND (rei.id IS NULL OR rei.is_quarantined IS NOT TRUE)
    """
)

# Row tuple: product_id, market_scope, sales_channel, source_id, price, observed_at, norm_unit_id, display_bucket
Row = tuple[Any, ...]


def rolling_window_bounds(report_date: date) -> tuple[date, date]:
    """Inclusive UTC calendar window of INDEX_WINDOW_DAYS ending on report_date."""
    d_end = report_date
    d_start = report_date - timedelta(days=INDEX_WINDOW_DAYS - 1)
    return d_start, d_end


def count_distinct_community_sources_in_window(session: Session, report_date: date) -> int:
    d_start, d_end = rolling_window_bounds(report_date)
    n = session.execute(
        _COUNT_SOURCES_WINDOW_SQL, {"d_start": d_start, "d_end": d_end}
    ).scalar_one()
    return int(n or 0)


def _median_dec(vals: list[Decimal]) -> Decimal | None:
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return ((s[mid - 1] + s[mid]) / 2).quantize(Decimal("0.0001"))


def _stddev_sample(vals: list[Decimal]) -> Decimal | None:
    n = len(vals)
    if n < 2:
        return None
    mean = sum(vals) / n
    var = sum((x - mean) ** 2 for x in vals) / Decimal(n - 1)
    if var <= 0:
        return None
    return Decimal(str(math.sqrt(float(var)))).quantize(Decimal("0.0001"))


def _collapse_latest_per_source(rows: list[Row], predicate: Callable[[Row], bool] | None = None) -> list[Row]:
    """Keep one row per source_id (latest observed_at). Optional predicate on full row tuple."""
    filtered = rows if predicate is None else [r for r in rows if predicate(r)]
    best: dict[int, Row] = {}
    for t in filtered:
        sid = int(t[3])
        cur = best.get(sid)
        if cur is None or t[5] > cur[5]:
            best[sid] = t
    return list(best.values())


def _stats_from_collapsed(
    session: Session,
    prod: Product,
    collapsed: list[Row],
    report_date: date,
) -> dict[str, Any] | None:
    """Price block for publish JSON, or None if below threshold / price rules fail."""
    if len(collapsed) < 2:
        return None
    per_source: dict[int, Decimal] = {int(t[3]): t[4] for t in collapsed}
    price_ok, _sup = price_rules_allow_publish(per_source)
    if not price_ok:
        return None

    prices = list(per_source.values())
    obs_times = [t[5] for t in collapsed]
    last_obs = max(obs_times)
    norm_ids = [int(t[6]) for t in collapsed if t[6] is not None]
    norm_u = max(norm_ids) if norm_ids else None
    mu = session.get(MeasurementUnit, norm_u) if norm_u is not None else None
    unit_label = mu.name_he if mu else ""

    mn, mx = min(prices), max(prices)
    avg_p = (sum(prices) / len(prices)).quantize(Decimal("0.0001"))
    med_p = _median_dec(prices)
    std_p = _stddev_sample(prices)

    return {
        "min_price": float(mn),
        "max_price": float(mx),
        "avg_price": float(avg_p),
        "median_price": float(med_p) if med_p is not None else None,
        "stddev_price": float(std_p) if std_p is not None else None,
        "sample_size": len(per_source),
        "distinct_sources": len(per_source),
        "normalized_unit": unit_label,
        "last_observed_at": last_obs.isoformat() if last_obs else None,
    }


def _dominant_sales_channel(collapsed: list[Row]) -> str:
    counts = Counter(str(t[2]) for t in collapsed if t[2] is not None)
    if not counts:
        return "community_direct"
    return counts.most_common(1)[0][0]


def build_rolling_publish_products(session: Session, report_date: date) -> list[dict[str, Any]]:
    """One row per catalog product (community): combined stats + per–filter-key stats.

    * ``all`` — latest observation per source across all sales_channel rows (one price per source).
    * ``grower`` / ``store`` / ``chain`` — same, but only sources whose ``display_bucket`` matches.
    * ``baskets`` — only for ``category == 'baskets'``; same as combined for that product.

    Top-level numeric fields mirror the **grower** slice when present, else ``stats_by_filter['all']``,
    matching the public UI default (grower-only filter; combined mode uses ``all`` in the client).
    """
    d_start, d_end = rolling_window_bounds(report_date)
    raw_rows = session.execute(
        _LATEST_PER_SOURCE_SQL, {"d_start": d_start, "d_end": d_end}
    ).all()

    by_product: dict[int, list[Row]] = defaultdict(list)
    for r in raw_rows:
        row: Row = (
            int(r[0]),
            r[1],
            r[2],
            int(r[3]),
            Decimal(str(r[4])),
            r[5],
            int(r[6]) if r[6] is not None else None,
            r[7],
        )
        by_product[int(r[0])].append(row)

    products_out: list[dict[str, Any]] = []
    for pid, rows in by_product.items():
        prod = session.get(Product, pid)
        if prod is None or not prod.is_active:
            continue

        collapsed_all = _collapse_latest_per_source(rows)
        stats_all = _stats_from_collapsed(session, prod, collapsed_all, report_date)
        if stats_all is None:
            continue

        def _pred_bucket(bucket: str) -> Callable[[Row], bool]:
            return lambda t: t[7] == bucket

        collapsed_grower = _collapse_latest_per_source(rows, predicate=_pred_bucket("grower"))
        collapsed_store = _collapse_latest_per_source(rows, predicate=_pred_bucket("store"))
        collapsed_chain = _collapse_latest_per_source(rows, predicate=_pred_bucket("chain"))

        stats_grower = _stats_from_collapsed(session, prod, collapsed_grower, report_date)
        stats_store = _stats_from_collapsed(session, prod, collapsed_store, report_date)
        stats_chain = _stats_from_collapsed(session, prod, collapsed_chain, report_date)

        if (prod.category or "") == "baskets":
            stats_baskets = dict(stats_all)
        else:
            stats_baskets = None

        stats_by_filter: dict[str, dict[str, Any] | None] = {
            "all": stats_all,
            "grower": stats_grower,
            "store": stats_store,
            "chain": stats_chain,
            "baskets": stats_baskets,
        }

        # Top-level numeric fields follow the public UI default: **grower-only** slice when present,
        # else fall back to combined ``all`` so SSR matches the default filter (no "הכל" pill).
        stats_default = stats_grower if stats_grower is not None else stats_all

        display_buckets = {t[7] for t in collapsed_all if t[7]}
        source_types = sorted(display_buckets)
        win_start, win_end = rolling_window_bounds(report_date)
        details = build_details_object(
            session,
            product=prod,
            market_scope="community",
            sales_channel=_dominant_sales_channel(collapsed_all),
            distinct_sources=stats_all["distinct_sources"],
            display_buckets=display_buckets,
            report_date=report_date,
            rolling_window_start=win_start,
            rolling_window_end=win_end,
        )

        products_out.append(
            {
                "product_id": prod.code,
                "canonical_name_he": prod.canonical_name_he,
                "category": prod.category if hasattr(prod, "category") else None,
                "market_scope": "community",
                "source_types": source_types,
                "meets_publish_threshold": True,
                "sample_size": stats_default["sample_size"],
                "distinct_sources": stats_default["distinct_sources"],
                "min_price": stats_default["min_price"],
                "max_price": stats_default["max_price"],
                "avg_price": stats_default["avg_price"],
                "median_price": stats_default["median_price"],
                "stddev_price": stats_default["stddev_price"],
                "normalized_unit": stats_default["normalized_unit"],
                "last_observed_at": stats_default["last_observed_at"],
                "stats_by_filter": stats_by_filter,
                "details": details,
            }
        )

    products_out.sort(key=lambda x: (x["canonical_name_he"], x["product_id"]))
    return products_out


def max_last_observed_from_products(products: list[dict[str, Any]]) -> datetime | None:
    """Latest observation timestamp across published product rows."""
    best: datetime | None = None
    for p in products:
        raw = p.get("last_observed_at")
        if not raw:
            continue
        try:
            ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if best is None or ts > best:
            best = ts
    return best
