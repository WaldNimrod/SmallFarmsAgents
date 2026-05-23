---
id: UPRESS_PROVISIONING_RESULTS_SFA-S003-P003-WP-1_v1.0.0
type: PROVISIONING_RESULTS
gate: WP-1 closure
work_package: SFA-S003-P003-WP-1
date: 2026-05-23
recorded_by: team_100 (executed by team_00 on uPress panel, verified end-to-end by team_100)
status: WP-1 COMPLETE
unblocks: SFA-S003-P003-WP-2 (Slim PHP skeleton + DB schema + ingest endpoint)
---

# WP-1 Provisioning Results — sfa.nimrod.bio on uPress + Cloudflare

## §1 Outcome

**APPROVED & VERIFIED 2026-05-23**: dedicated SFA delivery tier `sfa.nimrod.bio` is provisioned end-to-end. All WP-1 acceptance criteria met. WP-2 may proceed.

## §2 Verified end-to-end (by team_100 from Mac)

| Layer | Test | Result |
|-------|------|--------|
| DNS | `dig +short sfa.nimrod.bio` | `172.67.167.139`, `104.21.73.254` (Cloudflare proxy IPs) ✅ |
| HTTPS | `curl -sSI https://sfa.nimrod.bio/` | `HTTP/2 404 server: cloudflare` (= origin reached, app not deployed yet — expected) ✅ |
| FTP DNS | `dig +short ftp.s1240.upress.link` | `185.108.148.246` ✅ |
| TCP port 21 | `nc -zv -w 5 ftp.s1240.upress.link 21` | `succeeded` (after IP `147.235.203.51` added to uPress allowlist) ✅ |
| FTPS + TLS + auth | `lftp -e "set ftp:ssl-force true; set ftp:ssl-protect-data true; ls"` | listing returned: `index.php` (327058 B) ✅ |

## §3 Resources provisioned

| Resource | Value | Stored where |
|----------|-------|--------------|
| Site domain | `sfa.nimrod.bio` | Cloudflare CNAME (proxied), uPress site root |
| FTP host | `ftp.s1240.upress.link` | `.env` → `SFA_FTP_HOST` |
| FTP user | `sfadeploy@sfa.nimrod.bio` | `.env` → `SFA_FTP_USER` |
| FTP pass | (in `.env` only — chmod 600) | `.env` → `SFA_FTP_PASS` |
| FTP allowlist | `147.235.203.51` (Mac) | uPress panel — pending: add waldhomeserver public IP |
| MySQL DB name | `sfanms2u_SFAUserUiDB` | `.env` → `SFA_DB_NAME` |
| MySQL DB user | `sfanms2u_DbAdmin` | `.env` → `SFA_DB_USER` |
| MySQL DB pass | (in `.env` only — chmod 600) | `.env` → `SFA_DB_PASS` |
| MySQL host (app-side) | `localhost` | `.env` → `SFA_DB_HOST` |
| Ingest HMAC secret | (in `.env` only — 32 bytes base64) | `.env` → `SFA_INGEST_HMAC_SECRET` |
| Cloudflare DNS record | CNAME `sfa` → www target, **proxied** (orange cloud) | Cloudflare zone `nimrod.bio` |
| Cloudflare TLS | Universal SSL (auto) | Cloudflare edge |

## §4 Discoveries that affect downstream WPs

1. **No WordPress auto-install on this site** — `ls` of site root shows only `index.php` (327KB — uPress default landing). Original DECISION §1 assumed coexistence with a WP shell; reality is **cleaner**: we can drop Slim app directly at site root, no `/app/` subdirectory needed. WP-2 LOD400 will reflect this.

2. **FTP IP allowlist is per-account** — adding the Mac IP to the legacy `mezoohost@nimrod.bio` account did NOT auto-apply to the new `sfadeploy@sfa.nimrod.bio` account. **TODO before WP-4**: add waldhomeserver's public IP to allowlist (so the daily publisher can push). team_00 to run `ssh waldhomeserver curl -sS https://api.ipify.org` and add that IP via uPress panel.

3. **FTPS prot_c required** — same as legacy site (`set ftp:ssl-protect-data true` ≡ `prot_c`). Without it, data channel attempts fail TLS. Pre-existing knowledge confirmed.

4. **Cloudflare proxy on** — confirmed by `server: cloudflare` header. Edge cache + Universal SSL active. Pass-through for dynamic routes.

## §5 Resolved open items from LOD400

| Item | Status |
|------|--------|
| Subdomain on existing plan? | ✅ same plan, no additional cost |
| MySQL DB on subdomain? | ✅ provisioned `sfanms2u_SFAUserUiDB` |
| PHP 8.x available? | ⏸ to verify in WP-2 first deploy (uPress default is current PHP) |
| FTP credentials work? | ✅ verified via `lftp` |
| mod_rewrite for clean URLs? | ⏸ to verify in WP-2 (will deploy `.htaccess` and confirm rewrites work) |
| HTTPS / Let's Encrypt | ✅ via Cloudflare Universal SSL (no LE needed at origin) |
| Bandwidth / file-size / execution-time limits | ⏸ standard uPress shared limits — to test under load in WP-3 |
| Cloudflare-to-uPress origin pull | ✅ works (404 returned via CF→origin→back) |

## §6 Environment hygiene

- Local `.env` file: `chmod 600`, gitignored, contains only new-architecture vars (all UPRESS_* legacy keys removed)
- Legacy archived: `.env.legacy_2026-05-23` (chmod 600, gitignored)
- Legacy `.env.upress` archived: `.env.upress.legacy_2026-05-23` (chmod 600, gitignored) — was loaded by `config.py` AFTER `.env`, would have overridden new values
- HMAC secret generated via `openssl rand -base64 32`, embedded in `.env`, pending mirror on waldhomeserver `.env`

## §7 Security notes (acknowledged)

Both FTP and DB passwords were displayed in shell output during diagnostic runs (`sed -n` and `lftp` debug). They appear in this session's transcript. Recommended action **after WP-2/3/4 stable**: rotate both via uPress panel (1-minute action each). Not blocking.

## §8 Hand-off to WP-2

team_100 proceeds immediately to author WP-2 LOD400 (Slim PHP skeleton + DB schema + ingest endpoint). All inputs from this WP-1 closure are sufficient. No further team_00 action required until WP-2 LOD400 is presented for approval.

---

*Filed 2026-05-23 by team_100 (smallfarmsagents) on behalf of team_00.*
*Branch: `claude/gallant-elbakyan-727a60`*
