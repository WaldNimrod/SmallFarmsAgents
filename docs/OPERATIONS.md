# Operations — OrganicMarketAgent

## Development workstations (read first)

**Do not install the cron line below on a developer laptop used for coding.** Scheduled ingestion is **disabled by policy** on dev machines; runs are **manual / on-demand only**. See [`documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md`](../documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md).

---

## Scheduled pipeline (cron)

The admin scheduler stores UTC hour/minute in `scheduler_config`. The host runs the runner **every minute**; the runner exits unless the current time matches the configured slot (±1 minute).

### Install cron (macOS / Linux)

```bash
crontab -e
```

Add line (adjust paths to your checkout and virtualenv):

```bash
* * * * * cd /Users/nimrod/Documents/SmallFarmsAgents && /path/to/.venv/bin/python -m organic_market_agent.scheduler.runner >> logs/runner.log 2>&1
```

Create a `logs/` directory in the project root if it does not exist.

### Verify

```bash
crontab -l | grep runner
```

Team 20 installs the cron line on the host after Team 10 delivers `organic_market_agent/scheduler/runner.py`.
