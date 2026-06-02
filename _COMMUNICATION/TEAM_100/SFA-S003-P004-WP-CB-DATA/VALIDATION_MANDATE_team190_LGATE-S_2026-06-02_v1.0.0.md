# VALIDATION MANDATE + PROMPT — SFA-S003-P004-WP-CB-DATA (L-GATE_S) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_190 (Independent Validator)
**Routed by:** team_00
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/sfa-p004-cbdata-classb-2026-06-02` (off `main` be0e04f)
**Gate:** **L-GATE_S** (spec review) of WP-CB-DATA — Crop Book Enrichment Mirror. **Pre-build** — review the LOD400 for soundness, precision, and constitutional compliance. No live-DB execution (nothing built yet).

---

## 0. Cross-engine constraint (IR#1/#5 — MANDATORY)
LOD400 author + future builder = Claude (team_100 Opus / team_10 Sonnet). Therefore this L-GATE_S **MUST run on a NON-CLAUDE engine** (Cursor Composer / GPT-5.x / Codex). Confirm engine in the verdict header.

## 1. Context
team_00 authorized WP-CB-DATA in-session (this session) at **full scope**: mirror **both**
`crop_field_enrichment` and `crop_attribute` from the canonical Mac Postgres to the uPress **MySQL**
delivery tier, so the live `/calc` book-chip bind and crop-page structured provenance / COMPLETE-PARTIAL
state read from **tables** instead of degrading. This closes the WP-CB-UI-ALIGN L-GATE_V R3 non-blocking
follow-up. The enrichment-computation layer (reconciler / `enrichment_runner` / `field_policy.py` / crop_book
models / migrations 035–060) is **LOCKED** — this WP is **mirror + transport only**.

## 2. Artifacts to review
- **LOD400 (this gate's subject):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-DATA/LOD400_spec.md` (v0.1.0)
- **Canon (LOCKED, context):** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (v1.3.0)
- **Field interface contract:** `_archive/SFA-S003-P004-WP-CB-1/TEAM_100/FIELD_INTERFACE_MAP_v1.0.0.md`
- **Live consumers (already shipped, degrade-gracefully):**
  `sfa_delivery/app/Controllers/HubController.php` L142–164; `sfa_delivery/app/Controllers/CropBookViewController.php` L473–508.
- **Source models (LOCKED):** `organic_market_agent/crop_book/enrichment_models.py`, `attribute_models.py`,
  `canon/field_registry.py`, `canon/units.py`; publisher `organic_market_agent/publisher/sfa_ingest_push.py`
  (L324–381 whitelists + τ constants; L732 `--table` choices); endpoint `sfa_delivery/app/Controllers/IngestController.php`
  (L28–45 `TABLE_COLUMNS`); runner `sfa_delivery/migrations/migrate.php`.

## 3. Spec-review checklist — run each independently

### 3.1 Constitutional (all must PASS)
- **C1 — Mirror + transport only.** The LOD touches **no** locked enrichment-computation file (reconciler,
  `enrichment_runner`, `field_policy.py`, crop_book ORM models, alembic migrations 035–060) and **no** locked LOD.
  Confirm the WI/AC set is confined to `sfa_delivery/` + `organic_market_agent/publisher/sfa_ingest_push.py` + new tests.
- **C2 — IR#4.** AC-12 mandates the builder makes zero `_aos/roadmap.yaml` and zero `_aos/` edits. Confirm the AC exists.
- **C3 — No UI threshold math.** field_state is **backend-stamped** at ingest using the **existing**
  `_FIELD_STATE_TAU=0.40` / `_HIGH_TRUST_CLASSES={EX,NI}` constants (AC-06). The spec must NOT introduce a new
  threshold or push tau to the UI (this was the WP-CB-1 L-GATE_V blocker — verify the spec respects it).
- **C4 — Layer fidelity.** Crop-level mirror keys on `crop_id` (matching both consumer queries). T1 numerics →
  `crop_field_enrichment`; T2/T3 categoricals → `crop_attribute` (`attribute_name`→`attribute_key`, `value_list`
  jsonb preserved). No concept duplicated across the two mirror tables.
- **C5 — Additive migrations.** MySQL migrations `004`/`005` are `CREATE TABLE IF NOT EXISTS` only, FK to `crops`
  with `ON DELETE CASCADE`, composite PK as the upsert key; no alteration of `001`–`003`. `migrate.php` auto-globs
  (no runner edit needed). Confirm.

### 3.2 Precision / executability (junior-dev gate)
- **P1 — Consumer-contract fidelity.** The WI-1/WI-2 column sets EXACTLY satisfy the live SELECTs:
  `/calc` reads `value_best` keyed by `(crop_id, field_name)`; the crop page reads
  `field_name, value_best, unit, field_state, winning_source_class, confidence_score` and
  `attribute_key, value_canonical, value_list`. Verify every column a consumer reads is present in the migration.
