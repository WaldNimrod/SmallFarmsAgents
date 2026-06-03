# SFA Delivery, Deployment, and Operations

**Document 07 of the SFA Product Information Pack.**
**Audience:** DevOps engineers, platform operators, engineering managers, NotebookLM ingestion.
**Sources:** `documentation/02-architecture/sfa-delivery-tier.md`; `documentation/05-admin-and-operations/UI_DEPLOY_RUNBOOK.md`; `documentation/05-admin-and-operations/FTPS_CRED_ROTATION_SYNC_RUNBOOK.md`; `documentation/08-troubleshooting/README.md`; `documentation/KNOWN_DEBT.md`; `documentation/08-troubleshooting/` (Docker workstation doc).

**Abstract.** The SFA platform is operated across three physically distinct machines with non-overlapping roles. This document covers the hosting topology and the rationale for each machine's role; the two-part deploy pipeline (code via FTPS relay, data via HMAC ingest); cron automation and freshness guards; the complete security model (HMAC, IP allowlist, FTPS explicit TLS, migration token gate); Docker port canon for the shared development workstation; and a high-level summary of known operational debt. Operators and engineers planning new features or infrastructure changes should read this document before touching anything deploy/host/network related.

---

## 1. Three-Host Topology

The word "host" refers to three completely different machines. Never conflate them.

| Role | Machine | What it does | What it does NOT do |
|------|---------|--------------|---------------------|
| **Web host** (the live site + MySQL) | **uPress** shared LAMP `sfa.nimrod.bio`, Cloudflare edge | Serves ALL end-user HTTP; hosts the live MySQL read-mirror; terminates TLS via Cloudflare | — |
| **Backend / pipeline host** | **waldhomeserver** (home server, private network, Tailscale) | Canonical Postgres SSoT; all scrapers, normalizer, aggregator, cron; AOS infra agents | NEVER serves end-user HTTP; not a staging mirror |
| **Deploy relay / data push origin** | **waldhomeserver** (egress IP allowlisted by uPress on port 21) for *code*; **Mac** or waldhomeserver for *data* | Runs `lftp mirror` (code FTPS) and/or `sfa_ingest_push.py` (data HTTPS) toward uPress | Does not host or serve anything to end users |

### Why this topology exists

Three separate concerns drove the three-machine split:

1. **End-user HTTP needs a reliable public host with a proper SSL cert.** uPress provides this: shared LAMP on a CDN-backed hostname (`sfa.nimrod.bio`), Cloudflare Universal SSL, nginx managed by uPress. Running a web server on the home server would require a static IP, port forwarding, cert management, and DDoS exposure — not viable for a shared-workstation home network.

2. **Long-running background jobs (scraping, Playwright, cron) need a persistent always-on machine that can't run on shared hosting.** uPress shared hosting caps CPU, has no persistent processes, no cron that runs long jobs, and no Playwright/headless Chromium. waldhomeserver fills this role.

3. **FTPS deploy to uPress requires an allowlisted egress IP.** uPress restricts FTPS port-21 access to a short IP allowlist. The Mac's Bezeq residential ISP IP is not on the allowlist (dynamic IP, not registered). waldhomeserver has a static IP (`46.235.231.114`) registered on the allowlist. HTTPS (port 443) to Cloudflare has no such restriction — so data pushes can originate from either the Mac or the server.

---

## 2. Deploy Pipeline

There are two distinct deployment operations with different transports, different origins, and different cadences.

### 2.1 Code Deploy (UI, CSS, JS, PHP)

**What is deployed:** the `sfa_delivery/` directory — PHP/Slim app, Composer vendor, CSS/JS assets, templates, migrations.

**Transport:** FTPS port 21 (explicit TLS, `prot_c` required), lftp mirror with `--delete`.

