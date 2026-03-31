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
| `g3_alias_backfill_template.sql` | SQL template for alias backfill (historical) |

Server scripts use PID files in `/tmp/` and `nohup` for background operation.

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
