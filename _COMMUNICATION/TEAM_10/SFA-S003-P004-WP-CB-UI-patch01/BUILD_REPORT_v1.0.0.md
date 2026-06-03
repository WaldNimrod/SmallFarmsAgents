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
| `sfa_delivery/tests/ClassBRouteTest.php` | 7 new test methods (WI-1/WI-2) |

---

## WI-3 — Hub copy + system-wide terminology

### Files changed
- `sfa_delivery/templates/pages/hub_home.php` — typo fix, term swap, `$page_sub`
- `sfa_delivery/templates/_layout.php` — default `$page_sub` fallback
- `sfa_delivery/templates/pages/community.php` — term swap in `<h2>`
- `sfa_delivery/templates/macros/market_disclaimer.php` — term swap in disclaimer bullet
- `sfa_delivery/templates/pages/hub_tiers.php` — neutralize Tend mentions
- `sfa_delivery/public_assets/css/classb.css` — one-line tagline CSS fix

### WI-3a: Typo fix — audience card label

| Location | Before | After |
|---|---|---|
| `hub_home.php:177` (audcard div) | `גינאי ביתי` | `גנן` |

Preserved `<small>GARDENER</small>` unchanged. The description "לגינה הקטנה" NOT touched (unrelated "קטנה").

### WI-3b: One-line tagline at desktop

**Before (`classb.css` ~L47):**
```css
.hub-intro p { font-size: 14.5px; line-height: 1.55; color: var(--gj-ink-soft); margin: 0; max-width: 52ch; }
```

**After:**
```css
.hub-intro p { font-size: 14.5px; line-height: 1.55; color: var(--gj-ink-soft); margin: 0; }
@media (min-width: 760px) {
  .hub-intro p { white-space: nowrap; font-size: clamp(13px, 1.2vw, 14.5px); }
}
```

- `max-width: 52ch` removed (was forcing wrap)
- At ≥760px: `white-space: nowrap` prevents line break; `clamp(13px, 1.2vw, 14.5px)` scales font so tagline fits within 1100px container without overflow
- At <760px: falls back to default (no `nowrap`) — wraps naturally, no horizontal overflow

### WI-3c: "small" → "local" term swap

| File | Line(s) | Before | After |
|---|---|---|---|
| `hub_home.php` | `$page_sub` (~L65) | `'חקלאות קטנה'` | `'חקלאות מקומית'` |
| `hub_home.php` | `<h1>` (~L76) | `לחקלאות <em>קטנה</em>` | `לחקלאות <em>מקומית</em>` |
| `hub_home.php` | `<h2>` (~L151) | `ידע פתוח לחקלאות <em>קטנה</em>` | `ידע פתוח לחקלאות <em>מקומית</em>` |
| `hub_home.php` | audcard (~L183) | `חקלאי קטן` | `חקלאי מקומי` |
| `_layout.php` | L6 default | `'חקלאות קטנה'` | `'חקלאות מקומית'` |
| `community.php` | L53 `<h2>` | `חקלאות קטנה` | `חקלאות מקומית` |
| `market_disclaimer.php` | L22 | `השוק החקלאי הקטן` | `השוק החקלאי המקומי` |

**Not touched (per spec):**
- `hub_home.php:178` — "לגינה הקטנה" (unrelated "קטנה")
- `community.php:60` — "תרומה קטנה" (unrelated "קטנה")
- `modules.php` — internal AI-art-generation prompts (not customer-facing)

### WI-3d: Tend mention disposition

| File | Location | Occurrence | Action |
|---|---|---|---|
| `hub_tiers.php` | L33 `$tier_examples['custom']['title']` | `'חיבור Tend'` (rendered in `.tier-row__eg > b` on /about) | **Neutralized** → `'נתוני שדה'` (Tend integration/connection teaser) |
| `hub_tiers.php` | L41 `$fallback_copy['custom']` | `'בדיוק לחווה שלך — חיבור Tend, יומן שדה, אינטגרציות.'` (rendered in `.tier-row__txt p`) | **Neutralized** → `'בדיוק לחווה שלך — נתוני שדה, יומן שדה, אינטגרציות ייעודיות.'` |
| `book_variety.php` | L5 (PHPdoc comment) | `extends CB5 with ... <dl><dt><dd>` — "tend" only in "extends" (English word, unrelated) | No action — not "Tend" brand |
| `book_entry.php` | L178–179 | `value="tender"` / `value="very_tender"` (HTML form values for frost resistance) | No action — not "Tend" brand |
| `book_variety.php` | No Tend brand occurrences in rendered HTML | — | No action needed |

---

## WI-4 — Hub CTA section

