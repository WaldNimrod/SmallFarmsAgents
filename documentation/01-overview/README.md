# Overview

## What this repository is

**MyFarmAgents / OrganicMarketAgent** — a Python pipeline that collects price data from community organic vegetable sources, normalizes it against a catalog, aggregates it, and publishes static JSON/HTML for a WordPress site (no public API in V1).

For a fuller **vision, boundaries, and repository map**, see [`PROJECT_VISION_AND_SYSTEM_MAP.md`](PROJECT_VISION_AND_SYSTEM_MAP.md).

## Locked stack (summary)

- Python 3.11+, package `organic_market_agent`
- PostgreSQL + SQLAlchemy 2.x + Alembic
- Local Flask admin (127.0.0.1)
- Publish: `manifest.json` + versioned public report artifacts

## Product scope (V1)

Organic **vegetables** in **community** sales channels; baskets/CSA as basket products.  
Out-of-scope retail lines (donations, cleaning products, dry grocery on mixed grids) may be marked as **approved scope skips** via `catalog_scope_skip_rules` (see `03-data-and-schema` and admin `/catalog/scope-skip`).

## Where requirements live

- **English glossary:** [`docs/GLOSSARY.md`](../../docs/GLOSSARY.md)
- **Roadmap / gates:** [`_COMMUNICATION/ROADMAP.md`](../../_COMMUNICATION/ROADMAP.md)
- **Detailed specs:** often still under `docs/*_HE.md` or `_COMMUNICATION` — see [`../external-references/`](../external-references/)

## Related sections

- Architecture: [`../02-architecture/`](../02-architecture/)
- End-to-end data flow: [`../04-pipelines-and-runtime/`](../04-pipelines-and-runtime/)
