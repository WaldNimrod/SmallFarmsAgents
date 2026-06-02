# VISUAL QA REPORT — WP-CB-UI-CLASSB
**Report:** `VISUAL_QA_REPORT_2026-06-02_v1.0.0.md`
**Date:** 2026-06-02 · **Team:** team_50 (QA & Functional Acceptance)
**Build:** main @ `0f5ea64` · **Mandate:** `QA_MANDATE_visual_2026-06-02_v1.0.0.md`
**Reference:** Board-B — `SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html`

---

## Overall Verdict: PASS_WITH_FINDINGS

No BLOCKERs. Two MAJORs (one structural — RTL hero alignment vs design board — and one incomplete component). Six MINORs and two COSMETICs. The Class B functional specification is implemented correctly; the visual delta from Board-B is limited to layout divergences that are cosmetic/acceptable on RTL but should be verified by team_35 against their intent.

---

## Environment

| Item | Value |
|------|-------|
| Server | Local PHP 8.5.6 built-in, port 8099, router with `DB_DSN=sqlite:/tmp/sfa-qa.db` |
| DB | SQLite empty-state (no production data); one test product added for market detail |
| CSS/JS | All static assets served from `sfa_delivery/public_assets/` — 200 OK |
| Design ref | Board-B served locally port 8097 |
| Data mode | **Empty-state** — market product (עגבנייה, 0 price reports) added for detail QA |

**Impact of empty-state:** Shell/layout/palette checks are fully valid. Product cards, search rows, and market history render in honest-data empty states, which is exactly what the mandate tests. No data was fabricated.

---

## Per-Surface Summary Table

| Surface | Route | Desktop Fidelity | Mobile Shell | Key Findings |
|---------|-------|-----------------|--------------|--------------|
| Hub / Home | `/` | PASS_WITH_FINDINGS | PASS | MAJOR-1: hero/intro left column blank (RTL layout diverges from design) |
| Market list | `/market/` | PASS | PASS | mkt-disc present, emptybox on empty DB, toggle present |
| Market detail | `/market/{slug}` | PASS | PASS | rangesel 7י/28י active, 90י/שנה disabled; emptybox on empty history |
| Search (match) | `/search?q=…` | PASS | PASS | srow shows price only, no min/max/source counts |
| Search (no-match) | `/search?q=xyz` | PASS | PASS | srch-nomatch + request CTA present |
| Community | `/community` | PASS_WITH_FINDINGS | PASS | MAJOR-2: manifesto hero image slot empty (beige/tan rectangle placeholder) |
| About / Tiers | `/about` | PASS | PASS | 5 tier rows rendered, all classb assets |
| Account | `/account` | PASS | PASS | "בקרוב" labels present, form disabled |
| App-shell (all) | every route | PASS | PASS | See shell detail below |

---

## Check-by-Check Results

### 1. Visual Fidelity vs Board-B

**Background palette:** `body { background: var(--gj-paper) }` → computed `rgb(248, 251, 248)` = `#f8fbf8`. Matches Board-B design spec exactly. No cream `#f5f3ec` found anywhere in computed styles.

**Typography:** `font-family: "Assistant", "Heebo", system-ui, ...` on body. Frank Ruhl Libre loaded and applied to headings via `.t-display`. Carmela loaded via `@font-face` in tokens.css and applied to `.sh__mark` wordmark. Matches Board-B specification.

**Hub (hub-home frame):**
- The 3 modtile cards (CALC β, MARKET open, CROP-BOOK open) render with watercolor art illustrations matching the design board tile art exactly (calculator, market, book watercolors).
- Hub-manifest banner, audience cards (PLANNER/FARMER/GARDENER) — all present and RTL-correct.
- MAJOR-1: See findings section — the `hub-intro` hero text (h1 "כלים פתוחים לחקלאות קטנה" + description) is RIGHT-aligned (correct for RTL) but the left ~50% of the viewport above the modtile grid is empty/blank. Design board shows the hero text integrated closer to the modtile grid. The live layout has the hero text column flush-right with empty whitespace left. This is a CSS layout issue that may not have matched Board-B intent.

**Market list (market-list frame):**
- `.mkt-disc` disclaimer banner present and always-on at top. 4 bullets visible. 7-days copy confirmed.
- Category filter chips, freshness legend (3 states), cards/table toggle all present.
- `.pcard.is-empty` renders with "—" price and "אין דיווח" for 0-report product.
- `emptybox` renders when products table is empty (correct honest-data state).

