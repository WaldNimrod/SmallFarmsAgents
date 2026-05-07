# Deploy Handoff — SFA-S002-P001-WP007 — WP REST Upload (F-01 Fix)

**Date:** 2026-05-07
**From:** sfa_build (Team 10)
**To:** team_99 (production operator)
**WP:** SFA-S002-P001-WP007
**Priority:** P0 — lifts F-01 (public index stale)

---

## Context

Bezeq home network blocks outbound port 21 on waldhomeserver. FTPS uploads fail silently. Port 443 (HTTPS) is open. This WP now uses the WP REST `/wp/v2/media` API for all artifact uploads — same pattern as shaked-wg-agent (proven on same host). FTPS code is preserved as opt-in fallback (`UPRESS_FALLBACK_FTPS=1`).

---

## Step 1 — Get WP Application Password from team_00

team_00 holds the `UPRESS_WP_APP_USER` and `UPRESS_WP_APP_PASS` (WordPress Application Password) for `www.nimrod.bio`. These are already in shaked-wg-agent's `.env` on the server — confirm they also work for SFA's uploads (same WP install, same user).

Application Password format: `xxxx xxxx xxxx xxxx xxxx xxxx` — 24 chars with spaces. Strip spaces before base64-encoding (the `_token()` function does this automatically).

---

## Step 2 — Update waldhomeserver `.env`

Add or update these lines in `/data/projects/smallfarmsagents/.env`:

```env
# WP REST API upload (WP007 — primary, replaces FTPS port 21)
UPRESS_WP_REST_BASE=https://www.nimrod.bio/wp-json
UPRESS_WP_APP_USER=<wp_user_login_from_team_00>
UPRESS_WP_APP_PASS=<application_password_from_team_00>
# Leave UPRESS_FALLBACK_FTPS unset (default=off) — FTPS is blocked anyway
```

Do NOT set `UPRESS_FALLBACK_FTPS=1` unless explicitly testing FTPS on a non-Bezeq network.

---

## Step 3 — Handle JSON MIME type (if uPress rejects .json uploads)

uPress may restrict media library uploads by extension. If the first upload run returns HTTP 415 or similar for `.json` files, install the following mu-plugin:

Create `/wp-content/mu-plugins/sfagent-allow-json.php` via FTPS or WP admin:

```php
<?php
/**
 * Plugin Name: SFAgent Allow JSON Upload
 * Description: Allows .json files in the WP media library for SFA artifact uploads.
 * Version: 1.0
 */
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

Upload this file to `wp-content/mu-plugins/sfagent-allow-json.php` via FTPS. It activates automatically (no WP admin action needed).

---

## Step 4 — Register WP option for manifest-of-URLs (AC-04 Option A)

The shortcode reads `get_option('sfagent_manifest_of_urls_url')` to find the pointer file URL. This option must be registered in WordPress for the REST `/wp/v2/settings` endpoint to accept it. Add to the child theme's `functions.php`:

```php
// SFAgent: register manifest-of-URLs option for REST API (WP007)
function sfagent_register_settings() {
    register_setting('general', 'sfagent_manifest_of_urls_url', array(
        'type'         => 'string',
        'description'  => 'SFAgent manifest-of-URLs pointer file URL (WP REST media library)',
        'show_in_rest' => true,
        'default'      => '',
    ));
}
add_action('init', 'sfagent_register_settings');
```

This is safe to add to existing functions.php alongside the shortcode code. Download, edit, re-upload via FTPS.

---

## Step 5 — Run the shortcode installer

Re-run the shortcode installer to update functions.php with the new shortcode definition (it fetches via manifest-of-URLs instead of reading from disk):

```bash
cd /data/projects/smallfarmsagents
python scripts/wp_shortcode_install.py
```

This will update functions.php on the WP server to use the new AC-04 Option A shortcode. It requires FTPS credentials for the shortcode install step.

---

## Step 6 — Smoke test: first upload

```bash
cd /data/projects/smallfarmsagents
python -m organic_market_agent run_publisher --upload
```

Expected output:
```
PublishEngine: artifacts written to output/public
WP REST upload OK: 5 artifacts uploaded
  sfagent-manifest.json → media_id=NNN url=https://www.nimrod.bio/wp-content/uploads/YYYY/MM/sfagent-manifest.json
  sfagent-public-report.json → media_id=NNN url=...
  sfagent-public-report.html → media_id=NNN url=...
  sfagent-public-report-body.html → media_id=NNN url=...
  sfagent-manifest-of-urls.json → media_id=NNN url=https://www.nimrod.bio/wp-content/uploads/YYYY/MM/sfagent-manifest-of-urls.json
```

Capture the `sfagent-manifest-of-urls.json` URL from the output.

---

## Step 7 — Set the manifest-of-URLs WP option

```bash
python scripts/wp_shortcode_install.py --set-mou-url "https://www.nimrod.bio/wp-content/uploads/YYYY/MM/sfagent-manifest-of-urls.json"
```

Replace the URL with the actual URL from Step 6 output.

If the REST endpoint returns a non-200 (option not yet registered — Step 4 not done), set it manually in WP admin:

1. Go to `https://www.nimrod.bio/wp-admin/options.php`
2. Search for `sfagent_manifest_of_urls_url`
3. Paste the URL from Step 6
4. Save

---

## Step 8 — Verify public page

```bash
curl -s "https://www.nimrod.bio/SmallFarmsAgent" | grep -c "sfagent"
```

Should return a positive count (shortcode rendered content). Also:

```bash
curl -s "https://www.nimrod.bio/wp-content/uploads/YYYY/MM/sfagent-manifest.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print('artifact_version:', d['artifact_version'])"
```

Should show today's `artifact_version` (format: `YYYYMMDD_HHMMSS`).

---

## Step 9 — Confirm pipeline_alerts

```sql
SELECT protocol, status, message, created_at
FROM pipeline_alerts
ORDER BY created_at DESC
LIMIT 10;
```

There should be no `FTPS upload FAILED` entries. WP REST failures (if any) will appear with `WP REST` in the message.

---

## Rollback (if needed)

To revert to FTPS fallback temporarily (e.g., on a non-Bezeq network):

```env
UPRESS_FALLBACK_FTPS=1
```

This bypasses WP REST and uses the existing FTPS code. Remove once WP REST is confirmed working.

---

## File locations (new, on server)

| Path | Purpose |
|------|---------|
| `data/.wp_media_id_sfagent_manifest_json` | Tracks WP media_id for sfagent-manifest.json |
| `data/.wp_media_id_sfagent_public_report_json` | Tracks media_id for sfagent-public-report.json |
| `data/.wp_media_id_sfagent_public_report_html` | Tracks media_id for sfagent-public-report.html |
| `data/.wp_media_id_sfagent_public_report_body_html` | Tracks media_id for sfagent-public-report-body.html |
| `data/.wp_media_id_sfagent_manifest_of_urls_json` | Tracks media_id for sfagent-manifest-of-urls.json |
| `output/public/sfagent-manifest-of-urls.json` | Locally-written pointer file (uploaded to WP) |

These files persist between runs to enable delete-before-overwrite (keeps URLs clean, no `-1`/`-2` suffix).

---

*Ready for team_99 deploy. Blockers: team_00 must supply WP Application Password.*
