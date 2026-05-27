---
id: RESEARCH_dual_template_tree_resolution_2026-05-27_v1.0.0
from: team_100 (research sub-agent — read-only)
to: team_100 (Chief System Architect — WP-UI RE-BUILD orchestrator)
date: 2026-05-27
type: RESEARCH_REPORT
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
authority: read-only investigation; no files modified
worktree: /Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/
status: COMPLETE
recommendation: A (keep `pages/`, delete legacy)
---

# Dual Template Tree Resolution — Research Report

## Scope

Determine which of the two template subtrees under `sfa_delivery/templates/` is wired to the live Slim controllers, and recommend cleanup before the WP-UI RE-BUILD overwrites the wrong files.

- Primary tree under inspection: `templates/pages/*.php` (14 files)
- Legacy tree under inspection: `templates/crop_book/{detail,list}.php`, `templates/market/{detail,list}.php`

All paths below are inside the build worktree
`/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/` unless noted otherwise.

---

## 1. Controller → Route → Template wiring map

Source of truth for routing: `app/routes.php`.
Every `Template::render('<name>', …)` call in `app/Controllers/` was grepped.

### 1.1 All `Template::render()` call sites (full inventory)

| Controller | Method | `Template::render('…')` name |
|---|---|---|
| `HomeController.php:14` | (unused — see §1.3) | `'home'` |
| `HubController.php:15` | `home` | `'pages/hub_home'` |
| `HubController.php:24` | `tiers` | `'pages/hub_tiers'` |
| `HubController.php:33` | `search` | `'pages/search_results'` |
| `HubController.php:39` | `calc` | `'pages/hub_calc'` |
| `HubController.php:47` | `community` | `'pages/community'` |
| `CropBookViewController.php:19` | `entry` | `'pages/book_entry'` |
| `CropBookViewController.php:31` | `questions` | `'pages/book_questions'` |
| `CropBookViewController.php:37` | `family` | `'pages/book_family'` |
| `CropBookViewController.php:54` | `tableView` | `'pages/book_table'` |
| `CropBookViewController.php:70` | `search` | `'pages/book_search'` |
| `CropBookViewController.php:84` | `detail` (404) | `'error'` |
| `CropBookViewController.php:106` | `detail` | `'pages/book_crop'` |
| `CropBookViewController.php:121` | `variety` (404) | `'error'` |
| `CropBookViewController.php:137` | `variety` (404) | `'error'` |
| `CropBookViewController.php:140` | `variety` | `'pages/book_variety'` |
| `MarketViewController.php:21` | `index` | `'pages/market_list'` |
| `MarketViewController.php:32` | `detail` (404) | `'error'` |
| `MarketViewController.php:37` | `detail` | `'pages/market_product'` |

**Result: zero controller references to `crop_book/` or `market/` legacy subtrees.**
A repo-wide grep `templates/crop_book\|templates/market\b` against `sfa_delivery/` returned **no matches** — the legacy paths are referenced nowhere in PHP, route definitions, tests, or bootstrap.

### 1.2 Mandate §3 — 14-route mapping (controller → template → tree)

| # | Route | Controller method | Template (resolved file) | Tree |
|---|---|---|---|---|
| 1 | `/` | `HubController::home` | `templates/pages/hub_home.php` | `pages/` |
| 2 | `/about[/]` | `HubController::tiers` | `templates/pages/hub_tiers.php` | `pages/` |
| 3 | `/search[/]` | `HubController::search` | `templates/pages/search_results.php` | `pages/` |
| 4 | `/calc[/]` | `HubController::calc` | `templates/pages/hub_calc.php` | `pages/` |
| 5 | `/crop-book[/]` | `CropBookViewController::entry` | `templates/pages/book_entry.php` | `pages/` |
| 6 | `/crop-book/questions[/]` | `CropBookViewController::questions` | `templates/pages/book_questions.php` | `pages/` |
| 7 | `/crop-book/family[/]` | `CropBookViewController::family` | `templates/pages/book_family.php` | `pages/` |
| 8 | `/crop-book/table[/]` | `CropBookViewController::tableView` | `templates/pages/book_table.php` | `pages/` |
| 9 | `/crop-book/search[/]` | `CropBookViewController::search` | `templates/pages/book_search.php` | `pages/` |
| 10 | `/crop-book/{slug}[/]` | `CropBookViewController::detail` | `templates/pages/book_crop.php` | `pages/` |
| 11 | `/crop-book/{slug}/variety/{vslug}[/]` | `CropBookViewController::variety` | `templates/pages/book_variety.php` | `pages/` |
| 12 | `/market[/]` | `MarketViewController::index` | `templates/pages/market_list.php` | `pages/` |
| 13 | `/market/{slug}[/]` | `MarketViewController::detail` | `templates/pages/market_product.php` | `pages/` |
| 14 | `/community[/]` | `HubController::community` | `templates/pages/community.php` | `pages/` |

**All 14 mandate routes resolve to `templates/pages/`. None resolves to the legacy tree.**

### 1.3 `HomeController` note

