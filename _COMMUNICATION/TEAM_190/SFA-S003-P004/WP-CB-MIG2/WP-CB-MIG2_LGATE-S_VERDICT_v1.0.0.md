---
id: VERDICT_SFA-S003-P004-WP-CB-MIG2_L-GATE_S_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-06-01
type: validation_verdict
wp: SFA-S003-P004-WP-CB-MIG2
gate: L-GATE_S
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md
artifact_version: v1.0.0
canon: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
canon_amendment: v1.3.0 §15–§20 (DRAFT)
validator_engine: Cursor Composer (non-Claude)
phase_owner: team_190
correction_cycle: R1
result: PASS_WITH_FINDINGS
---

# WP-CB-MIG2 L-GATE_S Verdict

```yaml
wp: SFA-S003-P004-WP-CB-MIG2
gate: L-GATE_S
validator_engine: Cursor Composer (non-Claude)
result: PASS_WITH_FINDINGS
constitutional_checks: 6/6
precision_checks: 5/6
scope_checks: 3/3
findings:
  - id: F-190-MIG2-S-01
    severity: MAJOR
    summary: "WI-6/AC-07 rename planting_season→season_window in field_policy.py conflates T2 attribute layer with T1 enrichment; season_window belongs in crop_attribute (canon/field_registry.py L247–254), not FIELD_POLICY."
    evidence: "field_policy.py L77–80 has planting_season (hard_winner); enrichment_runner discovers numeric source_values only (L108–109); attribute_resolver maps season_window from planting_season column (_COLUMN_ORIGIN_ATTRS). WI-6 instructs rename, not removal."
    disposition: fix-inline
  - id: F-190-MIG2-S-02
    severity: MAJOR
    summary: "New T1 units units_per_hr (labor_rate_*) and per-field weeks/count maps are declared in Canon §16 but absent from §6.1 / canon/units.py; WI-5 does not mandate registry extension."
    evidence: "Canon §16 L391–394; units.py UNIT_REGISTRY/ALL_CANONICAL_UNITS end at count/pH/seeds_per_g — no units_per_hr; Canon §6.1 rule requires field units in registry."
    disposition: fix-inline
  - id: F-190-MIG2-S-03
    severity: MAJOR
    summary: "No WI/AC requires extending organic_market_agent/crop_book/canon/field_registry.py FIELD_REGISTRY with the §16 fields (Python SSoT parity with WP-CB-MIG pattern)."
    evidence: "WI-8 mentions canon/field_registry.py for aliases only; FIELD_REGISTRY currently ends at harvest_stage (L288–295); test_field_registry.py asserts layer/disposition per entry."
    disposition: fix-inline
  - id: F-190-MIG2-S-04
    severity: MAJOR
    summary: "T2 attribute delivery to the delivery tier is left as builder inference; WI-7 defers attribute whitelist wiring and AC-08 covers T1 _AGRONOMY_FIELD_WHITELIST only."
    evidence: "sfa_ingest_push.py pushes crops/crop_varieties/products/cover_crops only (L634–637); comment L430 references crop_attribute but no attribute fetch/push; CropBookViewController reads MySQL crop_attribute or payload fallback (L488–507)."
    disposition: fix-inline
  - id: F-190-MIG2-S-05
    severity: MINOR
    summary: "WI-8 prose says '5 unwired fields' but lists seven: seeder_settings, common_pests, foliar_feeding_program, labor_rate_harvest, labor_rate_wash, plantings_per_season, harvest_weeks_span."
    evidence: "LOD400_spec.md WI-8 L61"
    disposition: fix-inline
  - id: F-190-MIG2-S-06
    severity: MINOR
    summary: "§6.3a closed/open-vocab table not extended for MIG2 attrs; declarations live only in §16 (sufficient for C4 but inconsistent with F-190-CB0-01 single-table discipline)."
    evidence: "Canon §6.3a ends at rootstock_variety; new CLOSED attrs irrigation_type/root_depth_class/needs_summer_shade and OPEN attrs common_pests/foliar_feeding_program/unit_size appear in §16 only."
    disposition: builder-acknowledge
  - id: F-190-MIG2-S-07
    severity: INFO
    summary: "Canon §19 F-CB1-UI-01 lists planting_season→season_window/sowing_months; LOD400 WI-6 names season_window only — align prose to avoid sowing_months ambiguity."
    evidence: "Canon amendment §19 L434–436 vs LOD400 WI-6 L54"
    disposition: fix-inline
authorize_build: true
summary: "The WP-CB-MIG2 LOD400 + Canon v1.3.0 amendment is constitutionally sound: the v1.2.0 body is unchanged (git diff 2d255ee..0e966ce shows additive §15–§20 only), layer ownership is preserved via sale_unit→harvest_unit and seeder_model→seeder aliases, only migration 060 adds nullable seeder_settings, closed/open vocab is explicit, AC-15 guards IR#4, and scope matches team_00 characterization including needs_summer_shade {none, shade_30, shade_40, shade_50}. Four MAJOR precision gaps remain before a junior builder can execute without inference: field_policy planting_season handling, units registry coverage, Python FIELD_REGISTRY entries, and explicit T2 delivery-tier wiring. No blocker re-decides the locked canon or introduces duplicate-concept storage."
```

## Scope

Validated artifacts:

- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md` v1.0.0
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` amendment §15–§20 (commit `0e966ce` on `main`)
- Direction cross-check: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD200_spec.md`, `_COMMUNICATION/team_35/.../OPEN_ISSUES.md`

Engine constraint satisfied: **Cursor Composer** (non-Claude). Pre-build spec review only — no live-DB execution, no Alembic run.

Branch note: mandate cited `claude/wp-cb-mig2-2026-06-01`; artifacts are on `main` at `0e966ce` (spec commit). Review used that commit as SSoT.

## Constitutional checks (6/6)

| Check | Result | Evidence |
|-------|--------|----------|
| **C1 — Additive amendment** | PASS | `git diff 2d255ee..0e966ce -- LOD200_CROP_DATA_MODEL_CANON.md`: hunks start after the v1.2.0 closing `*Author team_100...*` line; +117 lines §15–§20 only; no edits to §1–§14 body. |
| **C2 — Layer ownership** | PASS | §16 + WI-3/AC-05: `sale_unit` alias to `harvest_unit`, no resolver entry; `seeder_model` alias to `seeder` column; T1→enrichment, T2/T3→crop_attribute, T5→column; no D2 duplicate storage. |
| **C3 — No new tables** | PASS | Only DDL is migration 060 nullable `seeder_settings` TEXT on `crop_varieties` (WI-4, AC-01); T1/T3 facts via enrichment + source_values; T2/T3 via crop_attribute. |
| **C4 — Closed vs open vocab** | PASS | §16 + WI-2: CLOSED `irrigation_type`, `root_depth_class`, `needs_summer_shade`; OPEN `common_pests`, `foliar_feeding_program`, `unit_size`; AC-03 mandates rejection/normalization. |
| **C5 — IR#4 AC-15** | PASS | LOD400 §2 AC-15 + §3: builder makes zero `_aos/roadmap.yaml` edits. |
| **C6 — Migration 060 safety** | PASS | WI-4: `down_revision: 059`, nullable column add, downgrade drops column, SQLite `batch_alter_table`; pattern matches 059 additive/reversible style; no locked-column drop/rename. |

## Precision / executability (5/6)

| Check | Result | Notes |
|-------|--------|-------|
| **P1 — Real files + mechanisms** | PASS_WITH_FINDINGS | §0 paths verified: head 059, `attribute_resolver.py`, `canon/enums.py`, `field_policy.py`, `sfa_ingest_push.py:320`, `FieldRegistry.php`, `book_crop.php:257`. Gaps: `canon/field_registry.py` FIELD_REGISTRY not in WIs (F-190-MIG2-S-03); `topics.py`/060/scripts to be created per spec. |
| **P2 — T1 discovery pinned** | PASS | WI-5 + AC-06 explicitly require builder to confirm `enrichment_runner` reconciles new field_names (policy-driven vs explicit list). |
| **P3 — Backfill provenance honest** | PASS | §17 + WI-10: PR parseable vs NI-only split correct; does not claim PR fills narrative-only groups (`needs_summer_shade`, labor rates, `plantings_per_season`). |
| **P4 — Console + NI importer** | PASS | WI-11 + AC-12/AC-13: per-gap records, defaults, clipboard JSON, NI-class ingest, idempotency, re-resolve. |
| **P5 — F-CB1-UI-01 rename** | PASS | WI-6/AC-07: four keys at field_policy L57/63/68/77; `calculator_meta.py` already canonical (grep verified); AC-07 grep-clean is testable. Layer fix needed for planting_season (F-190-MIG2-S-01). |
| **P6 — CROP_TOPICS parity** | PASS | WI-1/AC-02: Python SSoT + PHP parity test mandated; `book_crop.php:257` 13-topic array present as baseline. |

## Scope discipline (3/3)

| Check | Result | Notes |
|-------|--------|-------|
| **S1 — Out of scope** | PASS | §5 excludes labor-cost calculator, F-50-patch01-01 JS revenue fix, UI beyond proposed slots + מזיקים notes. |
| **S2 — needs_summer_shade tokens** | PASS | §16 + WI-2: `{none, shade_30, shade_40, shade_50}` matches team_00 ratification and OPEN_ISSUES.md. |
| **S3 — 16-AC matrix** | PASS | AC-01–AC-16 cover migration, topics, enums, resolver, aliases, T1 policy, renames, whitelist, UI proposed, pest notes, PR backfill, console, NI round-trip, validate_aos, IR#4, LOD500 scope audit. Delivery-path gap is WI-level, not missing AC category (address via F-190-MIG2-S-04). |

## Requested team_100 disposition (R1)

| Finding | Action |
|---------|--------|
| F-190-MIG2-S-01 | Change WI-6/AC-07: **remove** `planting_season` from `FIELD_POLICY` (do not rename to `season_window`); season_window stays attribute-only via resolver + PR backfill (WI-10). |
| F-190-MIG2-S-02 | Add WI + AC: extend `canon/units.py` (`units_per_hr`, `weeks`, `count` variant maps for new T1 fields). |
| F-190-MIG2-S-03 | Add WI + AC: register all §16 fields in `canon/field_registry.py` FIELD_REGISTRY with type/layer/disposition/unit. |
| F-190-MIG2-S-04 | Add explicit AC (e.g. AC-08b): new T2/T3 attrs delivered to delivery tier — specify ingest path (payload block and/or `crop_attribute` table push) mirroring existing `planting_method` pattern. |
| F-190-MIG2-S-05 | Fix WI-8 count (7 fields, not 5). |
| F-190-MIG2-S-06 | Optional: mirror §16 enum rows into §6.3a for consistency. |
| F-190-MIG2-S-07 | Align §19 prose with WI-6 (season_window only, or document sowing_months split). |

On inline fix → bump LOD400 to v1.0.1 if material → dispatch **team_10** L-GATE_B build → bump Canon frontmatter to **v1.3.0 LOD200_LOCKED**.

No R2 required unless team_100 declines to fix MAJOR items.

-- team_190 (Cursor Composer, non-Claude)
