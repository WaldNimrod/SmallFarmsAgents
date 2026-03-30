"""QAEngine — log-only quality checks for normalized observations (M4)."""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, timezone
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Session

from organic_market_agent.models import IngestionRun, NormalizedObservation, Source, SourceFetchRun
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)


class QAEngine:
    """Return QA warning strings for an ingestion run (no DB writes)."""

    def run(self, session: Session, run_id: int) -> list[str]:
        warnings: list[str] = []
        run = session.get(IngestionRun, run_id)
        if not run:
            return [f"QA: ingestion_run id={run_id} not found"]

        warnings.extend(self._qa003_duplicates(session, run_id))
        warnings.extend(self._qa001_outliers(session, run_id))
        warnings.extend(self._qa002_missing_sources(session, run_id))

        for w in warnings:
            logger.warning("%s", w)
        return warnings

    def _qa003_duplicates(self, session: Session, run_id: int) -> list[str]:
        """Duplicate (source_id, product_id, observed day) in this run."""
        sql = """
        SELECT no.source_id, no.product_id, (no.observed_at AT TIME ZONE 'UTC')::date AS d, COUNT(*) AS cnt
        FROM normalized_observations no
        JOIN source_fetch_runs sfr ON sfr.id = no.source_fetch_run_id
        WHERE sfr.ingestion_run_id = :rid
        GROUP BY no.source_id, no.product_id, (no.observed_at AT TIME ZONE 'UTC')::date
        HAVING COUNT(*) > 1
        """
        rows = session.execute(sa.text(sql), {"rid": run_id}).all()
        out: list[str] = []
        for source_id, product_id, _d, cnt in rows:
            out.append(
                f"QA003: duplicate observations source_id={source_id} product_id={product_id} count={cnt}"
            )
        return out

    def _qa001_outliers(self, session: Session, run_id: int) -> list[str]:
        """Price > mean + 3*sample_stddev per (product_id, day) within this run."""
        obs = session.execute(
            sa.select(
                NormalizedObservation.id,
                NormalizedObservation.product_id,
                NormalizedObservation.source_id,
                NormalizedObservation.observed_at,
                NormalizedObservation.price_amount,
                NormalizedObservation.normalized_price_value,
            )
            .join(SourceFetchRun, SourceFetchRun.id == NormalizedObservation.source_fetch_run_id)
            .where(SourceFetchRun.ingestion_run_id == run_id)
        ).all()

        by_day_product: dict[tuple[int, date], list[tuple[int, int, Decimal]]] = defaultdict(list)
        for oid, pid, sid, obs_at, price_amt, norm_val in obs:
            price = norm_val if norm_val is not None else price_amt
            if obs_at is None:
                continue
            if hasattr(obs_at, "astimezone"):
                day = obs_at.astimezone(timezone.utc).date()
            else:
                day = obs_at
            by_day_product[(pid, day)].append((oid, sid, Decimal(str(price))))

        out: list[str] = []
        for (pid, _day), points in by_day_product.items():
            if len(points) < 2:
                continue
            prices = [p[2] for p in points]
            n = len(prices)
            mean = sum(prices) / n
            variance = sum((x - mean) ** 2 for x in prices) / (n - 1)
            std = Decimal(str(math.sqrt(float(variance)))) if variance > 0 else Decimal("0")
            if std == 0:
                continue
            for oid, sid, price in points:
                if price > mean + 3 * std:
                    out.append(
                        f"QA001: outlier observation id={oid} source_id={sid} product_id={pid} "
                        f"price={price} mean={mean:.4f} threshold={mean + 3 * std:.4f}"
                    )
        return out

    def _qa002_missing_sources(self, session: Session, run_id: int) -> list[str]:
        """Sources that succeeded in previous run but not in current run."""
        current = session.execute(
            sa.select(SourceFetchRun.source_id)
            .where(SourceFetchRun.ingestion_run_id == run_id)
            .where(SourceFetchRun.status == "success")
        ).scalars().all()
        current_set = set(current)

        prev_id = session.execute(
            sa.select(IngestionRun.id)
            .where(IngestionRun.id < run_id)
            .order_by(IngestionRun.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if prev_id is None:
            return []

        prev_sources = session.execute(
            sa.select(SourceFetchRun.source_id)
            .where(SourceFetchRun.ingestion_run_id == prev_id)
            .where(SourceFetchRun.status == "success")
        ).scalars().all()
        prev_set = set(prev_sources)

        missing = prev_set - current_set
        out: list[str] = []
        for sid in missing:
            src = session.get(Source, sid)
            code = src.code if src else str(sid)
            out.append(
                f"QA002: source {code} (id={sid}) succeeded in run {prev_id} but missing from run {run_id}"
            )
        return out
