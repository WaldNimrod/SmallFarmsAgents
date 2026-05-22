---
id: SFA-S003-P001-LOD400-VERDICT
type: L-GATE_SPEC verdict
validator: team_190
date: 2026-05-07
wps: [SFA-S003-P001-WP002, SFA-S003-P001-WP003]
verdict: PASS_WITH_FINDINGS
---

# L-GATE_SPEC Verdict - SFA-S003-P001 - Team 190 - v1.0.0

**Date:** 2026-05-07
**Author:** team_190
**WP:** SFA-S003-P001-WP002 + SFA-S003-P001-WP003
**Type:** L-GATE_SPEC verdict

## §0 Summary

Team 190 returns **PASS_WITH_FINDINGS** for SFA-S003-P001-WP002 and SFA-S003-P001-WP003 at L-GATE_SPEC. The LOD400 specs are sufficient for sfa_build / team_10 to begin implementation, and no hard Iron Rule violation or unbuildable condition was found. Findings below are non-blocking but must be carried into build execution and LOD500 closure, because several spec details diverge from the LOD200 schema foundation or leave UI behavior imprecise.

## §1 Constitutional Checks C1-C10

| Check | Result | Finding if any |
|---|---|---|
| C1 Directory authority | PASS_WITH_FINDING | WP002 necessarily creates Alembic migrations under `organic_market_agent/db/versions/`, which is application source and not forbidden, but the activation checklist's narrow path list omitted this required migration location. Both specs also list team_10 build reports under `_COMMUNICATION/team_10/`; this is acceptable as team_10's own artifact space, but it should not be confused with application deliverables. |
| C2 Raw material guard | PASS | WP002 AC-08 explicitly requires source CSV/XLSX files to remain read-only and never written, moved, or deleted. |
| C3 Iron Rule #1 - cross-engine | PASS | Builder is sfa_build / Team 10 / Sonnet; validator is team_190 / external non-Claude. |
| C4 Iron Rule #4 - roadmap single writer | PASS | Neither LOD400 spec directs the builder to update `_aos/roadmap.yaml`; roadmap updates remain with team_100 after verdict. |
| C5 Iron Rule #7 / ADR034 R9 offline DB | PASS | Offline DB is expected. WP002 specifies `require_postgres` skip/mock behavior in AC-01-OFFLINE, and WP003 uses mocked DB sessions for view tests. |
| C6 Scope isolation | PASS | WP002 owns migrations/models/importer. WP003 depends on WP002 tables and models for read-only views and declares no writes to crop-book data. |
| C7 ACs are testable | PASS_WITH_FINDING | Most ACs are objective. WP003 has a few conflicting statements around conditional tab visibility versus all-tab rendering; see §4. |
| C8 S002 regression risk | PASS | The module is additive. Existing S002 tables and publish paths are not modified; admin registration is additive. |
| C9 validate_aos.sh mandate | PASS | WP002 AC-08 and WP003 AC-11 both require `validate_aos.sh .` to return 0 FAIL. Current preflight observed 29 PASS / 17 SKIP / 0 FAIL. |
| C10 No half-finished implementation | PASS_WITH_FINDING | S003 view-only scope is broadly complete. Market-price delta/live price display is deferred in WP003 build notes, which is acceptable only if the builder renders the specified placeholder and documents the pricebook integration boundary in LOD500. |

## §2 Additional findings

1. **C-check label drift in the submitted materials.** The activation handoff and bundle manifest both define C1-C10, but C7/C8/C9 labels do not fully match. This verdict uses the activation handoff matrix as authoritative. This is a process precision issue, not a blocker.
2. **`/tmp/crop_book_v3.html` is an unstable reference path.** WP003 references the prototype and `ENTITY_REGISTRY` in `/tmp`. The file exists in this session and contains `ENTITY_REGISTRY`, but `/tmp` is not durable. Builder may proceed, but should copy the registry into repo-owned JS during implementation and record the copied source/version in LOD500.

## §3 WP002-specific findings

1. **LOD200 ID type drift.** LOD200 defines all six table `id` fields as UUID PKs, while WP002 §2.5 and §5 specify BigInteger PKs. The LOD400 spec is internally buildable, but it is not type-consistent with the approved LOD200 schema foundation. Builder may proceed using LOD400 BigInteger only because the build notes explicitly call it the intended existing-pattern choice; Team 100 should record this as an approved schema refinement before L-GATE_VALIDATE.
2. **Field-name storage convention needs build discipline.** LOD200 examples for `זן_ערכי_מקור.שם_שדה` use Hebrew logical field names, while WP002/WP003 query and reconcile using English DB field names such as `documented_price`. Builder should standardize on English DB field names for `crop_variety_source_values.field_name` to keep WP003 queries testable, and document that convention in LOD500.
3. **Reconciliation rules are sufficient but terse.** Winning-source rules cover the critical fields, including DTM precedence and outlier rejection. Ambiguity remains for multi-year documented price when only 2022 PRODUCT_SOLD is explicitly path-listed; builder should log which years were found and use source labels like `Tend_2022` consistently.
4. **Mutual-exclusion CHECK constraint is logically sound.** The `crop_unit_conversions` constraint correctly enforces exactly one of `conversion_group_id` or `crop_id` as non-null.
5. **CLI flags are sufficient.** `--all`, `--crops`, `--dry-run`, `--year`, and `--source-dir` cover idempotent seeding, scoped sample validation, and no-write parsing.

## §4 WP003-specific findings

1. **Tab visibility semantics conflict.** WP003 §3.2 says some tabs show only where data exists, while AC-04 says all 8 tabs render and tabs with no data show placeholders. Builder should follow AC-04 as the testable rule: render all core panes with placeholders, with equipment allowed hidden/greyed exactly as AC-04 states.
2. **Market-price behavior conflicts with earlier UI text.** §3.5 describes a live market-price delta, but §6 defers live price integration and says to render a placeholder when `pricebook_product_id` is set. Builder should follow §6 for S003 and avoid implementing unowned pricebook reads in WP003.
3. **ENTITY_REGISTRY origin is clear enough but not durable.** The spec says to copy it from the prototype and expand with new entities discovered during seed. Because the prototype lives in `/tmp`, the implemented registry must become repo-owned static JS and should not retain runtime dependence on `/tmp`.

## §5 Recommendation

**PASS_WITH_FINDINGS:** builder (sfa_build / team_10) may proceed on both WPs. Findings are non-blocking and should be handled during implementation and explicitly closed or acknowledged in LOD500:

- Resolve or record the LOD200 UUID vs LOD400 BigInteger schema refinement.
- Standardize `crop_variety_source_values.field_name` on English DB field names for WP002/WP003 interoperability.
- Treat WP003 AC-04 as authoritative for tab rendering and §6 as authoritative for deferred market-price behavior.
- Copy `ENTITY_REGISTRY` into repo-owned static assets and remove any runtime dependency on `/tmp`.
