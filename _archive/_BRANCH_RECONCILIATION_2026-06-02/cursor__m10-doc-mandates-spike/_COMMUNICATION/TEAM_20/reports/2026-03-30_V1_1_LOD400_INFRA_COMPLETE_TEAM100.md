# v1.1.0 LOD400 infrastructure — completion report (Team 20 → Team 100)

**Date:** 2026-03-30  
**Task:** Team 20 plan — v1.1.0 Infrastructure (LOD400 + ARCH binding)  
**Mandate / decisions:** ARCH-20260408-TEAM20-RESPONSE-V1-1; LOD400 Phase A (`SPEC-20260408-PHASE-A-LOD400` via `2026-04-08_PHASE_A_LOD400_SPEC_TEAM100.md`); briefing `2026-04-08_TEAM20_BRIEFING_V1_1_INFRA_READINESS_TEAM100.md`

## H1 intake used

| Item | Document / basis |
|------|------------------|
| **072 (CQ-P01)** | No row-level A2 triage H1 in-repo. **072** implements ARCH §3.1–3.2 **templates** with **empty** data lists; follow-up when Team 10 files tuples + `display_order` band. |
| **073 (SRC_WA + CHECK)** | ARCH §3.6–3.7 (SRC_WA **APPROVED** §3.7). Fetch/normalizer stubs from `2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md` **content**, applied in **073** after ARCH renumbering. |
| **H1 / ARCH reconciliation** | `_COMMUNICATION/TEAM_20/reports/2026-04-09_V1_1_ARCH_H1_RECONCILE_TEAM20.md` |

### Supersession of 2026-03-30 Team 10 request

`2026-03-30_V1_1_MIGRATION_072_REQUEST_TEAM10.md` assigned **072 = SRC_WA only**. **Team 100 §3.7** requires **072 = CQ-P01**, **073 = SRC_WA + `pending_manual`**. Implementation follows **ARCH** numbering; SRC_WA SQL from that request is **moved to 073** with **ARCH** canonical `sources` row (`WhatsApp Community Submissions`, `priority` 3).

## Alembic chain

| Revision | File | Summary |
|----------|------|---------|
| **072** | `organic_market_agent/db/versions/072_cq_p01_alias_batch.py` | `catalog_scope_skip_rules` + `product_aliases` per ARCH templates (empty batches). `down_revision` = `071`. `downgrade()` = `pass`. |
| **073** | `organic_market_agent/db/versions/073_src_wa_pending_manual.py` | Replace `chk_rei_extraction_status` to allow `pending_manual`; seed `SRC_WA`; `source_fetch_profiles` + `normalizer_profiles` (idempotent `NOT EXISTS`). |
| **074** | — | **Not authored** — no separate A1 drift H1. |

`alembic heads` (offline): **`073 (head)`**.

### Dev database — Docker (canonical)

- **Fixed host port:** `5433` → container `5432` (`docker-compose.yml`).  
- **Scripts:** `scripts/docker_postgres.sh` — `start | stop | down | restart | status | wait`.  
- **`.env.example`:** default `DATABASE_URL` is the Docker URL (`oma` / `oma` / `organic_market_agent`).

### Verification bundle + evidence for Team 100

Run on a machine where Postgres is up and `.env` points at it (or rely on the default Docker URL):

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents
./scripts/docker_postgres.sh start
./scripts/verify_dev_db_team100.sh
```

The script runs `alembic upgrade head`, `alembic current`, `pytest` (minus uPress/FTPS), `db.check`, and SQL smoke for `SRC_WA` + `chk_rei_extraction_status`. It writes a timestamped log under `artifacts/` (filename printed at top of output). Attach that log to QA / Team 100.

**Note:** A **completely empty** database may still fail mid-chain on older revisions (e.g. assumptions about seeded `sources.id` values). Normal dev DBs that are already at **071+** are the intended target for validating **072/073**.

## ORM

- `organic_market_agent/models/runs.py` — `RawExtractedItem`: `chk_rei_extraction_status` includes **`pending_manual`**.

## Tests / health check

- **New:** `tests/test_extraction_status_pending_manual.py` — asserts constraint text contains `pending_manual` and `sources.code = 'SRC_WA'`; **skips** if PostgreSQL unavailable (same pattern as other DB integration tests).
- **`db.check`:** `REQUIRED_COUNTS["sources"]` updated from **20 → 21** (`organic_market_agent/db/check.py`) after **073** seeds `SRC_WA`.

## Blockers

- None for **code delivery**. Run `./scripts/verify_dev_db_team100.sh` after `./scripts/docker_postgres.sh start` and attach the generated log as verification evidence.

---

*Team 20 (Infrastructure)*
