# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-MIG (L-GATE_V) — team_100 → team_190 — v1.0.0

**Date:** 2026-05-31
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · `main` · HEAD `a6df5f4`
**Gate:** **L-GATE_V** (final validation) of WP-CB-MIG, after build + 2 team_100-caught correctives.

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
Builder = Claude Sonnet (team_10). Verifier = Claude Opus (team_100). Therefore this L-GATE_V **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm engine in header.

## 1. Context: why thorough validation is especially warranted
The team_100 independent L-GATE_B verification caught **two defects** the build self-attested as PASS/pre-existing:
1. **AC-05 false PASS** — 4 derived fields regenerated (Phase 4 deleted enrichment rows but not source_values; Phase 8 re-enrich recreated them). Corrective: delete from both tables + Phase 4 code fixed.
2. **19 "pre-existing" failures were NEW + hid a site-crashing bug** — `views.py` read DROPPED columns → every HTTP request would `AttributeError`-crash the live site; `engine.py` dropped required fields from data.json → broke SPA filters. Both fixed.

A fresh non-Claude pass is warranted for confidence before this closes.

## 2. Artifacts
- **Build report (incl. correctives):** `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG/BUILD_REPORT_v1.0.0.md`
- **Coverage snapshot:** `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG/COVERAGE_SNAPSHOT_CB1_v1.0.0.md`
- **Canon (SSoT, LOCKED):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (v1.2.0 @ d16a611)
- **Migration LOD400 (LOCKED):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md` (v1.0.0)

## 3. Validation checklist — run each independently against the live DB

### 3.1 DB state (run the SQL; compare to expected)

**Unit canonicality (AC-02):**
```sql
SELECT coalesce(unit,'(NULL)'), count(*) FROM crop_variety_source_values
WHERE unit NOT IN ('°C','days','weeks','cm','kg_per_bed_m','kg_per_ha','ILS_per_kg',
  'ILS_per_bunch','ILS_per_unit','pct','pH','seeds_per_g','count','kg_per_m2')
  OR unit IS NULL
GROUP BY 1;
```
PASS iff only NULL-unit rows are categorical fields (no numeric value). Zero `celsius`/`C`/bare-`kg`-on-yield/`%`/`seeds/g`.

**Enum canonicality (AC-03):**
```sql
SELECT value_text, count(*) FROM crop_variety_source_values
WHERE field_name = 'frost_tolerance_class'
  AND value_text NOT IN ('hardy','half_hardy','tender','very_tender')
GROUP BY 1;
SELECT value_text, count(*) FROM crop_variety_source_values
WHERE field_name = 'planting_method'
  AND value_text NOT IN ('direct_seed','transplant','seed_tuber','slip','cutting')
GROUP BY 1;
```
PASS iff both return empty.

**Derived fields eliminated (AC-05 — the corrected defect):**
```sql
SELECT field_name, count(*) FROM crop_field_enrichment
WHERE field_name IN ('yield_per_m2_kg','nutrient_removal_p2o5_kg_ha',
  'nutrient_removal_k2o_kg_ha','plants_per_m2','avg_revenue_per_bed_m')
GROUP BY 1;
SELECT field_name, count(*) FROM crop_variety_source_values
WHERE field_name IN ('yield_per_m2_kg','nutrient_removal_p2o5_kg_ha',
  'nutrient_removal_k2o_kg_ha','plants_per_m2')
GROUP BY 1;
```
PASS iff **both return empty** (0 rows in both tables).

**crop_attribute populated (AC-04):**
```sql
SELECT attribute_name, count(*) FROM crop_attribute GROUP BY 1 ORDER BY 1;
```
PASS iff all 11 Canon §7.2 attributes present: `frost_tolerance_class, harvest_stage, harvest_unit, planting_method, rootstock_variety, season_window (note: 0 rows is a DATA GAP, not a defect — source column was NULL for all varieties), sowing_months, storage_ethylene_sensitivity, transplant_months, variety_provider`.

**No renamed fields remain under old name (AC-06):**
```sql
SELECT field_name, count(*) FROM crop_field_enrichment
WHERE field_name IN ('avg_yield_per_bed_m','in_row_spacing_cm','seeds_per_gram',
  'days_in_gh_total','documented_price') GROUP BY 1;
