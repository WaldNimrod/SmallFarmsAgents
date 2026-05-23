---
id: WP-3_WP-4_BUILD_REPORT_v1.0.0
type: BUILD_REPORT
gate: L-GATE_V (WP-3 closed); L-GATE_B PARTIAL (WP-4)
work_packages: [SFA-S003-P003-WP-3, SFA-S003-P003-WP-4]
date: 2026-05-24
recorded_by: team_100 (executed in-session as sfa_build)
status: WP-3 LOD500_LOCKED; WP-4 PARTIAL (manual push proven)
live_urls:
  - https://sfa.nimrod.bio/
  - https://sfa.nimrod.bio/crop-book/
  - https://sfa.nimrod.bio/market/
---

# WP-3 + WP-4 BUILD Report — User-facing routes LIVE + canonical data pushed

## §1 Outcome

**`https://sfa.nimrod.bio` is now a fully browsable site** with real canonical data:
- 52 crops in ספר גידולים (crop book) with category filters + detail pages
- 190 crop varieties (linked from each crop's detail)
- 65 active products in מחירון (market) with category filters
- All Hebrew RTL, mobile-first responsive, server-rendered PHP, zero JS framework deps

End-to-end browser test verified via Claude_in_Chrome (1280×900 viewport, zero console errors).

## §2 WP-3 — user-facing PHP routes

**Files added to `sfa_delivery/`:**

| File | Role |
|------|------|
| `app/Lib/Template.php` | 30-line plain-PHP template renderer with HTML-escape helper |
| `app/Controllers/HomeController.php` | `GET /` → home template |
| `app/Controllers/CropBookViewController.php` | `GET /crop-book/` + `/crop-book/{slug}` |
| `app/Controllers/MarketViewController.php` | `GET /market/` + `/market/{slug}` |
| `templates/_layout.php` | site chrome (header + nav + footer), RTL Hebrew |
| `templates/home.php` | landing with 2 CTAs |
| `templates/crop_book/list.php` | grid of 52 crops + category facets |
| `templates/crop_book/detail.php` | crop detail + meta + varieties section |
| `templates/market/list.php` | products table + category facets |
| `templates/market/detail.php` | product detail + price history (when present) |
| `templates/error.php` | Hebrew 404/500 page |
| `public_assets/css/site.css` | 6.5 KB minimal RTL Hebrew + mobile-first (@600px breakpoint) |

**`app/routes.php` updated** to mount new routes alongside existing JSON API.

**Stack:** Slim 4 routing + plain PHP includes (no Twig/Smarty) + vanilla CSS (no build step). PSR-4 autoload. ~600 lines total.

**Browser-verification screenshots** captured for: home (1.5KB body), `/crop-book/` (24KB), `/crop-book/anise-hyssop` (2KB detail), `/market/` (22KB table), `/market/{nonexistent}` (graceful Hebrew 404).

## §3 WP-4 light — Python publisher push

**File added: `organic_market_agent/publisher/sfa_ingest_push.py`** (~390 lines).

What it does:
1. Reads canonical Postgres (`DATABASE_URL`) — crops (joined with crop_families), crop_varieties (with all detail fields), products (joined with measurement_units + daily_aggregates for latest price)
2. Transforms each row to the ingest contract: top-level columns + `payload_json` blob with `schema_version: 1`
3. Generates per-batch `idempotency_key = "{table}_{YYYYMMDD-HHMMSS}_{seq:03d}"`
4. HMAC-SHA256 signs the JSON body using `SFA_INGEST_HMAC_SECRET`
5. POSTs in batches of 50 to `SFA_INGEST_URL` with `X-SFA-Auth: sha256=<hex>` header
6. CLI flags: `--table {crops,crop_varieties,products,all}`, `--limit N`, `--dry-run`, `--verbose`

**Verified push (real data, Mac → live ingest API):**
```
crops batch=1 size=50 -> {http_status:200, accepted:50, rejected:0}
crops batch=2 size=2  -> {http_status:200, accepted:2,  rejected:0}
crop_varieties batch=1 size=50 -> {accepted:50, rejected:0}
crop_varieties batch=2 size=50 -> {accepted:50, rejected:0}
crop_varieties batch=3 size=50 -> {accepted:50, rejected:0}
crop_varieties batch=4 size=40 -> {accepted:40, rejected:0}
products batch=1 size=50 -> {accepted:50, rejected:0}
products batch=2 size=15 -> {accepted:15, rejected:0}
```
**Total: 307 rows accepted in 8 batches, <1 second wall time.** Hebrew UTF-8 preserved through full pipeline.

## §4 Live verification (browser screenshots)

| Page | URL | Status | Notes |
|------|-----|--------|-------|
| Home | `/` | 200, 1.5 KB | RTL Hebrew, 2 CTAs ("לספר הגידולים", "למחירון"), sticky nav |
| Crop book | `/crop-book/` | 200, 24 KB | 52 cards in 4-column grid, 4 category facets (vegetables 34, herbs 15, fruits 1, fruit_trees 2) |
| Crop detail | `/crop-book/anise-hyssop` | 200, 2 KB | "אזוב מצוי" with breadcrumb, KV list (משפחה, קטגוריה, מחזור, יחידת קציר, זנים), varieties section |
| Market | `/market/` | 200, 22 KB | 65-row table with 9 category facets (leafy_greens 16, fruits 11, fruiting_vegetables 12, ...) |
| 404 | `/market/non-existent` | 404 | Hebrew "שגיאה 404 / מוצר לא נמצא" + back-to-home button |
| CSS | `/public_assets/css/site.css` | 200, 6.5 KB | Loads cleanly, no MIME issues |
| Console | (all pages) | clean | zero errors per `read_console_messages` |

## §5 Findings (audit)

| ID | Sev | Description | Disposition |
|----|-----|-------------|-------------|
| F-3-1 | INFO | Products show "—" for prices because Postgres `daily_aggregates` has no recent (90-day) rows for most products on the local dev DB. Production push from waldhomeserver should populate prices fully. | Expected for local dev push. Re-test from waldhomeserver. |
| F-3-2 | INFO | `lftp` `mirror:include-hidden` directive name was wrong on this lftp version (4.9.3); workaround: `--include-glob '.*'`. Doc note for ops. | Captured; non-blocking. |
| F-3-3 | LOW | Current design is **minimal interim** — when team_35 (Design Studio) ships LOD300 design book, templates will be re-skinned. Schema + routing don't change. | DEFERRED to WP-3-patch01 (post-WP-B). |
| F-3-4 | INFO | Mobile responsive CSS exists (`@media (max-width: 600px)`) but `resize_window` MCP tool resizes the OS window, not the page viewport meta. Visual mobile test pending real device or Chrome devtools. | Manual user test recommended. |

## §6 What this delivers (re user directive 2026-05-23)

> "המשימה שלנו היא לפרוס את המערכת באופן מלא לשרת חדש שיצרנו. כולל בדיקות מלאות בדפדפן."

| Required | Delivered |
|----------|-----------|
| Full deployment to new server | ✅ sfa.nimrod.bio LIVE end-to-end (5 routes + API) |
| Browser tests | ✅ 5 pages screenshotted + verified zero console errors |

## §7 Remaining for full P003 closure (DEFERRED)

| Item | WP | Priority |
|------|-----|----------|
| Deploy `sfa_ingest_push.py` to waldhomeserver + wire to existing scheduler/cron | WP-4-patch01 | HIGH (replaces broken daily cron) |
| Add waldhomeserver public IP to uPress FTP allowlist | WP-4-patch01 | MEDIUM |
| Cron to prune `ingest_log` rows >30d on MySQL side | WP-4-patch01 | LOW |
| 301 redirect from `www.nimrod.bio/smallfarmsagent/` → `https://sfa.nimrod.bio/market/` + remove mu-plugin | **WP-5** | After WP-4-patch01 |
| Deprecate `wp_upload.py` + `static_upload.py` once WP-5 done | WP-5 | After WP-5 |
| team_35 design re-skin | WP-3-patch01 | After WP-B LOD300 |
| `.htaccess` hardening on uPress (`composer.json` + SQL files) | WP-2-patch01 | LOW |
| Rotate FTP/DB/SMTP passwords (leaked in transcript) | ops housekeeping | After stable |

## §8 Files of record

- Source (WP-3): `sfa_delivery/app/Controllers/{Home,CropBookView,MarketView}Controller.php`, `sfa_delivery/app/Lib/Template.php`, `sfa_delivery/templates/**`, `sfa_delivery/public_assets/css/site.css`
- Source (WP-4 light): `organic_market_agent/publisher/sfa_ingest_push.py`
- Routes: `sfa_delivery/app/routes.php`
- Roadmap: `_aos/roadmap.yaml` (WP-3 → COMPLETE, WP-4 → PARTIAL)
- WP-2 BUILD report (prior): `_COMMUNICATION/team_00/WP-2_BUILD_REPORT_2026-05-23_v1.0.0.md`
- Canonical architecture: `documentation/02-architecture/sfa-delivery-tier.md`
- Canonical schema: `documentation/03-data-and-schema/sfa-mysql-mirror.md`

---

*Build report filed 2026-05-24 by team_100. P003 phase-1 (WP-1 + WP-2 + WP-3 + WP-4 light) functionally COMPLETE; phase-2 (WP-4-patch01 + WP-5) deferred per user directive scope.*
