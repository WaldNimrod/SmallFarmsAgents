# Data and schema

## Source of truth

1. **Running database** — actual state after `alembic upgrade head`
2. **Alembic migrations** — [`../../organic_market_agent/db/versions/`](../../organic_market_agent/db/versions/) (ordered revisions `001`, `002`, …)
3. **SQLAlchemy models** — [`../../organic_market_agent/models/`](../../organic_market_agent/models/)

## High-value tables (conceptual)

| Table | Role |
|-------|------|
| `sources`, `source_fetch_profiles` | Where and how to fetch |
| `ingestion_runs`, `source_fetch_runs`, `raw_assets` | Run tracking and stored raw responses |
| `raw_extracted_items` | Parsed rows; `extraction_status`: extracted / normalized / unresolvable / **ignored** |
| `products`, `product_aliases` | Catalog and raw-name mapping |
| `normalizer_profiles`, `normalizer_rules` | Per-source normalizer config |
| `catalog_scope_skip_rules` | Approved V1 out-of-scope patterns → `ignored` + `approved_scope_skip:…` |
| `normalized_observations` | Publishable facts |
| `daily_aggregates`, `weekly_snapshots` | Admin / charts (daily path unchanged vs rolling publish) |
| `pipeline_alerts` | Operator-facing messages |
| `users`, `audit_logs` | Admin auth and write audit |

## Migrations workflow

```bash
cd /path/to/SmallFarmsAgents
python3 -m alembic upgrade head
```

Revision chain starts at `organic_market_agent/db/versions/`. New revisions must set `down_revision` to current head.

## Legacy written specs

Full 23-table narrative may still live in Hebrew-titled files under `docs/` (see [`../external-references/`](../external-references/)). When English replacements exist, prefer them; otherwise treat DB + migrations as authoritative.

## Related

- Admin catalog UI: `/catalog/scope-skip` (numbered `display_order`)
- Glossary entry **Approved Scope Skip**: [`docs/GLOSSARY.md`](../../docs/GLOSSARY.md)
