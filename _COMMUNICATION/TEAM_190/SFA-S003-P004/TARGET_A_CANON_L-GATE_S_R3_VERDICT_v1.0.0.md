---
id: VERDICT_SFA-S003-P004_TARGET_A_CANON_L-GATE_S_R3_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-31
type: validation_verdict
wp: SFA-S003-P004-WP-CB-0
gate: L-GATE_S
target: A (Canon L-GATE_S) — Round 3
round: 3
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
artifact_version: v1.2.0
validator_engine: Cursor Composer (non-Claude)
r2_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_R2_VERDICT_v1.0.0.md
commit_validated: d16a611
result: PASS
---

# Target A Verdict — Crop Data Model Canon — L-GATE_S Round 3

```yaml
target: A (Canon L-GATE_S) — Round 3
validator_engine: Cursor Composer (non-Claude)
result: PASS
errata_recheck:
  - id: F-190-CB0-01
    status: RESOLVED
    note: "Canon v1.2.0 §6.3 collapse includes half-hardy→half_hardy alongside semi_hardy→half_hardy. Live frost_tolerance_class values {half-hardy, hardy, semi_hardy, tender, very_tender} all map to {hardy, half_hardy, tender, very_tender}."
  - id: F-190-CB0-03
    status: RESOLVED
    note: "Canon v1.2.0 §6.1 variant map lists kg (63 rows) and kg/m for yield_per_bed_m → kg_per_bed_m. Live avg_yield_per_bed_m has sole distinct unit kg; maps to kg_per_bed_m."
other_stranded_variants_found: none
summary: "Round 3 confirms both R2 errata are correctly and completely applied in Canon v1.2.0. Independent live-DB gates for Errata A (half-hardy collapse) and Errata B (bare kg on yield) pass. Optional full enum + unit sweep finds no additional stranded values beyond the two already fixed. F-190-CB0-02 (seeder_roller_plate) was RESOLVED in R2 and is not re-opened. Canon is eligible to LOCK (LOD200_LOCKED); team_100 may open the Migration WP."
```

## Scope executed

Ultra-narrow R3 per team_100 mandate (2026-05-31): re-check **only** F-190-CB0-01 and F-190-CB0-03 errata. No R1 base checks; no Target B; F-190-CB0-02 not re-opened.

**Canon read:** v1.2.0 — §6.1 line 133 (`kg`→`kg_per_bed_m`), §6.3 line 149 (`half-hardy`→`half_hardy`), §12 zero-assertions, §14 remediation matrix.

## Errata A — F-190-CB0-01 (`half-hardy` collapse)

**Canon §6.3:**

```text
frost_tolerance_class | hardy, half_hardy, tender, very_tender | semi_hardy→half_hardy, half-hardy→half_hardy
```

**Command:**

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct value_text from crop_variety_source_values where field_name='frost_tolerance_class'"
```

**Live:** `half-hardy`, `hardy`, `semi_hardy`, `tender`, `very_tender`

| live | canonical via §6.3 |
|------|-------------------|
| half-hardy | half_hardy (collapse) |
| semi_hardy | half_hardy (collapse) |
| hardy | hardy |
| tender | tender |
| very_tender | very_tender |

**Gate:** PASS

## Errata B — F-190-CB0-03 (bare `kg` on yield)

**Canon §6.1 variant map:**

```text
yield_per_bed_m (from avg_yield_per_bed_m) | kg (live, 63 rows), kg/m | kg_per_bed_m
```

**Command:**

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select distinct coalesce(unit,'(NULL)') from crop_variety_source_values where field_name='avg_yield_per_bed_m'"
```

**Live:** `kg` only (63 rows; no other unit on this field).

**Gate:** PASS (`kg` → `kg_per_bed_m`)

Cross-check: all 63 `unit='kg'` rows are on `avg_yield_per_bed_m` only (no other field uses bare `kg`).

## Belt-and-suspenders — full enum + unit sweep

**All distinct units** (2061 source_values rows):

| unit | count | §6.1 target |
|------|------:|-------------|
| days | 521 | `days` |
| (NULL) | 451 | field registry default |
| kg/ha | 201 | `kg_per_ha` |
| °C | 184 | `°C` |
| cm | 124 | `cm` |
| % | 82 | `pct` |
| pH | 82 | `pH` |
| kg | 63 | `kg_per_bed_m` (yield field only) |
| celsius | 60 | `°C` |
| count | 54 | `count` |
| seeds/g | 50 | `seeds_per_g` |
| ILS/unit | 48 | `ILS_per_<unit>` |
| C | 43 | `°C` |
| kg/m2 | 34 | derived / `kg_per_m2` |
| weeks | 19 | `weeks` |
| ILS/kg | 19 | `ILS_per_<unit>` |
| rows | 19 | `count` |
| ILS/bunch | 7 | `ILS_per_<unit>` |

**Closed-enum fields:**

| field | live values | all map? |
|-------|-------------|----------|
| planting_method | direct_seed, direct_sow, seed_tuber, slip, transplant | yes (`direct_sow`→`direct_seed`) |
| frost_tolerance_class | (above) | yes |
| storage_ethylene_sensitivity | high, low, medium | yes ⊆ {none, low, medium, high} |

**other_stranded_variants_found:** none

## Final decision

**PASS** — both R2 errata **RESOLVED**; no new stranded variants.

**Disposition:** Canon **LOCKS** for LOD200 (team_100: set `LOD200_LOCKED`, open Migration WP per mandate).

— team_190
