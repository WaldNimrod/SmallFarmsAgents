# Baseline raw capture — first full scan (2026-03-30)

**Purpose:** Immutable-style workspace for the **first complete ingestion capture** used for downstream QA, parser tuning, and offline inspection.

## Layout

| Path | Role |
|------|------|
| `capture/` | **`RAW_FILES_ROOT`** for this snapshot only. Collector layout: `capture/{SOURCE_CODE}/{YYYY-MM-DD}/{SOURCE_CODE}_{HHMMSS}.{ext}` |
| `SNAPSHOT_MANIFEST.json` | Generated after the run: DB run ids, row counts, capture root path (machine-local) |

## How this snapshot was produced

1. `export DATABASE_URL=…` (PostgreSQL 15 direct install; same DB used for ingestion).
2. `export RAW_FILES_ROOT=<this_directory>/capture`
3. `python -m organic_market_agent.scheduler.run_ingestion --run-type manual` (Python 3.11+)

Do **not** point a second ingestion at this folder expecting a clean slate unless you intend to append or manually prune files; for a new baseline, create a new dated sibling directory under `data_snapshots/`.

## Git

The `capture/` tree and `SNAPSHOT_MANIFEST.json` are listed in `.gitignore` (large / machine-specific paths). This `README.md` is tracked.
