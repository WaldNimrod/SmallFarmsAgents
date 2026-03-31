"""`python -m organic_market_agent <command>`."""
from __future__ import annotations

import json
from pathlib import Path

import click


@click.group()
def cli() -> None:
    """OrganicMarketAgent CLI entry."""
    pass


@cli.command("run_ingestion")
@click.option("--run-type", default="daily", type=click.Choice(["daily", "manual", "retry"]))
@click.option("--source-code", default=None, help="Run a single source by code")
@click.option(
    "--normalize",
    is_flag=True,
    default=False,
    help="Run M3 normalizer after ingestion for this ingestion run",
)
def run_ingestion_cmd(
    run_type: str,
    source_code: str | None,
    normalize: bool,
) -> None:
    """Run collectors + parsers (and optionally normalizer)."""
    from organic_market_agent.scheduler.run_ingestion import run_ingestion

    run_ingestion(
        run_type=run_type,
        source_code=source_code,
        normalize=normalize,
    )


@cli.command("catalog_renormalize")
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Only print how many unresolvable rows would be re-queued; no DB writes",
)
@click.option("--skip-normalize", is_flag=True, default=False, help="Only re-queue rows")
@click.option("--skip-aggregate", is_flag=True, default=False)
@click.option("--skip-publish", is_flag=True, default=False)
@click.option(
    "--aggregate-date",
    default=None,
    help="YYYY-MM-DD for AggregatorEngine (default: today UTC)",
)
@click.option(
    "--output-dir",
    default="output/public",
    show_default=True,
    help="Publish output directory",
)
def catalog_renormalize_cmd(
    dry_run: bool,
    skip_normalize: bool,
    skip_aggregate: bool,
    skip_publish: bool,
    aggregate_date: str | None,
    output_dir: str,
) -> None:
    """After new products/aliases: re-queue unresolvable raw rows, normalize, aggregate, publish.

    Resets non-quarantined `raw_extracted_items` from `unresolvable` to `extracted`, runs the
    normalizer on all pending rows, rolls up `daily_aggregates` for one day (default today UTC),
    then writes public artifacts. Does not reset already-normalized rows.
    """
    from datetime import date as date_cls

    from organic_market_agent.db.session import SessionFactory
    from organic_market_agent.maintenance.catalog_renormalize import (
        count_unresolvable_requeueable,
        run_catalog_renormalize,
    )

    if dry_run:
        with SessionFactory() as session:
            n = count_unresolvable_requeueable(session)
        click.echo(f"Would re-queue {n} raw_extracted_items (unresolvable → extracted).")
        return

    d = date_cls.fromisoformat(aggregate_date) if aggregate_date else None
    stats = run_catalog_renormalize(
        skip_normalize=skip_normalize,
        skip_aggregate=skip_aggregate,
        skip_publish=skip_publish,
        aggregate_date=d,
        output_dir=Path(output_dir),
    )
    click.echo(f"Re-queued unresolvable rows: {stats.unresolvable_requeued}")
    if not skip_normalize:
        click.echo(
            f"Normalizer: resolved={stats.normalizer_resolved} "
            f"unresolvable={stats.normalizer_unresolvable} "
            f"scope_skipped={stats.normalizer_scope_skipped} skipped={stats.normalizer_skipped}"
        )
    if not skip_aggregate:
        click.echo(
            f"Aggregator ({stats.aggregate_date}): "
            f"created={stats.aggregate_created} updated={stats.aggregate_updated}"
        )
    if not skip_publish:
        if stats.publish_ok:
            click.echo(f"PublishEngine: OK → {output_dir}")
        else:
            click.echo(f"PublishEngine: skipped or failed: {stats.publish_error}", err=True)
            raise SystemExit(1)


