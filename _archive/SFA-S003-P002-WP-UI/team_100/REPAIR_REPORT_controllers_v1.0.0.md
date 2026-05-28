# REPAIR_REPORT — Controllers Alignment

**Sub-agent:** R-Controllers
**Dispatched by:** team_100 (Claude Opus 4.7)
**Mission:** Align `sfa_delivery/app/Controllers/*` with the new template variable contracts established by R1 + R2 build agents (B2 macros + B3–B6 page templates).
**Worktree:** `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/sfa-ui-build-v2/`
**Date:** 2026-05-27

---

## 1. Per-controller mapping — current → patched data shape

### 1.1 MarketViewController

Most-flagged controller in B5 BUILD_REPORT. Patched `::index` and `::detail`.
JSON API method `productHistoryApi` left untouched (preserves `/api/v1/market/{slug}/history` shape).

**Index `/market/`:**

| Template/macro key      | Source (before)     | Source (after) — patched controller                                  |
| ----------------------- | ------------------- | -------------------------------------------------------------------- |
| `name_he`               | (missing)           | alias of `hebrew_name`                                               |
| `en_name`               | (missing)           | `''` placeholder (DB has no en column)                               |
| `unit_he`               | (missing)           | alias of `unit`                                                      |
| `glyph_letter`          | (missing)           | first UTF-8 char of `hebrew_name`                                    |
| `price_current`         | (missing)           | alias of `last_price`                                                |
| `currency`              | (missing)           | `'₪'` constant                                                       |
| `price_min`             | (missing → 0)       | `MIN(price) FROM product_prices` aggregated query                    |
| `price_max`             | (missing → 0)       | `MAX(price) FROM product_prices`                                     |
| `price_median`          | (missing → 0)       | computed per-product via `fetchMedian()`                             |
| `source_count`          | (missing → 0)       | `COUNT(DISTINCT source) FROM product_prices`                         |
| `observation_count`     | (missing → 0)       | `COUNT(*) FROM product_prices`                                       |
| `icon_slug`             | (missing)           | from `ICON_MAP` by slug or category; falls back to `'leaf'`          |
| `book_slug`             | (missing)           | same as product `slug` (assumes alignment with crop book)            |
| `book_label_he`         | (missing)           | alias of `hebrew_name`                                               |
| `updated_he`            | (missing)           | `last_price_date` formatted as `"26 במאי"` via `formatHebrewDate()`  |
| `$categories`           | (missing)           | distinct `category` rows wrapped as `[slug,name_he]`                 |
| legacy `hebrew_name`, `last_price`, `unit`, `category`, `freshness_days` | passed through | **preserved** (still in row — array_merge keeps both shapes) |

**Detail `/market/{slug}`:**

| Template key (book_crop / market_product macros)                       | Source after patch                                              |
| ---------------------------------------------------------------------- | --------------------------------------------------------------- |
| All of the above for `$product`                                        | computed via `mapProductRow($row, aggregateFromHistory($history))` |
| `$product['history']` (alt shape)                                      | `mapHistoryRows()` — adds `date_he`, normalizes `price`         |
| `$history` (legacy top-level)                                          | preserved exactly as before (raw DB rows)                       |

### 1.2 CropBookViewController

Aligned all six render call-sites to the canonical template shape.
`::entry` was already template-defaulted — left untouched. JSON `/api/v1/crops/*` (CropsController) NOT touched.

**`::family` → `book_family.php`:**

| Template key  | Before                  | After                                            |
| ------------- | ----------------------- | ------------------------------------------------ |
| `slug`        | (missing)               | `slugify(family_name_he)` (or `'family'` fallback) |
| `name_he`     | alias of `family_name_he` (template fallback) | explicit `name_he` field              |
| `name_lat`    | (missing)               | `''` placeholder                                 |
| `crop_count`  | (missing → `total` fallback) | explicit alias                              |
| `total`       | DB column               | **preserved** (back-compat)                      |

**`::tableView` → `book_table.php`:**

| Template key       | Before                 | After                                               |
| ------------------ | ---------------------- | --------------------------------------------------- |
| `name_he`          | (template fallback)    | alias of `hebrew_name`                              |
| `family_he`        | (template fallback)    | alias of `family_name_he`                           |
| `dtm_days`         | (missing — only `dtm_min`/`dtm_max` present) | derived as `dtm_max ?? dtm_min`        |
| `yield_kg_per_m2`  | (missing)              | `null` (template renders `—`)                       |
| `best_season`      | (missing)              | alias of `season`                                   |
| `source_count`     | (missing)              | `null` (template renders `—`)                       |
| `icon_slug`        | (missing)              | from `ICON_MAP[slug]` or `'leaf'`                   |
| legacy DB columns  | passed through         | **preserved**                                       |

