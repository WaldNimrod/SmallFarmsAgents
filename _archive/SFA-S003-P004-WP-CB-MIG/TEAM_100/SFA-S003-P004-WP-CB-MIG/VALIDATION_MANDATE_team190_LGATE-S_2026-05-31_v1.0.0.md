# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-MIG (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-05-31
**From:** team_100 (Chief System Architect, Claude Opus) · **To:** team_190 · **Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · `main` · HEAD `38e504b`
**Gate:** **L-GATE_S** (spec validation) of the Migration LOD400, **before any build**.

---

## 0. Cross-engine constraint (Iron Rule #1 / #5 — MANDATORY)
The migration will be **built by Claude Sonnet** (team_10). Therefore this L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex — your prior rounds used these). Confirm engine in the verdict header. A Claude engine cannot issue this verdict.

## 1. What you are validating
- **Artifact:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG/LOD400_spec.md` (v0.1.0).
- **Against (SSoT, LOCKED):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (v1.2.0, LOD200_LOCKED @ d16a611) — §6 vocab, §7 registry, §8 phases, §14 errata.
- **Gate question:** is this migration spec **faithful to the locked canon, safe, complete, and executable by a junior builder without guessing** — and does it actually correct WP-CB-1's field layer?

This validates the **spec**, not an implementation (none exists). Do NOT build.

## 2. Checklist (validate each)

1. **Canon faithfulness** — every transform in the LOD400 (units §3.1, enums §3.2, renames/derive/attr/drop §3.3–§3.6) matches Canon §6/§7/§14 **exactly**. Flag any place the migration re-decides or diverges from the locked canon. Spot-check: `avg_yield_per_bed_m→yield_per_bed_m`; `days_in_gh_total→days_in_nursery`; `half-hardy→half_hardy`; bare `kg→kg_per_bed_m`; elemental-canonical / oxide-derived; `direct_sow→direct_seed`.
2. **Completeness** — every canon disposition (KEEP / RENAME / DERIVE / →ATTR / DROP-COL / DQ in Canon §7) is handled by some phase. Find any field or transform with no phase. Cross-check the §7.2 categorical set is fully covered by Phase 3.
3. **Phase-order safety** — order 1→8 is binding; **column-DROP (Phase 6 / migration 059) runs LAST and is gated** by a precondition check AFTER the Phase 5 alias cutover; DB dumps precede the rewriting phases (1/3/4/6); each rewriting phase has `--dry-run` + a rollback/down-migration. Flag any ordering that could break a consumer or lose data.
4. **`crop_attribute` design (Phase 3 / migration 058)** — table shape matches Canon §4 (value_canonical, value_list jsonb, provenance, UNIQUE(variety_id, attribute_name)); resolver does `hard_winner` **after** enum-canonicalization; **mirrors but does NOT modify** `enrichment_runner`/`reconciler`. SQLite `.with_variant` for tests.
5. **WP-CB-1 field-layer correction (Phase 5 / AC-07)** — confirm the migration actually fixes the known mapping: calc #3/#4/#5 → `days_in_nursery`; #4/#5/#6/#11 → categoricals from `crop_attribute`; yield → `yield_per_bed_m`. (This supersedes the FINDINGS patch.)
6. **Derive-don't-store (Phase 4 / AC-05)** — `derive.py` math: per-m² = per-bed-m ÷ 0.8 (bed_width AssumptionField); P₂O₅ = P×2.29; K₂O = K×1.205; plants_per_m2 from rows/spacing/bed_width. Stored rows for the 4 derived fields are deleted; per-m²-only crops converted to per-bed-m BEFORE deletion (R-03).
7. **Constraints** — `reconciler.py`/`enrichment_runner.py` untouched; the ONLY LOD500-lock exception is `models.py` for the §7.4 column drops (team_00-authorized, §authorization_note); dev-only (Mac oma-postgres) — **no production/server/uPress action** anywhere.
8. **Precision gate** — could a junior builder execute each phase from this spec without inventing transforms? List any gap (e.g., a transform that points to "the canon" without the canon actually enumerating it — note the canon IS locked, so pointers are acceptable IF the canon enumerates them).
9. **AC adequacy** — the 12 ACs (§4) are testable and cover all 8 phases + the invariants (zero residual units/enums, attribute population, no stored derived, alias cutover, gated drop, DQ, re-enrich, validate_aos 0 FAIL).
10. **Risk coverage** — R-01..R-05 (§5) adequately mitigate data-loss, consumer-break, per-m²-only, SQLite parity, production. Flag any unmitigated risk.

## 3. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-MIG
gate: L-GATE_S
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
checks: <n/10>
findings:
  - id: F-190-MIG-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    location: <LOD400 § / canon §>
    remediation: ...
summary: <one paragraph>
```
- **BLOCKED** if the migration diverges from the locked canon, has an unsafe phase order (esp. drop-not-last or no cutover gate), a missing transform that would lose data, or touches production.
- **PASS / PASS_WITH_FINDINGS** → team_100 dispositions; on PASS, team_10 begins the phase-by-phase build (team_50 QA, team_190 L-GATE_V at the end).

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---
*Self-contained L-GATE_S package for non-Claude execution. team_00: route to a non-Claude validator. (Your separate UI review runs against team_35's mockups — a different track from this data-model spec.)*