@cli.command("full_data_refresh")
@click.option(
    "--all-scopes",
    is_flag=True,
    default=False,
    help="Include non-community sources (default: community sources only).",
)
@click.option(
    "--aggregate-date",
    default=None,
    help="YYYY-MM-DD for AggregatorEngine / publish (default: today UTC).",
)
@click.option(
    "--output-dir",
    default="output/public",
    show_default=True,
    help="Publish output directory",
)
def full_data_refresh_cmd(all_scopes: bool, aggregate_date: str | None, output_dir: str) -> None:
    """Delete normalized_observations for community raw rows (normalized+unresolvable), re-normalize, aggregate, publish.

    Does not reset rows already in ignored (approved scope skips). Destructive: use after backup.
    """
    from datetime import date as date_cls

    from organic_market_agent.maintenance.full_data_refresh import run_full_data_refresh

    d = date_cls.fromisoformat(aggregate_date) if aggregate_date else None
    stats = run_full_data_refresh(
        community_only=not all_scopes,
        aggregate_date=d,
        output_dir=Path(output_dir),
    )
    click.echo(
        f"Targets: raw_items={stats.target_raw_item_count} "
        f"flags_deleted={stats.observation_flags_deleted} "
        f"obs_deleted={stats.normalized_observations_deleted} reset={stats.raw_items_reset_to_extracted}"
    )
    click.echo(
        f"Normalizer: resolved={stats.normalizer_resolved} "
        f"unresolvable={stats.normalizer_unresolvable} "
        f"scope_skipped={stats.normalizer_scope_skipped} skipped={stats.normalizer_skipped}"
    )
    click.echo(
        f"Aggregator ({stats.aggregate_date}): "
        f"created={stats.aggregate_created} updated={stats.aggregate_updated}"
    )
    if stats.publish_ok:
        click.echo(f"PublishEngine: OK → {output_dir}")
    else:
        click.echo(f"PublishEngine: failed: {stats.publish_error}", err=True)
        raise SystemExit(1)


@cli.command("run_normalizer")
@click.option("--source-id", default=None, type=int)
@click.option("--ingestion-run-id", default=None, type=int)
@click.option(
    "--metrics",
    is_flag=True,
    default=False,
    help="Print forward-metrics summary after run",
)
def run_normalizer_cmd(
    source_id: int | None,
    ingestion_run_id: int | None,
    metrics: bool,
) -> None:
    """Run M3 normalizer on pending raw_extracted_items."""
    from organic_market_agent.normalizer.run_normalizer import run_normalizer_cli

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


@cli.command("run_aggregator")
@click.option(
    "--date",
    "agg_date",
    default=None,
    help="Aggregate date (YYYY-MM-DD). Defaults to today.",
)
def run_aggregator_cmd(agg_date: str | None) -> None:
    """Roll normalized_observations into daily_aggregates and weekly_snapshots."""
    from datetime import date as _date

    from organic_market_agent.aggregator.engine import AggregatorEngine
    from organic_market_agent.db.session import SessionFactory

    d = _date.fromisoformat(agg_date) if agg_date else _date.today()
    with SessionFactory() as session:
        counts = AggregatorEngine().run(session, d)
    click.echo(
        f"AggregatorEngine: date={d} created={counts['created']} updated={counts['updated']}"
    )


@cli.command("run_publisher")
@click.option(
    "--output-dir",
    "output_dir",
    default="output/public",
    show_default=True,
    help="Directory to write public_report.json / .html and manifest.json",
)
def run_publisher_cmd(output_dir: str) -> None:
    """Generate publish artifacts (public_report.json, .html, manifest.json)."""
    from organic_market_agent.db.session import SessionFactory
    from organic_market_agent.publisher.engine import PublishEngine
    from organic_market_agent.utils.exceptions import PublishAbortError

    try:
        with SessionFactory() as session:
            PublishEngine().run(session, Path(output_dir))
        click.echo(f"PublishEngine: artifacts written to {output_dir}")
    except PublishAbortError as exc:
        click.echo(f"PublishEngine ABORTED: {exc}", err=True)
        raise SystemExit(1)


