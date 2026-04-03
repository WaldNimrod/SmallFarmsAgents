# uPress + WordPress Agent Playbook (Project-Specific — SmallFarmsAgents)

> **SUPERSEDED:** This document has been superseded by the cross-project organizational standard:
> **[UPRESS_WORDPRESS_STANDARD_v2.md](UPRESS_WORDPRESS_STANDARD_v2.md)** (v2.0, 2026-04-08).
>
> This file is retained as a **project-specific reference** for SmallFarmsAgents (nimrod.bio) with
> concrete credentials, paths, and implementation details unique to this project. For normative
> procedures, policies, and patterns — always refer to the v2 standard.

> Source project: **MyFarmAgents / SmallFarmsAgents** (nimrod.bio)
> Created: 2026-04-02 | Version: 1.0 (superseded by Standard v2.0)

---

## 1. Environment Overview

### uPress Hosting Characteristics

| Property | Value |
| --- | --- |
| Provider | uPress.co.il — managed WordPress hosting (Israel) |
| Plan type | Shared Pro |
| Server naming | `s{NNN}` (e.g., `s887`) |
| WordPress root | FTP root = WP root (no `public_html/` prefix) |
| PHP version | Managed by uPress (auto-updated) |
| MySQL | Localhost only — not accessible remotely |
| SSL | Built-in, auto-renewed |
| CDN | Built-in (uPress CDN) |
| Backups | Daily automatic backups |
| Dev environments | Available via uPress panel |
| Premium plugin library | Available via uPress panel (includes Yoast, Elementor, etc.) |
| cPanel equivalent | uPress custom dashboard at `my.upress.co.il` |

### What Is Blocked

| Resource | Status | Workaround |
| --- | --- | --- |
| SSH / SFTP (port 22) | Blocked | Use FTPS (port 21) |
| WP-CLI | Not installed | Use REST API or functions.php hooks |
| Direct MySQL (port 3306) | Blocked remotely | Use phpMyAdmin (browser) or `$wpdb` via functions.php |
| File execution via URL | `.php` in uploads blocked | Use theme/plugin directories |
| Server-level cron | Not available | Use WP cron or external cron service |

---

## 2. Access Channels

### Channel 1: FTPS (File Transfer)

**What:** FTP over TLS on port 21 — full read/write access to every file in the WordPress installation.

**When to use:**
- Deploying code changes (functions.php, CSS, templates)
- Uploading static files (data files, media)
- Reading wp-config.php for configuration details
- Backup/restore of specific files
- Installing or updating plugins/themes manually

**Env vars:**

```
UPRESS_SFTP_HOST=ftp.s{NNN}.upress.link
UPRESS_SFTP_PORT=21
UPRESS_SFTP_USER={user}@{domain}
UPRESS_SFTP_PASS={password}
```

**Python implementation:**

```python
import ftplib, os, io
from dotenv import load_dotenv

load_dotenv(".env.upress")

# uPress requires TLS session reuse — standard ftplib fails on data connections.
# This subclass fixes it by passing the control socket's TLS session to data sockets.
class ReusedSessionFTP_TLS(ftplib.FTP_TLS):
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session
            )
        return conn, size

def get_ftp():
    ftp = ReusedSessionFTP_TLS()
    ftp.connect(os.getenv("UPRESS_SFTP_HOST"), int(os.getenv("UPRESS_SFTP_PORT", 21)))
    ftp.login(os.getenv("UPRESS_SFTP_USER"), os.getenv("UPRESS_SFTP_PASS"))
    ftp.prot_p()  # Enable data channel encryption
    return ftp

# Read a file
ftp = get_ftp()
buf = io.BytesIO()
ftp.retrbinary("RETR /wp-content/themes/flatsome-child/functions.php", buf.write)
content = buf.getvalue().decode("utf-8", "ignore")

# Write a file
upload_buf = io.BytesIO(modified_content.encode("utf-8"))
ftp.storbinary("STOR /wp-content/themes/flatsome-child/functions.php", upload_buf)

ftp.quit()
```

