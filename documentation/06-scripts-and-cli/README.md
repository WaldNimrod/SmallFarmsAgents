# Scripts and CLI

## Shell scripts

Repository [`../../scripts/`](../../scripts/) (examples):

| Script | Purpose |
|--------|---------|
| `restart_all_servers.sh` | Local dev server orchestration (if present in your tree) |
| `admin_server.sh` | Start admin Flask |
| `backup_postgres.sh` | DB backup helper |
| `verify_pipeline_e2e.sh` | End-to-end pipeline check |

Always inspect script contents before running in production.

## Python CLI (`python -m organic_market_agent`)

Defined in [`../../organic_market_agent/__main__.py`](../../organic_market_agent/__main__.py). Common commands:

| Command | Purpose |
|---------|---------|
| `run_admin` | Local admin dashboard |
| `run_ingestion` | Collect/parse (optional `--normalize`) |
| `run_normalizer` | Normalize pending `extracted` rows |
| `run_aggregator` | Roll aggregates for a date |
| `catalog_renormalize` | Re-queue `unresolvable`, normalize, aggregate, publish |
| `full_data_refresh` | Community full NO refresh + normalize + aggregate + publish |
| `baseline_snapshot` | Write normalizer baseline JSON |
| `prune_raw_pipeline` | Prune old pipeline data (destructive; read `--help`) |

Example:

```bash
python3 -m organic_market_agent catalog_renormalize
python3 -m organic_market_agent full_data_refresh --output-dir output/public
```

## Tools directory

[`../../tools/`](../../tools/) — non-production helpers (e.g. HTML review generators). Not part of the installed package by default.
