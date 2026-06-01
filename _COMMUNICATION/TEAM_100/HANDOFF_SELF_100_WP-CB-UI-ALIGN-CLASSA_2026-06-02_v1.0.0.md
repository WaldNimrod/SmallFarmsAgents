# Session Handoff — team_100 | IMPLEMENT WP-CB-UI-ALIGN Class A: make the crop-book + calculator surfaces + the global app-shell VISUALLY EXACT to the team_35 LOD300 (white-green v2, .sh/.sh__nav shell), fix /calc interactivity (14 calcs, JS load, export). Orchestrate full: LOD400 → team_190 L-GATE_S → team_10 build → team_50 VISUAL QA (design-vs-live per screen) → team_190 L-GATE_V (non-Claude). team_00 rule: interface/style/structure EXACT to team_35; content/fields from code.

**Date:** 2026-06-02 · **Author:** team_100 · **Type:** SESSION_HANDOFF · **Depth:** full · **Branch:** `claude/wp-cb-ui-align-2026-06-02` (HEAD on push)

---

## 1. MISSION (Class A — immediate)
Implement **WP-CB-UI-ALIGN Class A**: bring the surfaces team_35 ALREADY designed in v2 into exact visual
fidelity, and build the global app-shell. Scope:
1. **Unify the palette** — remove the legacy cream `--paper #f5f3ec` ("Cool Stone") ground; `body` background →
   `--gj-paper #f8fbf8` (white-green). Reconcile every legacy `--paper`/`--ink` consumer to `--gj-*`. Zero cream
   remains in served CSS. (design `tokens.css` is SSoT.)
2. **Build the team_35 app-shell** — `.sh` + `.sh__nav` (desktop: ▤ ספר גידולים [leaf] · ∑ מחשבון [sun] · ₪ מחירון
   [tomato] + `.sh__acct` "החשבון שלי") + `.sh__nav--mobile` (4-item bottom tab bar) + `#sfa-logo` symbol.
   Per `spec/COMPONENTS-delta.md` §24 + §"Brand note". Replace the legacy `.gj-shell`/`.dt-shell` chrome.
   ⚠ The shell wraps ALL pages — building it touches the global layout, but in Class A only the **crop-book +
   calculator** pages must be visually verified; hub/market/etc. (Class B) keep functioning on the new shell
   even though their *content* styling is finished later. (Confirm with team_00 if the shell should visibly
   replace chrome site-wide now, or be scoped — see §6 open question.)
3. **Crop-book + calculator visual fidelity** — these already use the v2 component CSS; verify they now render
   EXACTLY like the LOD300 frames (book-entry, crop simple/full/drill, calc-dash) once on the white ground + shell.
4. **Fix /calc** (team_50 F-CALC-002/003): `_layout.php` must load `crop-book-v1.js` on `/calc/` (and any page
   with calculators), so `SFA_CALC` is defined and panels recompute; surface the **14 calculators** (catalog),
   not 5.
5. **Fix /calc/export.pdf 404** (F-EXPORT-001): verify the route exists in the built code (it does on branch —
   `routes.php` `/calc/export.{fmt:csv|pdf}`); if the live 404 is deploy-lag, route a deploy mandate to team_99.

## 2. NOT in scope (Class A)
- Class B surfaces (hub/home, market, search, community, about, account) — those are **WP-CB-UI-CLASSB**,
  BLOCKED on team_35 v2 templates (DESIGN_REQUEST issued). Do not design/guess them.
- Data/field changes, backend, migrations (WP-CB-MIG2). The non-kg revenue conversion (F-50-patch01-01).
- Data findings F-STAT-001/002 (hub 66/30 vs API 70/65) + F-MKT-002 (no priced products) — ingest/data, not UI;
  log as a separate data follow-up, not part of this WP.

## 3. ROOT-CAUSE EVIDENCE (so the build targets the real problem)
- `sfa_delivery/public_assets/css/tokens.css:12` `--paper: #f5f3ec` (cream) + `:86 body { background: var(--paper) }`
  → whole site cream. Design wants `--gj-paper #f8fbf8`.
- No template uses `.sh`/`.sh__nav` — all use legacy `.gj-shell`/`.dt-shell` (`_layout.php:82-83` includes
  `shell/mobile.php` + `shell/desktop.php`). The team_35 app-shell was never built.
- `_layout.php` loads `crop-book-v1.js` only for crop-book routes → `/calc/` panels inert.
- Design SSoT: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/` (tokens.css, cropbook-v1.css/js,
  `LOD300 Crop Book v1.html`) + `spec/COMPONENTS-delta.md` §24 (nav) + DESIGN_TOKENS-delta.md.

## 4. ACCEPTANCE CRITERIA (visual fidelity is MANDATORY — the gap the prior 2 QA rounds missed)
- **AC-1** zero cream: served CSS has no `--paper:`/`#f5f3ec`/"Cool Stone" ground; computed `body` background =
  `#f8fbf8` (verify via preview_inspect computed style, not screenshot).
- **AC-2** app-shell present: `.sh__nav` desktop + `.sh__nav--mobile` + `#sfa-logo`; active nav color per surface
  (leaf/sun/tomato); legacy `.gj-shell`/`.dt-shell` removed from the in-scope pages.