**Critical notes:**
- The `ReusedSessionFTP_TLS` class is mandatory — uPress servers require TLS session reuse on data channels. Standard `ftplib.FTP_TLS` will fail with connection errors.
- FTP root IS the WordPress root (no `public_html/` subdirectory).
- Always `ftp.prot_p()` after login to enable data channel encryption.
- Always `ftp.quit()` when done (connection pool is limited).

---

### Channel 2: WP REST API (Authenticated)

**What:** Full WordPress REST API with administrator privileges via Application Password (HTTP Basic Auth over HTTPS).

**When to use:**
- CRUD operations on pages, posts, comments, menus, widgets
- Managing plugins (activate/deactivate/install)
- Reading and updating site settings
- Managing media library
- Querying content for verification
- Bulk operations (e.g., deleting spam comments)

**Env vars:**

```
UPRESS_WP_APP_USER={username}
UPRESS_WP_APP_PASS={application_password}
UPRESS_WP_REST_BASE=https://www.{domain}/wp-json
```

**Setup — Creating an Application Password:**

Application Passwords (built into WordPress 5.6+) provide non-interactive API authentication without exposing the main admin password. Create one via a one-time `init` hook in functions.php:

```php
function create_app_password_once() {
    if (get_option('my_app_password_created') === 'done') return;
    
    $user = get_user_by('login', '{admin_username}');
    if (!$user || !class_exists('WP_Application_Passwords')) return;
    
    $result = WP_Application_Passwords::create_new_application_password(
        $user->ID,
        array('name' => 'agent-automation')
    );
    
    if (!is_wp_error($result)) {
        // Store plain password temporarily for retrieval
        update_option('my_app_password_plain', $result[0]);
        update_option('my_app_password_user', $user->user_login);
    }
    update_option('my_app_password_created', 'done');
}
add_action('init', 'create_app_password_once');

// Temporary REST endpoint to retrieve it (remove after retrieval!)
function register_password_endpoint() {
    register_rest_route('setup/v1', '/app-password', array(
        'methods'  => 'GET',
        'callback' => function($request) {
            if ($request->get_param('secret') !== '{one-time-secret}') {
                return new WP_Error('forbidden', '', array('status' => 403));
            }
            $pw = get_option('my_app_password_plain', '');
            if (empty($pw)) return new WP_REST_Response(array('status' => 'empty'), 200);
            delete_option('my_app_password_plain'); // Security: delete after read
            return new WP_REST_Response(array(
                'user'     => get_option('my_app_password_user'),
                'password' => $pw,
            ), 200);
        },
        'permission_callback' => '__return_true',
    ));
}
add_action('rest_api_init', 'register_password_endpoint');
```

After retrieving the password, **immediately remove** the endpoint code and the `create_app_password_once` function via FTPS. Store the credentials in `.env.upress`.

**Usage — curl:**

```bash
AUTH="$UPRESS_WP_APP_USER:$UPRESS_WP_APP_PASS"

# Read all pages (including drafts and private)
curl -s "$UPRESS_WP_REST_BASE/wp/v2/pages?per_page=100&status=any&context=edit" -u "$AUTH"

# Update a page
curl -s -X POST "$UPRESS_WP_REST_BASE/wp/v2/pages/{id}" \
  -u "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title","content":"<p>New content</p>"}'

# Delete spam comments in bulk (100 at a time)
curl -s "$UPRESS_WP_REST_BASE/wp/v2/comments?status=spam&per_page=100" -u "$AUTH" \
  | python3 -c "import sys,json; [print(c['id']) for c in json.load(sys.stdin)]" \
  | while read id; do
      curl -s -X DELETE "$UPRESS_WP_REST_BASE/wp/v2/comments/$id?force=true" -u "$AUTH" > /dev/null
    done

# Manage plugins
curl -s "$UPRESS_WP_REST_BASE/wp/v2/plugins" -u "$AUTH"
curl -s -X POST "$UPRESS_WP_REST_BASE/wp/v2/plugins/{plugin/file}" \
  -u "$AUTH" -H "Content-Type: application/json" -d '{"status":"inactive"}'

# Read site settings
curl -s "$UPRESS_WP_REST_BASE/wp/v2/settings" -u "$AUTH"
```

