# BUILD_REPORT — B5: WP-UI Market page templates (Round 2)

- **Agent:** Build sub-agent B5 (Claude Sonnet)
- **Dispatched by:** team_100 (Chief Architect — Claude Opus 4.7)
- **Mandate:** `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` §3 routes 12-13 (worktree `gallant-elbakyan-727a60`)
- **LOD400 ref:** v1.0.3 §0.5 — COMPONENTS.md is SSoT (team_00 approved 2026-05-27 20:00 IDT)
- **Design contract:** `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/COMPONENTS.md` §4, §5, §8, §10
- **Data inventory ref:** `_COMMUNICATION/TEAM_100/RESEARCH_data_layer_inventory_2026-05-27_v1.0.0.md`
- **Dual-tree resolution ref:** `_COMMUNICATION/TEAM_100/RESEARCH_dual_template_tree_resolution_2026-05-27_v1.0.0.md`
- **Working tree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
- **Date:** 2026-05-27

---

## 1. Templates rewritten — paths + line counts

| # | Template | Path (relative to worktree root) | Lines | `php -l` |
|---|----------|-----------------------------------|-------|----------|
| 1 | market_list    | `sfa_delivery/templates/pages/market_list.php`    | 88  | PASS |
| 2 | market_product | `sfa_delivery/templates/pages/market_product.php` | 126 | PASS |

**Total:** 2 templates, 214 lines, **0 syntax errors** (`php -l`).

Both files use `ob_start()` → `ob_get_clean()` → `Template::render('_layout', compact(...))` — same pattern as the rest of `templates/pages/` (e.g. `hub_home.php`).

---

## 2. Per-route BEM checklist (mandate §3 vs COMPONENTS.md mapping)

### 2.1 Route 12 — `/market/` → `market_list.php`

Mandate §3 named `.gj-shell` + `.market-disclaimer` + `.gj-row`/`gj-row__big`/`gj-row__sub`. Per LOD400 v1.0.3 §0.5 (COMPONENTS.md SSoT, names verbatim):

| Mandate §3 token | Emitted token | Source | Notes |
|------------------|---------------|--------|-------|
| `.gj-shell`           | n/a (shells emit it) | shell/mobile.php + shell/desktop.php | Layout-owned, not page-owned. |
| `.market-disclaimer`  | `.mk-disclaimer` (+ `__head`, `__icon`, `__h`, `__list`, `__cta`) | `macros/market_disclaimer.php` (included at top) | COMPONENTS.md §10. Hebrew copy LOCKED. |
| `.gj-row`             | `.pcard` (+ `__head`, `__glyph`, `__name`, `__unit`, `__price`, `.big`, `.cur`, `.med`, `__range`, `.fill`, `__range-text`, `__meta`, `.sources`, `__bookcta`) | `macros/price_card.php` (included per product) | COMPONENTS.md §5 is SSoT for the price-card pattern; `.gj-row` is not defined anywhere. |
| `.gj-row__big`        | `.pcard__price .big` | inside price_card macro | |
| `.gj-row__sub`        | `.pcard__unit` + `.pcard__meta` | inside price_card macro | Holds unit + date + source count. |

Additional template-owned classes emitted by `market_list.php`:

| Class | Present? | Purpose |
|-------|----------|---------|
| `mk-chips` | ✓ | Wraps facet chips (when `$categories` non-empty). |
| `mk-chip` | ✓ | Each chip; combined with `is-active` for current facet. |
| `is-active` | ✓ | Active-chip modifier. |
| `mk-list` | ✓ | Section wrapping the product grid. |
| `mk-grid` | ✓ | Grid container for `.pcard` items. |
| `mk-empty` | ✓ | Empty-state paragraph (no products). |
| `mk-disclaimer*` | ✓ | Emitted by `market_disclaimer.php` macro (mandatory). |
| `pcard*` | ✓ | Emitted by `price_card.php` macro. |
| `contrib-strip*` | ✓ | Emitted by `contrib_strip.php` macro (`context=market.list`). |

