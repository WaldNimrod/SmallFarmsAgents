# BUILD DISPATCH — SFA-S003-P004-WP-CB-UI-CLASSB (QA fix-all) — team_100 → team_10 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_10 (sfa_build, Claude **Sonnet** sub-agent)
**Gate:** L-GATE_B (remediation build)
**Authority:** team_00 directive this session — *"fix ALL findings, not just the MAJORs, then resubmit to L-GATE_V."*
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02` (work in the existing working tree; **do NOT run any git command** — team_100 owns all git state per IR#4 + the subagent-git-isolation guard).
**Source verdict:** team_50 `VISUAL_QA_REPORT_2026-06-02_v1.0.0.md` (PASS_WITH_FINDINGS — 2 MAJOR, 6 MINOR, 2 COSMETIC).
**Design SSoT:** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html` (the delivered design — fix TO match it, never guess).

## 0. Cross-engine + scope guard
- IR#1: you are **Claude Sonnet**; team_100 (Opus) will independently verify + own git. team_190 (non-Claude) gates L-GATE_V.
- **Delivery tier ONLY** — you may edit `sfa_delivery/templates/**`, `sfa_delivery/public_assets/css/classb.css`, `sfa_delivery/tests/**`. **No** `_aos/`, **no** Python, **no** migration, **no** LOCKED backend, **no** server-side feature.
- **Do NOT run git** (no add/commit/checkout/branch/stash). Make file edits, run tests to self-verify, report the diff.
- If any fix appears to need a server-side change, STOP and report it for `WP-SRV-IDEAS` (do not build it).

## 1. Fixes (each grounded in the design SSoT + verified file:line)

### F-1 — MAJOR-1: hub-intro blank-left at wide viewport (`/`)
- **Root cause:** `classb.css:32` `.sh__body--wide { padding: … }` has **no max-width**; `.hub-intro p` caps at `52ch` (`classb.css:41`) so at full width the text hugs the RTL right edge and the `.hub-intro__stats` pills sit at the far left, leaving a blank middle/left band.
- **Design intent (Board-B L166–175):** a balanced single band — `.hub-intro__txt` (h1+p) on the right, two `.hub-intro__stats` tier pills on the left, aligned with the `.hub-grid` below. **There is NO left hero image** in the design.
- **Fix:** constrain the hub content so the intro band and the modtile grid share one max-width and read as the bounded Board-B frame (e.g. a `max-width` cap on the hub content wrapper / `.hub-intro` + `.hub-grid`, centered, matching the grid's natural width). Match Board-B proportions; verify at ≥1280px the intro no longer leaves a blank left half. Scope the cap to the hub (do not alter `.sh__body--wide` globally if other wide pages rely on it).

### F-2 — MAJOR-2 + MINOR-3: community banner empty beige box (`/community`)
- **Root cause:** `community.php:35` points at `'/public_assets/img/heroes/community-banner.webp'` which **does not exist**; `.comm-banner` (`classb.css:437`) has `background:#f4ecdc` + `aspect-ratio:24/7`, so with no `<img>` it renders as a bare warm-beige rectangle (this is BOTH MAJOR-2 and MINOR-3).
- **Design intent (Board-B L807):** `<div class="comm-banner"><img src="assets/contact.webp" …/></div>` — a real banner image.
- **Fix:** point the banner at an existing asset — `/public_assets/img/contact.webp` exists (Board-B uses `contact.webp`); `clients.webp` is an alternative. Render the `<img>` (lazy/async, empty alt — decorative). Keep the `file_exists` guard but **only render the `.comm-banner` box when an image will actually display** (no bare beige box ever). Confirm the warm `#f4ecdc` wash is fully covered by the image (M-3 resolved).

### F-3 — MINOR-1: search no-match CTA vs Board-B (`/search?q=<no-match>`)
- Board-B (§3.5 note L774) intends the same **"◐ בקשו" request CTA** the MISSING cue uses. Live shows a `.srch-nomatch` "בקשו הוספה ←" link to `/community` — functionally compliant but verify it matches the Board-B `search-nomatch` CTA affordance/styling (the `◐` request glyph + chip-style button if the frame shows one). Align the CTA markup/class to the Board-B request affordance. Keep the `/community` (contribute) destination.

### F-4 — MINOR-4: SFA logo overlaps nav on `/account`
- `account_landing.php:28` renders an in-page `<svg><use href="#sfa-logo"/></svg>` (acct hero logo) that visually collides with the shell `.sh__mark` at top-right. Fix the overlap: reposition/space the acct hero block below the shell bar, or drop the in-page logo (the shell already provides the brand mark). Match Board-B account frame.

### F-5 — MINOR-5: market table headers use inline styles (`/market/`)
- `market_list.php:172–174` use `<th style="…">`. Move to a CSS class (e.g. `.pcard-table th` / `.mkt-table th`) defined in `classb.css`; remove the inline `style=` attributes. No visual change.

### F-6 — MINOR-6: footer "קהילה" self-reference on `/community`
- `_layout.php:138` `<a href="/community">קהילה</a>` links to the current page when on `/community`. Suppress/disable (or mark `aria-current`) the footer קהילה link when `$active`/route is community. Minor, non-destructive.

### F-7 — COSMETIC-1: nav route-hint trailing space
- `_layout.php:115,116,130,131` produce `class="is-calc "` (trailing space when not active). Trim the class output (e.g. wrap in `trim(...)`), preserving the `is-active` behavior. Apply to both desktop and mobile nav.

## 2. Explicit NON-fixes (do NOT change — report only)
- **MINOR-2 (hub stats hardcoded):** Board-B itself shows static stats (L184/L192: "66 גידולים", "30 מוצרים"). Making them live = a **server-side** change → out of Class B scope (team_00 Q4 rule). team_100 logs a `WP-SRV-IDEAS` entry; leave the UI as the design intends (static from `MODULES_REGISTRY.yaml`).
- **COSMETIC-2 (canonical/og = production):** correct **on production** (the live site IS `sfa.nimrod.bio`). Only "wrong" in local dev. No change.

## 3. Tests + self-verification
- Update/extend `sfa_delivery/tests/ClassBRouteTest.php` to assert the fixes (community banner `<img>` present + no bare box; hub intro width container; footer no self-link on community; `th` has no inline `style`; nav class has no trailing space).
- Confirm the full delivery suite is green: `composer test` (the prior stale `CropBookV1RouteTest::testCalcExportPdfReturnsPrintHtml` was realigned to `/calc/print` in commit 92f482a — verify no residual failure; if it still fails, align it to `/calc/print` as a test-harness fix).
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → expect **0 FAIL** (ignore the Check-32 "uncommitted drift" line — team_100 commits).

## 4. Report
Write `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-CLASSB/BUILD_REPORT_FIXALL_v1.0.0.md`: per-finding fix (file:line, before→after), the design-SSoT reference, test results (composer count + new asserts), validate_aos result, and the exact list of files changed. **Do not commit** — hand the working tree to team_100.
