---
id: SFA-S003-P004-WP-CB-MIG2-LOD400
wp: SFA-S003-P004-WP-CB-MIG2 — Crop Data Model Expansion (13-topic taxonomy + 7 field groups)
gate: L-GATE_S (LOD400 — executable) → PASS_WITH_FINDINGS (team_190 Cursor Composer, non-Claude); 4 MAJOR fixed inline; build authorized
status: L-GATE_S PASS_WITH_FINDINGS — findings addressed inline (v1.0.1); ready for team_10 L-GATE_B
author: team_100 (Claude Code, Chief Architect)
date: 2026-06-01
version: v1.0.1
canon_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md (Amendment v1.3.0 §15–§20)
lod200_ref: _aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD200_spec.md
team_00_approval: characterization (אפיון) approved in-session 2026-06-01
depends_on: SFA-S003-P004-WP-CB-MIG (LOD500_LOCKED, head 059)
branch: claude/wp-cb-mig2-2026-06-01 (off main 8795b8a)
---

# LOD400 — WP-CB-MIG2: Crop Data Model Expansion

Executable spec for the Canon v1.3.0 amendment. Builder: **team_10** (Claude Sonnet sub-agent). Validator:
**team_190** (non-Claude, IR#1). The data layer is LOCKED — this WP is the chartered amendment vehicle.

## 0. Grounded preconditions (verified 2026-06-01)
- Alembic head = **`059`** (`organic_market_agent/db/versions/059_drop_duplicated_crop_columns.py`). This WP adds **`060`**.
- `crop_attribute` table + `attribute_models.py` + `importer/attribute_resolver.py` exist (hard_winner; reads `crop_variety_source_values`).
- Closed/open enum vocab in `organic_market_agent/crop_book/canon/enums.py` (`ENUM_TOKENS`, `OPEN_VOCAB_ATTRS`, `canonicalize_enum`).
- T2 attrs registered in `attribute_resolver._SOURCE_VALUES_ATTRS` (multi-source) or `_COLUMN_ORIGIN_ATTRS` (column).
- T1 facts: `crop_field_enrichment` keyed by `field_name`; policy in `field_policy.py` (`FIELD_POLICY` dict); reconciled by `enrichment_runner`.
- Ingest whitelist: `organic_market_agent/publisher/sfa_ingest_push.py:320` (`_AGRONOMY_FIELD_WHITELIST`).
- UI: `sfa_delivery/app/Lib/FieldRegistry.php` (`CANON` aliases, `LABELS`, `isProposed`); topics in `templates/pages/book_crop.php:257`.
- **Key consequence:** the only DDL is adding the `seeder_settings` column. New T2/T3 attrs and T1 facts are Python-config + data, no DDL.

## 1. Work items

### WI-1 — Canon constant `CROP_TOPICS`
Add `organic_market_agent/crop_book/canon/topics.py` (or extend `canon/`) with the ordered 13-topic list (§15) as the single SSoT. The PHP `book_crop.php:257` array must match it (verify parity in a test).

### WI-2 — Enum vocab (canon/enums.py)
- CLOSED-ENUM add to `ENUM_TOKENS`: `irrigation_type {drip, sprinkler, mixed}`, `root_depth_class {shallow, medium, deep}`, `needs_summer_shade {none, shade_30, shade_40, shade_50}`.
- OPEN-VOCAB add to `OPEN_VOCAB_ATTRS`: `common_pests`, `foliar_feeding_program`, `unit_size`.
- Closed-enum import-time rejection + open-vocab trim/case/dedup normalization must apply (existing `canonicalize_enum` path).

### WI-3 — Attribute resolver entries (attribute_resolver.py)
Add to `_SOURCE_VALUES_ATTRS` (canonical → source field_name): `irrigation_type`, `root_depth_class`, `needs_summer_shade`, `common_pests`, `foliar_feeding_program`, `unit_size`.
- `common_pests` is T3 (list) — confirm list handling path (like `sowing_months`).
- **`sale_unit` gets NO resolver entry** — it is a FieldRegistry alias to the existing `harvest_unit` attribute (D-MIG2-1).

### WI-4 — Migration 060 (the only DDL)
`organic_market_agent/db/versions/060_seeder_settings.py` (down_revision `059`): add nullable `seeder_settings` TEXT column to `crop_varieties`. Downgrade drops it. SQLite-compatible (`batch_alter_table` if needed). No other columns — T1 facts live in enrichment, T2/T3 in crop_attribute.

### WI-5 — T1 numeric facts (field_policy.py + enrichment)
Add `FIELD_POLICY` entries for `drip_lines_per_bed` (count), `labor_rate_harvest`, `labor_rate_wash` (units_per_hr), `plantings_per_season` (count), `harvest_weeks_span` (weeks). Use trust_order + a sensible blend (`weighted_mean` for rates, `hard_winner` for counts — match nearest existing analog).
- **AC:** builder must confirm `enrichment_runner` reconciles these field_names (verify its field discovery — policy-driven vs explicit list; wire if explicit).

### WI-5b — Unit registry coverage (canon/units.py + Canon §6.1) — **(adds F-190-MIG2-S-02)**
The new T1 facts introduce a new dimension. Extend `organic_market_agent/crop_book/canon/units.py` `UNIT_REGISTRY` and Canon §6.1:
- Add dimension `labor_rate → "units_per_hr"` (for `labor_rate_harvest`, `labor_rate_wash`).
- `drip_lines_per_bed`, `plantings_per_season` → existing `count`; `harvest_weeks_span` → existing `weeks` (`duration_weeks`). Confirm each new T1 field resolves to a registry unit (no field left unit-less); add `UNIT_VARIANT_MAP` entries only if the live/PR data carries variant unit strings.
- **AC:** every new T1 field's unit ∈ `UNIT_REGISTRY` (units.py + §6.1 parity).

### WI-6 — F-CB1-UI-01 field_policy.py corrections — **(corrects F-190-MIG2-S-01)**
Three drifted **enrichment** keys are renamed to canon: `avg_yield_per_bed_m`→`yield_per_bed_m` (L57), `documented_price`→`price_documented` (L63), `in_row_spacing_cm`→`spacing_in_row_cm` (L68). The fourth key, **`planting_season` (L77), is REMOVED from `FIELD_POLICY` — not renamed.** `season_window` is a **T2 attribute** (resolved by `attribute_resolver._COLUMN_ORIGIN_ATTRS: season_window→planting_season` into `crop_attribute`) and must NOT exist in the enrichment policy dict; renaming would wrongly create a T1 enrichment fact for a T2 concept (layer-ownership violation). Verify no other module imports the old keys (grep); `calculator_meta.py` already uses canonical names.

### WI-7 — Delivery-tier wiring (T1 whitelist + T2 attribute path) — **(corrects F-190-MIG2-S-04)**
- **T1:** add to `_AGRONOMY_FIELD_WHITELIST` (`sfa_ingest_push.py:320`): `drip_lines_per_bed`, `labor_rate_harvest`, `labor_rate_wash`, `plantings_per_season`, `harvest_weeks_span`.
- **T2/T3:** the new attributes (`irrigation_type`, `root_depth_class`, `needs_summer_shade`, `unit_size`, `common_pests`, `foliar_feeding_program`) are delivered via the **`agronomy` payload block** built in `_fetch_crop_varieties` (`sfa_ingest_push.py:430` — "categoricals from crop_attribute" via `agronomy_by_variety` + `field_state`), exactly as `planting_method`/`harvest_unit` are today. Builder must ensure the categorical-attribute list driving that block includes the new attrs (NOT the T1 whitelist). `sale_unit` rides on `harvest_unit` (alias).

### WI-8 — FieldRegistry alias + proposed (PHP + Python)
- `FieldRegistry::CANON` + Python `canon/field_registry.py` alias maps: `sale_unit→harvest_unit`, `seeder_model→seeder`.
- `isProposed()` / `LABELS`: add the **7** currently-unwired fields (`seeder_settings`, `common_pests`, `foliar_feeding_program`, `labor_rate_harvest`, `labor_rate_wash`, `plantings_per_season`, `harvest_weeks_span`) with Hebrew labels + explainers; keep the 6 already listed (`needs_summer_shade`, `irrigation_type`, `root_depth_class`, `unit_size`, `sale_unit`, `drip_lines_per_bed`).
- Controller `CropBookViewController.php`: provision the newly-wired fields with `field_state=PROPOSED` until data lands.

### WI-8b — Python FIELD_REGISTRY entries (canon/field_registry.py) — **(adds F-190-MIG2-S-03)**
The Python `FIELD_REGISTRY` (the type/layer/disposition SSoT, asserted by `test_field_registry.py`) currently ends at `harvest_stage`. Register every §16 field with a `FieldMeta(field_type, layer, disposition, unit, canonical, label)`:
- T1 enrichment: `drip_lines_per_bed` (count), `labor_rate_harvest`/`labor_rate_wash` (units_per_hr), `plantings_per_season` (count), `harvest_weeks_span` (weeks) — disposition `KEEP`/`NEW`.
- T2/T3 crop_attribute: `irrigation_type`, `root_depth_class`, `needs_summer_shade`, `unit_size`, `common_pests`, `foliar_feeding_program` — layer `crop_attribute`, disposition `ATTR`.
- T5 column: `seeder_settings` (column, KEEP).
- Aliases: `sale_unit`→canonical `harvest_unit`, `seeder_model`→canonical `seeder` (disposition `ALIAS`/`RENAME` so they flow into `ALIAS_MAP`).
- **AC:** `test_field_registry.py` extended/green for every new entry; `get_canonical()` resolves the two aliases.

### WI-9 — מזיקים topic renders knowledge_notes (D-MIG2-3)
Wire the `pest` topic in `book_crop.php` to render the existing `crop_knowledge_notes` (`pest_disease`/`irrigation` note types) for drill-down, in addition to the structured `common_pests`/`foliar_feeding_program` attribute values. Confirm the controller surfaces notes to the view.

### WI-10 — PR backfill (load_masterclass_sheets.py)
Extend the MD parser to emit `crop_variety_source_values` rows (PR class, `PR:jmf_masterclass`, weight 0.70) for the parseable groups: `irrigation_type`, `drip_lines_per_bed`, `root_depth_class`, `harvest_weeks_span`, partial `common_pests`/`foliar_feeding_program`/`unit_size`. Also backfill `season_window` from JMF where present (fold-in). Idempotent (ON CONFLICT). Keep the existing `crop_knowledge_notes` ingestion unchanged.

### WI-11 — Validation console + NI importer (§18)
- `scripts/build_crop_gap_console.py`: live DB gap-scan → self-contained `data/crop_gap_console.html`. One record per `(crop × missing field)`, grouped by the 13 topics, pre-filled best-effort default (PR parse else marked agronomic default). UI: confirm/edit/skip per field, progress, **export JSON to clipboard + download**. No external deps (inline CSS/JS).
- `scripts/ingest_nimrod_validation.py`: read the returned JSON → write `crop_variety_source_values` rows as **NI class** (`NI:nimrod_validation`, hard override) → re-run attribute_resolver + enrichment_runner. Idempotent; dry-run flag.

### WI-12 — Re-resolve + snapshot
Run `attribute_resolver` + `enrichment_runner` after backfill; regenerate the coverage snapshot; report COMPLETE/PARTIAL split for the new fields.

## 2. Acceptance criteria
| AC | Statement |
|----|-----------|
| AC-01 | `alembic upgrade head` reaches `060`; `seeder_settings` column present; downgrade clean. |
| AC-02 | `CROP_TOPICS` constant exists; PHP topic array matches it (parity test). |
| AC-03 | New closed enums in `ENUM_TOKENS`; out-of-set tokens rejected at import; open-vocab normalized. |
| AC-04 | New T2/T3 attrs in `_SOURCE_VALUES_ATTRS`; resolver writes `crop_attribute` rows with provenance for crops that have data. |
| AC-05 | `sale_unit`→`harvest_unit` and `seeder_model`→`seeder` resolve via FieldRegistry alias (no duplicate storage); no `sale_unit`/`seeder_model` resolver entry. |
| AC-06 | New T1 facts have `FIELD_POLICY` entries; `enrichment_runner` reconciles them; values land in `crop_field_enrichment`. |
| AC-06b | Every new T1 field's unit ∈ `canon/units.py UNIT_REGISTRY` (incl. new `units_per_hr`); §6.1 parity. |
| AC-07 | F-CB1-UI-01: 3 keys renamed (`yield_per_bed_m`/`price_documented`/`spacing_in_row_cm`); `planting_season` **REMOVED** from `FIELD_POLICY` (not renamed — it is T2/attribute, resolved by `attribute_resolver`); zero references to old keys remain (grep clean). |
| AC-08 | T1: `_AGRONOMY_FIELD_WHITELIST` extended; `sfa_ingest_push` dry-run includes the new T1 fields. |
| AC-08b | T2/T3: the 6 new attributes are emitted in the per-variety `agronomy` payload block (crop_attribute read path), mirroring `planting_method`; `sfa_ingest_push` dry-run shows them under `agronomy`. |
| AC-17 | `canon/field_registry.py FIELD_REGISTRY` registers every §16 field (type/layer/disposition/unit); `test_field_registry.py` green; `get_canonical()` resolves `sale_unit`→`harvest_unit` and `seeder_model`→`seeder`. |
| AC-09 | `isProposed`/`LABELS` cover all 7 groups + `needs_summer_shade`; controller provisions them; UI shows מוצע until data lands, real values after. |
| AC-10 | מזיקים topic renders `crop_knowledge_notes` drill-down + structured attrs. |
| AC-11 | PR backfill run: parseable groups + `season_window` populated from the 37 MDs (idempotent). |
| AC-12 | `build_crop_gap_console.py` generates a self-contained HTML with per-gap records, defaults, and clipboard-JSON export. |
| AC-13 | `ingest_nimrod_validation.py` round-trips a sample JSON → NI rows → re-resolve; idempotent. |
| AC-14 | `validate_aos.sh .` 0 FAIL; full `tests/crop_book/` suite green; no NEW pytest failures (2 pre-existing unrelated acknowledged). |
| AC-15 | Iron Rule #4 CLEAN — builder makes no edits to `_aos/roadmap.yaml`. |
| AC-16 | No LOD500_LOCKED file outside the chartered amendment scope is modified (git diff audit). |

## 3. Constraints
- **IR#4:** builder never edits `_aos/roadmap.yaml` (team_100 only).
- **IR#7:** DB online → structured mutations via API where applicable; this is an L2 spoke (file roadmap SSoT, ADR034 R9). DB writes go through the established importer/resolver paths, not ad-hoc SQL.
- **Delivery canon:** site is uPress; backend is waldhomeserver. No www-tier revival.
- Language: English in code/docs; Hebrew only in UI copy + DB seed product names.

## 4. Test plan (builder self-attest at L-GATE_B)
- New unit tests: enum rejection/normalization; resolver writes for each new attr; alias resolution; field_policy renames; whitelist membership; CROP_TOPICS↔PHP parity; console JSON shape; NI importer idempotency.
- Migration up/down test (SQLite + PG variant).
- Full `tests/crop_book/` regression green.

## 5. Out of scope
UI beyond lighting proposed slots + מזיקים notes; the labor-cost calculator; the JS revenue-conversion fix (F-50-patch01-01).

---

## 6. L-GATE_S remediation matrix (v1.0.1) — team_190 verdict addressed inline
team_190 (Cursor Composer, non-Claude) issued **PASS_WITH_FINDINGS** (constitutional 6/6, precision 5/6, scope 3/3, `authorize_build: true`). Verdict: `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/WP-CB-MIG2_LGATE-S_VERDICT_v1.0.0.md`. All 4 MAJOR + 2 MINOR + 1 INFO addressed inline (validator: no R2 required on inline fix):

| Finding | Sev | Disposition | Fix |
|---------|-----|-------------|-----|
| **F-190-MIG2-S-01** — WI-6 renamed `planting_season`→`season_window` in FIELD_POLICY (T1/T2 layer conflation) | MAJOR | **FIXED** | WI-6 + AC-07 now **REMOVE** `planting_season` from `FIELD_POLICY` (season_window is T2/attribute-only, resolved by `attribute_resolver`); only 3 enrichment keys renamed |
| **F-190-MIG2-S-02** — `units_per_hr` + new T1 unit maps absent from `canon/units.py` / §6.1 | MAJOR | **FIXED** | new **WI-5b** + **AC-06b**: extend `UNIT_REGISTRY` (`labor_rate→units_per_hr`) + §6.1; every new T1 unit ∈ registry |
| **F-190-MIG2-S-03** — no WI/AC to extend `canon/field_registry.py FIELD_REGISTRY` | MAJOR | **FIXED** | new **WI-8b** + **AC-17**: register every §16 field (type/layer/disposition/unit) + alias entries; `test_field_registry.py` green |
| **F-190-MIG2-S-04** — T2 delivery path left to builder inference; AC-08 = T1 only | MAJOR | **FIXED** | WI-7 split T1 (whitelist) vs **T2/T3 (`agronomy` payload block, crop_attribute path, mirrors `planting_method`)**; new **AC-08b** |
| **F-190-MIG2-S-05** — WI-8 "5 unwired fields" but lists 7 | MINOR | **FIXED** | WI-8 corrected to **7** |
| **F-190-MIG2-S-06** — §6.3a not extended for MIG2 attrs | MINOR | **FIXED** | new Canon **§16a** mirrors the §6.3a CLOSED/OPEN policy for the MIG2 attrs **additively** (locked §6.3a untouched — preserves C1) |
| **F-190-MIG2-S-07** — §19 `season_window/sowing_months` vs WI-6 wording | INFO | **FIXED** | Canon §19 aligned: `planting_season` removed from FIELD_POLICY; `season_window` attribute-only (no `sowing_months` split) |

**OPEN: none. WAIVED: none.**

*Author team_100, 2026-06-01. L-GATE_S PASS_WITH_FINDINGS (team_190 non-Claude); findings fixed inline (v1.0.1); build authorized. Next → dispatch team_10 L-GATE_B; on L-GATE_B PASS bump Canon frontmatter to v1.3.0 LOD200_LOCKED.*
