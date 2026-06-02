---
id: VERDICT_SFA-S003-P004-WP-CB-UI-ALIGN_L-GATE_S_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-06-02
type: validation_verdict
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_S
round: 1
artifact: _aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-ALIGN/LOD400_spec.md
branch: claude/wp-cb-ui-align-2026-06-02
head: a308d28
validator_engine: Cursor / Composer (non-Claude)
result: PASS_WITH_FINDINGS
---

# WP-CB-UI-ALIGN L-GATE_S Verdict (Round 1)

```yaml
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_S
round: 1
validator_engine: Cursor / Composer (non-Claude)
result: PASS_WITH_FINDINGS
checks:
  - id: C1
    result: PASS
    evidence: "Design tokens.css:18-23,166-173 --gj-paper #f8fbf8 … --gj-soil #8b5d2f match LOD400 D1 table. Served sfa_delivery/public_assets/css/tokens.css:168-173,182,195-199 same values. rg 'var\\(--(paper|ink|ink-soft|line|soil)\\)' sfa_delivery/public_assets/css → 0 matches; rg '#f5f3ec|Cool Stone' sfa_delivery → 0. body uses var(--gj-paper) tokens.css:78. QA addendum F-QA-01 (gj.css cream :root) incorporated in spec; served gj.css:3-6 documents removal, no --gj-paper:#f6f1e3 anywhere in sfa_delivery."
  - id: C2
    result: PASS
    evidence: "LOD400 §2c matches LOD300 Crop Book v1.html:70-82 (bar→mark+name+.sh__nav book/calc/market+.sh__nav__sp+.sh__acct+.sh__icon) and 1217-1222 mobile (ספר/מחשבון/מחירון/חשבון). §2a CSS block matches design cropbook-v1.css:98-118+463-484 verbatim (served crop-book-v1.css:592-630). Active tokens --gj-leaf-deep #4d6a2c, --gj-sun-deep #a4711a, --gj-tomato-deep #8e3018 tokens.css:177-180,182."
  - id: C3
    result: PASS
    evidence: "LOD400 §2c: crop-book→is-active; calc→is-calc + is-active; market→is-market + is-active; home/community/''→no pill. Matches selectors .sh__nav a.is-active, .is-active.is-calc, .is-active.is-market (crop-book-v1.css:611-613,624-626 mobile)."
  - id: C4
    result: PASS
    evidence: "LOD400 §2d symbol matches LOD300 lines 12-19; _layout.php:80-87 inline + <use href=\"#sfa-logo\"/> :90. COMPONENTS-delta.md:232-234 Brand note (system mark, not seedling). shell/_mark_svg.php absent (retired)."
  - id: C5
    result: PASS
    evidence: "Retirement table §2e: templates/shell/*.php, partials/nav.php, desktop.css deleted; _layout.php:81-109 single .sh, no nav/mobile/desktop includes; no desktop.css <link>; gj.css starts .gj-eyebrow:22 (no .gj-shell); hub.css has no .sfa-nav rules; desktop-extras.css:512 notes shell swap removed. Asset foreach tokens.css:27 keeps tokens,gj,hub,community,crop-book-*; desktop removed. 899/900px toggle crop-book-v1.css:629-630, documented §2b as project-authored."
  - id: C6
    result: PASS
    evidence: "_layout.php:68-69 in_array(['crop-book','calc'],true) loads crop-book-v1.js. CALC fns seed,beds,yield,revenue,pop,fert crop-book-v1.js:36-114. calc_dash.php modules #1-#14 (6 interactive data-calc, 8 modcard--disabled per catalog §7); #7 beds interactive, #11 frost disabled (team_00 content-from-code). routes.php:24 calc/export.{csv|pdf}; calc_dash.php:419-420 export links."
  - id: C7
    result: PASS
    evidence: "§0 OUT Class B + WP-CB-UI-CLASSB; delivery-tier only sfa_delivery/; Files-touched has no Python/migration/_aos/LOCKED. AC-1..AC-6 binding with mandatory AC-3 pixel-fidelity + AC-1 computed-style. validate_aos/composer test mandated §Deliverable 5."
findings:
  - id: F-190-UIALIGN-01
    severity: MINOR
    where: LOD400 §Deliverable 1 (lines 44-46)
    fix: "Merge QA addendum F-QA-01 into D1 body: legacy-token consumer grep is insufficient; any served file redefining --gj-paper/--gj-ink* to cream (e.g. gj.css :root) must be removed. Addendum already states this — fold into D1 so builders need not rely on addendum alone."
  - id: F-190-UIALIGN-02
    severity: MINOR
    where: LOD400 §2c
    fix: "LOD300 uses <button class=\"sh__icon\"> (line 81); spec uses <a href=\"/search\">. Acceptable for routing; note explicitly as intentional content-from-code / navigation deviation or revert to button+JS if strict DOM parity required."
  - id: F-190-UIALIGN-03
    severity: MINOR
    where: LOD400 §2a / QA F-QA-03–04
    fix: "Promote post-QA shell fixes into §2a verbatim block: .sh__foot .dot { flex:none; } and .sh__nav--mobile a active-state colors (design SSoT gap — team_35 Class B follow-up). Build already has these at crop-book-v1.css:604,621-626."
summary: "LOD400 (including the 2026-06-02 QA addendum) is faithful to team_35 design tokens + LOD300 shell DOM/CSS, reconciled with LOD200 Class A scope and the calculator catalog, and applies the team_00 EXACT-to-design / content-from-code rule (beds #7 interactive, frost #11 disabled). Independent grep of served sfa_delivery CSS confirms zero legacy var(--paper|ink|…) consumers and zero cream ground. Three MINOR documentation nits only; no BLOCKER or MAJOR. LOD400 LOCKS for team_10 / standing build on branch claude/wp-cb-ui-align-2026-06-02."
```

## Evidence summary

| Check | Verdict | Key proof |
|------:|---------|-----------|
| C1 | PASS | D1 `--gj-*` hex values match design `tokens.css`; served CSS grep clean |
| C2 | PASS | LOD300 shell DOM + verbatim `.sh` / `.sh__nav` CSS from `cropbook-v1.css` §1/§11 |
| C3 | PASS | `$active` → class composition matches `.is-active.is-calc` / `.is-market` |
| C4 | PASS | `#sfa-logo` once + `<use>`; COMPONENTS-delta § Brand note |
| C5 | PASS | Retirements listed; de-references complete; 900px toggle non-conflicting |
| C6 | PASS | JS gate + 14 calcs + 6 interactive + export route per catalog |
| C7 | PASS | Class A only; delivery-tier files; testable ACs incl. visual fidelity |

## Disposition

**LOD400 locks.** Proceed to L-GATE_V (build/visual) per program; no R2 required for spec unless team_100 chooses to fold MINOR findings into the main sections.

---
*team_190 · L-GATE_S Round 1 · IR#1/#5 satisfied (non-Claude validator).*
