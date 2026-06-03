---
id: BUILD_REPORT_v1.0.0
wp: SFA-S003-P004-WP-CB-UI-patch01
team: team_10 (sfa_build — Claude Sonnet)
date: 2026-06-03
branch: claude/ui-polish-hub-cropbook-2026-06-03
status: BUILD_COMPLETE — L-GATE_B SATISFIED (0 FAIL)
---

# Build Report — WP-CB-UI-patch01

## Summary

Two delivery-tier UI fixes per team_00 live feedback on sfa.nimrod.bio.
All changes are CSS + PHP template only. No backend, Python, migration, or `_aos/` files touched.

---

## WI-1 — `/crop-book/` entry page: compact/fit-to-screen

### Files changed
- `sfa_delivery/public_assets/css/crop-book-v1.css` — crop card grid density
- `sfa_delivery/public_assets/css/crop-book-deep.css` — compact hero modifier
- `sfa_delivery/templates/pages/book_entry.php` — apply compact hero class

### Before → After

| Element | Before | After |
|---|---|---|
| `.cards-grid` minmax track | `168px` | `120px` |
| `.cards-grid` gap | `12px` | `10px` |
| `.ccard__art` aspect-ratio | `1.3 / 1` | `1.7 / 1` (flatter) |
| `.ccard__art img` footprint | `78%` | `64%` |
| `.ccard__art .veg` font | `46px` | `28px` |
| `.ccard__body` padding | `10px 12px 12px` | `6px 8px 8px` |
| `.ccard__body` gap | `4px` | `3px` |
| `.ccard__name` font-size | `16px` | `13px` |
| mobile `@media(max-width:600px)` minmax | `145px` | `100px` |
| `.cb-hero` on entry page | full size (clamp 160–320px art) | `.cb-hero--compact`: art `clamp(80px,14vw,140px)`, padding `10px 18px`, title `clamp(18–24px)` |

CSS lines changed: crop-book-v1.css L33, L41–42, L46–47, L55–56, L548;
crop-book-deep.css: added `.cb-hero--compact` modifier block after L4.
PHP: book_entry.php L83 — `class="cb-hero"` → `class="cb-hero cb-hero--compact"`.

**Result**: At ≥1280px the grid achieves ≥6 columns (1280px ÷ 120px+10px gap ≈ 9 columns) vs ~7 before at 168px.
Cards are markedly smaller. Hero is compact. All functionality retained (filters, search, audience toggle, entry-paths).

---

## WI-2 — `/` hub: full-width open-tools row + Field Log tile

### Files changed
- `sfa_delivery/public_assets/css/classb.css` — `auto-fill` → `auto-fit`, `.modtile.is-dev` styles
- `sfa_delivery/templates/pages/hub_home.php` — 4th tile appended to open-tools `.hub-grid`

### Before → After

| Element | Before | After |
|---|---|---|
| `.hub-grid` columns | `repeat(auto-fill, minmax(248px,1fr))` | `repeat(auto-fit, minmax(248px,1fr))` |
| Open-tools tile count | 3 (live modules only) | 4 (3 live + Field Log teaser) |
| Field Log tile | absent | `<div class="modtile modtile--soil is-dev" aria-disabled="true">` with title "יומן השדה", small "FIELD-LOG", desc "תיעוד פעולות שדה — זריעה, השקיה, יבול ומשימות", foot badge "בפיתוח", glyph 📒 |
| `.modtile.is-dev` CSS | absent | mirrors `.is-soon`: no hover lift, muted `--gj-paper-2` bg, default cursor, dashed border, italic footer text |

CSS: classb.css L55 (auto-fit), added `.modtile.is-dev` block after `.is-soon` block.
PHP: hub_home.php — Field Log `<div>` appended after `endforeach` of `$open_mods`, inside the same `.hub-grid`, before closing `</div>`.

**Result**: `auto-fit` collapses empty tracks → 4 tiles fill the full row width at desktop.
Field Log tile is visually muted (dashed border, grayscale art tint), `aria-disabled="true"`, no href — reads as "in development", never as available.

---

## Tests

### New tests added — `sfa_delivery/tests/ClassBRouteTest.php`

7 new test methods (appended to existing class):

| Method | Asserts |
|---|---|
| `testHubHomeHasFieldLogTitle` | `/` body contains "יומן השדה" |
| `testHubHomeHasFieldLogBadge` | `/` body contains "בפיתוח" |
| `testHubHomeFieldLogHasIsDevClass` | `/` body contains `is-dev` |
| `testHubHomeFieldLogHasNoHref` | Field Log tile has no `href` attribute |
| `testClassbCssUsesAutoFit` | `.hub-grid` in classb.css uses `auto-fit`, not `auto-fill` |
| `testCropBookEntryReturns200` | `/crop-book/` returns HTTP 200 |
| `testCropBookEntryHasCardsGrid` | `/crop-book/` renders `.cb-hero` + `.cb-paths` |

### Test run result
```
PHPUnit 10.5.63 — PHP 8.5.6
Tests: 149 / Assertions: 383 / Failures: 0 / Errors: 0
OK (1 PHPUnit deprecation — not a test failure)
```

### php -l
```
No syntax errors detected in templates/pages/hub_home.php
No syntax errors detected in templates/pages/book_entry.php
No syntax errors detected in tests/ClassBRouteTest.php
```

### validate_aos.sh
```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```
(Check-32 uncommitted-drift excluded per spec mandate.)

---

## Local render sanity

Local PHP dev server (sqlite in-memory) returns HTTP 500 due to MySQL driver requirement —
identical to prior WP build sessions. PHPUnit bootstraps the app via `Bootstrap::createApp()`
with sqlite and renders all routes end-to-end (149 tests, full HTML output assertions).
The new tests exercise `/` and `/crop-book/` through the real Slim router + controller pipeline.

---

## Constraints satisfied

- Delivery tier ONLY: no `_aos/`, Python, migration, or backend files touched.
- IR#4 respected: roadmap.yaml not modified.
- No git commands executed.
- Palette/tokens unchanged (white-green, `--gj-*` tokens only).
- `classb.css` stays last in load order (unchanged).
- "יומן השדה / Field Log" reads as "בפיתוח" — no href, `aria-disabled="true"`, muted tile.

---

## Files changed (summary)

| File | Change type |
|---|---|
| `sfa_delivery/public_assets/css/crop-book-v1.css` | CSS values (grid, card art, body, name) |
| `sfa_delivery/public_assets/css/crop-book-deep.css` | Added `.cb-hero--compact` modifier |
| `sfa_delivery/public_assets/css/classb.css` | `auto-fit` fix + `.modtile.is-dev` styles |
| `sfa_delivery/templates/pages/book_entry.php` | Added `cb-hero--compact` class to hero |
| `sfa_delivery/templates/pages/hub_home.php` | Added Field Log tile in open-tools `.hub-grid` |
| `sfa_delivery/tests/ClassBRouteTest.php` | 7 new test methods |