**Market detail (market-detail frame):**
- `.mkt-disc--compact` present.
- `.pgraph` + `.rangesel` with 7י/28י as `.is-active`, 90י/שנה as `.is-disabled` + `disabled` attribute.
- `.emptybox` shown for empty price history — correct.
- "תרמו מחיר" contribute prompt present.

**Search (search-results / search-nomatch frames):**
- `.srch-bar` inline search bar at top of page.
- Product results: `.srow` rows show name, unit, price only — NO min/max/source counts (MINOR F-04 compliance confirmed).
- No-match: `.srch-nomatch` + "בקשו הוספה ←" CTA linking to /community.

**Community (community frame):**
- Manifesto text ("חקלאות קטנה — ידע משותף") present.
- `.reqcard` with `.reqchip` chips (שאלה/דיווח מחיר/הצעת גידול/דיווח שנייה/שיתוף-פעולה) present.
- No activity feed — CORRECT (feed-less design as specified).
- MAJOR-2: The community page has a large beige/tan rectangle at the top (~160px tall) that appears to be a placeholder for a hero image/illustration that did not render. In the Board-B community frame, this area shows an illustration. The live build renders an empty box element (checked HTML: `<div class="community-hero">` with no content inside, just background).

**About (about-tiers frame):**
- `.tier-hero`, `.tier-list` with 5 tier rows (community/beta/coming/advanced/custom).
- Correct tier labels and descriptions.

**Account (account / account-profile frames):**
- Login form fields disabled + "כניסה — בקרוב" button disabled.
- "מערכת החשבונות בפיתוח — בקרוב" message.
- `.acct-profile` section with "עריכה — בקרוב", שם/דוא"ל with "בקרוב" sub-labels.
- No fake profile data — honest empty state.

---

### 2. Computed Palette

| Check | Result |
|-------|--------|
| `body` background computed value | `rgb(248, 251, 248)` = `#f8fbf8` — PASS |
| Cream `#f5f3ec` found in CSS | NONE — tokens.css comment says "legacy cream palette removed" — PASS |
| `--gj-paper` value in tokens.css | `#f8fbf8` — PASS |
| classb.css contains cream | NONE — PASS |

---

### 3. App-Shell

| Check | Result |
|-------|--------|
| `.sh__nav` desktop present | PASS — all routes |
| Nav links: ▤ספר גידולים / ∑מחשבון / ₪מחירון | PASS — correct order, correct glyphs |
| Active state: is-market on /market/ | PASS — `class="is-market is-active"` |
| Active state: is-active on /account | PASS — `.sh__acct.is-active` |
| No nav item active on hub `/` | PASS — no `is-active` on any nav link |
| `.sh__nav--mobile` 4-tab (ספר/מחשבון/מחירון/חשבון) | PASS — all 4 tabs present |
| `.sh__search` inline search field on desktop | PASS |
| Footer `.sh__foot` present | PASS — all routes |
| Footer content: SFA · קוד פתוח · קהילתי · על הכלים · קהילה | PASS |
| RTL `dir="rtl"` on `<html>` | PASS — `<html lang="he" dir="rtl">` |

---

### 4. The 7 Minors Actually Rendered

| Minor | Spec | Result |
|-------|------|--------|
| F-01: `.mkt-disc` always-on | Present on market list AND market detail | PASS |
| F-01: 4-bullet copy incl. "7 ימים אחרונים" | All 4 bullets rendered, "7 ימים אחרונים" in bullet מה | PASS |
| F-02: graph range labels 7י/28י active | `.rangesel` buttons: `7י` `.is-active`, `28י` `.is-active` | PASS |
| F-05: 90י/שנה DISABLED | `class="is-disabled" disabled aria-disabled="true"` on both | PASS |
| F-03: community feed-less | reqcard + reqchips present; NO feed/activity/timeline element | PASS |
| F-04: search rows no fake min/max/source | Template comment: "Do NOT show price_min/max/median/source_count" — only price shown | PASS |
| F-06: reqchips present on search no-match | "בקשו הוספה ←" CTA → /community (not individual chips but CTA present) | MINOR — design shows chip-style request but live shows text CTA link |
| classb.css loaded | Confirmed in `<link>` tag | PASS |
| classb.js loaded | Confirmed in `<script>` tag | PASS |
| cropbook-v1.js before classb.js | cropbook-v1.js: position 2 of scripts; classb.js: position 3 | PASS |