**Usage — Python:**

```python
import requests, os
from dotenv import load_dotenv

load_dotenv(".env.upress")

REST = os.getenv("UPRESS_WP_REST_BASE")
AUTH = (os.getenv("UPRESS_WP_APP_USER"), os.getenv("UPRESS_WP_APP_PASS"))

# Read pages
pages = requests.get(f"{REST}/wp/v2/pages", params={"per_page": 100, "status": "any", "context": "edit"}, auth=AUTH).json()

# Update a page
requests.post(f"{REST}/wp/v2/pages/91325", auth=AUTH, json={"content": "<p>Updated</p>"})

# Get comment counts from headers
r = requests.head(f"{REST}/wp/v2/comments", params={"per_page": 1, "status": "spam"}, auth=AUTH)
spam_count = int(r.headers.get("X-WP-Total", 0))
```

**Available namespaces (typical uPress + common plugins):**

| Namespace | Routes | Provides |
| --- | --- | --- |
| `wp/v2` | 100-130 | Core WP entities (pages, posts, comments, menus, widgets, plugins, themes, users, media, settings, blocks, templates) |
| `yoast/v1` | 50+ | SEO metadata, indexing, social profiles |
| `ezcache/v1` | 6 | Cache status, settings, purge, WebP conversion |
| `toolset-views/v1` | 20 | Views, content templates, post types |
| `monsterinsights/v1` | 9 | Google Analytics integration |
| `wp-site-health/v1` | 8 | Health checks, directory sizes |

**Discovering available routes:**

```bash
curl -s "https://www.{domain}/wp-json/" | python3 -c "
import sys,json
d = json.load(sys.stdin)
routes = sorted(d.get('routes',{}).keys())
print(f'Total routes: {len(routes)}')
for r in routes:
    print(f'  {r}')
"
```

**Discovering the admin username:**

The WordPress admin login name may differ from the email used in the dashboard. The init hook approach (Channel 4) lets you query `$wpdb->users` to discover the correct `user_login`.

**Critical notes:**
- Application Passwords require HTTPS — they will not work over plain HTTP.
- The password is transmitted with every request (Basic Auth) — always use HTTPS.
- `context=edit` is required to get raw content (vs rendered HTML).
- `status=any` is required to see drafts, private, and trash (authenticated only).
- Rate limiting may apply — batch operations should include small delays.
- Pagination: use `X-WP-Total` and `X-WP-TotalPages` response headers.

---

### Channel 3: phpMyAdmin (Browser-Based Database)

**What:** Full database access via web-based phpMyAdmin interface.

**When to use:**
- Inspecting database tables and structure
- Running complex SQL queries
- Bulk data operations that are too complex for REST API
- Debugging — inspecting `wp_options`, `wp_posts`, `wp_postmeta`
- Emergency fixes when other channels fail

**Env vars:**

```
UPRESS_PHPMYADMIN_URL=https://s-il-{NNN}-{code}.upress.io/{token}/
UPRESS_DB_NAME={db_name}
UPRESS_DB_USER={db_user}
UPRESS_DB_PASS={db_pass}
UPRESS_DB_TABLE_PREFIX={prefix}_
```

**Access method:**
- Open the phpMyAdmin URL in a browser (or use browser MCP for automation)
- Login with DB credentials
- The URL contains a security token — keep it private

**Common queries:**

