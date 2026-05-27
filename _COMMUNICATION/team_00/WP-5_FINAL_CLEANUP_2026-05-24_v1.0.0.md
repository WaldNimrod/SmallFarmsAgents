---
id: WP-5_FINAL_CLEANUP_v1.0.0
type: BUILD_REPORT_AMENDMENT
gate: L-GATE_V (revised — full physical separation achieved)
work_package: SFA-S003-P003-WP-5
date: 2026-05-24
recorded_by: team_100 (in-session, sfa_build role)
status: LOD500_LOCKED — supersedes prior "meta-refresh" interim
triggers: team_00 directive 2026-05-24 ("התנתק לגמרה … יש למחוק … לא צריך הפניה אוטומטית")
---

# WP-5 Final Cleanup — Complete Physical Separation from Legacy Site

## §1 Outcome (revised final state)

`https://www.nimrod.bio/smallfarmsagent/` → **native WordPress 404 page** of the legacy site's "מהגינה של נימרוד" theme. No redirect. No SFA artifacts. The legacy commerce site continues to serve its own content with **zero coupling** to the SFA delivery tier.

`https://sfa.nimrod.bio/market/` → unchanged, fully functional, 65 products with real prices.

## §2 What changed since the 2026-05-24 interim report

The earlier WP-5 close described a meta-refresh interim solution because the uPress FTP allowlist on the legacy site (`s887`) had not propagated. The user (team_00) explicitly directed a deeper cleanup:

> "המערכת שלנו צריכה להתנתק לגמרה מהאתר הישן nimrod.bio ולפעול אך ורק מהאתר החדש - התקיות והקבצים באתר הישן יש למחוק!!!! לא צריך הפניה אוטומטית מהכתובת הישנה."

Translation: System must fully separate from the old nimrod.bio site and operate ONLY from the new site. Folders and files on the old site must be deleted. No need for auto-redirect from the old address.

FTP allowlist was now propagated (re-probed `nc` to port 21 on `185.201.148.144` → OPEN). Executed the full physical cleanup.

## §3 Execution log

### FTPS connection
- Custom `ReusedSessionFTP_TLS` subclass (required by uPress data-channel TLS session reuse — base `ftplib.FTP_TLS` returns 425 "Operation not permitted" without it)
- `prot_p()` + `set_pasv(True)`

### Files deleted from /smallfarmsagents/ (7 files + 2 dirs)
```
DEL  /smallfarmsagents/market/sfagent-manifest.json
DEL  /smallfarmsagents/market/sfagent-manifest-of-urls.json
DEL  /smallfarmsagents/market/sfagent-public-report-body.html
DEL  /smallfarmsagents/market/sfagent-public-report.html
DEL  /smallfarmsagents/market/sfagent-public-report.json
DEL  /smallfarmsagents/market/sfagent-smoke-test.json
DEL  /smallfarmsagents/market/test-auth.txt
RMD  /smallfarmsagents/market
RMD  /smallfarmsagents
```

### mu-plugins deleted (3 files)
```
DEL  /wp-content/mu-plugins/sfagent-allow-json.php
DEL  /wp-content/mu-plugins/sfagent-crop-book-shortcode.php
DEL  /wp-content/mu-plugins/sfagent-file-upload.php
```
(Other mu-plugins like `booter-crawlers-manager-mu.php` left untouched — they belong to the legacy commerce site.)

### WP page deletion
```
DELETE /wp-json/wp/v2/pages/91325?force=true
→ HTTP 200, previous status = publish, now permanently deleted (not trashed)
```

### Verification (same connection, post-cleanup)
- `/smallfarmsagents` present? **False**
- Remaining `sfagent-*` in mu-plugins: **0**

## §4 Browser-verified separation

| URL | Browser result | Theme |
|-----|----------------|-------|
| `https://www.nimrod.bio/smallfarmsagent/` | Native WP 404 ("נראה כי העמוד אותו חיפשת איננו קיים") | "מהגינה של נימרוד" intact, footer "Copyright 2026 © nimrod.bio · Design By Costalita.art" |
| `https://sfa.nimrod.bio/market/` | Slim PHP market table | "חקלאות קטנה" tier — 65 products, real prices |

Zero console errors on both. No artifact bleed.

## §5 Updated invariant (binding going forward)

**The SFA delivery tier `sfa.nimrod.bio` is now fully autonomous.** Architectural invariants:
- No publish/upload paths target `www.nimrod.bio`
- No SFA code expects to find files at `nimrod.bio/smallfarmsagents/*`
- No WP shortcode, no mu-plugin, no WP REST API call into the legacy site by SFA Python code
- The legacy `UPRESS_*` env vars (in `.env.legacy_*` archive) are dead code — Python deprecation annotations document this
- Future developers should not re-introduce any coupling

## §6 Carry-overs (revised — vs prior list)

| Item | Status |
|------|--------|
| ~~True 301 via .htaccess~~ | **N/A** — no redirect desired |
| ~~Physical deletion of sfagent-*.php~~ | **DONE this session** |
| Remove deprecated `wp_upload.py` + chain (callers + module) | S004 cleanup pass |
| alembic 035-042 on waldhomeserver prod Postgres | ops/prod-parity |
| Rotate FTP/DB/SMTP passwords (legacy + new) | team_00 |
| `.env.legacy_*` and `.env.upress.legacy_*` archives | Keep on disk (chmod 600, gitignored). Harmless. Audit trail of past credentials. |
| team_191 archive of stale team_99/SFA-S002-P001-WP008/ | next archive sweep |

## §7 P003 program status — FINAL

| WP | Status | Live evidence |
|----|--------|---------------|
| WP-1 uPress + DNS | ✅ LOD500_LOCKED | DNS resolves, FTPS works |
| WP-2 Slim app + DB + ingest | ✅ LOD500_LOCKED | https://sfa.nimrod.bio/api/v1/health |
| WP-3 user routes | ✅ LOD500_LOCKED | https://sfa.nimrod.bio/{crop-book,market}/ |
| WP-4 publisher cron | ✅ LOD500_LOCKED | Daily 06:30 cron on waldhomeserver |
| WP-5 cutover | ✅ LOD500_LOCKED (REVISED) | Legacy SFA artifacts fully deleted; 404 on old URL |

**`SFA-S003-P003` PROGRAM COMPLETE WITH FULL TIER SEPARATION.**

---

*Amendment filed 2026-05-24 by team_100. Supersedes the meta-refresh interim language in the prior WP-5 build report.*
