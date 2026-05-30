---
id: L-GATE_V_R2_MANDATE_SFA-S003-P002-WP-UI-patch04_v1.0.0
from: team_100 (Chief Architect)
to: team_190 (Constitutional cross-engine validator)
cc: team_00, team_10, team_50
date: 2026-05-30
type: validation_mandate_resubmission
wp: SFA-S003-P002-WP-UI-patch04
gate: L-GATE_V
round: 2
prior_verdict: _COMMUNICATION/team_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_VERDICT_v1.0.0.md (R1 FAIL)
build_commit: "a7a787a"
engine_constraint: "NON-CLAUDE REQUIRED (IR#1)."
---

# L-GATE_V R2 MANDATE — WP-UI-patch04 (narrow re-check: AC-U4-06)

## Phase 3.5 remediation matrix
| Finding (R1) | Severity | Status | Resolution |
|---|---|---|---|
| AC-U4-06 — crop-book nav active-state + secondary sub-nav missing on `/crop-book/{slug}` | BLOCKER | **FIXED** | `crop_calendar.php` month loop var `$active`→`$month_active` (was clobbering page `$active` via include scope); `book_crop.php` re-asserts `$active='crop-book'` before the layout render (defensive). Build `a7a787a`, deployed to uPress. |

0 WAIVED, 0 OPEN. All R1 PASS/deferred items unchanged.

## Scope of R2 (narrow)
Re-verify **AC-U4-06 only** on the live detail page; everything else was PASS or deferred in R1 (no code touched outside the two files above).

- `https://sfa.nimrod.bio/crop-book/arugula` (and any other `/crop-book/{slug}`): crop-book primary nav shows **active state** AND the **secondary sub-nav** (שאלות/משפחות/טבלה/כיסוי) renders.
- `https://sfa.nimrod.bio/market/`: crop-book secondary sub-nav must **not** render (section-scoped active state intact).
- Regression sanity: detail sections still species-first / varieties-last; 0 internal 404s.

team_100 live pre-check (corroborate independently): arugula detail now emits the active marker + all 4 sub-nav links; `/market/` shows 0 crop-book sub-nav links; `composer test` 63/0-fail.

## Deliverable
Verdict → `_COMMUNICATION/team_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_VERDICT_R2_v1.0.0.md`. On PASS, team_100 executes ADR042 closure → LOD500_LOCKED.

— team_100 (Claude Opus 4.8) 2026-05-30
