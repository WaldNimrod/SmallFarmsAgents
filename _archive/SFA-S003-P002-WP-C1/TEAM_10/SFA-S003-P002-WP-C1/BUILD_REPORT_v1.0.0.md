---
id: BUILD_REPORT_SFA-S003-P002-WP-C1_v1.0.0
from: team_10 (sfa_build)
to: team_00
date: "2026-05-27"
type: BUILD_REPORT
wp: SFA-S003-P002-WP-C1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md
status: BUILD_COMPLETE
validator: team_190 (L-GATE_V — pending)
---

# BUILD_REPORT — SFA-S003-P002-WP-C1 v1.0.0

## Summary

WP-C1 (Wave 1: Israeli structured data + Tend 2019–2021 backfill) implemented per
LOD400. Migrations **049/050** (renumbered from spec 047/048 — head already at 048).
Five importers + tend_overlay flat-CSV resolution + `seed.py --c1-only` / `--no-c1`.

## Migration note

LOD400 §3 specifies revisions 047/048; repo head was already 048
(`crop_knowledge_notes_crops` + nullable patch). team_00 approved **049/050** for
WP-C1 DDL. `created_at` columns use `TIMESTAMPTZ` per project db_health convention.

## Acceptance criteria evidence

| AC | Result | Evidence |
|----|--------|----------|
| AC-C1-01 | PASS | `049_crop_planting_calendar.py` fwd/bwd verified; tests in `test_planting_calendar.py` |
| AC-C1-02 | PASS | `050_crop_cover_crops.py` fwd/bwd verified; tests in `test_cover_crops.py` |
| AC-C1-03 | PASS | Live ingest: 41 `NI:groworganic` rows in `crop_planting_calendar` (≥30) |
| AC-C1-04 | PASS | L01 `SX`/`XS` cells → dual rows; test `test_sx_split_into_two_activities` |
| AC-C1-05 | PASS | 90.7% of 107 distinct Hebrew labels mapped via `IL_CROP_MAP` (≥80%) |
| AC-C1-06 | PASS | BUSTAN: 38 crops parsed, 44 DB rows (≥20) |
| AC-C1-07 | PASS | Idan L03 max_row=203, L04 max_row=150; 155 `OP:Idan_2017` source values |
| AC-C1-08 | PASS | 35 `crop_cover_crops` rows (≥10) with temp/zone fields |
| AC-C1-09 | PASS | Tend 2019: 442 CROP_PLAN rows, 1884 HARVESTS raw → 111 harvest_stats |
| AC-C1-10 | PASS | Tend 2020: 724 CROP_PLAN, 3720 HARVESTS raw → 128 harvest_stats |
| AC-C1-11 | PASS | Tend 2021: 552 CROP_PLAN, 1723 HARVESTS raw → 119 harvest_stats |
| AC-C1-12 | PASS | New sources registered; enrichment_runner blended without code change |
| AC-C1-13 | PASS* | EnrichmentRunner `high_conf=5`; validate_enrichment shadow shows CALIBRATED pairs |
| AC-C1-14 | PASS | `--c1-only` runs all importers + enrich; `--no-c1` wired in `--all` flow |
| AC-C1-15 | PASS | Re-run `--c1-only` idempotent (upsert keys enforced) |
| AC-C1-16 | PASS | `validate_aos.sh`: 29 PASS / 19 SKIP / 0 FAIL |
| AC-C1-17 | PASS | +25 new tests (25 pass); full suite 672 pass, 1 pre-existing admin fail |
| AC-C1-18 | PASS | LOD500_LOCKED grep → OK |
| AC-C1-19 | PASS | `UNMAPPED_CROPS_v1.0.0.md` filed |
| AC-C1-20 | PASS | This BUILD_REPORT |

## Post-ingestion DB counts (PostgreSQL)

| Table / filter | Count |
|----------------|------:|
| `crop_planting_calendar` total | 113 |
| `NI:groworganic` | 41 |
| `NI:bustan` | 44 |
| `OP:Idan_2017` (planting + source values) | 155 SV rows |
| `crop_cover_crops` | 35 |
| `crop_harvest_stats` Tend_2019 | 111 |
| `crop_harvest_stats` Tend_2020 | 128 |
| `crop_harvest_stats` Tend_2021 | 119 |

## Test baseline

- Focused WP-C1: **25 passed**
- Full suite: **672 passed**, 14 skipped, **1 failed** (pre-existing `test_admin_routes` — unchanged)
- `test_db_health timestamptz`: PASS after TIMESTAMPTZ fix

## Files created / modified

**New:** migrations 049/050, ORM `planting_calendar.py` / `cover_crops.py`, importers
under `israeli/` and `jmf/`, 7 test modules, this report + UNMAPPED_CROPS.

**Modified:** `constants.py` (`IL_CROP_MAP`), `source_registry.py`, `tend_overlay.py`
(flat CSV + variety `.first()`), `seed.py`, `requirements.txt`.

## Routing

Ready for team_190 L-GATE_V (cross-engine validation per IR#1).