- **P2 — Default-variety aggregation is unambiguous.** Decision §2.1: pick `crop_varieties.is_default = TRUE`,
  fallback `MIN(id)`; exactly one row per `(crop_id, field_name)` / `(crop_id, attribute_key)`. Confirm AC-04
  pins this (incl. the no-default fallback) and that it matches the SSoT default-variety rule the existing `dtm`
  join uses (`sfa_ingest_push.py` L101 region).
- **P3 — Unit source is pinned.** Decision §2.2 + AC-05: `unit` comes from `FIELD_REGISTRY[field_name].unit`
  (None→NULL), since Postgres enrichment has no `unit` column. Confirm the spec names the registry, not a literal map.
- **P4 — Whitelist alignment.** The fetchers read `field_name IN _AGRONOMY_FIELD_WHITELIST` and
  `attribute_name IN _CATEGORICAL_ATTRS_WHITELIST` (the existing publisher constants). Confirm the `/calc`
  IN-clause (which lists BOTH canonical and legacy alias names) is satisfied by the canonical names the whitelist
  carries post-MIG (e.g. `spacing_in_row_cm`, `yield_per_bed_m`, `price_documented`, `seeds_per_g`,
  `nutrient_removal_n_kg_per_ha`) — so book-chips will actually bind.
- **P5 — Idempotency + upsert key.** AC-08 + the composite PK guarantee the generic
  `INSERT … ON DUPLICATE KEY UPDATE` upsert is stable (no row duplication across re-pushes). Confirm.
- **P6 — Tests are specified.** WI-5 names publisher pytest (default-variety incl. fallback, unit attach,
  field_state truth table, value_list→JSON, name mapping) + a delivery PHPUnit upsert/idempotency test. Confirm
  AC coverage maps to each.

### 3.3 Scope discipline
- **S1** — Out-of-scope (§6) correctly excludes: enrichment-computation change; variety-level MySQL mirror;
  any server-side feature (→ `WP-SRV-IDEAS`). The F-UI-01 payload fallback is left in place (not removed).
- **S2** — The 12-AC matrix is sufficient to attest the mirror end-to-end (migration → endpoint → fetcher →
  push → live `/calc` + crop-page bind) without gaps. AC-09/AC-10 are correctly marked post-deploy/live.
- **S3** — `crop_attribute` `field_state` is additive (not consumer-required at L492) and does not change the
  current explicit-column read.

## 4. Verdict format → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-S_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-DATA
gate: L-GATE_S
validator_engine: <non-Claude>
result: PASS | PASS_WITH_FINDINGS | BLOCKED
constitutional_checks: <n/5>
precision_checks: <n/6>
scope_checks: <n/3>
findings:
  - id: F-190-CBDATA-S-NN
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: ...
    disposition: <fix-inline | builder-acknowledge | R2>
authorize_build: true | false
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS (build-authorized)** → team_100 addresses any MAJOR/MINOR inline, then dispatches team_10 L-GATE_B build.
- **BLOCKED** → team_100 revises LOD400 and routes R2.

Notify via `_COMMUNICATION/team_100/` (MSG, ADR043 naming).

---

## 5. Cursor prompt (paste into the non-Claude validator)

> You are **team_190**, an independent validator running on a **non-Claude** engine (Cursor Composer / GPT-5 /
> Codex). Confirm your engine in the verdict header (IR#1/#5: the spec author and the future builder are Claude,
> so you must not be). Repo: `/Users/nimrod/Documents/SmallFarmsAgents`, branch
> `claude/sfa-p004-cbdata-classb-2026-06-02`. Gate: **L-GATE_S** (pre-build spec review) of **WP-CB-DATA**.
>
> Read `_aos/work_packages/S003/SFA-S003-P004-WP-CB-DATA/LOD400_spec.md` (v0.1.0). Cross-check every claim
> against the real code: the two live consumer queries (`sfa_delivery/app/Controllers/HubController.php` L142–164;
> `CropBookViewController.php` L473–508), the publisher whitelists + τ constants (`sfa_ingest_push.py` L324–381,
> L732), the endpoint allowlist (`IngestController.php` L28–45), the migration runner (`migrations/migrate.php`),
> and the source models (`enrichment_models.py`, `attribute_models.py`, `canon/field_registry.py`).
>
> Run the checklist in §3 above (constitutional C1–C5, precision P1–P6, scope S1–S3). The central question: **do
> the specified mirror tables + fetchers EXACTLY satisfy the columns/keys the already-shipped consumers read, so
> the live `/calc` book-chips and crop-page structured reads will bind?** Flag any column a consumer reads that
> the migration omits; any aggregation ambiguity; any locked-file touch; any reintroduced UI threshold math.
>
> Emit the verdict YAML (§4) to `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-DATA/WP-CB-DATA_LGATE-S_VERDICT_v1.0.0.md`
> and set `authorize_build` true/false. This is spec review only — do not build, migrate, or push data.
