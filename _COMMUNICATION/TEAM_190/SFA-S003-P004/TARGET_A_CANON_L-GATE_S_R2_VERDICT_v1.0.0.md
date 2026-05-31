---
id: VERDICT_SFA-S003-P004_TARGET_A_CANON_L-GATE_S_R2_v1.0.0
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
target: A (Canon L-GATE_S) — Round 2
round: 2
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
artifact_version: v1.1.0
validator_engine: Cursor Composer (non-Claude)
r1_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_VERDICT_v1.0.0.md
result: PASS_WITH_FINDINGS
---

# Target A Verdict — Crop Data Model Canon — L-GATE_S Round 2

```yaml
target: A (Canon L-GATE_S) — Round 2
validator_engine: Cursor Composer (non-Claude)
result: PASS_WITH_FINDINGS
findings_recheck:
  - id: F-190-CB0-01
    status: INSUFFICIENT
    note: "§6.3a satisfies R1 (every T2/T3 attribute has CLOSED-ENUM / OPEN-VOCAB / LIST policy, reject/DQ rule, open-vocab trim/case/dedup). Independent live-value gate fails: frost_tolerance_class live token half-hardy (1 row) is neither a canonical token (half_hardy) nor covered by §6.3 collapse (only semi_hardy→half_hardy). D6 documents half-hardy chaos but remediation did not add the collapse row. planting_method and storage_ethylene_sensitivity pass (direct_sow→direct_seed; high/low/medium ∈ closed set)."
  - id: F-190-CB0-02
    status: RESOLVED
    note: "§7.3a explicit registry row: seeder_roller_plate | T5 | KEEP (column) SSoT; source_values residue → DQ-drop. No seeder* wildcard inference required. Live DB: 7 rows in crop_variety_source_values (blank unit; machine config strings)."
  - id: F-190-CB0-03
    status: INSUFFICIENT
    note: "§6.1 variant map covers mandate examples (rows/NULL→count, pH blank→pH, kg/m2→derived, °C/celsius/C, kg/ha, seeds/g, ILS/*, %). Independent unit inventory fails on bare kg: 63 rows on avg_yield_per_bed_m use unit=kg; map lists only kg/m→kg_per_bed_m for yield_per_bed_m, not kg. (null) 451 rows covered by §6.1 field-default rule."
summary: "Round 2 confirms the three inline remediations materially address R1 precision gaps (§6.3a policy table, §7.3a seeder row, §6.1 live-variant map). F-190-CB0-02 is complete. F-190-CB0-01 and F-190-CB0-03 fail the mandated independent live-DB gates on two residual variants (half-hardy, kg) that §1/D6 already imply but §6.3/§6.1 do not yet spell. No architectural regression vs R1; Canon lock and Migration WP should wait for a short §6.3/§6.1 errata (R3 re-check) — not a redesign."
```

## Scope executed

- **In scope:** R2 re-check of F-190-CB0-01, F-190-CB0-02, F-190-CB0-03 only (per team_100 mandate `VALIDATION_MANDATE_team190_R2_2026-05-30_v1.0.0.md`).
- **Out of scope:** R1 11/11 base checks; Target B backend (unchanged).

**Canon artifact read:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` v1.1.0 (§6.1, §6.3, §6.3a, §7.3a, §14). Workspace HEAD at validation time: `0f333e6` (mandate cited `3cd5643`; canon content reviewed at path above).

## Evidence — independent DB checks (oma-postgres)

### F-190-CB0-01 — closed-enum live values

```bash
for f in planting_method frost_tolerance_class storage_ethylene_sensitivity; do
  echo "== $f =="; docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
    "select distinct value_text from crop_variety_source_values where field_name='$f'"; done
```

| field | live distinct values | maps via canon? |
|-------|---------------------|-----------------|
| planting_method | direct_seed, direct_sow, seed_tuber, slip, transplant | direct_sow→direct_seed (§6.3); others ∈ set |
| frost_tolerance_class | half-hardy, hardy, semi_hardy, tender, very_tender | semi_hardy→half_hardy; hardy/tender/very_tender ∈ set; **half-hardy stranded** |
| storage_ethylene_sensitivity | high, low, medium | ⊆ {none, low, medium, high} |

Row counts (`frost_tolerance_class`): half-hardy=1, semi_hardy=13, hardy=29, tender=23, very_tender=14.

### F-190-CB0-02 — seeder_roller_plate

§7.3a row present (lines 222–230). Live residue:

```text
seeder_roller_plate|roller:F24:plate:none||2
seeder_roller_plate|roller:X24:plate:none||2
seeder_roller_plate|roller:XY24:plate:none||1
seeder_roller_plate|roller:YYJ24:plate:none||2
```

(7 rows total; disposition DQ-drop per canon.)

### F-190-CB0-03 — live units

```bash
docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
  "select coalesce(unit,'(null)'), count(*) from crop_variety_source_values group by 1 order by 2 desc"
```

| live unit | count | §6.1 resolution |
|-----------|------:|-----------------|
| days | 521 | registry `days` |
| (null) | 451 | field registry default (§6.1 rule) |
| kg/ha | 201 | `kg_per_ha` |
| °C / celsius / C | 184+60+43 | `°C` |
| cm | 124 | `cm` |
| % | 82 | `pct` |
| pH | 82 | `pH` |
| **kg** | **63** | **not in variant map** (only `kg/m` listed for yield_per_bed_m) |
| count / seeds/g / ILS/* / kg/m2 / weeks / rows | … | mapped per §6.1 table |

`kg` appears only on `avg_yield_per_bed_m` (63 rows).

## Per-finding structural review (canon text)

| ID | R1 ask | v1.1.0 section | Structural fix | Live gate |
|----|--------|----------------|----------------|-----------|
| F-190-CB0-01 | Complete T2 enum/open-vocab policy | §6.3a | **Yes** — 10 attributes, kinds, rules | **No** — `half-hardy` |
| F-190-CB0-02 | Explicit `seeder_roller_plate` row | §7.3a | **Yes** | **Yes** |
| F-190-CB0-03 | Explicit live unit variants | §6.1 map | **Partial** — R1 examples covered | **No** — bare `kg` |

## Required team_100 errata before R3 / Canon lock

1. **§6.3** — add collapse `half-hardy`→`half_hardy` (and align §8.2 / §12 acceptance with zero `half-hardy` post-migration, alongside `semi_hardy`).
2. **§6.1 variant map** — add row for `avg_yield_per_bed_m` / `yield_per_bed_m`: live unit `kg` → `kg_per_bed_m` (63 rows today).

## Final decision

**PASS_WITH_FINDINGS** — remediations are directionally correct; **Canon does not LOCK** until both live-value gaps are inlined and R3 (or team_00 waiver) closes the loop.

— team_190
