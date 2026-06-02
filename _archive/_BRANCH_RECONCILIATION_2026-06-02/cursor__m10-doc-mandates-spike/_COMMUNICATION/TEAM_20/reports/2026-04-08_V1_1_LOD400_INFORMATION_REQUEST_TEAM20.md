# v1.1.0 LOD400 — Team 20 orientation and information completion request

**Date:** 2026-04-08  
**Team:** Team 20 (Infrastructure)  
**Document type:** Readiness review only — **no migrations or code changes** in this round  
**Inputs read:** `docs/GLOSSARY.md`, `SPEC-20260408-PHASE-A-LOD400`, `MANDATE-20260408-V1-1-LOD400-EXEC`, `HANDOFF-20260408-V1-1-ORCH-TEAM10`  
**Canonical protocols:** `_COMMUNICATION/ROADMAP.md`, `.cursor/rules/team-roles.mdc`, `.cursor/rules/project-context.mdc`

---

## 1. Team 20 role (refreshed)

Per **team-roles.mdc** and the orchestration handoff:

- **Owns:** Alembic migrations under `organic_market_agent/db/versions/`, SQLAlchemy models in `organic_market_agent/models/`, seed data delivered via migrations, `db.check` extensions when schema/seed invariants change, environment/skeleton concerns (M1-style).
- **Does not own:** Feature application code (collectors, parsers, normalizer stages beyond schema), routes, HTML, or running the full ingestion pipeline for production evidence (operator: Nimrod).
- **Reports to:** User (Nimrod); written artifacts under `_COMMUNICATION/TEAM_20/reports/` using `YYYY-MM-DD_{TOPIC}_TEAM20.md`.
- **Gate discipline:** No gate sign-off by Team 20; Team 50 validates against spec. Escalate blockers with `[USER ACTION REQUIRED]` when the user must act.

**Binding rule from HANDOFF §3 / §5.1:** Team 10 prepares migration *content* (SQL spec, triage); Team 20 creates the revision file, applies `alembic upgrade head`, and files confirmation. Team 10 must not apply migrations unilaterally.

---

## 2. Program goal and scope (Team 20 lens)

**End state:** Gate **G-V1.1** PASS after Team 50 runs `QA_MANDATE_G_V1_1.md` against evidence from Team 10’s completion package (and Team 190 preflight where applicable).

**LOD400 spec** (`SPEC-20260408-PHASE-A-LOD400`) is the **implementation-precision** layer on top of ARCH/CQ-MASTER policy. **MANDATE-20260408-V1-1-LOD400-EXEC** orders phases; **HANDOFF** defines coordination and artifacts.

**Phases (abbreviated):**

| Phase | Team 20 involvement |
|-------|---------------------|
| **Pre-work** | None (CHANGELOG discipline is Team 10). |
| **A1** | **Only if** cherry/basket SQL audits show drift: new migration (spec names `072_cq_p08_p09_drift_fix.py`; if used, A2 batch shifts to **073**). |
| **A2** | **Primary Team 20 workload for v1.1 catalog:** migration **`072_cq_p01_alias_batch.py`** (or `073` if A1 consumed 072) from Team 10’s filed migration request — aliases + `catalog_scope_skip_rules` per triage. |
| **A3** | Optional migration `07X_cq_m10x_source_fixes.py` only if schema/seed changes are required (often none). |
| **A4** | No DB work unless Team 100/10 mandates a `SRC_WA` (or equivalent) source row; spec A4.3 example SQL must be validated against **actual** `raw_extracted_items` columns before any migration. |
| **B–E** | No Team 20 code path except any late migration explicitly called out; operator runs pipelines. |

---

## 3. Repository baseline relevant to numbering

As of this review, the latest Alembic file in tree is **`071_alias_baby_mix_sprouts_blend.py`** with `revision = "071"`, `down_revision = "070"`. That **aligns** with the LOD400 A2 template’s `down_revision = '071'`.

**Next revision:** `072` for first v1.1 deliverable unless A1 drift fix consumes `072`, in which case alias batch becomes `073` — exactly as spec §A2.1 states.

---

## 4. Information completion requests (for Team 100 / Team 10)

These items block **correct** migration authoring without guesswork. Team 20 requests explicit resolution before implementing A2 (and before copying spec templates verbatim).

### 4.1 LOD400 §A2.3 template SQL vs live schema (CRITICAL)

The spec’s `catalog_scope_skip_rules` INSERT uses columns **`rule_pattern`** and omits required fields. The live model and migrations use:

