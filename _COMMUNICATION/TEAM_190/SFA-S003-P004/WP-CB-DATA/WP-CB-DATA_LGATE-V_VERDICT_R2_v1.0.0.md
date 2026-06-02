---
id: VERDICT_SFA-S003-P004-WP-CB-DATA_L-GATE_V_R2_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-03
type: validation_verdict
wp: SFA-S003-P004-WP-CB-DATA
gate: L-GATE_V
mandate: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-DATA/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md
deploy_report: _COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md
branch: claude/sfa-p004-cbdata-classb-2026-06-02
branch_head: 5ead7e1c2138f96284f246e57d0bda61e1f91be1
deployed_sha: c51c2e57bb70698bbf2ff5f179188bb94951f6c0
validator_engine: Cursor / Composer 2.5 Fast (GPT — non-Claude)
phase_owner: team_190
correction_cycle: R2
prior_verdict: _COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-V_VERDICT_v1.0.0.md
result: PASS_WITH_FINDINGS
---

# WP-CB-DATA L-GATE_V Verdict (R2)

```yaml
wp: SFA-S003-P004-WP-CB-DATA
gate: L-GATE_V
validator_engine: Cursor / Composer 2.5 Fast (GPT — non-Claude)
result: PASS_WITH_FINDINGS
live_checks: 3/3
code_checks: 3/3
findings:
  - id: F-190-CBDATA-V-R2-01
    severity: INFO
    summary: "C3 live no-default crop spot-check N/A — canonical Postgres has 0 crops lacking is_default; representative-variety rule attested by code + AC-04 tests only."
    evidence: "docker exec oma-postgres psql -U oma -d organic_market_agent → no_default_count=0 (2026-06-03). sfa_ingest_push.py L631-641 CTE ORDER BY is_default DESC, name ASC; test_ingest_enrichment_mirror.py AC-04a/b PASS."
    disposition: builder-acknowledge
  - id: F-190-CBDATA-V-R2-02
    severity: INFO
    summary: "pytest crop_book 750 pass / 2 known pre-existing fail (unchanged from L-GATE_B baseline)."
    evidence: "FAILED test_ni_publisher_isolation.py::TestNiPublisherIsolation::test_ac21b_publisher_dir_clean; FAILED test_source_registry.py::test_uc_prefix_requires_moderation (2026-06-03 @ 5ead7e1)."
    disposition: builder-acknowledge
summary: "L-GATE_V R2 PASS_WITH_FINDINGS: team_99 DEPLOY_REPORT precondition met (migrations 004/005 + 1010 rows @ c51c2e5). Live /calc emits populated window.SFA_CROP_BOOK; crop pages read table-backed provenance (watermelon pv-validated=18/pv-fallback=0; anise-hyssop 9/0). Branch consumer-contract, idempotency, scope, composer 141/141, validate_aos 0 FAIL all satisfied. team_100 may advance WP-CB-DATA to LOD500_LOCKED."
```

## Engine constraint (IR#1 / IR#5)

Validator: **Cursor / Composer 2.5 Fast (GPT — non-Claude)**. LOD author team_100 (Claude Opus); builder team_10 (Claude Sonnet); L-GATE_B team_100; QA team_50 (Claude Haiku). Cross-engine satisfied.

## Precondition gate (R2)

| Requirement | Result | Evidence |
|-------------|--------|----------|
| team_99 DEPLOY_REPORT = SUCCESS | **PASS** | `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md` status SUCCESS, deployed_sha c51c2e5 |
| Migrations 004/005 + data push | **PASS** | 767 enrichment + 243 attribute rows; `/admin/migrate` applied both tables |

## Live data-binding (mandate §3.1)

| Check | Result | Evidence |
|-------|--------|----------|
| C1 `/calc` book-chips + `SFA_CROP_BOOK` | **PASS** | `curl -sL https://sfa.nimrod.bio/calc/` → `window.SFA_CROP_BOOK = {` count=1; keys include `watermelon`, `anise-hyssop` |
| C2 Crop-page structured read from tables | **PASS** | `/crop-book/watermelon`: pv-validated=18, pv-fallback=0, unit `<small>` tags present. `/crop-book/anise-hyssop`: pv-validated=9, pv-fallback=0 |
| C3 No-default → first-by-name (not MIN id) | **PASS (code-attested)** | Postgres no_default_count=0 → live spot-check N/A; CTE + CropBookViewController name-order alignment + pytest AC-04 (see F-190-CBDATA-V-R2-01) |

## Code/constitutional (deployed SHA c51c2e5)

| Check | Result | Evidence |
|-------|--------|----------|
| C4 Consumer-contract fidelity | **PASS** | 004 PK `(crop_id, field_name)` columns match HubController L142-155 + CropBookViewController L477; 005 matches L492. IngestController allowlists L45-52. field_state stamped at push (`_FIELD_STATE_TAU=0.40`, `{EX,NI}`); prov_value.php L10-13 no UI threshold math |
| C5 Idempotency | **PASS** | Live re-push `--table crop_attribute --limit 5` → HTTP 200, accepted=5, rejected=0. IngestEnrichmentMirrorTest.php OK (6/6) |
| C6 Scope/locked + tests | **PASS** | Locked reconciler/enrichment_runner/field_policy + alembic 035-060: 0-line diff vs main. validate_aos 29 PASS / 19 SKIP / 0 FAIL. pytest crop_book 750 pass / 2 pre-existing fail. composer 141/141 |

## R1 → R2 delta

| R1 state (2026-06-03) | R2 state |
|-----------------------|----------|
| No DEPLOY_REPORT; live SFA_CROP_BOOK empty | DEPLOY_REPORT SUCCESS; populated 11 651 B assignment live |
| Crop pages payload-only fallback | pv-validated > 0, pv-fallback = 0 on sampled crops |
| code_checks 3/3 (branch ready) | code_checks 3/3 confirmed @ c51c2e5 |

## Verdict

**PASS_WITH_FINDINGS** — team_100 may advance WP-CB-DATA to **LOD500_LOCKED** and record the gate + ADR042 archive mandate → team_191.

— team_190
