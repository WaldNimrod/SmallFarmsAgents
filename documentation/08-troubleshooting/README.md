# Troubleshooting

## Pipeline alerts

1. Open admin **Alerts** page (`/alerts`) or export JSON.
2. Read the **prefix** on `message`:
   - `[OPS:process_restart]` / `[OPS:admin_stop_all]` — expected lifecycle after admin restart or stop-all
   - `[PIPELINE:failure]` / `[PIPELINE:missing_run]` — real worker errors
   - `[SCHEDULER:…]` — cron runner events (overlap guard, time gate, disabled)
   - `[SIMULATION:test]` — pytest or `triggered_by=test` runs; filter or mark read after review
   - `[MAINTENANCE:…]` — background maintenance finished or failed (renormalize, refresh, prune)
   - `[AGG_PRICE_RULE:two_source_price_spread_gt_100pct]` — price dispersion suppressed publish (2 sources, >100% spread)
   - `[AGG_PRICE_RULE:multi_source_outlier_gt_2sigma]` — price outlier suppressed publish (3+ sources, >2σ)

Full tag list: `organic_market_agent/utils/pipeline_alert_tags.py`.

## Normalizer hit rate

- **Dashboard** `/` — KPI funnel (normalized / unresolvable / ignored / total)
- **Diagnostics** `/diagnostics/normalizer` — reason buckets, top raw strings, per-source rates
- **Approved skips** — `ignored` + `ignore_reason_code = approved_scope_skip`; listed separately from `unresolvable`
- **Scope-skip catalog** — `/catalog/scope-skip` — view all 301 rules by category
- **Aliases** — `product_aliases` (global `source_id` NULL or per-source); admin at `/aliases`
- **Unresolvable detail** — `/unresolved/<id>` — full context for diagnosis and optimization

### Current resolution rate: 100%

All non-ignored items are successfully normalized. If new unresolvable items appear after ingestion, check:
1. Is there a matching alias? → add one at `/aliases/new`
2. Is this an out-of-scope item? → add scope-skip rule
3. Is there a price parsing issue? → check raw_price_text in unresolvable detail

## Publish abort

- Rolling publish needs ≥2 distinct community sources in the UTC window (see publisher logs / alerts).
- Check `manifest.json` and `public_report*.json` under `output/public/`.
- Price dispersion rules may suppress individual products — check for `[AGG_PRICE_RULE:…]` alerts.

## Database

- Confirm `alembic current` matches `029` (current head)
- Health check: `python -m organic_market_agent.db.check` — should report PASS
- Status breakdown: `SELECT extraction_status, COUNT(*) FROM raw_extracted_items GROUP BY extraction_status`
- Expected: normalized + ignored = total (0 unresolvable, 0 extracted)

## Server management

```bash
# Admin server (port 5001)
bash scripts/admin_server.sh start|stop|restart|status

# Public viewer (port 8080)
bash scripts/viewer_server.sh start|stop|restart|status

# Both servers
bash scripts/restart_all_servers.sh restart
```

PID files stored in `/tmp/`. Check `lsof -i :5001` or `lsof -i :8080` if PID files are stale.

## Logs

- Admin may write to configured loggers (`organic_market_agent.utils.logging_setup`)
- Ingestion run detail pages (`/runs/<id>`) show linked `log_entries` where populated
- Server logs: `nohup` output in log files referenced by server scripts

## Common issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Admin shows old data | Stale server process | `bash scripts/restart_all_servers.sh restart` |
| `alembic current` not at head | Missing migrations | `python3 -m alembic upgrade head` |
| Test fails with `OperationalError` | PostgreSQL not running | `docker-compose up -d` |
| New items all unresolvable | Missing aliases | Check `/unresolved/<id>` for raw names, add aliases |
| Aggregation missing products | Below publish threshold | Need ≥2 observations from ≥2 sources |
| `MultipleResultsFound` in tests | Stale test data | Run `_cleanup_m4` or check for leftover alerts |

## Escalation path

1. Reproduce with smallest command (`run_normalizer`, single source).
2. Capture alert JSON + relevant `ingestion_run_id`.
3. If schema suspected, compare migration vs [`../03-data-and-schema/`](../03-data-and-schema/).
4. Check `_COMMUNICATION/TEAM_100/reports/` for recent architectural decisions.