```sql
-- Find table prefix
SHOW TABLES LIKE '%options';

-- Check active plugins
SELECT option_value FROM {prefix}_options WHERE option_name = 'active_plugins';

-- Check theme mods
SELECT option_value FROM {prefix}_options WHERE option_name = 'theme_mods_{theme-slug}';

-- Find all posts containing a string
SELECT ID, post_title, post_type, post_status
FROM {prefix}_posts
WHERE post_content LIKE '%search_string%';

-- Count comments by status
SELECT comment_approved, COUNT(*) as cnt
FROM {prefix}_comments
GROUP BY comment_approved;

-- Delete all spam comments
DELETE FROM {prefix}_comments WHERE comment_approved = 'spam';

-- Check widget settings
SELECT option_value FROM {prefix}_options WHERE option_name LIKE 'widget_%';
```

**Critical notes:**
- Database is only accessible from server localhost — phpMyAdmin is the only remote DB access.
- Always note the table prefix (e.g., `qvj_`) — it varies per installation.
- Be careful with direct SQL updates — WordPress caches options aggressively. After changing `wp_options`, purge the object cache (or restart PHP via uPress panel).

---

### Channel 4: functions.php Hooks (Server-Side Code Execution)

**What:** PHP code injected into the child theme's `functions.php`, executed server-side on every WordPress page load.

**When to use:**
- Registering custom shortcodes
- One-time database operations (update options, delete posts, clean data)
- Modifying WordPress behavior (filters, actions)
- Creating REST API endpoints
- Operations that require `$wpdb` direct database access
- Bulk content updates across all posts/pages
- Modifying serialized data in `wp_options`

**Deployment workflow:**

```
1. Download current functions.php via FTPS
2. Modify locally (append new code)
3. Upload modified file via FTPS
4. Trigger execution by visiting any page on the site
5. Verify changes took effect
6. Remove one-time code, re-upload cleaned version
```

**Pattern — One-Time Init Hook:**

```php
function my_one_time_fix() {
    if (get_option('my_fix_done') === 'v1') return;
    
    global $wpdb;
    
    // Do the work...
    $wpdb->query("UPDATE {$wpdb->posts} SET post_content = REPLACE(post_content, 'old', 'new') WHERE post_content LIKE '%old%'");
    
    update_option('my_fix_done', 'v1');
}
add_action('init', 'my_one_time_fix');
```

**Pattern — Custom Shortcode:**

```php
function my_custom_shortcode($atts) {
    ob_start();
    // Generate HTML output
    echo '<div class="my-component">...</div>';
    return ob_get_clean();
}
add_shortcode('my_shortcode', 'my_custom_shortcode');
```

**Pattern — Modifying Serialized Options (e.g., Theme Mods):**

```php
function fix_theme_mods() {
    if (get_option('theme_mods_fixed') === 'v1') return;
    
    $theme_slug = get_option('stylesheet');
    $mods = get_option("theme_mods_{$theme_slug}");
    
    // Serialized arrays can't be searched with REPLACE — encode to JSON, replace, decode
    $json = json_encode($mods);
    $json = str_replace('old_value', 'new_value', $json);
    $mods = json_decode($json, true);
    
    update_option("theme_mods_{$theme_slug}", $mods);
    update_option('theme_mods_fixed', 'v1');
}
add_action('init', 'fix_theme_mods');
```

**Pattern — Updating Widget Content:**

```php
$widget_key = 'widget_text'; // for text widgets
$widgets = get_option($widget_key);
// $widgets is an array like [3 => ['title' => '...', 'text' => '...'], 4 => [...]]
$widgets[4]['text'] = '<p>New widget content</p>';
update_option($widget_key, $widgets);
```

**Pattern — Updating WordPress Custom CSS:**

```php
$css_post = wp_get_custom_css_post();
if ($css_post) {
    $css = $css_post->post_content;
    // Remove or replace CSS rules
    $css = preg_replace('/\.old-class\s*\{[^}]*\}/', '', $css);
    wp_update_custom_css_post($css);
}
```

