# H1 — Migration 072 CQ-P01 data population (Team 10 → Infrastructure)

**Date:** 2026-04-08  
**Handoff:** H1 per `HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` §5.1  
**Code:** `organic_market_agent/db/versions/072_cq_p01_alias_batch.py`

## Context

Revision **072** is already merged with **empty** `SCOPE_SKIP_RULES`, `GLOBAL_ALIASES`, and `SCOPED_ALIASES` lists (Team 20 infra report). Team 10 has **not** run `alembic upgrade head`.

## Current triage status

`_COMMUNICATION/TEAM_10/reports/2026-04-08_CQ-P01_TRIAGE_TABLE_TEAM10.md` — **incomplete**: live `/unresolved/export.json` blocked until operator DB is available. No safe batch of tuples is submitted in this wave.

## Request

1. **No code change required** until triage produces tuples.
2. When Team 10 files a **follow-up** H1 with populated Python lists (or raw SQL), please either:
   - extend **072** before first production apply (if 072 not yet applied anywhere), **or**
   - author **074+** with the same insert helpers pattern as 072.

## SQL spec alignment

Use only templates from `SPEC-20260408-PHASE-A-LOD400` §A2.3 / ERR-01 / ERR-02 (`pattern`, `display_order`, `category_code`, `confidence`, no `updated_at` on aliases).

## Wait condition

Team 10 will not claim A2 **exit criteria** (distinct unresolvable ≤ 20, etc.) until batch applied + `catalog_renormalize` run + metrics captured.
