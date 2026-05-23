---
id: DECIDE_SFA-S003-P003-WP-2_SCHEMA_STRATEGY_v1.0.0
type: DECISION_REQUEST
gate: WP-2 LOD400 pre-BUILD
work_package: SFA-S003-P003-WP-2
date: 2026-05-23
recorded_by: team_100 (smallfarmsagents Chief Architect)
status: AWAITING_TEAM_00_DECISION
authority: team_00 (Principal — architectural authority)
related_decision: DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0
blocks: SFA-S003-P003-WP-2 BUILD (and by extension WP-3 + WP-4)
team_100_recommendation: Option B (Hybrid — minimal mirror + payload_json)
---

# DECIDE — MySQL Schema Strategy on sfa.nimrod.bio Delivery Tier

## §1 The question (one line)

**How do we shape the MySQL schema on `sfa.nimrod.bio`, given that the canonical SSoT is Postgres on waldhomeserver?**

## §2 Why this matters

The choice is **irreversible-ish**: changing it later means writing data-migrating migrations across whatever rows are live, plus refactoring publisher (WP-4) push payloads and read endpoints (WP-2 + WP-3). The wrong call costs ~3-5 days; the right call costs us nothing extra.

The question reduces to a single trade-off:

> **Granularity of mirror** ≈ **MySQL maintenance cost** vs **read-endpoint flexibility**

Three viable options surveyed below.

## §3 Inventory of the canonical Postgres schema

| Domain | Tables | Status | User-facing? |
|--------|--------|--------|---|
| **Crop book** (S003 Phase 1) | `crop_families`, `crop_conversion_groups`, `crops`, `crop_varieties`, `crop_variety_source_values`, `crop_unit_conversions` | LOCKED, 66 crops seeded | **YES** — ספר גידולים LIVE today |
| **Products + prices** | `products`, `product_variants`, `product_aliases`, `product_merges`, `daily_aggregates`, `weekly_snapshots` | LIVE | **YES** — market index |
| **Observations** | `normalized_observations`, `observation_flags` | LIVE (high volume) | **PARTIAL** — only as aggregated price |
| **Source attribution** | `sources`, `source_fetch_profiles`, `source_fetch_runs`, `raw_assets`, `raw_extracted_items` | LIVE | **PARTIAL** — only `source.name` shown |
| **Pipeline state** | `ingestion_runs`, `scheduler_config`, `pipeline_alerts` | LIVE | **NO** — backend ops only |
| **Catalog management** | `product_catalog_suggestions`, `pending_product_aliases`, `catalog_scope_skip_rules` | LIVE | **NO** — backend QA only |
| **Units** | `measurement_units`, `unit_conversions` | LIVE | **NO** — backend transforms only |
| **Users + audit** | `users`, `audit_log`, `log_entries` | LIVE | **NO** (yet) — S004 will surface |

**Total Postgres tables: ~30. User-facing portion (today): ~8-10 tables' worth of fields.**

Critical observation: **the user-facing subset is small, stable, and read-only.** Backend tables (pipeline state, catalog management, source provenance chains) are operationally important on waldhomeserver but the user never sees them, never queries them. Mirroring them to MySQL is pure overhead.

## §4 The three options

### Option A — Full Normalized Mirror (~25 tables on MySQL)

MySQL = high-fidelity replica of Postgres user-facing schema. Each Postgres table → corresponding MySQL table with the same columns. Reconciler (WP-A) does row-level diff.

**Pros:**
- Standard normalized SQL — joinable, queryable, debuggable via phpMyAdmin
- Read endpoints can do server-side filtering on any column (e.g., "crops in family X with DTM < 60")
- Audit trail per field

**Cons:**
- **Migration tax**: every Postgres schema change → matching MySQL migration. Postgres changes ~weekly during active dev. Means ~50+ MySQL migrations over a year, each requiring deploy + apply + reconcile.
- Publisher push payload (WP-4) becomes complex — must walk relationships, batch foreign keys correctly, handle insert order
- Postgres→MySQL type mapping issues (Postgres ARRAY, JSONB, custom enums → MySQL has no native equivalent for ARRAY; ENUM is rigid)
- DB connection limit on shared host stressed (more queries per page render = more open connections)
- Single dev (you) carrying schema-sync cognitive load on every Postgres change

