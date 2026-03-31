"""PublishEngine — local public_report.json, public_report.html, manifest.json."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from jinja2 import Environment, PackageLoader, select_autoescape
from sqlalchemy.orm import Session

from organic_market_agent.models import DailyAggregate, MeasurementUnit, Product
from organic_market_agent.models.observations import NormalizedObservation
from organic_market_agent.utils.exceptions import PublishAbortError
from organic_market_agent.utils.logging_setup import get_logger

logger = get_logger(__name__)

def _staleness_level(generated_at: datetime, reference_now: datetime) -> str:
    """Mandate: current <=3d, warning 4–7d, irrelevant >7d (8-day legacy wording)."""
    age = (reference_now.date() - generated_at.date()).days
    if age <= 3:
        return "current"
    if age <= 7:
        return "warning"
    return "irrelevant"


class PublishEngine:
    """Write local publish artifacts from daily_aggregates (community, threshold met)."""

    def run(
        self,
        session: Session,
        output_dir: Path,
        report_date: date | None = None,
        generated_at: datetime | None = None,
        reference_now: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate public_report.json, public_report.html, manifest.json in output_dir.

        generated_at: timestamp written into artifacts (default UTC now).
        reference_now: clock for staleness in manifest (default UTC now); override in tests.

        Returns a small summary dict for pipeline logging.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        gen = generated_at or datetime.now(timezone.utc)
        if gen.tzinfo is None:
            gen = gen.replace(tzinfo=timezone.utc)
        ref = reference_now or gen
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)

        if report_date is None:
            report_date = session.execute(
                sa.select(sa.func.max(DailyAggregate.aggregate_date))
            ).scalar_one_or_none() or gen.date()

        comm_src = session.execute(
            sa.select(sa.func.count(sa.distinct(NormalizedObservation.source_id))).where(
                sa.func.date(sa.func.timezone("UTC", NormalizedObservation.observed_at))
                == report_date,
                NormalizedObservation.market_scope == "community",
                NormalizedObservation.flag_status == "ok",
            )
        ).scalar_one()
        if comm_src < 2:
            raise PublishAbortError(
                f"Publish requires at least 2 community sources for report_date={report_date}; got {comm_src}"
            )

        rows = session.execute(
            sa.select(DailyAggregate, Product, MeasurementUnit)
            .join(Product, Product.id == DailyAggregate.product_id)
            .outerjoin(MeasurementUnit, MeasurementUnit.id == DailyAggregate.normalized_unit_id)
            .where(
                DailyAggregate.aggregate_date == report_date,
                DailyAggregate.market_scope == "community",
                DailyAggregate.meets_publish_threshold.is_(True),
            )
        ).all()

        products_out: list[dict[str, Any]] = []
        max_observed: datetime | None = None
        for da, prod, mu in rows:
            if da.last_observed_at:
                max_observed = (
                    max(max_observed, da.last_observed_at)
                    if max_observed
                    else da.last_observed_at
                )
            unit_label = mu.name_he if mu else ""
            products_out.append(
                {
                    "product_id": prod.code,
                    "canonical_name_he": prod.canonical_name_he,
                    "market_scope": da.market_scope,
                    "meets_publish_threshold": True,
                    "sample_size": da.sample_size,
                    "distinct_sources": da.distinct_sources,
                    "min_price": float(da.min_price) if da.min_price is not None else None,
                    "max_price": float(da.max_price) if da.max_price is not None else None,
                    "avg_price": float(da.unweighted_avg_price)
                    if da.unweighted_avg_price is not None
                    else None,
                    "median_price": float(da.median_price) if da.median_price is not None else None,
                    "stddev_price": float(da.stddev_price) if da.stddev_price is not None else None,
                    "normalized_unit": unit_label,
                    "last_observed_at": da.last_observed_at.isoformat()
                    if da.last_observed_at
                    else None,
                }
            )

        report_payload = {
            "generated_at": gen.isoformat(),
            "report_date": report_date.isoformat(),
            "products": products_out,
        }
        (output_dir / "public_report.json").write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        stale_banner = False
        if max_observed:
            days_old = (ref.date() - max_observed.date()).days
            stale_banner = days_old > 3

        env = Environment(
            loader=PackageLoader("organic_market_agent.publisher", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        tpl = env.get_template("public_report.html")
        html = tpl.render(
            report_date=report_date.isoformat(),
            generated_at=gen.isoformat(),
            products=products_out,
            stale_banner=stale_banner,
        )
        (output_dir / "public_report.html").write_text(html, encoding="utf-8")

        manifest = {
            "last_published_at": gen.isoformat(),
            "report_date": report_date.isoformat(),
            "product_count": len(products_out),
            "staleness_level": _staleness_level(gen, ref),
            "community_sources": int(comm_src),
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(
            "PublishEngine: wrote %d products to %s",
            len(products_out),
            output_dir,
        )
        return {
            "report_date": report_date.isoformat(),
            "product_count": len(products_out),
            "community_sources": int(comm_src),
            "staleness_level": manifest["staleness_level"],
            "output_dir": str(output_dir.resolve()),
        }
