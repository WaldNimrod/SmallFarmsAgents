# BUILD REPORT — SFA-S003-P004-WP-CB-UI-CLASSB (fix-all) — team_10 — v1.0.0

**Date:** 2026-06-02
**From:** team_10 (sfa_build, Claude Sonnet)
**To:** team_100 (Chief Architect)
**Dispatch:** `DISPATCH_sfa_build_FIXALL_2026-06-02_v1.0.0.md`
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02`
**Source verdict:** team_50 `VISUAL_QA_REPORT_2026-06-02_v1.0.0.md` (PASS_WITH_FINDINGS)

---

## Result summary

All 7 findings fixed. 0 findings required server-side changes. 2 findings explicitly NOT changed per dispatch §2.

| Finding | Severity | Status |
|---------|----------|--------|
| F-1 (MAJOR-1) | hub-intro blank-left wide viewport | FIXED |
| F-2 (MAJOR-2 + MINOR-3) | community banner empty beige box | FIXED |
| F-3 (MINOR-1) | search no-match CTA glyph alignment | FIXED |
| F-4 (MINOR-4) | account logo overlaps nav | FIXED |
| F-5 (MINOR-5) | market `<th>` inline styles | FIXED |
| F-6 (MINOR-6) | footer קהילה self-link on /community | FIXED |
| F-7 (COSMETIC-1) | nav class trailing space | FIXED |
| MINOR-2 | hub stats hardcoded | NOT CHANGED (design-intended) |
| COSMETIC-2 | canonical/og = production | NOT CHANGED (correct in prod) |

---

## Per-finding detail

### F-1 — MAJOR-1: hub-intro blank-left at wide viewport

**Design SSoT ref:** Board-B `hub-home` frame — intro text + stats share one bounded column aligned with the `.hub-grid`.

**Root cause:** `.sh__body--wide` had no max-width; `.hub-intro__txt { flex: 1 }` caused text to stay flush-right in RTL at full viewport width, leaving a blank left half.

**Fix — scoped to hub only (`.sh__body--wide` unchanged globally):**

`sfa_delivery/templates/pages/hub_home.php` — added `.hub-home__inner` wrapper div immediately inside `.sh__body--wide`:
```html
<!-- before (line 70): -->
<div class="sh__body--wide">
  <div class="hub-intro">…

<!-- after: -->
<div class="sh__body--wide">
<div class="hub-home__inner">
  <div class="hub-intro">…
…
</div><!-- /hub-home__inner -->
</div><!-- /sh__body--wide -->
```

`sfa_delivery/public_assets/css/classb.css` — added after `.sh__body--wide` rule (line ~33):
```css
/* hub-specific inner wrapper — caps intro + grid at Board-B frame width,
   centered, eliminates blank-left band at wide viewport. Hub-only. */
.hub-home__inner { max-width: 1100px; margin: 0 auto; }
```

---

### F-2 — MAJOR-2 + MINOR-3: community banner empty beige box

**Design SSoT ref:** Board-B L807 — `<div class="comm-banner"><img src="assets/contact.webp" alt=""/></div>`.

**Root cause:** `community.php:35` pointed at `/public_assets/img/heroes/community-banner.webp` which does not exist. The `.comm-banner` div was always rendered with `background:#f4ecdc` and no image — a bare warm-beige rectangle.

**Fix:**

`sfa_delivery/templates/pages/community.php` (lines 32–40):
```php
<!-- before: -->
<div class="comm-banner" aria-hidden="true">
  <?php
  $banner_img = '/public_assets/img/heroes/community-banner.webp';
  if (file_exists(__DIR__ . '/../../public_assets/img/heroes/community-banner.webp')):
  ?>
    <img src="…" alt="" loading="lazy" decoding="async">
  <?php endif; ?>
</div>

<!-- after: -->
<?php
$banner_candidates = [
    '/public_assets/img/contact.webp'        => __DIR__ . '/../../public_assets/img/contact.webp',
    '/public_assets/img/heroes/clients.webp' => __DIR__ . '/../../public_assets/img/heroes/clients.webp',
];
$banner_img = null;
foreach ($banner_candidates as $url => $path) {
    if (file_exists($path)) { $banner_img = $url; break; }
}
?>
<?php if ($banner_img !== null): ?>
<div class="comm-banner" aria-hidden="true">
  <img src="<?= $h($banner_img) ?>" alt="" loading="lazy" decoding="async">
</div>
<?php endif; ?>
```

