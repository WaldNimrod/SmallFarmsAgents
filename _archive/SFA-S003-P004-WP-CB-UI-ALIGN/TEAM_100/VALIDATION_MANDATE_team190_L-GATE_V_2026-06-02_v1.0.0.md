# VALIDATION MANDATE (L-GATE_V) — SFA-S003-P004-WP-CB-UI-ALIGN — team_100 → team_190 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_190 · **Routed by:** team_00
**Branch:** `claude/wp-cb-ui-align-2026-06-02` · **Gate:** L-GATE_V (final, constitutional) · **Class:** A
**PRECONDITION:** the branch is DEPLOYED to `sfa.nimrod.bio` (team_99 deploy mandate). Do not run until deploy
is confirmed (team_99 will post the deployed SHA + smoke to `_COMMUNICATION/team_100/`).

## 0. Cross-engine (IR#1 / IR#5)
Build = Claude (Sonnet); internal QA = Claude (Haiku/team_50). L-GATE_V is the **constitutional** final gate →
**non-Claude** engine (**Cursor**), recorded as `validator_engine`. team_100 (Claude) cannot self-issue it.

## 1. What L-GATE_V validates
The DEPLOYED live site matches the team_35 LOD300 design **pixel/visually** (the standard that the prior 2 rounds
missed) AND functions, against the LOD400 ACs. This is the live per-page round the internal QA could not do (no
local DB). The internal QA already confirmed the CSS/shell layer green — see
`_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-UI-ALIGN/INTERNAL_VISUAL_QA_2026-06-02_v1.0.0.md`. Re-verify on live
and ADD the data-driven pages.

## 2. Checks (against LIVE `https://sfa.nimrod.bio`, with design frames open from the LOD300 board)

**V1 — AC-1 zero cream (computed, not screenshot).** On the live site, computed `body` background = `#f8fbf8`
(`rgb(248,251,248)`). View-source the served `tokens.css`: zero `--paper:`/`#f5f3ec`/"Cool Stone"; one
`--gj-paper` = #f8fbf8 (watch Cloudflare cache — confirm `?v=` advanced; if stale, flag for purge).

**V2 — AC-2 shell present site-wide.** Every page renders inside `.sh` (logo `#sfa-logo` + `.sh__nav`
book/calc/market + `.sh__acct`); `.sh__nav--mobile` 4-item bar at ≤899px; active nav color per surface
(leaf #4d6a2c / sun #a4711a / tomato #8e3018). No legacy `.gj-shell`/`.dt-shell`/`.sfa-nav` on any page.

**V3 — AC-3 pixel fidelity, design-vs-live PER SCREEN.** Capture a design-frame-vs-live pair for: book-entry,
crop page simple / full / drill-down, calc-dash. Confirm palette, type (Assistant / Frank Ruhl Libre / Carmela
brand), spacing, components match the LOD300 frames. This is the MANDATORY visual standard — a pair per screen.

**V4 — AC-4 /calc interactive (live data).** `typeof SFA_CALC !== 'undefined'`; each of the 6 interactive calcs
(#1 seed, #7 beds, #8 yield, #9 revenue, #10 pop, #12 fert) recomputes when inputs change on a real crop; 14
cards surfaced (8 in the §7 disabled/coming-soon state, clearly labeled); export CSV downloads; export PDF opens
a print view (no 404).

**V5 — AC-6 RTL + content integrity (live).** RTL legible; no raw DB keys / "Array" / "object Object" / stray
"—"; watercolor heroes + crop art render on the `.sh` shell.

**V6 — AC-5 no regression (live).** All mandated routes 200 (`/`, `/crop-book/`, a crop page, `/market/`,
`/calc/`, `/calc/export.csv`). (composer test is blocked locally — phpunit absent in vendor, pre-existing; note,
do not block on it.)

**V7 — design-gap items confirmed.** F-QA-04 mobile-nav styling + the `.sh__icon <a>` deviation (F-190-UIALIGN-02)
are acceptable as shipped; the mobile-nav design gap is flagged for team_35 to own in Class B (not a Class A
blocker).

## 3. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-ALIGN/WP-CB-UI-ALIGN_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_V
validator_engine: <non-Claude — Cursor>
deployed_sha: <from team_99>
result: PASS | PASS_WITH_FINDINGS | FAIL
checks:
  - id: V1..V7
    result: PASS | FAIL
    evidence: <computed values / design-vs-live screenshot pair refs>
findings:
  - id: F-190-UIALIGN-VNN
    severity: BLOCKER | MAJOR | MINOR
    where: <page / selector>
    fix: <precise>
summary: <one paragraph — MUST state visual-fidelity outcome per screen>
```
- **PASS** → team_100 executes ADR042 closure (archive mandate to team_191, roadmap → DONE/LOD500_LOCKED).
- BLOCKER/MAJOR → list precisely; team_100 routes a build fix + re-QA + L-GATE_V R2.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043).

---
*Self-contained package for non-Claude (Cursor) execution. Requires the live deploy first.*
