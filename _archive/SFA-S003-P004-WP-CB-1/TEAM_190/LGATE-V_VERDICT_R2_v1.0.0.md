# L-GATE_V VERDICT R2 — SFA-S003-P004-WP-CB-1 — Team 190 — v1.0.0

**Date:** 2026-06-01  
**Validator:** team_190 (Cursor Composer / non-Claude engine)  
**Mandate:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/VALIDATION_MANDATE_team190_LGATE-V_R2_2026-06-01_v1.0.0.md`  
**Supersedes:** `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_v1.0.0.md` (R1 FAIL, commit `6802edb`)

## §0 Verdict Box

| Field | Value |
|---|---|
| Gate | L-GATE_V |
| WP | SFA-S003-P004-WP-CB-1 |
| Round | 2 |
| Commit (remediation tip) | `6b4a819d` (branch HEAD `d793b73` — docs-only delta; no `sfa_delivery/` change) |
| Branch | `claude/wp-cb-1-ui-2026-05-31` |
| Verdict | **FAIL** |
| AC coverage | AC-10 PASS; AC-11 PASS_WITH_FINDINGS; AC-12 PASS_WITH_DECLARED_PREEXISTING_FAILURES; AC-13-local PASS_WITH_FINDINGS *(unchanged from R1 — delta is presentation-only)* |
| Constitutional | C1 PASS *(reconfirmed)*; C2 PASS *(reconfirmed)*; C3 PASS *(reconfirmed)*; C4 PASS *(reconfirmed)*; C5 PASS; C6 **FAIL**; C7 PASS *(reconfirmed)* |
| LOD500 | **DO NOT LOCK UI LOD500** — C6 still blocked (partial remediation) |

## §1 Reviewed Artifacts

| Artifact | Evidence |
|---|---|
| R2 validation mandate | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/VALIDATION_MANDATE_team190_LGATE-V_R2_2026-06-01_v1.0.0.md` |
| R1 verdict (baseline) | `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_v1.0.0.md` |
| Remediation commits | `f4e04f1` (calc_panel + prov_value), `6b4a819` (prov_table) |
| Delta reviewed | `git diff 9f9d9d1..6b4a819` — three presentation macros (+ R1 verdict/roadmap commits in range, out of C6 scope) |
| Code inspected | `sfa_delivery/templates/macros/{calc_panel,prov_value,prov_table}.php`, `sfa_delivery/app/Lib/FieldRegistry.php` |

## §2 Execution Evidence

Executed independently on branch `claude/wp-cb-1-ui-2026-05-31` at remediation tip `6b4a819` (same `sfa_delivery/` tree as HEAD `d793b73`).

| Command | Result |
|---|---|
| `git checkout claude/wp-cb-1-ui-2026-05-31 && git log --oneline -1` | HEAD `d793b73` (docs-only after `6b4a819`; remediation code at `6b4a819`). |
| `cd sfa_delivery && composer test` | **96 tests / 278 assertions / 0 failures**. 1 PHP **warning** on `testCalcPanelDisabledWhenRequiredFieldMissing` — Array-to-string in disabled-panel label path (see F-V-R2-01). |
| `php -l templates/macros/calc_panel.php prov_value.php prov_table.php` | **All clean** — no syntax errors; no leaked markdown fence in `prov_table.php`. |
| `grep -rnE "0\.40\|0\.50\|>= 0\.\|<= 0\." templates/macros/` | **1 comment-only hit** (`prov_value.php:13` — narrative reference to a future τ fast-follow; **no executable threshold**). |
| `grep -rn "code><?=.*field_name" templates/` | **No matches** — raw key no longer wrapped in `<code>`. |
| `bash _aos/lean-kit/.../validate_aos.sh .` | **29 PASS / 19 SKIP / 0 FAIL**. |
| `python3 -m pytest tests/crop_book/ -q` | **631 passed / 2 failed / 1 skipped** — same pre-existing failures as R1. |
| `git diff --name-only main..HEAD` | **No** locked backend (`calculators.py`, `assumptions.py`, `calculator_meta.py`, `field_policy.py`, `models.py`) or migration edits. |
| Runtime smoke (validator) | `prov_value.php`: unstamped present value → `span.pv-unknown` ✓; stamped VALIDATED → `span.pv-validated` ✓. `calc_panel.php` disabled path → renders literal **`Array`** + PHP warning, not Hebrew label ✗. |

## §3 AC Matrix

