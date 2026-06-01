---
id: VALIDATION_MANDATE_SFA-S003-P004-WP-CB-1-patch01_L-GATE_V_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_190 (Senior Constitutional Validator — external/non-Claude engine)
date: 2026-06-01
type: GATE_MANDATE
gate: L-GATE_V
scope: ui-followup
round: 1
wp: SFA-S003-P004-WP-CB-1-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. builder = Claude (team_10). QA = Claude (team_50). validator (you) = team_190 NON-CLAUDE. Claude MUST NOT self-issue this verdict (IR#1/#5)."
parent_wp: SFA-S003-P004-WP-CB-1
parent_verdict_ref: "_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/LGATE-V_VERDICT_R3_v1.0.0.md"
build_report_ref: "_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1-patch01/BUILD_REPORT_v1.0.0.md"
spec_ref: "_aos/work_packages/S003/SFA-S003-P004-WP-CB-1-patch01/LOD200_spec.md"
---

# L-GATE_V Validation Mandate — SFA-S003-P004-WP-CB-1-patch01 (UI follow-ups + watercolor art)

**Branch:** `claude/wp-cb-1-ui-2026-05-31` · **Commit:** `ba68b38` (art wiring lands across the patch01 commits 3708c8e..ba68b38)

## Context
The parent WP-CB-1 passed L-GATE_V R3 PASS_WITH_FINDINGS (verdict 8018df6) and is LOD500_LOCKED.
patch01 carries the declared follow-ups + the team_00-directed watercolor art integration. It edits
LOD500_LOCKED delivery files **under the chartered patch01 scope** — that scope expansion is exactly
what this gate evaluates.

## Scope to validate (5 items — all built; BUILD_REPORT + QA PASS_WITH_FINDINGS attached)
1. **V-03 JS↔Python calc parity #7/#9/#12** — `tests/CropBookV1MacroTest.php` asserts JS `CALC[...]`
   equals `calculators.py` for beds_for_target_yield / expected_revenue / fertilizer_compost_rate.
2. **Server-side filtering on book_index** — `CropBookViewController::entry()` filters q/family/season/
   dtm_max in SQL + sow/frost via payload post-filter; `book_entry.php` is a real GET form; 0-result
   shows a recoverable empty-state.
3. **/calc export** — `GET /calc/export.{csv,pdf}` (`HubController::calcExport` + `routes.php` +
   `calc_export_print.php`); CSV (UTF-8 BOM) + print-friendly PDF; JS `wireCalcExport()` appends the plan.
4. **F-UI-01** — `buildCb1Fields()` falls back to the default-variety payload (agronomy + field_state)
   because the MySQL mirror has no crop_field_enrichment / crop_attribute tables.
5. **Watercolor art** — 28 crop masters + `wc-cropbook-hero` + 3 home module-card heroes; every
   `WC_ART` / `$wc_art_map` ref resolves to a served PNG (`CROP_ART_MASTERS/README.md` is the intake log).

## Independent execution expected
```
git checkout claude/wp-cb-1-ui-2026-05-31 && git log --oneline -1     # expect ba68b38
cd sfa_delivery && composer test                                       # expect 107/107 (313 assertions)
php -l on the 8 changed PHP files                                       # expect clean
cd .. && bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .   # expect 0 FAIL (clean tree)
python3 -m pytest tests/crop_book/ -q                                  # expect 631 pass / 2 pre-existing fail
git diff --name-only main..HEAD | grep -E "crop_book/(calculators|assumptions|calculator_meta|field_policy|models).py|/versions/|/migrations/"   # expect: empty
# spot-check every WC_ART/$wc_art_map ref resolves to sfa_delivery/public_assets/img/crops/wc-*.png
```

## Constitutional checks (report each)
C1 directory authority (delivery-tier + _COMMUNICATION + CROP_ART_MASTERS only) · C2 roadmap authority
(builder made no roadmap edit; only team_100) · C3 IR#1 (builder/QA Claude, validator you = non-Claude) ·
C4 LOCKED Python backend + migrations untouched · C5 IR#5 (verdict by team_190) · C6 FIM fidelity
(filters/export/F-UI-01 honor the field contract; no raw DB key to users; no UI τ math — the F-UI-01
fallback renders backend-stamped state or a neutral UNKNOWN, never assumes VALIDATED) · C7 asset integrity
(art refs resolve; no broken `<img>`/`<use>`).

## Findings to assess (do not re-discover — confirm/escalate)
- **F-50-patch01-01 (LOW, latent):** `crop-book-v1.js CALC.revenue` does **no non-kg unit conversion**
  (uses `book.price` as ₪/kg) whereas `calculators.py expected_revenue` converts via `kg_per_unit`. Not
  reachable today (prices per-kg; dashboard panel exposes no price `[data-book]`); V-03 charter is the
  per-kg path. team_100 view: track to a future non-kg-pricing patch, non-blocking. Your call on severity.
- **patch01 edits LOD500_LOCKED delivery files** by charter (art + UI follow-ups). Confirm this is
  acceptable as a chartered follow-on patch (parent WP stays locked; patch01 is the additive layer).

## Verdict
Write `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-1-patch01/LGATE-V_VERDICT_v1.0.0.md` (§0 box + §1–§7).
On **PASS / PASS_WITH_FINDINGS** → team_100 advances patch01 LOD500_LOCKED + archive mandate to team_191.
Commit message: `validate(SFA-S003-P004-WP-CB-1-patch01/L-GATE_V): <VERDICT> — Team 190`.

*Issued by team_100 · 2026-06-01 · hand-off to Nimrod for non-Claude execution (IR#1/#5).*
