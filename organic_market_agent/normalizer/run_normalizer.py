"""Standalone normalizer CLI: `python -m organic_market_agent.normalizer.run_normalizer`."""
from __future__ import annotations

import click
from sqlalchemy.orm import Session

from organic_market_agent.db.session import SessionFactory
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.utils.config import config


def _print_cycle_metrics(session: Session, ingestion_run_id: int | None) -> None:
    """Print forward-metrics summary for the given run_id (or all pending runs)."""
    from sqlalchemy import text

    run_filter = "sfr.ingestion_run_id = :run_id" if ingestion_run_id else "1=1"
    params: dict = {}
    if ingestion_run_id:
        params["run_id"] = ingestion_run_id

    # Detect whether migration 013 has been applied (source_tier column exists)
    has_tier: bool = (
        session.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_name='sources' AND column_name='source_tier'"
            )
        ).scalar()
        > 0
    )

    tier_filter = "s.source_tier = 'price_grid'" if has_tier else "s.source_group = 'direct_price'"
    quarantine_clause = "AND r.is_quarantined = false" if has_tier else ""

    sql = text(f"""
        SELECT
            COUNT(*) FILTER (WHERE r.extraction_status = 'normalized') AS resolved,
            COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable') AS unresolvable,
            COUNT(*) AS total,
            COUNT(DISTINCT no_obs.product_id) AS distinct_products,
            COUNT(DISTINCT sfr.source_id) FILTER (
                WHERE r.extraction_status = 'normalized'
                  AND s.market_scope = 'community'
            ) AS community_sources_ok,
            COUNT(DISTINCT sfr.source_id) FILTER (
                WHERE s.market_scope = 'community'
            ) AS community_sources_total
        FROM raw_extracted_items r
        JOIN source_fetch_runs sfr ON r.source_fetch_run_id = sfr.id
        JOIN sources s ON sfr.source_id = s.id
        LEFT JOIN normalized_observations no_obs
               ON no_obs.source_fetch_run_id = sfr.id
        WHERE {run_filter}
          AND {tier_filter}
          {quarantine_clause}
    """)

    row = session.execute(sql, params).mappings().one()
    resolved = row["resolved"] or 0
    unresolvable = row["unresolvable"] or 0
    total = row["total"] or 0
    distinct = row["distinct_products"] or 0
    comm_ok = row["community_sources_ok"] or 0
    comm_total = row["community_sources_total"] or 0

    rate = round(100.0 * unresolvable / total, 1) if total > 0 else 0.0

    def _ok(cond: bool) -> str:
        return "✅" if cond else "❌"

    run_label = f"run_id={ingestion_run_id}" if ingestion_run_id else "all runs"
    tier_label = "price_grid, non-quarantined" if has_tier else "direct_price proxy"
    click.echo(f"\n=== Cycle Metrics ({run_label}) ===")
    click.echo(f"resolved           : {resolved}")
    click.echo(f"unresolvable       : {unresolvable}")
    click.echo(f"unresolvable_rate  : {rate}% ({tier_label})")
    click.echo(f"distinct_products  : {distinct}")
    click.echo(f"community_sources  : {comm_ok} / {comm_total} succeeded")
    click.echo(
        f"thresholds         : "
        f"resolved {_ok(resolved >= 10)}  "
        f"distinct_products {_ok(distinct >= 3)}  "
        f"unresolvable_rate {_ok(rate <= 30.0)}  "
        f"community_sources {_ok(comm_ok >= 2)}"
    )


def run_normalizer_cli(
    source_id: int | None = None,
    ingestion_run_id: int | None = None,
    metrics: bool = False,
) -> dict[str, int]:
    """Run normalizer; return counts dict."""
    config.ensure_dirs()
    with SessionFactory() as session:
        engine = NormalizerEngine()
        counts = engine.run(
            session,
            ingestion_run_id=ingestion_run_id,
            source_id=source_id,
        )
        if metrics:
            _print_cycle_metrics(session, ingestion_run_id)
        return counts


@click.command()
@click.option("--source-id", default=None, type=int, help="Limit to one source (sources.id)")
@click.option(
    "--ingestion-run-id",
    default=None,
    type=int,
    help="Limit to raw items from this ingestion run",
)
@click.option(
    "--metrics",
    is_flag=True,
    default=False,
    help="Print forward-metrics summary after run (resolved, distinct_products, unresolvable_rate)",
)
def main(source_id: int | None, ingestion_run_id: int | None, metrics: bool) -> None:
    """Normalize all pending raw_extracted_items (extraction_status='extracted')."""
    counts = run_normalizer_cli(
        source_id=source_id,
        ingestion_run_id=ingestion_run_id,
        metrics=metrics,
    )
    click.echo(
        f"NormalizerEngine: resolved={counts['resolved']} "
        f"unresolvable={counts['unresolvable']} "
        f"scope_skipped={counts.get('scope_skipped', 0)} skipped={counts['skipped']}"
    )


if __name__ == "__main__":
    main()
