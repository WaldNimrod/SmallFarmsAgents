# DEPLOY_LOG — SFA-S002-P001-WP007 — team_99

**Date:** 2026-05-06
**Author:** team_99 (waldhomeserver)
**WP:** SFA-S002-P001-WP007
**Type:** DEPLOY_LOG
**Smoke result:** BLOCKED — uPress rejects all non-image uploads via WP REST API

---

## 1. Pre-deploy verification

- WP REST auth: HTTP 200 (`agent` user, id confirmed)
- `.env` has 3 WP REST vars: UPRESS_WP_REST_BASE, UPRESS_WP_APP_USER, UPRESS_WP_APP_PASS
- `wp_upload.py` present on offline branch
- Build succeeds: 32 products, `artifact_version=20260506_231744`

## 2. Upload attempt — FAIL

```
WP REST upload attempt 1/3 failed for sfagent-manifest.json:
  500 Server Error: Internal Server Error
  {"code":"rest_upload_sideload_error","message":"אין לך הרשאות להעלות קבצים מהסוג הזה"}
```

Translation: "You don't have permission to upload files of this type."

## 3. Root cause investigation

| File type | Extension | Content-Type | HTTP | Result |
|-----------|-----------|-------------|------|--------|
| PNG image | `.png` | `image/png` | **201** | SUCCESS |
| JSON | `.json` | `application/json` | 500 | BLOCKED |
| HTML | `.html` | `text/html` | 500 | BLOCKED |
| Text | `.txt` | `text/plain` | 500 | BLOCKED |

**uPress restricts WP media uploads to images only.** All non-image file types (JSON, HTML, TXT) are rejected with HTTP 500 "אין לך הרשאות להעלות קבצים מהסוג הזה".

## 4. mu-plugin cannot be installed remotely

The DEPLOY_HANDOFF §3 specifies a `sfagent-allow-json.php` mu-plugin to override MIME restrictions. However:

- FTP port 21 is blocked (NAT64 limitation — documented in WP006 DEPLOY_LOG)
- SFTP port 22 — timed out
- FTP port 990 (implicit FTPS) — timed out
- FTP port 2222 — timed out
- WP REST API cannot install mu-plugins (not managed via `/wp/v2/plugins`)
- WP plugin management REST endpoint exists but cannot create mu-plugins

**No remote path exists to install the mu-plugin from waldhomeserver.**

## 5. Required manual action (team_00)

Nimrod must manually install the mu-plugin via one of:

1. **uPress WP Admin** → Plugins → Plugin File Editor → create `mu-plugins/sfagent-allow-json.php`
2. **uPress cPanel/file manager** (if available) → navigate to `wp-content/mu-plugins/`
3. **FTP from Mac** (has IPv4 connectivity) → upload to `wp-content/mu-plugins/`

PHP content (from DEPLOY_HANDOFF §3):

```php
<?php
function sfagent_allow_json_mime($mime_types) {
    $mime_types['json'] = 'application/json';
    return $mime_types;
}
add_filter('upload_mimes', 'sfagent_allow_json_mime');

function sfagent_fix_json_check($data, $file, $filename, $mimes) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if ($ext === 'json') {
        $data['ext']  = 'json';
        $data['type'] = 'application/json';
    }
    return $data;
}
add_filter('wp_check_filetype_and_ext', 'sfagent_fix_json_check', 10, 4);
```

Also need to allow HTML uploads — add to the same file:

```php
function sfagent_allow_html_mime($mime_types) {
    $mime_types['html'] = 'text/html';
    $mime_types['htm'] = 'text/html';
    return $mime_types;
}
add_filter('upload_mimes', 'sfagent_allow_html_mime');

function sfagent_fix_html_check($data, $file, $filename, $mimes) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if (in_array($ext, ['html', 'htm'])) {
        $data['ext']  = $ext;
        $data['type'] = 'text/html';
    }
    return $data;
}
add_filter('wp_check_filetype_and_ext', 'sfagent_fix_html_check', 10, 4);
```

## 6. After mu-plugin is installed

team_99 will resume from step 5 of MSG-003:
1. `python -m organic_market_agent run_publisher --upload`
2. `python scripts/wp_shortcode_install.py --set-mou-url <url>`
3. Smoke + WP003 Pass-2

---

*team_99 | waldhomeserver | 2026-05-06 | BLOCKED on manual mu-plugin install*
