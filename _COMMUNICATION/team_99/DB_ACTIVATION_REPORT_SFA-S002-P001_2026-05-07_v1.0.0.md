# DB Activation Report — SFA-S002-P001 — 2026-05-07

**Date:** 2026-05-07
**Author:** team_99 (waldhomeserver)
**Type:** DB_ACTIVATION_REPORT
**Verdict:** FAIL — migration 033 blocked by NOT NULL constraint

---

## Pre-flight

- `db_connectivity_status.json`: `status: online` ✓
- Branch: `offline/2026-05-07-smallfarmsagents-release-prep` (pulled latest)
- Alembic current: `031`

## Task A — Alembic upgrade head: FAIL

Migration 032 applied successfully (catalog_scope_skip_rules + product_aliases).

**Migration 033 FAILED:**

```
psycopg2.errors.NotNullViolation: null value in column "source_tier" 
of relation "sources" violates not-null constraint
```

Root cause: Migration `033_src_wa_pending_manual.py` INSERT into `sources` does not include the `source_tier` column, which is NOT NULL without a default value.

Existing `source_tier` values: `discovery`, `price_grid`, `benchmark`, `basket`.

Transaction rolled back — alembic remains at `031`. Migration 032's changes were also rolled back (transactional DDL).

| Check | Result |
|-------|--------|
| Alembic current version | `031` (unchanged) |
| `display_bucket` column | **NO** — migration 034 not reached |
| Migrations 032-034 applied | **NO** — 033 blocks all |

## Task B — Seed MyPIPS sources: NOT ATTEMPTED

Blocked by Task A. Additionally, `scripts/seed_mypips_sources.py` also lacks `source_tier` in its INSERT data — it would fail with the same NOT NULL violation.

## Task C — Pipeline smoke: NOT ATTEMPTED

Blocked by Task A + B.

## Defect details

| File | Issue |
|------|-------|
| `organic_market_agent/db/versions/033_src_wa_pending_manual.py` | INSERT into `sources` missing `source_tier` column (NOT NULL, no default) |
| `scripts/seed_mypips_sources.py` | Same — 4 MyPIPS source dicts lack `source_tier` key |

## Recommendation for team_100

Both files need `source_tier` added to the INSERT/seed data. Likely values:
- SRC_WA (WhatsApp Community): `source_tier = 'discovery'` or `'price_grid'`
- MyPIPS sources (mashtelatharoe, anatiyot, fruit4soul, finerotem): `source_tier = 'price_grid'` or `'basket'`

This is an application code fix — out of scope for team_99 (IR §63). Route to sfa_build (team_10) for a 1-line fix per file.

---

*team_99 | waldhomeserver | 2026-05-07 | FAIL — awaiting code fix from team_10*
