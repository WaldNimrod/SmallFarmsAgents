# VALIDATION MANDATE + PROMPT (ROUND 2) — SFA-S003-P004-WP-CB-0 — team_100 → team_190 — v1.0.0

**Date:** 2026-05-30
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `main` · HEAD `3cd5643`
**Round:** **2** (re-check of inline remediations) · **References R1 verdict** `_COMMUNICATION/team_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_VERDICT_v1.0.0.md`

---

## 0. Cross-engine constraint (Iron Rule #1 / #5 — MANDATORY)
Builder = Claude Sonnet, architect = Claude Opus → **this re-validation MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm your engine in the verdict header. (Your R1 ran on Codex/GPT-5 — fine to reuse.)

## 1. Why Round 2
R1 returned **PASS_WITH_FINDINGS** (11/11 checks; 3 precision findings, no blockers) and pre-authorized advancing. team_00 has directed a **formal R2 re-check** so the 3 inline remediations are **independently confirmed** rather than team_100-self-certified. **This is the only open loop** before the Canon locks.

## 2. Scope (NARROW — re-check the 3 fixes only)
- **In scope:** confirm F-190-CB0-01, F-190-CB0-02, F-190-CB0-03 are correctly and completely resolved in **Canon v1.1.0**.
- **Out of scope:** the 11/11 base checks already PASSED R1 — do **not** re-run them unless a fix introduced a regression. **Target B (backend)** PASSED clean in R1 — **not** re-validated here.

**Artifact:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (v1.1.0, commit `3cd5643`). Remediation matrix: §14.

## 3. Per-finding re-check criteria

### F-190-CB0-01 (was MAJOR) — T2 enum/open-vocab policy → **§6.3a**
Confirm §6.3a now gives **every** T2/T3 attribute an explicit kind:
- CLOSED-ENUM attributes (`planting_method`, `frost_tolerance_class`, `growth_cycle`, `category`, `harvest_unit`, `harvest_stage`, `storage_ethylene_sensitivity`) each have a canonical token set, and a reject-or-DQ rule for out-of-set tokens.
- OPEN-VOCAB attributes (`variety_provider`, `rootstock_variety`) have an explicit normalization rule (trim/case/dedup) + still carry provenance.
- **Independent check:** for each closed-enum attribute, query live values and confirm every live value maps to a canonical token (none stranded):
  ```bash
  for f in planting_method frost_tolerance_class storage_ethylene_sensitivity; do
    echo "== $f =="; docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
      "select distinct value_text from crop_variety_source_values where field_name='$f'"; done
  ```
  PASS iff no live value falls outside the canon's tokens/collapse rules.

### F-190-CB0-02 (was MINOR) — seeder_roller_plate → **§7.3a**
Confirm §7.3a has an **explicit** registry row for `seeder_roller_plate` (canonical name, type T5, disposition KEEP-column, source_values residue → DQ-drop), not a `seeder*` wildcard. PASS iff a junior builder needs no inference.

### F-190-CB0-03 (was MINOR) — live unit-variant normalization → **§6.1**
Confirm §6.1's explicit variant map resolves **every** live `source_values.unit` value (incl. `rows`, blank/NULL, `kg/m2`, pH-blank). 
- **Independent check:**
  ```bash
  docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
    "select coalesce(unit,'(null)'), count(*) from crop_variety_source_values group by 1 order by 2 desc"
  ```
  PASS iff every distinct live unit (including NULL/blank) has a canonical target in §6.1.

## 4. Verdict format → write to `_COMMUNICATION/team_190/SFA-S003-P004/TARGET_A_CANON_L-GATE_S_R2_VERDICT_v1.0.0.md`
```yaml
target: A (Canon L-GATE_S) — Round 2
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
findings_recheck:
  - id: F-190-CB0-01
    status: RESOLVED | INSUFFICIENT
    note: ...
  - id: F-190-CB0-02
    status: RESOLVED | INSUFFICIENT
  - id: F-190-CB0-03
    status: RESOLVED | INSUFFICIENT
summary: <one paragraph>
```
- **PASS** (all 3 RESOLVED) → Canon LOCKS; team_100 opens the Migration WP.
- Any **INSUFFICIENT** → list precisely what's still missing; team_100 revises and re-routes R3.

Notify back via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---

*Self-contained R2 package for non-Claude execution. team_00: route to a non-Claude validator session.*
