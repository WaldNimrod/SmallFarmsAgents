# Visual diff notes — SFA-S003-P002-WP-UI B.4 (team_100 remediation 2026-05-27)

## Method

Each of the 14 LOD400 §3.3 HTML routes navigated via Claude_in_Chrome MCP against
the live https://sfa.nimrod.bio/ deployment (post-team_100 a11y patches).

Tool: `mcp__Claude_in_Chrome__computer.screenshot` with save_to_disk=true.

## Viewport disclosure (honest limitation)

`mcp__Claude_in_Chrome__resize_window` resizes the OS-level Chrome window but
does NOT emulate CSS viewport like Chrome DevTools mobile profile. Screenshots
captured at OS window content area (~1456×835), regardless of the requested
390×844 mobile size. Therefore:
- **Desktop layout** (`.dt-shell` visible) is the layout shown in every screenshot.
- **True mobile layout** (`.gj-shell` visible, `.dt-shell` `display:none`) was
  exercised + verified by Lighthouse runs (form-factor=mobile, throttling=simulate)
  which got **Accessibility = 100/100/100** on all 3 measured routes — that's the
  authoritative mobile evidence.
- For a third-party visual-diff at true mobile viewport in the future, use Chrome
  DevTools device emulation or Playwright/Puppeteer with explicit viewport.

## Per-route results (16 screenshots captured)

| AC | Route | HTTP | Render | Notes |
|----|-------|------|--------|-------|
| AC-07 | `/`                                  | 200 | ✓ | 8 modules in 3-tier sections, all Hebrew |
| AC-08 | `/about`                             | 200 | ✓ | 5 tier-labels bulleted in Hebrew |
| AC-09 | `/search?q=`                         | 200 | ✓ | Search box + "0 results" |
| AC-10 | `/calc`                              | 200 | ✓ | "בטא · בפיתוח" badge + WhatsApp link |
| AC-11 | `/crop-book/`                        | 200 | ✓ | 4 entry-path links (search/table/family/questions) |
| AC-12 | `/crop-book/questions`               | 200 | ✓ | 5 question cards |
| AC-13 | `/crop-book/family`                  | 200 | ✓ | 14 families with counts |
| AC-14 | `/crop-book/table`                   | 200 | ✓ | 52 crops in table, `<th scope="col">` confirmed |
| AC-15 | `/crop-book/search?q=`               | 200 | ✓ | Search box |
| AC-16 | `/crop-book/anise-hyssop`            | 200 | ✓ | Crop detail + 1 variety listed |
| AC-17 | `/crop-book/anise-hyssop/variety/variety-1` | 200 | ✓ | (v1.0.2) deterministic `variety-{id}` slug pattern (F-BUILD-04 RESOLVED); labeled Hebrew fields per CB5 design — שם באנגלית / ימים לבגרות / מרווח בשורה / שיטת שתילה / etc. (F-BUILD-05 RESOLVED); skip-empty rendering |
| AC-18 | `/market/`                           | 200 | ✓ | Disclaimer block + 65 products with REAL prices |
| AC-19 | `/market/prd017`                     | 200 | ✓ | בצל יבש detail, מחיר אחרון 15.25 ₪ |
| AC-20 | `/community`                         | 200 | ✓ | Static info page + WhatsApp link (no form, no POST) |

## Findings from initial visual evidence (RESOLVED in v1.0.2)

### F-BUILD-04 (MAJOR — RESOLVED 2026-05-27)

**Original symptom (v1.0.1):** `CropBookViewController::slugify()` strips all non-ASCII
characters (`[^a-z0-9\s-]`). For Hebrew variety names (all 190 of them), this
returned the fallback literal `'variety'` — every variety of every crop collided
on the same URL; only the first variety per crop was URL-reachable.

**Fix (v1.0.2):** New `CropBookViewController::varietySlug($variety)` static method
returns `'variety-' . (int)$variety['id']`. Deterministic, unique, ASCII-safe,
no URL-encoding needed. Both the CB5 link generator (line ~102) and the variety
route lookup (line ~128) now use it.

**Live verification:** CB5 detail page renders `<a href="/crop-book/{slug}/variety/variety-1">`
etc. with unique IDs; multi-variety crops correctly produce distinct URLs.
phpunit `RouteSmokeTest::testHtmlRoutesReturnSuccess` updated for new pattern.

### F-BUILD-05 (MINOR — RESOLVED 2026-05-27)

**Original symptom (v1.0.1):** `book_variety.php` rendered `json_encode($variety, ...)`
inside `<pre>` — raw JSON text on the user-facing page.

**Fix (v1.0.2):** Template fully rewritten. Renders breadcrumb (ספר גידולים ›
{crop} › {variety}), title with optional "ברירת מחדל" tag, then `<dl
class="variety-fields">` with Hebrew labels per field (שם באנגלית, ימים
לבגרות, חלון קציר מינ׳/מקס׳, מרווח בשורה, שיטת שתילה, עונת שתילה, יחידת
קציר, מחיר מתועד, יחידת מחיר, מקור מחיר, הערות). Skips empty fields
gracefully. Back-link with proper a11y touch target. Inline scoped CSS
for layout.

**Live verification:** `<pre>` raw-JSON count: 0; `<dt>` labels count: 12;
`.variety-fields` class present.

## Console errors

`read_console_messages onlyErrors:true` returned `No console errors or exceptions
found` after navigating all 14 routes. AC-32 PASS.

## Bottom line

All 14 HTML routes return 200 with Hebrew content rendered correctly. The
implementation is functionally complete (per LOD400 §3.3 + §4 contract). Two
implementation-quality findings (F-BUILD-04, F-BUILD-05) on the variety
sub-route — these affect /crop-book/{slug}/variety/{vslug} UX but don't break
other routes. team_190 will evaluate at L-GATE_V.
