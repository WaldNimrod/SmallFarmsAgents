---
id: VALIDATION_MANDATE_SFA-S003-P004-WP-CB-1_L-GATE_V_R3_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_190 (Senior Constitutional Validator — external/non-Claude engine)
date: 2026-06-01
type: GATE_MANDATE
gate: L-GATE_V
scope: ui
round: 3
wp: SFA-S003-P004-WP-CB-1
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. builder/remediator = Claude. validator (you) = team_190 NON-CLAUDE. Claude MUST NOT self-issue this verdict (IR#1/#5)."
supersedes_round: 2
r1_verdict_ref: "_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_v1.0.0.md"
r2_verdict_ref: "_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_R2_v1.0.0.md"
---

# L-GATE_V Validation Mandate — Round 3 — SFA-S003-P004-WP-CB-1 (UI slice)

**Branch:** `claude/wp-cb-1-ui-2026-05-31` · **R3 remediation commit:** `9747152` (single file + its test)

## Why round 3 (and how narrow it is)
- R1 (`6802edb`) FAIL on C6 → two findings.
- R2 (`ad2b180`) FAIL: **F-190-CB1-V-02 RESOLVED** (prov_value/prov_table τ removed — confirmed by you),
  but **F-190-CB1-V-01 still broken** — `calc_panel.php` passed `FieldRegistry::label()`'s
  `[label_he, explainer_he]` tuple straight to `$h()`, causing Array-to-string → literal "Array" in the UI.
- R3 fixes exactly that one bug. **This is the only change since `ad2b180`.** Everything you already PASSed in
  R2 (V-02, C1–C5, C7, all green execution) is untouched.

## The single change to verify
`git diff ad2b180 9747152` — two files, one logical fix:

**`sfa_delivery/templates/macros/calc_panel.php`** (the V-01 fix)
```php
// before (R2): renders literal "Array"
<b><?= $h(FieldRegistry::label((string)($disabled_field['field_name'] ?? ''))) ?></b>
// after (R3): destructure the tuple, then escape the string — same pattern as book_crop.php:284
<?php [$disabled_label_he] = FieldRegistry::label((string)($disabled_field['field_name'] ?? '')); ?>
<b><?= $h($disabled_label_he) ?></b>
```
**`sfa_delivery/tests/CropBookV1MacroTest.php`** — `testCalcPanelDisabledWhenRequiredFieldMissing` now asserts:
resolved Hebrew label present (`FieldRegistry::label('yield_per_bed_m')[0]`), **no** `>Array<`, **no**
`<b>yield_per_bed_m` (raw key never in visible copy; allowed only in the `data-field` hook).

## Independent execution expected
```
git checkout claude/wp-cb-1-ui-2026-05-31 && git log --oneline -1   # expect 9747152
cd sfa_delivery && composer test                                     # expect 96/96 (281 assertions); the R2 PHP warning is GONE
php -l templates/macros/calc_panel.php
grep -n "FieldRegistry::label" templates/macros/calc_panel.php       # expect destructured form, not passed to $h() directly
# render-smoke the disabled panel: confirm the Hebrew label string appears and "Array" does not
cd .. && bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .   # expect 0 FAIL (clean tree)
python3 -m pytest tests/crop_book/ -q                                # expect 631 pass / 2 pre-existing fail
git diff --name-only main..HEAD                                      # no LOCKED backend, no migration
```

## Scope guard
- C6 is the only check still in question; it should now flip to PASS (both V-01 and V-02 resolved).
- Carry C1–C5/C7 forward from R2 with a one-line re-confirmation — the R3 delta is one macro + its test,
  touches no backend, no migration, no roadmap.
- Non-blockers unchanged (R1 §5 / R2): **V-03** (#7/#9/#12 JS parity), server-side filters, `/calc` export,
  glyph fallback, F-UI-01, F-CB1-UI-01→WP-CB-MIG2, 2 pre-existing pytest fails. team_100 view: track all to the
  WP-CB-1 follow-up patch.

## Verdict
Write `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_R3_v1.0.0.md` (§0 box + §1–§7).
On **PASS / PASS_WITH_FINDINGS** → team_100 advances UI LOD500_LOCKED + archive mandate to team_191; the
declared PARTIAL items + V-03 become the tracked WP-CB-1 follow-up patch.
Commit message: `validate(SFA-S003-P004-WP-CB-1/L-GATE_V): <VERDICT> R3 — Team 190`.

*Issued by team_100 · 2026-06-01 · hand-off to Nimrod for non-Claude execution (IR#1/#5).*
