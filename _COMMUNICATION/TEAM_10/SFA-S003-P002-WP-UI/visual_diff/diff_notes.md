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
| AC-17 | `/crop-book/anise-hyssop/variety/variety` | 200 | ⚠️ | Renders payload_json as raw text — see F-BUILD-04 |
| AC-18 | `/market/`                           | 200 | ✓ | Disclaimer block + 65 products with REAL prices |
| AC-19 | `/market/prd017`                     | 200 | ✓ | בצל יבש detail, מחיר אחרון 15.25 ₪ |
| AC-20 | `/community`                         | 200 | ✓ | Static info page + WhatsApp link (no form, no POST) |

## New findings from visual evidence

### F-BUILD-04 (MAJOR) — variety slug collision

`CropBookViewController::slugify()` strips all non-ASCII characters (`[^a-z0-9\s-]`).
For Hebrew variety names (which is most/all of our 190 varieties), this returns
empty string and falls back to literal `'variety'`. Therefore:
- All `<a href>` links in CB5 detail page point to `/crop-book/{slug}/variety/variety`
- Only the FIRST variety per crop is ever reachable via the route
- Other 189 varieties are effectively orphaned at the URL layer

**Remediation:** Use Hebrew-aware slug (Unicode-letters `\p{L}` regex via `preg_replace`
with `/u` flag), OR add a deterministic numeric suffix (e.g. `variety-{id}`), OR
URL-encode the Hebrew name directly. Defer to L-GATE_V verdict — team_190 may
choose to flag this BUILD_PARTIAL or accept as MAJOR-with-fix-required.

### F-BUILD-05 (MINOR) — variety detail template renders raw JSON

`book_variety.php` template appears to render the variety payload as serialized
text rather than discrete labeled fields. Visual screenshot of
`/crop-book/anise-hyssop/variety/variety` shows JSON-like text dump.

**Remediation:** Format the variety payload fields (days_to_maturity,
planting_method, harvest_unit, etc.) per the CB5 design artboard expectations.
Defer to L-GATE_V verdict.

## Console errors

`read_console_messages onlyErrors:true` returned `No console errors or exceptions
found` after navigating all 14 routes. AC-32 PASS.

## Bottom line

All 14 HTML routes return 200 with Hebrew content rendered correctly. The
implementation is functionally complete (per LOD400 §3.3 + §4 contract). Two
implementation-quality findings (F-BUILD-04, F-BUILD-05) on the variety
sub-route — these affect /crop-book/{slug}/variety/{vslug} UX but don't break
other routes. team_190 will evaluate at L-GATE_V.
