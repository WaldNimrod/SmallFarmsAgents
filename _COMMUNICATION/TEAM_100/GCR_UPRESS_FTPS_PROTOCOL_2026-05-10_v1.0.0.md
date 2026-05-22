---
id: GCR_UPRESS_FTPS_PROTOCOL_2026-05-10_v1.0.0
type: GOVERNANCE_CHANGE_REQUEST
from: Team 10 (sfa_build / SmallFarmsAgents)
to: Team 100 (Chief System Architect)
cc: Team 00 (Principal)
date: 2026-05-10
version: v1.0.0
urgency: HIGH
target_file: core/governance/upress_infrastructure.md (new) + all uPress-adjacent team contracts
project: cross-project (SmallFarmsAgents, TikTrack, any project on uPress/nimrod.bio)
---

# Governance Change Request: uPress FTPS — Canonical Connection Protocol

## 1. Requesting Team

- **Team ID:** 10 (sfa_build)
- **Role:** Builder
- **Project:** SmallFarmsAgents (discovered during WP004 crop-book deploy, 2026-05-10)
- **Engine:** Claude Sonnet 4.6

## 2. Proposed Change

Add a canonical infrastructure knowledge document covering the **correct and only working method for FTPS connection to uPress hosting** (`nimrod.bio`), to be propagated to all spoke repos and teams that interact with uPress.

The document should cover:
1. The exact Python ftplib connection pattern (`prot_c`, not `prot_p`)
2. IP allowlist requirement and workflow
3. What fails and why (so future agents don't repeat 3 hours of debugging)
4. WP option registration timing (mu-plugin must be installed before `register_setting` can be called via REST)
5. ezcache purge endpoint

## 3. Rationale

**This discovery cost significant agent time and was non-obvious.** The existing `.env` comment says "SSH/SFTP port 22 is blocked" — which is correct — but gave no guidance on how FTPS *does* work. Multiple connection attempts failed:

- Implicit FTPS (port 990) → timeout
- Explicit FTPS with `prot_p` (encrypted data channel) → `425 Unable to build data connection`
- curl `--ssl-reqd` → SSL cert failure → `425`

**The working combination is non-obvious:** explicit FTPS on port 21, control channel TLS only, data channel clear (`prot_c`), with IP allowlist in uPress panel.

Without this knowledge canonized:
- Every future agent/team touching uPress will repeat this debugging
- The IP allowlist requirement will cause silent failures with no clear error
- The mu-plugin timing issue (option registration before REST PUT) will cause `--set-mou-url` to silently no-op

**Affected projects:** SmallFarmsAgents (active), TikTrack-Phoenix (uPress), any future project on `nimrod.bio`.

## 4. Precise Prompt for Team 100

> Create a new canonical infrastructure document at:
> `core/governance/infrastructure/upress_ftps_protocol.md`
>
> With the following content (verbatim):
>
> ---
> # uPress FTPS — Canonical Connection Protocol
>
> **Host:** `ftp.s887.upress.link` · **Port:** 21 (explicit FTPS, STARTTLS)
> **Credentials:** `UPRESS_SFTP_HOST`, `UPRESS_SFTP_PORT`, `UPRESS_SFTP_USER`, `UPRESS_SFTP_PASS` from project `.env`
>
> ## Working Python pattern
>
> ```python
> import ftplib, ssl
>
> ctx = ssl.create_default_context()
> ctx.check_hostname = False
> ctx.verify_mode = ssl.CERT_NONE  # uPress data channel cert is self-signed
>
> ftp = ftplib.FTP_TLS(context=ctx)
> ftp.connect('ftp.s887.upress.link', 21, timeout=15)
> ftp.login(user, password)
> ftp.prot_c()       # MANDATORY — prot_p causes 425 on data channel
> ftp.set_pasv(True)
> # ftp.cwd(...), ftp.storbinary(...), ftp.nlst(...) all work now
> ```
>
> ## IP allowlist (MANDATORY before every connect)
>
> uPress blocks FTP by source IP. Before connecting:
> 1. `curl -s ifconfig.me` — get current agent IP
> 2. Open uPress control panel → FTP accounts → IP allowlist → add IP
> 3. Nimrod must confirm allowlist update before agent retries
>
> The agent IP is NOT static. Check before each session.
>
> ## What does NOT work
>
> | Attempt | Result |
> |---------|--------|
> | Implicit FTPS (port 990) | TCP timeout |
> | `prot_p()` on data channel | `425 Unable to build data connection` |
> | `curl --ssl-reqd ftps://...` | SSL cert error then `425` |
> | Connecting without IP allowlist | TCP timeout |
>
> ## WP option registration timing
>
> When a mu-plugin calls `register_setting()` on `init`, the option is only
> addressable via `POST /wp/v2/settings` **after the mu-plugin is installed**.
> Always install mu-plugin via FTPS first, then call `--set-mou-url` or equivalent.
>
> ## ezcache purge (after any file deploy)
>
> ```python
> requests.delete(
>     'https://www.nimrod.bio/wp-json/ezcache/v1/cache',
>     auth=(WP_APP_USER, WP_APP_PASS)
> )
> ```
> ---
>
> Then add a reference to this document in the governance contracts of all teams
> that interact with uPress/nimrod.bio (currently: team_10, any team in
> TikTrack-Phoenix, team_60 server-ops if relevant).

## 5. Impact Assessment

- **Affects other teams:** YES — any team touching uPress hosting: team_10 (SmallFarmsAgents), TikTrack teams, team_60 (server ops)
- **Requires context refresh broadcast:** YES — short broadcast to all active uPress-adjacent teams
- **Backward compatible:** YES — additive knowledge document only, no existing contracts modified

## 6. Approval

- [ ] Team 100 reviewed
- [ ] Team 00 approved
- [ ] Change executed in `core/governance/infrastructure/upress_ftps_protocol.md`
- [ ] Reference added to relevant team contracts
- [ ] Propagated to all relevant spoke repos
- [ ] Team 10 (requesting) notified

---

*Governance Change Request | AOS system*
*Filed: 2026-05-10 by sfa_build (team_10 / Claude Sonnet 4.6)*
*Discovery context: SmallFarmsAgents WP004 crop-book deploy — 3+ hours debugging FTPS*
