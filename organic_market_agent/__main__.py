"""`python -m organic_market_agent <command>`."""
from __future__ import annotations

import click


@click.group()
def cli() -> None:
    """OrganicMarketAgent CLI entry."""
    pass


@cli.command("run_normalizer")
@click.option("--source-id", default=None, type=int)
@click.option("--ingestion-run-id", default=None, type=int)
def run_normalizer_cmd(source_id: int | None, ingestion_run_id: int | None) -> None:
    """Run M3 normalizer on pending raw_extracted_items."""
    from organic_market_agent.normalizer.run_normalizer import run_normalizer_cli

    counts = run_normalizer_cli(source_id=source_id, ingestion_run_id=ingestion_run_id)
    click.echo(
        f"NormalizerEngine: resolved={counts['resolved']} "
        f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
    )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