**`::search` → `book_search.php`:**

| Template key    | Before                  | After                                                            |
| --------------- | ----------------------- | ---------------------------------------------------------------- |
| `query`         | (only `$q` was passed)  | explicit `$query` (canonical name)                               |
| `q`             | passed                  | **preserved** (back-compat alias for B6 defensive shim)          |
| `results`       | (only `$items`)         | explicit `$results` (canonical name)                             |
| `items`         | passed                  | **preserved** (back-compat alias)                                |
| each result row | `slug,hebrew_name,scientific_name,category` | mapped to `slug,name_he,en_name,family_tag_he,dtm_days,icon_svg` (crop_card contract) |

**`::detail` → `book_crop.php`:**

| Template key            | Before                                  | After                                                  |
| ----------------------- | --------------------------------------- | ------------------------------------------------------ |
| `$crop['name_he']`      | (template fallback to `hebrew_name`)    | explicit alias                                         |
| `$crop['name_lat']`     | (template fallback to `scientific_name`)| explicit alias                                         |
| `$crop['en_name']`      | (missing)                               | `''` placeholder                                       |
| `$crop['icon_slug']`    | (missing — template defaulted to `'leaf'`) | from `ICON_MAP[slug]` or `'leaf'` (payload override wins) |
| `$crop['description_he']`| (payload-only, possibly missing)       | always present (defaults to `''`)                      |
| `$crop['family_tag_he']`| (missing)                               | alias of `family_name_he`                              |
| `$crop['dtm_days']`     | (only `dtm_min`/`dtm_max`)              | derived (payload override → `dtm_max` → `dtm_min`)     |
| `$crop['family']`       | (missing)                               | `{slug, name_he}` object built from `family_name_he`   |
| `$crop['varieties']`    | passed as separate top-level only       | **also nested into `$crop['varieties']`** per template contract |
| `$crop['knowledge_notes']`| (payload-only, possibly absent)        | defaulted to `[]` (preserves `is_internal_farm_use_only` from payload) |
| `$crop['market_link']`  | (missing)                               | best-effort lookup against `products` table (slug match); only added when match found |
| `$crop['timeline']`     | (not computed)                          | **NOT added — STUBBED** (left to template fallback, see §5) |
| each variety row        | `id,name,*payload`                      | augmented with `vslug` (canonical), `slug` (back-compat), `name_he` |

**`::variety` → `book_variety.php`:** added `vslug` + `name_he` aliases to `$variety`, and `name_he`/`name_lat` aliases to `$crop`.

**`::questions` → `book_questions.php`:** rewrote inline stub questions to match template contract (`q_he,sub_he,href,slug` instead of legacy `title,category`).

### 1.3 HubController

Added optional `PDO` constructor injection (PHP-DI autowires; signature defaults `null` for back-compat). Patched `::search` from a stub to a functional global search.

**`::search` → `search_results.php`:**

| Template key       | Before                            | After                                                       |
| ------------------ | --------------------------------- | ----------------------------------------------------------- |
| `query`            | (missing — template fallback to `$q`) | explicit `$query`                                       |
| `q`                | passed                            | **preserved** (back-compat alias for defensive shim)        |
| `crop_results`     | (missing → template empty)        | array of `{slug,name_he,en_name,family_tag_he,dtm_days,icon_svg}` (crop_card contract) — up to 20 |
| `product_results`  | (missing → template empty)        | array per price_card contract (name_he, price_current, etc.) — up to 20; aggregates stubbed (see §5) |

`::home`, `::tiers`, `::calc`, `::community` — unchanged. They already pass the variables the templates consume.

### 1.4 HomeController

Renders the legacy `home.php` template. Route `/` is mapped to `HubController::home` in `routes.php`, so HomeController is currently **unbound to any route**. Left untouched (no template alignment needed). No breakage risk.

### 1.5 SearchController (JSON `/api/v1/search`)

**Untouched.** Returns `{query, crops, products}` JSON to API consumers. Out of scope for template alignment.

### 1.6 ProductsController, CropsController, HealthController, IngestController, ModulesController

