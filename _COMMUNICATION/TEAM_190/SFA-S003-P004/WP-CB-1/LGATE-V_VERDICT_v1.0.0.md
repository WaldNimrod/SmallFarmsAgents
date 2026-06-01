# L-GATE_V VERDICT — SFA-S003-P004-WP-CB-1 — Team 190 — v1.0.0

**Date:** 2026-05-31  
**Validator:** team_190 (Codex / non-Claude engine)  
**Mandate:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/VALIDATION_MANDATE_team190_LGATE-V_2026-05-31_v1.0.0.md`

## §0 Verdict Box

| Field | Value |
|---|---|
| Gate | L-GATE_V |
| WP | SFA-S003-P004-WP-CB-1 |
| Commit | `9f9d9d1dcaab0bdd11632dcadc2568614dbd9d11` |
| Branch | `claude/wp-cb-1-ui-2026-05-31` |
| Verdict | **FAIL** |
| AC coverage | AC-10 PASS; AC-11 PASS_WITH_FINDINGS; AC-12 PASS_WITH_DECLARED_PREEXISTING_FAILURES; AC-13-local PASS_WITH_FINDINGS |
| Constitutional | C1 PASS; C2 PASS; C3 PASS; C4 PASS; C5 PASS; C6 **FAIL**; C7 PASS |
| LOD500 | **DO NOT LOCK UI LOD500** until C6 is remediated and revalidated |

## §1 Reviewed Artifacts

Reviewed, in mandate order:

| Artifact | Evidence |
|---|---|
| Validation mandate | `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/VALIDATION_MANDATE_team190_LGATE-V_2026-05-31_v1.0.0.md` |
| Build report | `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1/BUILD_REPORT_UI_v1.0.0.md` |
| Binding field contract | `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/FIELD_INTERFACE_MAP_v1.0.0.md` |
| Dispatch | `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/DISPATCH_sfa_build_UI_2026-05-31_v1.0.0.md` |
| LOD400 §10/§11 | `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md` |
| Design source of truth | `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` |
| Code at HEAD | `sfa_delivery/app`, `sfa_delivery/templates`, `sfa_delivery/public_assets`, `sfa_delivery/tests` |

## §2 Execution Evidence

Executed independently on commit `9f9d9d1`.

| Command | Result |
|---|---|
| `git worktree add --detach /private/tmp/sfa-wp-cb-1-val claude/wp-cb-1-ui-2026-05-31` | Clean detached source worktree created at `9f9d9d1`. |
| `cd sfa_delivery && composer test` | Initial run lacked `vendor/`; after copying existing dependency tree into the temp worktree, PHPUnit passed: **96 tests / 278 assertions / 0 failures / 1 PHPUnit deprecation**. |
| `php -l` on changed PHP files | **19/19 changed PHP files clean**; no syntax errors detected. |
| `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` | **28 PASS / 20 SKIP / 0 FAIL**. This supersedes the build report's older 1-FAIL AOS note for this branch state. |
| `python3 -m pytest tests/crop_book/ -q` | Escalated run, with local DB/network access: **631 passed / 2 failed / 1 skipped / 76 warnings**. Failures are unchanged backend/governance tests, not introduced by the UI diff. |
| `git diff --name-only main..HEAD` | No `organic_market_agent/crop_book/{calculators.py,assumptions.py,calculator_meta.py,field_policy.py,models.py}` edits and no migration edits. `_aos` edits limited to `roadmap.yaml` and `SFA-S003-P004-WP-CB-MIG2/LOD200_spec.md`. |

The non-escalated pytest run in the main checkout showed the same two logical failures plus one sandbox-blocked live DB access. The escalated run resolved the DB access and left the declared two failures.

## §3 AC Matrix

| AC | Verdict | Evidence |
|---|---|---|
| AC-10 | PASS | Audience switch is implemented via `book_entry.php` and JS `wireAudience`; Simple/Full/Drill via `depth_tabs.php`, `book_crop.php`, and JS `wireDepths`; `assumption_field.php` renders default, override input, explainer, reset, and read-more; `prov_value.php` renders VALIDATED / UNVALIDATED `*` / MISSING `—` + request-info. |
| AC-11 | PASS_WITH_FINDINGS | JS formulas for interactive #1, #7, #8, #9, #10, #12 are present in `public_assets/js/crop-book-v1.js`. Source inspection confirms #1, #8, #10 match `calculators.py`. PHPUnit covers #1, #8, #10 formula parity, but does not execute the JS runtime directly. |
| AC-12 | PASS_WITH_DECLARED_PREEXISTING_FAILURES | `validate_aos.sh` is 0 FAIL; `composer test` is green; `pytest tests/crop_book/` has the declared two pre-existing failures; locked backend and migrations are untouched. |
| AC-13-local | PASS_WITH_FINDINGS | Macro tests cover enabled calcs, MISSING-disabled calcs, request-info CTA, and UNVALIDATED-not-disabled behavior. Local live-crop visual/browser smoke was not executed in this gate; logic-level evidence is adequate for the local proxy but should be repeated after C6 remediation. |

## §4 Findings

| ID | Severity | Root Cause | Impact |
|---|---|---|---|
| F-V-01 | **MAJOR / Constitutional C6** | `sfa_delivery/templates/macros/calc_panel.php` renders the internal field name directly in the disabled-calculator user message: `המחשבון יידלק כש<code>field_name</code> יתמלא`. It uses `field_name` instead of `FieldRegistry::label()`. | Violates the binding Field Interface Map and mandate C6: raw DB/canonical keys must not be rendered to users. This is a direct L-GATE_V blocker. |
| F-V-02 | **MAJOR / Constitutional C6** | UI code performs threshold/state presentation logic at `τ=0.40`: `prov_value.php` derives VALIDATED/UNVALIDATED when `field_state` is absent, and `prov_table.php` marks confidence bars low with `conf < 0.40`. | The declared `field_state` fallback is honest for F-UI-01, but the implementation still embeds threshold policy in UI code. The binding contract says stamped-state rendering, no UI threshold math. Remediate by limiting fallback to an explicitly named temporary adapter or moving derivation into ingest/mirror data before LOD500. |
| F-V-03 | MINOR / AC-11 | PHPUnit parity tests compute PHP-side expected formulas and inspect parity by construction; they do not execute `crop-book-v1.js`. | Not a blocker by itself because #1/#8/#10 source formulas match Python, but it leaves future JS drift under-tested. Add a headless JS parity fixture for #1/#8/#10 at minimum, and ideally #7/#9/#12. |

## §5 Declared-Deviations Assessment

| Declared item | Assessment |
|---|---|
| F-UI-01: live mirror lacks `field_state`; UI degrades defensively | Honest for missing and low-confidence values: null/empty becomes MISSING, low confidence becomes UNVALIDATED, and request-info is shown. However, the threshold fallback contributes to C6 risk and must be contained before LOD500. |
| PARTIAL: server-side filter execution on book_index | Accepted as non-blocking. The UI makes the filter rail visible, while server-side filtering remains a follow-up. |
| PARTIAL: `/calc` PDF/CSV export | Accepted as non-blocking. Export controls are visibly disabled/stubbed rather than falsely active. |
| PARTIAL: JS parity for #7/#9/#12 not headless-tested | Accepted as declared follow-up; #1/#8/#10 were independently checked. |
| Tomato/cucumber glyph fallback | Accepted as non-blocking asset follow-up; watercolor assets for lettuce/radish/parsley/dill exist and are optimized in delivery assets. |
| F-CB1-UI-01 old-name drift carried to WP-CB-MIG2 | Accepted. UI resolver is drift-immune in source inspection, and locked backend drift is not edited here. |
| Two pre-existing pytest failures | Accepted as non-UI-induced. Escalated run failures: `test_ni_publisher_isolation.py::TestNiPublisherIsolation::test_ac21b_publisher_dir_clean` and `test_source_registry.py::test_uc_prefix_requires_moderation`. No changed files under `organic_market_agent/` or those tests in this UI diff. |

## §6 Constitutional Checks

| Check | Verdict | Evidence |
|---|---|---|
| C1 directory authority | PASS | Build commits `1456c48`, `47c2dfd`, `695c658`, `1b1ef5f`, `7149ee4`, `4d7b1e8` are confined to `sfa_delivery/` and `_COMMUNICATION/TEAM_10/`; non-build commits account for team_35, team_100, docs, and `_aos` artifacts. |
| C2 roadmap authority | PASS | `_aos/roadmap.yaml` was edited by architecture/mandate commits, not by the build commits. |
| C3 IR#1 | PASS | Builder is Claude; validator is Codex/non-Claude. Cross-engine requirement satisfied. |
| C4 LOCKED-backend integrity | PASS | No changes to locked Python backend modules or migrations in `main..HEAD`. |
| C5 IR#5 | PASS | This verdict is issued by team_190. |
| C6 LOD400/FIM fidelity | **FAIL** | FieldRegistry alias resolver exists and is tested, but raw internal field names are rendered to users in disabled calc copy, and UI threshold math exists in presentation code. |
| C7 model/asset integrity | PASS | Delivery assets exist; Carmela font checksum matches source handoff asset; crop images are valid optimized PNGs in `sfa_delivery/public_assets/img/crops/`. |

## §7 Verdict

**FAIL.**

The UI slice is functionally close and the independent execution evidence is mostly green: delivery tests pass, AOS validation is 0 FAIL, locked backend/migrations are untouched, and the Python crop-book suite has only the declared two pre-existing failures under a DB-enabled run.

The gate cannot pass because C6 is explicit and currently violated. The disabled calculator renders an internal field key directly to users, and UI code still contains threshold/state derivation behavior that the binding contract assigns to stamped backend state. These are remediation-sized defects, not architectural collapse, but they block LOD500 UI lock.

Required remediation before revalidation:

1. Replace every user-visible internal field key in UI copy with `FieldRegistry::label()` output; keep raw keys only in data attributes/dev-only diagnostics.
2. Remove or formally isolate UI threshold math so normal rendering consumes stamped `field_state`; if F-UI-01 fallback remains temporarily necessary, document it as a named compatibility adapter and ensure it cannot be confused with the permanent contract.
3. Add a direct JS parity fixture for at least #1/#8/#10, or document why source-level parity plus PHPUnit formula checks are the intended gate standard.

Team 100 should route this back for a narrow UI remediation patch, then resubmit to team_190 for L-GATE_V revalidation. No deploy or LOD500 UI lock is authorized from this verdict.
