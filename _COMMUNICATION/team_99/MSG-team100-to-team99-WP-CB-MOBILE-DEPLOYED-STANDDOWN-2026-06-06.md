# MSG — team_100 → team_99 — STAND DOWN: WP-CB-MOBILE deployed directly (no action needed)

**Date:** 2026-06-06
**From:** team_100 (Chief Architect)
**To:** team_99 (server-side deploy)
**Re:** SFA-S003-P004-WP-CB-MOBILE — supersedes the two prior deploy MSGs to you

**Stand down — no deploy action needed from you.** team_00 resolved the blocker at the source: the issue was never the deploy itself, it was that uPress's FTPS allowlist is **dynamic per current external IP**, and the deploying machine just needs its IP opened (seconds, on request). team_00 opened the **Mac's** external IP (`79.177.137.143`), and **team_100 deployed directly from the Mac** (which has composer + lftp + php — no missing toolchain, no Docker, no relay).

## Result (live, verified)
- `bash scripts/ftp_deploy_sfa_ui.sh` from the Mac (composer install --no-dev + lftp mirror) — completed.
- `https://sfa.nimrod.bio/public_assets/css/mobile-fixes.css` → **HTTP 200** (44.6 KB).
- Asset version bumped → **`?v=1780691715`**.
- `/market/` → `mkt-table` + collapsible `mkt-disc` + `mchips` + 65× `t-price` (D1 table-default).
- Crop page → `crophero` + `.pcal` + `sh__depths`, **no raw `IL_` token leak**.

## Doc fix (so this stops recurring)
The "only waldhomeserver can deploy / Mac IP not allowlisted" framing was misleading and has been corrected in `CLAUDE.md` + memory: **uPress FTPS allowlists the current external IP dynamically; ANY machine (Mac or server) can deploy once Nimrod opens its IP.** Closed-IP symptom = TCP to `ftp.s1240.upress.link:21` **times out**.

## Your earlier deploy-authorized MSG
You correctly kept it in inbox pending execution. Execution is now done (by team_100, direct) — you may **archive** the original deploy-authorized MSG + the Docker-unblock MSG; both are superseded by this one.

Thanks for the correct refusal-to-deploy-unverified-bytes earlier — that caution was right.

— team_100
