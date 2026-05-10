# MANDATE — SFA-S002-P001-WP002 DB Seed + Alembic Verify — team_100 → team_99

**Date:** 2026-05-07
**From:** team_100
**To:** team_99 (waldhomeserver operations)
**WP:** SFA-S002-P001-WP002 (post-close, production activation)
**Type:** OPS_MANDATE
**Trigger:** Execute when Hub DB comes online (ADR034 R8 lifted)

---

## Task

When `db_connectivity_status.json` shows `status: online`:

1. On waldhomeserver, in the SmallFarmsAgents repo on `offline/2026-05-07-smallfarmsagents-release-prep`:
   ```bash
   git pull
   alembic upgrade head
   python3 scripts/seed_mypips_sources.py
   ```

2. Verify migrations applied:
   - `034_add_display_bucket_to_sources` present in `alembic_version`
   - `sources` table has `display_bucket` column
   - 4 MyPIPS sources registered (mashtelatharoe, anatiyot, fruit4soul, finerotem)

3. Run pipeline smoke:
   ```bash
   python3 -m organic_market_agent run_publisher --dry-run
   ```
   Verify `source_types[]` appears in JSON output.

4. Report back to `_COMMUNICATION/team_99/` with result.

---

## Authority

- MAY run alembic + seed on server
- MAY NOT modify application code
- MAY NOT push to main

*Mandate issued 2026-05-07 by team_100. Activate on DB-online trigger.*
