---
id: VERDICT_SFA-S003-P004-WP-CB-MIG_L-GATE_S_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-31
type: validation_verdict
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_S
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md
artifact_version: v0.1.0
canon: _aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md
canon_version: v1.2.0
validator_engine: Codex / GPT-5 (non-Claude)
phase_owner: team_190
correction_cycle: R1
result: PASS_WITH_FINDINGS
---

# WP-CB-MIG L-GATE_S Verdict

```yaml
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_S
validator_engine: Codex / GPT-5 (non-Claude)
result: PASS_WITH_FINDINGS
checks: 10/10
findings:
  - id: F-190-MIG-01
    severity: MAJOR
    summary: "Phase 3's executable attribute population list omits Canon §7.2 harvest_unit/harvest_stage and does not explicitly describe column-origin reads for season_window/harvest_unit/harvest_stage."
    location: "LOD400 §3 Phase 3 / §4 AC-04; Canon §7.2"
    remediation: "Add explicit Phase 3 resolver inputs for column-origin attributes: planting_season→season_window, harvest_unit/harvest_stage→crop_attribute; include harvest_unit and harvest_stage in AC-04 and tests."
  - id: F-190-MIG-02
    severity: MAJOR
    summary: "Canon §7.2 storage_life_text is DERIVE/DROP, but no phase or AC explicitly removes or gates the stranded text field in favor of storage_life_days."
    location: "LOD400 §3 Phase 4/7 and §4 AC-05/AC-09; Canon §7.2"
    remediation: "Add storage_life_text to Phase 4 dedup or Phase 7 DQ with a zero-residual assertion and rollback note; state that numeric storage_life_days is the only read path."
  - id: F-190-MIG-03
    severity: MAJOR
    summary: "Nursery companion fields are not fully executable: Canon maps days_to_first_potting/days_to_germinate_gh to nursery_days_to_potting/nursery_days_to_germinate, but Phase 5 omits them and Phase 7 uses non-canonical names."
    location: "LOD400 §3 Phase 5/7; Canon §7.1"
    remediation: "Add explicit rename/alias handling for days_to_first_potting→nursery_days_to_potting and days_to_germinate_gh→nursery_days_to_germinate, or issue a canon erratum if KEEP means no rename; update the Phase 7 trio assertion to canonical names."
  - id: F-190-MIG-04
    severity: MINOR
    summary: "AC-03 says every T2 value must be in a canonical enum, which overstates the locked canon because variety_provider and rootstock_variety are open-vocab attributes."
    location: "LOD400 §4 AC-03; Canon §6.3a"
    remediation: "Scope AC-03 to CLOSED-ENUM T2/T3 attributes and add an assertion that open-vocab attributes are trim/whitespace/case-fold normalized with provenance."
  - id: F-190-MIG-05
    severity: INFO
    summary: "Phase 6 is described as LAST while phases 7 and 8 still follow; the safe interpretation is last destructive schema drop after Phase 5 cutover, not last numbered phase."
    location: "LOD400 §2/§3 Phase 6/§5; Canon §8.6-§8.8"
    remediation: "Clarify the wording as 'last destructive/schema phase' or move the drop to Phase 8 if team_100 intends literal last execution."
summary: "The migration spec is faithful to the locked canon in the core unit, enum, rename, derive, attribute, drop, and dev-only constraints, and it is safe enough to advance after team_100 dispositions. The remaining findings are precision/completeness gaps that a junior builder would otherwise have to infer: column-origin attributes, storage_life_text DERIVE/DROP, nursery companion field names, open-vocab AC wording, and one sequencing wording ambiguity. No finding identifies a canon re-decision, production touch, unsafe ungated drop, or loss-producing transform."
```

## Scope

Validated artifact: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md` v0.1.0.

Locked SSoT: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` v1.2.0, `LOD200_LOCKED`, commit reference `d16a611`.

Engine constraint satisfied: this verdict was issued by Codex / GPT-5, a non-Claude engine. No implementation was built.

## Check Results

| # | Check | Result | Notes |
|---:|-------|--------|-------|
| 1 | Canon faithfulness | PASS | Spot checks align: `avg_yield_per_bed_m→yield_per_bed_m`, `days_in_gh_total→days_in_nursery`, `half-hardy→half_hardy`, bare `kg→kg_per_bed_m`, elemental canonical / oxide derived, `direct_sow→direct_seed`. |
| 2 | Completeness | PASS_WITH_FINDINGS | Most §7 dispositions are phased, but `harvest_unit`/`harvest_stage`, `storage_life_text`, and nursery companion names need explicit handling. |
| 3 | Phase-order safety | PASS_WITH_INFO | Order 1→8 is binding, dumps precede 1/3/4/6, rewriting phases have `--dry-run` and rollback notes, and drop is gated after Phase 5 cutover. Clarify "LAST" wording. |
| 4 | `crop_attribute` design | PASS_WITH_FINDINGS | Table shape, uniqueness, provenance, SQLite variant, and resolver ordering match Canon §4. Column-origin attributes need explicit resolver inputs. |
| 5 | WP-CB-1 field-layer correction | PASS | AC-07 correctly moves calc #3/#4/#5 to `days_in_nursery`, #4/#5/#6/#11 categoricals to `crop_attribute`, and yield to `yield_per_bed_m`. |
| 6 | Derive-don't-store | PASS_WITH_FINDINGS | Per-m2, oxide, plants/m2, and revenue derivations are correct; per-m2-only conversion is present. Add `storage_life_text` DERIVE/DROP handling. |
| 7 | Constraints | PASS | `reconciler.py`/`enrichment_runner.py` are explicitly untouched; the only LOD500-lock exception is `models.py` for §7.4 drops; dev-only Mac `oma-postgres`, no server/uPress action. |
| 8 | Precision gate | PASS_WITH_FINDINGS | The spec is mostly executable, but the findings identify the places a junior builder would otherwise infer source columns or canonical names. |
| 9 | AC adequacy | PASS_WITH_FINDINGS | ACs cover all 8 phases and main invariants. AC-03 needs closed-enum/open-vocab precision; AC-04 needs the full §7.2 attribute set. |
| 10 | Risk coverage | PASS | R-01..R-05 cover data-loss, consumer break, per-m2-only conversion, SQLite parity, and production isolation. |

## Verdict

`PASS_WITH_FINDINGS`.

team_100 should disposition the five findings before routing to team_10. The findings are implementation-spec precision gaps, not blockers to the locked canon itself.

-- team_190
