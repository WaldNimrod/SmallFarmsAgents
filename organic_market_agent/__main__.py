"""`python -m organic_market_agent <command>`."""
from __future__ import annotations

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
        f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
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
