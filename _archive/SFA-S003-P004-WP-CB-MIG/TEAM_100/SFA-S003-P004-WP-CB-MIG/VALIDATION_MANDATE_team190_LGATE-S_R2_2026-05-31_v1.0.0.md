# VALIDATION MANDATE (L-GATE_S ROUND 2) — SFA-S003-P004-WP-CB-MIG — team_100 → team_190 — v1.0.0

**Date:** 2026-05-31 · **From:** team_100 (Claude Opus) · **To:** team_190 · **Routed by:** team_00
**Repo:** `main` · HEAD `<this commit>` · **Round:** 2 · **R1 verdict:** `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG/WP-CB-MIG_LGATE-S_VERDICT_v1.0.0.md`

## 0. Cross-engine (IR#1/#5)
Migration will be built by Claude Sonnet → **non-Claude only** (Cursor/GPT-5/Codex). Confirm engine.

## 1. Why R2 (narrow)
R1 = PASS_WITH_FINDINGS (10/10; faithfulness/safety/constraints all PASS). 5 findings FIXED inline in **LOD400 v0.2.0** (§7 matrix). team_00 wants the fixes **cross-engine-confirmed**, not self-certified. Re-check **only** the 5 remediations; do **not** re-run the 10 base checks unless a fix introduced a regression.

**Artifact:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md` (v0.2.0). **Against:** Canon LOD200_LOCKED v1.2.0.

## 2. Re-check the 5 fixes
1. **F-190-MIG-01** (§3 Phase 3 / AC-04): confirm explicit candidate ORIGIN per attribute (source_values vs column-origin), `harvest_unit`+`harvest_stage` now in the resolver set + AC-04, and all **11** §7.2 attributes covered with both origins tested. RESOLVED?
2. **F-190-MIG-02** (§3 Phase 7 / AC-09): confirm `storage_life_text` is DROPPED with a zero-residual assertion + rollback, and `storage_life_days` is stated as sole read path. RESOLVED?
3. **F-190-MIG-03** (§3 Phase 5 + 7): confirm `days_to_first_potting→nursery_days_to_potting` and `days_to_germinate_gh→nursery_days_to_germinate` renames are in the FIELD_REGISTRY, and the Phase 7 trio assertion uses canonical names. Confirm this matches Canon §7.1 (no canon re-decision). RESOLVED?
4. **F-190-MIG-04** (§4 AC-03): confirm AC-03 is scoped to CLOSED-ENUM and adds an open-vocab (trim/case/dedup + provenance) assertion for `variety_provider`/`rootstock_variety` per Canon §6.3a. RESOLVED?
5. **F-190-MIG-05** (§5): confirm the "LAST" wording now means last destructive/schema phase (Phase 6), with 7/8 explicitly non-destructive. RESOLVED?

(Optional regression spot-check: the v0.2.0 edits did not contradict the locked canon or weaken phase-order safety.)

## 3. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG/WP-CB-MIG_LGATE-S_R2_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_S — Round 2
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS
findings_recheck:
  - id: F-190-MIG-01..05
    status: RESOLVED | INSUFFICIENT
regression_found: <none | …>
summary: <one paragraph>
```
- **PASS** (all 5 RESOLVED, no regression) → LOD400 LOCKS; team_10 begins the phase-by-phase build.
- Any INSUFFICIENT → list precisely; team_100 fixes + R3.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043).

---
*Self-contained R2 package for non-Claude execution.*
