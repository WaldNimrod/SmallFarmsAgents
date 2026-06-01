---
id: VALIDATION_MANDATE_SFA-S003-P004-WP-CB-1_L-GATE_V_R2_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_190 (Senior Constitutional Validator — external/non-Claude engine)
date: 2026-06-01
type: GATE_MANDATE
gate: L-GATE_V
scope: ui
round: 2
wp: SFA-S003-P004-WP-CB-1
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. builder/remediator = Claude. validator (you) = team_190 NON-CLAUDE. Claude MUST NOT self-issue this verdict (IR#1/#5)."
supersedes_round: 1
r1_verdict_ref: "_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_v1.0.0.md"
---

# L-GATE_V Validation Mandate — Round 2 — SFA-S003-P004-WP-CB-1 (UI slice)

**Branch:** `claude/wp-cb-1-ui-2026-05-31` · **Remediation commits:** `f4e04f1` + `6b4a819` (on top of validated `9f9d9d1`)

## Why round 2
Round 1 = **FAIL** on **C6** (verdict `6802edb`). Two BLOCKERs (F-190-CB1-V-01/02), both now remediated.
Everything else was green and is unchanged. This round is a **focused re-check of the fixes** +
confirmation nothing else regressed. C1–C5 and C7 were PASS in R1; re-confirm C6.

## What changed since the R1-validated commit (review ONLY this delta + its blast radius)
`git diff 9f9d9d1 6b4a819` — exactly **three** presentation files (calc_panel.php, prov_value.php, prov_table.php):

1. **F-190-CB1-V-01 fix** — `sfa_delivery/templates/macros/calc_panel.php`
   The disabled-calculator copy no longer prints the raw DB key. Was:
   `…כש<code><?= $h($disabled_field['field_name']) ?></code> יתמלא` →
   now: `…כש<b><?= $h(FieldRegistry::label($disabled_field['field_name'])) ?></b> יתמלא`.
   The raw key remains only in the `data-field` machine hook on the reqinfo control (allowed per your R1 note).
   **Verify:** no visible raw key in the rendered disabled panel; the Hebrew label shows instead.

2. **F-190-CB1-V-02 fix** — `sfa_delivery/templates/macros/prov_value.php`
   All τ threshold math removed from the UI. The macro now renders the backend-stamped `field_state`
   verbatim. Logic: value empty → `MISSING`; value present + state ∈ {VALIDATED,UNVALIDATED,MISSING} →
   render that state; value present + **no/unknown** state → new neutral **`UNKNOWN`** cue
   (`span.pv-unknown`, `--gj-ink-soft`, "טרם אומת מול הספר") — **never** assumed VALIDATED. No `0.40`/`0.50`
   constant remains in any macro.
   **Verify:** grep the macros for any numeric threshold (expect none); confirm an unstamped present value
   renders `pv-unknown`, not `pv-validated`.

3. **F-190-CB1-V-02 fix (part 2)** — `sfa_delivery/templates/macros/prov_table.php` (commit `6b4a819`)
   The R1 verdict named prov_table.php's `conf < 0.40` bar threshold as the second half of V-02; the first
   remediation patch (`f4e04f1`) missed it. Now removed — the "is-low" emphasis is driven by a
   backend-stamped `$s['is_low']` flag (no UI τ); the bar WIDTH remains a raw display of the confidence
   number. Also removed a leaked ` ``` ` markdown fence + malformed close that PHP was misparsing as
   backtick shell-exec operators (latent bug), and fixed the `.prov` div nesting.
   **Verify:** no `0.40` in prov_table.php; no backtick-fence; `php -l` clean; `.prov` opens/closes once.

## Independent execution expected
```
git checkout claude/wp-cb-1-ui-2026-05-31 && git log --oneline -1   # expect 6b4a819
cd sfa_delivery && composer test                                     # expect 96/96
php -l templates/macros/calc_panel.php templates/macros/prov_value.php
grep -rnE "0\.40|0\.50|>= 0\.|<= 0\." templates/macros/             # expect: no matches
grep -rn "code><?=.*field_name" templates/                          # expect: no matches
cd .. && bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .   # expect 0 FAIL (clean tree)
python3 -m pytest tests/crop_book/ -q                                # expect 631 pass / 2 pre-existing fail
git diff --name-only main..HEAD                                      # no LOCKED backend, no migration
```

## Scope guard
- C6 is the only gate that flipped; re-issue the full §0 box but you may carry C1–C5/C7 forward with a
  one-line re-confirmation (the delta touches no backend, no migration, no roadmap — `6b4a819` is two
  presentation files only).
- Declared non-blockers unchanged from R1 §5 (server-side filters, /calc export, glyph fallback, F-UI-01,
  F-CB1-UI-01→WP-CB-MIG2, 2 pre-existing pytest fails). **V-03 (parity #7/#9/#12) intentionally NOT done this
  round** — assess whether it should block (team_100 view: MINOR, track to the WP-CB-1 follow-up patch).

## Verdict
Write `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_R2_v1.0.0.md` (same §0+§1–§7 format).
On **PASS / PASS_WITH_FINDINGS** → team_100 advances UI LOD500_LOCKED + archive mandate to team_191; the
declared PARTIAL items + V-03 become a tracked WP-CB-1 follow-up patch.
Commit message: `validate(SFA-S003-P004-WP-CB-1/L-GATE_V): <VERDICT> R2 — Team 190`.

*Issued by team_100 · 2026-06-01 · hand-off to Nimrod for non-Claude execution (IR#1/#5).*