`app/Controllers/HomeController.php:14` calls `Template::render('home', [])` (→ `templates/home.php`).
`HomeController` is **not registered** in `app/routes.php` (no `[HomeController::class, …]` entry). It is an orphan controller, distinct from the dual-tree question but worth flagging as dead code.

---

## 2. `Template::render()` path-resolution logic

File: `app/Lib/Template.php` (35 lines, full read).

```php
private const ROOT = __DIR__ . '/../../templates';

public static function render(string $name, array $vars = []): string
{
    $file = self::ROOT . '/' . $name . '.php';
    if (!is_file($file)) {
        throw new \RuntimeException("template not found: {$name}");
    }
    extract($vars, EXTR_SKIP);
    ob_start();
    include $file;
    return (string)ob_get_clean();
}
```

Resolution is **purely literal string concatenation**:

`templates/{name as passed by controller}.php`

There is no namespace search, no fallback lookup, no auto-routing between subtrees. If the controller passes `'pages/book_crop'`, the renderer loads `templates/pages/book_crop.php` and nothing else. The doc-block example
`Template::render('crop_book/list', ['crops' => $rows])` is illustrative comment text only — no controller actually issues that call.

---

## 3. Legacy tree usage (per-file)

For each file in the two legacy subtrees, the result of grepping `app/` for references:

| File | Lines | Controller refs | Status |
|---|---|---|---|
| `templates/crop_book/detail.php` | 99 | **none** | DEAD |
| `templates/crop_book/list.php` | 57 | **none** | DEAD |
| `templates/market/detail.php` | 79 | **none** | DEAD |
| `templates/market/list.php` | 72 | **none** | DEAD |

The string `crop_book/` appears in `app/` exactly once, in the Template.php docblock example (line 11). The string `market/` appears in `app/routes.php` only as URL prefixes (`/market/{slug}`, `/market/{slug}/history`), never as a template path. **No controller, no test, no bootstrap, no middleware references any of the four legacy files.**

Substantive content gap (informational — for the merge decision):

- `crop_book/detail.php` is richer than `pages/book_crop.php`: breadcrumb, scientific-name styling, kv-list of `family_name_he` / `category` / `season` / `dtm_min/max` / `harvest_unit_default` / `variety_count`, description prose block, full variety cards (`planting_method`, `planting_season`, `in_row_spacing_cm`, `documented_price` + unit + source, notes), `last_pushed_at` footer. `pages/book_crop.php` renders only `<h1>hebrew_name</h1><p>scientific_name</p><h2>זנים</h2><ul>` of variety links.
- `crop_book/list.php` carries a category-facet chip nav + card-grid (`card`, `card-link`, `card-title`, `card-subtitle`, `card-meta`); `pages/book_entry.php` is the 4-entry-card hub for `/crop-book/`, a structurally different page (mandate §3 row 5 = CB0 module-card hub, not a crop list).
- `market/detail.php` includes price-history table, organic/basket tags, seasonality prose, `last_pushed_at`. `pages/market_product.php` has price + 28-day history table, includes `macros/market_disclaimer.php`, but lacks the organic/basket tag handling and seasonality block.
- `market/list.php` has category-facet nav + table with freshness color-coded badges. `pages/market_list.php` is shorter (25 lines).

The legacy templates **predate** the WP-UI v1 sequence: they use semantic class names (`crop-detail`, `kv-list`, `card-grid`, `facets`) that do NOT match the team_35 BEM contract from `COMPONENTS.md` (`crop-detail__head`, `crop-detail__h1`, `crop-vars__list`, `gj-shell`, `module-card`, etc.). They are not the design-fidelity target. Any RE-BUILD must produce DOM per mandate §3 (BEM under `gj-shell` / `dt-shell`), which neither tree currently satisfies — the legacy tree is closer in *information density*, the `pages/` tree is closer in being the active wiring.

---

## 4. Live HTML evidence

`curl -sS https://sfa.nimrod.bio/crop-book/anise-hyssop/`

Returned body (within `<main class="gj-main">`):

```html
<section>
  <h1>אזוב מצוי</h1>
  <p>Lamiaceae</p>
  <h2>זנים</h2>
  <ul>
    <li>
      <a href="/crop-book/anise-hyssop/variety/variety-1">אזוב מצוי</a>
    </li>
  </ul>
</section>
```

Distinctive markers:

- **Matches `templates/pages/book_crop.php` byte-for-byte** (h1 hebrew_name → p scientific_name → h2 "זנים" → ul of variety links). No breadcrumb, no kv-list, no description block, no `crop-detail__` wrapper, no `last_pushed_at` footer.
- **Absent** from the live HTML: every distinctive class from `templates/crop_book/detail.php` — no `breadcrumb`, no `crop-detail`, no `kv-list`, no `variety-list`, no `variety-meta`, no `meta-footer`. If `crop_book/detail.php` were rendering we would see all of these.
- The outer shell (`gj-shell` mobile + `dt-shell` desktop) is supplied by `templates/_layout.php` + `templates/shell/mobile.php` + `templates/shell/desktop.php` — unrelated to the dual-tree question.

