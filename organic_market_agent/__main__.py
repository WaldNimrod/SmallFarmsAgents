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


def _do_upload(output_dir: Path, ftps_file_list: list[str]) -> None:
    """Upload artifacts via WP REST API (primary) or FTPS fallback (if UPRESS_FALLBACK_FTPS=1).

    Thin wrapper around dispatch_upload — all policy lives in upload_dispatch.py (WP008).
    Exits with code 2 on failure.
    """
    from organic_market_agent.publisher.upload_dispatch import (
        NoUploadConfigured,
        UploadResult,
        dispatch_upload,
    )
    from organic_market_agent.publisher.wp_upload import (
        MissingCredentialsError as WpMissingCredentialsError,
    )

    try:
        result: UploadResult = dispatch_upload(output_dir)
    except NoUploadConfigured as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(2)
    except WpMissingCredentialsError as exc:
        click.echo(f"WP REST upload: credentials error — {exc}", err=True)
        raise SystemExit(2)
    except Exception as exc:
        click.echo(f"Upload FAILED: {exc}", err=True)
        raise SystemExit(2)

    if result.protocol_used == "wp_rest":
        click.echo(f"WP REST upload OK: {result.success_count} artifacts uploaded")
        for canonical, (mid, url) in result.wp_artifacts.items():
            click.echo(f"  {canonical} → media_id={mid} url={url}")
    elif result.protocol_used == "ftps":
        if result.success:
            click.echo(f"FTPS upload OK: {result.success_count} files uploaded")
        else:
            click.echo(
                f"FTPS upload FAILED: {result.success_count} ok, "
                f"{len(result.files_failed)} failed — {'; '.join(result.errors) or 'see logs'}",
                err=True,
            )
            raise SystemExit(2)

    if not result.success:
        raise SystemExit(2)


@cli.command("run_publisher")
@click.option(
    "--output-dir",
    "output_dir",
    default="output/public",
    show_default=True,
    help="Directory to write public_report.json / .html and manifest.json",
)
@click.option(
    "--upload",
    is_flag=True,
    default=False,
    help="After publishing, upload artifacts to uPress via WP REST API (primary) or FTPS fallback",
)
def run_publisher_cmd(output_dir: str, upload: bool) -> None:
    """Generate publish artifacts (public_report.json, .html, manifest.json) and optionally upload.

    Upload strategy (WP007):
      Primary: WP REST API (HTTPS port 443) via UPRESS_WP_APP_USER/UPRESS_WP_APP_PASS.
      Fallback: FTPS (port 21) when UPRESS_FALLBACK_FTPS=1 and WP REST is unavailable.
    """
    import os

    from organic_market_agent.db.session import SessionFactory
    from organic_market_agent.publisher.engine import PublishEngine
    from organic_market_agent.utils.exceptions import PublishAbortError

    try:
        with SessionFactory() as session:
            summary = PublishEngine().run(session, Path(output_dir))
        click.echo(f"PublishEngine: artifacts written to {output_dir}")

        if upload:
            _do_upload(Path(summary["output_dir"]), summary["files"])

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


@cli.command("run_upload")
@click.option(
    "--output-dir",
    "output_dir",
    default="output/public",
    show_default=True,
    help="Directory containing publish artifacts",
)
@click.option("--dry-run", is_flag=True, default=False, help="Log what would be uploaded without connecting (FTPS path only)")
def run_upload_cmd(output_dir: str, dry_run: bool) -> None:
    """Upload existing local publish artifacts to uPress.

    Primary: WP REST API (HTTPS port 443) — set UPRESS_WP_APP_USER + UPRESS_WP_APP_PASS.
    Fallback: FTPS (port 21) — set UPRESS_FALLBACK_FTPS=1 (also supports --dry-run).
    """
    odir = Path(output_dir)
    manifest = odir / "manifest.json"
    if not manifest.exists():
        click.echo(f"No manifest.json in {output_dir} — run 'run_publisher' first.", err=True)
        raise SystemExit(1)

    if dry_run:
        # dry-run is only meaningful for FTPS; for WP REST it's no-op
        import os
        from organic_market_agent.publisher.ftps_upload import upload_artifacts as ftps_upload_artifacts

        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        files_to_upload: list[str] = []
        for key in ("json", "html", "body"):
            versioned = manifest_data.get("artifacts", {}).get(key)
            if versioned:
                files_to_upload.append(versioned)
        for key in ("json", "html", "body"):
            fixed = manifest_data.get("fixed_names", {}).get(key)
            if fixed:
                files_to_upload.append(fixed)
        if (odir / "manifest_last_good.json").exists():
            files_to_upload.append("manifest_last_good.json")
        files_to_upload.append("manifest.json")

        result = ftps_upload_artifacts(odir, files_to_upload, dry_run=True)
        click.echo(f"FTPS dry-run OK: would upload {len(result.files_uploaded)} files")
        return

    # Build FTPS file list for fallback path
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    ftps_files: list[str] = []
    for key in ("json", "html", "body"):
        versioned = manifest_data.get("artifacts", {}).get(key)
        if versioned:
            ftps_files.append(versioned)
    for key in ("json", "html", "body"):
        fixed = manifest_data.get("fixed_names", {}).get(key)
        if fixed:
            ftps_files.append(fixed)
    if (odir / "manifest_last_good.json").exists():
        ftps_files.append("manifest_last_good.json")
    ftps_files.append("manifest.json")

    _do_upload(odir, ftps_files)


