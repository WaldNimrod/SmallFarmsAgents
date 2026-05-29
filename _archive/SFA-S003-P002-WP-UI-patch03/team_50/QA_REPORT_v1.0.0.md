# QA_REPORT — SFA-S003-P002-WP-UI-patch03 — team_50 — v1.0.0

**Date:** 2026-05-29
**Author:** team_50 (Claude Haiku, orchestrated via Workflow)
**WP:** SFA-S003-P002-WP-UI-patch03
**Type:** QA_REPORT
**Reviewed commit:** 1e98c1a (pre-fix build) — fixes 2e381d7/509c5f5 verified live by team_100
**Overall:** QA_PASS (10/10 testable ACs; AC-U3-11 deferred to deploy, since verified live)

## AC dispositions
| AC | Disposition | Evidence (independently run) |
|----|-------------|------------------------------|
| AC-U3-01 | PASS | `_fetch_crop_varieties` vs local oma-postgres → 364/364 varieties carry `agronomy`; single bulk query; non-null only; existing keys preserved |
| AC-U3-02 | PASS | `variety_row.php` AGRO_LABELS map; renders only present fields; default variety ≥3 values |
| AC-U3-03 | PASS | controller `dtm_days = dtm_days ?? agronomy.days_to_maturity`; macro uses aliased dtm_days |
| AC-U3-04 | PASS | controller per-variety `agro_delta`; macro applies `cb-var__val--delta`; test covers it |
| AC-U3-05 | PASS | `book_crop.php` `.cb-crop-detail` full-width; `hub.css` rule present |
| AC-U3-06 | PASS | `hub.css` `.cb-var__grid` 13px (labels 10px) — bumped from 11px |
| AC-U3-07 | PASS | `entry()` queries crops; `book_entry.php` renders crop-card grid |
| AC-U3-08 | PASS | grep `variety_row.php` → 0 color/taste/shape labels |
| AC-U3-09 | PASS | `php -l` clean ×5; `composer test` 57 tests / 0 failures |
| AC-U3-10 | PASS | `validate_aos.sh` 29/19/0; no reconciler/schema change; no www.nimrod.bio |
| AC-U3-11 | DEFERRED→MET | live deploy verified by team_100 + team_190 (all URLs 200, agronomy visible) |

**Issues:** none. IR#1 chain: builder Claude Sonnet ≠ QA Claude Haiku ≠ validator (non-Claude team_190).

— team_50 (Claude Haiku) — 2026-05-29
