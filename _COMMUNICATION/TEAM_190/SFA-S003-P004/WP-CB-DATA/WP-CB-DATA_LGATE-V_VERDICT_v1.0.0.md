---
id: VERDICT_SFA-S003-P004-WP-CB-DATA_L-GATE_V_v1.0.0
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
branch: claude/sfa-p004-cbdata-classb-2026-06-02
branch_head: d0437c61ab6af1feef07021aceda27330dcf035f
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
phase_owner: team_190
correction_cycle: R1
result: FAIL
---

# WP-CB-DATA L-GATE_V Verdict

```yaml
wp: SFA-S003-P004-WP-CB-DATA
gate: L-GATE_V
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
result: FAIL
live_checks: 0/3
code_checks: 3/3
findings:
  - id: F-190-CBDATA-V-01
    severity: BLOCKER
    summary: "Mandate precondition unmet — team_99 DEPLOY_REPORT for WP-CB-DATA not present in repo; live site shows no enrichment mirror bind."
    evidence: "Expected `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md` absent (2026-06-03). Live `curl https://sfa.nimrod.bio/calc` has SFA_CROP_BOOK JS references but no `window.SFA_CROP_BOOK = {…}` assignment (PHP `crop_book_values` empty → table absent or empty)."
    disposition: R2
  - id: F-190-CBDATA-V-02
    severity: BLOCKER
    summary: "C1 FAIL — /calc book-chips do not bind from crop_field_enrichment (AC-09)."
    evidence: "Branch emits assignment only when `!empty($crop_book_values)` (calc_dash.php L434–440). Live calc HTML: grep `window.SFA_CROP_BOOK =` → 0; only consumer JS at L802. `data-book` chips present but no populated book object."
    disposition: R2
  - id: F-190-CBDATA-V-03
    severity: BLOCKER
    summary: "C2 FAIL — crop pages do not read structured enrichment from mirror tables (AC-10)."
    evidence: "Live `/crop-book/lettuce?depth=full` (88 830 B): `statebadge--partial` renders (F-UI-01 payload path) but `winning_source_class`=0, `confidence_score`=0, `prov__cue`/`pv-validated`/`tip` cues absent; provenance block for days_to_maturity is an empty `.prov` shell — not table-backed structured rows with unit + source class."
    disposition: R2
  - id: F-190-CBDATA-V-04
    severity: MAJOR
    summary: "C3 NOT VERIFIED live — no-default first-by-name mirror spot-check blocked (migrations/push not attested on production)."
    evidence: "Publisher dry-run on branch Mac PG yields 767 enrichment rows; no `no default variety` log (0 no-default crops in canonical DB). Cannot compare live mirror vs first-by-name without successful push + DEPLOY_REPORT."
    disposition: R2
  - id: F-190-CBDATA-V-05
    severity: INFO
    summary: "C5 live idempotency re-push not executed (HMAC ingest); branch PHPUnit AC-08 PASS."
    evidence: "IngestEnrichmentMirrorTest.php OK (6 tests, 25 assertions) on branch @ d0437c6 — duplicate=true replay + stable row count."
    disposition: builder-acknowledge
  - id: F-190-CBDATA-V-06
    severity: INFO
    summary: "Branch code/constitutional checks PASS — consumer contract, scope, tests ready pending deploy."
    evidence: "IngestController TABLE_COLUMNS L45–52 match HubController L142–155 + CropBookViewController L477/492; locked reconciler/enrichment_runner untouched (0-line diff vs main); pytest crop_book 750 pass / 2 known pre-existing fail; composer 141/141; validate_aos.sh 29 PASS / 19 SKIP / 0 FAIL."
    disposition: builder-acknowledge
summary: "L-GATE_V FAIL: team_99 DEPLOY_REPORT for CB-DATA is missing and live sfa.nimrod.bio does not bind /calc book-chips or crop-page structured reads from crop_field_enrichment/crop_attribute (no embedded SFA_CROP_BOOK object; no table-sourced provenance cues). Branch implementation and tests are ready (code_checks 3/3). team_99 must complete coupled Class B + CB-DATA deploy (migrations 004/005 + Mac push), publish DEPLOY_REPORT SUCCESS, then team_190 re-runs L-GATE_V R2."
```

## Engine constraint (IR#1 / IR#5)

Validator: **Cursor / Composer 2.5 (GPT — non-Claude)**. LOD author + L-GATE_B verifier = Claude (team_100 / team_10); QA = team_50 (Claude Haiku). Cross-engine satisfied.

## Precondition gate

| Requirement | Result | Evidence |
|-------------|--------|----------|
| team_99 DEPLOY_REPORT = SUCCESS | **FAIL** | `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md` not found in repo |
| Migrations 004/005 applied + data push | **FAIL** | Live `/calc` lacks `window.SFA_CROP_BOOK = {…}`; crop pages lack table provenance markers |
| Coupled Class B deploy (same FTPS pass) | **FAIL** | Live still lacks `.hub-home__inner`, `contact.webp`, `.ptable__th` (see WP-CB-UI-CLASSB R2 verdict) |

## Live data-binding (mandate §3.1)

| Check | Result | Evidence |
|-------|--------|----------|
| C1 `/calc` book-chips + `SFA_CROP_BOOK` | **FAIL** | No JSON assignment in live calc HTML; HubController join returns empty when table missing/empty |
| C2 Crop-page structured read + COMPLETE/PARTIAL from tables | **FAIL** | Lettuce full depth: partial badge only; no `winning_source_class` / validated prov cues in HTML |
| C3 No-default → first-by-name (not MIN id) | **NOT VERIFIED** | Blocked on live mirror; branch fetcher uses `ORDER BY is_default DESC, name ASC` per LOD §2.1 |

## Code/constitutional (branch @ d0437c6)

| Check | Result | Evidence |
|-------|--------|----------|
| C4 Consumer-contract fidelity | **PASS** | Migrations 004/005 columns + composite PKs; IngestController whitelist; field_state via `_FIELD_STATE_TAU=0.40` / `{EX,NI}` in `sfa_ingest_push.py` |
| C5 Idempotency | **PASS (branch)** | `IngestEnrichmentMirrorTest.php` + pytest mirror module (28 pass); live re-push not run |
| C6 Scope/locked + tests | **PASS (branch)** | No reconciler/enrichment_runner edits; pytest 750/2 pre-existing; composer 141; validate_aos 0 FAIL |

## Verdict

**FAIL** — do not advance to LOD500_LOCKED. Route team_99 deploy + data push → publish DEPLOY_REPORT → team_190 L-GATE_V R2.

— team_190
