---
id: BUILD_REPORT_WP-CB-UI-FIDELITY_team10_v1.2.0
from: team_10 (Builder, Claude Sonnet)
to: team_100 (Chief Architect)
date: 2026-06-04
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
branch: claude/ui-polish-hub-cropbook-2026-06-03
supersedes: BUILD_REPORT_v1.1.0.md
---

# BUILD_REPORT v1.2.0 — UI Polish delta (A1 / B1 / C1 / A3)

Four render-layer fixes applied to `sfa_delivery/` only. Zero git operations; tree left dirty for team_100 to commit.

---

## Files changed

| File | Lines changed |
|------|--------------|
| `sfa_delivery/public_assets/css/crop-book-v1.css` | L33, L28+29, L550, L563 |
| `sfa_delivery/app/Controllers/CropBookViewController.php` | const WC_ART (L293–L337, expanded) |
| `sfa_delivery/templates/pages/book_entry.php` | `$wc_art_map` (L79, expanded) |
| `sfa_delivery/tests/CropCardIconTest.php` | new data-driven regression test added |
| `sfa_delivery/tests/ClassBRouteTest.php` | `testCropBookCssUsesCompactGrid` updated to assert restored team_35 value |

---

## Fix A1 — card size (team_35 values restored)

**`sfa_delivery/public_assets/css/crop-book-v1.css`**

- L33 `.cards-grid`: `minmax(120px, 1fr)` → `minmax(168px, 1fr)`, `gap:10px` → `gap:12px`
- L550 `@media (max-width:600px)` `.cards-grid`: `minmax(100px, 1fr)` → `minmax(140px, 1fr)`

Stale ClassBRouteTest assertion (was checking ≤128px / the shrunken patch01 value) updated to assert `minmax(168px, 1fr)`.

---

## Fix B1 — crop-page centered container

**`sfa_delivery/public_assets/css/crop-book-v1.css` L563**

```
before: .cb-crop-detail { max-width: 100%; overflow-x: clip; }
after:  .cb-crop-detail { max-width: 1120px; margin-inline: auto; overflow-x: clip; }
```

---

## Fix A3 — toggle alignment

**`sfa_delivery/public_assets/css/crop-book-v1.css` L28–29**

```
before: .aud-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }

after:  .aud-head { display: flex; align-items: center; justify-content: flex-start; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
        .aud-head__sub { margin-inline-start: auto; }
```

Result: h2 title + `.aud` switch sit together on the start side; `.aud-head__sub` count is pushed to the far (inline-end) side. The switch no longer floats centered.

---

## Fix C1 — slug→art recovery (plural DB slug aliases)

### DB slug verification

Ran: `docker exec oma-postgres psql -U oma -d organic_market_agent -tAc "SELECT lower(regexp_replace(coalesce(name_en,name_he),'[^a-zA-Z0-9]+','-','g')) FROM crops ORDER BY 1;"`

All 14 proposed plural slug aliases confirmed present in DB output.

### Existing `wc-*.png` files confirmed

```
wc-basil.png  wc-beet.png  wc-broccoli.png  wc-bush-bean.png  wc-cabbage.png
wc-carrot.png  wc-chard.png  wc-cucumber.png  wc-dill.png  wc-eggplant.png
wc-fennel.png  wc-garlic.png  wc-ginger.png  wc-kale.png  wc-leek.png
wc-lettuce.png  wc-melon.png  wc-onion.png  wc-parsley.png  wc-pea.png
wc-pepper.png  wc-pole-bean.png  wc-radish.png  wc-scallion.png  wc-spinach.png
wc-tomato.png  wc-turmeric.png  wc-zucchini.png
```

### Added slug→art pairs (same in both `WC_ART` const + `$wc_art_map`)

| DB slug | wc-*.png |
|---------|----------|
| `carrots` | `wc-carrot.png` |
| `tomatoes` | `wc-tomato.png` |
| `cucumbers` | `wc-cucumber.png` |
| `onions` | `wc-onion.png` |
| `peppers` | `wc-pepper.png` |
| `peas` | `wc-pea.png` |
| `beets` | `wc-beet.png` |
| `radishes` | `wc-radish.png` |
| `melons` | `wc-melon.png` |
| `leeks` | `wc-leek.png` |
| `cherry-tomato` | `wc-tomato.png` |
| `summer-squash` | `wc-zucchini.png` |
| `onions-scallions` | `wc-scallion.png` |
| `beans-default-pole-climbing-` | `wc-pole-bean.png` |

### Art coverage after fix

| State | Count |
|-------|-------|
| Singular keys already working (before this fix) | 28 |
| New plural aliases added (now also render art) | 14 |
| **Total mapped slugs** | **42** |

### DB slugs still with NO watercolor art (no matching wc-*.png file exists)

The following DB slugs have no art file — they render the generic glyph (expected, no file to map to):

`anise-hyssop`, `artichokes`, `arugula`, `bay`, `blackberry`, `cauliflower`, `celery`,
`chickpea`, `chicory`, `chinese-lantern`, `chives`, `cilantro`, `cress`, `edamame`,
`fava-bean`, `hibiscus`, `jerusalem-artichokes`, `jicama`, `kohlrabi`, `lemon-balm`,
`lemon-verbena`, `lettuce-salad-mix`, `lovage`, `mint`, `new-zealand-spinach`, `okra`,
`oranges`, `pac-choi-bok-choy-`, `potato`, `sage`, `sesame`, `soybean`, `strawberry`,
`sunflower`, `sweet-corn`, `sweet-potato`, `tarragon`, `thyme`, `turnips`, `watermelon`,
`wheat`, `winter-squash`

(42 DB crops without art; no action required — files simply don't exist yet.)

---

## Regression test added

**`sfa_delivery/tests/CropCardIconTest.php`** — new `testPluralSlugResolvesToWcArt()` method with `pluralSlugArtProvider()` data provider.

Asserts all 14 plural slug aliases are present in `WC_ART` constant via ReflectionClass (no DB or rendered template required). Guards against silent regression of the singular-only map.

---

## Verification results

### `php -l` (all edited PHP files)

```
No syntax errors detected in app/Controllers/CropBookViewController.php
No syntax errors detected in templates/pages/book_entry.php
No syntax errors detected in tests/CropCardIconTest.php
No syntax errors detected in tests/ClassBRouteTest.php
```

### `composer test`

```
PHPUnit 10.5.63  —  PHP 8.5.6
Tests: 182, Assertions: 485, PHPUnit Deprecations: 1.
OK (0 failures, 0 errors)
```

All 182 tests pass including the new plural-slug regression tests (14 data-driven cases via `testPluralSlugResolvesToWcArt`).

---

*No commits made. Tree left dirty on branch `claude/ui-polish-hub-cropbook-2026-06-03` for team_100.*
