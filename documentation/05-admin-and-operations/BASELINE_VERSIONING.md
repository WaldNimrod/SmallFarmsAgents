# Normalizer baseline snapshots — versioning convention

The dashboard compares live [`compute_normalizer_snapshot`](../../organic_market_agent/admin/baseline_metrics.py) output to a JSON file (default [`data/normalizer_baseline.json`](../../data/normalizer_baseline.json); override with `NORMALIZER_BASELINE_JSON`).

## Policy (Nimrod decision)

- The **primary baseline file** may stay fixed for long-term trend tracking.
- When recording a new reference point, **add a new file** instead of silently overwriting history, unless you explicitly choose to replace the primary file.

## Recommended file naming

Create an additional snapshot with UTC (or local) timestamp in the name, for example:

- `data/normalizer_baseline_2026-03-31T1930Z.json`

Or a compact form:

- `data/normalizer_baseline_20260331_1930.json`

## How to produce a snapshot

Use the admin **Save baseline** maintenance action (if enabled) or call `write_baseline_snapshot_file(session, path)` from the same module, pointing `path` to the new dated filename.

## Schema

Each file should keep `schema: normalizer_baseline_snapshot_v1` and the same keys as the default baseline (`raw_extracted_items`, `resolution_pct_norm_vs_unres`, `distinct_unresolved_raw_names`, etc.) so [`diff_against_baseline`](../../organic_market_agent/admin/baseline_metrics.py) remains valid when you temporarily point `NORMALIZER_BASELINE_JSON` at a dated file.

---

*See also: [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md) and [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md).*