**Origin:** waldhomeserver ONLY (Mac's Bezeq IP is port-21-blocked by uPress firewall).

**Script:** `scripts/ftp_deploy_sfa_ui.sh`

**Steps the script performs:**
1. Load `.env` (reads `SFA_FTP_HOST`, `SFA_FTP_PORT=21`, `SFA_FTP_USER`, `SFA_FTP_PASS`, `SFA_FTP_ROOT=/`).
2. Run `composer install --no-dev --optimize-autoloader` in `sfa_delivery/` to produce the production `vendor/` directory (gitignored; never in the repo).
3. Verify `vendor/` exists (guard against silent Composer failure).
4. Run `lftp mirror -R --delete` from the local `sfa_delivery/` tree to `SFA_FTP_ROOT` on uPress, excluding: `.env*`, `.git*`, `logs/`, `tests/`, `.DS_Store`, `*.pyc`, `__pycache__/`.

The `--delete` flag makes the remote tree mirror the local source exactly. This means re-deploying an earlier commit is a rollback: the remote will match the local source, no manual cleanup needed.

**FTPS protocol notes:** uPress requires explicit TLS on port 21 with `prot_c` (data channel protection). Plain FTP and implicit FTPS (port 990) do not work. The protocol is documented in the lean-kit `UPRESS_FTPS_PROTOCOL_v1.0.0.md`.

**Post-deploy smoke checks:**
1. `curl -sI https://sfa.nimrod.bio/ | head -1` → HTTP 200
2. Load `https://sfa.nimrod.bio/` — home renders with module grid.
3. Spot-check a crop page (`/crop-book/<slug>`) and `/market/`.

**When to run:** after any merge to main that changes `sfa_delivery/`, `public_assets/`, or PHP templates. Not automated; runs manually from waldhomeserver.

### 2.2 Data Push (Crop Book and Market Index)

**What is pushed:** rows from Postgres tables (`crops`, `crop_varieties`, `products`, `product_prices`, `crop_field_enrichment`, `crop_attribute`) to the delivery-tier MySQL.

**Transport:** HTTPS POST to `https://sfa.nimrod.bio/api/v1/ingest` (HMAC-authenticated). No IP restriction — Cloudflare accepts connections from any IP.

**Script:** `python -m organic_market_agent.publisher.sfa_ingest_push [--table TABLE] [--dry-run] [--limit N]`

**Two cadences:**
- **Price index (OMA market):** waldhomeserver cron at 06:30 daily. The scraper → normalizer → aggregator → publisher pipeline runs on waldhomeserver; after publish, `sfa_ingest_push.py` pushes the `products` and `product_prices` tables to MySQL.
- **Crop book:** pushed from the Mac on change (not a daily cron). When Nimrod or agents enrich crop data (imports, validation console, enrichment runner), the operator runs `sfa_ingest_push.py --table crops` (or `all`) from the Mac or waldhomeserver.

**Why data can originate from the Mac:** HTTPS to Cloudflare does not require an allowlisted source IP. The HMAC signature provides the authentication guarantee. The Mac pushes crop-book data directly; waldhomeserver pushes price-index data via its daily cron.

---

## 3. First-Deploy Migration Runner

Before data can be pushed to a fresh uPress instance, the MySQL schema must be created. The migration runner is a web-accessible PHP script (`sfa_delivery/migrate.php`) that applies all pending numbered SQL migrations.

**URL:** `https://sfa.nimrod.bio/admin/migrate?token=<ADMIN_MIGRATE_TOKEN>`

**Security:** single-use bearer token in the query string, compared server-side with the `ADMIN_MIGRATE_TOKEN` env var (constant-time comparison). After migrations are applied, the token should be rotated or the `migrate.php` file removed from the deployed tree.

**Migrations applied in order:** `001_schema_migrations.sql` → `002_crops.sql` → `003_products.sql` → `004_crop_field_enrichment.sql` → `005_crop_attribute.sql`.

Each migration's version string is recorded in `schema_migrations` after successful application; re-running the runner skips already-applied versions.

---

## 4. Cron and Automation

### 4.1 waldhomeserver Cron Jobs

| Schedule | Command | Purpose |
|----------|---------|---------|
| 06:30 daily | `python -m organic_market_agent.scheduler.runner` | Market pipeline: collect → normalize → aggregate → publish → ingest push (products + prices) |
| Nightly (time TBD) | Reconciler (`reconciler.py` WP-A) | Postgres ↔ MySQL drift audit; queues corrective re-push if needed |
| Daily | `pg_dump` to `/data/backups/` | Local Postgres backup (30-day retention; same-disk only — see §7.2 debt) |

The scheduler runner (`scheduler/runner.py`) self-gates: it runs every minute via system cron but executes the pipeline only if `is_enabled=True` in the `scheduler_config` table AND the current time matches `run_hour:run_minute` (±1 minute). An overlap guard prevents concurrent runs.

### 4.2 Freshness Guard

`freshness_days` on the `products` table is computed at push time by the publisher (`today - last_price_date`). The delivery-tier index query filters by `freshness_days <= 7` to show only "fresh this week" products. If a source goes down and prices are not scraped for >7 days, its products automatically drop from the index — no manual intervention needed.

### 4.3 Development Workstation Scheduler Policy

The Mac dev workstation must NOT have an automated daily scheduler for the market pipeline. Simultaneous runs from Mac + server against the same DB would corrupt pipeline run tracking. The policy is documented in `documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md`: on the Mac, all ingestion runs are manual (via the Flask admin UI or CLI) and on-demand only.

---

## 5. Security Model

### 5.1 HMAC-SHA256 Ingest Authentication

Every `POST /api/v1/ingest` request carries `X-SFA-Auth: sha256=<hmac_hex>`. The HMAC is computed over the raw request body bytes using the shared secret `SFA_INGEST_HMAC_SECRET` (32 bytes, base64-encoded, from `openssl rand -base64 32`).

On the delivery tier, `HmacAuthMiddleware.php` verifies the signature using PHP's `hash_equals()` (constant-time comparison, prevents timing attacks). Mismatch → HTTP 401; no body processing.

The secret is identical on waldhomeserver (in the backend `.env`) and on uPress (in the delivery `.env`). Rotation policy: annually or immediately on suspected leak. Rotation requires updating both env files and confirming the push pipeline still works.

### 5.2 FTPS IP Allowlist

uPress restricts outbound FTPS (port 21) to an IP allowlist. Registered entries:
- waldhomeserver: `46.235.231.114` (static)
- Mac dev: registered separately (may be a dynamic Bezeq IP; if changed, must be updated at uPress firewall)

This allowlist is enforced at the uPress network level, not in application code. It cannot be bypassed with software changes on our side.

### 5.3 FTPS Explicit TLS (`prot_c`)

The uPress FTPS server requires explicit TLS on port 21 with data channel protection (`PROT P` / `prot_c` in lftp). Control channel and data channel are both encrypted. Plain FTP or implicit FTPS (port 990) are not accepted.

### 5.4 Delivery-Tier `.env` Security

The `.env` file on uPress contains database credentials and the HMAC secret. Security hardening:
- `chmod 600` on `.env` (PHP-FPM user reads; nginx cannot serve it).
- `.htaccess` blocks direct HTTP access to `.env` (returns 403).
- Secrets never committed to git. `.env.example` lists required keys without values.
- No KMS available on shared hosting — `.env` is the only secret storage available.

### 5.5 Security Blocks in `.htaccess`

The delivery-tier `.htaccess` returns HTTP 403 for direct HTTP access to:
`/.env`, `/composer.{json,lock}`, `/migrations/`, `/app/`, `/tests/`, `/vendor/`, `/logs/`

All HTTP is forced to HTTPS by an `.htaccess` rewrite rule (defense-in-depth; Cloudflare also enforces HTTPS).

### 5.6 Ingest Idempotency (Anti-Replay)

The `idempotency_key` in every ingest payload prevents double-application of the same push. If the same key arrives twice, the controller returns `{"duplicate": true}` with HTTP 200 without re-applying rows. This protects against transient network retries replaying the same payload.

The `ingest_log` table retains keys for 30 days (opportunistic pruning: ~1% of requests run a `DELETE ... WHERE applied_at < NOW() - INTERVAL 30 DAY`).

### 5.7 S003 Read-Only Delivery (Current)

In the S003 scope (current production), the delivery tier has no user write paths. All writes flow only through the HMAC-signed publisher push. There is no user authentication, no user data in MySQL, no community features. This minimizes attack surface.

S004 will introduce JWT-gated user writes (calculator saves, favorites). That will be a separate decision artifact with its own security design.

---

## 6. Docker Port Canon (Shared Workstation)

The Mac is a shared development workstation running multiple Docker-based projects. Port assignments are canonical and must not conflict:

| Port | Container / Service | Project |
|------|---------------------|---------|
| **5433** | `oma-postgres` (PostgreSQL) | SmallFarmsAgents |
| **5001** | Admin Flask server | SmallFarmsAgents |
| **8081** | Public viewer (static HTML/JSON) | SmallFarmsAgents |
| 5432 | PostgreSQL | Other projects (not SFA) |
| 8080 | Frontend | TikTrack (not SFA) |

Never use ports 5432 (conflicts with other Postgres), 8080 (TikTrack frontend), or 3306 (MySQL default — uPress MySQL is not exposed locally).

Docker compose file for the local Postgres: `docker-compose.yml` in the repo root. The service is named `oma-postgres`; connection string: `postgresql://postgres:postgres@localhost:5433/organic_market_agent`.

---

## 7. Operational Constraints and Known Debt

### 7.1 Crop Book Data Push: Manual, Not Cron

The crop book data push is intentionally NOT a daily cron job. Crop data changes are episodic — re-pushing identical artifacts daily would be wasteful and would generate `ingest_log` churn. The operator runs `sfa_ingest_push.py` manually after each enrichment or import session.

Tracking item: `documentation/KNOWN_DEBT.md` §A.2 — "Daily cron auto-publish for crop book." Promoted when a daily-changing crop data source (e.g. live market prices integrated into the crop book) is introduced.

### 7.2 Backup Posture (Risk — flagged 2026-05-30)

The home server takes daily local `pg_dump` backups to `/data/backups/` with 30-day retention. However:
- **Same disk as data** — not offsite.
- **No restore verification** — backups are untested.
- **Blast-radius mitigation already in place:** the price index is reconstructible by re-scraping; the crop book's canonical source is the git repo (re-seedable). A home-server total loss would not lose authored data — only running state.

Recommended follow-up (not blocking): add offsite copy of price-index DB dump + periodic restore test. Tracked in `KNOWN_DEBT.md` as a server-infra item.

### 7.3 uPress MySQL Backups

uPress takes automatic nightly backups of the entire site as part of their service. For belt-and-suspenders, a `mysqldump` periodic export via SSH cron from waldhomeserver is deferred to a post-cutover ops WP.

### 7.4 Code Deploy Is Not Automated

There is currently no CI/CD pipeline for the `sfa_delivery/` code deploy. Merges to main do not automatically trigger an FTPS deploy. The operator runs `bash scripts/ftp_deploy_sfa_ui.sh` manually from waldhomeserver after each significant merge.

### 7.5 PHP Migration Runner Security

The `migrate.php` web-accessible migration runner (`/admin/migrate?token=...`) is intended for first-deploy use only. It should be rotated to an unguessable token (or the file removed) after migrations are applied. This is a known low-severity operational discipline item.

### 7.6 Waldhomeserver Home Server Reliability

waldhomeserver is a shared home server, not a managed cloud instance. It has:
- No SLA or uptime guarantee.
- No automatic restart of the daily cron if the machine is rebooted.
- Residential internet connection (Bezeq); periods of outage are expected.

Impact on users: if waldhomeserver is down, price-index data on `sfa.nimrod.bio` becomes stale after 7 days (`freshness_days > 7`) and products drop from the market index. The crop book is unaffected (it is near-static data pushed from the Mac; the delivery tier serves it from MySQL with no runtime dependency on waldhomeserver).

### 7.7 Mobile Responsive Tuning (KNOWN_DEBT.md §A.3)

The crop book SPA was originally built desktop-first. Mobile parity is best-effort. The UX/UI overhaul WP (WP-B, team_35) explicitly addresses mobile-first design. This is a MEDIUM severity item expected to be consumed by WP-B.

### 7.8 Credentials Management

There is no centralized secrets manager or vault. All secrets live in `.env` files on each machine:
- Mac: `.env` in repo root (gitignored).
- waldhomeserver: `.env` in the deployment directory.
- uPress: `.env` in the site root (FTPS-uploaded; `chmod 600`).

Rotation checklist documented in `documentation/05-admin-and-operations/FTPS_CRED_ROTATION_SYNC_RUNBOOK.md`. The HMAC secret must be identical on waldhomeserver and uPress and rotated in lockstep.

---

## 8. Troubleshooting Quick Reference

### 8.1 Pipeline Alerts

All pipeline alerts are persisted in the `pipeline_alerts` table (Postgres, waldhomeserver). Access via Flask admin at `/alerts` or SQL export. Alert prefix taxonomy:

| Prefix | Meaning |
|--------|---------|
| `[OPS:process_restart]` / `[OPS:admin_stop_all]` | Expected lifecycle events after admin restart / stop-all |
| `[PIPELINE:failure]` / `[PIPELINE:missing_run]` | Real worker errors |
| `[SCHEDULER:…]` | Cron runner events (overlap guard, time gate, disabled) |
| `[SIMULATION:test]` | Pytest or `triggered_by=test` runs — filter after review |
| `[MAINTENANCE:…]` | Background maintenance finished or failed (renormalize, refresh) |
| `[AGG_PRICE_RULE:two_source_price_spread_gt_100pct]` | Publish suppressed: 2-source spread >100% |
| `[AGG_PRICE_RULE:multi_source_outlier_gt_2sigma]` | Publish suppressed: 3+-source outlier >2σ |

### 8.2 Common Operational Scenarios

| Symptom | Likely cause | Resolution |
|---------|-------------|-----------|
| Market prices stale on sfa.nimrod.bio | waldhomeserver cron not running | Check `scheduler_config.is_enabled`; restart scheduler |
| New products not appearing | Below publish threshold (<2 observations, <2 sources) | Add aliases; check scope-skip rules |
| Crop book data stale after schema migration | New fields not yet pushed | Run `sfa_ingest_push.py --table crops` from Mac |
| `/api/v1/health` returns `db: fail` | MySQL connection issue on uPress | Check uPress DB status; check `.env` credentials |
| Ingest push returns 401 | HMAC secret mismatch | Verify `SFA_INGEST_HMAC_SECRET` matches on both ends |
| Ingest push returns 200 `{duplicate: true}` | Same idempotency key reused (expected) | Normal on retry; no action needed |
| Admin shows old data | Stale Flask server process | `bash scripts/restart_all_servers.sh restart` |
| `alembic current` not at head | Missing migrations | `python3 -m alembic upgrade head` |
| Tests fail with `OperationalError` | PostgreSQL container not running | `docker-compose up -d` |
| FTPS deploy fails | Egress IP not allowlisted or wrong credentials | Verify waldhomeserver IP; check uPress allowlist; check `.env` FTPS creds |

### 8.3 Server Management Commands

```bash
# Flask admin server (port 5001) — waldhomeserver or Mac
bash scripts/admin_server.sh start|stop|restart|status

# Public viewer (port 8081) — local static HTML server for dev
bash scripts/viewer_server.sh start|stop|restart|status

# Both servers
bash scripts/restart_all_servers.sh restart

# Database health check
python -m organic_market_agent.db.check

# Push all tables to delivery tier (dry run first)
python -m organic_market_agent.publisher.sfa_ingest_push --dry-run
python -m organic_market_agent.publisher.sfa_ingest_push --table all

# UI code deploy (from waldhomeserver)
bash scripts/ftp_deploy_sfa_ui.sh
```

---

## 9. Environment Variables Reference

| Variable | Where used | Purpose |
|----------|-----------|---------|
| `DATABASE_URL` | Python (all) | PostgreSQL connection string (`postgresql://...@localhost:5433/...`) |
| `SFA_INGEST_URL` | `sfa_ingest_push.py` | Target ingest endpoint (`https://sfa.nimrod.bio/api/v1/ingest`) |
| `SFA_INGEST_HMAC_SECRET` | `sfa_ingest_push.py` + `HmacAuthMiddleware.php` | 32-byte base64 HMAC secret (must match both ends) |
| `ADMIN_SECRET_KEY` | Flask admin | Session signing key |
| `ADMIN_MIGRATE_TOKEN` | `migrate.php` (uPress) | One-time migration runner auth token |
| `SFA_FTP_HOST` | `ftp_deploy_sfa_ui.sh` | uPress FTPS hostname |
| `SFA_FTP_PORT` | `ftp_deploy_sfa_ui.sh` | `21` (explicit TLS) |
| `SFA_FTP_USER` / `SFA_FTP_PASS` | `ftp_deploy_sfa_ui.sh` | uPress FTPS credentials |
| `SFA_FTP_ROOT` | `ftp_deploy_sfa_ui.sh` | FTPS target path on uPress (typically `/`) |
| `SFA_DB_NAME` (uPress PHP .env) | `IngestController.php` / PDO | MySQL database name (`sfanms2u_SFAUserUiDB`) |
| `SFA_DB_USER` / `SFA_DB_PASS` (uPress PHP .env) | PDO | MySQL credentials |
| `NORMALIZER_BASELINE_JSON` | Flask admin dashboard | Optional baseline path for delta display |
| `RAW_FILES_ROOT` | Collectors | Raw asset storage directory |
| `AOS_ACTOR_API_KEY` | AOS messaging | Actor key for AOS hub API (see `reference_aos_actor_key.md`) |

---

## 10. Deployment Lifecycle Checklist

For each release that changes the delivery tier:

- [ ] Code changes merged to main in `sfa_delivery/` or `public_assets/`
- [ ] If schema changed: new numbered migration SQL file added (`sfa_delivery/migrations/XXX_*.sql`)
- [ ] `composer.lock` updated if new PHP deps added
- [ ] `vendor/` NOT committed (gitignored; deploy script runs `composer install`)
- [ ] Deploy from waldhomeserver: `bash scripts/ftp_deploy_sfa_ui.sh`
- [ ] If schema migration: run `https://sfa.nimrod.bio/admin/migrate?token=<TOKEN>` once
- [ ] Post-deploy smoke: curl HTTP 200; load site; spot-check crop page and market page
- [ ] If crop data changed: `python -m organic_market_agent.publisher.sfa_ingest_push --table crops`
- [ ] Monitor `/api/v1/health` for `db: ok`

For rollback: re-deploy the previous known-good commit's `sfa_delivery/` tree (lftp `--delete` makes it idempotent).

---

## 11. Future S004 Infrastructure Considerations

When opening S004 (calculator persistence + community features), the following infrastructure changes are anticipated:

- **JWT authentication** — a 50-line JWT helper is already designed (deferred to S004). Routes for user writes will be separate from the current read-only surface.
- **User tables in MySQL** — `user_favorites`, `user_calculator_inputs`, per-user state. Separate decision and migrations from current S003 schema.
- **Community submission tables** — comments, crop corrections. Separate decision; separate auth scheme.
- **Potential host migration** — if uPress shared hosting becomes a constraint (user writes, persistent sessions, connection pools), migration to a managed LAMP host (DigitalOcean, Hetzner, A2) is straightforward given the portability-first architecture (§12 in doc 06). No uPress-specific bindings exist.

Pre-S004 operational items to resolve (from `documentation/KNOWN_DEBT.md`): AOS actor API key provisioning (B.1); GCR status updates (B.2); mobile responsive debt (A.3); Tend cross-year ingestion for calculator data (C.1).

---

*Document 07 — authored 2026-06-03 by team_100 for the SFA Product Information Pack.*
*Sources: sfa-delivery-tier.md; UI_DEPLOY_RUNBOOK.md; FTPS_CRED_ROTATION_SYNC_RUNBOOK.md; 08-troubleshooting/README.md; KNOWN_DEBT.md; 05-admin-and-operations/README.md; sfa_ingest_push.py.*
