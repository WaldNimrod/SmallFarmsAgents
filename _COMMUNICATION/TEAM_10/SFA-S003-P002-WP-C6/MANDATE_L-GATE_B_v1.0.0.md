---
id: MANDATE_L-GATE_B_SFA-S003-P002-WP-C6_v1.0.0
from: team_100 (Chief Architect)
to: team_10 (builder — Claude Sonnet)
cc: team_00, team_50, team_190
date: 2026-05-28
type: build_mandate
wp: SFA-S003-P002-WP-C6
gate: L-GATE_B
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C6/LOD400_spec.md
status: MANDATED
---

# L-GATE_B Build Mandate — WP-C6 Sparse Crops Expansion

team_10 (Claude **Sonnet**) builds per LOD400_spec.md v1.0.0. The full spec is
binding — this mandate is the dispatch summary.

## Goal
Bring the **19 sparse crops** (≤2 enriched fields; list in LOD400 §2 +
`_COMMUNICATION/team_100/SFA-S003-P002-WP-C6/COVERAGE_SNAPSHOT_v1.0.0.md`) to
**≥6 enriched fields each** via in-session WR research (NO external API, $0,
web-grounded) → import as `WR:claude_sparse_crops_v1` → re-run enrichment.

## Deliverables (LOD400 §5)
1. WR pack JSON: `data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json` (gemini-pack schema + `_sources` URLs per crop).
2. Importer `organic_market_agent/crop_book/importer/ni/claude_sparse_crops_research.py` — mirror `ni/gemini_il_research.py` (SOURCE=`WR:claude_sparse_crops_v1`, TRUST=`WR`, CONFIDENCE=0.60, 19-crop name_he map, idempotent).
3. Wire into the WR import entrypoint; run importer + `enrichment_runner.run_enrichment(session, dry_run=False)`.
4. `tests/crop_book/test_c6_sparse_crops.py` (each crop ≥6 fields; no regression).

## Hard constraints
- DB: local `oma-postgres` (5433), db `organic_market_agent`, alembic head 056.
- Data-only: NO new field_names, NO migrations, NO engine/reconciler/schema change.
- `crops.name_he` must match DB exactly (ids in LOD400 §2). 0 unresolved lookups.
- Web-ground each value (WebSearch/WebFetch) against reputable extension/horti
  sources; omit a field rather than fabricate. ≥6 SOLID fields > 10 shaky.
- Verify all of AC-C6-01..10 (LOD400 §6) and record evidence per AC.
- Touch only: the new JSON, the new importer, the test, and the import wiring.
  Do NOT edit `_aos/`, other teams' `_COMMUNICATION/`, or unrelated files.

## Deliverable on done
BUILD_REPORT → `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C6/BUILD_REPORT_v1.0.0.md`
(per-AC table + the coverage query before/after). Commit on branch
`wp/c6-sparse-crops`. Flag QA readiness to team_50.

— team_100 (Claude Opus 4.7) 2026-05-28
