---
report: BUILD_REPORT_WI8_v1.0.0
work_item: WI-8
work_package: WP-CB-UI-patch01
team: team_10 (sfa_build)
date: 2026-06-04
branch: claude/ui-polish-hub-cropbook-2026-06-03
status: COMPLETE — no commit (team_100 commits)
---

# WI-8 Build Report — /crop-book/table Mobile Overflow Fix

## Summary

Fixed horizontal overflow on `/crop-book/table` at 375px mobile viewport.
The fix is a single CSS rule addition to `crop-book-deep.css`.
Composer tests: 167/167 PASS. validate_aos.sh: 0 FAIL. PHP lint: clean.

---

## Diagnosis

### CDP DOM-Walk Result (live site, 375px viewport)

**Document:** `scrollWidth=517 clientWidth=375` — 142px overflow confirmed.

**Offending element:** `table.dt-table` — the root cause element.

```
table.dt-table
  boundRight=498  boundWidth=560  scrollW=560  clientW=560
  minWidth=560px  maxWidth=none   display=table  overflowX=visible
```

The `.dt-table-wrap` WAS correctly set to `overflow-x: auto` (WI-7 fix) and DID clip
the 560px table within its 339px content area. However the document's `scrollWidth`
was still 517px.

### Root Cause: RTL Coordinate System Leak

Chain analysis (all at 375px, live site):

| Element          | left | right | width | scrollW | clientW | overflowX |
|-----------------|------|-------|-------|---------|---------|-----------|
| `html`           | 142  | 517   | 375   | **517** | 375     | visible   |
| `body.sfa-app`   | 142  | 517   | 375   | 375     | 375     | visible   |
| `.sh`            | 142  | 517   | 375   | 375     | 375     | visible   |
| `.sh__body`      | 142  | 517   | 375   | 375     | 375     | visible   |
| `.cb-table-page` | 160  | 499   | 339   | 339     | 339     | visible   |
| `.dt-table-wrap` | 160  | 499   | 339   | **560** | 337     | **auto**  |
| `.dt-table`      | -62  | 498   | 560   | 560     | 560     | visible   |

`windowScrollX = -142` — this is the diagnostic key.

In `<html dir="rtl">` documents, Chrome places the scroll origin at the RIGHT
edge. The horizontal scroll position starts at a negative value (RTL convention).
`document.documentElement.scrollWidth` = 517 = clientWidth(375) + |scrollX|(142).
The 142px "overflow" is the RTL-origin extent: the portion of the layout that
lies to the LEFT of the initial viewport in RTL coordinate space.

The `.dt-table-wrap` properly provides a scroll container (`overflow-x: auto`),
and the 560px table IS visually clipped within it. But the RTL scroll offset
from the table's left-side overflow LEAKS UP to `<html>.scrollWidth` because
no ancestor has `overflow-x` set to a clipping value.

### Why scrollWidth = 517 specifically

`.dt-table-wrap.scrollW = 560` (the table inside the wrapper).
`.dt-table-wrap.clientW = 337` (the wrapper's content box, 339 - 2px border).
In RTL, the initial scroll position of `.dt-table-wrap` is at the RIGHT end
(showing the first Hebrew columns). The leftmost 221px of table content are
"scrolled out" to the left. This RTL overflow propagates to `<html>.scrollWidth`
because all ancestors have `overflow-x: visible`.

---

## Fix

### File changed

`sfa_delivery/public_assets/css/crop-book-deep.css`

### CSS added (lines 144–160 approximate)

```css
/* WI-8: .cb-table-page gets overflow-x:clip to prevent the RTL-origin layout
   width (scrollX starts negative in RTL) from leaking into the document
   scrollWidth. clip does not create a scroll context, so .dt-table-wrap's
   own overflow-x:auto scroll continues to work normally. */
.cb-table-page {
  overflow-x: clip;
}
```

Additionally, added `min-width: 0` to `.dt-table-wrap` (defensive flex child
rule, though not strictly required here since `.dt-table-wrap` is a block child
of a block container):

```css
.dt-table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--gj-line);
  border-radius: 10px;
  margin-bottom: 12px;
  min-width: 0;           /* WI-8: defensive */
}
```

### Why `overflow-x: clip` (not `hidden`)

- `clip` clips without creating a scroll container — so `.dt-table-wrap`'s own
  `overflow-x: auto` scroll REMAINS FUNCTIONAL (users can scroll the table).
- `hidden` would also work visually but creates a scroll container on
  `.cb-table-page`, potentially interfering with sticky headers or position:fixed
  descendants.
- `overflow-x: clip` is supported in Chrome 90+, Firefox 81+, Safari 16+.

### Scope

Only `.cb-table-page` (the section wrapping `/crop-book/table` content) is
affected. Other pages (`/crop-book/lettuce/`, `/market/{slug}`) do not use this
class — they are unaffected.

---

## Verification

### Local static HTML test (CDP, dependency-free)

Reproduced the RTL table structure in `/tmp/test_overflow_fix.html` with
`<html dir="rtl">` + the same CSS chain. Confirmed before/after:

| Viewport | Before fix | After fix |
|----------|-----------|-----------|
| 375px    | scrollWidth=517, overflow=YES | **scrollWidth=375, overflow=NO** |
| 768px    | N/A        | **scrollWidth=768, overflow=NO** |
| 1440px   | scrollWidth=1440, overflow=NO | **scrollWidth=1440, overflow=NO** |

Note: Local PHP server returns 500 (DB unavailable on this machine — expected,
Postgres lives on waldhomeserver). Static HTML test is authoritative for the
CSS geometry check.

### Live site note

The live site at `sfa.nimrod.bio/crop-book/table` will be verified by team_100
after deploy via the standard `qa_probe.mjs` run. The CSS is the only delivery
artifact — no PHP template changes.

### composer test

```
Tests: 167, Assertions: 407 — OK (1 pre-existing PHPUnit deprecation, not a test failure)
```

### PHP lint

```
No syntax errors detected in templates/pages/book_table.php
```

### validate_aos.sh

```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## Files Changed

| File | Change |
|------|--------|
| `sfa_delivery/public_assets/css/crop-book-deep.css` | Added `.cb-table-page { overflow-x: clip }` + `min-width: 0` to `.dt-table-wrap` |

No template changes. No other CSS files touched.

---

## DO NOT COMMIT — team_100 commits.
