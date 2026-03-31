# Admin and operations

## Local Flask admin

- Create app: `organic_market_agent.admin.create_app`
- Default: `python -m organic_market_agent run_admin` → `127.0.0.1:5000`
- **Secret:** `ADMIN_SECRET_KEY` (see `.env.example`)

## Useful routes (high level)

| Path | Purpose |
|------|---------|
| `/` | Dashboard KPIs, charts, maintenance shortcuts |
| `/diagnostics/normalizer` | Unresolvable buckets, top raw names, scope-skip summary |
| `/catalog/scope-skip` | Numbered approved scope-skip catalog (+ JSON export when logged in) |
| `/unresolved` | Rows stuck in `unresolvable` |
| `/alerts` | `pipeline_alerts` — copy JSON for agents |
| `/runs` | Ingestion runs, trigger/stop |

## Environment

- **`DATABASE_URL`** — PostgreSQL connection string (required)
- **`NORMALIZER_BASELINE_JSON`** — optional path for dashboard baseline deltas
- **`ADMIN_SECRET_KEY`** — session signing

## Pipeline alerts

All alerts are persisted. Prefixes identify class: `[OPS:…]`, `[PIPELINE:…]`, `[SCHEDULER:…]`, `[SIMULATION:test]`, `[MAINTENANCE:…]`, `[AGG_PRICE_RULE:…]`.  
Filter in SQL or UI; see `08-troubleshooting/`.

## Playbooks

- **Unresolvable backlog (4 phases):** [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md)

## Related

- Scripts: [`../06-scripts-and-cli/`](../06-scripts-and-cli/)
- Schema notes: [`../03-data-and-schema/`](../03-data-and-schema/)
