---
id: VERDICT_SFA-S003-P004_TARGET_A_CANON_L-GATE_S_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-30
type: validation_verdict
wp: SFA-S003-P004-WP-CB-0
gate: L-GATE_S
target: A (Canon L-GATE_S)
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS_WITH_FINDINGS
checks: 11/11 passed
---

# Target A Verdict — Crop Data Model Canon — L-GATE_S

```yaml
target: A (Canon L-GATE_S)
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS_WITH_FINDINGS
checks: 11/11 passed
findings:
  - id: F-190-CB0-01
    severity: MAJOR
    summary: "Some T2 attributes are dispositioned to crop_attribute without complete canonical enum/open-vocabulary policy."
    location: "_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md:127"
    remediation: "Add canonical token tables or explicit open-vocab treatment for storage_ethylene_sensitivity, variety_provider, rootstock_variety, and harvest_unit/harvest_stage before the migration WP executes."
  - id: F-190-CB0-02
    severity: MINOR
    summary: "Live seeder_roller_plate is covered only by a wildcard seeder* note, not an explicit registry row."
    location: "_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md:185"
    remediation: "Add an explicit seeder_roller_plate row to §7 with canonical field/layer/disposition so a junior builder does not have to infer it."
  - id: F-190-CB0-03
    severity: MINOR
    summary: "Unit normalization rules need explicit treatment for live unit variants beyond the named examples."
    location: "_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md:107"
    remediation: "Add rows or migration-map examples for rows_per_bed unit 'rows' and blank, soil pH blank, and yield_per_m2 unit 'kg/m2'."
summary: "The canon is architecturally sound and safe to advance, with refinements needed before the migration WP starts. The six-type taxonomy, ownership rule, attribute layer, compute-don't-store posture, yield/nutrient math, team_00 decisions, and migration order are coherent. The findings are precision gaps, not design blockers."
```

## Evidence

### Live DB Inventory

Commands run:

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select field_name,count(*) from crop_field_enrichment group by 1 order by 1"

docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct field_name from crop_variety_source_values order by 1"
```

Observed enriched fields include 29 names: `avg_yield_per_bed_m`, `days_in_gh_total`, `days_to_first_potting`, `days_to_maturity`, `documented_price`, germination temp trio, `harvest_window_max_days`, `in_row_spacing_cm`, nutrient elemental and oxide fields, `plants_per_m2`, `rows_per_bed`, `seeds_per_gram`, soil pH fields, storage fields, `succession_interval_weeks`, and `yield_per_m2_kg`.

Observed source-value fields include the enriched set plus `frost_tolerance_class`, `planting_method`, `rootstock_variety`, `seed_months_list`, `seeder_roller_plate`, `storage_ethylene_sensitivity`, `storage_life_text`, `transplant_months_list`, and `variety_provider`.

### Canon Checklist

| # | Check | Result | Evidence |
|---|---:|---|---|
| 1 | Taxonomy coherence | PASS | T1/T2/T3/T4/T5/T6 are mutually separable by storage/reconciliation/access path; computed values are not stored; provenance is modeled alongside facts/attributes. |
| 2 | Layer ownership | PASS | §3 and §7 enforce T1→enrichment, T2/T3→`crop_attribute`, T4→computed, T5→columns. Physical duplicate columns are sequenced to DROP last. |
| 3 | Registry correctness vs live DB | PASS_WITH_FINDINGS | Every live field has a disposition, but `seeder_roller_plate` should be explicit rather than inferred from `seeder*`. |
| 4 | Units + enums | PASS_WITH_FINDINGS | Required collapses `celsius`/`C`→`°C`, `direct_sow`→`direct_seed`, `semi_hardy`→`half_hardy` are present and match live values. Additional live unit variants and T2 tokens need explicit policy. |
| 5 | `crop_attribute` design | PASS | Table mirrors `crop_field_enrichment`, carries provenance/confidence/source count/candidates, and resolves after enum canonicalization, which is the correct order. |
| 6 | Yield/nutrients arithmetic | PASS | `yield_per_m2 = yield_per_bed_m / bed_width_m`; with bed width 0.8 this is per-bed-m / 0.8. Oxide conversions are correct: P2O5 = P x 2.29; K2O = K x 1.205. |
| 7 | Compute-don't-store | PASS | `plants_per_m2`, `avg_revenue_per_bed_m`, `yield_per_m2_kg`, and oxide nutrients are DERIVE/drop-stored. |
| 8 | Migration safety | PASS | The column DROP is phase 6, after unit/enum normalize, attributes, derivation stop, and rename+alias cycle. Consumers cut over before any physical DROP. |
| 9 | Future namespace | PASS | `plan_`, `task_`, `sale_`, and `op_` namespaces extend the same typed layers and avoid per-module table churn, with `crop_task_templates` acknowledged as the existing task layer. |
| 10 | team_00 decisions | PASS | Bed width assumption, physical DROP last, and nursery semantics are explicitly embedded in §6.4, §7.4/§8, and §13. |
| 11 | Precision gate | PASS_WITH_FINDINGS | A junior builder can execute the phase order, but the findings above should be tightened before implementation to remove guessing around open-vocab attributes and unit variants. |

### Architecture Context

`documentation/02-architecture/sfa-delivery-tier.md` §1A is consistent with §0/§1. It clarifies development/background/production roles and per-dataset SSoT without changing the production serving path: uPress serves end-user HTTP, waldhomeserver runs background jobs/deploy relay, and Mac can publish curated crop-book data via HTTPS ingest.

## Final Decision

**PASS_WITH_FINDINGS.**

No blocker, contradiction, registry gap that would lose data, or unsafe migration order was found. The canon may advance, provided the migration WP incorporates the precision findings before executing schema/data changes.
