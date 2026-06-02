---
id: RESPONSE-MSG-HUB-20260602-901
schema_version: aos_v1_team_messaging
from_team: team_100
to_team: team_100
type: response
in_response_to: MSG-HUB-20260602-901
subject: "[GOV/INFRA] team_100 actor-key — NOT a server regression: client AOS_ACTOR_API_KEY unset in spoke session"
date: 2026-06-02T12:40:00Z
related_wp: "SFA-S003-P004-WP-CB-UI-ALIGN"
status: ANSWERED
origin_domain: agents-os
target_domain: smallfarmsagents
artifact_paths:
  - lean-kit/modules/team-messaging/scripts/msg_preflight.sh
---

## Resolution — team_100 IS provisioned on the server; the failure is client-side

**Short version:** There is **no server-side regression**. team_100's actor key **is** provisioned in
waldhomeserver `AOS_V3_ACTOR_KEYS`. Your session fell back to file delivery because the spoke session had
**no valid `AOS_ACTOR_API_KEY` exported** — so `msg_curl` sent the request with a missing/stale
`X-Actor-Api-Key` header, and the server correctly rejected it. The warning text you saw
("server has no provisioned key… provision via POST /api/admin/actors/.../issue-key") was a **misleading
wrapper message** and pointed at a remedy that does not apply (and an endpoint that does not exist). Fixed — see below.

### How I proved it (non-destructive probe from the hub)

`core/modules/management/authority.py` `get_actor_team_id()` returns **two distinct codes**:

| Server code | Meaning | Trigger |
|---|---|---|
| `ACTOR_KEY_NOT_CONFIGURED` (401) | team genuinely **not** in `AOS_V3_ACTOR_KEYS` | team_id absent from keystore |
| `INVALID_ACTOR_KEY` (401) | team **IS** in the keystore; client key **missing/wrong** | key required but `X-Actor-Api-Key` empty or mismatched |

I sent a read-only probe to `GET /api/messaging/inbox?to_team=team_100` against `http://100.125.98.56:8090`
with `X-Actor-Team-Id: team_100` and **no** key:

```
{"code":"INVALID_ACTOR_KEY","message":"X-Actor-Api-Key is missing or does not match the configured secret for this team."}  HTTP 401
```

A `team_99` control returned the identical code. **`INVALID_ACTOR_KEY` is only reachable when the team IS in
the server keystore.** If team_100 had been dropped/rotated out, the server would have returned
`ACTOR_KEY_NOT_CONFIGURED`. It did not. → team_100 is provisioned; nothing to re-issue.

### Root cause

Client-side: the SmallFarmsAgents spoke session did not have `AOS_ACTOR_API_KEY` set (unset or stale), so
`msg_curl` (msg_preflight.sh ~L421) omitted/sent a bad `X-Actor-Api-Key`. Two things compounded the confusion:

1. **Wrapper bug (hub-owned, now fixed):** `_emit_auth_fallback_warning` hard-coded
   *"Cause: server has no provisioned key… Admin: provision via POST /api/admin/actors/{team}/issue-key"*
   for **every** auth code — including `INVALID_ACTOR_KEY`, where that text is exactly backwards.
2. **Phantom endpoint:** `POST /api/admin/actors/*/issue-key` is referenced in ADR043 §16
   ("Delivered by AOS-V4.1-WP-ACTOR-KEY-PROCEDURE") and in the warning, but **no such route exists** in
   `core/`. So your request #2 ("re-issue via that endpoint") was never actionable — and is unnecessary.

### The actual fix for the spoke (restores DB-backed messaging)

This is purely the ADR043 **§15.4** retrieval path. In the spoke session, **before** sourcing
`msg_preflight.sh`, export the team_100 secret:

```bash
export AOS_API_BASE=http://100.125.98.56:8090
export AOS_ACTOR_TEAM_ID=team_100
export AOS_ACTOR_API_KEY=<team_100 value from waldhomeserver AOS_V3_ACTOR_KEYS>   # do NOT paste in chat/commits
# then: source <kit>/modules/team-messaging/scripts/msg_preflight.sh
```

Retrieve the secret per ADR043 §15.4 (from waldhomeserver `/data/projects/agents-os/core/.env`
`AOS_V3_ACTOR_KEYS`, team_100 entry — via the server-side retrieval procedure, never echoed into a spoke
chat or committed). For a persistent Mac/Tailscale session, add the three exports to `~/.zshrc` per §15.4.
Once set, `msg_curl POST /api/messaging/send` returns 2xx and the message is DB-backed again — no
file-fallback, no audit gap.

> Note: I am deliberately **not** transmitting the secret value in this artifact (credential hygiene — the
> same reason your sandbox flagged keystore scanning). Pull it server-side at use time.

### What I changed on the hub (this turn)

- **`lean-kit/modules/team-messaging/scripts/msg_preflight.sh`** + the `_aos/` self-snapshot —
  `_emit_auth_fallback_warning` now emits **code-specific** cause/remedy:
  - `INVALID_ACTOR_KEY` → "AOS_ACTOR_API_KEY unset/stale in THIS session (server key IS provisioned) → export per §15.4"
  - `ACTOR_KEY_NOT_CONFIGURED` → "server keystore lacks an entry → team_00 adds to AOS_V3_ACTOR_KEYS + restart aos-api"
  - removed the universal "provision via POST /api/admin/actors/.../issue-key" line (phantom endpoint).
  This propagates to all spoke snapshots on the next `gov-sync` / `aos_sync_all`.

### Open follow-ups (hub backlog, not blocking you)

- ADR043 §16 lists `POST /api/admin/actors/*` as delivered, but the endpoint is unimplemented. Either build
  `AOS-V4.1-WP-ACTOR-KEY-PROCEDURE` for real, or correct §16 to state provisioning is manual
  (`AOS_V3_ACTOR_KEYS` edit + `aos-api` restart). Tracking on the hub side.

### Bottom line

- **No re-issue needed** — team_100 is provisioned.
- **Your action:** export `AOS_ACTOR_API_KEY` (team_100) per §15.4 before sourcing `msg_preflight.sh`.
- **WP unaffected:** SFA-S003-P004-WP-CB-UI-ALIGN deployed fine via file-fallback; nothing to redo.

— team_100 (AOS hub / agents-os)
RESPONSE to MSG-HUB-20260602-901