The `.comm-banner` box is now only rendered when an image will actually display. Primary candidate is `/public_assets/img/contact.webp` (confirmed present). Fallback to `heroes/clients.webp`. MINOR-3 (warm beige color) is resolved because the image covers the background.

---

### F-3 — MINOR-1: search no-match CTA glyph

**Design SSoT ref:** Board-B `search-nomatch` frame L755 — `<a class="reqinfo" href="#" style="font-size:13px;padding:8px 16px">◐ בקשו להוסיף לספר</a>`.

**Fix:**

`sfa_delivery/templates/pages/search_results.php` (line 83):
```php
<!-- before: -->
<a class="reqinfo" href="/community">בקשו הוספה ←</a>

<!-- after: -->
<a class="reqinfo" href="/community">◐ בקשו הוספה</a>
```

`sfa_delivery/public_assets/css/classb.css` — added `.reqinfo` chip-style CSS after `.srch-nomatch p` (the class was used in templates but had no definition):
```css
.reqinfo {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; font-weight: 700; padding: 8px 16px;
  border-radius: var(--gj-r-pill);
  border: 1px solid color-mix(in oklch, var(--gj-leaf) 50%, var(--gj-line));
  background: color-mix(in oklch, var(--gj-leaf) 10%, var(--gj-paper));
  color: var(--gj-leaf-deep); text-decoration: none; cursor: pointer;
  transition: background .15s, border-color .15s;
}
.reqinfo:hover { background: color-mix(in oklch, var(--gj-leaf) 18%, var(--gj-paper)); border-color: var(--gj-leaf); }
```

---

### F-4 — MINOR-4: account logo overlaps nav

**Design SSoT ref:** Board-B `account` frame — logo SVG is sized within the card, not overflowing.

**Root cause:** `account_landing.php:27-29` wraps the `<svg>` in `.acct-card__mark` (a 52×52 div), but the SVG element itself had no `width`/`height` attributes. Browsers default unattributed SVG to 300×150px, causing overflow beyond the container.

**Fix:**

`sfa_delivery/public_assets/css/classb.css` (line ~341):
```css
<!-- before: -->
.acct-card__mark { width: 52px; height: 52px; margin: 0 auto 14px; }

<!-- after: -->
.acct-card__mark { width: 52px; height: 52px; margin: 0 auto 14px; display: block; overflow: hidden; }
.acct-card__mark svg { width: 100%; height: 100%; display: block; }
```

The container clips the SVG and the SVG is constrained to fill its parent — no template change needed.

---

### F-5 — MINOR-5: market table `<th>` inline styles

**Design SSoT ref:** CSS-over-inline-style mandate, no visual change.

**Fix:**

`sfa_delivery/templates/pages/market_list.php` (lines 172–174):
```html
<!-- before: -->
<th style="text-align:start;padding:8px 10px;border-bottom:1px solid var(--gj-line)">מוצר</th>
<th style="padding:8px 10px;border-bottom:1px solid var(--gj-line)">מחיר</th>
<th style="padding:8px 10px;border-bottom:1px solid var(--gj-line)">טריות</th>

<!-- after: -->
<th class="ptable__th ptable__th--start">מוצר</th>
<th class="ptable__th">מחיר</th>
<th class="ptable__th">טריות</th>
```

`sfa_delivery/public_assets/css/classb.css` — added before existing `.ptable .t-price` rule:
```css
.ptable__th { padding: 8px 10px; border-bottom: 1px solid var(--gj-line); }
.ptable__th--start { text-align: start; }
```

---

### F-6 — MINOR-6: footer קהילה self-link on /community

**Design SSoT ref:** UX — a link to the current page is a self-referential circular navigation.

**Fix:**