**Note on F-06:** The mandate calls for "reqchips present" on search no-match. The live search no-match page (`/search?q=xyz`) shows a `.srch-nomatch` block with a "בקשו הוספה ←" link to /community. It does NOT render the reqchip component inline on the search page. The Board-B `search-nomatch` frame shows a request CTA but its exact form could not be verified as req-chip vs link. This is flagged as MINOR — does not block gate but should be confirmed against Board-B spec.

---

### 5. Honest-Data States

| Check | Result |
|-------|--------|
| 0-report product → `.pcard.is-empty` with "—" price | PASS — `<span class="big">—</span>` + "אין דיווח" |
| 0-report product → "תרמו מחיר" CTA in detail | PASS — present in detail page |
| Empty history → `.emptybox` | PASS — multiple emptybox instances on market detail |
| No-match search → `.srch-nomatch` + request CTA | PASS |
| No fake prices, no fabricated data | PASS — no Array/NULL/undefined leakage confirmed |
| `.pcard.is-empty` class (not `.pcard.is-good` or price) | PASS |

---

### 6. States

| Check | Result |
|-------|--------|
| Hub `.is-soon` cards | 5 cards with `is-soon` + `aria-disabled="true"` — PASS |
| Account "בקרוב" labels | Present on form inputs, button, profile fields — PASS |
| Market cards⇄table toggle | `.pcard-grid[data-view="cards"]` + `[data-view="table"]` both present; `.aud__btn[data-aud="table"]` button — PASS |
| Freshness pill 3-state | `.fresh--fresh` / `fresh--mid` / `fresh--old` via legend (gj-leaf/gj-sun/gj-tomato) — PASS |

---

### 7. RTL Legibility / Raw Data

| Check | Result |
|-------|--------|
| RTL direction set | `<html lang="he" dir="rtl">` — PASS |
| No raw DB keys | 0 instances of "Array", "NULL", "undefined", "[object" across all routes — PASS |
| No stray "—" where value belongs | "—" appears only intentionally (0-report price, empty profile fields) — PASS |
| No Hebrew text truncation on nav items | Nav items render fully at desktop width — PASS |

---

## Findings by Severity

### MAJOR

**MAJOR-1: Hub hero intro — blank left column / layout gap vs Board-B**
- **Route:** `/`
- **Observation:** The `.hub-intro` section uses `display:flex` with the `.hub-intro__txt` taking `flex:1`. In RTL at wide viewport, the hero heading and description render flush to the RIGHT side of the viewport, leaving the left ~50% of the hero area empty. The Board-B `hub-home` design frame shows the hero text more centered/integrated with the modtile grid, not isolated to the far-right column.
- **Root cause:** `.hub-intro { display:flex; align-items:center; gap:20px; flex-wrap:wrap }` with only `.hub-intro__txt` + `.hub-intro__stats` as children. In RTL, flex items stack right-to-left, leaving a blank left area when no left-column content is present.
- **Impact:** Visual fidelity gap from Board-B. Hero section feels unbalanced / top-heavy empty at wide viewport.
- **Recommendation:** team_10 should verify Board-B hub-home frame intent — was there a left column element (e.g., hero image, decorative element) that was omitted? Or should the intro section be max-width centered?

**MAJOR-2: Community hero image slot empty (placeholder box visible)**
- **Route:** `/community`
- **Observation:** A large (~160px tall) beige/sand-colored rectangle appears at the top of the community page below the shell nav. This appears to be a `.community-hero` or similar container element that has a background color but no content (no illustration, no image). The Board-B `community` frame shows content in this area.
- **HTML check:** `<div class="community-hero">` contains no child elements.
- **Impact:** The community page looks broken — a visually prominent empty box is the first thing users see.
- **Recommendation:** team_10 — either supply the hero illustration/content, or remove the container if it was not intended for Class B.

---

### MINOR

**MINOR-1: Search no-match — reqchip component not rendered inline**
- **Route:** `/search?q=<no-match>`
- **Observation:** The `.srch-nomatch` block shows a text CTA "בקשו הוספה ←" linking to `/community`. The mandate specifies "reqchips present" on search no-match. The Board-B `search-nomatch` panel frame may intend an inline reqcard/chips component.
- **Severity:** Minor — the CTA does direct to the community contribution form. But if the Board-B design shows chips inline, this is a fidelity gap.