**Effort:** WP-2 grows from ~2-3 days → ~5-7 days. WP-4 publisher complexity ~2× (per-table push instead of per-domain). Ongoing tax: ~30 min per Postgres schema change forever.

---

### Option B — Hybrid: Minimal Mirror + `payload_json` Blob ⭐ RECOMMENDED

MySQL has ~4-6 small tables (`crops`, `crop_varieties`, `products`, `product_prices`, `sources`, `ingest_log`). Each carries:
- **Top-level columns** for fields needed by query filters / sorts / indexes (id, slug, hebrew_name, category, season, dtm_min, last_price, last_price_date, etc.)
- **`payload_json` column** for everything else (description_md, economics block, equipment block, all of `crop_variety_source_values`, etc.)

Publisher (WP-4) pushes pre-rendered JSON per row. Read endpoints return JSON merged from columns + `payload_json`. Filters use indexed columns; "show me the full crop" returns merged JSON straight.

**Pros:**
- **Schema stability**: changing Postgres-side internal fields requires zero MySQL migrations as long as they go into JSON blob. Only adding a new filter column triggers a migration.
- Publisher push is dead simple — one row per logical entity, no relationships to chase
- Read endpoints are 1-query (no joins, no N+1)
- Page render time predictable + cacheable
- MySQL connection pool stays cool
- Future schema changes can be additive-only (new optional JSON keys)
- phpMyAdmin still works for spot inspection (MySQL 8 has `JSON_EXTRACT` for ad-hoc queries)

