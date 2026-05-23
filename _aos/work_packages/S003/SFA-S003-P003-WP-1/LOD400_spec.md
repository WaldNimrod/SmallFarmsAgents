# LOD400 — SFA-S003-P003-WP-1 — uPress Provisioning + Cloudflare DNS for sfa.nimrod.bio

**Date:** 2026-05-23 (v2 — rewritten after uPress docs research)
**Author:** team_100
**WP:** SFA-S003-P003-WP-1 — uPress dedicated subdomain provisioning
**Type:** LOD400_SPEC — admin/provisioning WP (team_00 self-executes via uPress + Cloudflare dashboards)
**Status:** ELIGIBLE / L-GATE_E PASS
**Builder:** team_00 (Principal — admin tasks at uPress + Cloudflare dashboards)
**Validator:** team_00 (self-attest on completion)
**Effort:** SMALL (~30-60 min team_00 work, no support ticket needed)
**Blocks:** WP-2, WP-3, WP-4

---

## §1 Reality check (uPress docs research 2026-05-23)

Reviewed official uPress knowledgebase (`support.upress.io`). Reality:

| Capability | Status | Source |
|------------|--------|--------|
| Subdomain creation via dashboard | ✅ "My Sites" → "All sites" → "Create a new site" | [support.upress.io/getting-started/how-do-i-create-sub-domain/](https://support.upress.io/getting-started/how-do-i-create-sub-domain/) |
| Subdomain = WP install (auto) | ⚠ **Yes — uPress's "site" model installs WordPress automatically.** Subdomain is treated as a fully-separate site (own backups, plugins, updates). | same |
| Multiple MySQL DBs per site | ✅ Via "Database Management" → "Add New" | [support.upress.io/dev/create-new-database/](https://support.upress.io/dev/create-new-database/) |
| FTP account per site/folder | ✅ "Manage FTP Accounts" — can grant root or folder-restricted | [support.upress.io/dev/how-to-create-an-ftp-account-in-upress/](https://support.upress.io/dev/how-to-create-an-ftp-account-in-upress/) |
| PHP version per site | ✅ User controls PHP version; uPress doesn't restrict to whitelist | uPress FAQ |
| Cron jobs | ✅ Per-site cron config | [support.upress.io/dev/how-to-add-cron-jobs-to-your-website/](https://support.upress.io/dev/how-to-add-cron-jobs-to-your-website/) |
| PhpMyAdmin | ✅ Per-site | [support.upress.io/dev/how-to-login-phpmyadmin/](https://support.upress.io/dev/how-to-login-phpmyadmin/) |
| GIT via file manager | ✅ Web UI | [support.upress.io/advanced/manage-git-via-file-manager/](https://support.upress.io/advanced/manage-git-via-file-manager/) |
| Cache management | ✅ Per-site cache clear | [support.upress.io/dev/how-to-clear-cache/](https://support.upress.io/dev/how-to-clear-cache/) |
| .htaccess / mod_rewrite | ✅ Standard LAMP — uPress runs Apache/nginx with .htaccess support |  |
| SSH access | ❌ Not documented (FTP only) | inferred from docs absence |
| Composer install via shell | ❌ Not directly. Workaround: run `composer install` locally and FTP `vendor/` | inferred |
| "Raw PHP hosting" (no WP) | ❌ Not officially. uPress is positioned as managed WP. | inferred |

## §2 The architectural adjustment — "minimal WP shell + custom app"

Since uPress auto-installs WP on every new "site", we **co-exist** with WP rather than fight it:

```
sfa.nimrod.bio (uPress new site)
├─ wp-admin/, wp-content/, wp-includes/, ...        ← uPress's WP install. We leave it alone.
├─ wp-content/mu-plugins/sfagent-bypass.php         ← tiny mu-plugin: hooks template_redirect,
│                                                      detects /api/* and /crop-book/* and /market/*
│                                                      paths, dispatches to our Slim app, exits.
├─ app/                                              ← our Slim PHP app (uploaded via FTP)
│   ├─ vendor/                                       ← composer dependencies, uploaded as tarball
│   ├─ src/                                          ← Slim controllers
│   ├─ migrations/                                   ← numbered SQL files
│   └─ public/index.php                              ← Slim entry point
└─ .htaccess                                         ← rewrites: /crop-book/* /market/* /api/*
                                                       → /app/public/index.php (Slim handles)
                                                       Everything else → WP (unchanged)
```

**Why this works:**
- uPress's backup/security/auto-update systems see a normal WP install and stay happy.
- Our app lives under `/app/` (or `/sfa/`), routed via `.htaccess` rewrites.
- WP admin remains accessible (we may use it later for: WooCommerce if we add e-commerce, WP user auth if we want SSO, plugin-mediated features).
- Standard LAMP → portable to any host (just copy `/app/` + DB dump; ignore the WP files when moving).

**Honest trade-off:** We're paying for a WP install we mostly don't use. Acceptable — uPress charges per site/plan tier, not per-feature.

## §3 Step-by-step Action Guide for team_00

### Phase A — uPress dashboard (estimated 15-20 min)

#### A.1 Create the subdomain "site"
1. Login → **"My Sites"** → **"All sites"**
2. Click **"Create a new site"** (`צור אתר חדש`)
3. Domain: enter `sfa.nimrod.bio`
4. Confirm plan choice (subdomain may count as one of N sites in your plan, or may have a small extra fee — uPress will indicate)
5. Submit. uPress provisions the new site (this can take a few minutes — they email when ready).

#### A.2 Create the MySQL database (after site is provisioned)
1. Select the new `sfa.nimrod.bio` site from "My Sites"
2. **"Overview"** tab → **"Database Management"** → **"Add new"**
3. Click green **"Add New"** button. Fill:
   - **Database Name**: `sfa_main` (or your choice)
   - **Username**: `sfa_app`
   - **Password**: generate strong, save it
4. Click **"Create"**
5. Save credentials in your `.env` (or a manual secrets file — NOT in git)

#### A.3 Create a dedicated FTP account (if you want isolation from main site's FTP)
1. Site overview → **"Manage FTP Accounts"**
2. **"Create new FTP account"**
3. Recommend: limit to the site root directory; full access within it
4. Save FTP credentials

*Optional*: skip this if you prefer to use existing nimrod.bio FTP creds (the same ones that work today for the publisher). uPress may allow same FTP user for both sites — verify in the FTP accounts list.

#### A.4 Confirm PHP version
1. Site overview → look for **"PHP Version"** or **"Settings"**
2. Set to **PHP 8.1 or higher** (8.2 ideal)
3. Verify extensions enabled (the standard set we need — pdo, pdo_mysql, mbstring, json, curl, intl — are all standard in any modern PHP install)

### Phase B — Cloudflare dashboard (estimated 5-10 min)

#### B.1 Add subdomain DNS
1. Cloudflare dashboard → select `nimrod.bio` zone → **"DNS"** → **"Records"**
2. **"Add record"**:
   - Type: `CNAME`
   - Name: `sfa`
   - Target: same target as your existing `www` record (likely uPress's CNAME — check `www` row to confirm)
   - Proxy status: **Proxied** (orange cloud)
   - TTL: Auto
3. Save.

#### B.2 Validate
After ~30 seconds (CF + uPress propagation):
```bash
curl -sSI https://sfa.nimrod.bio/
# Expect: HTTP 200 (or 301 redirect to a default WP page) — meaning DNS + TLS + uPress origin are alive
```

### Phase C — Initial validation (after Phase A + B done)

#### C.1 Verify uPress site is alive
- Open `https://sfa.nimrod.bio/` in browser — should see default WP page (sample post or hello world)

#### C.2 Verify FTP access
```bash
# Test FTP login (Mac, lftp or FileZilla)
# Use the FTP credentials from A.3 (or existing nimrod.bio creds if shared)
# Should be able to list the site root and see wp-admin/, wp-content/, wp-includes/, etc.
```

#### C.3 Verify MySQL access
- Site overview → **PhpMyAdmin** → login with credentials from A.2
- See empty DB `sfa_main` ready for our migrations

#### C.4 Verify HTTPS
- Browser shows green padlock at `https://sfa.nimrod.bio/`

---

## §4 Output deliverable

Create `_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_2026-05-XX.md` with:

```yaml
---
id: UPRESS_PROVISIONING_RESULTS_SFA_SUBDOMAIN
type: PROVISIONING_REPORT
from: team_00
to: team_100
date: 2026-05-XX
related_wp: SFA-S003-P003-WP-1
---

# uPress Provisioning Results — sfa.nimrod.bio

## Site
- subdomain: sfa.nimrod.bio
- uPress site path: /home/nimrodbi/domains/sfa.nimrod.bio/public_html  (verify from FTP)
- PHP version: 8.X
- WP install: default (uPress auto-installed) — kept for co-existence

## DB
- name: sfa_main
- host: localhost  (or as uPress provides)
- user: sfa_app
- password: <in .env as SFA_DB_PASSWORD — not in git>

## FTP
- using: existing nimrod.bio creds  OR  dedicated sfa.nimrod.bio account
- host: <upress FTP host>
- root path: /

## DNS
- sfa.nimrod.bio → CNAME → <upress target>, CF proxy ON
- TLS: active (Let's Encrypt via uPress or CF Universal SSL)

## Validation
- [x] https://sfa.nimrod.bio/ returns HTTP 200 (default WP page)
- [x] FTP login + ls of site root works
- [x] PhpMyAdmin login + see empty DB
- [x] HTTPS green padlock

## Notes / surprises
- (any unexpected uPress behavior, costs, restrictions)
```

---

## §5 Acceptance Criteria

| AC | Criterion | Evidence |
|----|-----------|----------|
| AC-01 | `https://sfa.nimrod.bio/` resolves and returns 200 (default WP page acceptable) | `curl -sSI https://sfa.nimrod.bio/` |
| AC-02 | FTP login + ls returns site root with WP files | manual confirm |
| AC-03 | MySQL DB exists, accessible via PhpMyAdmin | manual confirm |
| AC-04 | DB credentials stored in `.env` (not in git) — verify by `grep SFA_DB .gitignore` (.env should be ignored) | env file present, gitignored |
| AC-05 | Cloudflare CNAME proxied (orange cloud) for `sfa.nimrod.bio` | CF dashboard screenshot or `dig sfa.nimrod.bio` shows CF IPs |
| AC-06 | PHP version ≥ 8.1 confirmed (uPress settings page OR upload `<?php echo phpversion();` test file, fetch, delete) | screenshot or HTTP response |
| AC-07 | Results doc filed at `_COMMUNICATION/team_00/UPRESS_PROVISIONING_RESULTS_*.md` with all sections populated | file exists |

---

## §6 What this enables (next WPs)

After WP-1 LOD500_LOCKED:
- **WP-2** unblocks: team_100 authors detailed LOD400 for Slim app skeleton + migrations + ingest API, based on confirmed PHP version + DB version + paths. Dispatched to sfa_build.
- **WP-3**: ditto, post-WP-2 + team_35 design.
- **WP-4**: publisher migration — uses the DB + ingest endpoint that WP-2 builds.

---

## §7 What NOT to do (anti-patterns from today's session)

- ❌ Do NOT touch the WP install on the new subdomain. Leave wp-admin/, wp-content/, wp-includes/ alone (uPress backups assume normal WP structure).
- ❌ Do NOT install plugins on the new subdomain unless we explicitly need them (more WP plugins = more attack surface + uPress security scan noise).
- ❌ Do NOT put our app code in wp-content/ (uPress treats that as theirs; future updates may overwrite). Use a separate `/app/` directory at site root.
- ❌ Do NOT edit anything on the existing www.nimrod.bio site as part of this WP — completely separate.

---

## §8 Cross-references

- Decision record: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- uPress KB: subdomain creation [support.upress.io/getting-started/how-do-i-create-sub-domain/](https://support.upress.io/getting-started/how-do-i-create-sub-domain/)
- uPress KB: DB creation [support.upress.io/dev/create-new-database/](https://support.upress.io/dev/create-new-database/)
- uPress KB: FTP account [support.upress.io/dev/how-to-create-an-ftp-account-in-upress/](https://support.upress.io/dev/how-to-create-an-ftp-account-in-upress/)
- uPress KB: PhpMyAdmin [support.upress.io/dev/how-to-login-phpmyadmin/](https://support.upress.io/dev/how-to-login-phpmyadmin/)
- uPress KB: Cron jobs [support.upress.io/dev/how-to-add-cron-jobs-to-your-website/](https://support.upress.io/dev/how-to-add-cron-jobs-to-your-website/)
- uPress KB: GIT via file manager [support.upress.io/advanced/manage-git-via-file-manager/](https://support.upress.io/advanced/manage-git-via-file-manager/)
- uPress KB: Cache clear [support.upress.io/dev/how-to-clear-cache/](https://support.upress.io/dev/how-to-clear-cache/)

---

*LOD400 v2 — rewritten 2026-05-23 after uPress docs research. Replaces v1 "ask uPress support" approach with concrete self-service UI flow.*
