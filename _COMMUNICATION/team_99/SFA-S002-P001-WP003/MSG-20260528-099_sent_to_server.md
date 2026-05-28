---
id: MSG-20260528-099
from: team_99 (mac)
to: server
date: 2026-05-28
type: task
priority: high
expects_response: true
wp: SFA-S002-P001-WP003
---

## Subject
WP003 publish gap — re-upload fresh market artifact (DNS recovered) + add upload resilience

## Body
ROOT CAUSE (diagnosed from /data/backups/sfa-scheduler.log): the 06:00 cron on
2026-05-28 hit a transient DNS/NAT64 failure (`Temporary failure in name
resolution`). PublishEngine wrote 33 products to output/public
(version=20260528_065729) but the WP-REST upload to
www.nimrod.bio/wp-json/sfagent/v1/upload failed all 3 retries. Result: the
PUBLIC manifest is stale (product_count=1, report_date=2099-08-12,
artifact_version=20260417). DNS has since RECOVERED (www.nimrod.bio resolves;
endpoint reachable).

ACTIONS (server-side):
1. Re-publish the existing fresh artifact:
   cd /data/projects/smallfarmsagents && .venv/bin/python -m organic_market_agent run_publisher --upload
2. Verify public manifest.json → product_count≈33, report_date=2026-05-24,
   artifact_version=20260528_065729, staleness ∈ {fresh, acceptable}.
3. Investigate https://www.nimrod.bio/SmallFarmsAgent returning 404 (page
   moved/renamed? S003 UI is now sfa.nimrod.bio). Confirm intended public URL.
4. Add an upload-freshness guard: if public artifact_version < on-host
   artifact_version, auto-retry the upload (so a transient DNS blip can't strand
   the public site for a full day).
5. Report back: WP003 Pass-3 self-attestation (AC-04/AC-05) so team_100 can
   reconcile the roadmap status to closed.

Full diagnosis: _COMMUNICATION/team_99/SFA-S002-P001-WP003/ROOT_CAUSE_REMEDIATION_v1.0.0.md
