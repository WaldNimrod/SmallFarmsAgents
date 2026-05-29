---
id: DEPLOY_ROUTING_DECISION_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief Architect)
to: team_00 (Principal)
cc: team_99, team_190
date: 2026-05-29
type: routing_decision
wp: SFA-S003-P002-WP-UI-patch02 (+ WP-UI-patch01 media)
status: BLOCKED — awaiting team_00 infra decision
---

# Deploy routing decision — sfa.nimrod.bio media

## State
WP-UI-patch02 Phase 1 is **LOD500_LOCKED** (build + cross-engine L-GATE_V PASS).
But the **live deploy never reached the wire** — team_99 reports a persistent,
multi-day uPress FTPS allowlist block across every available egress:

| Route | Result |
|-------|--------|
| Mac home Wi-Fi (IPv4 79.177.137.169) | timed out / not on allowlist |
| waldhomeserver (46.235.231.114) | blocked at network layer (outbound 21 + not allowlisted) |
| Yesterday's allowlisted IP (79.177.143.165) | ISP rotated — no longer egress |

Consequence: the 3 brand-media URLs (crop-book.webp, og-default.webp, favicon-32.png)
are still **404** on sfa.nimrod.bio. Root cause: the home IP **rotates**, so any
laptop-IP allowlist entry is short-lived.

## Recommendation: Path 2 — waldhomeserver as the canonical deploy origin
Make the always-on, stable-IP `waldhomeserver` (46.235.231.114) the single
deploy route: (a) team_00 allowlists 46.235.231.114 at uPress, (b) open outbound
21 on the server. Then deploys run from the server (scriptable, repeatable, even
cron-able) — immune to ISP IP rotation. This also matches where the data pipeline
already runs.

Path 1 (allowlist current Mac IP) = quick stopgap but fragile (rotates again).
Path 3 (other allowlisted network/hotspot) = works if you have one, ad-hoc.

## Note
This is a uPress-account + network decision only team_00 can make (panel access).
Phase-1 closure stands (build/validation); only the operational delivery is
pending. Until deployed, the UI renders the SVG fallback (no broken images).

— team_100 (Claude Opus 4.7) 2026-05-29

---
## CORRECTION 2026-05-29 — host is s1240, not s887
Deploy attempt from waldhomeserver (egress 46.235.231.114) FAILED `max-retries
exceeded`. Root cause: `SFA_FTP_HOST=ftp.s1240.upress.link` (sfa.nimrod.bio is on
uPress **s1240**), but `s1240:21` is TCP-BLOCKED from the server while `s887:21`
(old market host) is OPEN. So outbound 21 works generally — **s1240 drops
46.235.231.114 at the network layer (not on s1240's FTPS allowlist)**. team_100's
earlier connectivity test/mandate referenced s887 (from the retired UPRESS_SFTP_*
market creds) — corrected here.

ACTION (team_00): allowlist **46.235.231.114** on the **s1240** server's FTPS for
sfa.nimrod.bio (NOT s887). Then re-run the deploy from waldhomeserver. All else
(lftp, vendor, creds, repo) staged.
