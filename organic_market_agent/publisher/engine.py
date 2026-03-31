"""PublishEngine — local public_report.json, public_report.html, manifest.json."""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from jinja2 import Environment, PackageLoader, select_autoescape
from sqlalchemy.orm import Session

from organic_market_agent.models import DailyAggregate
from organic_market_agent.utils.data_quality_snapshot import compute_raw_pipeline_counts
from organic_market_agent.utils.exceptions import PublishAbortError
from organic_market_agent.utils.logging_setup import get_logger

from .rolling_aggregate import (
    INDEX_WINDOW_DAYS,
    build_rolling_publish_products,
    count_distinct_community_sources_in_window,
    max_last_observed_from_products,
    rolling_window_bounds,
)

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
    """Write local publish artifacts from a rolling 7-day community index (latest per source)."""

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

        d_start, d_end = rolling_window_bounds(report_date)
        comm_src = count_distinct_community_sources_in_window(session, report_date)
        if comm_src < 2:
            raise PublishAbortError(
                f"Publish requires at least 2 distinct community sources in the "
                f"{INDEX_WINDOW_DAYS}d UTC window ending {report_date}; "
                f"window=[{d_start}..{d_end}]; got {comm_src}"
            )

        products_out = build_rolling_publish_products(session, report_date)
        max_observed = max_last_observed_from_products(products_out)
        data_quality = compute_raw_pipeline_counts(session)

        report_payload = {
            "generated_at": gen.isoformat(),
            "report_date": report_date.isoformat(),
            "index": {
                "mode": "rolling_7d",
                "window_days": INDEX_WINDOW_DAYS,
                "window_start": d_start.isoformat(),
                "window_end": d_end.isoformat(),
            },
            "data_quality": data_quality,
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
            data_quality=data_quality,
        )
        (output_dir / "public_report.html").write_text(html, encoding="utf-8")

        manifest = {
            "last_published_at": gen.isoformat(),
            "report_date": report_date.isoformat(),
            "product_count": len(products_out),
            "staleness_level": _staleness_level(gen, ref),
            "community_sources": int(comm_src),
            "index_window_days": INDEX_WINDOW_DAYS,
            "window_start_date": d_start.isoformat(),
            "window_end_date": d_end.isoformat(),
            "distinct_community_sources_in_window": int(comm_src),
            "data_quality": data_quality,
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info(
            "PublishEngine: wrote %d products to %s (rolling %dd window)",
            len(products_out),
            output_dir,
            INDEX_WINDOW_DAYS,
        )
        return {
            "report_date": report_date.isoformat(),
            "product_count": len(products_out),
            "community_sources": int(comm_src),
            "staleness_level": manifest["staleness_level"],
            "output_dir": str(output_dir.resolve()),
        }