**Cons:**
- Can't filter on fields buried inside JSON without `JSON_EXTRACT` (slower than indexed column scan)
- Server-side aggregations across many crops require pulling more data (mitigation: most aggregations are pre-computed by publisher on waldhomeserver and pushed as a separate row)
- Schema-of-JSON drift between publisher and read endpoint is implicit (mitigation: `schema_version` field in each row's JSON + assertions in `CropsController::detail`)

**Effort:** WP-2 as currently scoped (~2-3 days). WP-4 publisher straightforward HTTP push. Ongoing tax: ~0.

---

### Option C — Cache-Only (no MySQL, all dynamic from waldhomeserver)

MySQL not used. Every read endpoint on `sfa.nimrod.bio` proxies to a waldhomeserver API.

**Pros:**
- Zero schema drift (only Postgres exists)
- Always-fresh data

**Cons (mostly disqualifying):**
- **Violates the explicit architectural decision in §2 of DECISION_SFA-S003-P003** ("waldhomeserver = backend only, not strong enough for end users")
- waldhomeserver outage → SFA offline
- Adds latency (hop: user → CF → uPress → waldhomeserver → back)
- Defeats the portability rationale (uPress LAMP no longer enough — also need waldhomeserver always-on at known URL)
- WAN reliability dependency

**Why included:** completeness only. Strongly disrecommended; would require team_00 to reverse the parent decision.

## §5 Comparison matrix

| Dimension | A (Full mirror) | B (Hybrid) | C (Cache-only) |
|-----------|----|----|----|
| WP-2 effort | 5-7d | **2-3d** | 1d (less code) |
| WP-4 effort | 3-4d | **1-2d** | 0d (no push) |
| Ongoing maintenance | High (per-change migration) | **Low (additive JSON)** | None |
| Read endpoint latency | Best (1 query, native) | **Best (1 query, native)** | Worst (proxy hop + WAN) |
| Filter flexibility | Best (any column) | Good (indexed cols + JSON_EXTRACT) | Limited (whatever WHS exposes) |
| phpMyAdmin debuggability | Best | **Good** | N/A |
| Failure isolation (WHS down) | OK | **OK** | BAD (full outage) |
| Architectural fit | OK | **Best** | Violates parent DECISION |
| Schema cognitive load | High | **Low** | None (but at runtime cost) |

## §6 Recommendation: **Option B — Hybrid**

team_100 strongly recommends **Option B** because:

1. **The user-facing schema is small and stable.** Crop book has been LIVE since 2026-05-08 with ~66 crops; the surface is well-known. Products list is ~32. We aren't building a generic CMS; we're publishing a curated dataset.

2. **Postgres-side changes happen weekly.** Every change paying ~30 min of MySQL-migration tax forever is a real cost — and exactly the kind of friction that motivated the parent decision (escape WP shortcode hell). Option A re-introduces a "schema tax" with a different shape.

3. **The "lose JSON filtering" objection is small in practice.** Filter use cases on the user-facing tier are: season tabs, category tabs, DTM range. All three are top-level columns in the proposed minimal schema. Free-text search → client-side over the loaded grid (already how `crop_book` SPA works today).

4. **Reconciler (WP-A) is simpler.** WP-A team_110 architecture will diff `Postgres row → JSON-equivalent` and compare to `MySQL row.payload_json`. Single comparison per logical entity, no join graph traversal.

5. **Forward compatibility for S004.** Calculator + community features can add new fields to the JSON without DB migrations on either side. Per-user state (S004) will be its own MySQL tables (orthogonal to this decision).

## §7 What "Option B" looks like concretely (binding if chosen)

```sql
-- 4 main tables on MySQL (per WP-2 LOD400 §7):
crops               (id, slug, hebrew_name, family_id, category, season, dtm_min, dtm_max,
                     description_short, last_pushed_at, payload_json)
crop_varieties      (id, crop_id, name, payload_json)
products            (id, slug, hebrew_name, category, unit, last_price, last_price_date,
                     freshness_days, last_pushed_at, payload_json)
product_prices      (id, product_id, price_date, price, source)  -- thin, no JSON

-- 2 plumbing tables:
schema_migrations   (version, applied_at)
ingest_log          (idempotency_key, table_name, applied_at, row_count, status)
```

`payload_json` example for `crops` row:
```json
{
  "schema_version": 1,
  "description_md": "...",
  "economics": {"yield_per_dunam": 1200, "price_window_nis": [4.5, 7.0], ...},
  "care": {"sowing": "...", "watering": "..."},
  "varieties_summary": [...],
  "source_attribution_chain": [
    {"source_id": 17, "source_name": "המועצה לצמחי נוי", "field": "dtm_min"},
    ...
  ],
  "timeline": {...},
  "equipment": [...]
}
```

Read endpoint `GET /api/v1/crops/{slug}` returns `{...top-level cols, ...payload_json}` merged.

## §8 What "Option A" would change (if chosen instead)

WP-2 LOD400 §7 migrations expand from 3 files (002 crops, 003 products) to ~10 files (one per Postgres table). `IngestController` becomes ~3× larger (per-table router). WP-4 publisher gets a "schema sync" job ahead of every push to validate Postgres↔MySQL alignment.

I can re-author WP-2 LOD400 for Option A on request, but no point until decision is made.

## §9 Out of scope of this DECIDE

- Whether to also store on MySQL the *raw extracted items* (`raw_extracted_items` Postgres table) for audit — NO regardless of A/B (that's pipeline state, never user-facing)
- Schema of the eventual S004 per-user tables (separate decision)
- Whether to use MySQL 8 JSON or TEXT for `payload_json` column — auto-decide based on uPress MySQL version probe in WP-2 first deploy (8.0+ → JSON; older → TEXT with VALIDATE constraint)

## §10 Decision needed

Pick one of:

- ✅ **APPROVED Option B (Hybrid)** — team_100 proceeds to BUILD WP-2 as currently specified in LOD400
- ⚠️ **APPROVED Option A (Full mirror)** — team_100 rewrites WP-2 LOD400 to expand schema (~half day), then BUILD
- ❌ **APPROVED Option C (Cache-only)** — requires reversing parent DECISION §2; team_100 will refuse and escalate

---

*DECIDE artifact authored 2026-05-23 by team_100 (smallfarmsagents Chief Architect).*
*Branch: `claude/gallant-elbakyan-727a60`*
*Awaiting team_00 single-line response: "B" / "A" / "C" / questions.*
