---
id: ROOT_CAUSE_REMEDIATION_SFA-S002-P001-WP003_v1.0.0
from: team_99 (OPS / server)
to: team_00 (Principal), team_60
cc: team_100, team_190
date: 2026-05-28
type: root_cause_remediation
wp: SFA-S002-P001-WP003
severity: HIGH (public data stale ~21 days)
status: DIAGNOSED — remediation ready (server-side, DNS recovered)
---

# WP003 regression — root cause + remediation

## Symptom (team_100 live re-attestation 2026-05-28)
Public market manifest `https://www.nimrod.bio/wp-content/uploads/market/manifest.json`
serves the pre-WP007 stale snapshot: `product_count=1`, `report_date=2099-08-12`,
`artifact_version=20260417_004822`. `/SmallFarmsAgent` returns 404.

## Root cause (confirmed on host 100.125.98.56)
**Transient DNS / NAT64 resolution failure during the 06:00 daily cron.**
`/data/backups/sfa-scheduler.log` (2026-05-28 06:50–06:58):
- Collectors SRC003 (EasyFarm) + SRC006 failed: `[Errno -3] Temporary failure in name resolution`.
- PublishEngine still wrote **33 products** to `output/public` (`version=20260528_065729`).
- **Upload failed all 3 retries**: `static_upload ... www.nimrod.bio:443 /wp-json/sfagent/v1/upload` → `NameResolutionError`. `run_pipeline: upload unexpected error`.

So the on-host artifact is **fresh** (`output/public/manifest.json` = 20260528,
product_count=33, report_date=2026-05-24, community_sources=4) — it was simply
never uploaded. This is an F-01-class publish-gap, triggered by the F-02-class
DNS/clatd instability (cf. roadmap WP003 "clatd fix" 2026-05-03).

## Current state (probed 2026-05-28, post-incident)
- `getent hosts www.nimrod.bio` → resolves (Cloudflare IPv6). `easyfarm.co.il` → resolves.
- `clatd` active; upload endpoint reachable (HTTP 404 on GET = POST-only, alive).
- **DNS has recovered.** A re-publish will now succeed.

## Remediation (server-side, team_99)
1. Re-run the publish+upload of the existing fresh artifact:
   `cd /data/projects/smallfarmsagents && .venv/bin/python -m organic_market_agent run_publisher --upload`
   (or the scheduler's upload-only path).
2. Re-verify: public `manifest.json` → product_count≈33, report_date=2026-05-24,
   artifact_version=20260528_065729, staleness∈{fresh,acceptable}.
3. Investigate `/SmallFarmsAgent` 404 (likely the S002 market page moved/renamed;
   the S003 crop-book UI is now at `sfa.nimrod.bio`). Confirm intended public URL.
4. **Resilience (prevent recurrence):** add a publish-retry/backstop so a transient
   DNS blip doesn't leave the public site stale a full day — e.g. a post-cron
   "upload freshness guard" that re-attempts upload if public artifact_version <
   on-host artifact_version, or a longer/again-scheduled retry window.
5. On success → team_99 self-attest WP003 Pass-3; team_100 reconciles roadmap status.

— team_99 (OPS) 2026-05-28