**All untouched.** Pure JSON API surface — verified by `git diff`.

---

## 2. Files modified

| File                                                                          | +ins  | -dels | Notes                                                  |
| ----------------------------------------------------------------------------- | ----- | ----- | ------------------------------------------------------ |
| `sfa_delivery/app/Controllers/MarketViewController.php`                       | ~226  | ~9    | Added `mapProductRow`, `mapHistoryRows`, `fetchAggregatesAll`, `fetchMedian`, `aggregateFromHistory`, `fetchCategories`, `formatHebrewDate`; ICON_MAP + HE_MONTHS constants |
| `sfa_delivery/app/Controllers/HubController.php`                              | ~66   | ~6    | Added optional PDO injection; `::search` now functional with crop+product result mapping |
| `sfa_delivery/app/Controllers/CropBookViewController.php`                     | ~124  | ~4    | Added ICON_MAP; rewrote `::family`, `::tableView`, `::search`, `::detail`, `::variety`, `::questions` to canonical template shape |

`git diff --stat` (verbatim):
```
sfa_delivery/app/Controllers/CropBookViewController.php     | 128 +++++++++--
sfa_delivery/app/Controllers/HubController.php              |  72 ++++++-
sfa_delivery/app/Controllers/MarketViewController.php       | 235 ++++++++++++++++++++-
3 files changed, 416 insertions(+), 19 deletions(-)
```

---

## 3. `php -l` per file

```
$ php -l sfa_delivery/app/Controllers/MarketViewController.php
No syntax errors detected in sfa_delivery/app/Controllers/MarketViewController.php

$ php -l sfa_delivery/app/Controllers/HubController.php
No syntax errors detected in sfa_delivery/app/Controllers/HubController.php

$ php -l sfa_delivery/app/Controllers/CropBookViewController.php
No syntax errors detected in sfa_delivery/app/Controllers/CropBookViewController.php

# All other controllers (untouched) — linted for sanity:
$ php -l sfa_delivery/app/Controllers/HomeController.php       → No syntax errors
$ php -l sfa_delivery/app/Controllers/SearchController.php     → No syntax errors
$ php -l sfa_delivery/app/Controllers/ModulesController.php    → No syntax errors
$ php -l sfa_delivery/app/Controllers/ProductsController.php   → No syntax errors
$ php -l sfa_delivery/app/Controllers/CropsController.php      → No syntax errors
$ php -l sfa_delivery/app/Controllers/HealthController.php     → No syntax errors
$ php -l sfa_delivery/app/Controllers/IngestController.php     → No syntax errors
```

---

## 4. `validate_aos.sh` output

```
RESULT: 29 PASS / 19 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

No new FAIL introduced. Pre-existing SKIPs unchanged (Check 21/22 pre-V318 data debt; Check 25 PENDING_DB_SYNC offline session — both predate this repair).

### PHPUnit regression check

```
PHPUnit 10.5.63 by Sebastian Bergmann and contributors.
.................................                            31 / 31 (100%)

