"""AggregatorEngine — normalized_observations → daily_aggregates + weekly_snapshots."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from organic_market_agent.models.aggregates import DailyAggregate, WeeklySnapshot
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

_AGG_SQL = """
SELECT
    no.product_id,
    no.market_scope,
    no.sales_channel,
    BOOL_OR(no.is_basket_product) AS is_basket_agg,
    COUNT(*)::int AS sample_size,
    COUNT(DISTINCT no.source_id)::int AS distinct_sources,
    MIN(COALESCE(no.normalized_price_value, no.price_amount)) AS min_price,
    MAX(COALESCE(no.normalized_price_value, no.price_amount)) AS max_price,
    AVG(COALESCE(no.normalized_price_value, no.price_amount)) AS avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY COALESCE(no.normalized_price_value, no.price_amount)
    ) AS median_price,
    STDDEV_SAMP(COALESCE(no.normalized_price_value, no.price_amount)) AS stddev_price,
    MAX(COALESCE(no.normalized_unit_id, no.display_unit_id)) AS norm_unit_id,
    MAX(no.observed_at) AS last_observed_at
FROM normalized_observations no
LEFT JOIN raw_extracted_items rei ON rei.id = no.raw_extracted_item_id
WHERE (no.observed_at AT TIME ZONE 'UTC')::date = :agg_date
  AND no.market_scope IN ('community', 'benchmark')
  AND no.flag_status = 'ok'
  AND (rei.id IS NULL OR rei.is_quarantined IS NOT TRUE)