Verification: `grep -oE 'class="[^"]+"' market_list.php` shows literal template classes `mk-chips`, `mk-chip`, `is-active`, `mk-list`, `mk-empty`, `mk-grid`. Macro-emitted classes are documented in BUILD_REPORT_B2.

Shell vars set: `$page_title='מחירון'`, `$page_sub='מחירי שוק קהילתיים'`, `$active='market'`.

### 2.2 Route 13 — `/market/{slug}` → `market_product.php`

Mandate §3 named `.gj-shell` + `.gj-pricebig` + `.gj-pricebig__big` + `.gj-pricebig__unit` + price-history table. The mandate prompt also provided a fully-fleshed structure that adds: `__head`, `__glyph`, `__name`, `__en`, `__price`, `__cur`, `__lbl`, `__meta`; plus `.gj-pricehist`, `.gj-pricehist__h`, `.gj-pricehist__table`.

| Class | Emitted? | Source |
|-------|----------|--------|
| `mk-disclaimer*` | ✓ | `market_disclaimer.php` macro (top of page, mandatory). |
| `gj-pricebig`            | ✓ | template literal |
| `gj-pricebig__head`      | ✓ | template literal |
| `gj-pricebig__glyph`     | ✓ | template literal (wraps icon SVG `<use>`) |
| `gj-pricebig__name`      | ✓ | `<h1>` |
| `gj-pricebig__en`        | ✓ | `<p>` |
| `gj-pricebig__price`     | ✓ | template literal |
| `gj-pricebig__big`       | ✓ | template literal (price number) |
| `gj-pricebig__cur`       | ✓ | template literal (currency glyph) |
| `gj-pricebig__unit`      | ✓ | template literal (unit_he) |
| `gj-pricebig__lbl`       | ✓ | template literal (median + range) |
| `gj-pricebig__meta`      | ✓ | template literal (source count, obs count, updated) |
| `gj-pricehist`           | ✓ | template literal (`<section>`) |
| `gj-pricehist__h`        | ✓ | template literal (`<h2>`) |
| `gj-pricehist__table`    | ✓ | template literal (`<table>` with `data-sort` th attrs) |
| `gj-crosslink` + `gj-crosslink--soil` | ✓ | `crosslink.php` macro with `$direction='market-to-book'` |
| `contrib-strip*`         | ✓ | `contrib_strip.php` macro (`context=market.{slug}`) |

CSS coverage note: `gj.css` currently defines selectors for `gj-pricebig`, `__big`, `__cur`, `__lbl`, `__med` (no `__head`, `__name`, `__en`, `__price`, `__unit`, `__meta`, nor `gj-pricehist*`). The mandate's structure goes beyond what's styled today. The template emits the documented BEM contract as instructed; any missing CSS rules are out of scope for B5 (template-only) and should be flagged in the assets build stream (B7).

Shell vars set: `$page_title=<product hebrew_name>`, `$page_sub='מחירון · <name>'`, `$active='market'`.

---

## 3. Disclaimer presence on both pages (`grep mk-disclaimer`)

```
$ grep -n "mk-disclaimer\|market_disclaimer" sfa_delivery/templates/pages/market_list.php sfa_delivery/templates/pages/market_product.php
sfa_delivery/templates/pages/market_list.php:13:    *   .mk-disclaimer (via market_disclaimer.php macro)
sfa_delivery/templates/pages/market_list.php:35:<?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>
sfa_delivery/templates/pages/market_product.php:11: * BEM contract (mandate §3 — `gj-pricebig` family; LOD400 §0.5 — `mk-disclaimer`, ...
sfa_delivery/templates/pages/market_product.php:13:    *   .mk-disclaimer       (via market_disclaimer.php macro)
sfa_delivery/templates/pages/market_product.php:55:<?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>
```

Both templates include `macros/market_disclaimer.php` as the **first content node** inside the `ob_start` buffer (above any chips, header, or price). The macro emits `.mk-disclaimer` with all 4 sub-bullets (what / from / why / NOT) verbatim per LOCKED Hebrew copy. Confirmed present on **both** market pages.

---

## 4. Legacy files deleted

