# VALIDATION MANDATE (L-GATE_S) — SFA-S003-P004-WP-CB-UI-ALIGN — team_100 → team_190 — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 (Claude Opus 4.8) · **To:** team_190 · **Routed by:** team_00
**Repo:** `SmallFarmsAgents` · **Branch:** `claude/wp-cb-ui-align-2026-06-02` · **HEAD:** `a308d28`
**Gate:** L-GATE_S (spec) · **Round:** 1 · **Class:** A
**Note:** the build (team_10, Sonnet) + team_50 internal visual QA already ran on this branch; the LOD400 now
carries a QA addendum (4 findings, all fixed). Review the LOD400 **including** that addendum.

## 0. Cross-engine (IR#1 / IR#5)
The build will be executed by **Claude (Sonnet)**. This spec gate must therefore be validated by a
**non-Claude engine** — **Cursor** (current SFA non-Claude validator; not Codex). Record `validator_engine` in
the verdict. team_100 (Claude) cannot self-issue this verdict.

## 1. What this gate validates
The **LOD400 build mandate** is precise, faithful to the design SSoT + LOD200, internally consistent, and safe to
build — *before* team_10 starts. This is a SPEC gate, not a build gate.

**Artifact under review:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-ALIGN/LOD400_spec.md`
**Against:**
- LOD200: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-ALIGN/LOD200_spec.md`
- Design SSoT: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/` (tokens.css,
  cropbook-v1.css, `LOD300 Crop Book v1.html`) + `spec/COMPONENTS-delta.md` §24 + `DESIGN_TOKENS-delta.md`
- Calculator SSoT: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/CALCULATOR_CATALOG_v1.0.0.md`
- team_00 rule: *interface/style/structure EXACT to team_35; content/fields from code; never guess a missing template.*

## 2. Checks (verify each PASS / FAIL with evidence)

**C1 — Token reconciliation faithful & complete.** The D1 mapping table (legacy → `--gj-*`) matches the design
tokens.css values (`--gj-paper #f8fbf8`, `--gj-ink #1f2a22`, `--gj-line #dce6dc`, `--gj-ink-soft #5d6b5e`,
`--gj-paper-2 #eef4ee`, `--gj-paper-3 #dde8dd`, `--gj-soil #8b5d2f`). Confirm the consumer-line list (tokens.css
86,87,104,119,120,139,140) is the COMPLETE set of legacy-token consumers — i.e. grep the served CSS yourself and
confirm zero `var(--paper|--ink|--ink-soft|--line|--soil)` usages exist outside tokens.css. If any exist that the
LOD400 missed → FAIL with the file:line.

**C2 — Shell markup faithful to LOD300.** The `.sh` markup block in LOD400 §2c matches the design DOM
(`LOD300 Crop Book v1.html` lines 70–82 desktop + 1217–1222 mobile): bar → mark + name + `.sh__nav`(book/calc/
market) + `.sh__nav__sp` + `.sh__acct` + `.sh__icon`; mobile 4-item bar (ספר/מחשבון/מחירון/חשבון). The `.sh`/
`.sh__nav` CSS in §2a is verbatim from design cropbook-v1.css §1 (98–118) + §11 (463–484). Active colors:
book=leaf-deep #4d6a2c, calc=sun-deep #a4711a, market=tomato-deep #8e3018.

**C3 — `is-active` logic correct.** Driven by `$active` (value set home/crop-book/market/calc/community/''):
crop-book→book is-active; calc→`is-active is-calc`; market→`is-active is-market`; others→no pill. Confirm the
class composition matches the CSS selectors (`.is-active.is-calc`, `.is-active.is-market`).

**C4 — `#sfa-logo` brand rule.** Symbol defined once (verbatim from LOD300 12–19), referenced via
`<use href="#sfa-logo"/>`; the legacy `_mark_svg.php` seedling mark is retired. Matches COMPONENTS-delta §24
Brand note.

**C5 — Retirement list safe.** Retiring shell/mobile.php, shell/desktop.php, partials/nav.php, shell/_mark_svg.php,
desktop.css, and the gj.css 27–96 / hub.css `.sfa-nav*` blocks does NOT remove still-used non-shell components
(gj.css keeps `.gj-eyebrow`+ ; hub.css keeps module cards). Confirm the `<link>`/`include`/asset-array
de-references are all listed so nothing 404s or includes a deleted file. Confirm the responsive 900px toggle
(authored, not in SSoT) is a reasonable, non-conflicting addition.

**C6 — `/calc` fix correct.** The `_layout.php:69` condition change to
`in_array($active, ['crop-book','calc'], true)` will load crop-book-v1.js on `/calc/` (where `$active='calc'`).
14-calc surfacing follows the catalog §2; 6 interactive follow the **code** (#1,7,8,9,10,12 — note `beds`#7 over
design's `frost`#11, justified by the content-from-code rule); the other 8 use the §7 disabled-state contract.
Export route untouched.

**C7 — Scope & safety.** Delivery-tier only; no Python/migration/`_aos`/LOCKED files in the Files-touched list;
Class B surfaces explicitly excluded; ACs (AC-1..AC-6) are testable and include the mandatory visual-fidelity AC.

## 3. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-ALIGN/WP-CB-UI-ALIGN_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_S
round: 1
validator_engine: <non-Claude — e.g. Cursor/GPT-5>
result: PASS | PASS_WITH_FINDINGS | FAIL
checks:
  - id: C1..C7
    result: PASS | FAIL
    evidence: <file:line / grep output>
findings:
  - id: F-190-UIALIGN-NN
    severity: BLOCKER | MAJOR | MINOR
    where: <LOD400 §>
    fix: <precise>
summary: <one paragraph>
```
- **PASS** (or PASS_WITH_FINDINGS, minors only) → LOD400 LOCKS; team_10 (Sonnet) build proceeds / stands.
- Any BLOCKER/MAJOR → list precisely; team_100 fixes the LOD400 + routes R2.

Notify via `_COMMUNICATION/team_100/` (MSG per ADR043).

---
*Self-contained package for non-Claude (Cursor) execution. The spec is a single file — no build artifacts to
review at this gate.*