**Critical notes:**
- Always use a **version-gated option** (`get_option('fix_done') === 'v1'`) to prevent re-execution.
- Always test locally that the PHP is syntactically valid before uploading — a syntax error in functions.php will **white-screen the entire site**.
- Keep a `.bak` copy: `cp functions.php functions.php.bak` via FTPS before modifying.
- Remove one-time code after it runs successfully — leave only a comment noting what was done and when.
- The `init` hook runs on every page load — guard all one-time operations.

---

## 3. Common Workflows

### Workflow: Content Update (Text, Phone, Email, Links)

**Best approach:** REST API (for individual pages) or functions.php `$wpdb` (for bulk across all posts).

```bash
# Update a single page
curl -s -X POST "$REST/wp/v2/pages/{id}" -u "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"content":"updated HTML content"}'
```

```php
// Bulk replace across all content
$wpdb->query("UPDATE {$wpdb->posts} SET post_content = REPLACE(post_content, 'old_phone', 'new_phone') WHERE post_content LIKE '%old_phone%'");
```

### Workflow: Menu Management

```bash
# List menus
curl -s "$REST/wp/v2/menus" -u "$AUTH"

# List menu items
curl -s "$REST/wp/v2/menu-items?menus={menu_id}&per_page=100" -u "$AUTH"

# Delete a menu item
curl -s -X DELETE "$REST/wp/v2/menu-items/{item_id}?force=true" -u "$AUTH"

# Create a menu item
curl -s -X POST "$REST/wp/v2/menu-items" -u "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Item","url":"https://example.com","menus":7,"status":"publish"}'
```

### Workflow: Plugin Management

```bash
# List all plugins with status
curl -s "$REST/wp/v2/plugins" -u "$AUTH"

# Deactivate a plugin
curl -s -X POST "$REST/wp/v2/plugins/{plugin/file}" -u "$AUTH" \
  -H "Content-Type: application/json" -d '{"status":"inactive"}'

# Activate a plugin
curl -s -X POST "$REST/wp/v2/plugins/{plugin/file}" -u "$AUTH" \
  -H "Content-Type: application/json" -d '{"status":"active"}'
```

### Workflow: Comment Cleanup

```bash
# Count spam
curl -sI "$REST/wp/v2/comments?per_page=1&status=spam" -u "$AUTH" | grep x-wp-total

# Bulk delete spam (100 per batch, loop until done)
while true; do
  IDS=$(curl -s "$REST/wp/v2/comments?status=spam&per_page=100" -u "$AUTH" \
    | python3 -c "import sys,json; ids=json.load(sys.stdin); [print(c['id']) for c in ids]; exit(0 if ids else 1)" 2>/dev/null)
  [ $? -ne 0 ] && break
  echo "$IDS" | while read id; do
    curl -s -X DELETE "$REST/wp/v2/comments/$id?force=true" -u "$AUTH" > /dev/null
  done
  echo "Deleted batch..."
  sleep 1
done
```

### Workflow: CSS Changes

**For shared/base CSS:** Deploy via FTPS to child theme directory.

```python
# Upload CSS file
ftp = get_ftp()
css_content = open("sfagent-base.css", "rb")
ftp.storbinary("STOR /wp-content/themes/flatsome-child/sfagent-base.css", css_content)
ftp.quit()
```

**For WordPress Customizer "Additional CSS":** Use functions.php hook.

```php
$css_post = wp_get_custom_css_post();
$css = $css_post ? $css_post->post_content : '';
$css .= "\n/* New rules */\n.my-class { color: red; }";
wp_update_custom_css_post($css);
```

### Workflow: SEO (Yoast) Management

```bash
# Get SEO head for a URL
curl -s "$REST/yoast/v1/get_head?url=https://www.{domain}/{slug}"

# Yoast settings are stored in wp_options — update via REST API settings endpoint or functions.php
```

```php
// Update Yoast meta description for homepage
$titles = get_option('wpseo_titles');
$titles['metadesc-home-wpseo'] = 'New meta description';
update_option('wpseo_titles', $titles);

// Update Yoast social/OG settings
$social = get_option('wpseo_social');
$social['og_frontpage_title'] = 'OG Title';
$social['og_frontpage_desc'] = 'OG Description';
update_option('wpseo_social', $social);
```

