# Development workstation — scheduler policy

**Version:** 1.0  
**Date:** 2026-04-10  
**Status:** Canonical  
**Owner:** Team 100 (Architecture)

## Policy

**OrganicMarketAgent development workstations must not execute automated daily (or periodic) ingestion scans.** Pipeline runs on a dev machine are **manual / on-demand only** (admin UI trigger, explicit CLI, or tests).

## Rationale

- Avoid duplicate load on source websites from developer machines.
- Prevent accidental writes to a shared or production-like database from unreviewed schedules.
- Keep the **home server (waldhomeserver)** as the primary host for scheduled community ingestion unless Team 100 defines otherwise.

## Required practices

| Practice | Detail |
|----------|--------|
| **No cron** | Do **not** install the `crontab` line from `docs/OPERATIONS.md` on a personal development Mac/Linux workstation used for SFA coding. |
| **No LaunchAgents / Task Scheduler** | Do not register the scheduler runner to start on an interval on dev hosts. |
| **Database `scheduler_config`** | When a developer uses a **local PostgreSQL** with a migrated schema, keep **`is_enabled = false`** in `scheduler_config` unless you are deliberately testing the scheduler itself (then disable again after the test). |
| **How to run ingestion** | Use the Flask admin **`/runs`** “trigger” flow (authenticated), maintenance commands from `project-context.mdc`, or `python -m organic_market_agent.scheduler.run_ingestion` **explicitly** for debugging — not on a timer. |

## Production / staging exception

Scheduled runs belong on **approved hosts** only (e.g. **waldhomeserver** with Team 61 operations). That environment follows `docs/OPERATIONS.md` and server runbooks.

## Related

- Cron install (approved hosts): [`docs/OPERATIONS.md`](../../docs/OPERATIONS.md)
- Home server handoff: [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](WALD_HOME_SERVER_AGENT_COMMUNICATION.md)
