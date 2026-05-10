# DB Activation Report — SFA-S002-P001 — 2026-05-07 (v2 — re-run)

**Date:** 2026-05-07
**Author:** team_99 (waldhomeserver)
**Type:** DB_ACTIVATION_REPORT
**Verdict:** PASS

---

## Pre-flight

- `db_connectivity_status.json`: `status: online` ✓
- Branch: `offline/2026-05-07-smallfarmsagents-release-prep`
- Hotfix commit: `49c197d` (source_tier added to 033 + seed script)

## Task A — Alembic upgrade head: PASS

```
Running upgrade 031 -> 032, 032: CQ-P01 — catalog_scope_skip_rules + product_aliases
Running upgrade 032 -> 033, 033: Extend raw_extracted_items extraction_status for pending_manual; seed SRC_WA + profiles
Running upgrade 033 -> 034, 034: Add display_bucket column to sources table
```

| Check | Result |
|-------|--------|
| Alembic current version | **034** (head) |
| `display_bucket` column | **YES** — `character varying`, NOT NULL |
| Migrations 032-034 | All applied |

## Task B — Seed MyPIPS sources: PASS

```
INSERT SRC_MP01 (משתלת הראה) — id=23
INSERT SRC_MP02 (הננתיות) — id=24
INSERT SRC_MP03 (השחקן שהפך לירקן) — id=25
INSERT SRC_MP04 (משק רתם פיין) — id=26
Done: inserted=4, skipped=0
```

| source_code | name | display_bucket | source_tier |
|-------------|------|----------------|-------------|
| SRC_MP01 | משתלת הראה | grower | price_grid |
| SRC_MP02 | הננתיות | store | price_grid |
| SRC_MP03 | השחקן שהפך לירקן | store | price_grid |
| SRC_MP04 | משק רתם פיין | grower | price_grid |

## Task C — Pipeline smoke: PASS

```
PublishEngine: wrote 33 products to output/public (rolling 7d window, version=20260507_124151)
```

## DB health check

| Check | Result |
|-------|--------|
| Total sources (all) | 25 |
| Active sources | 11 |
| Includes 4 MyPIPS | YES (SRC_MP01–SRC_MP04) |
| Publisher products | 33 |

## Summary

| Task | v1 (first attempt) | v2 (after hotfix) |
|------|-------------------|-------------------|
| A — Alembic upgrade | FAIL (source_tier) | **PASS** |
| B — Seed MyPIPS | NOT ATTEMPTED | **PASS** |
| C — Pipeline smoke | NOT ATTEMPTED | **PASS** |
| DB check | — | **PASS** (25 sources) |

**L-GATE_BUILD self-attestation: PASS**

---

*team_99 | waldhomeserver | 2026-05-07*
