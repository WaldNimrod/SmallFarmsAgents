# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-MIG2 (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-01
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/wp-cb-mig2-2026-06-01` (off `main` 8795b8a)
**Gate:** **L-GATE_S** (spec review) of WP-CB-MIG2 — Crop Data Model Expansion. **Pre-build** — review the LOD400 + Canon amendment for soundness, precision, and constitutional compliance. No live-DB execution (nothing built yet).

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
LOD400 author + future builder = Claude (team_100 / team_10 Sonnet). Therefore this L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm engine in the verdict header.

## 1. Context
team_00 approved the WP-CB-MIG2 characterization (אפיון) in-session 2026-06-01: FULL adoption of the team_35 gap-analysis — the 13-topic taxonomy + 7 field groups + `needs_summer_shade`, folding in F-CB1-UI-01 and the season_window data gap. The crop data layer is **LOCKED** (WP-CB-0 Canon v1.2.0, WP-CB-MIG LOD500); this WP is the chartered **Canon amendment** vehicle. Four characterization decisions were made by team_00 (D-MIG2-1..4, Canon §16).

## 2. Artifacts to review
- **LOD400 (this gate's subject):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md` (v1.0.0)
- **Canon amendment v1.3.0 (DRAFT, additive §15–§20):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md`
- **LOD200 direction:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD200_spec.md`
- **Origin gap-analysis:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/spec/OPEN_ISSUES.md`
- **Locked base Canon body (v1.2.0):** §1–§14 of the Canon file (must remain unchanged by the amendment).

## 3. Spec-review checklist — run each independently

### 3.1 Constitutional (all must PASS)
- **C1 — Amendment is additive.** The locked v1.2.0 body (§1–§14) is unchanged; v1.3.0 is appended (§15–§20). Verify via `git diff main -- <canon>` that only additions below the v1.2.0 closing line exist.
- **C2 — Layer-ownership preserved.** Every new field maps to exactly one layer per its type (T1→enrichment, T2/T3→crop_attribute, T5→column). No concept stored in two layers. Specifically: `sale_unit` is an alias to `harvest_unit` (NOT a second unit attribute); `seeder_model` aliases the `seeder` column (no duplicate). Confirm no D2-style duplicate-concept reintroduced.
- **C3 — No new tables / storage shapes** (Canon principle #6). New fields slot into existing enrichment / crop_attribute / columns. Only DDL is the `seeder_settings` column (migration 060). Confirm the spec adds no table.
- **C4 — Closed vs open vocab explicit** (§6.3a discipline). Each new T2/T3 attr is declared CLOSED-ENUM (`irrigation_type`, `root_depth_class`, `needs_summer_shade`) or OPEN-VOCAB (`common_pests`, `foliar_feeding_program`, `unit_size`). No attribute left ambiguous.
- **C5 — IR#4.** LOD400 mandates builder makes zero `_aos/roadmap.yaml` edits (AC-15). Confirm the AC exists.
- **C6 — Migration safety.** Migration 060 (`down_revision: 059`) is additive (nullable column), reversible, SQLite-compatible. No drop/rename of locked columns.

### 3.2 Precision / executability (junior-dev gate)
- **P1 — Every work item names the real file + mechanism** (verified paths in LOD400 §0). Spot-check: `attribute_resolver._SOURCE_VALUES_ATTRS`, `canon/enums.py` `ENUM_TOKENS`/`OPEN_VOCAB_ATTRS`, `field_policy.FIELD_POLICY`, `sfa_ingest_push.py:320`, `FieldRegistry.php`.
- **P2 — T1 fact discovery is pinned.** WI-5/AC-06 require the builder to confirm `enrichment_runner` reconciles the new field_names (policy-driven vs explicit list). Confirm this is an explicit AC, not an assumption.
- **P3 — Backfill provenance is honest.** §17 + WI-10 separate PR-parseable (`irrigation_type`, `drip_lines_per_bed`, `root_depth_class`, `harvest_weeks_span`, partial others) from NI-only (`needs_summer_shade`, `labor_rate_*`, `plantings_per_season`). Verify the spec does NOT claim PR can fill the narrative-only groups.
- **P4 — Console + NI importer are specified** (WI-11) with: per-gap records, best-effort defaults, clipboard-JSON export, NI-class ingest, idempotency, re-resolve. Confirm AC-12/AC-13 cover them.
- **P5 — F-CB1-UI-01 rename is complete.** WI-6/AC-07 rename all 4 keys (field_policy.py L57/63/68/77) and require a grep-clean of old keys. Confirm no consumer still imports an old key (the spec says `calculator_meta.py` already uses canonical — verify the claim is testable).
- **P6 — CROP_TOPICS parity.** WI-1/AC-02 require a Python `CROP_TOPICS` SSoT that the PHP `book_crop.php:257` array must match (parity test). Confirm the AC mandates the test.

### 3.3 Scope discipline
- **S1** — Out-of-scope items (§5) correctly excluded: labor-cost calculator, JS revenue fix (F-50-patch01-01), UI beyond proposed slots + מזיקים notes.
- **S2** — `needs_summer_shade` 4-token enum `{none, shade_30, shade_40, shade_50}` matches the team_00 ratification (30/40/50 + none).
- **S3** — The 16-AC matrix is sufficient to attest the amendment without gaps.

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/WP-CB-MIG2_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MIG2
gate: L-GATE_S
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
constitutional_checks: <n/6>
precision_checks: <n/6>
scope_checks: <n/3>
findings:
  - id: F-190-MIG2-S-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: ...
    disposition: <fix-inline | builder-acknowledge | R2>
authorize_build: true | false
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS (build-authorized)** → team_100 addresses any MAJOR/MINOR inline, then dispatches team_10 L-GATE_B build.
- **BLOCKED** → team_100 revises LOD400 and routes R2.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---
*Self-contained L-GATE_S package for non-Claude execution. team_00: route to a non-Claude validator. This is a SPEC review — no build exists yet; do not attempt live-DB checks.*
