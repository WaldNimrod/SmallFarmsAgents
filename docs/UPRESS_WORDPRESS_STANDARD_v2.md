# uPress + WordPress Development Standard

**Version:** 2.0
**Date:** 2026-04-08
**Scope:** WordPress development, hosting, file/DB access, automation, and deployment on uPress — applicable to **all projects** in this environment.
**Out of scope:** Team structure, gate/milestone procedures, Cursor agent workflows — governed by separate project-management documents.

**Lineage:** Synthesized from SmallFarmsAgents Playbook v1.0 (2026-04-02, production on nimrod.bio) and Eyal Amit 2026 Standard v1.0 (2026-04-08, staging on eyalamit.co.il), with cross-project synthesis and organizational decisions by Team 100.

---

## 1. Platform Lock — uPress as Organizational Default

| Decision | Detail |
| --- | --- |
| **Default hosting** | **uPress** (upress.co.il) — managed WordPress hosting, Israel-based, for all WordPress projects unless a documented exception exists at project level. |
| **Canonical documentation** | **Hebrew:** [support.upress.co.il](https://support.upress.co.il/) — **English:** [support.upress.io](https://support.upress.io/) — **Features:** [upress.co.il/features](https://www.upress.co.il/features) |

**Per-project requirement:** Every project must document in its environment file: server number (`s{NNN}`), staging/production domains, and a reference to the credentials file.

### What uPress Provides

- Managed WordPress with auto-updated PHP
- Built-in SSL (auto-renewed), CDN, daily backups
- Dev/sandbox environments: [upress.co.il/features/sandboxes](https://www.upress.co.il/features/sandboxes/)
- Premium plugin library: [upress.co.il/features/wordpress-premium-plugins-library](https://www.upress.co.il/features/wordpress-premium-plugins-library/)
- FTP accounts via panel: [support.upress.co.il/dev/create-new-ftp](https://support.upress.co.il/dev/create-new-ftp/)
- phpMyAdmin via panel: [support.upress.co.il/dev/how-to-login-myadmin](https://support.upress.co.il/dev/how-to-login-myadmin/)
- `wp-autologin.php` for cPanel-based auto-login

### What Is NOT Available

| Resource | Status | Workaround |
| --- | --- | --- |
| SSH / SFTP (port 22) | Blocked on shared hosting | Use FTP/FTPS (port 21) |
| WP-CLI on server | Not installed | Use local Docker + WP-CLI, or REST API, or functions.php hooks |
| Direct MySQL (port 3306) | Blocked remotely (DB_HOST = localhost) | Use phpMyAdmin (browser) or `$wpdb` in PHP |
| PHP execution in `uploads/` | Blocked | Place code only in theme/plugin/mu-plugins directories |
| Server-level cron | Not available | Use WP-Cron or external cron service |

---

## 2. FTP — Connection Standard

| Parameter | Standard |
| --- | --- |
| **Port** | **21** — organizational default for all uPress FTP connections. |
| **FTP account setup** | Per uPress documentation: [create FTP](https://support.upress.co.il/dev/create-new-ftp/) / [use FTP](https://support.upress.co.il/dev/how-to-use-ftp/) |

### 2.1 TLS Policy (Production vs Staging)

| Environment | Policy |
| --- | --- |
| **Production** | **FTPS+TLS is the default.** uPress production servers enforce TLS on data channels. Use the `ReusedSessionFTP_TLS` class (below). Connections without TLS should be treated as a configuration error. |
| **Staging / Sandbox** | uPress staging environments may not have SSL certificates. **Test TLS first**; if it fails, plain FTP is acceptable **during development only** — document the exception. Upgrade to FTPS when staging gets SSL. |
| **General rule** | Always attempt FTPS first. Fall back to plain FTP only when TLS demonstrably fails on that specific server, and document the reason. |

### 2.2 Python FTP Client — Canonical Implementation

uPress production servers require TLS session reuse on data channels. Standard Python `ftplib.FTP_TLS` fails because it does not pass the control socket's TLS session to new data sockets. This subclass fixes it:

```python
import ftplib, os, io
from dotenv import load_dotenv

load_dotenv(".env.upress")

class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    """uPress-compatible FTPS client with TLS session reuse on data channels."""
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session
            )
        return conn, size

def get_ftp(use_tls=True):
    """Connect to uPress FTP. Set use_tls=False only for staging without SSL."""
    if use_tls:
        ftp = ReusedSessionFTP_TLS()
    else:
        ftp = ftplib.FTP()
    ftp.connect(os.getenv("UPRESS_SFTP_HOST"), int(os.getenv("UPRESS_SFTP_PORT", 21)))
    ftp.login(os.getenv("UPRESS_SFTP_USER"), os.getenv("UPRESS_SFTP_PASS"))
    if use_tls:
        ftp.prot_p()
    return ftp
```

### 2.3 Deployment Script Requirements

All FTP deployment scripts must include:
- **`--dry-run` flag** — list files that would be uploaded without actually uploading
- **Explicit remote path** — never rely on implicit CWD; always specify full remote target
- **File name validation** — skip files with newlines or non-printable characters in names; log a warning for manual correction
- **Backup before overwrite** — for critical files (functions.php, wp-config.php), download the current version as `.bak` before uploading

---

## 3. FTP Accounts — Standard and Overrides

| Rule | Detail |
| --- | --- |
| **Default** | One standard FTP account per project: access to the WordPress root (or the path assigned by uPress), port 21, credentials stored in `.env.upress`. |
| **Per-project overrides** | Additional FTP accounts or restricted paths are allowed when the project requires it (e.g., a static hub directory, a separate uploads path). **Must be documented** in the project's runbook or environment file: purpose, path, who holds the password. |
| **Hub-specific paths** | When a static client hub exists outside WordPress (see Section 9), a separate FTP path is allowed relative to the account root. |

### FTP Root Variance

- **Some uPress accounts:** FTP root = WordPress root (no `public_html/` prefix). Confirmed in SmallFarmsAgents.
- **Other accounts:** FTP root may include `public_html/` or a subdirectory. Confirmed in Eyal Amit.
- **Rule:** Always verify and document the correct remote path. Never assume. Use `--dry-run` on first deploy.

---

## 4. Database Access

### 4.1 Available Channels

| Channel | Capability | When to Use |
| --- | --- | --- |
| **phpMyAdmin** (browser) | Full DDL + DML access | Complex queries, inspecting structure, emergency fixes |
| **`$wpdb` in PHP** (functions.php hooks) | Full server-side DB access | Bulk content updates, serialized option changes, one-time migrations |
| **REST API** | WordPress-mediated CRUD | Content/settings that map to WP entities (pages, posts, comments, options) |
| **WP-CLI** (local Docker only) | Full WordPress CLI | Local testing, WXR import/export, plugin management before deploy |

### 4.2 Safety Rules

| Rule | Detail |
| --- | --- |
| **No SQL REPLACE on serialized data** | WordPress stores many settings as serialized PHP arrays in `wp_options`. Using SQL `REPLACE()` corrupts serialization lengths. Always use `get_option()` / `update_option()` in PHP, or JSON-encode → string-replace → JSON-decode. |
| **Table prefix** | Never hardcode `wp_`. Every uPress installation has a unique prefix (e.g., `qvj_`). Read it from `wp-config.php` or use `$wpdb->prefix` in PHP. Document it in `.env.upress` as `UPRESS_DB_TABLE_PREFIX`. |
| **Risk audit for direct SQL** | Before running destructive SQL (DELETE, UPDATE without WHERE, DROP) or one-time PHP hooks on a production site, document: what, why, rollback plan. Default posture: low-risk operations only. |
| **Approved query templates** | Maintain a set of approved read-only queries in the project runbook (active plugins, comment counts, post search). Destructive queries require explicit approval. |

### 4.3 phpMyAdmin Configuration

```
UPRESS_PHPMYADMIN_URL=https://s-il-{NNN}-{code}.upress.io/{token}/
UPRESS_DB_NAME={db_name}
UPRESS_DB_USER={db_user}
UPRESS_DB_PASS={db_pass}
UPRESS_DB_TABLE_PREFIX={prefix}_
```

Per uPress docs: [DB connection details](https://support.upress.co.il/dev/obtaining-database-details/) / [phpMyAdmin login](https://support.upress.co.il/dev/how-to-login-myadmin/)

### 4.4 Common Approved Queries

```sql
-- Find table prefix
SHOW TABLES LIKE '%options';

-- Check active plugins
SELECT option_value FROM {prefix}_options WHERE option_name = 'active_plugins';

-- Check theme mods
SELECT option_value FROM {prefix}_options WHERE option_name = 'theme_mods_{theme-slug}';

-- Find posts containing a string
SELECT ID, post_title, post_type, post_status
FROM {prefix}_posts WHERE post_content LIKE '%search_string%';

-- Count comments by status
SELECT comment_approved, COUNT(*) AS cnt
FROM {prefix}_comments GROUP BY comment_approved;

-- Check widget settings
SELECT option_value FROM {prefix}_options WHERE option_name LIKE 'widget_%';
```

---

## 5. Environments — Staging vs Production

| Rule | Detail |
| --- | --- |
| **TLS/FTP may differ** | Staging and production on the same uPress account may have different SSL/TLS configurations. Never assume one environment's behavior applies to the other without testing. |
| **Production hardening** | After final deployment and lock: revoke unnecessary Application Passwords, disable debug endpoints, remove one-time hooks, restrict REST API access if not needed, review file permissions. |
| **Development mode** | During active development: maximize agent capabilities — REST API with Application Password, automated testing, FTP deployment scripts, phpMyAdmin access. |
| **uPress sandboxes** | Per [uPress sandbox docs](https://www.upress.co.il/features/sandboxes/), staging environments are separate WordPress instances. Content sync from production to staging is available via uPress panel import: [import to sandbox](https://support.upress.co.il/dev/import-to-sandbox/). |

---

## 6. Local Docker Environment — Strongly Recommended

| Decision | Detail |
| --- | --- |
| **Status** | **Strongly recommended** for all projects with custom PHP, theme development, or plugin work. Optional for simple content-only sites. |
| **Rationale** | Provides WP-CLI, Xdebug, safe testing environment, and PHP version alignment with uPress — without risking the live site. One-time setup investment with ongoing benefits. |

### 6.1 Minimum Stack

```yaml
# docker-compose.yml (reference structure)
services:
  wordpress:
    build: .
    ports: ["8080:80"]
    volumes:
      - ./site/wp-content:/var/www/html/wp-content
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_NAME: wordpress
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress
  db:
    image: mariadb:10.11
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress
      MYSQL_ROOT_PASSWORD: root
```

### 6.2 Requirements Per Project

Every project using Docker must document:
- `docker compose build` / `docker compose up` commands
- WP-CLI verification: `docker compose exec wordpress wp --info`
- PHP version alignment with uPress production
- Volume mapping for `wp-content/` (themes, plugins, uploads)

### 6.3 Reference Implementation

The Eyal Amit 2026 project provides a complete Docker setup:
- `local/docker-compose.yml`, `local/Dockerfile.wordpress`
- `local/README.md` with setup instructions
- `local/verify_local_wp_cli.sh` for validation

---

## 7. REST API and Application Passwords

### 7.1 Policy

| Phase | Policy |
| --- | --- |
| **Development / Staging** | **Maximize capabilities:** REST API with Application Password, automated scripts, full CRUD for agents and testing. |
| **Production (post-lock)** | **Harden:** Revoke unused Application Passwords, limit endpoints if possible, monitor access logs. |
| **Security** | Secrets outside Git; never leave temporary password-retrieval endpoints in production; use one Application Password per automation use case for easy audit and revocation. |

### 7.2 Creating an Application Password

Application Passwords (WordPress 5.6+) provide non-interactive REST API authentication via HTTP Basic Auth over HTTPS.

**Preferred method:** Create via wp-admin > Users > Application Passwords UI.

**Programmatic method** (when wp-admin is not accessible to agents): Deploy a one-time `init` hook via functions.php:

```php
function create_app_password_once() {
    if (get_option('agent_app_pw_created') === 'done') return;

    // Discover admin user — login name may differ from email
    $user = get_user_by('login', '{admin_username}');
    if (!$user) {
        global $wpdb;
        $row = $wpdb->get_row("SELECT ID, user_login FROM {$wpdb->users} WHERE ID = 1");
        if ($row) $user = get_user_by('ID', $row->ID);
    }
    if (!$user || !class_exists('WP_Application_Passwords')) return;

    $result = WP_Application_Passwords::create_new_application_password(
        $user->ID,
        array('name' => 'agent-automation')
    );

    if (!is_wp_error($result)) {
        update_option('agent_app_pw_plain', $result[0]);
        update_option('agent_app_pw_user', $user->user_login);
    }
    update_option('agent_app_pw_created', 'done');
}
add_action('init', 'create_app_password_once');
```

Pair with a temporary REST endpoint for retrieval (see Section 10 one-time hook pattern). **Checklist after retrieval:**
- [ ] Store credentials in `.env.upress`
- [ ] Remove the init hook from functions.php
- [ ] Remove the retrieval endpoint from functions.php
- [ ] Delete the `agent_app_pw_plain` option from DB
- [ ] Verify auth: `curl -s "$REST/wp/v2/users/me?context=edit" -u "$USER:$PASS"`

### 7.3 Usage

```bash
AUTH="$UPRESS_WP_APP_USER:$UPRESS_WP_APP_PASS"
REST="$UPRESS_WP_REST_BASE"

# Verify authentication
curl -s "$REST/wp/v2/users/me?context=edit" -u "$AUTH"

# Read all pages (including drafts/private)
curl -s "$REST/wp/v2/pages?per_page=100&status=any&context=edit" -u "$AUTH"

# Update a page
curl -s -X POST "$REST/wp/v2/pages/{id}" -u "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","content":"<p>Updated</p>"}'

# Manage plugins
curl -s "$REST/wp/v2/plugins" -u "$AUTH"
curl -s -X POST "$REST/wp/v2/plugins/{plugin/file}" -u "$AUTH" \
  -H "Content-Type: application/json" -d '{"status":"inactive"}'

# Read site settings
curl -s "$REST/wp/v2/settings" -u "$AUTH"
```

```python
import requests, os
from dotenv import load_dotenv

load_dotenv(".env.upress")

REST = os.getenv("UPRESS_WP_REST_BASE")
AUTH = (os.getenv("UPRESS_WP_APP_USER"), os.getenv("UPRESS_WP_APP_PASS"))

pages = requests.get(f"{REST}/wp/v2/pages",
    params={"per_page": 100, "status": "any", "context": "edit"}, auth=AUTH).json()
```

### 7.4 Key Notes

- Application Passwords require **HTTPS**; they will not work over plain HTTP.
- `context=edit` returns raw content; `status=any` includes drafts/private/trash.
- `user_login` (for auth) may differ from the email shown in wp-admin. Always verify.
- Pagination: max 100 items per page. Check `X-WP-Total` / `X-WP-TotalPages` headers.
- Rate limiting may apply — add small delays to bulk operations.

### 7.5 Discovering Available Routes

```bash
curl -s "https://www.{domain}/wp-json/" | python3 -c "
import sys,json
d = json.load(sys.stdin)
routes = sorted(d.get('routes',{}).keys())
print(f'Total routes: {len(routes)}')
for r in routes: print(f'  {r}')
"
```

Common namespaces on uPress with typical plugins:

| Namespace | Routes | Provides |
| --- | --- | --- |
| `wp/v2` | 100-130 | Pages, posts, comments, menus, widgets, plugins, themes, users, media, settings, blocks, templates |
| `yoast/v1` | 50+ | SEO metadata, indexing, social profiles |
| `ezcache/v1` | ~6 | Cache status, settings, purge, WebP |
| `toolset-views/v1` | ~20 | Views, content templates, post types |
| `monsterinsights/v1` | ~9 | Google Analytics |
| `wp-site-health/v1` | ~8 | Health checks, directory sizes |

---

## 8. Plugins — Standardization Policy

| Rule | Detail |
| --- | --- |
| **uPress premium library** | Reference: [upress.co.il/features/wordpress-premium-plugins-library](https://www.upress.co.il/features/wordpress-premium-plugins-library/). Use library plugins before purchasing external licenses. |
| **Per-project plugin list** | Each project must maintain an approved plugin inventory (active + inactive + mu-plugins). Documented in project environment or runbook. |
| **Not a uniform mandate** | Different sites have different themes, architectures, and needs. Plugin standardization is a **recommendation**, not a forced identical list across all projects. |
| **Minimum-plugin principle** | Prefer fewer plugins. Custom code in child theme is preferable to adding a plugin for a single feature. Architectural mandates (e.g., "no Elementor") are per-project decisions by Team 100. |
| **mu-plugins awareness** | uPress places its own must-use plugins in `wp-content/mu-plugins/` (e.g., `booter-crawlers-manager-mu.php`). These load before regular plugins and cannot be deactivated. Map all mu-plugins in the inventory. |

---

## 9. Client Hub — Recommended Pattern (Optional)

When a project requires a structured client-facing interface outside wp-admin (status updates, deliverables, feedback forms), the static hub pattern from Eyal Amit 2026 is the recommended approach:

| Component | Description |
| --- | --- |
| **Source** | `data/*.json` files in the project repo |
| **Build** | Python script generates static HTML from JSON |
| **Deploy** | FTP to a dedicated path (e.g., `ea-eyal-hub/`) outside WordPress |
| **Features** | No PHP required server-side; `noindex` for privacy; JSON-based SSOT for feedback |

This pattern is optional — use only when the project has an external client communication need. Reference implementation: Eyal Amit 2026 repo (`docs/project/eyal-client-hub/`, `scripts/build_eyal_client_hub.py`, `scripts/ftp_publish_eyal_client_hub.py`).

---

## 10. functions.php Patterns — Server-Side Code Execution

PHP code in the child theme's `functions.php` runs server-side on every WordPress request. It is the primary mechanism for operations requiring direct database access or WordPress API calls that REST cannot provide.

### 10.1 Deployment Workflow

```
1. Download current functions.php via FTP
2. Create .bak copy via FTP
3. Modify locally — validate syntax: php -l functions.php
4. Upload via FTP
5. Trigger execution: visit any page on the site
6. Verify changes (curl + grep, REST API check)
7. Remove one-time code, re-upload cleaned version
8. Leave a dated comment noting what was done
```

### 10.2 One-Time Init Hook (Version-Gated)

```php
function my_one_time_fix() {
    if (get_option('my_fix_done') === 'v1') return;

    global $wpdb;
    $wpdb->query(
        "UPDATE {$wpdb->posts} SET post_content = REPLACE(post_content, 'old', 'new')
         WHERE post_content LIKE '%old%'"
    );

    update_option('my_fix_done', 'v1');
}
add_action('init', 'my_one_time_fix');
```

### 10.3 Custom Shortcode

```php
function my_shortcode($atts) {
    ob_start();
    echo '<div class="my-component">...</div>';
    return ob_get_clean();
}
add_shortcode('my_shortcode', 'my_shortcode');
```

### 10.4 Modifying Serialized Options (e.g., Theme Mods)

```php
function fix_theme_mods() {
    if (get_option('theme_mods_fixed') === 'v1') return;

    $theme_slug = get_option('stylesheet');
    $mods = get_option("theme_mods_{$theme_slug}");
    $json = json_encode($mods);
    $json = str_replace('old_value', 'new_value', $json);
    $mods = json_decode($json, true);
    update_option("theme_mods_{$theme_slug}", $mods);

    update_option('theme_mods_fixed', 'v1');
}
add_action('init', 'fix_theme_mods');
```

### 10.5 Updating Widget Content

```php
$widgets = get_option('widget_text');
$widgets[4]['text'] = '<p>New widget content</p>';
update_option('widget_text', $widgets);
```

### 10.6 Updating WordPress Custom CSS

```php
$css_post = wp_get_custom_css_post();
if ($css_post) {
    $css = $css_post->post_content;
    $css = preg_replace('/\.old-class\s*\{[^}]*\}/', '', $css);
    wp_update_custom_css_post($css);
}
```

### 10.7 Safety Rules

| Rule | Detail |
| --- | --- |
| **Version gate** | Every one-time hook MUST check `get_option('key') === 'vN'` to prevent re-execution. |
| **Backup first** | Download `.bak` via FTP before uploading modified functions.php. |
| **Syntax validation** | Run `php -l functions.php` locally before uploading. A syntax error = white-screen for the entire site. |
| **Remove after run** | Delete one-time code after successful execution. Leave only a dated comment. |
| **Child theme only** | All code changes go in the child theme. Parent theme updates will overwrite direct changes. |
| **Risk audit** | For destructive operations (bulk DELETE, DROP, mass REPLACE): document what/why/rollback before execution. |

---

## 11. Decision Matrix — Which Channel for Which Task

| Task | Recommended Channel | Rationale |
| --- | --- | --- |
| Read page/post content | REST API | Fast, structured JSON, no deployment needed |
| Update a single page | REST API | Direct CRUD, immediate effect |
| Bulk content replace (all posts) | functions.php `$wpdb` | SQL REPLACE across all rows in one query |
| Deploy CSS / PHP code | FTP | Direct file access to theme/plugin directories |
| Manage plugins (activate/deactivate) | REST API | No file access needed |
| Manage menus | REST API | Full CRUD on menu items and locations |
| Manage widgets (read) | REST API | Rendered content available |
| Manage widgets (write) | functions.php `update_option` | Widget options are serialized arrays |
| Delete spam comments | REST API | Paginated bulk delete |
| Complex SQL queries | phpMyAdmin | Full SQL access, visual interface |
| Update serialized options | functions.php | PHP serialization handling required |
| Read wp-config.php | FTP | Direct file read |
| Verify live output | curl + `?nocache=` | Bypass CDN/browser cache |
| Update Yoast SEO settings | functions.php | Settings are serialized arrays in `wp_options` |
| Purge cache (ezCache) | REST API | `POST /ezcache/v1/cache` |
| Check site health | REST API | `/wp-site-health/v1/tests/{test}` |
| Upload media | REST API or FTP | REST for media library integration; FTP for raw files |
| Local PHP testing / WP-CLI | Docker | Safe sandbox, no risk to live site |
| WXR import/export | Docker WP-CLI | `wp import`, `wp export` |

---

## 12. Credentials Template — `.env.upress`

**This is the organizational standard for storing uPress/WordPress secrets.** Never use markdown files for secrets. Always `.gitignore` this file.

```env
# ── FTPS ──
UPRESS_SFTP_HOST=ftp.s{NNN}.upress.link
UPRESS_SFTP_PORT=21
UPRESS_SFTP_USER={user}@{domain}
UPRESS_SFTP_PASS={password}

# ── URLs ──
UPRESS_PUBLIC_BASE=https://{domain}
UPRESS_WP_ADMIN=https://{domain}/wp-admin
UPRESS_WP_REST_BASE=https://www.{domain}/wp-json
UPRESS_PAGE_SLUG=/{primary_page_slug}
UPRESS_UPLOAD_PATH=wp-content/uploads/{project}

# ── phpMyAdmin ──
UPRESS_PHPMYADMIN_URL=https://s-il-{NNN}-{code}.upress.io/{token}/
UPRESS_DB_NAME={db_name}
UPRESS_DB_USER={db_user}
UPRESS_DB_PASS={db_pass}
UPRESS_DB_TABLE_PREFIX={prefix}_

# ── WordPress Admin (dashboard login) ──
UPRESS_WP_ADMIN_USER={admin_email}
UPRESS_WP_ADMIN_PASS={admin_password}

# ── REST API Application Password ──
UPRESS_WP_APP_USER={wp_user_login}
UPRESS_WP_APP_PASS={application_password}
```

**Per-project `.env.upress.example`** (committed to repo): Same structure with placeholder values and comments explaining each field. No real secrets.

---

## 13. Lessons Learned — Merged Pitfalls

### FTPS TLS Session Reuse (Critical)
uPress production servers enforce TLS session reuse on data channels. Standard Python `ftplib.FTP_TLS` will fail silently or with cryptic connection errors. The `ReusedSessionFTP_TLS` subclass (Section 2.2) is mandatory for production. Staging may work without TLS if SSL is not provisioned.

### WordPress Admin Username vs Email
The WordPress login screen accepts email, but Application Passwords authenticate with the `user_login` field. These are often different (e.g., `NimrodAdmin` vs `admin@mezoo.co`). Always discover the correct `user_login` via `$wpdb->users` or `/wp/v2/users/me`.

### Serialized Data in wp_options
SQL `REPLACE()` on serialized data corrupts length markers. Always use PHP APIs (`get_option` / `update_option`) or the JSON encode/replace/decode pattern.

### functions.php Syntax Errors = Site Down
A PHP syntax error in functions.php will white-screen the entire site. Always: (1) keep a `.bak` copy, (2) run `php -l` locally, (3) have FTP access ready to revert instantly.

### One-Time Hooks Must Be Idempotent
The `init` hook runs on every page load. Ungated one-time code will re-execute continuously, potentially causing data corruption or performance issues.

### Cache Invalidation After Changes
After content or settings changes, purge the cache. Methods: (1) ezCache REST: `POST /ezcache/v1/cache`, (2) uPress panel SuperCache purge, (3) `?nocache=$(date +%s)` for verification.

### REST API Pagination
Max 100 items per page. Always check `X-WP-Total` and `X-WP-TotalPages` response headers. Loop with `page=` parameter for complete datasets.

### Application Password Security
- Store in `.env.upress`, never in code or commits
- Application Passwords bypass 2FA and can be revoked independently
- One password per automation use case — easier to audit and revoke
- The plain password is only available at creation time — stored hashed afterward

### FTP Root Path Varies
Some uPress accounts: FTP root = WordPress root. Others: FTP root = `public_html/` or another prefix. Always verify on first connection. Document in `.env.upress` as `UPRESS_UPLOAD_PATH`.

### Child Theme is Mandatory
All code changes go in the child theme, never the parent theme. Parent theme updates will overwrite direct changes. This is true regardless of which parent theme is used (Flatsome, GeneratePress, etc.).

### mu-plugins Are Platform-Managed
uPress places its own must-use plugins in `wp-content/mu-plugins/`. These load before regular plugins and cannot be deactivated. Do not conflict with their names.

### Staging-to-Production Differences
Do not assume staging and production behave identically. TLS, SSL certificates, FTP configuration, caching, and CDN may differ. Always verify critical behavior in the target environment.

---

## 14. Quick Reference

### REST API Endpoints

```
GET    /wp/v2/pages?per_page=100&status=any&context=edit
POST   /wp/v2/pages/{id}
GET    /wp/v2/posts?per_page=100
GET    /wp/v2/comments?status={status}&per_page=100
DELETE /wp/v2/comments/{id}?force=true
GET    /wp/v2/menus
GET    /wp/v2/menu-items?menus={id}
DELETE /wp/v2/menu-items/{id}?force=true
POST   /wp/v2/menu-items
GET    /wp/v2/widgets
GET    /wp/v2/plugins
POST   /wp/v2/plugins/{plugin/file}
GET    /wp/v2/settings
POST   /wp/v2/settings
GET    /wp/v2/media?per_page=100
POST   /wp/v2/media
GET    /wp/v2/users/me?context=edit
GET    /wp/v2/themes?status=active
GET    /yoast/v1/get_head?url={url}
GET    /ezcache/v1/status
POST   /ezcache/v1/cache
GET    /wp-site-health/v1/tests/{test}
```

All authenticated endpoints require: `-u "$UPRESS_WP_APP_USER:$UPRESS_WP_APP_PASS"`

### Post-Deploy Checklist

- [ ] Verify site loads: `curl -s -o /dev/null -w "%{http_code}" "https://www.{domain}/?nocache=$(date +%s)"`
- [ ] Verify target page: `curl -s "https://www.{domain}/{slug}/?nocache=$(date +%s)" | grep "expected_content"`
- [ ] Purge cache if ezCache: `curl -s -X POST "$REST/ezcache/v1/cache" -u "$AUTH" -H "Content-Type: application/json" -d '{"action":"purge"}'`
- [ ] Check for PHP errors: visit site, check for blank pages or error output
- [ ] Remove one-time hooks from functions.php
- [ ] Verify REST API auth still works: `curl -s "$REST/wp/v2/users/me?context=edit" -u "$AUTH"`

### Server File Structure (Generic)

```
/                                 <- FTP root (may or may not = WP root)
├── wp-config.php                 <- DB credentials, table prefix, debug mode
├── wp-content/
│   ├── themes/
│   │   ├── {parent-theme}/       <- Do NOT modify
│   │   └── {child-theme}/        <- All code changes go here
│   │       ├── functions.php     <- Custom PHP hooks, shortcodes
│   │       ├── style.css         <- Child theme declaration
│   │       └── {project}.css     <- Project-specific shared CSS (optional)
│   ├── plugins/                  <- All plugins
│   ├── mu-plugins/               <- Must-use plugins (uPress + project)
│   └── uploads/                  <- Media library + custom uploads
│       └── {project}/            <- Project-specific data files
├── wp-admin/
├── wp-includes/                  <- WordPress core (do NOT modify)
└── wp-autologin.php              <- uPress auto-login (from cPanel)
```

---

*This standard is based on production experience with SmallFarmsAgents (nimrod.bio) and Eyal Amit 2026 (eyalamit.co.il) on uPress hosting. It supersedes project-specific playbooks and should be adopted as the canonical reference for all uPress + WordPress projects.*
