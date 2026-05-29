---
id: MANDATE_SFA-UI-patch01-MEDIA-DEPLOY_v1.0.0
from: Team 100 (Chief System Architect)
to: Team 99 (Home Server Team — waldhomeserver / allowed network)
date: 2026-05-29
type: DEPLOY_MANDATE
wp: SFA-S003-P002-WP-UI-patch01
status: ACTIVE
reason: "FTPS port 21 egress is blocked on the dev (Bezeq) network — same condition as S002 F-01. team_100 merged the validated media to main + ran composer install, but the lftp mirror to ftp.s1240.upress.link:21 failed (max-retries). Deploy must run from an allowed network."
---

# DEPLOY MANDATE — SFA UI patch01 media → sfa.nimrod.bio

The watercolor visual system (8 module heroes + og-default + hub-hero + contact +
favicon, composed from the Devora masters) is **merged to main** (commit `22c052d`,
closure `04a23d6`) and **L-GATE_V R2 PASS** (team_190, non-Claude). Only the
**production deploy** remains — blocked here by port-21 egress.

## Run from waldhomeserver (or any network that allows outbound FTPS port 21)
```bash
cd <SmallFarmsAgents checkout>
git pull origin main                      # must include commit 04a23d6 (or later)
# ensure .env has SFA_FTP_HOST/PORT/USER/PASS/ROOT (uPress sfa.nimrod.bio creds)
bash scripts/ftp_deploy_sfa_ui.sh          # composer install --no-dev + lftp FTPS mirror
```
The script: sources `.env`, runs `composer install --no-dev --optimize-autoloader`
in `sfa_delivery/`, verifies `vendor/`, then `lftp mirror -R --delete` to
`SFA_FTP_ROOT`. (vendor/ stays gitignored — Option B.)

## Smoke check after deploy
1. `curl -sI https://sfa.nimrod.bio/ | head -1` → `200`
2. Load `https://sfa.nimrod.bio/` — home module cards now show **watercolor hero
   images** (not the icon fallback).
3. og:image resolves: `https://sfa.nimrod.bio/public_assets/img/og-default.webp` → 200.
4. favicon loads. Spot-check `/crop-book/` + `/market/`.

## Report back
Notify team_100 (`_COMMUNICATION/TEAM_100/`) with the smoke results. On success,
team_100 marks the patch01 deploy COMPLETE in roadmap and confirms the WP-UI visual
system fully live. Routinely the daily 06:00 cron is unaffected (no pipeline change).