| AC | Verdict | R2 note |
|---|---|---|
| AC-10 | PASS | Remediation delta does not alter audience/depth/assumption/provenance components beyond C6 fixes. |
| AC-11 | PASS_WITH_FINDINGS | Unchanged; V-03 (#7/#9/#12 headless parity) still untested — team_100 declared MINOR follow-up. |
| AC-12 | PASS_WITH_DECLARED_PREEXISTING_FAILURES | Delivery + AOS green; pytest 2 pre-existing fails; no backend drift. |
| AC-13-local | PASS_WITH_FINDINGS | Macro tests still cover enabled/disabled calcs and prov_value VALIDATED/UNVALIDATED/MISSING; **no test** for UNKNOWN cue or disabled-panel Hebrew label (gap exposed by F-V-R2-01). |

## §4 Findings

| ID | Severity | Root Cause | Impact |
|---|---|---|---|
| F-V-R2-01 | **BLOCKER / Constitutional C6** (reopens F-190-CB1-V-01) | `calc_panel.php:81` passes the **array** return of `FieldRegistry::label()` directly into `$h()`. `FieldRegistry::label()` returns `[label_he, explainer_he]` (see `FieldRegistry.php:127–137`); correct usage elsewhere is `[$lbl_he,] = FieldRegistry::label($fn)` (`book_crop.php:284`). | Disabled-calculator copy renders PHP `"Array"` (with runtime warning) instead of the Hebrew label. Raw DB key is no longer visible in `<code>`, but FIM §4 / mandate C6 requirement — user-visible resolved label — is **not met**. PHPUnit `testCalcPanelDisabledWhenRequiredFieldMissing` passes but emits the same warning; test does not assert label text. |
| F-V-R2-02 | **RESOLVED** (was F-190-CB1-V-02) | `prov_value.php` no longer derives VALIDATED/UNVALIDATED from `confidence_score` or source class. Unstamped present values → neutral `UNKNOWN` / `span.pv-unknown`. | UI threshold math removed from provenance cue macro. C6 sub-check **PASS** for prov_value. |
| F-V-R2-03 | **RESOLVED** (was F-190-CB1-V-02 pt.2) | `prov_table.php` `conf < 0.40` removed; `is_low` backend flag drives emphasis; bar width remains raw confidence display; `.prov` nesting fixed; fence artifact removed. | C6 sub-check **PASS** for prov_table. |
| F-V-R2-04 | MINOR | `span.pv-unknown` has no dedicated CSS rule in `public_assets/css/` (mandate cited `--gj-ink-soft`; class relies on default styling + `title` tooltip). | Cosmetic / design-token gap only; does not block gate once F-V-R2-01 is fixed. |
| F-V-R2-05 | MINOR (carried V-03) | No headless JS parity fixture for calcs #7/#9/#12. | Accepted non-blocker per R1 §5 and R2 mandate scope guard; track to WP-CB-1 follow-up patch. |

## §5 Declared-Deviations Assessment

| Declared item | R2 assessment |
|---|---|
| F-UI-01 (mirror lacks `field_state`) | **Improved.** UNKNOWN cue is honest — present values without stamped state are no longer promoted to VALIDATED via UI τ. Acceptable interim behavior pending backend ingest. |
| PARTIAL: server-side filters, /calc export, glyph fallback | Unchanged — non-blocking. |
| F-CB1-UI-01 → WP-CB-MIG2 | Unchanged — non-blocking. |
| 2 pre-existing pytest failures | Unchanged — non-UI-induced. |
| V-03 (#7/#9/#12 parity) | **Non-blocking** per team_100 R2 scope; agree with MINOR classification. |

## §6 Constitutional Checks

| Check | Verdict | Evidence |
|---|---|---|
| C1 directory authority | PASS *(reconfirmed)* | Remediation commits touch only `sfa_delivery/templates/macros/` (+ R1 verdict/roadmap in intermediate commits). |
| C2 roadmap authority | PASS *(reconfirmed)* | No builder edit to `_aos/roadmap.yaml` in remediation commits `f4e04f1`/`6b4a819`. |
| C3 IR#1 | PASS *(reconfirmed)* | Builder/remediator = Claude; validator = Cursor Composer (non-Claude). |
| C4 LOCKED-backend integrity | PASS *(reconfirmed)* | `main..HEAD` diff excludes locked Python backend and migrations. |
| C5 IR#5 | PASS | This verdict issued by team_190. |
| C6 LOD400/FIM fidelity | **FAIL** | F-190-CB1-V-02 fully remediated (no UI τ in prov macros). F-190-CB1-V-01 **not** remediated — disabled calc label path is broken (`Array` literal). |
| C7 model/asset integrity | PASS *(reconfirmed)* | Remediation delta does not touch assets or fonts. |

## §7 Verdict

**FAIL (Round 2).**

Round 2 confirms the **F-190-CB1-V-02** remediation is complete and correct: UI threshold math is gone from `prov_value.php` and `prov_table.php`, unstamped values render `pv-unknown`, syntax is clean, and independent execution evidence remains green (96/96 delivery tests, 0 AOS FAIL, declared pytest failures only).

Round 2 **cannot** pass because **F-190-CB1-V-01** remains broken. Replacing `<code><?= field_name ?></code>` with `$h(FieldRegistry::label(...))` without destructuring the `[label_he, explainer_he]` tuple causes an Array-to-string conversion and user-visible `"Array"` text — not the Hebrew label the binding contract requires. This is a one-line-class fix (destructure label before `$h()`, matching `book_crop.php`).

Required remediation before R3:

1. **F-V-R2-01:** In `calc_panel.php`, resolve label as `[$disabled_lbl_he,] = FieldRegistry::label(...)` and pass `$disabled_lbl_he` to `$h()`. Add PHPUnit assertion that disabled copy contains Hebrew label and excludes raw canonical key in visible text.
2. *(Optional follow-up, non-blocking)* Add macro test for `prov_value` UNKNOWN state; add `.pv-unknown` token styling per design spec.

No deploy or LOD500 UI lock is authorized. Team 100 should route a **narrow R3 remediation** (calc_panel label destructuring only), then resubmit for L-GATE_V Round 3.
