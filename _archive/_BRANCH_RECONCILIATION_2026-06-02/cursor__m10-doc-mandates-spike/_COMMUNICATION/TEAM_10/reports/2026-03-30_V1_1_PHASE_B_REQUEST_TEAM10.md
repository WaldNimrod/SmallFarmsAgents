# Phase B request — full pipeline (Nimrod operator)

**Date:** 2026-03-30  
**From:** Team 10  
**Handoff:** H2 per `HANDOFF_V1_1_ORCHESTRATION_TEAM10.md` §5.2  
**Status:** `[USER ACTION REQUIRED]`

## Preconditions (not all met at filing time)

- [ ] Team 20 confirms `alembic current` = head including migration **072** (SRC_WA).
- [ ] Docker Postgres (`oma-g2-ev` or project-standard compose service) is running.
- [ ] `DATABASE_URL` and source credentials available on operator workstation.

## Commands (canonical CLI)

```bash
alembic current
python -m organic_market_agent run_ingestion --run-type manual --normalize
python -m organic_market_agent run_normalizer
python -m organic_market_agent run_aggregator
python -m organic_market_agent run_publisher
```

## Post-run verification (Team 10 / Nimrod)

- PRD027 appears **at most once** in `output/public/public_report.json` (`product_id` field).
- Published product count **≥ 77**.
- Log source failures (non-blocking per spec) in the completion report.

## Reply artifact

Please reply by appending results to `_COMMUNICATION/TEAM_10/reports/2026-03-30_V1_1_COMPLETION_TEAM10.md` §3 evidence or a dated operator addendum.
