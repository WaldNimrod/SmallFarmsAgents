---
id: VALIDATION_MANDATE_SFA-S003-P004-WP-CB-UI-CLASSB_L-GATE_S_v1.0.0
from: team_100 (Chief System Architect)
to: team_190 (Senior Constitutional Validator — external/non-Claude engine)
date: 2026-06-02
type: GATE_MANDATE
gate: L-GATE_S
round: 1
wp: SFA-S003-P004-WP-CB-UI-CLASSB
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "IR#1 cross-engine. spec author = team_100 (Claude). validator (you) = team_190 NON-CLAUDE. Claude MUST NOT self-issue gate verdicts (IR#1/#5)."
spec_ref: "_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md"
design_ssot: "_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/"
---

# L-GATE_S Validation Mandate — WP-CB-UI-CLASSB (LOD400 v1.0.0)

Validate that the LOD400 is precise enough for team_10 to build the team_35 Class B design **without guessing** —
the precision gate. This is a SPEC review (not a build review).

## What this WP is
Implement team_35's Class B v2 design across the 6 non-crop-book surfaces (hub, market list+detail, search,
community, about, account) + app-shell refinements, on the existing Slim4/PHP delivery tier. Structure/style EXACT
to the team_35 boards; content/fields from existing code. Delivery-tier only — **no backend/migration/schema**.

## Read
1. `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md` (the spec under gate — v1.0.0 LOCKED).
2. Design SSoT: `…/HANDOFF/design/Board-B-*.html` + `classb.css` + `classb.js` + `spec/B_COMPONENTS-TEMPLATES-classb-delta.md`.
3. Intake manifest (provenance + checksums): `…/HANDOFF/INTAKE_MANIFEST_team100_v1.0.0.md`.
4. team_00 decisions: LOD400 §9 + the APPROVED §9a units/freshness table.
5. Current delivery code the spec maps to: `sfa_delivery/{templates/pages/*,app/Controllers/{Hub,MarketView}Controller.php}`.

## L-GATE_S checks (report each PASS / PASS_WITH_FINDINGS / FAIL)
- **Precision:** can a fresh builder implement each of the 7 surfaces from §2 + the board + classb.css alone, with
  no ambiguity? (exact templates, controllers, board frames, component classes are named.)
- **Data fidelity:** §3 claims market history/graph/sources/freshness + contribute + tiers + modules are already
  served by existing code (MarketViewController `fetchHistory(28)` + `/api/v1/market/{slug}/history`,
  AssumptionsController::contribute, Modules::all()). Verify these exist and the spec reads them correctly. The
  ONLY new code claimed is `AccountController` + `account_landing` (visual shell). Confirm no hidden backend need.
- **Honest-data rule (§4):** spec forbids invented values — empty/stale/disabled states where data is absent
  (`.pcard.is-empty`, `.emptybox`, `.srch-nomatch`, disabled `.rangesel` 90/year). Confirm it's specified, not optional.
- **team_00 decisions correctly encoded (§9):** community feed-less; account UI-shell + "בקרוב"; graph 7+28 live /
  90+year disabled; search client-side only; §9a freshness ≤3/4-7/>7 on the 7-day OMA window + unit-display table.
- **Server-side guardrail:** §9 #4 + `SFA-S003-P004-WP-SRV-IDEAS` register require any server-side change to be
  logged as PROPOSED (unapproved), never built in this WP. Confirm the spec binds the builder to this.
- **Constitutional:** delivery-tier only; no LOCKED Python/migration; reuses the Class A app-shell (depends_on
  WP-CB-UI-ALIGN); palette unchanged (tokens.css byte-identical to v1, per the intake manifest).
- **AC testability (§5):** are AC-1..AC-7 objectively verifiable? Note the VISUAL fidelity AC (design-vs-live per
  surface) — the standard the prior 2 QA rounds lacked.

## Findings / open items to assess
- LOD400 §9a thresholds are team_00-APPROVED — treat as locked, don't relitigate.
- The Class A app-shell is being built in parallel (WP-CB-UI-ALIGN); this spec depends on it. Flag if any Class B
  surface needs a shell hook not yet in the Class A scope.

## Verdict
Write `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-CLASSB/LOD400-VERDICT_v1.0.0.md` (§0 box + checks + findings).
On PASS / PASS_WITH_FINDINGS → team_100 dispatches team_10 build. On BLOCKED → team_100 revises + re-routes.
Commit message: `validate(SFA-S003-P004-WP-CB-UI-CLASSB/L-GATE_S): <VERDICT> — Team 190`.

*Issued by team_100 · 2026-06-02 · non-Claude execution per IR#1/#5.*