### Workflow: Cache Management (ezCache)

```bash
# Check cache status
curl -s "$REST/ezcache/v1/status" -u "$AUTH"

# Purge cache (after content changes)
curl -s -X POST "$REST/ezcache/v1/cache" -u "$AUTH" \
  -H "Content-Type: application/json" -d '{"action":"purge"}'
```

### Workflow: Site Health Check

```bash
# Run health tests
curl -s "$REST/wp-site-health/v1/tests/https-status" -u "$AUTH"
curl -s "$REST/wp-site-health/v1/tests/page-cache" -u "$AUTH"
curl -s "$REST/wp-site-health/v1/tests/loopback-requests" -u "$AUTH"
```

### Workflow: Verify Live Changes

Always verify after any deployment:

```bash
# Bypass cache with nocache parameter
curl -s "https://www.{domain}/?nocache=$(date +%s)" | grep "expected_content"

# Check specific page
curl -s "https://www.{domain}/{slug}/?nocache=$(date +%s)" | grep "expected_content"
```

---

## 4. Environment Configuration Template

### `.env.upress` structure

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
UPRESS_WP_APP_USER={wp_username}
UPRESS_WP_APP_PASS={application_password}
```

---

## 5. Lessons Learned and Pitfalls

### FTPS TLS Session Reuse
uPress servers enforce TLS session reuse on data connections. Standard Python `ftplib.FTP_TLS` will fail. Always use the `ReusedSessionFTP_TLS` subclass (Section 2, Channel 1).

### WordPress Admin Username vs Email
The WordPress login screen accepts email, but REST API Application Passwords authenticate with the `user_login` field — which may be different (e.g., `NimrodAdmin` instead of `admin@mezoo.co`). Always verify via `$wpdb->users` or the REST API `/wp/v2/users/me`.

### Serialized Data in wp_options
Many WordPress and plugin settings store serialized PHP arrays in `wp_options`. You cannot use SQL `REPLACE()` on serialized data — it will corrupt the serialization lengths. Use `get_option()` / `update_option()` in PHP, or JSON encode/decode the array, do string replacements on the JSON, then decode back.

### functions.php Syntax Errors = Site Down
A PHP syntax error in `functions.php` will white-screen the entire WordPress site. Always:
1. Keep a `.bak` copy before editing
2. Validate PHP syntax locally if possible
3. Have FTPS access ready to revert immediately

### One-Time Hooks Must Be Idempotent
Always gate one-time `init` hooks with an option check. WordPress loads `functions.php` on every request — ungated hooks will re-execute continuously.

### Cache Invalidation After Changes
After any content or settings change, purge the cache:
- ezCache: REST API `/ezcache/v1/cache` with `{"action": "purge"}`
- Or append `?nocache=` query param for verification
- uPress SuperCache (server-level) may also need purging via the uPress panel

### REST API Pagination
The REST API returns max 100 items per page. Always check `X-WP-Total` and `X-WP-TotalPages` headers for total counts and paginate accordingly.

### Application Password Security
- Store in `.env.upress`, never in code or commits
- Application Passwords bypass 2FA and can be revoked independently
- One password per automation use case — easier to audit and revoke
- The plain password is only available at creation time — it's stored hashed afterward

### WordPress Database Table Prefix
Every uPress installation has a unique table prefix (e.g., `qvj_`). Never hardcode `wp_` — always read it from `wp-config.php` or use `$wpdb->prefix` in PHP.

### Child Theme is Mandatory
All code changes go in the child theme (e.g., `flatsome-child`), never the parent theme. Parent theme updates will overwrite any changes.

### mu-plugins
uPress places its own must-use plugins in `wp-content/mu-plugins/`. These load before regular plugins and cannot be deactivated. Common: `booter-crawlers-manager-mu.php` (bot rate limiting).

---

## 6. Decision Matrix: Which Channel to Use

| Task | Recommended Channel | Why |
| --- | --- | --- |
| Read page content | REST API | Fast, structured JSON, no file deployment needed |
| Update single page | REST API | Direct CRUD, immediate effect |
| Bulk content replace (all posts) | functions.php `$wpdb` | SQL REPLACE across all rows in one query |
| Deploy CSS/PHP code | FTPS | Direct file access |
| Manage plugins | REST API | Activate/deactivate/list without file access |
| Manage menus | REST API | Full CRUD on menu items |
| Manage widgets | REST API (read) + functions.php (write) | REST read works; writing widget options is easier via PHP `update_option` |
| Delete spam comments | REST API | Paginated bulk delete |
| Complex SQL queries | phpMyAdmin | Full SQL access, visual interface |
| Update serialized options | functions.php | PHP serialization handling required |
| Read wp-config.php | FTPS | Direct file read |
| Verify live output | curl + grep | Bypass cache, check rendered HTML |
| Update Yoast SEO settings | functions.php | Settings are serialized arrays in options |
| Purge cache | REST API (ezCache) | API endpoint available |
| Check site health | REST API | Built-in health test endpoints |
| Upload media files | REST API or FTPS | REST for media library integration; FTPS for raw file placement |

---

## 7. Quick Reference — Common REST API Endpoints

```
GET    /wp/v2/pages?per_page=100&status=any&context=edit
POST   /wp/v2/pages/{id}                    — update page
GET    /wp/v2/posts?per_page=100
GET    /wp/v2/comments?status={status}&per_page=100
DELETE /wp/v2/comments/{id}?force=true
GET    /wp/v2/menus
GET    /wp/v2/menu-items?menus={id}
DELETE /wp/v2/menu-items/{id}?force=true
POST   /wp/v2/menu-items                    — create menu item
GET    /wp/v2/widgets
GET    /wp/v2/plugins
POST   /wp/v2/plugins/{plugin/file}         — activate/deactivate
GET    /wp/v2/settings
POST   /wp/v2/settings                      — update settings
GET    /wp/v2/media?per_page=100
POST   /wp/v2/media                         — upload (multipart)
GET    /wp/v2/users/me?context=edit
GET    /wp/v2/themes?status=active
GET    /yoast/v1/get_head?url={url}
GET    /ezcache/v1/status
POST   /ezcache/v1/cache                    — purge
GET    /wp-site-health/v1/tests/{test}
```

All authenticated endpoints require: `-u "$UPRESS_WP_APP_USER:$UPRESS_WP_APP_PASS"`

---

## 8. File Structure on uPress Server

```
/                               ← FTP root = WordPress root
├── wp-config.php               ← DB credentials, table prefix, debug mode
├── wp-content/
│   ├── themes/
│   │   ├── flatsome/           ← Parent theme (do NOT modify)
│   │   └── flatsome-child/     ← Child theme (all code changes go here)
│   │       ├── functions.php   ← Custom PHP hooks, shortcodes
│   │       ├── style.css       ← Child theme declaration
│   │       ├── sfagent-base.css ← Project-specific shared CSS
│   │       ├── header.php      ← Custom header overrides
│   │       └── footer.php      ← Custom footer overrides
│   ├── plugins/                ← All plugins
│   ├── mu-plugins/             ← Must-use plugins (uPress managed)
│   └── uploads/                ← Media library + custom uploads
│       └── {project}/          ← Project-specific data files
├── wp-admin/                   ← Admin dashboard
├── wp-includes/                ← WordPress core (do NOT modify)
└── wp-autologin.php            ← uPress auto-login (from cPanel)
```

---

*This playbook is based on production experience with the MyFarmAgents project (nimrod.bio) on uPress shared Pro hosting. It should be applicable to any WordPress site hosted on uPress with minor adjustments for domain, credentials, and theme.*
