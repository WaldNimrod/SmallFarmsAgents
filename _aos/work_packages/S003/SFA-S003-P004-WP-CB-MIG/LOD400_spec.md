---
id: SFA-S003-P004-WP-CB-MIG-LOD400
wp: SFA-S003-P004-WP-CB-MIG — Crop Data Model Migration (execute the Canon)
gate: L-GATE_S (LOD400 — implementation spec)
status: DRAFT — for team_190 L-GATE_S (non-Claude) before any build
author: team_100 (Claude Code, Chief Architect)
date: 2026-05-31
version: v0.1.0
canon_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md   # LOD200_LOCKED v1.2.0 @ d16a611
depends_on: SFA-S003-P004-WP-CB-0 (Canon LOCKED)
builder: team_10 (Claude Sonnet) → QA team_50 (Haiku) → L-GATE_V team_190 (non-Claude, IR#1)
authorization_note: >
  team_00 approved (Canon §13) the PHYSICAL DROP of duplicated crop_varieties columns — this WP is
  explicitly authorized to modify models.py + add migrations for those drops, superseding the prior
  LOD500_LOCK on those specific columns. All other LOD500_LOCKED files remain untouched except the
  reconciler/enrichment additions named below.
---

# LOD400 — SFA-S003-P004-WP-CB-MIG: Crop Data Model Migration

**Executes the LOCKED Crop Data Model Canon (LOD200 v1.2.0) against the live data.** Brings the DB to the canonical taxonomy, names, units, enums, and layers; introduces the `crop_attribute` layer; removes duplicated/computed-stored fields; and re-enriches. **Read the Canon first — this spec implements it, it does not re-decide it.**

**Read before a single line:**
1. `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (LOCKED) — §6 vocab, §7 registry, §8 phases, §14 errata. **The registry §7 + the §6.1/§6.3/§6.3a tables are the authoritative transform maps.**
2. `organic_market_agent/crop_book/{field_policy.py, enrichment_models.py, source_registry.py}` + `importer/{reconciler.py, enrichment_runner.py}` (READ — mirror, don't modify the reconciler).
3. `organic_market_agent/publisher/sfa_ingest_push.py` (consumer to update).

---

## 1. Goal & invariants

Transform live data → canon, in **8 reversible-where-possible phases**, with **zero data loss** and **no consumer breakage** (alias cycle before any drop). On completion: every `source_values.unit` ∈ the unit registry; every T2 value ∈ canonical enums; categoricals resolved in `crop_attribute` with provenance; no stored derived/duplicate facts; consumers read the uniform contract (Canon §10).

**Hard invariants:**
- **No data loss:** every phase that rewrites is preceded by a DB backup (Mac `oma-postgres` dump) and is idempotent.
- **Cut over before drop:** the column-DROP migration (Phase 6) runs **only after** all consumers read from enrichment/attributes (Phase 5 alias cycle verified).
- **Reconciler untouched:** `reconciler.py`/`enrichment_runner.py` are not modified; the attribute resolver is a NEW sibling.
- **Dev-only this WP:** runs against Mac `oma-postgres` (head 057, canonical crop-book source per the deploy architecture). No server/uPress action — production publish is a later, separate gated step.

---

## 2. Module / migration layout

```
organic_market_agent/crop_book/
├── canon/                          ← NEW package (the canon as executable data)
│   ├── units.py                    ← UNIT_REGISTRY + UNIT_VARIANT_MAP (Canon §6.1) + normalize_unit()
│   ├── enums.py                    ← ENUM_TOKENS + ENUM_COLLAPSE (Canon §6.3/§6.3a) + canonicalize_enum()
│   ├── field_registry.py           ← FIELD_REGISTRY: name→{canonical, type, unit, layer, disposition} (Canon §7)
│   └── derive.py                   ← computed accessors: yield_per_m2(), oxide_from_elemental(), plants_per_m2(), revenue_per_bed_m()
├── attribute_models.py             ← NEW: CropAttribute ORM (Canon §4)
├── importer/
│   └── attribute_resolver.py       ← NEW: resolve T2/T3 → crop_attribute (hard_winner after enum-canon; mirrors enrichment_runner)
└── field_policy.py                 ← MODIFY: rename keys to canon; T2/T3 fields move to attribute policy

organic_market_agent/db/versions/
├── 058_crop_attribute.py           ← NEW: crop_attribute table
└── 059_drop_duplicated_crop_columns.py  ← NEW: drop §7.4 columns (runs LAST; gated)

organic_market_agent/publisher/sfa_ingest_push.py  ← MODIFY: read canon names + crop_attribute; emit uniform field_state

tests/crop_book/
├── test_canon_units.py, test_canon_enums.py, test_field_registry.py, test_derive.py
├── test_attribute_resolver.py
└── test_migration_phases.py        ← end-to-end per-phase assertions against a seeded fixture DB
```

---

## 3. The 8 phases (each = a runnable step + tests + a rollback note)

> Each phase is a CLI subcommand of a new `python -m organic_market_agent.crop_book.canon.migrate <phase>` runner, idempotent, with `--dry-run`. A **DB dump precedes phases 1, 3, 4, 6** (the rewriting/structural ones).

### Phase 1 — Unit normalize (data-only, reversible)
- Build `canon/units.py` `UNIT_VARIANT_MAP` from Canon §6.1 (incl. errata: `celsius`/`C`→`°C`; `kg`→`kg_per_bed_m` for `avg_yield_per_bed_m`; `rows`/NULL→`count`; pH-blank→`pH`; `kg/ha`→`kg_per_ha`; `seeds/g`→`seeds_per_g`; `%`→`pct`; price qualifiers preserved).
- `UPDATE crop_variety_source_values SET unit = normalize_unit(field_name, unit)`.
- **AC:** `SELECT DISTINCT unit` ⊆ registry; **zero** `celsius`/`C`/bare-`kg`-on-yield/blank rows. Rollback: restore dump.

### Phase 2 — Enum canonicalize (data-only, reversible)
- `canon/enums.py` `ENUM_COLLAPSE` from Canon §6.3/§6.3a (incl. errata `half-hardy→half_hardy`, `direct_sow→direct_seed`, `semi_hardy→half_hardy`); month CSV→int array.
- `UPDATE ... SET value_text = canonicalize_enum(field_name, value_text)` for T2; transform list fields.
- **AC:** every T2 value ∈ canonical token set; closed-enum out-of-set → logged to DQ (zero expected per the R3 sweep).

### Phase 3 — `crop_attribute` layer (migration 058 + resolver)
- `058_crop_attribute.py`: table per Canon §4 (`variety_id`, `attribute_name`, `value_canonical`, `value_list jsonb`, `winning_source_class`, `confidence_score`, `source_count`, `candidates jsonb`, `computed_at`; UNIQUE(variety_id, attribute_name)). SQLite-variant for tests.
- `attribute_models.py` ORM + `importer/attribute_resolver.py`: for each §7.2 attribute, gather source_values candidates → enum-canonicalize → `hard_winner` by the field's trust order (reuse `source_registry`) → upsert `crop_attribute` with provenance. Mirrors `enrichment_runner` structure; does NOT modify it.
- **AC:** `crop_attribute` populated for `planting_method, frost_tolerance_class, season_window, sowing_months, transplant_months, storage_ethylene_sensitivity, variety_provider, rootstock_variety`; provenance present; calculators #4/#5/#6/#11 inputs now resolvable.

### Phase 4 — Derive / dedup (stop storing derived; data-only)
- `canon/derive.py` computed accessors: `yield_per_m2 = yield_per_bed_m / bed_width(AssumptionField 0.8)`; `p2o5 = p×2.29`, `k2o = k×1.205`; `plants_per_m2` from rows/spacing/bed_width; `revenue_per_bed_m = yield×price`.
- DELETE stored enrichment rows for `yield_per_m2_kg`, `nutrient_removal_{p2o5,k2o}_kg_ha`, `plants_per_m2`, `avg_revenue_per_bed_m`. (Pre-check: per-m²-only crops converted to per-bed-m first — Canon §6.1.)
- **AC:** zero stored rows for the 4 derived fields; accessors return correct values; no consumer reads them as stored.

### Phase 5 — Rename + alias (data + access layer; NO break)
- `canon/field_registry.py` `FIELD_REGISTRY` holds `current→canonical` (Canon §7.1): `avg_yield_per_bed_m→yield_per_bed_m`, `in_row_spacing_cm→spacing_in_row_cm`, `seeds_per_gram→seeds_per_g`, `days_in_gh_total→days_in_nursery`, `documented_price→price_documented`, `nutrient_removal_*_kg_ha→*_kg_per_ha`.
- `UPDATE ... SET field_name = canonical` in source_values + crop_field_enrichment + field_policy keys. Provide a **read-alias map** so `sfa_ingest_push` + calculator_meta + any consumer resolve old-or-new for one cycle.
- Update consumers (`sfa_ingest_push.py`, WP-CB-1 `calculator_meta.py`) to canonical names + the days_in_nursery/categorical read paths (this is the **WP-CB-1 field-layer correction**, done here).
- **AC:** all consumers green on canonical names; alias resolves legacy; `pytest tests/crop_book` green.

### Phase 6 — Drop duplicated columns (migration 059 — LAST, gated)
- `059_drop_duplicated_crop_columns.py`: drop the Canon §7.4 columns from `crop_varieties` (yield/spacing/price/method/season/succession/days_in_gh/harvest_window/plants_per_m2/avg_revenue…). Modify `models.py` accordingly (team_00-authorized, §authorization_note).
- **Precondition gate (in the migration + an AC):** assert no consumer references a dropped column (grep + a runtime check) BEFORE dropping. Keep `seeder*` + identity columns.
- **AC:** columns gone; `models.py` matches; full suite + `validate_aos` green; no consumer broken. Rollback: down-migration re-adds columns (nullable) + restore dump.

### Phase 7 — Data-quality pass
- Purge duration text leaked into variety `name_he` (Canon D8); drop `seeder_roller_plate` source_values residue (7 rows; column is SSoT); validate nursery trio (`days_to_germinate ≤ days_to_potting ≤ days_in_nursery` where present).
- **AC:** zero polluted `name_he`; residue dropped; trio violations logged/0.

### Phase 8 — Re-enrich + coverage snapshot
- Run `enrichment_runner` (numerics) + `attribute_resolver` (categoricals); regenerate `COVERAGE_SNAPSHOT_CB1` (Gap-Fill §4) against the canonical vocabulary; report COMPLETE/PARTIAL split + the Nimrod fill-list.
- **AC:** snapshot produced; calculators’ required fields resolvable for the COMPLETE set; report filed.

---

## 4. Acceptance criteria (precision gate)
| AC | Criterion |
|----|-----------|
| AC-01 | `canon/units.py,enums.py,field_registry.py,derive.py` implement Canon §6.1/§6.3/§6.3a/§7 exactly; unit tests green. |
| AC-02 | Phase 1: `SELECT DISTINCT unit` ⊆ registry; 0 `celsius`/`C`/bare-kg-yield/blank. |
| AC-03 | Phase 2: every T2 value ∈ canonical enum; 0 `direct_sow`/`semi_hardy`/`half-hardy`. |
| AC-04 | Migration 058 creates `crop_attribute` (PG + SQLite variant); resolver populates §7.2 set with provenance. |
| AC-05 | Phase 4: 0 stored rows for yield_per_m2_kg/oxide/plants_per_m2/avg_revenue; `derive.py` correct (P2O5×2.29, K2O×1.205, per-m²=÷0.8). |
| AC-06 | Phase 5: field_name renamed in source_values+enrichment+policy; alias map resolves legacy; all consumers (ingest, calculator_meta) on canonical names. |
| AC-07 | Phase 5 corrects WP-CB-1 field mapping: calc #3/#4/#5 read `days_in_nursery`; #4/#5/#6/#11 read categoricals from `crop_attribute`; yield = `yield_per_bed_m`. |
| AC-08 | Migration 059 drops §7.4 columns AFTER a precondition check; `models.py` updated; down-migration restores. |
| AC-09 | Phase 7: 0 polluted variety name_he; seeder residue dropped; nursery trio validated. |
| AC-10 | Phase 8: re-enrich + attribute-resolve run; coverage snapshot filed. |
| AC-11 | `validate_aos.sh` 0 FAIL; full `pytest tests/crop_book/` green; reconciler/enrichment_runner unchanged. |
| AC-12 | Each rewriting phase has a `--dry-run` + a documented rollback; DB dump taken before phases 1/3/4/6. |

---

## 5. Sequencing & risks
- **Order is binding:** 1→2→3→4→5→6→7→8. Phase 6 (drop) is irreversible-ish → runs last, gated, after Phase 5 cutover + a clean full-suite run.
- **R-01 (data loss on rewrite):** dumps before 1/3/4/6; idempotent + `--dry-run`. **R-02 (consumer break on rename):** alias cycle (Phase 5) before drop (Phase 6). **R-03 (per-m²-only crops):** convert to per-bed-m before deleting yield_per_m2 (Phase 4 pre-check). **R-04 (SQLite test parity):** `crop_attribute` + JSONB use `.with_variant`. **R-05 (production):** none — dev-only WP; the canonical re-publish to uPress is a separate later gated step.
- **No team_35 dependency** — runs in parallel with UI design. On completion, WP-CB-1 unpauses (field layer corrected) for the UI slice once team_35 mockups land.

---

## 6. Out of scope
Production/server/uPress publish; UI; new agronomic data acquisition (gap-fill data is Phase 8's *report*, not new sourcing). Calculator math (already built + verified) is untouched except the field-mapping correction in Phase 5.

---

*Author team_100. Spec only — NO build until team_190 L-GATE_S PASS (non-Claude, IR#1). Then team_10 builds phase-by-phase; team_50 QA; team_190 L-GATE_V.*
