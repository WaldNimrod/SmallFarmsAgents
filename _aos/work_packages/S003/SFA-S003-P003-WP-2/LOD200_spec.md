# LOD200 — SFA-S003-P003-WP-2 — Slim PHP Skeleton + DB Schema + Ingest API (STUB)

**Date:** 2026-05-23
**Status:** LOD200_DRAFT — **BLOCKED on WP-1 output**. This is a stub; full LOD200 → LOD400 will be authored after WP-1 (uPress provisioning checklist) returns concrete values for PHP version, MySQL specs, FTP paths.

## Scope summary (to be expanded post-WP-1)

Build the foundation app on `sfa.nimrod.bio`:

1. **Slim Framework 4** PHP application skeleton
   - Composer autoload (or manual if no SSH on uPress)
   - Routing layer
   - Middleware: auth (for ingest endpoint), CORS, error handling, logging
2. **DB schema** (MySQL — mirror of relevant Postgres tables on waldhomeserver):
   - `crops` (52 rows expected)
   - `crop_varieties` (242 rows)
   - `crop_variety_source_values` (audit trail per field per source)
   - `crop_families`, `crop_conversion_groups`, `crop_unit_conversions`
   - `market_products` (32+ rows)
   - `market_index_runs` (provenance per daily run)
3. **Migrations system**: numbered SQL files (`001_init.sql`, `002_add_*.sql`) + tiny PHP runner script (~50 lines)
4. **Ingest API endpoint**: `POST /api/v1/ingest`
   - Auth: HMAC-SHA256 header (shared secret with waldhomeserver publisher)
   - Body: JSON delta payload — what changed since last push
   - Idempotency: by `(table, primary_key, version)` tuple
   - Response: 200 with counts, 4xx on auth/validation error
5. **Read API endpoints** (for WP-3 to consume):
   - `GET /api/v1/crops` — list with filters (category, season, search)
   - `GET /api/v1/crops/<id>` — full detail with varieties + source_values
   - `GET /api/v1/products` — market index list
   - `GET /api/v1/products/<id>` — market detail with price history

## Effort estimate

~2-3 days post-unblock by WP-1 (assuming standard PHP 8.x + MySQL 8.x).

## Will be expanded to LOD400 when

- WP-1 results received (`_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_*.md`)
- Concrete answers to: PHP version, MySQL version, FTP path, Composer availability

---

*Stub LOD200 — authored 2026-05-23 by team_100. To be expanded post-WP-1.*
