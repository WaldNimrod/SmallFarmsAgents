# BUILD_REPORT — SFA-S003-P002-WP-UI-patch03 — team_10 — v1.0.0

**Date:** 2026-05-29
**Author:** team_10 (Claude Sonnet sub-agents, orchestrated via Workflow; integrated by team_100)
**WP:** SFA-S003-P002-WP-UI-patch03
**Type:** BUILD_REPORT
**Build commit:** 509c5f5 (initial 1e98c1a + team_00-directed fixes 2e381d7, 509c5f5)
**Spec:** `_aos/work_packages/S003/SFA-S003-P002-WP-UI-patch03/LOD400_spec.md`

## Orchestration
Two parallel Claude Sonnet sub-agents (disjoint paths), then Claude Haiku QA, integrated by team_100.

### Sub-agent A — data layer (`organic_market_agent/publisher/sfa_ingest_push.py`)
- Added `_AGRONOMY_FIELD_WHITELIST` (16 fields, LOD400 §2).
- `_fetch_crop_varieties` now runs one bulk `SELECT variety_id, field_name, value_best FROM
  crop_field_enrichment WHERE field_name IN (...)` and attaches an `agronomy` object to each
  variety `payload_json` (non-null values only; omit `agronomy` when empty). All existing
  payload keys preserved; idempotent.
- Self-test (local oma-postgres): 364/364 varieties; sample variety carries 9–16 agronomy fields. **AC-U3-01.**

### Sub-agent B — frontend (`sfa_delivery/`)
- `CropBookViewController::detail` — `days_to_maturity→dtm_days` alias; per-variety `agro_delta`
  vs the default; `entry()` queries crops for the landing grid.
- `templates/macros/variety_row.php` — agronomic field set with Hebrew labels, drops
  color/taste/shape, `cb-var__val--delta` highlight; renders only present fields.
- `templates/pages/book_crop.php` — `.cb-crop-detail` central full-width wrapper.
- `public_assets/css/hub.css` — `.cb-crop-detail` layout, `.cb-var__grid` 13px (labels 10px),
  `.cb-var__val--delta` accent.
- `templates/pages/book_entry.php` — landing crop-card grid via `crop_card.php`.
- `tests/VarietyRowAgronomyTest.php` — new (AC-U3-04/08/09).
- Self-test: `php -l` clean ×5; `composer test` 57 tests / 0 failures. **AC-U3-02/04/07/08/09.**

## team_00-directed follow-up fixes (during live smoke)
- **2e381d7** — default-variety agronomy backfill from sibling **median** ("the default becomes
  the datum we have"); render-time only (uPress MySQL stays a faithful Postgres mirror).
- **509c5f5** — type-safe (epsilon) delta comparison, eliminating spurious int-vs-float deltas.

## team_100 independent re-verification
`php -l` clean ×5; `composer test` 57/0-fail; `validate_aos.sh` 29/19/0; ingest 364/364 carry agronomy;
no engine/reconciler/schema change; no `www.nimrod.bio`.

— team_10 build (orchestrated) / team_100 integration — 2026-05-29
