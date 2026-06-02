# INTERNAL VISUAL QA — SFA-S003-P004-WP-CB-UI-ALIGN (Class A) — team_50 — v1.0.0

**Date:** 2026-06-02 · **By:** team_50 (internal QA, orchestrated by team_100) · **Branch:** `claude/wp-cb-ui-align-2026-06-02`
**Build under test:** HEAD `f22138d` (team_10 build) → fixes at `f85691e` · **Method:** design-vs-live CSS-render harness
**Standard:** the NEW mandatory VISUAL standard — computed-style verification (not screenshot-only), per-screen.

## 0. Why a CSS-render harness (scope honesty)
The PHP delivery tier needs a live MySQL with seed data to render data-driven pages (`Db::create()` throws
without `DB_NAME`/`DB_USER`), and the branch is **not deployed** — so full live-data design-vs-live QA awaits a
DB stand-up or a staging deploy. BUT the gap that shipped twice (cream vs white ground; missing shell) is **pure
CSS + static markup**. This round verified that layer directly: a static harness loading the ACTUAL served
`tokens.css` + `gj.css` + `crop-book-v1.css` + `crop-book-v1.js`, rendering the real `.sh` shell DOM + a calc
header, served by `php -S` and inspected with computed styles. This is the strongest possible check for AC-1/AC-2
and catches the exact class of defect that previously escaped.

**Deferred to post-deploy (L-GATE_V live round):** per-page design-vs-live for book-entry, crop simple/full/drill,
and the full 14-card calc dash with live crop data (AC-3 full, AC-4 recompute-with-data, AC-6 art/heroes).

## 1. Results vs ACs

| AC | Check | Result | Evidence (computed) |
|----|-------|--------|---------------------|
| AC-1 | `body` background = #f8fbf8 | **PASS (after fix)** | `getComputedStyle(body).backgroundColor` = `rgb(248,251,248)`; `color` = `rgb(31,42,34)` (#1f2a22). Served CSS grep: zero `--paper:`/`#f5f3ec`/"Cool Stone"; `--gj-paper` defined once = #f8fbf8. |
| AC-2 | `.sh` shell + nav + `#sfa-logo`; active color per surface | **PASS** | `.sh__bar` present; `.sh__mark use` present; calc-active nav bg = `rgb(164,113,26)` (#a4711a sun-deep). Desktop (1280px): `.sh__nav` flex, `.sh__nav--mobile` none, `.sh__acct` flex. Mobile (375px): `.sh__nav` none, `.sh__nav--mobile` flex, 4 items. |
| AC-2 | footer status dot | **PASS (after fix)** | `.sh__foot .dot` = 8×8, bg `rgb(111,138,69)` (#6f8a45 via --status-fresh). |
| AC-3 | brand type | **PASS (shell-level)** | `.sh__name` font-family = `Carmela, "Frank Ruhl Libre", serif`. Full per-page type fidelity → live round. |
| AC-4 | `SFA_CALC` defined; 6 interactive keys | **PASS** | `typeof window.SFA_CALC` = object; keys = `[seed, beds, yield, revenue, pop, fert]` (the 6 interactive, incl. #7 beds). Recompute-with-data → live round. |
| AC-4 | 14 calcs surfaced | **PASS (static)** | build report: 14 `modcard__head` in calc_dash.php (6 interactive + 8 §7 disabled). Visual confirm → live round. |
| AC-2 | mobile bottom-nav legible + active color | **PASS (after fix)** | mobile links: color ink-soft `rgb(93,107,94)`, active(calc) `rgb(164,113,26)`, `text-decoration:none`, `display:flex`/`column`. |

Screenshots captured (desktop 1280×800 + mobile 375×812): top-nav with amber-active "מחשבון" pill + brand +
account pill + search; mobile 4-item bottom bar (icon-over-label) with amber-active calc; white-green ground +
green footer dot in both.

## 2. Defects found + fixed (this round) — all build-domain, fixed by team_100 at `f85691e`

| # | Severity | Defect | Root cause | Fix |
|---|----------|--------|-----------|-----|
| F-QA-01 | **BLOCKER (AC-1)** | `body` rendered cream `#f6f1e3`, not `#f8fbf8` | `gj.css:4–10` leftover v1 cream `:root` redefined `--gj-paper`/`-2`/`-3`/`--gj-ink`/`-soft`/`--gj-line`; gj.css loads after tokens.css → overrode v2. The build deleted the `.gj-shell` chrome block (lines 27–96) but not this top-of-file `:root`. The LOD400 D1 grep targeted `var(--paper)` consumers, not `--gj-*` *re*definitions — spec gap. | Removed the cream redefinitions from gj.css; tokens.css v2 values now win. |
| F-QA-02 | MAJOR | footer status dot transparent | served tokens.css missing `--status-{fresh,aging,stale,error}` (in design tokens.css §status, never ported) | added the status ramp to tokens.css |
| F-QA-03 | MINOR | status dot collapsed to width:0 | `.dot` is a flex child with `flex-shrink:1` | `.sh__foot .dot { flex:none }` |
| F-QA-04 | MAJOR | mobile bottom-nav links default blue/underlined, no active color | SSoT styles only `.sh__nav a`, not `.sh__nav--mobile a` (gap present in the design board too) | added faithful mobile-nav color + per-surface active; **flagged for team_35 to confirm in Class B** |

## 3. Verdict
**PASS_WITH_FIXES** (internal). All shell + palette ACs verified green after the 4 fixes. This internal QA does
**not** substitute for team_190 L-GATE_V (non-Claude/Cursor), which must add the live-data per-page round once the
branch is deployed (or a local DB is stood up). The 4 fixes + the spec gaps they expose are carried into the
L-GATE_V mandate and the LOD400 addendum.

---
*Method: `php -S 127.0.0.1:8099 -t sfa_delivery` + static `.sh` harness + Claude preview (computed-style inspect,
resize 1280/375, screenshots). Harness removed post-run; evidence = computed measurements above.*
