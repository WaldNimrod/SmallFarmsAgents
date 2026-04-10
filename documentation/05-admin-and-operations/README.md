# Admin and operations

## Local Flask admin

- Create app: `organic_market_agent.admin.create_app`
- Default: `python -m organic_market_agent run_admin` → `127.0.0.1:5001`
- **Authentication:** Flask-Login + bcrypt. Default credentials seeded in migration 015 (`admin@local` / `admin`).
- **Secret:** `ADMIN_SECRET_KEY` (see `.env.example`)
- **UI language:** Full Hebrew RTL (see `docs/RTL_DEVELOPMENT_GUIDE.md`)
- **Server script:** `scripts/admin_server.sh start|stop|restart`

## Admin routes

| Path | Purpose |
|------|---------|
| `/login` | Authentication page |
| `/` | Dashboard — KPIs, Chart.js graphs (14-day resolution rate + source success/fail), unread alert panel, maintenance shortcuts |
| `/sources` | Source list with status, tier, last fetch |
| `/sources/<code>` | Source detail — stats, observations, fetch history, link to external website |
| `/products` | Product list with observation counts |
| `/products/<id>` | Product detail — drill-down showing data origin, source, timestamps |
| `/unresolved` | Unresolvable items list |
| `/unresolved/<id>` | Unresolvable detail — full context for normalizer optimization |
| `/aliases` | Product alias list |
| `/aliases/new` | Create new alias |
| `/rules` | Normalizer rules list |
| `/rules/new` | Create new normalizer rule |
| `/qa-flags` | Observation flags view |
| `/catalog/scope-skip` | Scope-skip rules catalog (+ JSON export) |
| `/catalog/suggestions` | Catalog inbox — product suggestions |
| `/catalog/pending-aliases` | Catalog inbox — pending alias proposals |
| `/diagnostics/normalizer` | Normalizer diagnostics — reason buckets, top raw names, scope-skip summary |
| `/runs` | Ingestion run list — trigger manual/focused runs, live status polling |
| `/runs/<id>` | Run detail — alerts, duration, per-source results |
| `/scheduler` | Schedule control — enable/disable, time edit, cleanup trigger with row-count feedback |
| `/alerts` | Pipeline alerts — mark read, bulk mark-all-read |
| `/audit` | Audit log viewer (all admin write actions logged) |
| `/maintenance/*` | Background pipeline triggers (catalog renormalize, full refresh) |

## Public viewer

- Default: `python -m organic_market_agent run_viewer` → `127.0.0.1:8080`
- Serves static HTML/JSON from `output/public/`
- **Server script:** `scripts/viewer_server.sh start|stop|restart`
- **Combined restart:** `scripts/restart_all_servers.sh restart`

## Environment

- **`DATABASE_URL`** — PostgreSQL connection string (required)
- **`NORMALIZER_BASELINE_JSON`** — optional path for dashboard baseline deltas
- **`ADMIN_SECRET_KEY`** — session signing
- **`RAW_FILES_ROOT`** — raw asset storage directory (default: `raw_files/`)

## Pipeline alerts

All alerts are persisted in `pipeline_alerts` table (in-app only, no SMTP). Prefixes identify class:
- `[OPS:…]` — lifecycle events (process restart, stop)
- `[PIPELINE:…]` — worker errors, missing runs
- `[SCHEDULER:…]` — cron runner events
- `[SIMULATION:test]` — pytest or triggered_by=test runs
- `[MAINTENANCE:…]` — background maintenance (renormalize, refresh)
- `[AGG_PRICE_RULE:…]` — price dispersion rule suppression

Filter in SQL or UI; see `08-troubleshooting/`.

## Development vs production scheduling

- **Dev workstations — no automated daily runs:** [`DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md`](DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md) (manual / on-demand ingestion only; do not install cron for the runner on coding machines).

## Home staging server (waldhomeserver) and Team 61

- **File-based handoff (canonical):** [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](WALD_HOME_SERVER_AGENT_COMMUNICATION.md) — Mac `~/Documents/_agent_comm/outbox/` → `scp` → server `~/agent_comm/inbox/` for Team 61. Use this whenever server agents must see a written task or receipt; do not rely on SSH alone for that visibility.

## Playbooks

- **Unresolvable backlog (4 phases):** [`UNRESOLVABLE_BACKLOG_PLAYBOOK.md`](UNRESOLVABLE_BACKLOG_PLAYBOOK.md)
- **Normalizer baseline snapshots (dated files):** [`BASELINE_VERSIONING.md`](BASELINE_VERSIONING.md)
- **Pre-publish review:** [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md)
- **WordPress / nimrod.bio go-live (static upload + page):** [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md)

## Related

- Scripts: [`../06-scripts-and-cli/`](../06-scripts-and-cli/)
- Schema notes: [`../03-data-and-schema/`](../03-data-and-schema/)
- Troubleshooting: [`../08-troubleshooting/`](../08-troubleshooting/)