**MINOR-2: Hub stats pills — showing hardcoded values from modules.yaml**
- **Route:** `/`
- **Observation:** Hub shows "30 מוצרים · 14 מקורות" and "66 גידולים · 242 זנים" from `MODULES_REGISTRY.yaml` static values, not live DB counts. These are decorative stats from config, not real-time — may diverge from actual DB state in production.
- **Severity:** Minor — consistent with the design board frame which shows the same static stats.

**MINOR-3: Community hero empty box color is slightly warm/beige**
- See MAJOR-2 — the empty rectangle color is not `#f8fbf8` but appears slightly warmer. This compounds the MAJOR-2 finding.

**MINOR-4: Account page — SFA logo SVG partially overlaps nav bar on account page**
- **Route:** `/account`
- **Observation:** The large SFA logo icon in the top-right corner (`.sh__mark` large format?) visually overlaps/obscures part of the nav bar text at the right side.

**MINOR-5: Market pcard table toggle — table header text uses inline style**
- **Route:** `/market/`
- **Observation:** `<th style="padding:8px 10px;border-bottom:1px solid var(--gj-line)">` — table headers use inline styles rather than CSS classes. Functional but fragile.
- **Severity:** Cosmetic/Minor.

**MINOR-6: Footer "קהילה" link on community page creates circular reference**
- **Route:** `/community`
- **Observation:** The footer links to `/community` from the community page itself. Minor UX issue.

---

### COSMETIC

**COSMETIC-1: `is-calc` and `is-market` route-hint classes on nav links**
- These are present on nav `<a>` tags that are NOT active (e.g. `<a class="is-calc " href="/calc/">` — note trailing space). These are functional route-hint classes used by JS for active-state coloring and appear in the design board as well. Not a defect but the trailing space is unclean.

**COSMETIC-2: Favicon and og: tags reference production domain**
- `<link rel="canonical" href="https://sfa.nimrod.bio/">` — canonical and og: URLs point to production even in local dev. Not a rendering issue.

---

## Asset Load Order Verification

```
tokens.css          (1st — palette/typography foundation)
gj.css              (2nd — component base)
hub.css             (3rd)
community.css       (4th)
crop-book-deep.css  (5th)
crop-book-v1.css    (6th) ← cropbook-v1 CSS before classb
desktop-extras.css  (7th)
classb.css          (8th — Class B overrides last) ✓

sfa.js              (1st script)
crop-book-v1.js     (2nd) ← before classb.js ✓
classb.js           (3rd) ✓
```

**Asset load order: PASS** — classb.css loads last (correct), cropbook-v1.js loads before classb.js (correct per mandate).

---

## Route HTTP Status Matrix

| Route | HTTP | Notes |
|-------|------|-------|
| `/` | 200 | OK |
| `/market/` | 200 | OK (500 without SQLite tables) |
| `/market/{slug}` | 200 / 404 | 200 for known slug, 404 for unknown — correct |
| `/search?q=…` | 200 | OK |
| `/search?q=<no-match>` | 200 | OK |
| `/community` | 200 | OK |
| `/about` | 200 | OK |
| `/account` | 200 | OK |

---

## Data Mode Notation

All surfaces were checked with **empty-state SQLite DB**. The following visual elements were verified:
- Shell/layout/palette: fully valid (no DB needed)
- `.pcard.is-empty`, `.emptybox`, `.srch-nomatch`: verified against honest-data empty states
- Market detail: verified with 1 test product (0 price reports)
- No production MySQL data available locally — functional tests with real data must be done on deployed build (sfa.nimrod.bio)

---

## Routing to team_100

| Finding | Route |
|---------|-------|
| MAJOR-1 (hub hero layout gap) | → team_10 for assessment: intended RTL behavior or layout fix? |
| MAJOR-2 (community hero empty) | → team_10 fix required before L-GATE_V |
| MINOR-1 (search reqchip vs CTA) | → team_35 clarification: is text CTA sufficient or chip component required? |
| MINOR-2 to MINOR-6 | → batch for team_00 review |

---

*Issued by team_50 · 2026-06-02 · Evidence: `visual_evidence_2026-06-02/EVIDENCE_MANIFEST.md`*
