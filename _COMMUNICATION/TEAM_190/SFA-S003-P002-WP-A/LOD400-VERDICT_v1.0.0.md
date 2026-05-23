---
id: VERDICT-team190-SFA-S003-P002-WP-A-LGATE_S-R1
from: team_190
to: team_100
date: 2026-05-23
gate: L-GATE_S
round: 1
result: PASS_WITH_FINDINGS
---

# Team 190 L-GATE_S Verdict — SFA-S003-P002-WP-A

## 1. Scope

Team 190 reviewed the LOD400 spec for `SFA-S003-P002-WP-A` (Data Enrichment Architecture) as a spec-only constitutional validation.

Engine requirement: satisfied. This verdict was produced on a non-Claude engine per Iron Rule #1.

Primary inputs reviewed:

- `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-A/EXTERNAL_VALIDATION_BUNDLE/TEAM_190_ACTIVATION_PROMPT.md`
- `_aos/roadmap.yaml`
- `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md`
- `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md`
- `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md`
- Supporting evidence from existing `models.py`, `reconciler.py`, migrations `038` and `040`, `upload_dispatch.py`, and current crop-book tests.

Startup validation:

- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
- Result: `28 PASS / 18 SKIP / 0 FAIL`
- L-GATE_E state: roadmap confirms `SFA-S003-P002-WP-A` has `L-GATE_E` `PASS` dated `2026-05-23`.

## 2. Verdict

**Result: PASS_WITH_FINDINGS**

The LOD400 spec is constitutionally valid enough to proceed to builder dispatch. Two MAJOR findings must be addressed before L-GATE_B closure because they affect implementation precision and production-safety behavior. Two MINOR findings should be fixed or explicitly acknowledged in the BUILD_REPORT.

## 3. Constitutional Checks

| Check | Result | Evidence |
|---|---|---|
| C1 — Directory authority | PASS | Builder deliverables stay in application/test/script surfaces plus `_COMMUNICATION/TEAM_10/`; no `_aos/` mutation is assigned to the builder. |
| C2 — Iron Rule #1 | PASS | LOD400 header assigns builder `sfa_build (team_10)` and validator `team_190 (non-Claude, Iron Rule #1)`. |
| C3 — Iron Rule #4 | PASS | LOD400 does not instruct builder to modify `_aos/roadmap.yaml`. |
| C4 — LOD500_LOCKED guard | PASS | §19 lists locked files and bounds the `models.py` exception to three `CropVarietySourceValue` columns plus the `CropVariety.enrichments` relationship. |
| C5 — Raw material guard | PASS | Tend/JMF raw material is not assigned for modification; existing importer source files are read/called only in WP-A. |
| C6 — GCR_1 authorization chain | PASS | team_00 decision record §2 Q6 pre-authorizes `models.py` modification for the three source-value metadata columns. |
| C7 — Backward compatibility | PASS | §9.3 preserves `reconcile_dtm(name_he, tend_values, jmf_value)` and `reconcile_variety(source_rows)` wrapper signatures. |
| C8 — Migration chain | PASS | LOD400 specifies `041` with `down_revision = "040"` and `042` with `down_revision = "041"`. |
| C9 — SQLite compatibility | PASS_WITH_FINDING | AC-01 requires SQLite guard for 042 backfill, but the §4 code snippet omits the guard. See F-190-WP-A-04. |
| C10 — Additive-only principle | PASS | Prior migrations `001-040`, `views.py`, existing publisher files, and raw importers are locked; only GCR_1-scoped `models.py`, reconciler, seed CLI, and new additive files are in scope. |

## 4. Architectural Correctness Checks

