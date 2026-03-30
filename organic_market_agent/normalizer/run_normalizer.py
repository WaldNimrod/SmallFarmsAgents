"""Standalone normalizer CLI: `python -m organic_market_agent.normalizer.run_normalizer`."""
from __future__ import annotations

import click

from organic_market_agent.db.session import SessionFactory
from organic_market_agent.normalizer.engine import NormalizerEngine
from organic_market_agent.utils.config import config


def run_normalizer_cli(
    source_id: int | None = None,
    ingestion_run_id: int | None = None,
) -> dict[str, int]:
    """Run normalizer; return counts dict."""
    config.ensure_dirs()
    with SessionFactory() as session:
        engine = NormalizerEngine()
        return engine.run(
            session,
            ingestion_run_id=ingestion_run_id,
            source_id=source_id,
        )


@click.command()
@click.option("--source-id", default=None, type=int, help="Limit to one source (sources.id)")
@click.option(
    "--ingestion-run-id",
    default=None,
    type=int,
    help="Limit to raw items from this ingestion run",
)
def main(source_id: int | None, ingestion_run_id: int | None) -> None:
    """Normalize all pending raw_extracted_items (extraction_status='extracted')."""
    counts = run_normalizer_cli(source_id=source_id, ingestion_run_id=ingestion_run_id)
    click.echo(
        f"NormalizerEngine: resolved={counts['resolved']} "
        f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
    )


if __name__ == "__main__":
    main()
