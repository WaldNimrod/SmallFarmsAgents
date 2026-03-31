"""Rolling 7-day UTC community index for public publish (latest quote per source per bucket)."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from organic_market_agent.aggregator.price_rules import price_rules_allow_publish
from organic_market_agent.models import MeasurementUnit, Product

INDEX_WINDOW_DAYS = 7

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
        COALESCE(no.normalized_unit_id, no.display_unit_id) AS norm_unit_id
    FROM normalized_observations no
    LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
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


def build_rolling_publish_products(session: Session, report_date: date) -> list[dict[str, Any]]:
    """Rows for public_report products[] after 7d window, latest-per-source, and price rules."""
    d_start, d_end = rolling_window_bounds(report_date)
    raw_rows = session.execute(
        _LATEST_PER_SOURCE_SQL, {"d_start": d_start, "d_end": d_end}
    ).all()

    # (product_id, market_scope, sales_channel) -> list of (source_id, price, observed_at, norm_unit_id)
    buckets: dict[tuple[int, str, str | None], list[tuple[int, Decimal, datetime, int | None]]] = (
        defaultdict(list)
    )
    for r in raw_rows:
        pid, ms, sc, sid, price, obs_at, nu = (
            int(r[0]),
            r[1],
            r[2],
            int(r[3]),
            Decimal(str(r[4])),
            r[5],
            int(r[6]) if r[6] is not None else None,
        )
        buckets[(pid, ms, sc)].append((sid, price, obs_at, nu))

    products_out: list[dict[str, Any]] = []
    for (pid, ms, sc), rows in buckets.items():
        per_source: dict[int, Decimal] = {t[0]: t[1] for t in rows}
        if len(per_source) < 2:
            continue
        price_ok, _sup = price_rules_allow_publish(per_source)
        if not price_ok:
            continue

        prices = list(per_source.values())
        obs_times = [t[2] for t in rows]
        last_obs = max(obs_times)
        norm_ids = [t[3] for t in rows if t[3] is not None]
        norm_u = max(norm_ids) if norm_ids else None

        mn, mx = min(prices), max(prices)
        avg_p = (sum(prices) / len(prices)).quantize(Decimal("0.0001"))
        med_p = _median_dec(prices)
        std_p = _stddev_sample(prices)

        prod = session.get(Product, pid)
        if prod is None or not prod.is_active:
            continue
        mu = session.get(MeasurementUnit, norm_u) if norm_u is not None else None
        unit_label = mu.name_he if mu else ""

        products_out.append(
            {
                "product_id": prod.code,
                "canonical_name_he": prod.canonical_name_he,
                "market_scope": ms,
                "meets_publish_threshold": True,
                "sample_size": len(per_source),
                "distinct_sources": len(per_source),
                "min_price": float(mn),
                "max_price": float(mx),
                "avg_price": float(avg_p),
                "median_price": float(med_p) if med_p is not None else None,
                "stddev_price": float(std_p) if std_p is not None else None,
                "normalized_unit": unit_label,
                "last_observed_at": last_obs.isoformat() if last_obs else None,
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
