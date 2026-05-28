---
id: CLEANUP_AUDIT_SFA-S003-P002-WP-C5_v1.0.0
from: team_10
to: team_00 + team_100
date: 2026-05-28
type: cleanup_audit
wp: SFA-S003-P002-WP-C5
phase: Phase A (code+data cleanup)
status: COMPLETE
---

# WP-C5 Phase A — Cleanup Audit (before vs after)

## Migrations applied (2026-05-28)

```
053 → 054  crop_source_weights table created
054 → 055  data cleanup (basil + tomato + beans consolidation)
055 → 056  crop_source_weights seeded (39 rows, 8 tiers incl. WR=0.60)
```

`alembic current` = `056`. All forward-only; migration 055 is non-reversible
by design (restore from backup if rollback ever needed).

---

## Crop-level changes

| crop | name_he | name_en | before | after | Δ |
|------|---------|---------|--------|-------|---|
| 4 | בזיל | Basil | 6 var / 32 sv | **7 var / 41 sv** | +1 / +9 |
| 6 | שעועית | Beans (default: Pole/Climbing) | 8 var / 40 sv | **13 var / 40 sv** | +5 / 0 |
| 49 | עגבנייה | Tomatoes | 19 var / 67 sv | **12 var / 58 sv** | −7 / −9 (consolidation) |
| 73 | עגבניית שרי | Cherry Tomato | 4 var / 43 sv | **1 var / 39 sv** | −3 / −4 (consolidation) |
| 58 | בזיליקום | Basil | 1 var / 9 sv | **DELETED** | — |
| 59 | שעועית שיחית | Beans (Bush) | 1 var / 0 sv | **DELETED** | — |
| 60 | שעועית מטפסת | Beans (Pole) | 9 var / 1 sv | **DELETED** | — |

**Net catalog change**: −3 crops, −2 varieties (consolidations net out
against re-parented varieties). Source-value total preserved (merges used
`ON CONFLICT DO NOTHING` — kept the target's row on collision).

---

## Variety-level merge map (Decision #2 — Tomato Option A)

| from vid | merged into | crop | before sv | after sv (target) |
|----------|-------------|------|-----------|-------------------|
| 222, 403, 404, 405, 406 | **233 (default)** | 49 | 1+3+2+3+1 | 44 → 47 (+3) |
| 227 "montecarlo F.1" | 225 "hyd. montecarlo F1" | 49 | 1 | (no collision) |
| 229 "Lobelo - חישתיל מורכב" | 226 "Lobelo hyd. מורכב" | 49 | 1 | (no collision) |
| 443, 444, 445 | **460 (default)** | 73 | 8+3+1 | 31 → 39 (+8) |

vid 477 listed in DECISION_RECORD §2 for crop 73 was a typo — it was
actually the crop-58 (basil) default; handled by Decision #1 instead.
See addendum in `DECISION_RECORD_v1.0.0.md`.

---

## Source-weights table seeded

```
EX: 1 (team_00)
NI: 6 (sentinel + 5 concrete labels)
PR: 13 (sentinel + JMF + 11 university extension)
WR: 1 (★ WR:* @ 0.60 — Decision #5 Option B)
OP: 14 (sentinel + Tend×6 + Idan×3 + 4 catalog)
MK: 2 (MK:* + OMA:*)
WB: 1 (WB:*)
UC: 1 (UC:* requires_moderation)
─────
TOTAL: 39 rows
```

The `WR:*` row carries the team_00 rationale verbatim in its `notes`
column so future operators can find context via:

```sql
SELECT notes FROM crop_source_weights WHERE source_label = 'WR:*';
```

---

## Engine re-run (post-cleanup, DB-driven weights)

```
varieties processed: 367
field consensus rows: 5,291
outliers rejected:   223  (includes new WR:* outliers — proves WR is
                          participating in blend with weight 0.60 and
                          MAD/IQR gates work)
high-confidence:     811
```

Engine v1.1 inheritance + DB-driven WR weights both active.

---

## Tests & validation

| Suite | Result |
|-------|--------|
| `test_source_weights_db.py` (new, 15 tests) | 15 PASSED |
| `test_reconciler.py` | 10 PASSED |
| `test_reconciler_inheritance.py` | 6 PASSED |
| `test_reconciler_engine.py` | 18 PASSED |
| `test_enrichment_runner.py` | 5 PASSED |
| **Total focused** | **54 / 54 PASSED, 0 regressions** |

`validate_aos.sh` post-migration: **28 PASS / 19 SKIP / 1 FAIL** — the
single FAIL is Check 32 (uncommitted `_aos/` drift) which resolves on
commit; not a code/data issue.

---

## Future tuning workflow (Decision #5 — operationalized)

Per team_00 critical requirement (DECISION_RECORD §5), weight changes
are now a single SQL statement system-wide:

```sql
UPDATE crop_source_weights
SET weight = 0.65,
    notes  = 'increased after farmer feedback Q3-2026 — IL research proved reliable'
WHERE source_label = 'WR:*';
```

Then:

```bash
python3 -c "
from organic_market_agent.crop_book import source_weights_db
source_weights_db.invalidate_cache()
from organic_market_agent.db.session import SessionFactory
from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
import organic_market_agent.crop_book.enrichment_models
with SessionFactory() as s:
    run_enrichment(s); s.commit()
"
```

**No code deployment needed** — exactly what team_00 demanded.

---

## Files touched

**New:**
- `organic_market_agent/db/versions/054_crop_source_weights.py`
- `organic_market_agent/db/versions/055_wp_c5_data_cleanup.py`
- `organic_market_agent/db/versions/056_seed_crop_source_weights.py`
- `organic_market_agent/crop_book/source_weights_db.py`
- `tests/crop_book/test_source_weights_db.py`
- `_aos/work_packages/S003/SFA-S003-P002-WP-C6/LOD200_spec.md`
- `_COMMUNICATION/team_10/SFA-S003-P002-WP-C5/DECISION_RECORD_v1.0.0.md`
- `_COMMUNICATION/team_10/SFA-S003-P002-WP-C5/CLEANUP_AUDIT_v1.0.0.md` (this file)

**Modified:**
- `organic_market_agent/crop_book/source_registry.py` (facade over DB +
  added WR class + WR slotted in CLASS_RANK)
- `_aos/roadmap.yaml` (WP-C5 notes amended; WP-C6 registered PROPOSED)
- `_aos/work_packages/S003/SFA-S003-P002-WP-C5/LOD200_spec.md` (v1.1.0 —
  Phase A added)

**LOD500_LOCKED files untouched**: `reconciler.py`, `enrichment_runner.py`,
`validate_enrichment.py`, migrations 001-053, all WP-UI / publisher files.

---

*Audit by team_10 (Claude Sonnet 4.7) 2026-05-28 closing WP-C5 Phase A
under team_00 grant per DECISION_RECORD §intro.*
