# Data and schema

## Source of truth

1. **Running database** — actual state after `alembic upgrade head`
2. **Alembic migrations** — [`../../organic_market_agent/db/versions/`](../../organic_market_agent/db/versions/) (29 revisions: 001–029, no 009)
3. **SQLAlchemy models** — [`../../organic_market_agent/models/`](../../organic_market_agent/models/)

## Database overview

- **29 tables** in the `public` schema (original 23 + scheduler_config, pipeline_alerts, catalog_scope_skip_rules, product_catalog_suggestions, pending_product_aliases, product_merges)
- **67 products**, **232 active aliases**, **301 active scope-skip rules**
- **20 sources** (7 active, 13 deactivated/candidate), **11 measurement units**
- **Alembic head: 029**

## High-value tables (conceptual)

| Table | Role |
|-------|------|
| `sources`, `source_fetch_profiles`, `normalizer_profiles` | Where and how to fetch; which normalizer to use |
| `ingestion_runs`, `source_fetch_runs`, `raw_assets` | Run tracking and stored raw responses |
| `raw_extracted_items` | Parsed rows; `extraction_status`: extracted / normalized / unresolvable / **ignored** |
| `products`, `product_aliases`, `product_merges` | Catalog (67 products), raw-name mapping (232 active aliases), merge tracking |
| `catalog_scope_skip_rules` | Approved V1 out-of-scope patterns (301 rules) → `ignored` + `approved_scope_skip:…` |
| `normalizer_profiles`, `normalizer_rules` | Per-source normalizer config |
| `normalized_observations` | Publishable price facts |
| `daily_aggregates`, `weekly_snapshots` | Statistical rollups for admin / charts / publish |
| `pipeline_alerts` | Operator-facing messages (in-app alerts, no SMTP) |
| `scheduler_config` | Single-row cron configuration (time, enabled, retry, cleanup) |
| `users`, `audit_log` | Admin auth (Flask-Login + bcrypt) and write audit trail |
| `product_catalog_suggestions`, `pending_product_aliases` | Catalog inbox for new product/alias proposals |
| `observation_flags` | Admin/system marks on observations |
| `log_entries` | Detailed run logs |
| `publish_runs`, `publish_artifacts` | Publish tracking (M7) |

## Migrations workflow

```bash
cd /path/to/SmallFarmsAgents
python3 -m alembic upgrade head
python3 -m alembic current     # verify head
python3 -m organic_market_agent.db.check   # health check
```

Revision chain starts at `organic_market_agent/db/versions/`. New revisions must set `down_revision` to current head (029).

### Migration groups

| Revisions | Scope |
|-----------|-------|
| 001–005 | Initial schema (23 tables) + seed data (units, products, sources, aliases) |
| 006–007 | Alias completion + source profile fixes |
| 008 | `unresolvable_reason` column widened to TEXT |
| 010–012 | Source profile fixes, missing aliases, basket aliases |
| 013 | `source_tier` + `is_quarantined` columns |
| 014 | M4 aggregation schema (no-op — tables already in 001) |
| 015 | M5 admin user seed (Flask-Login + bcrypt) |
| 016 | M6 scheduler_config + pipeline_alerts tables |
| 017–023 | Product merges, catalog cleanup, priority aliases batch |
| 024–026 | `catalog_scope_skip_rules` schema + seed (cleaning, dry_grocery, donation) |
| 027 | Bare aliases for zucchini, potato, clementine |
| 028 | Grocery scope category + 289 mined scope-skip rules |
| 029 | Catalog inbox tables (`product_catalog_suggestions`, `pending_product_aliases`) |

## Legacy written specs

Full table-level narrative may still live in Hebrew-titled files under `docs/` (see [`../external-references/`](../external-references/)). When English replacements exist, prefer them; otherwise treat DB + migrations as authoritative.

## Delivery tier — MySQL mirror (since SFA-S003-P003 — 2026-05-23)

Postgres on waldhomeserver remains the **canonical SSoT**. End-user-facing data is **mirrored** to a small MySQL schema on `sfa.nimrod.bio` (uPress) via HMAC-authenticated push from the publisher. The mirror is read-only from the delivery tier's perspective; all writes happen on Postgres and flow downstream.

- **MySQL schema (binding):** [`sfa-mysql-mirror.md`](sfa-mysql-mirror.md) — 4 data tables + 2 plumbing tables; hybrid strategy (top-level filter cols + `payload_json` blob).
- **Architecture context:** [`../02-architecture/sfa-delivery-tier.md`](../02-architecture/sfa-delivery-tier.md)
- **Decision record:** [`../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md`](../../_COMMUNICATION/team_00/DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_2026-05-23_v1.0.0.md) (Option B — Hybrid — APPROVED 2026-05-23)

## Related

- Admin catalog UI: `/catalog/scope-skip` (numbered `display_order`)
- Catalog inbox: `/catalog/suggestions`, `/catalog/pending-aliases`
- Glossary entry **Approved Scope Skip**: [`docs/GLOSSARY.md`](../../docs/GLOSSARY.md)
