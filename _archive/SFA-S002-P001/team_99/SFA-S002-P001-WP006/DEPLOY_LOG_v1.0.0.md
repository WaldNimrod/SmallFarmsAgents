# DEPLOY_LOG — SFA-S002-P001-WP006 — team_99

**Date:** 2026-05-06
**Author:** team_99 (waldhomeserver)
**WP:** SFA-S002-P001-WP006
**Type:** DEPLOY_LOG
**Smoke result:** FAIL — FTPS upload timed out

---

## 1. Deploy

- **Branch:** `offline/2026-05-07-smallfarmsagents-release-prep`
- **Build commit:** `55ac306` (on offline branch)
- **Command:** `.venv/bin/python -m organic_market_agent run_publisher --upload`

## 2. Build result

Build phase succeeded — artifacts written to `output/public/`:

| Field | Before (stale) | After (built) |
|-------|----------------|---------------|
| `artifact_version` | `20260417_004822` | `20260506_220047` |
| `product_count` | 1 | **32** |
| `report_date` | `2099-08-12` (placeholder) | `2026-05-06` (correct) |
| `staleness_level` | `current` | `current` |

**Build is healthy.** 32 products from the rolling 7-day window.

## 3. Upload result — FAIL

```
2026-05-06 22:01:03 ERROR organic_market_agent.publisher.ftps_upload — FTPS upload error: timed out
FTPS upload FAILED: 0 ok, 0 failed — timed out
```

## 4. Root cause investigation

### Hypothesis tested: TLS session reuse (from Pass-1 F-01)

sfa_build confirmed the `ReusedSessionFTP_TLS` subclass was **already present** in `ftps_upload.py`. 14 tests pass. TLS session reuse is NOT the root cause.

### Actual root cause: NAT64 (clatd) does not support FTP port 21

| Test | Target | Port | Result |
|------|--------|------|--------|
| `ftp.s887.upress.link` | 185.201.148.144 | 21 | **timed out** |
| `ftp.debian.org` | (IPv4) | 21 | **timed out** |
| `185.201.148.144` | direct IP | 443 | **CONNECTED** |
| `1.1.1.1` | Cloudflare | 443 | **HTTP 301** (clatd works) |

**FTP port 21 is completely blocked via clatd/NAT64.** The `nat64.net` public NAT64 gateway does not forward FTP traffic. This affects ALL FTP targets, not just uPress.

**DNS records:**
- `ftp.s887.upress.link` → `185.201.148.144` (A only, no AAAA)

### Why it worked before May 3

Before exit-node removal (May 6 08:03 UTC), all traffic routed through the Mac's Tailscale exit-node, which provided full IPv4 connectivity including FTP. The exit-node was removed to fix cloudflared tunnel instability (CF 524 pilot blocker). HTTPS, SSH, and SMTP were all migrated to IPv6-native alternatives, but FTP was overlooked.

### Why HTTPS clatd works but FTP doesn't

HTTPS (port 443) is a single TCP stream — NAT64 translates it fine. FTP uses a control channel (port 21) plus a separate data channel (passive mode: server-chosen port). NAT64 gateways commonly block or can't handle FTP's multi-connection protocol, especially with PASV mode where the server sends back an IPv4 address that the NAT64 client can't reach directly.

## 5. Options for team_100

1. **SFTP/SCP instead of FTPS** — if uPress supports SSH-based upload, this would be a single TCP stream and work via clatd.
2. **Temporary exit-node for FTP** — re-enable Tailscale exit-node only during publisher cron runs (06:00 UTC), then disable. Requires scripting + Mac availability.
3. **Alternative upload method** — HTTP PUT/POST upload if the WordPress hosting supports it (REST API, WebDAV).
4. **Self-hosted NAT64** — replace nat64.net with local Tayga + Jool. Complex but gives full protocol support. Canon §4 warns against Tayga routing loops.
5. **Migrate to IPv6-capable hosting** — long-term, eliminates all NAT64 issues.

## 6. Conclusion

**F-01 root cause identified:** NAT64 (clatd via nat64.net) does not forward FTP port 21 traffic. The FTPS code is correct (TLS session reuse implemented). The issue is Layer 3/4 transport, not Layer 7 application.

**WP006 AC-04/05/06 FAIL** — upload does not succeed.
**WP003 Pass-2 BLOCKED** — cannot proceed until upload path is restored.

No application code changes were made (per IR §63). Surfacing to team_100 for re-spec.

---

*team_99 | waldhomeserver | 2026-05-06*
