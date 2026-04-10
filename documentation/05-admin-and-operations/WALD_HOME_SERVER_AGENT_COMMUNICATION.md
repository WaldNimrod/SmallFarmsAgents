# Wald home server — agent communication (Team 61)

**Version:** 1.0  
**Date:** 2026-04-10  
**Status:** Canonical (SmallFarmsAgents + server operations handoff)  
**Owner:** Team 100 (Architecture)

This document locks the **file-based procedure** for instructions and receipts between the Mac development environment and **Team 61 (Server Operations)** on **waldhomeserver**. It does **not** replace `git` deployment; it ensures the server-side agent always has a **durable message** in an agreed inbox.

---

## 1. Roles

| Role | Responsibility |
|------|----------------|
| **Mac / Cursor agents (Team 10, etc.)** | Write outbound messages under the Mac path below; **push** each new file to the server inbox with `scp` after any GitHub push that requires server action (or when standalone coordination is needed). |
| **Team 61 (server agent)** | Poll **`~/agent_comm/inbox/`** on waldhomeserver; execute tasks; leave receipts if the workflow requires acknowledgment. |
| **Direct SSH** | Allowed for `git pull`, `systemctl`, diagnostics — but **not** a substitute for the inbox when Team 61 must see a written handoff. |

---

## 2. Paths (exact)

### 2.1 Mac — outbound draft / archive

| Item | Path |
|------|------|
| Outbox (write new messages here) | `~/Documents/_agent_comm/outbox/` |
| Filename pattern | `MSG-YYYYMMDD-NNN.md` |
| Optional response copies (archive) | Same directory, name suffix `-RESPONSE` (e.g. `MSG-20260410-004-RESPONSE.md`) |

Use a monotonic `NNN` per day (001, 002, …). Do not collide with existing files in that directory.

### 2.2 Server — inbound for Team 61

| Item | Path |
|------|------|
| Inbox (canonical) | `/home/nimrodw/agent_comm/inbox/` |
| Equivalent | `~/agent_comm/inbox/` as user `nimrodw` |

Team 61 watches this directory for new `MSG-*.md` files.

---

## 3. Push command (required after creating a message)

From the Mac, after saving `MSG-YYYYMMDD-NNN.md` under the outbox:

```bash
scp ~/Documents/_agent_comm/outbox/MSG-YYYYMMDD-NNN.md \
  nimrodw@10.100.102.2:~/agent_comm/inbox/
```

**Tailscale (when LAN is unavailable):**

```bash
scp ~/Documents/_agent_comm/outbox/MSG-YYYYMMDD-NNN.md \
  nimrodw@100.125.98.56:~/agent_comm/inbox/
```

Verify on the server:

```bash
ssh nimrodw@10.100.102.2 'ls -la ~/agent_comm/inbox/MSG-YYYYMMDD-NNN.md'
```

### 3.1 Pull responses from Team 61 (canonical feedback on Mac)

Replies and reports are written by the server agent to **`~/agent_comm/outbox/`** on waldhomeserver. The Mac **does not** receive them automatically. Pull into your local **`~/Documents/_agent_comm/inbox/`**:

```bash
scp nimrodw@10.100.102.2:~/agent_comm/outbox/* ~/Documents/_agent_comm/inbox/
```

Use **Tailscale** when LAN is unavailable (`nimrodw@100.125.98.56`). If a message (e.g. **MSG-011** RFI) appears missing on the Mac, run this pull **before** re-sending the request.

---

## 4. Message format (minimum)

Each file should be readable as a standalone task. Recommended structure:

1. A short **YAML-style header block** (id, from, to, date, type, priority) — see existing messages in the Mac outbox for examples.
2. **`## Subject`** — one line.
3. **`## Body`** — commands, commit SHAs, verification steps (`curl`, `systemctl`, paths under `/data/projects/smallfarmsagents`).

Hebrew is allowed **only** in direct messages to Nimrod; **these files should remain English** so all operators and agents align with the project language policy.

---

## 5. SFA deployment context (reference)

| Key | Value |
|-----|--------|
| Hostname | waldhomeserver |
| Project path | `/data/projects/smallfarmsagents` |
| Admin service | `sudo systemctl start|stop|status|restart sfa-admin` |
| Admin URL (on server) | `http://127.0.0.1:5001` |

Git operations and restarts must still follow normal release hygiene; the inbox message documents **intent and verification** for Team 61.

---

## 6. Anti-patterns

- **Do not** assume Team 61 saw a deployment because SSH was used. If they need to act or acknowledge, **create and `scp` a message**.
- **Do not** store secrets (passwords, API keys) in inbox files; use existing env and credential patterns on the server.

---

## Related

- Admin & operations hub: [`README.md`](README.md)
- Project-wide agent context: `.cursor/rules/project-context.mdc` (staging server pointer)
