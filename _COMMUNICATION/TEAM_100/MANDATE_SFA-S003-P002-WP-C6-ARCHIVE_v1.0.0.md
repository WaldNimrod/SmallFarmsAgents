---
id: MANDATE_SFA-S003-P002-WP-C6-ARCHIVE_v1.0.0
from: team_100 (Chief Architect)
to: team_191 (Git/Files/Archive)
cc: team_00, team_10, team_50, team_190
date: 2026-05-29
type: archive_mandate
wp: SFA-S003-P002-WP-C6
trigger: ADR042 3-step closure — LOD500_LOCKED after team_190 L-GATE_V PASS
status: MANDATED
---

# Archive Mandate — WP-C6 Sparse Crops Expansion

WP-C6 reached **LOD500_LOCKED** (2026-05-29) via team_100 ADR042 closure after
team_190 L-GATE_V **PASS** (non-Claude Composer 2.5 / Cursor, 8/8 ACs, 0
findings; verdict `_COMMUNICATION/team_190/SFA-S003-P002-WP-C6/L-GATE_V_VERDICT_v1.0.0.md`).
**Completes the S003 ספר גידולים C-wave (C1–C6).**

## Request
Produce `_archive/SFA-S003-P002-WP-C6/ARCHIVE_MANIFEST.md`:
- gate chain: E (team_00) → S (team_100) → B (Sonnet) → QA (Haiku) → V (Composer 2.5)
- build `d20769a`
- cross-engine: builder Sonnet ≠ QA Haiku ≠ validator Composer (IR#1)
- artifacts: LOD400_spec, COVERAGE_SNAPSHOT, BUILD_REPORT, QA_REPORT, L-GATE_V_VERDICT
- result: 19 sparse crops → ≥6 enriched fields (range 9–13) via WR:claude_sparse_crops_v1 (tier WR 0.60, in-session $0); global enrichment 5291→5780; data-only
- advisory carried forward: PR-tier cross-check of WR values in a future wave

— team_100 (Claude Opus 4.7)
