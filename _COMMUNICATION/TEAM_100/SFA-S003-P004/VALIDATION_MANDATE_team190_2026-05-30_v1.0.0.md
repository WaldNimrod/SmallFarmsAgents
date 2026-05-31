# VALIDATION MANDATE + PROMPT — SFA-S003-P004 — team_100 → team_190 — v1.0.0

**Date:** 2026-05-30
**From:** team_100 (Chief System Architect, Claude Code / Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00 (hand-off — see §0 cross-engine constraint)
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `main` · HEAD `1222fe5`

---

## 0. Cross-engine constraint (Iron Rule #1 / #5 — MANDATORY)

The builder was **Claude Sonnet** (team_10) and the architect is **Claude Opus** (team_100). Therefore **this validation MUST run on a NON-CLAUDE engine** — Cursor Composer, GPT-5.x, or Codex. A Claude engine **cannot** issue these verdicts (constitutional). Confirm your engine in the verdict header.

---

## 1. What you are validating (two targets, two gates)

| # | Target | Artifact | Gate | Scope |
|---|--------|----------|------|-------|
| **A** | **Crop Data Model Canon** (LOD200) | `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` | **L-GATE_S** (design/spec) | FULL — design soundness, completeness, precision, migration safety, future-proofing |
| **B** | **WP-CB-1 backend slice** (calculators) | committed code `fd7dfba` + `1222fe5` | **Independent build verification** (confirm team_100's self-attested L-GATE_B) | **DURABLE CORE ONLY** — calculator math, AssumptionField registry, tests, constraints |

### Explicitly OUT OF SCOPE for Target B (do NOT flag as defects)
- **Field-mapping** (which DB field feeds which calculator: `days_in_gh_total` vs `days_in_nursery_cell`, categoricals `planting_method`/`planting_season`/`frost_tolerance_class` not in enrichment, yield field name). This is **known and intentionally deferred** to the Canon (Target A) + a future migration — documented in `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/FINDINGS_field_mapping_reconciliation_v1.0.0.md`. WP-CB-1 is `BUILD_PAUSED` for exactly this reason. Validate the **math and structure**, not the mapping.
- **UI / mockups / JS** (AC-10/11/13) — not built (team_35 in flight).
- **Live deploy / enrichment data rows** (AC-02/04) — DB-side, deferred.

### Context (read for grounding; light review, not gated)
- Architecture amendment: `documentation/02-architecture/sfa-delivery-tier.md` §1A (3-environment model + per-dataset SSoT) — confirm it does not contradict §0/§1 of the same doc.
- Spec artifacts: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/{CALCULATOR_CATALOG,MANDATORY_FIELD_SCHEMA,GAP_FILL_PLAN}_v1.0.0.md`, LOD400 draft `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md`.

---

## 2. Evidence map (commits)

| Commit | Contents |
|--------|----------|
| `fd7dfba` | backend slice: `calculators.py`, `assumptions.py`, `calculator_meta.py`, `field_policy.py` (+2), `sfa_ingest_push.py`, 4 test files |
| `3e47ffe` | architecture §1A amendment + FINDINGS artifact |
| `76c5b76`, `7caaf81` | Canon LOD200 v1.0.0 (+ roadmap WP-CB-0, CB-1→BUILD_PAUSED) |
| `1222fe5` | AssumptionField post_url fix (`/blog/` prefix) |

---

## 3. TARGET A — Canon LOD200 → L-GATE_S checklist

Validate the **design**, not an implementation (none exists yet). Check each:

1. **Taxonomy coherence** — are the 6 field types (T1 reconciled-numeric / T2 categorical / T3 list / T4 computed / T5 identity / T6 provenance) mutually exclusive and collectively exhaustive for crop data? Any datum that fits none or two?
2. **Layer-ownership rule** — is "one concept → one field → one unit → one layer" actually enforced by the registry (§7)? Find any field still claimed by two layers.
3. **Registry correctness (§7)** — spot-check the current→canonical dispositions against the **live DB vocabulary**. Run the inventory yourself:
   ```bash
   docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
     "select field_name,count(*) from crop_field_enrichment group by 1 order by 1"
   docker exec oma-postgres psql -U oma -d organic_market_agent -tAc \
     "select distinct field_name from crop_variety_source_values order by 1"
   ```
   Confirm: every enriched/source field is dispositioned (KEEP/RENAME/DERIVE/→ATTR/DROP-COL/DQ); no field is missed.
4. **Units (§6.1) + enums (§6.3)** — complete and canonical? Confirm `°C`/`celsius`/`C` collapse and `direct_sow→direct_seed`, `semi_hardy→half_hardy` are correct and that no live value is left unmapped.
5. **`crop_attribute` layer (§4)** — sound design? Does it integrate with the existing `source_registry` (8 classes) + reconciler pattern? Is the `hard_winner`-after-enum-canonicalization order correct?
6. **Yield/nutrients canon (§6.4)** — per-bed-m canonical + derived per-m² (linked to bed_width AssumptionField) + elemental-canonical/oxide-derived: arithmetically correct (per-m² = per-bed-m / 0.8; P₂O₅ = P×2.29; K₂O = K×1.205)?
7. **Compute-don't-store (§3 T4)** — `plants_per_m2`, `avg_revenue_per_bed_m` correctly classified as derived (not stored)?
8. **Migration safety (§8)** — is the phase order safe? Specifically: does the **column DROP run LAST**, after consumers cut over via the alias cycle (so nothing reads a dropped column)? Any phase that could lose data or break a live consumer?
9. **Future-vision namespace (§9)** — does the `plan_/task_/sale_/op_` namespace genuinely let CB-2..CB-5 extend the same layers without new tables / schema churn? Any case it fails?
10. **team_00 decisions (§13)** — are all three correctly embedded (nursery=sow→field total; physical column DROP; per-m² linked to bed_width AssumptionField)?
11. **Precision gate** — could a junior builder execute the §8 migration from this doc without guessing? List any gap.

## 4. TARGET B — backend build independent verification

Run these and confirm independently:
```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
python3 -m pytest tests/crop_book/test_calculators.py tests/crop_book/test_assumptions.py \
  tests/crop_book/test_calculator_meta.py tests/crop_book/test_field_policy.py -q   # expect 92 passed
python3 -m pytest tests/crop_book/ -q        # expect 548 passed / 2 failed (see below)
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .            # expect 0 FAIL
git show --stat fd7dfba                       # confirm files touched
```
Then validate:
1. **Calculator math** — independently recompute ≥1 case for each of the 14 functions in `organic_market_agent/crop_book/calculators.py` against the formulas in LOD400 §5. Confirm units + edge cases. Confirm `CalcUnavailable(<field>)` raises when a required **book** value is None (not for AssumptionFields/user inputs).
2. **AssumptionField registry** (`assumptions.py`) — 8 keys; defaults (germination 0.90, bed_width 0.80, oversow 1.10, std_bed_length_m 30, compost_N_pct 0.015, application_efficiency 0.50, rotation_gap_seasons 3); `germination_rate` + `bed_width` have non-null `post_url` (the `/blog/` form); `get_assumption` honors override; `tray_cells` + `hardiness_offset` tables present.
3. **`calculator_meta` internal consistency** — `calc_enabled` disables iff a required field is MISSING. (Do NOT judge whether the field *names* are the right live fields — that's the canon-deferred mapping, out of scope §1.)
4. **The 2 suite failures are PRE-EXISTING** — verify independently (they reproduce on a stash of the slice; they relate to a concurrent data-ingestion run, not this code): `test_ni_publisher_isolation::test_ac21b_publisher_dir_clean`, `test_source_registry::test_uc_prefix_requires_moderation`.
5. **Constraints** — confirm via `git show fd7dfba`: NO LOD500_LOCKED file changed (`reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`, `models.py`, `constants.py`, migrations 001–057); NO new migration; additive-only edits to `field_policy.py` + `sfa_ingest_push.py`.

---

## 5. Verdict format (write to `_COMMUNICATION/team_190/SFA-S003-P004/`)

Produce **two verdicts** (one per target). For each:
```yaml
target: A (Canon L-GATE_S) | B (backend build verification)
validator_engine: <Cursor Composer | GPT-5.x | Codex>   # MUST be non-Claude
result: PASS | PASS_WITH_FINDINGS | BLOCKED
checks: <n/n passed>
findings:
  - id: F-190-CB0-NN | F-190-CB1-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    location: <file:line / §>
    remediation: ...
summary: <one paragraph>
```
- **Target A** BLOCKED if the design has a contradiction, a registry gap that would lose data, or an unsafe migration order. PASS_WITH_FINDINGS for refinements.
- **Target B** — remember the field-mapping is OUT OF SCOPE; only the math/registry/constraints are judged. PASS if math is correct + constraints hold.

Notify back via `_COMMUNICATION/team_100/` (MSG per ADR043 naming).

---

## 6. Disposition after verdicts (team_100 will action)
- **A PASS** → Canon LOD500-locks the design; open the Migration WP (§8) + correct WP-CB-1 LOD400 field layer to the canon.
- **A findings** → team_100 revises the Canon, re-routes.
- **B PASS** → backend slice's L-GATE_B is cross-engine-confirmed; full WP-CB-1 L-GATE_V deferred until after the canon migration + UI.

---

*Prepared by team_100 for non-Claude execution. team_00: route to a non-Claude validator session. This file is the single self-contained package — the validator needs nothing from the originating conversation.*