**Conclusion: the live site is rendering `templates/pages/book_crop.php` exclusively.** The legacy `crop_book/detail.php` template is not being served and has not been served at any point reachable by current routes.

---

## 5. Recommendation: **A — keep `pages/`, delete legacy**

### Rationale

The dual-tree appears worrying at first glance but resolves cleanly:

1. **Wiring is unambiguous.** Every one of the 14 mandate routes points at `templates/pages/`. The legacy tree has zero inbound references from `app/`, `routes.php`, tests, bootstrap, middleware, or any other template. `Template::render()` is a literal-path renderer with no fallback lookup, so a "silent" hit on legacy is structurally impossible — only a code change would activate it.
2. **Live evidence corroborates.** Production HTML at `/crop-book/anise-hyssop/` is byte-identical to `pages/book_crop.php` and lacks every distinctive marker of `crop_book/detail.php`.
3. **The legacy tree's richer content is not a reason to keep it.** None of the legacy classes (`crop-detail`, `kv-list`, `card-grid`, `variety-list`, `meta-footer`, `facets`) appear in `COMPONENTS.md`'s BEM contract. The RE-BUILD must replace the bare `pages/` markup with the team_35 BEM contract (`crop-detail__head`, `crop-detail__h1`, `crop-vars__list`, `crop-vars__row`, etc., under `gj-shell`/`dt-shell`). Neither tree's current DOM satisfies §3 of the mandate; both must be rewritten. Merging legacy first (option C) would mean rewriting the same files twice and risks reintroducing non-BEM class names.
4. **Field-set ideas from legacy are still salvageable without keeping the files.** When you rewrite `pages/book_crop.php` and `pages/market_product.php` per the BEM contract, the *list of fields* the legacy templates handled (family_name_he, season, dtm, harvest_unit_default, planting_method, planting_season, in_row_spacing_cm, documented_price{,_unit,_source}, organic/basket flags, seasonality_notes, last_pushed_at) is a useful checklist for defensive rendering per Deliverable 2 (§1, DB-aware). Use them as a starting label-dictionary, not as templates to merge.
5. **Deletion reduces ambiguity for team_190 validators.** A clean templates tree with only the active subtree avoids any "which file did you actually edit?" question during L-GATE_V cross-engine review.

### Why not B, C, D

- **B (keep legacy, deprecate `pages/`):** would require re-wiring every controller to `'crop_book/detail'`/`'market/detail'` etc., creating 14 risk points and breaking parity with the v1 build branch the mandate is rebasing off.
- **C (merge then delete legacy):** the merge target is the BEM rewrite from team_35's `COMPONENTS.md`, not the legacy DOM. Merging legacy into `pages/` would import non-BEM markup that you must then strip again to satisfy §3.
- **D:** no scenario observed warrants a fourth path.

---

## 6. Cleanup commands

Execute from the worktree root (`/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`) on branch `claude/sfa-ui-build-v2`:

```bash
# Remove the four dead legacy templates
git rm sfa_delivery/templates/crop_book/detail.php \
       sfa_delivery/templates/crop_book/list.php \
       sfa_delivery/templates/market/detail.php \
       sfa_delivery/templates/market/list.php

# Remove the now-empty subdirs (git rm does not delete empty dirs; do this if rmdir succeeds)
rmdir sfa_delivery/templates/crop_book 2>/dev/null || true
rmdir sfa_delivery/templates/market 2>/dev/null || true

# Update the docblock example in Template.php so it no longer references the deleted path.
# Hand-edit app/Lib/Template.php line 11 from:
#   *   $html = Template::render('crop_book/list', ['crops' => $rows]);
# to:
#   *   $html = Template::render('pages/book_entry');
# (or any other live example)

# Commit
git commit -m "chore(WP-UI): remove dead legacy template trees (crop_book/, market/)

These four templates are unreferenced by any controller. Live site
renders templates/pages/* exclusively per routes.php + Template::render
literal-path resolution. Deletion eliminates dual-tree ambiguity ahead
of the WP-UI RE-BUILD overwriting the active pages/ files with the
team_35 BEM contract."
```

Optional follow-on (out of scope for the dual-tree question — flag for separate cleanup):

```bash
# HomeController is not registered in routes.php and points at a non-existent template alias.
# Verify it is truly unused (grep -rn 'HomeController' sfa_delivery/) before deleting.
# git rm sfa_delivery/app/Controllers/HomeController.php
# Also: templates/home.php — confirm it is the unused target of HomeController, then delete.
```

---

## Evidence index (absolute paths)

- Routes: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/app/routes.php`
- Renderer: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/app/Lib/Template.php`
- Controllers: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/app/Controllers/{CropBookViewController,MarketViewController,HubController,HomeController}.php`
- Active templates (14 + layout/shell): `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/templates/pages/`
- Dead legacy templates: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/sfa_delivery/templates/{crop_book,market}/`
- Live site sample: `https://sfa.nimrod.bio/crop-book/anise-hyssop/` (curl captured 2026-05-27)
- Mandate: `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/gallant-elbakyan-727a60/_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` §3