@cli.command("crop_book_publish")
@click.option(
    "--output-dir",
    "output_dir",
    default="output/crop_book",
    show_default=True,
    help="Directory to write crop book artifacts.",
)
@click.option(
    "--upload",
    is_flag=True,
    default=False,
    help='After rendering, upload artifacts via dispatch_upload(profile="crop_book").',
)
@click.option(
    "--set-mou-url",
    "set_mou_url",
    is_flag=True,
    default=False,
    help="After upload, write WP option sfagent_crop_book_manifest_of_urls_url via REST.",
)
def crop_book_publish_cmd(output_dir: str, upload: bool, set_mou_url: bool) -> None:
    """Render and optionally publish the ספר גידולים SPA to WordPress."""
    import base64
    import os

    import requests as _requests

    from organic_market_agent.crop_book.publisher.engine import (
        CropBookPublisher,
        CropBookPublishAbortError,
    )
    from organic_market_agent.db.session import SessionFactory
    from organic_market_agent.publisher.upload_dispatch import (
        NoUploadConfigured,
        dispatch_upload,
    )

    try:
        with SessionFactory() as session:
            summary = CropBookPublisher().run(session, Path(output_dir))
        click.echo(
            f"CropBookPublisher: {summary['crop_count']} crops, "
            f"{summary['variety_count']} varieties → {output_dir}"
        )

        if upload:
            result = dispatch_upload(Path(summary["output_dir"]), profile="crop_book")
            if not result.success:
                click.echo("Upload failed", err=True)
                raise SystemExit(1)
            click.echo(
                f"Uploaded {result.success_count} artifacts via {result.protocol_used}"
            )

            if set_mou_url:
                mou_entry = result.wp_artifacts.get("mou")
                if not mou_entry:
                    click.echo("No MoU URL returned from upload", err=True)
                    raise SystemExit(1)
                mou_url = mou_entry[1]

                wp_user = os.environ.get("UPRESS_WP_APP_USER", "").strip()
                wp_pass = os.environ.get("UPRESS_WP_APP_PASS", "").replace(" ", "")
                # Legacy www.nimrod.bio REST fallback RETIRED (2026-05-28); empty default.
                rest_base = os.environ.get(
                    "UPRESS_WP_REST_BASE", ""
                ).rstrip("/")

                if not (wp_user and wp_pass):
                    click.echo(
                        "UPRESS_WP_APP_USER / UPRESS_WP_APP_PASS not set — skipping --set-mou-url",
                        err=True,
                    )
                    raise SystemExit(1)

                token = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode()
                resp = _requests.put(
                    f"{rest_base}/wp/v2/settings",
                    headers={"Authorization": f"Basic {token}"},
                    json={"sfagent_crop_book_manifest_of_urls_url": mou_url},
                    timeout=15,
                )
                resp.raise_for_status()
                click.echo(f"WP option sfagent_crop_book_manifest_of_urls_url set → {mou_url}")

    except CropBookPublishAbortError as exc:
        click.echo(f"CropBookPublisher ABORTED: {exc}", err=True)
        raise SystemExit(1)
    except NoUploadConfigured as exc:
        click.echo(f"Upload not configured: {exc}", err=True)
        raise SystemExit(1)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
