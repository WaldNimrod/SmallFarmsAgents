---
id: DEPLOY_BLOCKED_SFA-S003-P002-WP-UI-patch02_v1.0.0
title: team_99 — SFA UI deploy BLOCKED (uPress FTPS allowlist mismatch, current network)
status: BLOCKED — awaiting allowlist update OR allowlisted network
from_team: team_99 (Home Server Team — OPS)
to_team: team_100 (Chief Architect)
cc_team: team_00 (Principal — uPress panel allowlist owner), team_190 (live-deploy evidence pending)
parent_mandate: ./DEPLOY_MANDATE_v1.0.0.md
date: 2026-05-29
wp: SFA-S003-P002-WP-UI-patch02 (+ WP-UI-patch01 media)
---

# SFA UI Deploy — BLOCKED at lftp mirror (allowlist)

## TL;DR

The mandate's premise — *"team_99 (OPS) on an ALLOWLISTED network for uPress FTPS"* —
**is not true for the current network state**. Both candidate hosts in scope for
this OPS session are off the allowlist for `ftp.s1240.upress.link:21` today:

| Host | IPv4 egress | port 21 to ftp.s1240 |
|---|---|---|
| MacBook (home Wi-Fi)        | `79.177.137.169` | **timed out** (forced IPv4) |
| waldhomeserver (Tailscale)  | `46.235.231.114` | **blocked at network layer** |
| Yesterday's allowlisted IP for s887 (per FTPS-VERIFY-2026-05-26) | `79.177.143.165` | not the current egress |

`lftp` returns `mirror: Fatal error: max-retries exceeded` — exactly the same error
team_100 hit when writing this mandate. The ISP rotated the home-network IPv4
between yesterday and today (`.143.165` → `.137.169`), and `ftp.s1240.upress.link`
appears to whitelist a specific IPv4 (or narrow range) that neither current
candidate IP matches.

## What was done before the block

1. ✅ Pulled `main` to `3f57357` (≥ build `08a0f9e` per mandate).
2. ✅ Verified `SFA_FTP_HOST/PORT/USER/PASS/ROOT` keys present in `.env`.
3. ✅ Verified tooling: `lftp 4.9.3`, `composer 2.9.8`, `php 8.5.6`.
4. ✅ Inspected `sfa_delivery/` — all patch01 brand media present
   (`heroes/{8 files}.webp`, `hub-hero.webp`, `og-default.webp`, `favicon-32.png`,
   `apple-touch-icon.png`, `contact.webp`, `icons.svg`) and patch02 view layer
   present (`templates/_layout.php`, `templates/macros/crop_card.php`,
   `templates/pages/book_crop.php`, `modules.php`).
5. ✅ Ran `scripts/ftp_deploy_sfa_ui.sh`:
   - `composer install --no-dev --optimize-autoloader` — **OK**, removed 26 dev
     packages, generated optimized autoload.
   - `lftp mirror` — **FAIL**: `max-retries exceeded`.

Composer left `sfa_delivery/vendor/` in production-only state (13 MB, no dev
deps). To restore dev-deps locally, run
`composer install --working-dir=sfa_delivery` (no-op for this deploy).

## Pre-deploy public state (live HEAD probes)

| URL | Status |
|---|---|
| `https://sfa.nimrod.bio/` | 200 |
| `https://sfa.nimrod.bio/crop-book/` | 200 |
| `https://sfa.nimrod.bio/public_assets/img/heroes/crop-book.webp` | **404** |
| `https://sfa.nimrod.bio/public_assets/img/og-default.webp` | **404** |
| `https://sfa.nimrod.bio/public_assets/img/favicon-32.png` | **404** |

The 3 × 404s confirm that **patch01 media has never reached production** either —
the patch01 deploy mandate from yesterday (`MANDATE_SFA-UI-patch01-MEDIA-DEPLOY_v1.0.0.md`)
was issued but did not successfully execute. The allowlist block is a persistent,
multi-day condition.

## Root cause

uPress shared host `ftp.s1240.upress.link` (`185.108.148.246`) drops port-21
SYN packets from non-allowlisted IPs (no RST → TCP timeout). The allowlist has
not been updated to include the current home-network IPv4
(`79.177.137.169`) — which today is the closest candidate for an allowlisted
egress.

## Unblock options (team_00 / team_100 to decide)

1. **uPress panel allowlist update.** Log into the uPress control panel for
   `sfa.nimrod.bio` and add `79.177.137.169/32` (current Mac egress) **or** the
   broader Bezeq subscriber range (e.g., `79.177.128.0/19` or wider — note this
   has privacy/security trade-offs) to the FTPS IP allowlist. Owner: team_00
   (Principal — only human with uPress credentials).
2. **Static allowlist via a server with a fixed IP.** Open outbound port 21 on
   waldhomeserver (currently dropped by host/network firewall) and add its
   Tailscale-fronted public egress (`46.235.231.114`) to the uPress allowlist.
   This survives ISP rotation. Note: `46.235.231.114` looks like a stable
   cellular/co-lo IP, not Bezeq DHCP. Owner: team_00 + team_60.
3. **VPN/proxy to a known allowlisted IP.** Out of scope for OPS today.

Once any of (1)(2) lands, re-run is a one-liner — composer is already done, and
`lftp mirror` is idempotent:

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents && bash scripts/ftp_deploy_sfa_ui.sh
```

## What I am NOT doing

- ❌ **Not** claiming AC-U2-06 closed or notifying team_190 of live-deploy
  evidence — the deploy did not reach the wire.
- ❌ **Not** modifying `_aos/`, `roadmap.yaml`, or any L0 governance file.
- ❌ **Not** force-pushing or amending commits.
- ❌ **Not** retrying lftp from a non-allowlisted network — burns retries and
  may trigger temporary block escalation.

— team_99 (OPS / MacBook on home Wi-Fi) 2026-05-29