### Files changed
- `sfa_delivery/templates/pages/hub_home.php` — added `.hub-cta` section before closing `</div><!-- /hub-home__inner -->`
- `sfa_delivery/public_assets/css/classb.css` — added `§3.9 · HUB CTA` block at end of file
- `sfa_delivery/app/Controllers/HubController.php` — pass `contact` array to `home()` method

### Markup summary
Two-card layout inside `.hub-cta`:
1. **Secondary** (`.hub-cta__card--secondary`): links to `/community`, copy "שתפו אותנו במידע והשלמות לספר"
2. **Primary** (`.hub-cta__card--primary`): links to `https://wa.me/972547776770` (from `$contact['whatsapp']` or hardcoded fallback), copy "ספרו לנו מה תרצו שנפתח לחווה שלכם"

### CSS summary
- Desktop: 2-column grid (`grid-template-columns: 1fr 1fr`)
- Mobile (≤680px): stacked (`grid-template-columns: 1fr`)
- Secondary card: palette-consistent white-green outline, `.hub-cta__card--secondary` fills with muted leaf-tinted bg
- Primary card: `background: var(--gj-leaf-deep)` filled, white text — visually most prominent
- No new palette tokens; reuses `--gj-leaf-deep`, `--gj-shadow-*`, `--gj-r-*`

---

## Tests — WI-3 + WI-4

### New tests added (appended to ClassBRouteTest.php) — 9 additional methods

| Method | Asserts |
|---|---|
| `testHubHomeGardenerLabelIsGnan` | `/` contains "גנן", does NOT contain "גינאי ביתי" |
| `testHubHomeUsesLocalFarmerTerm` | `/` contains "חקלאי מקומי", does NOT contain "חקלאי קטן" |
| `testHubHomeUsesLocalAgricultureTerm` | `/` contains "חקלאות מקומית", does NOT contain "חקלאות קטנה" |
| `testAboutHasNoTendIntegrationCopy` | `/about` does NOT contain "חיבור Tend" or "חיבור ל-Tend" |
| `testHubHomeHasCtaSection` | `/` contains `hub-cta` |
| `testHubCtaHasCommunityLink` | `/` `.hub-cta` contains `href="/community"` |
| `testHubCtaHasWhatsAppLink` | `/` `.hub-cta` contains `wa.me` |
| `testHubCtaHasPrimaryCard` | `/` contains `hub-cta__card--primary` |
| `testHubCtaHasContributionText` | `/` contains "שתפו אותנו במידע" |
| `testHubCtaHasFeatureRequestText` | `/` contains "ספרו לנו מה תרצו שנפתח" |

### Test run result (WI-1+2+3+4 combined)
```
PHPUnit 10.5.63 — PHP 8.5.6
Tests: 159 / Assertions: 397 / Failures: 0 / Errors: 0
OK (1 PHPUnit deprecation — not a test failure)
```

### php -l (WI-3+4 touched files)
```
No syntax errors detected in templates/pages/hub_home.php
No syntax errors detected in templates/pages/hub_tiers.php
No syntax errors detected in templates/pages/community.php
No syntax errors detected in templates/macros/market_disclaimer.php
No syntax errors detected in templates/_layout.php
No syntax errors detected in app/Controllers/HubController.php
No syntax errors detected in tests/ClassBRouteTest.php
```

### validate_aos.sh (WI-3+4 session)
```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## Files changed — full WI-1 through WI-4 summary

| File | Change type |
|---|---|
| `sfa_delivery/public_assets/css/crop-book-v1.css` | CSS values (grid, card art, body, name) — WI-1 |
| `sfa_delivery/public_assets/css/crop-book-deep.css` | Added `.cb-hero--compact` modifier — WI-1 |
| `sfa_delivery/public_assets/css/classb.css` | `auto-fit` fix + `.modtile.is-dev` styles + tagline nowrap + `.hub-cta` section — WI-2/WI-3/WI-4 |
| `sfa_delivery/templates/pages/book_entry.php` | Added `cb-hero--compact` class to hero — WI-1 |
| `sfa_delivery/templates/pages/hub_home.php` | Field Log tile + term swaps + גנן typo fix + hub-cta section — WI-2/WI-3/WI-4 |
| `sfa_delivery/templates/_layout.php` | Default `$page_sub` term swap — WI-3 |
| `sfa_delivery/templates/pages/community.php` | `<h2>` term swap — WI-3 |
| `sfa_delivery/templates/macros/market_disclaimer.php` | Disclaimer bullet term swap — WI-3 |
| `sfa_delivery/templates/pages/hub_tiers.php` | Neutralize Tend integration copy — WI-3 |
| `sfa_delivery/app/Controllers/HubController.php` | Pass `contact` to `home()` — WI-4 support |
| `sfa_delivery/tests/ClassBRouteTest.php` | 16 total new test methods (7 WI-1/2 + 9 WI-3/4) |
