# Baseline raw capture — first full scan (2026-03-30)

**Purpose:** Immutable-style workspace for the **first complete ingestion capture** used for downstream QA, parser tuning, and offline inspection.

## Layout

| Path | Role |
|------|------|
| `capture/` | **`RAW_FILES_ROOT`** used for the dedicated ingestion run. New bytes land here; sources skipped by checksum dedup do **not** get a second copy on disk. |
| `full_mirror/` | **Complete raw archive** of every file still referenced by `raw_assets` in the DB at manifest time (copied from `capture/` and from earlier `raw_files/` roots). Use this folder for a single-tree offline corpus. |
| `SNAPSHOT_MANIFEST.json` | DB run summary + file listings for `capture/` and `full_mirror/` (see `scripts/generate_snapshot_manifest.py`). |

## How this snapshot was produced

1. `export DATABASE_URL=…` (PostgreSQL 15 direct install; same DB used for ingestion).
2. `export RAW_FILES_ROOT=<this_directory>/capture`
3. `python -m organic_market_agent.scheduler.run_ingestion --run-type manual` (Python 3.11+)

After ingestion, build `full_mirror/` (all distinct `storage_path` rows):

```bash
export DATABASE_URL=…
python scripts/mirror_raw_assets_to_folder.py data_snapshots/first_full_scan_2026-03-30/full_mirror
python scripts/generate_snapshot_manifest.py \
  data_snapshots/first_full_scan_2026-03-30/capture \
  data_snapshots/first_full_scan_2026-03-30/SNAPSHOT_MANIFEST.json
```

Do **not** point a second ingestion at `capture/` expecting a clean slate unless you intend to append or manually prune files; for a new baseline, create a new dated sibling directory under `data_snapshots/`.

## Git

The `capture/` tree and `SNAPSHOT_MANIFEST.json` are listed in `.gitignore` (large / machine-specific paths). This `README.md` is tracked.
