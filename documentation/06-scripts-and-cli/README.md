# Scripts and CLI

## Shell scripts

Repository [`../../scripts/`](../../scripts/):

| Script | Purpose |
|--------|---------|
| `admin_server.sh` | Start / stop / restart admin Flask server (port 5001) |
| `viewer_server.sh` | Start / stop / restart public viewer server (port 8080) |
| `restart_all_servers.sh` | Combined restart of both admin and viewer servers |
| `backup_postgres.sh` | DB backup helper (pg_dump) |
| `verify_pipeline_e2e.sh` | End-to-end pipeline check |
| `generate_snapshot_manifest.py` | Generate data snapshot manifest |
| `mirror_raw_assets_to_folder.py` | Copy raw assets to a folder structure |
| `run_g3_phase_a_diagnosis.py` | G3 diagnostic helper (historical) |
| `mypips_discover.py` | Discover active public store pages on `mypips.app` (slug scan; outputs under `output/discovery/` by default) |
| `mypips_verify_suspected_csv.py` | Merge Team 80 + Team 10 suspected `mypips.app` URLs and probe each row (writes checked CSV; see `_COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv`) |
| `mypips_build_onboarding_workbook.py` | Build `data/mypips_source_onboarding_workbook.csv` from the verified suspected-links CSV (one row per store slug) |
| `g3_alias_backfill_template.sql` | SQL template for alias backfill (historical) |

Server scripts use PID files in `/tmp/` and `nohup` for background operation.

### MyPIPS discovery (Team 80 handoff, Team 10 implementation)

Library: [`organic_market_agent/discovery/mypips_scan.py`](../../organic_market_agent/discovery/mypips_scan.py) (httpx, verified TLS). Seeds: [`data/mypips_seeds.txt`](../../data/mypips_seeds.txt). **Active slug rule:** responses whose `<title>` contains the fixed Hebrew shell phrase `מערכת ההזמנות של העסקים העצמאיים והקהילתיים בישראל` are treated as **not** a real tenant (see [`data/mypips_reference_slugs.txt`](../../data/mypips_reference_slugs.txt) for known-good slugs).

```bash
# From repo root; writes output/discovery/mypips_scan.csv and mypips_active.txt (gitignored)
python3 scripts/mypips_discover.py \
  --seeds data/mypips_seeds.txt --hebrew --english \
  --workers 4 --delay 1.0 --years --max 3000

# Known-good calibration slugs only (no variant expansion)
python3 scripts/mypips_discover.py --reference --workers 2 --delay 1.0

# Custom slug list only — no Hebrew/English/year/numeric expansion (experiments, validation batches)
python3 scripts/mypips_discover.py --seeds path/to/slugs.txt --seeds-only --workers 3 --delay 1.0

# Onboarding workbook (committed CSV under data/)
python3 scripts/mypips_build_onboarding_workbook.py
```

Use `--no-ethics-reminder` only in automated contexts where the operator has already confirmed robots.txt / ToS. Promoting URLs to pipeline `Source` rows follows Team 100 onboarding phases ([source onboarding report](_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_STATUS_AND_PHASE2_PLAN.md)).

## Python CLI (`python -m organic_market_agent`)

Defined in [`../../organic_market_agent/__main__.py`](../../organic_market_agent/__main__.py). Commands:

| Command | Purpose |
|---------|---------|
| `run_admin` | Local admin dashboard (Flask, port 5001) |
| `run_viewer` | Local public viewer (port 8080) |
| `run_ingestion` | Collect/parse (optional `--normalize`, `--source-id`) |
| `run_normalizer` | Normalize pending `extracted` rows (optional `--source-id`, `--ingestion-run-id`) |
| `run_aggregator` | Roll aggregates for a date (`--date`) |
| `catalog_renormalize` | Re-queue `unresolvable` → normalize → aggregate → publish |
| `full_data_refresh` | Community full refresh (reset normalized/unresolvable → re-run pipeline). Does NOT reset approved `ignored` rows. |
| `baseline_snapshot` | Write normalizer baseline JSON (`data/normalizer_baseline.json`) |
| `prune_raw_pipeline` | Prune old pipeline data (destructive; read `--help`) |

### Examples

```bash
# Start servers
bash scripts/restart_all_servers.sh restart

# Run full pipeline
python3 -m organic_market_agent run_ingestion --normalize

# Normalize only
python3 -m organic_market_agent run_normalizer

# Aggregate for a specific date
python3 -m organic_market_agent run_aggregator --date 2026-03-31

# Re-process unresolvable items
python3 -m organic_market_agent catalog_renormalize

# Full community data refresh
python3 -m organic_market_agent full_data_refresh --output-dir output/public

# Take a normalizer baseline snapshot
python3 -m organic_market_agent baseline_snapshot

# DB health check
python3 -m organic_market_agent.db.check
```

## Cron scheduler

The cron runner is a self-gating entrypoint:

```bash
# Cron line (runs every minute; runner self-gates on scheduler_config)
* * * * * cd /path/to/SmallFarmsAgents && python -m organic_market_agent.scheduler.runner
```

Configuration is in the `scheduler_config` table (single row): `is_enabled`, `run_hour`, `run_minute`, `retry_attempts`, `cleanup_enabled`, `cleanup_after_days`.

Manage via admin UI at `/scheduler`.

## Tools directory

[`../../tools/`](../../tools/) — non-production helpers (e.g. HTML review generators). Not part of the installed package by default.
