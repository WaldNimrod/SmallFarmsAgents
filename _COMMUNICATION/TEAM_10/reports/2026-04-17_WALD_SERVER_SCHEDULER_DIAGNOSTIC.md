# Waldhomeserver — SFA scheduler diagnostic (2026-04-17)

**Host:** `nimrodw@10.100.102.2` (waldhomeserver)  
**Project:** `/data/projects/smallfarmsagents`  
**Evidence time (UTC):** 2026-04-17 ~00:54

## Summary

1. **The daily pipeline has been running** on schedule **2026-04-12 through 2026-04-16** (inclusive). Logs and DB `ingestion_runs` agree: daily cron at **06:00 UTC**, finish ~06:06 UTC, `PublishEngine` success lines present (e.g. `version=20260416_060611`).
2. **No 2026-04-17 06:00 run yet** at evidence time — server clock was **2026-04-17 00:54 UTC**, i.e. **before** the next cron slot. Expect the next automatic run at **06:00 UTC** on 2026-04-17 unless cron or host state changes.
3. **Automatic upload to nimrod.bio is OFF:** `scheduler_config.upload_enabled = False`. The scheduler **writes** `output/public/*` on the server but does **not** run FTPS upload. **FTPS credentials are present** in server `.env` (`UPRESS_SFTP_HOST` / `UPRESS_SFTP_USER` set). To push artifacts to WordPress automatically after each run, set `upload_enabled = true` (via admin `/scheduler` or SQL) after Team 00 approval.
4. **Runs are `partial`:** source **SRC017** (`pricez.co.il`) consistently returns **HTTP 403** (blocked / bot protection). Other sources continue; pipeline completes with partial status.
5. **Local manifest on server** (`output/public/manifest.json`) shows **`last_published_at` 2026-04-16T06:06:11Z**, **34 products**, **4 community sources** — consistent with a healthy rolling window for that date.

## Commands used (repeatable)

```bash
ssh nimrodw@10.100.102.2 'tail -200 /data/backups/sfa-scheduler.log'
ssh nimrodw@10.100.102.2 'sudo grep CRON /var/log/syslog | grep smallfarmsagents | tail -5'
# SQL via project venv: scheduler_config, ingestion_runs
```

## Related

- Inbox / Team 61: [`documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](../../../documentation/05-admin-and-operations/WALD_HOME_SERVER_AGENT_COMMUNICATION.md)
- Scheduler upload flag: `organic_market_agent/scheduler/runner.py`, `scheduler_config.upload_enabled`
