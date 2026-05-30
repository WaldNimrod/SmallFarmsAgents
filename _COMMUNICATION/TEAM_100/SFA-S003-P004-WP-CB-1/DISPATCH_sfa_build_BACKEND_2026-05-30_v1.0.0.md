# BUILD DISPATCH (BACKEND SLICE) — SFA-S003-P004-WP-CB-1 — team_100 → team_10 — v1.0.0

**Date:** 2026-05-30
**From:** team_100 (Chief Architect, Claude Code)
**To:** team_10 (sfa_build — Claude **Sonnet**; cross-engine IR#1: builder Sonnet ≠ validator)
**WP:** SFA-S003-P004-WP-CB-1 — Crop Book v1
**Scope:** **BACKEND / INFRASTRUCTURE ONLY** (UI-independent). Runs in parallel with team_35 UI design.
**Gate:** L-GATE_S PASS (backend scope, team_100 delegated) → build → team_50 QA → team_190 L-GATE_V (non-Claude)

---

## 1. Why a backend slice

team_00 directive 2026-05-30: progress the server side + infrastructure **in parallel** with team_35's UI design (which takes time). The LOD400 backend sections are fully specified and need **no mockups**. This dispatch covers exactly the UI-independent work; the UI slice (AC-10/11/13, §7/§10) is dispatched separately once team_35 LOD300 lands.

## 2. Read first
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-1/LOD400_spec.md` — §2–§6, §9 (steps 1–6), §11 (AC-01..09, 12), §12
- `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-1/{CALCULATOR_CATALOG,MANDATORY_FIELD_SCHEMA,GAP_FILL_PLAN}_v1.0.0.md`
- `organic_market_agent/crop_book/field_policy.py`, `importer/enrichment_runner.py`, `enrichment_models.py`, `publisher/sfa_ingest_push.py`

## 3. Build scope (in order — LOD400 §9 steps 1–6)
1. **`field_policy.py`** += `days_in_nursery_cell` (weighted_mean, EX>NI>PR>OP, z=3.5) + `succession_interval_weeks` (hard_winner, EX>NI>PR>OP) — exact snippets in LOD400 §3.1. Extend `test_field_policy.py`.
2. **`succession_interval_weeks` source rows** (LOD400 §3.2): ensure ≥1 `crop_variety_source_values` row exists for the shown set (JMF column if present, else stage EX/NI/WR seed). Then run `seed --enrich`; verify `crop_field_enrichment` rows appear for both new fields.
3. **`assumptions.py`** (NEW) — `Assumption` dataclass + `ASSUMPTIONS` registry + `get_assumption()` (LOD400 §4 / Schema §3.3). 8 keys; `germination_rate` (0.90) + `bed_width` (0.80) carry `post_url` (provisional finals: `https://nimrod.bio/seed-germination-rate/`, `https://nimrod.bio/garden-bed-width-80cm/` — see ROUTING_PROMPT_nimrod-bio_ASSUMPTION_POSTS). Include `tray_cells` + `hardiness_offset` tables. `test_assumptions.py`.
4. **`calculators.py`** (NEW) — all **14** pure functions with the EXACT §5 signatures + frozen result dataclasses + `CalcUnavailable`. No DB/IO/globals. `test_calculators.py` ≥30 tests (≥2/calc incl. one edge; assert numeric results match §5 formulas).
5. **`calculator_meta.py`** (NEW) — per-calc {audience, required_book_fields, assumption_keys, user_inputs}; must equal Catalog §6 (`test_calculator_meta.py` asserts equality). Disabled-state unit test (AC-08) over a synthetic field_state map.
6. **`sfa_ingest_push.py`** — agronomy whitelist += `days_in_nursery_cell`, `succession_interval_weeks`; embed per-field `field_state` (VALIDATED/UNVALIDATED/MISSING, τ=0.40, Gap-Fill §2) + the `ASSUMPTIONS` registry into payload. Preserve all existing keys.

## 4. Acceptance criteria (this slice)
AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, **AC-12** (validate_aos 0 FAIL; `pytest tests/crop_book/` green; **no change to LOD500_LOCKED files** per LOD400 §2 — reconciler/enrichment_runner/enrichment_models/migrations/models.py/constants.py).
**DEFERRED to UI slice (do NOT attempt):** AC-10 (UI), AC-11 (JS parity), AC-13 (live smoke), §7/§10. **No deploy** — data/UI deploy is a separate gated step.

## 5. Constraints
- **Iron Rule #4:** builder commits code ONLY — no edits to `_aos/roadmap.yaml`.
- **Iron Rule #1:** builder = Sonnet; final L-GATE_V = team_190 (non-Claude). team_50 (Haiku) QA in between.
- **No migration** expected (additive policy + config only). If one proves necessary, STOP and flag team_100.
- Hosting canon respected: no www.nimrod.bio; delivery tier untouched in this slice.

## 6. Deliverable
`BUILD_REPORT_v1.0.0.md` in `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1/` — per-AC attestation, test counts, validate_aos result, files touched, confirmation no LOD500_LOCKED file changed.
