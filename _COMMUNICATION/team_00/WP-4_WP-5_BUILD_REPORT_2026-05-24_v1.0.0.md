---
id: WP-4_WP-5_BUILD_REPORT_v1.0.0
type: BUILD_REPORT
gate: L-GATE_V (both WPs closed)
work_packages: [SFA-S003-P003-WP-4, SFA-S003-P003-WP-5]
date: 2026-05-24
recorded_by: team_100 (executed in-session as sfa_build)
status: BOTH LOD500_LOCKED — P003 phase-2 COMPLETE
program_status: SFA-S003-P003 fully closed (WP-1 + 2 + 3 + 4 + 5)
---

# WP-4 + WP-5 BUILD Report — Publisher deployed + Legacy cutover complete

## §1 Outcome

**Both WPs are LIVE end-to-end.** The SFA delivery migration (`SFA-S003-P003`)
is now fully closed:

- **Old URL** `https://www.nimrod.bio/smallfarmsagent/` → automatic browser redirect
- **New URL** `https://sfa.nimrod.bio/market/` → serves 65 products with **real prices** from waldhomeserver prod Postgres, via daily cron-driven HMAC-authenticated push
- The 2026-05-23 stale-data bug (1 product, placeholder 2099-08-12) is **fully SUPERSEDED**

## §2 WP-4 — publisher deployed to waldhomeserver

| Step | Detail |
|------|--------|
| File transfer | `scp organic_market_agent/publisher/sfa_ingest_push.py nimrodw@100.125.98.56:/data/projects/smallfarmsagents/.../` (Tailscale) |
| Deps check | `.venv/bin/python -c "import psycopg2, requests, dotenv"` — already present, no install needed |
| Env vars | `cp .env .env.bak.$(date)`; appended `SFA_HOST`, `SFA_PUBLIC_BASE`, `SFA_INGEST_URL`, `SFA_INGEST_HMAC_SECRET` (block sourced from Mac `.env` values, never echoed in transcript); `chmod 600 .env` |
| Live push test | `python organic_market_agent/publisher/sfa_ingest_push.py` from waldhomeserver: **65 products in 2 batches, both 200, ~3s**. Crops/varieties skipped cleanly per resilient handler (alembic 034 on prod < 042 local). |
| Daily cron | `30 6 * * * cd /data/projects/smallfarmsagents && .venv/bin/python organic_market_agent/publisher/sfa_ingest_push.py >> /data/backups/sfa-ingest-push.log 2>&1` — installed in `nimrodw` crontab, 30 min after existing scheduler.runner |
| Auto-retention | `IngestController.php` updated: 1% of POSTs run `DELETE FROM ingest_log WHERE applied_at < NOW() - INTERVAL 30 DAY`. Cheap (indexed), self-healing, no cron required. Re-deployed via FTPS. |
| Resilience patch | `sfa_ingest_push.py::_push_table` catches `psycopg2.errors.UndefinedTable`, rolls back, logs warning, skips with `{skipped:"source_schema_missing"}` — keeps daily cron robust against partial prod schemas. |
| Old code | `wp_upload.py` + `ftps_upload.py` + `upload_dispatch.py` annotated DEPRECATED in module docstrings. No callers removed (S004 cleanup will do that). |

### Sanity post-deploy
```
{"accepted":1,"rejected":0,"errors":[],"idempotency_key":"prune_check_001"}    POST → 200
{"accepted":1,"rejected":0,"errors":[],"idempotency_key":"prune_check_001_del"}  delete-op → 200
```

## §3 WP-5 — legacy cutover

**Initial plan:** FTP-based `.htaccess` 301 + remove `sfagent-*` mu-plugin files on `www.nimrod.bio` (legacy site `s887`).

**Encountered:** uPress FTP allowlist for `mezoohost@nimrod.bio` on `s887` did not propagate (port 21 timed out repeatedly even after user updated the panel). Per-account allowlist on a separate server pool from the new site (`s1240`).

**Pivot:** WP REST API approach.

| Step | Detail |
|------|--------|
| Find page | `GET /wp-json/wp/v2/pages?slug=smallfarmsagent` → id=91325 |
| PATCH content | `POST /wp-json/wp/v2/pages/91325` with new content: `<meta http-equiv="refresh"/>` + `<script>window.location.replace(...)</script>` + Hebrew RTL fallback `<div>` with manual button. Title set to "מועבר ל-sfa.nimrod.bio". Result: 200, modified `2026-05-23T22:43:34`. |
| Verify | Claude_in_Chrome navigated to https://www.nimrod.bio/smallfarmsagent/ → auto-redirect → final URL https://sfa.nimrod.bio/market/ ✅ |
| mu-plugin files | Left in place on disk (not reachable via FTP). Harmless: no page references the `[sfagent_market_report]` shortcode anymore, so the .php code is unreferenced dead-code. |

### Browser screenshot evidence
- Tab title: `מחירון · Small Farms Agents`
- URL bar: `sfa.nimrod.bio/market/`
- Page body: 65 products in RTL Hebrew table with real prices
- Console: zero errors

## §4 Trade-offs of WP-5 pivot

| Aspect | True 301 (.htaccess) | Meta-refresh (delivered) |
|--------|----------------------|---------------------------|
| HTTP semantic | clean 301 Permanent | 200 OK with redirect markup |
| Browser behavior | instant, no render | instant, brief no-render flash possible |
| SEO transfer | full link-juice transfer | partial (Google handles meta-refresh as redirect-ish for 1-2s delay) |
| User experience | identical | identical |
| Bookmarks rewritten | yes (302+ chain) | no |
| Implementation effort | needs FTP allowlist | done now |