@cli.command("run_viewer")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, type=int, show_default=True)
@click.option(
    "--dir",
    "directory",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True, exists=True),
    required=True,
    help="Directory to serve (e.g. publish output).",
)
def run_viewer_cmd(host: str, port: int, directory: Path) -> None:
    """Serve a directory over HTTP (local static viewer)."""
    from organic_market_agent.publisher.viewer import serve_directory

    click.echo(f"Serving {directory.resolve()} at http://{host}:{port}/")
    serve_directory(host, port, directory)


@cli.command("prune_raw_pipeline")
@click.option(
    "--timezone",
    default="Asia/Jerusalem",
    show_default=True,
    help="IANA zone for 'today' when selecting the run to keep",
)
@click.option(
    "--keep-ingestion-run-id",
    type=int,
    default=None,
    help="Keep this run id instead of auto-picking latest run started local-today",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print plan only; no deletes",
)
@click.option(
    "--yes",
    "confirm",
    is_flag=True,
    default=False,
    help="Required to perform deletes (safety)",
)
def prune_raw_pipeline_cmd(
    timezone: str,
    keep_ingestion_run_id: int | None,
    dry_run: bool,
    confirm: bool,
) -> None:
    """Remove raw pipeline data for all ingestion runs except the kept one.

    Default: keep the latest ingestion_run whose started_at falls on today's
    calendar date in --timezone. Deletes normalized_observations, raw_extracted_items,
    raw_assets, source_fetch_runs, pipeline_alerts, log_entries for other runs,
    then those ingestion_runs. Clears publish_runs.ingestion_run_id for pruned runs.

    Does not touch products, aliases, sources, or daily_aggregates — re-run
    run_aggregator if you need aggregates aligned with remaining observations.
    """
    from sqlalchemy import text

    from organic_market_agent.db.session import engine
    from organic_market_agent.maintenance.prune_raw_pipeline import (
        build_plan,
        execute_prune,
        resolve_keep_run_id,
    )

    with engine.connect() as conn:
        keep = keep_ingestion_run_id
        if keep is None:
            keep = resolve_keep_run_id(conn, timezone=timezone)
        if keep is None:
            raise click.ClickException(
                "No ingestion_run found for local today — pass --keep-ingestion-run-id ID"
            )
        row = conn.execute(
            text(
                "SELECT id, run_type, status, started_at FROM ingestion_runs WHERE id = :k"
            ),
            {"k": keep},
        ).one()
        plan = build_plan(conn, keep)

    click.echo(f"Keeping ingestion_run id={keep} ({row[1]} / {row[2]} / started {row[3]})")
    click.echo(
        f"Would remove: runs={plan.doomed_ingestion_run_count} "
        f"sfr={plan.doomed_sfr_count} no={plan.doomed_no_count} "
        f"rei={plan.doomed_rei_count} ra={plan.doomed_ra_count}"
    )

    if dry_run:
        click.echo("Dry run — no changes.")
        return

    if not confirm:
        raise click.ClickException("Refusing to delete without --yes (or use --dry-run)")

    with engine.begin() as conn:
        stats = execute_prune(conn, keep)
    click.echo("Done. Rowcounts:")
    for k, v in sorted(stats.items()):
        click.echo(f"  {k}: {v}")


@cli.command("baseline_snapshot")
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path, dir_okay=False),
    default=None,
    help="JSON output path (default: data/normalizer_baseline.json under project root)",
)
def baseline_snapshot_cmd(output_path: Path | None) -> None:
    """Write normalizer baseline snapshot for dashboard delta comparison."""
    from organic_market_agent.admin.baseline_metrics import (
        default_baseline_path,
        write_baseline_snapshot_file,
    )
    from organic_market_agent.db.session import SessionFactory

    out = output_path or default_baseline_path()
    with SessionFactory() as session:
        written = write_baseline_snapshot_file(session, path=out)
    click.echo(f"Wrote baseline snapshot to {written.resolve()}")


@cli.command("run_admin")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=5000, type=int, show_default=True)
def run_admin_cmd(host: str, port: int) -> None:
    """Read-only Flask admin dashboard (local only)."""
    from organic_market_agent.admin import create_app

    create_app().run(host=host, port=port, debug=False)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