Per dual-tree resolution recommendation A (no controllers reference `templates/market/`; only `pages/market_*.php` is wired in `MarketViewController`):

```
$ git rm sfa_delivery/templates/market/detail.php sfa_delivery/templates/market/list.php
rm 'sfa_delivery/templates/market/detail.php'
rm 'sfa_delivery/templates/market/list.php'
```

After deletion, `sfa_delivery/templates/` directory listing:

```
_layout.php
crop_book
error.php
home.php
macros
pages
shell
```

The `market/` directory no longer exists (auto-removed by `git rm` once empty). **2 legacy files deleted; 1 stale dir removed.**

---

## 5. `php -l` per file

```
$ php -l sfa_delivery/templates/pages/market_list.php
No syntax errors detected in sfa_delivery/templates/pages/market_list.php

$ php -l sfa_delivery/templates/pages/market_product.php
No syntax errors detected in sfa_delivery/templates/pages/market_product.php
```

Both files pass `php -l`. No legacy files remain to lint.

---

## 6. `validate_aos.sh` output

Ran from the worktree root:

```
$ bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
...
=================================================
RESULT: 29 PASS / 17 SKIP / 0 FAIL
=================================================
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

**0 FAIL** — invariant for this spoke preserved. (Check 33 raised a non-blocking advisory about pre-existing MSG-*.md filenames in `TEAM_100/`; unrelated to B5 scope.)

---

## 7. Unresolved questions / notes for team_100

1. **Controller data shape vs. template contract:** `MarketViewController` currently fetches `hebrew_name`, `last_price`, `last_price_date`, `freshness_days`, `unit`, `category`, `payload_json`. The mandate's template contract expects `name_he`, `price_current`, `price_median`, `price_min`, `price_max`, `source_count`, `observation_count`, `currency`, `icon_slug`, `book_slug`, `updated_he`, plus `history[].date_he` and `history[].source_count`. Both templates apply **defensive fallbacks** (e.g. `name_he ?? hebrew_name`, `price_current ?? last_price`) so they render with today's controller, but the richer aggregates (median, range, source/obs counts) will display `0.00` / `0` until the controller is upgraded. Constraint forbade controller edits — flagging for the data-layer stream.
2. **`gj-pricebig*` CSS coverage:** The detail page emits `__head`, `__name`, `__en`, `__price`, `__unit`, `__meta`, plus `.gj-pricehist*`, but `gj.css` only styles the four-area grid (`__big`, `__cur`, `__lbl`, `__med`). The detail page will render but visual fidelity will lag until B7 (assets) extends `gj.css` to cover the new subtree. Flagging for B7 verification.
3. **`mk-list`/`mk-grid`/`mk-chips`/`mk-empty` CSS coverage:** Likewise, the list-page layout classes are not yet in `gj.css`/`desktop.css` (only `desktop-extras.css` likely needs the grid rules). Flagging for B7.
4. **`$active='market'`** assumes the shells use `'market'` as the active-key for the market module. If shells expect a different token (e.g. `'sfa-market'`), this needs alignment.

---

## 8. Summary

- **2 templates rewritten** (`market_list.php`, `market_product.php`) — 214 lines total, both pass `php -l`.
- **2 legacy files deleted** (`templates/market/detail.php`, `templates/market/list.php`); empty `market/` dir removed by `git rm`.
- **Disclaimer macro included on BOTH market pages** as the first content node — mandatory per COMPONENTS.md §10.
- **All required BEM classes emitted** verbatim per COMPONENTS.md (`.mk-disclaimer`, `.pcard`, `.gj-pricebig*`, `.gj-pricehist*`, `.gj-crosslink--soil`, `.contrib-strip`) and template-owned wrappers (`mk-chips`, `mk-chip`, `is-active`, `mk-list`, `mk-grid`, `mk-empty`).
- **`validate_aos.sh` = 29 PASS / 17 SKIP / 0 FAIL** — invariant preserved.
- **No commit** per constraint.

Scope boundary respected: no shells, macros, controllers, JS, CSS, or DB code modified.