`sfa_delivery/templates/_layout.php` (line ~137–139):
```php
<!-- before: -->
<a href="/about">על הכלים</a> ·
<a href="/community">קהילה</a>

<!-- after: -->
<a href="/about">על הכלים</a> ·
<?php if ($active === 'community'): ?>
  <span aria-current="page">קהילה</span>
<?php else: ?>
  <a href="/community">קהילה</a>
<?php endif; ?>
```

When `$active === 'community'`, the footer link is replaced with a non-interactive `<span aria-current="page">`.

---

### F-7 — COSMETIC-1: nav class trailing space

**Design SSoT ref:** HTML cleanliness — `class="is-calc "` trailing space.

**Fix:**

`sfa_delivery/templates/_layout.php` — desktop nav (lines 115, 116) and mobile nav (lines 130, 131):
```php
<!-- before (desktop): -->
<a class="is-calc <?= $active==='calc' ? 'is-active' : '' ?>" href="/calc/">…</a>
<a class="is-market <?= $active==='market' ? 'is-active' : '' ?>" href="/market/">…</a>

<!-- after (desktop + mobile): -->
<a class="<?= trim('is-calc ' . ($active==='calc' ? 'is-active' : '')) ?>" href="/calc/">…</a>
<a class="<?= trim('is-market ' . ($active==='market' ? 'is-active' : '')) ?>" href="/market/">…</a>
```

`trim()` removes the trailing space when the route hint is not active. When active, result is `"is-calc is-active"` (no trailing space).

---

## Test results

### composer test (full delivery suite)

```
PHPUnit 10.5.63 · PHP 8.5.6
Tests: 135, Assertions: 348
OK (no failures) — 1 PHPUnit deprecation (pre-existing, unrelated)
```

Previous count: 129 tests / 341 assertions.
**6 new tests added** in `ClassBRouteTest.php`:

| New test | What it asserts |
|----------|-----------------|
| `testCommunityBannerHasImg` | `.comm-banner` div contains `<img` — image present |
| `testCommunityNoBareBeigeBannerBox` | No `.comm-banner` rendered without image content |
| `testHubHomeHasInnerWrapper` | Hub home has `.hub-home__inner` width-cap wrapper |
| `testFooterNoSelfLinkOnCommunity` | Footer has `aria-current="page"` (not `<a>`) on /community |
| `testMarketTableThHasNoInlineStyle` | Market `<th>` uses `.ptable__th` class, no `style=` attribute |
| `testNavClassNoTrailingSpace` | Nav `class="is-calc "` or `class="is-market "` trailing space absent |

---

## validate_aos result

```
29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

---

## Files changed

| File | Change |
|------|--------|
| `sfa_delivery/templates/pages/hub_home.php` | F-1: added `.hub-home__inner` wrapper div |
| `sfa_delivery/templates/pages/community.php` | F-2: banner pointed at `contact.webp`, bare-box guard |
| `sfa_delivery/templates/pages/search_results.php` | F-3: added `◐` glyph to `.reqinfo` CTA |
| `sfa_delivery/templates/pages/market_list.php` | F-5: `<th style=…>` → `<th class="ptable__th …">` |
| `sfa_delivery/templates/_layout.php` | F-6: footer קהילה self-link suppressed; F-7: nav class trailing space removed (desktop + mobile) |
| `sfa_delivery/public_assets/css/classb.css` | F-1: `.hub-home__inner` rule; F-3: `.reqinfo` chip CSS; F-4: `.acct-card__mark svg` size fix; F-5: `.ptable__th` CSS |
| `sfa_delivery/tests/ClassBRouteTest.php` | 6 new test methods for F-1/F-2/F-5/F-6/F-7 coverage |

---

## Non-fixes (per dispatch §2)

- **MINOR-2 (hub stats hardcoded):** Board-B itself shows static stats (L184/L192: "66 גידולים", "30 מוצרים"). Server-side live counts are out of Class B scope — logged for `WP-SRV-IDEAS` per team_100 note.
- **COSMETIC-2 (canonical/og = production):** Correct on the production deployment at `sfa.nimrod.bio`. Local dev discrepancy only — no change.

---

**Working tree left for team_100 to verify and commit. No git commands run.**

*Issued by team_10 (sfa_build, Claude Sonnet) · 2026-06-02*