| Check | Result | Assessment |
|---|---|---|
| 1. Reconciler algorithm (§9.2) | PASS | The 10-step algorithm is implementable and preserves wrapper behavior. The hard-override and blend sequencing are clear. |
| 2. Statistical outlier gate (§7.6 / AC-08) | PASS_WITH_FINDING | Modified Z-score formula is present and direction `abs(Z) > threshold` is clear, but MAD=0 is not specified. See F-190-WP-A-02. |
| 3. Confidence score formula (§9.2 step 9) | PASS | LOD400 improves on LOD200 by handling 0 rows, 1 row, and mean=0. Formula is testable via AC-12. |
| 4. Enrichment runner upsert key (§10) | PASS | `(variety_id, field_name)` matches the migration unique constraint and is sufficient for idempotent per-field consensus rows. |
| 5. `latest_op` blend strategy | PASS | `documented_price` uses `latest_op`; lexicographic ordering is acceptable for existing `Tend_YYYY` labels and legacy `Tend`. |
| 6. NI class activation (§11) | PASS | Skeleton is clear enough for no-file baseline and future subclass registration. |
| 7. AC matrix testability (§15) | PASS_WITH_FINDING | ACs are largely testable offline with SQLite/mocks; AC-17 avoids network dependency. The dispatch-upload wording in §14 is unsafe/imprecise. See F-190-WP-A-01. |
| 8. Build sequence (§17) | PASS | The 10 steps are in a logical order: registry/policy, ORM/migrations, reconciler, enrichment runner, NI skeleton, harness, publisher artifact, tests, validation, BUILD_REPORT. |

## 5. Findings

F-190-WP-A-01: MAJOR
Location: §14 Enrichment SPA artifact / AC-17 / §19 locked publisher inventory
Issue: The spec says the new enrichment publisher should call `dispatch_upload(profile="crop_book_enrichment")` and catch `UnknownProfile`, but the current `dispatch_upload()` supports only `"market"` and `"crop_book"` and defines no `UnknownProfile`. Passing `"crop_book_enrichment"` would not reliably fail as described; it can fall through to the market upload path, creating a production-safety risk and failing to deliver the intended crop-book enrichment media behavior.
Required fix: Specify that WP-A generates `output/sfagent-crop-book-enrichment.json` only, with no upload attempt, or define an exact non-locked upload mechanism that cannot route through the market profile. Do not instruct the builder to call `dispatch_upload()` with an unsupported profile unless `upload_dispatch.py` modification is separately authorized.

F-190-WP-A-02: MAJOR
Location: §9.2 step 4 / AC-08
Issue: The statistical outlier algorithm uses modified Z-score with MAD, but does not define behavior when `MAD == 0`. This occurs in common small-sample cases such as `[45, 45, 45, 200]`, where the intended outlier is obvious but the formula divides by zero.
Required fix: Add a deterministic `MAD == 0` branch, for example: if all values equal, no statistical outliers; otherwise use an alternate absolute-deviation/IQR fallback or mark values differing from the common median according to a specified threshold. Add an AC/test case covering MAD=0.

F-190-WP-A-03: MINOR
Location: §7 `SourceSpec` / §9.2 step 2.c / §4 migration 042 backfill
Issue: The SourceSpec examples assign EX and NI weights (`1.0`, `0.85`) while comments and migration semantics imply hard overrides should have `confidence_weight = NULL`. §9.2 step 2.c says to set row `confidence_weight = spec.weight (None for EX/NI)`, but the shown `SourceSpec` objects for EX/NI do not have `None` weights.
Required fix: Make the metadata contract explicit: either use `weight: float | None` and set EX/NI to `None`, or keep `trust_weight` for ranking but write `confidence_weight = None` whenever `is_hard_override=True`.

F-190-WP-A-04: MINOR
Location: §4 migration 042 / AC-01
Issue: AC-01 requires the 042 backfill to be skipped on SQLite via `op.get_bind().dialect.name == "sqlite"`, but the §4 migration snippet runs three raw `op.execute()` statements without showing the guard.
Required fix: Add the guard to the migration implementation instructions, not only the AC text, so the builder does not copy the snippet into a SQLite-incompatible migration.

## 6. Recommendation

Authorize `sfa_build` to proceed to L-GATE_B with the findings above logged.

Required before L-GATE_B closure:

- Resolve F-190-WP-A-01 by removing or correcting the unsupported dispatch-upload instruction.
- Resolve F-190-WP-A-02 by specifying and testing the MAD=0 outlier branch.

Expected BUILD_REPORT acknowledgements:

- Confirm F-190-WP-A-03 metadata semantics for EX/NI hard overrides.
- Confirm F-190-WP-A-04 SQLite guard is present in migration 042.