- **AC-3** pixel fidelity: book-entry, crop simple/full/drill, calc-dash — each compared design-frame-vs-live
  (palette, type Assistant/Frank-Ruhl/Carmela, spacing, components). A design-vs-live screenshot pair per screen.
- **AC-4** /calc interactive: `SFA_CALC` defined; 6 interactive calcs recompute live; 14 calcs surfaced; export
  CSV downloads + PDF opens print view (no 404).
- **AC-5** no regression: `composer test` green; `validate_aos` 0 FAIL; no LOCKED Python/migration touched; routes 200.
- **AC-6** RTL legible; no raw keys / "Array" / stray "—"; watercolor art + heroes render on the new shell.

## 5. ORCHESTRATION (full — per team_100 role)
1. team_100 authors **LOD400** (exact: token-map diff, the `.sh` shell markup to add, which legacy CSS/shell to
   retire, the `_layout.php` JS-load fix, the 14-calc surfacing) → **team_190 L-GATE_S** (non-Claude, IR#1).
2. **Build = team_10** (Claude sub-agent, delivery-tier only).
3. **QA = team_50** with the NEW mandatory **VISUAL standard**: for every in-scope screen, capture a
   design-frame-vs-live pair and confirm fidelity — NOT just 200-OK/0-console-errors (that standard let the gap
   ship twice). Use Playwright on the Mac (no Playwright on waldhomeserver) against LIVE or local.
4. **L-GATE_V = team_190 NON-CLAUDE** (IR#1/#5) — verdict must include a visual-fidelity check.
5. Closure ADR042 (archive mandate to team_191).

## 6. OPEN QUESTION for team_00 (resolve at LOD400)
The app-shell is global. Two options: (a) **build the shell site-wide now** — every page immediately gets the v2
shell + white ground, Class B pages just lack their *content* polish until their WP; or (b) **scope the shell to
crop-book + calc only** for Class A, and roll it site-wide in Class B. team_100 recommendation: **(a)** — one
shell, built once, avoids a second chrome migration; Class B then only styles page *content*. Confirm at LOD400.

## 7. KNOWN OPERATIONAL LESSONS (carry over)
- Case-folding: repo tracks `_COMMUNICATION/TEAM_*` (UPPERCASE); lowercase `git add` silently no-ops — verify
  every file with `git cat-file -e HEAD:<path>` after commit.
- Edit silent-fail: after any edit, confirm it's in the committed version (`git show HEAD:<file> | grep`).
- Never guess filenames/hashes; read them back from git/disk first.
- validate_aos after commit (Check 32 fires on uncommitted _aos/ drift).
- **NEW lesson (this whole episode):** functional QA ≠ visual QA. A UI WP is not done until it matches the
  design board pixel-wise. This is now an AC, not an afterthought.

## 8. MANDATORY READS
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-ALIGN/LOD200_spec.md` (this WP) · `_aos/governance/team_100.md`
- Design SSoT: `…/HANDOFF_PACKAGE/design/` + `spec/COMPONENTS-delta.md` §24 + `DESIGN_TOKENS-delta.md`
- team_50 evidence: `_COMMUNICATION/TEAM_50/SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md` + `e2e_evidence_2026-06-02/`
- Delivery tier: `sfa_delivery/{templates/_layout.php, templates/shell/*, public_assets/css/tokens.css, app/routes.php}`

## 9. ACTIVATION PROMPT
```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_100 only

# Agent Onboarding — team_100 (Chief System Architect)

## TL;DR
- Identity: team_100 · Claude Code · Chief System Architect · spoke: SmallFarmsAgents (L0)
- Assignment: WP=SFA-S003-P004-WP-CB-UI-ALIGN (Class A) · gate=L-GATE_E PASS → author LOD400 → orchestrate
- Task: Make crop-book + calculator + the global app-shell VISUALLY EXACT to the team_35 LOD300 (white-green v2,
  .sh/.sh__nav). Unify palette (kill cream), build the shell, fix /calc (14 calcs + JS load + export).
  team_00 rule: interface/style/structure EXACT to team_35; content/fields from code; never guess a missing template.
- Branch: claude/wp-cb-ui-align-2026-06-02 · Writes: _COMMUNICATION/team_100/ + _aos/roadmap.yaml (IR#4) + the WP folder + sfa_delivery/ (via build)

## Iron Rules
- IR#1 cross-engine: build = Claude sub-agent; L-GATE_V = team_190 NON-CLAUDE; team_100 never self-issues L-GATE_V (IR#5).
- IR#4 single-writer roadmap. team_00 is Principal — LOD400 visual-fidelity ACs are binding.

## First action
Read the WP-CB-UI-ALIGN LOD200 + the team_35 design SSoT (open the LOD300 board + COMPONENTS-delta §24). Resolve
the §6 open question with team_00 (shell site-wide now vs scoped). Then author LOD400 with EXACT token-map +
shell markup + /calc fix + visual ACs, and route team_190 L-GATE_S. Orchestrate build (team_10) → VISUAL QA
(team_50, design-vs-live per screen) → L-GATE_V (team_190 non-Claude).
```

## 10. CANONICAL OPTIONS
- [A] Resolve §6 (shell scope) with team_00 → author LOD400.
- [B] Author LOD400 + route team_190 L-GATE_S.
- [C] Dispatch team_10 build (after L-GATE_S).
- [D] Dispatch team_50 VISUAL QA (after build).
