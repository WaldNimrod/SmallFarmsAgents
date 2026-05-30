---
id: SFA-S003-P004-WP-CB-0-LOD200
wp: SFA-S003-P004-WP-CB-0 — Crop Data Model Canon
gate: L-GATE_S (LOD200 — architecture/design)
status: DRAFT — for team_00 review
author: team_100 (Claude Code, Chief Architect)
date: 2026-05-30
version: v0.1.0
supersedes_field_layer_of: SFA-S003-P004-WP-CB-1 (LOD400 field mapping will be corrected to this canon)
grounded_in: live oma-postgres inventory 2026-05-30 (head 057; 70 crops / 368 varieties / 2061 source_values / 5780 enrichment)
team_00_decisions:
  - "Full Canon first — pause calculator/UI build until approved"
  - "Per-bed-meter is the canonical yield basis (derive per-m²)"
  - "Uniform attributes layer — categoricals get single-best + provenance + confidence"
---

# LOD200 — Crop Data Model Canon

**The single source of truth for how crop knowledge is named, typed, stored, reconciled, and read.**
Mandate (team_00, 2026-05-30): *"the crop data structure must be precise, smart, and intuitive — otherwise it becomes huge technical debt. Examine the long range and prepare the data to serve the big future vision."*

---

## 1. Why this exists — the debt, measured

The crop data model accreted across ~12 WPs (JMF base, C1–C6 importers, WP-A enrichment, WP-C4 web sources) with no single design. Live inventory exposes concrete debt:

| # | Debt | Evidence (live DB) |
|---|------|--------------------|
| D1 | **Unit chaos** — one dimension, many unit strings | temperature stored as `°C` (184), `celsius` (60), `C` (43) |
| D2 | **Duplicate-concept fields** | yield: `avg_yield_per_bed_m` (106) **+** `yield_per_m2_kg` (132); nutrients elemental **+** oxide (`*_k_kg_ha` 187 **+** `*_k2o_kg_ha` 150; same for P) |
| D3 | **Computed values stored as facts** (drift risk) | `plants_per_m2` (92), `avg_revenue_per_bed_m` — derivable from inputs, yet stored as reconciled rows |
| D4 | **No layer-ownership rule** | same concept appears across `crop_varieties` columns, `source_values`, and `crop_field_enrichment` with no governing rule |
| D5 | **Categoricals stranded** (no `value_best`) | `planting_method`, `frost_tolerance_class`, `seed_months_list`, `transplant_months_list`, `variety_provider`, `storage_ethylene_sensitivity` live in `source_values`, unreconciled |
| D6 | **Categorical value chaos** | `planting_method`: `direct_seed` **and** `direct_sow`; `frost_tolerance_class`: `half-hardy` **and** `semi_hardy` — same concepts, different strings |
| D7 | **Naming inconsistency** | `avg_yield_per_bed_m` vs `yield_per_m2_kg`; `storage_life_days` (num) vs `storage_life_text` (text) for one concept |
| D8 | **Identity pollution** (data quality) | variety `name_he` values like `"45 יום"`, `"3 חודשים"` — durations leaked into the identity field |

This canon fixes D1–D8 at the root and defines the model so the **future vision** (Planner, Tasks, POS, Tend) extends it without breaking changes.

---

## 2. Design principles

1. **One concept → one canonical field → one unit → one owning layer.** No synonyms, no duplicate storage.
2. **Provenance everywhere.** Every knowledge value (numeric or categorical) carries: winning source class, confidence, source count, range. The "one winning value" is shown; the hierarchy is drill-down.
3. **Compute, don't store, what is derivable.** Derived quantities are functions of canonical facts, never persisted reconciled rows.
4. **Canonical vocabularies.** Units and categorical values come from closed, versioned enums — not free text.
5. **Crop baseline + variety override.** Crop-level defaults via the synthetic default variety; specific varieties override specific fields only.
6. **Extensible by namespace, not by schema churn.** New future-module fields slot into the same typed layers under reserved namespaces — no new tables per module.
7. **Repo is the canonical source; the DB is a materialization.** Importers + source files + the canon define truth; the DB is reproducible from them.

