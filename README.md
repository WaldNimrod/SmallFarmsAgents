# SmallFarmsAgents

Volunteer initiative under **MyFarmAgents** — collaborative AI-assisted tooling for Israel's small organic farming community. Primary code package: **`organic_market_agent`** (OrganicMarketAgent).

## What it does

OrganicMarketAgent collects organic vegetable price data from community sources (farms, CSAs, farm shops, farmers markets), normalizes it against a curated product catalog, aggregates statistics, and publishes a transparent price index.

## Quick start

```bash
# Prerequisites: Python 3.11+, Docker (PostgreSQL)
docker-compose up -d                          # Start PostgreSQL
cp .env.example .env                          # Configure DATABASE_URL
pip install -r requirements.txt
python3 -m alembic upgrade head               # Apply migrations (29 revisions)
python3 -m organic_market_agent.db.check      # Verify DB health
python3 -m organic_market_agent run_admin     # Admin UI → http://127.0.0.1:5001
```

## Current state (2026-03-31)

- **67 products**, **232 aliases**, **301 scope-skip rules**, **20 sources** (7 active)
- **100% resolution rate** — all extractable data is successfully normalized
- **174 normalized observations**, **29 database tables**, **29 Alembic migrations**
- **127 tests passing**, gates G1–G6 all PASS
- M7 (Public Publishing / Go-Live) pending Nimrod approval

## Documentation (start here)

| Resource | Purpose |
|----------|---------|
| [`documentation/README.md`](documentation/README.md) | **Documentation hub** — start here for any topic |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Canonical terminology — read first every session |
| [`CHANGELOG.md`](CHANGELOG.md) | **All code changes** — log every change here |
| [`_COMMUNICATION/ROADMAP.md`](_COMMUNICATION/ROADMAP.md) | Milestone roadmap and gate status |
| [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc) | AI assistant context (auto-loaded) |

- **RTL development guide:** [`docs/RTL_DEVELOPMENT_GUIDE.md`](docs/RTL_DEVELOPMENT_GUIDE.md)
- **Spec documents (legacy Hebrew):** in `docs/` — categorized by purpose in `project-context.mdc`

## Project structure

| Path | Role |
|------|------|
| `organic_market_agent/` | Application code (Python package) |
| `organic_market_agent/admin/` | Local Flask admin UI (Hebrew RTL, 25 templates) |
| `organic_market_agent/normalizer/` | 8-stage data-driven normalizer pipeline |
| `organic_market_agent/db/versions/` | Alembic migrations (schema history) |
| `tests/` | 15 test files, 127+ tests |
| `scripts/` | Server management + operational scripts |
| `documentation/` | English documentation hub (structured) |
| `docs/` | Glossary + legacy/bilingual technical specs |
| `_COMMUNICATION/` | Team reports, mandates, roadmap (process) |
| `data/` | Baseline snapshots and data files |
