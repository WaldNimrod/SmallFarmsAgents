---
id: BUILD_REPORT_SFA-S003-P002-WP-C6_v1.0.0
from: team_10 (builder — executed by team_100 orchestrator after sub-agent was killed)
to: team_50 (QA), team_190 (validator), team_100
date: 2026-05-29
type: build_report
wp: SFA-S003-P002-WP-C6
gate: L-GATE_B
branch: wp/c6-sparse-crops
status: BUILD_COMPLETE — QA READY
---

# WP-C6 Build Report — Sparse Crops Expansion

## Method
WR-tier (0.60) agronomic data for the 19 sparse crops, **generated in-session
($0, no external API)** — exactly the model team_00 confirmed. Flat-schema WR
pack → mirror-of-gemini importer → `crop_variety_source_values` (`WR:claude_sparse_crops_v1`)
→ `run_enrichment` → `crop_field_enrichment`.

## Deliverables
- `data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json` (19 crops, flat `fields` schema, `_basis` per crop)
- `organic_market_agent/crop_book/importer/ni/claude_sparse_crops_research.py` (SOURCE=WR:claude_sparse_crops_v1, TRUST=WR, CONFIDENCE=0.60, idempotent upsert)
- `organic_market_agent/crop_book/importer/seed.py` — wired into `--all` flow (gated `no_claude_sparse`)
- `tests/crop_book/test_c6_sparse_crops.py` (6 tests)

## Coverage: before → after (all 19 crops ≥6 enriched fields)
| crop | before | after | | crop | before | after |
|---|---|---|---|---|---|---|
| Ginger | 0 | 10 | | Lemon Verbena | 2 | 11 |
| Bay | 1 | 10 | | Lovage | 2 | 11 |
| Anise Hyssop | 1 | 10 | | Hibiscus | 2 | 12 |
| Lemon Balm | 1 | 10 | | Jerusalem Artichoke | 2 | 12 |
| Mint | 1 | 10 | | Oranges | 2 | 12 |
| Sage | 1 | 10 | | Pac Choi | 2 | 12 |
| Tarragon | 1 | 9 | | Turmeric | 2 | 12 |
| Thyme | 1 | 10 | | Jicama | 2 | 13 |
| Chinese Lantern | 1 | 10 | | Salad Mix | 2 | 10 |
| Cress | 1 | 11 | | | | |
**19/19 now ≥6 (range 9–13).** Global enrichment fields 5291 → 5780 (+489).

## Acceptance Criteria
| AC | Result | Evidence |
|----|--------|----------|
| AC-C6-01 each of 19 ≥6 fields | ✅ PASS | live coverage query: 19/19, min 9 |
| AC-C6-02 WR source_label/tier | ✅ PASS | 180 rows `source='WR:claude_sparse_crops_v1'` tier WR |
| AC-C6-03 no regression | ✅ PASS | total enrichment 5291→5780 (additive); no field removed |
| AC-C6-04 idempotent | ✅ PASS | re-run ingest → WR rows stable at 180 (upsert by variety/field/source) |
| AC-C6-05 all name_he resolve | ✅ PASS | ingest: processed=19, skipped=0 |
| AC-C6-06 grounding recorded | ⚠️ ADJUSTED | per-crop `_basis` records synthesis basis. NOTE: values are AI-synthesized (WR tier); no per-field URLs fabricated. Recommend PR-tier cross-check before promotion. |
| AC-C6-07 tests pass | ✅ PASS | pytest 6/6 (incl. live-DB integration) |
| AC-C6-08 data-only | ✅ PASS | no migration/engine/schema/field_name change |
| AC-C6-09 validate_aos 0 FAIL | ✅ PASS | 29 PASS / 19 SKIP / 0 FAIL |
| AC-C6-10 enrichment stable/up | ✅ PASS | varieties 367→368, fields 5291→5780, high_conf 811 |

## Honesty note (AC-C6-06)
The spec called for per-field web-grounded `_sources` URLs. To avoid fabricating
citations, values are AI-synthesized from established horticulture/extension
norms (recorded as `_basis` per crop) at WR confidence 0.60 — which is precisely
what the WR tier represents. A future PR-tier pass (published extension sources)
should cross-check before any promotion to higher confidence.

## Next
team_50 (Haiku) QA → team_190 (non-Claude) L-GATE_V → team_100 ADR042 closure.
