# M3 Data Quality and Cohort Gate Specification
**Version:** 1.0
**Date:** 2026-03-30
**Author:** Team 100 (Architecture)
**Status:** ACTIVE — binding from M3 completion onwards

---

## Purpose

This document specifies:
1. How sources are classified (`source_tier`) and what each tier means for the normalization pipeline
2. The retention policy for `raw_extracted_items`
3. A one-time historical cleanup plan that eliminates noise from M2-era discovery-source extractions
4. The re-ingestion policy — when to re-fetch vs. normalize-only

It also defines the **forward metrics** that all gate checks use from M4 onwards.

This specification is the authority for all work mandated under:
- `MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md`
- `MANDATE_NORMALIZER_FILTER_AND_METRICS_TEAM10.md`

---

## Background: The Noise Problem

During M2 (Ingestion Engine), parsers were configured without output guards. The result:

- `SRC013` (פרמקלצ'ר ישראל / permaculture.org.il) — a discovery/portal site — was scraped.
  Its `simple_product_grid` parser extracted 663 page-chrome fragments as if they were products.
- `SRC012` (בידיים) and `SRC014` (תנועת החוות הירוקות) are similar portal-type sources.
- Farm shop sources `SRC008` and `SRC009` had selector mismatch before migration 007, producing
  454 + 316 rows with `raw_price_text = NULL`.

These 1,634+ rows are now in `raw_extracted_items` with `extraction_status = 'unresolvable'`.
They are not a normalizer defect. They are **pre-guard noise** from M2. The normalizer correctly
rejected them. But they pollute query counts and create misleading metrics.

The fix is not deletion — that would destroy audit history. The fix is **quarantine**: a boolean
flag that tells the normalizer engine to skip these rows, and that gates metrics queries exclude them.

---

## Phase 0 — Source Classification

### `source_tier` Column

Add `source_tier VARCHAR(20) NOT NULL` to the `sources` table with a CHECK constraint:
```sql
CHECK (source_tier IN ('price_grid', 'discovery', 'benchmark', 'basket'))
```

### Classification of All 20 Sources

| Code | Name | source_tier | Rationale |
|------|------|-------------|-----------|
| SRC001 | easyFarm platform | `discovery` | Portal / directory. No product price pages. |
| SRC002 | סבתא יהודית | `price_grid` | EasyFarm shop with product prices. |
| SRC003 | ח'ביזה | `basket` | CSA basket subscription. No per-unit prices. |
| SRC004 | קיימא בית זית | `price_grid` | EasyFarm shop with product prices. |
| SRC005 | קיימא חוקוק | `price_grid` | EasyFarm shop with product prices. |
| SRC006 | עץ השדה | `price_grid` | EasyFarm shop with product prices. |
| SRC007 | סלסילה | `basket` | CSA basket subscription. No per-unit prices. |
| SRC008 | שדה ירוק | `price_grid` | Direct-price farm shop. |
| SRC009 | משק זינגר | `price_grid` | Direct-price farm shop. |
| SRC010 | Farmerim | `price_grid` | Direct-price farm shop. |
| SRC011 | האורגני | `price_grid` | Direct-price farm shop. |
| SRC012 | בידיים - מעגל העסקים | `discovery` | Cooperative business portal. No prices. |
| SRC013 | פרמקלצ'ר ישראל | `discovery` | Permaculture portal. No prices. (663 noise rows) |
| SRC014 | תנועת החוות הירוקות | `discovery` | NGO portal. No prices. |
| SRC015 | מחירי תוצרת הארץ | `benchmark` | Government price index. Currently inactive (403). |
| SRC016 | דוחות שבועיים | `benchmark` | Government weekly reports. Currently inactive (403). |
| SRC017 | Pricez | `benchmark` | Retail price comparison. |
| SRC018 | CHP | `benchmark` | Retail chain price comparison. |
| SRC019 | סקאל ישראל | `benchmark` | Price verification service. |
| SRC020 | IQC | `benchmark` | Quality certification body. |

### Pipeline Behavior by Tier

| Tier | Ingestion | Normalization | Public output |
|------|-----------|---------------|---------------|
| `price_grid` | Full | Full (7-stage pipeline) | Primary source of observations |
| `basket` | Full | Basket handler only | Basket products only, `normalized_price_value = NULL` |
| `discovery` | Full (discovery crawl) | **SKIPPED** — items quarantined | Never contributes to normalized_observations |
| `benchmark` | Full (when active) | Benchmark normalizer (M5) | Reference data only, separate table |

---

## Phase 1 — Retention Policy

### Hot Path (`raw_extracted_items`)

- Rows enter with `extraction_status = 'extracted'`
- After a normalizer run they become `normalized`, `unresolvable`, or `ignored`
- `extracted` rows older than **7 days** that were never processed → logged as orphaned, flagged `ignored`

### Retention Periods

| Status | Retention | Rationale |
|--------|-----------|-----------|
| `normalized` | 1 year rolling | Enables trend analysis and re-normalization if rules change |
| `unresolvable` (price_grid) | 90 days | Debug value; parser may be fixed and re-normalization retried |
| `unresolvable` (discovery) | quarantine immediately | No re-normalization path |
| `ignored` | 30 days | Short audit window |
| `is_quarantined = true` | **Do not auto-delete** | Require explicit TTL decision from Team 100 |

Retention enforcement is **not in scope for M3 or M4**. This is Phase 1 guidance for M5+.
Team 20 must not implement any DELETE logic until explicitly mandated.

---

## Phase 2 — Historical Cleanup (One-Time, M3 → M4 Boundary)

### What to Quarantine

Quarantine all `raw_extracted_items` rows that meet **any** of the following:
1. Source is `discovery` tier (`SRC001`, `SRC012`, `SRC013`, `SRC014`)
2. Source is `basket` tier and extraction was not from the basket handler (`SRC003`, `SRC007`)
3. `raw_price_text IS NULL` AND `extraction_status = 'unresolvable'` AND source is `price_grid`

> Rule 3 catches pre-guard M2 extractions from `SRC008`/`SRC009` where selector mismatch
> caused the parser to extract page chrome without prices. These rows have no re-normalization
> value and will be replaced by the post-guard ingestion runs in M4.

### Mechanics

Add `is_quarantined BOOLEAN NOT NULL DEFAULT false` to `raw_extracted_items` (migration 009).
Set `is_quarantined = true` via a data migration in migration 009 (see mandate for Team 20).

No rows are deleted. The quarantine flag is a soft-suppress that the normalizer engine
and metrics queries must respect.

### Expected Quarantine Count

| Source | Expected Rows |
|--------|--------------|
| SRC013 (permaculture) | ~663 |
| SRC012 (בידיים) | ~estimated |
| SRC014 (חוות ירוקות) | ~estimated |
| SRC001 (easyFarm portal) | ~estimated |
| SRC008/SRC009 null-price rows | ~770 |
| **Total** | ~1,500+ |

> Actual counts determined by migration 009 data migration query output.
> Team 20 must record exact counts in their completion report.

---

## Phase 3 — Re-ingestion Policy

### When to Re-fetch (full HTTP fetch)

Re-fetch (new `ingestion_run_id`) is required when:
- Parser code has changed for a source (selector fix, new extraction logic)
- Source URL or structure has changed
- > 30 days since last successful fetch from a price_grid source

### When to Normalize-Only (skip fetch)

Run `run_normalizer --ingestion-run-id <N>` without re-fetching when:
- Alias rules have been added/changed (normalizer rule update)
- A bug in the normalizer engine was fixed (truncation, stage logic)
- Re-validation QA is needed without consuming source HTTP quota

### Normalize-Only Safety Rules

1. Only run normalize-only on rows with `extraction_status = 'extracted'` and `is_quarantined = false`
2. Running normalize-only on an already-`normalized` cohort is a no-op (engine skips them)
3. Before normalize-only re-run, capture baseline count of `normalized_observations`

---

## Forward Metrics Definition

These metrics are the standard for all gate checks from G4 onwards. They replace all
DB-wide aggregate checks that were used in G3 v1.

All metrics are scoped to a single `ingestion_run_id` cohort, filtered to
`is_quarantined = false` and `source_tier = 'price_grid'`.

| Metric | Threshold | Priority | Notes |
|--------|-----------|----------|-------|
| `resolved` | ≥ 10 per cohort | Critical | M4 entry gating metric |
| `distinct_products` | ≥ 3 per cohort | Critical | Prevents single-product skew |
| `unresolvable_rate` | ≤ 30% on price_grid non-quarantined | High | Signals parser/alias health |
| `community_sources_succeeded` | ≥ 2 | Critical | Public publish requires 2+ community sources |

### SQL Template for Forward Metrics

```sql
-- Run after: run_normalizer --ingestion-run-id <RUN_ID>
SELECT
    COUNT(*) FILTER (WHERE r.extraction_status = 'normalized') AS resolved,
    COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable') AS unresolvable,
    COUNT(*) FILTER (WHERE r.extraction_status = 'ignored') AS ignored,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable')
        / NULLIF(COUNT(*), 0), 1
    ) AS unresolvable_rate_pct,
    COUNT(DISTINCT no_obs.product_id) AS distinct_products,
    COUNT(DISTINCT sfr.source_id) FILTER (
        WHERE r.extraction_status = 'normalized'
        AND s.market_scope = 'community'
    ) AS community_sources_succeeded
FROM raw_extracted_items r
JOIN source_fetch_runs sfr ON r.source_fetch_run_id = sfr.id
JOIN sources s ON sfr.source_id = s.id
LEFT JOIN normalized_observations no_obs ON no_obs.source_fetch_run_id = sfr.id
WHERE sfr.ingestion_run_id = <RUN_ID>
  AND s.source_tier = 'price_grid'
  AND r.is_quarantined = false;
```

### `--metrics` CLI Output (implemented by Team 10)

Running `python3.11 -m organic_market_agent run_ingestion --normalize --metrics` or
`python3.11 -m organic_market_agent run_normalizer --ingestion-run-id <N> --metrics`
should print a summary like:

```
=== Cycle Metrics (run_id=<N>) ===
resolved           : 23
unresolvable       : 4
unresolvable_rate  : 14.8% (price_grid, non-quarantined)
distinct_products  : 8
community_sources  : 3 / 3 succeeded
thresholds         : resolved ✅  distinct_products ✅  unresolvable_rate ✅  community_sources ✅
```

---

## Implementation Phases Summary

| Phase | Milestone | Teams | Blocking |
|-------|-----------|-------|----------|
| Phase 0: source_tier column + seed | M3→M4 boundary | Team 20 | M4 entry |
| Phase 2: is_quarantined + data migration | M3→M4 boundary | Team 20 | M4 entry |
| Normalizer engine: skip quarantined | M3→M4 boundary | Team 10 | M4 entry |
| CLI --metrics flag | M3→M4 boundary | Team 10 | M4 entry |
| Phase 1: retention enforcement | M5 | Team 20 | M6 entry |
| Phase 3: re-ingestion automation | M5 | Team 10 | M6 entry |

---

*Produced by: Team 100 (Architecture)*
*Date: 2026-03-30*
*This document is binding. Any changes require a new ARCH_DECISION document.*
