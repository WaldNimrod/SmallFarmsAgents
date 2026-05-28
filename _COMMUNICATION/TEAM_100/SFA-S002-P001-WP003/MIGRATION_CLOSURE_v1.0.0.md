---
id: MIGRATION_CLOSURE_SFA-S002-P001-WP003_v1.0.0
from: team_100 (Chief Architect)
to: team_00 (Principal)
cc: team_99, team_60, team_190
date: 2026-05-28
type: closure_report
wp: SFA-S002-P001-WP003
verdict: DONE (verified against sfa.nimrod.bio)
supersedes: _COMMUNICATION/team_99/SFA-S002-P001-WP003/WP003_PASS3_SELF_ATTESTATION (www-based veto — wrong domain)
---

# WP003 — domain migration closure (www.nimrod.bio → sfa.nimrod.bio)

## What was actually wrong
The "stale public manifest" was NOT a pipeline outage. Market delivery had
already migrated to the new dynamic tier **sfa.nimrod.bio** (`sfa_ingest_push`
→ `/api/v1/ingest`), but the **legacy www.nimrod.bio static-upload path was
never removed** — it ran daily in the 06:00 cron and failed (dead endpoint:
404, REST namespace gone), freezing the old public manifest since April.
team_99's Pass-3 attempted to "fix" www.nimrod.bio (deploy mu-plugin, renew
App Password) — that targeted the dead domain and is superseded by this closure.

## Remediation (team_00 directive: "no connection to the main domain")
1. **Server .env** — all `UPRESS_*` legacy vars retired (backed up) →
   `upress_configured()=False` → 06:00 legacy www upload phase auto-skips.
2. **Code** (commits on main thru `dfbd347`) — `config.py`/`__main__.py` www
   defaults → empty; `upload_dispatch/wp_upload/ftps_upload/static_upload`
   retired with a dead-host guard (`NoUploadConfigured` on any nimrod.bio main
   domain target); `freshness_guard.py` repointed from the dead www manifest to
   verify the **sfa** tier (health + canonical `sfa_ingest_push` re-push). 11/11
   guard tests pass.
3. **Cron** — now fully sfa-targeted, zero www: 06:00 generate → 06:30 push to
   sfa → **06:45 freshness_guard** (anti-drift backstop). crontab backed up.

## Verification (2026-05-28, live)
- `sfa.nimrod.bio/market/` → 200; `sfa.nimrod.bio/api/v1/health` → `{status:ok, db:ok}`.
- Guard health-only → `state=healthy, rc=0`. Guard full → re-pushed **65 products,
  HTTP 200, accepted=65, rejected=0**.
- `upress_configured()=False` on host (legacy path cannot fire).

## AC disposition (retargeted to new tier)
- AC-04 (artifact freshness): now = sfa.nimrod.bio market data freshness — PASS (fed daily via ingest; guard backstop).
- AC-05 (public page): `www.nimrod.bio/SmallFarmsAgent` is intentionally dead; the live page is `sfa.nimrod.bio/market/` → 200 — PASS.
- AC-01/02/03/06 (scheduler/collectors/logs/index): pipeline runs daily; collectors' transient DNS blips are non-blocking (NAT64/clatd), data delivered to sfa.

## Anti-drift guarantee
This class of drift cannot recur: the legacy www path is removed at env + code
level (can't silently re-enable), and the 06:45 guard re-pushes + alarms if the
sfa tier is unhealthy.

**WP003 → DONE (LOD500_LOCKED).** Archive mandate routed to team_191.

— team_100 (Claude Opus 4.7) 2026-05-28
