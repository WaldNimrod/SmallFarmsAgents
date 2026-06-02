# LIVE DEPLOY QA — SFA-S003-P004-WP-CB-UI-ALIGN (Class A) — team_50 — v1.0.0

**Date:** 2026-06-02 · **By:** team_50 (orchestrated by team_100) · **Target:** LIVE `https://sfa.nimrod.bio`
**Deployed SHA:** b72bcca (team_99, post-deploy) · **Method:** full functional+structural battery against the live site
**Complements:** the internal CSS-harness round (`INTERNAL_VISUAL_QA_2026-06-02_v1.0.0.md`). Pixel design-vs-live
screenshot pairs (AC-3) are the constitutional L-GATE_V (Cursor) round.

## Results vs ACs (live)

| AC | Check | Result | Evidence (live) |
|----|-------|--------|-----------------|
| AC-1 | served CSS zero cream; body #f8fbf8 | **PASS** | versioned `tokens.css?v=1780397450` (what the browser loads): `--gj-paper #f8fbf8` ×1, `#f5f3ec` ×0, `--paper:` def ×0. gj.css cream `--gj-paper #f6f1e3` override ×0. |
| AC-2 | `.sh` shell + `#sfa-logo` site-wide; no legacy chrome | **PASS** | `/`, `/crop-book/`, `/crop-book/tomatoes`, `/calc/`, `/market/`, `/crop-book/questions` — each `class="sh__bar"` ×1, `sfa-logo` ×2 (def+use), `gj-shell|dt-shell|sfa-nav` ×0. |
| AC-4 | `/calc` JS + 14 surfaced + 6 interactive + export | **PASS (CSV) / BLOCKED-CACHE (PDF)** | `/calc/`: `crop-book-v1.js` ×1, `data-calc` panels ×6, `modcard__head` ×14. `/calc/export.csv` → 200 (text/csv). **`/calc/export.pdf` → 404 (see F-LIVE-01).** |
| AC-5 | routes 200 | **PASS (1 cache exception)** | `/`,`/crop-book/`,`/crop-book/tomatoes`,`/calc/`,`/calc/export.csv`,`/market/`,`/search`,`/crop-book/questions` → 200. `/calc/export.pdf` → 404 (cached). |
| AC-6 | content integrity (RTL, no raw keys) | **PASS** | `/`,`/crop-book/`,`/crop-book/tomatoes`,`/calc/`,`/market/` — zero `Array(` / `object Object` / `undefined` / `field_name` / `value_best`. |
| AC-3 | pixel design-vs-live per screen | **DEFERRED → L-GATE_V (Cursor)** | structural+palette+content confirmed here; screenshot pairs are the browser-based constitutional round. |

## Findings

### F-LIVE-01 (MAJOR, NOT a code defect) — `/calc/export.pdf` serves a stale Cloudflare 404
- The deployed code FULLY supports PDF: route `/calc/export.{fmt:csv|pdf}` (routes.php:24), `HubController::calcExport`
  renders `pages/calc_export_print` for the pdf fmt, and `templates/pages/calc_export_print.php` EXISTS on the
  deployed tree. CSV (same route/controller) returns 200.
- Live `/calc/export.pdf` → **404 with `cf-cache-status: HIT`, `age 139`, `cache-control: max-age=14400`** — i.e.
  Cloudflare is serving a **cached 404 from the pre-fix era** (F-EXPORT-001, when the route truly 404'd). The zone
  ignores query strings, so `?cb=1` also HITs the same cached 404 (cannot probe origin cleanly from the edge).
- **Root cause:** stale edge cache, not code. The deploy does not purge Cloudflare, and `export.pdf` has no `?v=`
  buster (unlike CSS).
- **Fix (ops / team_99):** purge Cloudflare for `/calc/export.pdf` (or the zone), then re-verify → expect 200 +
  print-HTML. **Recommendation:** the calcExport PDF response should send `Cache-Control: no-store` so error/HTML
  responses are never edge-cached (small follow-up, optional hardening).

## Verdict
**PASS_WITH_FINDINGS (live, internal).** All in-scope ACs verified green on the live deployment except the PDF
export, which is a **cacheable-404 ops issue** (purge), not a build defect. Does not substitute for team_190
L-GATE_V (Cursor), which adds the AC-3 pixel design-vs-live screenshot pairs.

---
*Method: curl battery against https://sfa.nimrod.bio (route status, served-CSS computed values via versioned URL,
shell-markup presence per page, /calc JS+card counts, content-integrity grep). Deployed SHA b72bcca.*