```
PASS iff empty.

**Alembic head:**
```bash
python3 -m alembic current
```
PASS iff `059 (head)`.

**Columns dropped from crop_varieties (AC-08):**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name='crop_varieties'
  AND column_name IN ('avg_yield_per_bed_m','in_row_spacing_cm','rows_per_bed',
  'documented_price','planting_method','planting_season','succession_interval_weeks',
  'days_in_gh_total','harvest_window_min_days','harvest_window_max_days');
```
PASS iff empty (columns gone). Also verify canonical rename present:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name='crop_varieties' AND column_name='nursery_days_to_germinate';
```
PASS iff returns 1 row.

**DQ pass (AC-09) — storage_life_text eliminated:**
```sql
SELECT count(*) FROM crop_variety_source_values WHERE field_name='storage_life_text';
```
PASS iff 0.

### 3.2 Consumer code (the corrected site-crash bug — AC-07)
Verify `views.py` and `engine.py` NO LONGER reference the dropped columns directly on the ORM model:
```bash
grep -n "default_var\.\|variety\." organic_market_agent/crop_book/views.py \
  | grep -E "planting_season|days_to_maturity|harvest_window|days_in_gh|in_row_spacing_cm|avg_yield"
grep -n "\.\(planting_season\|days_to_maturity\|avg_yield_per_bed_m\|in_row_spacing_cm\)" \
  organic_market_agent/crop_book/publisher/engine.py
```
PASS iff both return empty (consumers now read from `crop_attribute` / `crop_field_enrichment` / `crop_field_enrichment`).

### 3.3 Code constraints (constitutional — all must PASS)
```bash
# Reconciler untouched
git diff a6df5f4 -- organic_market_agent/crop_book/importer/reconciler.py | wc -l   # expect 0

# Enrichment runner untouched  
git diff a6df5f4 -- organic_market_agent/crop_book/importer/enrichment_runner.py | wc -l   # expect 0

# Iron Rule #4 — no roadmap edit in builder commit
git show 0247a95 -- _aos/roadmap.yaml | wc -l   # expect 0

# No production push
grep -rn "sfa_ingest_push\|ingest_push\|POST.*ingest" \
  organic_market_agent/crop_book/canon/migrate.py   # must not push to live
```

### 3.4 Tests and validation
```bash
python3 -m pytest tests/crop_book/ -q
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```
PASS iff pytest has **only 2 known pre-existing failures** (`test_source_registry::test_uc_prefix_requires_moderation` and `test_ni_publisher_isolation::test_ac21b_publisher_dir_clean`). validate_aos = 0 FAIL.

### 3.5 Data gaps (NOT defects — report as NOTEs)
Two issues are pre-existing **data absences**, not migration defects. State them in the verdict as informational:
- **`season_window` = 0 rows** in `crop_attribute` — the source `planting_season` column was NULL for all 368 varieties; no importer populates it. Gap-fill needed (EX/NI/WR).
- **50 nursery-trio violations** — `nursery_days_to_potting > days_in_nursery` for some varieties: semantic mismatch between JMF (day-0 = pot-up) and Tend (day-0 = sow). Expert override or source re-eval needed.

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG/WP-CB-MIG_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_V
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | FAIL
constitutional_checks: <n/4>
ac_checks: <n/12>
findings:
  - id: F-190-MIG-LV-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: ...
notes:
  - season_window data gap
  - nursery-trio violation count
summary: <one paragraph>
```
- **PASS** → team_100 advances WP-CB-MIG to LOD500_LOCKED; WP-CB-1 unpauses (field layer now corrected); full program can converge when team_35 mockups land.
- **FAIL/BLOCKER** → team_100 remediates and routes R2.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---
*Self-contained L-GATE_V package for non-Claude execution. team_00: route to a non-Claude validator.*