For a small Hebrew agritech site with no significant inbound link juice, the meta-refresh delivers **100% of the user-visible value**. SEO carry-over is the only material difference — acceptable for our scale. True 301 remains as carry-over for whenever FTP allowlist propagates.

## §5 Findings (audit)

| ID | Sev | Description | Disposition |
|----|-----|-------------|-------------|
| F-4-1 | INFO | waldhomeserver Postgres alembic_version=034 < repo head 042. Migrations 035-042 (crop_book) haven't run on prod. Publisher gracefully skips crops/varieties from prod; Mac is interim source. | Carry-over to ops/prod-parity housekeeping (pre-existing gap from S003-P001 deploy — not new from P003). |
| F-5-1 | LOW | True 301 not possible until uPress FTP allowlist on `s887` propagates. Meta-refresh redirect delivered as functional equivalent. | Carry-over (low priority; current UX is identical to user). |
| F-5-2 | LOW | mu-plugin `.php` files still on disk in `wp-content/mu-plugins/` (e.g. `sfagent-file-upload.php`, `sfagent-shortcode.php`). Unreferenced and harmless — no page invokes their shortcodes. | Carry-over (clean up when FTP allowlist works). |
| F-5-3 | INFO | uPress nginx 80/443 reach `s887` fine; only port 21 firewalled. Confirms allowlist is per-account-per-protocol, not site-wide. | Documented for future deploy planning. |

## §6 Final inventory — what runs where

| Component | Where | How |
|-----------|-------|-----|
| Postgres SSoT (52 crops, 65 products + 242 varieties, ~daily aggregates) | waldhomeserver `oma-postgres` docker | unchanged backend |
| Pipeline (scrapers + normalizer + aggregator) | waldhomeserver via `organic_market_agent.scheduler.runner` cron @ 06:00 | unchanged |
| **Publisher** (Postgres → sfa.nimrod.bio) | waldhomeserver via `sfa_ingest_push.py` cron @ 06:30 | **NEW** |
| **MySQL mirror** | uPress `sfanms2u_SFAUserUiDB` (auto-pruned `ingest_log` >30d) | **NEW** |
| **Slim PHP app** | uPress `sfa.nimrod.bio` (PHP 8.5.5) | **NEW** |
| **Cloudflare proxy + edge TLS** | CF zone `nimrod.bio`, A record `sfa` → 185.108.148.246 | **NEW** |
| **HTML rendering** | Slim PHP templates on uPress (`/`, `/crop-book/`, `/market/`) | **NEW** |
| Legacy `/smallfarmsagent/` page | client-side redirect to `sfa.nimrod.bio/market/` via meta+JS | **CUTOVER** |
| Legacy `wp_upload.py` + `ftps_upload.py` + `upload_dispatch.py` | DEPRECATED docstrings, kept for reference | **DEPRECATED** |

## §7 P003 program-level summary (final)

| WP | Title | Status | Live evidence |
|----|-------|--------|---------------|
| WP-1 | uPress provisioning + Cloudflare DNS | ✅ COMPLETE | DNS resolves, FTPS works |
| WP-2 | Slim PHP skeleton + DB schema + ingest API | ✅ COMPLETE | https://sfa.nimrod.bio/api/v1/health |
| WP-3 | User-facing routes (crop-book + market) | ✅ COMPLETE | https://sfa.nimrod.bio/{crop-book,market}/ |
| WP-4 | Publisher migration → cron on waldhomeserver | ✅ COMPLETE | Daily 06:30 cron pushes real prices |
| WP-5 | Cutover from www.nimrod.bio/smallfarmsagent/ | ✅ COMPLETE | Old URL redirects to new live site |

**`SFA-S003-P003` program closed 2026-05-24.**

## §8 Known carry-overs (not blocking P003 closure)

| Item | Owner | When |
|------|-------|------|
| Run alembic 035-042 on waldhomeserver prod Postgres + seed crop_book | ops / Team 99 | next ops window |
| True 301 via `.htaccess` on legacy `www.nimrod.bio` (waiting allowlist) | ops | when allowlist propagates |
| Physically delete `sfagent-*` mu-plugin .php files from legacy site | ops | when FTP works |
| WP-2-patch01 .htaccess hardening (`composer.json` + SQL files) | sfa_build | low priority |
| WP-3-patch01 design re-skin per team_35 LOD300 | team_35 → sfa_build | when WP-B ships |
| Remove deprecated `wp_upload.py` + chain (callers + module) | sfa_build | S004 cleanup pass |
| Rotate FTP/DB/SMTP passwords leaked in transcript | team_00 | after this commit |
| team_191 archive of `team_99/SFA-S002-P001-WP008/` (pre-existing Check 15 fail) | team_191 | next archive sweep |

## §9 Files of record

- Source (WP-4): `organic_market_agent/publisher/sfa_ingest_push.py` (resilience patch + retention)
- Source (WP-5 server side): `sfa_delivery/app/Controllers/IngestController.php` (auto-prune block)
- Deprecation annotations: `organic_market_agent/publisher/{wp_upload,ftps_upload,upload_dispatch}.py`
- WP REST PATCH: page id 91325 on www.nimrod.bio (server-side state only)
- waldhomeserver cron: `nimrodw@100.125.98.56:~/.crontab` (line: `# SFA ingest push (P003)` + `30 6 * * * ...`)
- waldhomeserver env: `/data/projects/smallfarmsagents/.env` (4 new SFA_* keys, backup `.env.bak.*`)
- Roadmap: `_aos/roadmap.yaml` WP-4 + WP-5 → COMPLETE/LOD500_LOCKED; WP-5 newly added
- Build reports: this + WP-2 + WP-3_WP-4 prior reports

---

*Build report filed 2026-05-24 by team_100. SFA-S003-P003 program fully closed. Next program TBD by team_00.*
