---
id: L-GATE_V_MANDATE_SFA-S003-P002-WP-C6_v1.0.0
from: team_100 (Chief Architect — orchestrator)
to: team_190 (cross-engine validator — MUST be non-Claude per IR#1)
cc: team_00, team_10, team_50
date: 2026-05-29
type: validation_mandate
wp: SFA-S003-P002-WP-C6
gate: L-GATE_V
build_commit: "d20769a"
status: AWAITING_VALIDATION
---

# L-GATE_V Mandate — WP-C6 Sparse Crops Expansion

## Cross-engine (IR#1)
Built (Sonnet model) + QA'd (Haiku) — both Claude. Validator MUST be **non-Claude**
(GPT-5.x / Gemini / Cursor). builder ≠ QA ≠ validator.

## What was built
19 "sparse" crops (≤2 enriched fields) raised to **≥6 enriched fields each** via
in-session ($0) WR-tier agronomic data (`WR:claude_sparse_crops_v1`, weight 0.60)
→ importer `ni/claude_sparse_crops_research.py` → `run_enrichment`. Data-only; no
migration/engine/schema change. Spec: `_aos/work_packages/S003/SFA-S003-P002-WP-C6/LOD400_spec.md`.

## Verify (independently)
1. Coverage — all 19 crops ≥6 enriched fields (crop_ids 1,5,13,16,22,23,24,28,29,31,32,34,37,38,43,47,48,50,57):
   `docker exec oma-postgres psql -U oma -d organic_market_agent -c "WITH cov AS (SELECT c.id, COUNT(DISTINCT cfe.field_name) ef FROM crops c LEFT JOIN crop_varieties v ON v.crop_id=c.id LEFT JOIN crop_field_enrichment cfe ON cfe.variety_id=v.id WHERE c.id IN (1,5,13,16,22,23,24,28,29,31,32,34,37,38,43,47,48,50,57) GROUP BY c.id) SELECT min(ef), max(ef), count(*) FILTER (WHERE ef>=6) FROM cov;"` → min ≥6, count=19.
2. WR provenance — `SELECT count(*) FROM crop_variety_source_values WHERE source='WR:claude_sparse_crops_v1' AND trust_tier='WR';` ≈180.
3. Data-only — `git diff --stat <base>..d20769a` shows only the JSON pack, importer, seed.py, test, BUILD_REPORT.
4. Tests — `.venv/bin/python -m pytest tests/crop_book/test_c6_sparse_crops.py -q` all pass.
5. `validate_aos.sh .` 0 FAIL.
6. Constitutional: builder/QA/validator engines distinct; `_aos/` authored by team_100 (not builder).

## Disclosed caveat (not a defect)
Values are AI-synthesized at WR confidence 0.60 (per-crop `_basis`, no fabricated
source URLs — AC-C6-06 adjusted from the spec). This is exactly the WR tier's
purpose; a future PR-tier pass should cross-check. Validate plausibility, not
published-source precision.

## Evidence
LOD400_spec.md · COVERAGE_SNAPSHOT_v1.0.0 · BUILD_REPORT_v1.0.0 (team_10) ·
QA_REPORT_v1.0.0 (team_50).

## Verdict
→ `_COMMUNICATION/team_190/SFA-S003-P002-WP-C6/L-GATE_V_VERDICT_v1.0.0.md`
(name your engine). On PASS → team_100 ADR042 closure → LOD500_LOCKED.

— team_100 (Claude Opus 4.7) 2026-05-29