GROUP BY no.product_id, no.market_scope, no.sales_channel
"""


def _week_bounds(d: date) -> tuple[date, date]:
    """ISO week Monday–Sunday in local date (UTC calendar)."""
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end


class AggregatorEngine:
    """Roll normalized observations into daily_aggregates and weekly_snapshots."""

    def run(self, session: Session, aggregate_date: date) -> dict[str, int]:
        """Compute daily_aggregates for aggregate_date; roll up weekly_snapshots.

        Returns {"created": N, "updated": N} for daily rows touched.
        """
        existing = session.execute(
            sa.select(
                DailyAggregate.product_id,
                DailyAggregate.market_scope,
                DailyAggregate.sales_channel,
            ).where(DailyAggregate.aggregate_date == aggregate_date)
        ).all()
        existing_keys = {(r[0], r[1], r[2]) for r in existing}

        rows = session.execute(text(_AGG_SQL), {"agg_date": aggregate_date}).mappings().all()
        created = 0
        updated = 0

        for row in rows:
            sample_size = int(row["sample_size"])
            distinct_sources = int(row["distinct_sources"])
            meets = sample_size >= 2 and distinct_sources >= 2
            key = (row["product_id"], row["market_scope"], row["sales_channel"])
            if key in existing_keys:
                updated += 1
            else:
                created += 1

            avg_p = row["avg_price"]
            if avg_p is not None:
                avg_p = Decimal(str(avg_p)).quantize(Decimal("0.0001"))
            min_p = row["min_price"]
            if min_p is not None:
                min_p = Decimal(str(min_p)).quantize(Decimal("0.0001"))
            max_p = row["max_price"]
            if max_p is not None:
                max_p = Decimal(str(max_p)).quantize(Decimal("0.0001"))
            med_p = row["median_price"]
            if med_p is not None:
                med_p = Decimal(str(med_p)).quantize(Decimal("0.0001"))
            std_p = row["stddev_price"]
            if std_p is not None:
                std_p = Decimal(str(std_p)).quantize(Decimal("0.0001"))

            values: dict[str, Any] = {
                "aggregate_date": aggregate_date,
                "product_id": row["product_id"],
                "market_scope": row["market_scope"],
                "sales_channel": row["sales_channel"],
                "is_basket_aggregate": bool(row["is_basket_agg"]),
                "sample_size": sample_size,
                "distinct_sources": distinct_sources,
                "min_price": min_p,
                "max_price": max_p,
                "unweighted_avg_price": avg_p,
                "weighted_avg_price": avg_p,
                "median_price": med_p,
                "stddev_price": std_p if sample_size > 1 else None,
                "normalized_unit_id": row["norm_unit_id"],
                "meets_publish_threshold": meets,
                "last_observed_at": row["last_observed_at"],
            }

            tbl = DailyAggregate.__table__
            ins = pg_insert(tbl).values(**values)
            stmt = ins.on_conflict_do_update(
                constraint="uq_daily_aggregate",
                set_={
                    "is_basket_aggregate": ins.excluded.is_basket_aggregate,
                    "sample_size": ins.excluded.sample_size,
                    "distinct_sources": ins.excluded.distinct_sources,
                    "min_price": ins.excluded.min_price,
                    "max_price": ins.excluded.max_price,
                    "unweighted_avg_price": ins.excluded.unweighted_avg_price,
                    "weighted_avg_price": ins.excluded.weighted_avg_price,
                    "median_price": ins.excluded.median_price,
                    "stddev_price": ins.excluded.stddev_price,
                    "normalized_unit_id": ins.excluded.normalized_unit_id,
                    "meets_publish_threshold": ins.excluded.meets_publish_threshold,
                    "last_observed_at": ins.excluded.last_observed_at,
                },
            )
            session.execute(stmt)

        session.flush()
        self._rollup_week(session, aggregate_date)
        session.commit()
        logger.info(
            "AggregatorEngine: date=%s daily_groups=%d created=%d updated=%d",
            aggregate_date,
            len(rows),
            created,
            updated,
        )
        return {"created": created, "updated": updated}

    def _rollup_week(self, session: Session, aggregate_date: date) -> None:
        week_start, week_end = _week_bounds(aggregate_date)
        dailies = session.execute(
            sa.select(DailyAggregate).where(
                DailyAggregate.aggregate_date >= week_start,
                DailyAggregate.aggregate_date <= week_end,
            )
        ).scalars().all()

        by_key: dict[tuple[int, str, str | None], list[DailyAggregate]] = {}
        for d in dailies:
            key = (d.product_id, d.market_scope, d.sales_channel)
            by_key.setdefault(key, []).append(d)

        for (product_id, market_scope, sales_channel), group in by_key.items():
            total_n = sum(d.sample_size for d in group)
            if total_n == 0:
                continue
            w_sum = sum(
                (d.unweighted_avg_price or Decimal("0")) * d.sample_size for d in group
            )
            week_avg = (w_sum / total_n).quantize(Decimal("0.0001")) if total_n else None
            week_min = None
            week_max = None
            for d in group:
                if d.min_price is not None:
                    week_min = d.min_price if week_min is None else min(week_min, d.min_price)
                if d.max_price is not None:
                    week_max = d.max_price if week_max is None else max(week_max, d.max_price)
            med_list: list[Decimal] = []
            for d in group:
                if d.median_price is not None and d.sample_size:
                    med_list.extend([d.median_price] * d.sample_size)
            med_list.sort()
            week_median = None
            if med_list:
                mid = len(med_list) // 2
                week_median = (
                    med_list[mid]
                    if len(med_list) % 2
                    else ((med_list[mid - 1] + med_list[mid]) / 2).quantize(Decimal("0.0001"))
                )
            distinct_sources = max(d.distinct_sources for d in group)
            norm_ids = [d.normalized_unit_id for d in group if d.normalized_unit_id is not None]
            norm_u = max(norm_ids) if norm_ids else None

            values_ws: dict[str, Any] = {
                "week_start_date": week_start,
                "week_end_date": week_end,
                "product_id": product_id,
                "market_scope": market_scope,
                "sales_channel": sales_channel,
                "sample_size": total_n,
                "distinct_sources": distinct_sources,
                "data_completeness_pct": None,
                "week_avg_price": week_avg,
                "week_weighted_avg_price": week_avg,
                "week_median_price": week_median,
                "week_stddev_price": None,
                "week_min_price": week_min,
                "week_max_price": week_max,
                "normalized_unit_id": norm_u,
            }

            wtbl = WeeklySnapshot.__table__
            wins = pg_insert(wtbl).values(**values_ws)
            wstmt = wins.on_conflict_do_update(
                constraint="uq_weekly_snapshot",
                set_={
                    "sample_size": wins.excluded.sample_size,
                    "distinct_sources": wins.excluded.distinct_sources,
                    "week_avg_price": wins.excluded.week_avg_price,
                    "week_weighted_avg_price": wins.excluded.week_weighted_avg_price,
                    "week_median_price": wins.excluded.week_median_price,
                    "week_min_price": wins.excluded.week_min_price,
                    "week_max_price": wins.excluded.week_max_price,
                    "normalized_unit_id": wins.excluded.normalized_unit_id,
                },
            )
            session.execute(wstmt)