- **`pattern`** (not `rule_pattern`)
- **`display_order`** — **NOT NULL**, **globally unique** (`uq_catalog_scope_skip_rules_display_order`)
- **`category_code`** — NOT NULL, constrained to `donation|cleaning|dry_grocery|grocery|other`
- **`match_type`**, **`notes`**, **`is_active`**, **`created_at`**, **`updated_at`**

**Request:** Team 100 issues a short **errata** to §A2.3 (or Team 10 attaches a corrected template to the migration request) with a working INSERT shape and a rule for allocating **`display_order`** (e.g. next free integer band for CQ-P01).

The template’s **`ON CONFLICT DO NOTHING`** has no matching unique constraint on arbitrary columns; Team 20 will use **idempotent patterns** agreed with Team 10 (e.g. deterministic `display_order` + `ON CONFLICT (display_order)` or delete-then-insert in downgrade policy).

### 4.2 LOD400 §A2.3 `product_aliases` INSERT

Template uses **`confidence_score`**; the database column is **`confidence`**. Template includes **`updated_at`**; table **`product_aliases`** has **`created_at` only** (no `updated_at` per `001_initial_schema`).

**Request:** Publish a corrected INSERT template in the migration request or spec errata.

### 4.3 Mandate Task 2 vs spec §B1 — CLI commands

**MANDATE-20260408-V1-1-LOD400-EXEC** Task 2 lists:

- `run_ingestion --run-type manual --all-sources`
- separate `run_normalizer`, `run_aggregator`, `run_publisher`

**LOD400 spec §B1** and **HANDOFF** reference:

- `scheduler.run_ingestion --run-type manual --normalize` (and variants)

**Request:** Single **operator canonical command block** for Phase B (and E) endorsed by Team 100 so completion reports and Nimrod’s runbook do not contradict.

### 4.4 MANDATE Task 3 C3 vs LOD400 §D1 — Pantry ADR owner

**Mandate** Task 3 says Team 10 creates the Pantry ADR (C3). **LOD400 §D1** assigns ADR authorship to **Team 100** at a fixed path.

**Request:** Confirm binding owner and path so Team 20 is not pulled into duplicate or conflicting documents.

### 4.5 MANDATE `resolve_basket_tier` signature vs LOD400 §C4

**Mandate** §Task 3 specifies `csa_context_json: dict | None` and `price_amount: float | None`. **LOD400 §C4.2** shows **string JSON**, **`Decimal`** for price, and a richer return tuple `(product_code, note)`.

**Request:** Team 100 declares **one** binding public API; Team 20 does not implement resolver code but needs a stable contract reference if models or DB logging depend on it later.

### 4.6 Spec A4.3 — `psql` example and `SRC_WA`

The example `INSERT INTO raw_extracted_items` uses columns such as **`raw_name`**, **`raw_price`**, **`source_code`** on `sources`. These **do not match** typical `raw_extracted_items` / `sources` naming in this codebase (e.g. `raw_product_name`, `sources.code`, price fields as per current schema).

**Request:** Either (a) Team 100 corrects the verbatim example to match production schema, or (b) Team 10 files a migration + protocol errata for WhatsApp intake **before** Team 20 is asked to seed `SRC_WA`.

### 4.7 Team 10 migration request artifact (HANDOFF H1)

Before Team 20 creates `072`:

**Expected file:** `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_072_REQUEST_TEAM10.md` (or equivalent) containing:

- Full SQL or row-by-row spec for aliases and scope-skip rules
- Any A1 drift fix SQL if applicable
- Statement that Team 10 has **not** run `alembic upgrade head` for this revision

**Request:** Confirm this handoff is the **only** intake channel for CQ-P01 batch work.

---

## 5. What Team 20 will do after information is complete

1. Create the numbered migration(s) from Team 10’s request, with `down_revision` chained from current head (`071` → `072` / `073`).
2. Run `alembic upgrade head` on the validation database, extend `db.check` **only if** new invariants are mandated.
3. File `_COMMUNICATION/TEAM_20/reports/YYYY-MM-DD_V1_1_MIGRATION_0XX_COMPLETE_TEAM20.md` with `alembic current` and any notes.
4. Refuse to copy-paste uncorrected §A2.3 template SQL into production migrations without the errata above.

---

## 6. Acknowledgement

This round: **review and information request only** — no Alembic revision files were added or modified for v1.1.0 in this session.

---

*Team 20 (Infrastructure)*