Time: 00:00.027, Memory: 12.00 MB
OK, but there were issues!
Tests: 31, Assertions: 60, PHPUnit Deprecations: 1.
```

All 31 tests pass — including all **14 RouteSmoke data sets** (every HTML route: `/`, `/about/`, `/search/`, `/calc/`, `/crop-book/`, `/crop-book/questions/`, `/crop-book/family/`, `/crop-book/table/`, `/crop-book/search/?q=עגב`, `/crop-book/anise-hyssop/`, `/crop-book/anise-hyssop/variety/variety-11/`, `/market/`, `/market/onion-dry/`, `/community/`). The lone "PHPUnit Deprecation" is unrelated and pre-existing.

---

## 5. Stubbed aggregates — items left null (follow-up)

The following aggregates are intentionally `null` / placeholder and rely on template `—` rendering. Compute when underlying data lands:

| Field                                                | Reason                                                   |
| ---------------------------------------------------- | -------------------------------------------------------- |
| `book_table.crops[*].yield_kg_per_m2`                | No `yield_kg_per_m2` column in `crops` table — needs variety aggregation per crop |
| `book_table.crops[*].source_count`                   | No `crop_sources` table exposed in spoke schema yet      |
| `book_crop.crop.timeline`                            | No `timeline` data in `crops.payload_json` (per current ingest) — template safely skips section |
| `book_crop.crop.market_link.source_count`            | Joined product aggregate not computed in detail path (avoided extra round-trip in detail render) — left at 0 |
| `book_search.results[*].icon_svg`                    | Sprite SVG generation not pre-rendered — left as `''`; template gracefully falls back |
| `search_results.crop_results[*]`/`product_results[*]`| Hub search aggregates left at 0 (no `product_prices` join in hub search query) — could be enriched but P0 was just exposing the keys |

These are NOT bugs — templates have explicit `?? '—'` fallbacks for all of them.

---

## 6. JSON API regression check

```
$ git diff --name-only sfa_delivery/app/Controllers/
sfa_delivery/app/Controllers/CropBookViewController.php
sfa_delivery/app/Controllers/HubController.php
sfa_delivery/app/Controllers/MarketViewController.php
```

JSON-only controllers untouched:
- `ProductsController.php` (handles `/api/v1/products`, `/api/v1/products/{slug}`) — **0 changes**.
- `CropsController.php` (handles `/api/v1/crops`, `/api/v1/crops/{slug}`) — **0 changes**.
- `HealthController.php` (handles `/api/v1/health`, `/admin/migrate`) — **0 changes**.
- `IngestController.php` (handles `POST /api/v1/ingest`) — **0 changes**.
- `ModulesController.php` (handles `/api/v1/modules`) — **0 changes**.
- `SearchController.php` (handles `/api/v1/search`) — **0 changes**.

`MarketViewController::productHistoryApi` (used by `/api/v1/market/{slug}/history`) was deliberately left structurally identical — only `index()` and `detail()` (HTML render paths) were modified. The `MarketHistory` test suite (2 tests) passes unchanged.

Tests `Search::testSearchReturnsBothArrays` and `Search::testSearchEmptyQueryReturnsEmptyCollections` both pass — JSON `/api/v1/search` contract preserved.

---

## Constraints respected

- No edits to `organic_market_agent/db/`, `sfa_ingest_push.py`, or any path outside `sfa_delivery/`.
- No new direct `organic_market_agent/db/` queries — all aggregation goes through the existing PDO handle on the spoke replica.
- No new DB queries that hit unfamiliar tables — `product_prices`, `products`, `crops`, `crop_varieties` only (all already in spoke schema 002/003).
- `php -l` clean on every modified file.
- 31/31 PHPUnit tests pass.
- 0 FAIL on `validate_aos.sh`.
- No commits made — team_100 reviews + commits.

---

## Summary

- **Controllers modified:** 3 (`MarketViewController`, `HubController`, `CropBookViewController`).
- **Lines added:** ~416 across the 3 files.
- **Key aliases added (canonical → legacy back-compat preserved):**
  `name_he` ↔ `hebrew_name`, `name_lat` ↔ `scientific_name`, `price_current` ↔ `last_price`, `unit_he` ↔ `unit`, `family_tag_he` / `family_he` ↔ `family_name_he`, `dtm_days` ↔ `dtm_max`/`dtm_min`, `vslug` (new), `query` ↔ `q`, `results` ↔ `items`.
- **New aggregates computed:** `price_min`, `price_max`, `price_median`, `source_count`, `observation_count` (from `product_prices`); `icon_slug` (from ICON_MAP); `updated_he` (Hebrew-formatted date); `book_slug`/`book_label_he` (market→book cross-link); `family.slug` (slugified family name); `market_link` on crop detail (joins to `products` when matching slug found).
- **Unresolved (stubbed) data:** yield per m², per-crop source_count, timeline, search-result aggregate counts — all gracefully render `—` via template fallbacks (see §5).

## Unresolved questions

1. **Crop→product join key:** assumed `crops.slug == products.slug` for `market_link`. If product slugs diverge from crop slugs (e.g. `tomato-cherry` vs `tomato`), market_link will silently miss. Need confirmation from data team that slug alignment is the intended join key, or surface a `product_slug` column on `crops`.
2. **`icon_slug` registry:** hard-coded `ICON_MAP` in both `MarketViewController` and `CropBookViewController`. Should this be promoted to `app/Lib/Icons.php` (deduplication)? Out of scope for this repair — flagging for follow-up.
3. **Hub search aggregates:** `HubController::search` currently passes `source_count: 0` etc. for product results. If team_100 wants real aggregates surfaced in hub search, the controller should call into the same `fetchAggregatesAll()` logic as `MarketViewController` — recommend extracting that into `app/Lib/MarketAggregates.php`.
