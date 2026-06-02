# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-DATA (L-GATE_V) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-03
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/sfa-p004-cbdata-classb-2026-06-02`
**Gate:** **L-GATE_V** — final constitutional + live data-binding round for the enrichment mirror.
**Precondition:** team_99 DEPLOY_REPORT (CB-DATA) = SUCCESS — migrations 004/005 applied on uPress + the
`crop_field_enrichment`/`crop_attribute` push completed. Run AFTER deploy+push.

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
LOD author + builder = Claude (team_100 Opus / team_10 Sonnet); L-GATE_B verifier = team_100 Opus; QA = team_50 Haiku. This L-GATE_V **MUST run on a NON-CLAUDE engine**. Confirm in the verdict header.

## 1. Context
WP-CB-DATA mirrors `crop_field_enrichment` + `crop_attribute` (crop-level, default-variety aggregation) to the
uPress MySQL tier so the live `/calc` book-chips and crop-page structured reads bind from tables. L-GATE_S
PASS_WITH_FINDINGS (you, 2026-06-03; 2 INFO addressed inline → LOD v0.2.0). L-GATE_B verified by team_100
(pytest 750/2-pre-existing, composer 141, validate_aos 0 FAIL); team_50 QA PASS. Mirror + transport only — the
enrichment-computation layer is LOCKED and untouched.

## 2. Artifacts
- LOD400 v0.2.0: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-DATA/LOD400_spec.md`
- L-GATE_S verdict: `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-S_VERDICT_v1.0.0.md`
- Build report: `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-DATA/BUILD_REPORT_v1.0.0.md`
- QA: `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-DATA/QA_REPORT_v1.0.0.md`
- Deploy report (precondition): `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-DATA/DEPLOY_REPORT_v1.0.0.md`
- Code: migrations 004/005, `IngestController.php`, `sfa_ingest_push.py` (`_fetch_crop_field_enrichment`/`_fetch_crop_attribute`).

## 3. Checklist
### 3.1 Live data-binding (the point of the WP)
- **C1 — /calc book-chips bind:** on sfa.nimrod.bio, `crop_book_values` is non-empty for enriched crops; the
  `SFA_CROP_BOOK` object is populated; selecting a crop fills `[data-book]` chips (LOD AC-09).
- **C2 — crop-page structured read:** a sample crop page renders numeric provenance + categorical attributes +
  COMPLETE/PARTIAL state derived from the `crop_field_enrichment`/`crop_attribute` TABLES (not only the F-UI-01
  payload fallback) (LOD AC-10). Confirm value_best/unit/field_state/winning_source_class/confidence_score read through.
- **C3 — representative variety (INFO-2):** spot-check a crop with no default variety — the mirrored values match
  the page's default (first-by-name), not a MIN(id) variety.
### 3.2 Code/constitutional (on the deployed SHA)
- **C4 — consumer-contract fidelity:** the 004/005 columns + composite PKs exactly satisfy HubController L142 +
  CropBookViewController L477/L492. field_state backend-stamped (τ=0.40/{EX,NI}); no UI threshold math.
- **C5 — idempotency:** re-push is stable (no duplicate rows; upsert in place).
- **C6 — scope/locked:** no `_aos/` edit; reconciler/enrichment_runner/field_policy/crop_book models/migrations
  035–060 untouched; IR#4 (no builder roadmap edit). `validate_aos.sh` 0 FAIL; pytest crop_book 750 pass / 2
  known pre-existing; composer green.

## 4. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-DATA
gate: L-GATE_V
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | FAIL
live_checks: <n/3>
code_checks: <n/3>
findings: [ {id: F-190-CBDATA-V-NN, severity: …, summary: …, evidence: …} ]
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS** → team_100 advances WP-CB-DATA to LOD500_LOCKED + records the gate + ADR042 archive → team_191.
- **FAIL** → findings back to team_10; re-deploy/re-push; R2.

## 5. Cursor prompt (paste into the non-Claude validator)
> You are **team_190**, validating on a **non-Claude** engine (confirm in the header — IR#1/#5). Repo
> `/Users/nimrod/Documents/SmallFarmsAgents`, branch `claude/sfa-p004-cbdata-classb-2026-06-02`. Gate: **L-GATE_V**
> for WP-CB-DATA — run ONLY after team_99's DEPLOY_REPORT confirms migrations 004/005 applied + the data push
> completed on sfa.nimrod.bio. Run the §3 checklist against the LIVE site (does /calc bind book-chips? do crop
> pages read structured rows from the tables incl. a no-default crop?) AND the deployed code (consumer-contract
> fidelity, idempotency, scope/locked). Emit the verdict YAML (§4) to the path above.
