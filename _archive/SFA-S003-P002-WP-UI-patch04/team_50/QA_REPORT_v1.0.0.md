# QA_REPORT — SFA-S003-P002-WP-UI-patch04 — team_50 — v1.0.0

**Date:** 2026-05-29
**Author:** team_50 (Claude Haiku, orchestrated via Workflow)
**WP:** SFA-S003-P002-WP-UI-patch04
**Type:** QA_REPORT
**Reviewed commit:** 70dc728 (pre post-QA fixes)
**Overall:** QA_PASS_WITH_FINDINGS — all code ACs PASS; AC-U4-02/12 (live cover-crops + deploy) deferred to team_100 push/deploy.

## AC dispositions (LOD400 §4)
| AC | Disposition | Note |
|----|-------------|------|
| AC-U4-01 ingest rich payload | PASS | 7 sections embedded; public-notes filter present |
| AC-U4-02 cover-crops | DEFERRED→CODE PASS | fetcher + route + page wired (data not pushed — junk source) |
| AC-U4-03 species-first order | PASS | identity→…→varieties last |
| AC-U4-04 sections render data | PASS | arugula identity/calendar/harvest/storage/companions |
| AC-U4-05 internal notes never render | PASS | ingest + template hard-gate |
| AC-U4-06 global nav + sub-nav | PASS (R1) → fixed in L-GATE_V | (see note) |
| AC-U4-07 0 broken links | PASS (code) → 0 live after fixes | |
| AC-U4-08 full-width | PASS | `.cb-crop-detail` |
| AC-U4-09 landing sizing | PASS | responsive grid; valid slugs |
| AC-U4-10 tests | PASS | php -l clean; composer test 63/0-fail |
| AC-U4-11 constitutional | PASS | validate_aos 29/19/0; no schema/reconciler/www |
| AC-U4-12 live deploy | DEFERRED | team_100 deploy |

**Issues:** none at QA. (Note: AC-U4-06 later failed live at L-GATE_V R1 due to a `$active`
scope clobber not observable in the unit suite; fixed in build a7a787a, L-GATE_V R2 PASS.)
IR#1: builder Sonnet ≠ QA Haiku ≠ validator (non-Claude team_190).

— team_50 (Claude Haiku) — 2026-05-29
