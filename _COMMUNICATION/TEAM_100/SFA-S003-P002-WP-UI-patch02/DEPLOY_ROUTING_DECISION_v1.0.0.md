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
