# Troubleshooting

## Pipeline alerts

1. Open admin **Alerts** or export JSON.
2. Read the **prefix** on `message`:
   - `[OPS:process_restart]` / `[OPS:admin_stop_all]` — expected lifecycle after admin restart or stop-all
   - `[PIPELINE:failure]` / `[PIPELINE:missing_run]` — real worker errors
   - `[SIMULATION:test]` — pytest or `triggered_by=test` runs; filter or mark read after review
   - `[MAINTENANCE:…]` — background maintenance finished or failed

## Normalizer hit rate

- **Diagnostics** `/diagnostics/normalizer` — reason buckets, top raw strings, per-source rates
- **Approved skips** — `ignored` + `ignore_reason_code = approved_scope_skip`; listed separately from `unresolvable`
- **Aliases** — `product_aliases` (global `source_id` NULL or per-source)

## Publish abort

- Rolling publish needs ≥2 distinct community sources in the UTC window (see publisher logs / alerts).
- Check `manifest.json` and `public_report*.json` under `output/public/`.

## Database

- Confirm `alembic current` matches `heads`
- `SELECT COUNT(*) FROM raw_extracted_items GROUP BY extraction_status` — sanity split

## Logs

- Admin may write to configured loggers (`organic_market_agent.utils.logging_setup`)
- Ingestion run detail pages show linked `log_entries` where populated

## Escalation path

1. Reproduce with smallest command (`run_normalizer`, single source).
2. Capture alert JSON + relevant `ingestion_run_id`.
3. If schema suspected, compare migration vs [`../03-data-and-schema/`](../03-data-and-schema/).