---

## 3. Field-type taxonomy (the core)

Every crop datum is exactly one of six types. Type determines storage layer, reconciliation, and access.

| Type | Definition | Reconciliation | Owning layer | Read path |
|------|------------|----------------|--------------|-----------|
| **T1 Reconciled-numeric (Fact)** | multi-source number | trust-weighted (weighted_mean / latest_op) + outlier gate | `crop_field_enrichment` (`value_best`) | `value_best` |
| **T2 Categorical-single (Attribute)** | one canonical enum value | `hard_winner` by trust order | **`crop_attribute` (NEW)** — `value_canonical` + provenance | `value_canonical` |
| **T3 List (Attribute)** | ordered/set of canonical tokens | `hard_winner` by trust (best source's full list) | **`crop_attribute` (NEW)** — `value_list` (jsonb) | `value_list` |
| **T4 Computed (Derived)** | function of T1/T2 facts | n/a — **never stored** | none (calculator/view) | compute on read |
| **T5 Identity / relational** | crop/variety identity & taxonomy | single authored value | `crops` / `crop_varieties` / `crop_families` columns | column |
| **T6 Provenance** | per-fact audit (source, confidence, min/max) | produced by reconciliation | inside T1/T2/T3 rows | drill-down |

**Layer-ownership rule (binding):** a concept is stored in exactly **one** layer per its type. T1→enrichment, T2/T3→`crop_attribute`, T5→columns. **No concept is the source of truth in two layers.** Existing `crop_varieties` columns that duplicate a T1/T2 fact become **read-cache only or are dropped** (§8 migration) — never an independent SSoT.

---

## 4. The uniform Attributes layer (NEW — team_00 approved)

Categoricals and lists get the **same** one-winning-value + provenance treatment as numerics, via a new table parallel to `crop_field_enrichment`:

```
crop_attribute
  id                bigint PK
  variety_id        bigint FK → crop_varieties
  attribute_name    varchar   -- canonical T2/T3 field name
  value_canonical   varchar   -- T2: one canonical enum token
  value_list        jsonb     -- T3: ordered array of canonical tokens
  winning_source_class varchar -- EX|NI|PR|WR|OP|MK|WB|UC
  confidence_score  numeric(5,4)
  source_count      int
  candidates        jsonb     -- {source: value} audit (provenance/drill-down)
  computed_at       timestamptz
  UNIQUE(variety_id, attribute_name)
```

- Resolution: `hard_winner` by the field's trust order (EX>NI>PR>WR>OP>…), mapping raw source values through the **canonical-enum map** (§6.3) before selecting — so `direct_sow`→`direct_seed`, `semi_hardy`→`half_hardy` *before* a winner is chosen.
- This mirrors `crop_field_enrichment` so the UI/consumers read **one uniform shape** for every datum: `value` + `winning_source_class` + `confidence_score`. (Implements the existing 8-class `source_registry` for categoricals too.)

---

## 5. Granularity — crop baseline + variety override (formalized)

- Each crop has exactly one **default variety** (`is_default=true`, 70/70 today) carrying the crop-level baseline for every field.
- Specific varieties override **only** the fields that genuinely differ (e.g. DTM, name); unspecified fields inherit the default-variety value at read time.
- Consumers resolve: *variety value if present, else default-variety value*. This is already the de-facto pattern (patch03 delta-vs-default) — the canon makes it the rule.

---

## 6. Canonical vocabularies

### 6.1 Unit registry (one string per dimension — SSoT)
| Dimension | Canonical unit | Kills (migrate from) |
|-----------|----------------|----------------------|
| temperature | `°C` | `celsius`, `C` |
| duration (days) | `days` | — |
| duration (weeks) | `weeks` | — |
| length | `cm` | — |
| yield (per bed-m) | `kg_per_bed_m` | `kg/m` |
| nutrient load | `kg_per_ha` | `kg/ha` |
| price | `ILS_per_<unit>` | `ILS/kg`, `ILS/bunch`, `ILS/unit` (qualifier kept) |
| ratio/percent | `pct` | `%` |
| acidity | `pH` | — |
| seed density | `seeds_per_g` | `seeds/g` |
| count | `count` | — |

A field's unit lives in a **units registry** keyed by canonical field name — units are **not** re-spelled per row. `source_values.unit` free-text is normalized to the registry on import.

### 6.2 Naming convention
`<concept>[_<qualifier>][_<unit-suffix-only-when-it-disambiguates>]`, snake_case, no `avg_`/`default_` prefixes (averaging is a reconciliation detail, not part of the name). Examples: `yield_per_bed_m`, `spacing_in_row_cm`, `days_to_maturity`, `days_in_nursery`. Renames are aliased during migration to avoid breaking consumers (§8).

### 6.3 Canonical enums (T2/T3)
| Attribute | Canonical tokens | Collapse (from) |
|-----------|------------------|-----------------|
| `planting_method` | `direct_seed`, `transplant`, `seed_tuber`, `slip`, `cutting` | `direct_sow`→`direct_seed` |
| `frost_tolerance_class` | `hardy`, `half_hardy`, `tender`, `very_tender` | `semi_hardy`→`half_hardy` |
| `growth_cycle` | `annual`, `biennial`, `perennial` | (null allowed) |
| `category` | `vegetables`, `herbs`, `fruits`, `fruit_trees` | — |
| month-lists (`sowing_months`, `transplant_months`) | array of ints 1–12 | CSV `"2,3,5"`→`[2,3,5]` |

### 6.4 Yield & nutrients (team_00 decisions)
- **Yield canonical = `yield_per_bed_m`** (kg per linear bed-meter; JM/farm-native). `yield_per_m2` is **derived** (`= yield_per_bed_m / bed_width_m`, bed_width=0.8). Drop `yield_per_m2_kg` as a stored fact.
- **Nutrients canonical = elemental** `nutrient_removal_{n,p,k,ca,mg}_kg_per_ha`. Oxide forms `p2o5`/`k2o` are **derived** (×2.29 / ×1.205). Drop oxide stored facts.

---

## 7. Canonical field registry (current → canonical disposition)

Disposition: **KEEP** · **RENAME** · **DERIVE** (compute, stop storing) · **→ATTR** (move to attributes layer) · **DEPRECATE-COL** (column is no longer SSoT) · **DQ** (data-quality fix).

### 7.1 Reconciled-numeric facts (T1 → enrichment)
| Current field | Canonical | Disposition |
|---|---|---|
| days_to_maturity | days_to_maturity | KEEP |
| harvest_window_max_days | harvest_window_max_days | KEEP (min unused → drop from mandatory) |
| in_row_spacing_cm | spacing_in_row_cm | RENAME (alias) |
| rows_per_bed | rows_per_bed | KEEP |
| avg_yield_per_bed_m | yield_per_bed_m | RENAME |
| yield_per_m2_kg | — | DERIVE (drop stored) |
| documented_price (+unit) | price_documented (+unit qualifier) | RENAME |
| seeds_per_gram | seeds_per_g | RENAME |
| nutrient_removal_{n,p,k,ca,mg}_kg_ha | nutrient_removal_{…}_kg_per_ha | RENAME |
| nutrient_removal_{p2o5,k2o}_kg_ha | — | DERIVE (drop stored) |
| germination_temp_c_{min,opt,max} | germination_temp_{min,opt,max}_c | KEEP (unit-normalize °C) |
| soil_ph_target, soil_ph_liming_threshold | KEEP | unit `pH` |
| storage_temp_c_{min,max}, storage_rh_pct_{min,max}, storage_life_days | KEEP | unit-normalize |
| days_in_gh_total | **days_in_nursery** | RENAME (this is the nursery-duration field; calculators use it) |
| days_to_first_potting, days_to_germinate_gh | nursery_days_to_potting, nursery_days_to_germinate | KEEP (define the nursery phase trio relationship) |
| succession_interval_weeks | succession_interval_weeks | KEEP |
| plants_per_m2 | — | DERIVE (drop stored — function of rows/spacing/bed_width) |
| avg_revenue_per_bed_m | — | DERIVE (yield×price) |

### 7.2 Categorical / list attributes (T2/T3 → crop_attribute)
| Current (source_values) | Canonical | Type | Disposition |
|---|---|---|---|
| planting_method | planting_method | T2 | →ATTR + enum collapse |
| frost_tolerance_class | frost_tolerance_class | T2 | →ATTR + enum collapse |
| planting_season (column) | season_window | T2/T3 | →ATTR (currently column-only, unenriched) |
| seed_months_list | sowing_months | T3 | →ATTR (CSV→int array) |
| transplant_months_list | transplant_months | T3 | →ATTR |
| storage_ethylene_sensitivity | storage_ethylene_sensitivity | T2 | →ATTR |
| storage_life_text | — | — | DERIVE/DROP (use numeric storage_life_days) |
| variety_provider | variety_provider | T2 | →ATTR |
| rootstock_variety | rootstock_variety | T2 | →ATTR |
| harvest_unit / harvest_stage (column) | harvest_unit, harvest_stage | T2 | →ATTR (or KEEP as identity if 1:1 crop) |

### 7.3 Identity (T5 → columns, KEEP)
`name_he`, `name_en`, `scientific_name`, `family_id`, `category`, `growth_cycle`, `harvest_unit_default`, `first_fruit_year`, `is_grafted`, `oma_product_id`, `icon_url`, variety `name_he/name_en/is_default`. **DQ:** purge duration text leaked into variety `name_he` (D8).

### 7.4 Deprecated as SSoT (T1/T2 facts duplicated on columns)
`crop_varieties` columns that now defer to enrichment/attributes: `days_to_maturity`, `in_row_spacing_cm`, `rows_per_bed`, `avg_yield_per_bed_m`, `documented_price*`, `planting_method`, `planting_season`, `succession_interval_weeks`, `days_in_gh_total`, etc. → **DEPRECATE-COL** (kept as nullable read-cache, clearly flagged; never written as authority). Seeder fields (`seeder*`) → identity/ops, keep.

---

## 8. Migration plan (phased; data-only where possible)

1. **Unit normalize** — map `celsius`/`C`→`°C`, `kg/ha`→`kg_per_ha`, etc. across `source_values.unit` + the units registry. (Reversible; no value change.)
2. **Enum canonicalize** — collapse `direct_sow→direct_seed`, `semi_hardy→half_hardy`; CSV→int arrays. Build the canonical-enum map module.
3. **Attributes layer** — add `crop_attribute` table (1 migration) + an attribute resolver (mirrors enrichment_runner, `hard_winner`) + ingest of the §7.2 categoricals.
4. **Dedup → derive** — stop storing `yield_per_m2_kg`, oxide nutrients, `plants_per_m2`, `avg_revenue_per_bed_m`; provide computed accessors.
5. **Rename + alias** — apply §6.2 names; keep read aliases for one cycle so consumers migrate without breakage.
6. **Deprecate columns** — flag duplicated `crop_varieties` columns as read-cache only.
7. **Data-quality pass** — purge identity pollution (D8); validate nursery-phase trio consistency; outlier re-check.
8. **Re-enrich + snapshot** — run enrichment + attribute resolver; regenerate the coverage snapshot (Gap-Fill §4) against the canonical vocabulary.

Each phase is independently testable; phases 1–2 are pure data normalization (low risk), 3–4 add the structural model, 5–6 are consumer-facing (aliased).

---

## 9. Future-vision namespace (extensibility without schema churn)

Future modules add **typed fields under reserved namespaces** into the *same* layers — no per-module tables:

| Module | Namespace (field prefix) | Type / layer | Example future fields |
|--------|--------------------------|--------------|------------------------|
| Planner (CB-2) | `plan_` | T1 facts / computed | `plan_bed_width_m`, `plan_rotation_group` |
| Tasks (CB-3) | `task_` | crop_task_templates (exists) | timing anchors from calcs #4/#5 |
| Sales/POS (CB-4) | `sale_` | T1 facts / computed | `sale_channel`, `sale_pack_size` |
| Tend (CB-5) | `op_` | T1 facts via OP-class source | operational yields/prices feed enrichment as OP |

Rule: a new module **never** invents a new storage shape — it registers fields of types T1–T5 with canonical names+units+enums, and the existing enrichment/attribute/computed machinery serves them. This is the structural guarantee that the model "serves the big future vision."

---

## 10. Consumer access contract (uniform)

Every consumer (current UI, calculators, future modules) reads through **one** uniform shape:
- **Fact (T1):** `crop_field_enrichment(variety, name).value_best` (+ confidence, class).
- **Attribute (T2/T3):** `crop_attribute(variety, name).value_canonical | value_list` (+ confidence, class).
- **Computed (T4):** a calculator/view function over facts — never a stored read.
- **Identity (T5):** the column.
- Variety value, else default-variety value (§5).
- `field_state` (VALIDATED/UNVALIDATED/MISSING, τ) computes identically for facts and attributes.

This contract is what WP-CB-1's LOD400 field layer will be corrected to, and what CB-2..CB-5 build against.

---

## 11. Impact on WP-CB-1 (calculator backend)
- The committed backend math (14 pure functions, 92 tests) is **unaffected** — it operates on values, not storage.
- The **field mapping** (`calculator_meta`, ingest whitelist, `CalcUnavailable` names) is corrected to the canon: `days_in_gh_total`→`days_in_nursery`; categoricals (`planting_method`, `planting_season`/`season_window`, `frost_tolerance_class`) read from `crop_attribute`; yield = `yield_per_bed_m`.
- This supersedes `FINDINGS_field_mapping_reconciliation_v1.0.0.md` — that fix is now part of the canon migration, not a standalone patch.

---

## 12. Acceptance (for the canon's migration WP, after approval)
- All `source_values.unit` ∈ the unit registry; zero `celsius`/`C` rows.
- All T2 values ∈ canonical enums; zero `direct_sow`/`semi_hardy`.
- `crop_attribute` populated for the §7.2 set with provenance; calculators #4/#5/#6/#11 enable on crops that have the data.
- No stored `yield_per_m2_kg` / oxide / `plants_per_m2` / `avg_revenue` (computed accessors instead).
- Variety `name_he` free of duration pollution.
- Coverage snapshot regenerated; COMPLETE/PARTIAL split reported against the canon.
- `validate_aos.sh` 0 FAIL; full crop_book suite green.

---

## 13. Open questions for team_00
1. **Bed width** for yield_per_m2 derivation confirmed **0.8 m** (matches AssumptionField) — OK to hard-link the derivation to that AssumptionField?
2. **Column deprecation** — OK to treat duplicated `crop_varieties` columns as read-cache (not drop them physically this round) to minimize risk?
3. **Nursery phase trio** — confirm semantics so calculators use the right one: `days_to_germinate` (sow→emerge) → `days_to_potting` (→ pot-up) → `days_in_nursery` total (sow→field). Is `days_in_nursery` = sow→field-transplant the value calculators #3/#4/#5 should use? (We mapped it to the renamed `days_in_gh_total`.)

---

*Author team_100. On approval: open a Migration WP (the §8 phases) and correct WP-CB-1's LOD400 field layer to this canon. Build of new calculators/UI stays PAUSED until the canon is approved (team_00 directive).*
