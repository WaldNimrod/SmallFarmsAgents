# uPress WordPress Publish Pipeline — Operational Runbook

**Status:** Authoritative for all SFA publishing operations after **2026-05-07**.
**Owner:** team_100 (architecture) + team_99 (operations, waldhomeserver).
**Replaces:** Previous FTPS-primary publish flow (retained only as defensive fallback).

This runbook is the canonical reference for the SmallFarmsAgents publish pipeline. Future sessions in this domain MUST read this before touching publish/upload code or operating credentials.

---

## 1. Architecture summary

| Layer | Component | Path |
|------|-----------|------|
| **Primary upload** | WP REST API (`/wp/v2/media`) over **HTTPS port 443** | [`organic_market_agent/publisher/wp_upload.py`](../../organic_market_agent/publisher/wp_upload.py) |
| **Fallback (opt-in)** | FTPS (`ftplib.FTP_TLS` + `ReusedSessionFTP_TLS`) over port 21 | [`organic_market_agent/publisher/ftps_upload.py`](../../organic_market_agent/publisher/ftps_upload.py) — gated by `UPRESS_FALLBACK_FTPS=1` |
| **WordPress shortcode** | `[sfagent_market_report]` reads URLs from `sfagent_manifest_of_urls_url` WP option, dereferences via `wp_remote_get` | [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py) |
| **uPress mu-plugin** | `sfagent-allow-json.php` — overrides MIME restrictions on JSON+HTML uploads | `wp-content/mu-plugins/sfagent-allow-json.php` (server-side WP filesystem) |
| **Pipeline trigger** | Daily cron 06:00 UTC on `waldhomeserver` | `crontab -l` for user `nimrodw` |

### Data flow
```
ingest → normalize → aggregate → 4 artifacts in output/public/
   → POST /wp/v2/media (4 uploads, delete-before-overwrite per canonical filename)
   → POST /wp/v2/media (1 manifest-of-urls.json pointer)
   → wp_shortcode_install.py --set-mou-url <pointer-url>
   → public page renders fresh data
```

---

## 2. Why this architecture (decision history)

**Original design (pre-2026-05-07):** FTPS upload to uPress over port 21. Worked until ~2026-04-17.

**Failure mode discovered:** Site stuck on 19-day-old data (`artifact_version=20260417_004822`). Investigation chain:

1. **WP006 hypothesis** — Python `ftplib.FTP_TLS` lost `ReusedSessionFTP_TLS` subclass. **Disproven** — code was correct (sfa_build verified, 14 tests pass).
2. **NAT64 hypothesis** (team_99 Pass-1) — clatd via `nat64.net` chokes on FTP active-mode multi-connection protocol. **Partially correct but not the full picture.**
3. **Bezeq egress block** (team_99 + team_100 via `/server`) — `nc -z ftp.s887.upress.link 21` BLOCKED from BOTH waldhomeserver AND Mac at home. Block is on Bezeq ISP egress, **not** on uPress side. Confirmed: uPress IP whitelist did NOT unblock; `ftp.debian.org:21` also blocked → ISP-wide port 21 outbound block.
4. **Resolution (WP007)** — replace FTPS with WP REST API on port 443 (which is open). Pattern adapted from sibling project [`shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py`](../../../shaked-wg-agent/shaked_wg_agent/publisher/wp_upload.py).

**Why WP REST is the correct permanent answer (not just a workaround):**
- Bezeq port 21 block is upstream of the home router — router-level config cannot bypass it.
- IPv6-only WAN + active-mode FTP through NAT64 is structurally fragile (active mode requires the server to open inbound data ports, which NAT64 mishandles).
- shaked-wg-agent on the same host already had REST scaffolding for the same reason.
- Modern WordPress sites support `/wp/v2/media` natively — future-proof.
- Port 443 is universally accessible regardless of ISP policy.

---

## 3. Credentials

### Source of truth (Mac)
File: `/Users/nimrod/Documents/SmallFarmsAgents/.env` (mode 0600). Three keys:

```
UPRESS_WP_REST_BASE=https://www.nimrod.bio/wp-json
UPRESS_WP_APP_USER=agent
UPRESS_WP_APP_PASS=xxxx xxxx xxxx xxxx xxxx xxxx
```

### Replicas (server)
- `/data/projects/smallfarmsagents/.env` — production publish runtime
- `/data/projects/shaked-wg-agent/.env` — sibling project, kept in sync (per `shaked-wg-agent/scripts/env_from_sfa.sh` historical pattern)

### Format notes (binding)
- `UPRESS_WP_APP_USER` is the **WordPress username** (`agent`, 5 chars), NOT the application password label.
- `UPRESS_WP_APP_PASS` is a **WP application password** — 24 chars + 5 spaces = **29 chars total**, exactly as displayed in WP Admin → Users → Application Passwords. Spaces are part of the value; python-dotenv preserves them in unquoted .env values.
- The label `sfa-pipeline` (visible in WP Admin) is for human readability of the application password registration; it is NOT used for auth.

### Auth verification (5-second smoke)
From any environment that has the .env loaded:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -H "Authorization: Basic $(printf "%s:%s" "$UPRESS_WP_APP_USER" "$UPRESS_WP_APP_PASS" | base64 | tr -d '\n')" \
  "${UPRESS_WP_REST_BASE}/wp/v2/users/me"
```

Expected: HTTP 200 + JSON body with `id:373, slug:"agent", name:"agent"`.

### Rotation procedure
1. Log into `https://www.nimrod.bio/wp-admin/` as user `agent` (or admin user with edit-users permission).
2. Users → Profile (or All Users → agent) → scroll to **Application Passwords**.
3. Revoke the old `sfa-pipeline` entry. Create a new one with the same label.
4. Copy the 24+5-char value (shown ONCE).
5. Update `/Users/nimrod/Documents/SmallFarmsAgents/.env` on Mac.
6. Sync to server (canonical script — see §6 "Mac→server sync"):
   ```bash
   # team_100 / team_00 only
   ssh nimrodw@waldhomeserver "..." # see §6 for full command
   ```
7. Run auth smoke (above).
8. Backups created automatically: `.env.bak.<DATE>_wp007_creds` on each side.

---

## 4. uPress mu-plugin (REQUIRED — manual install)

uPress shared hosting **rejects** non-image uploads via `/wp/v2/media` by default — JSON, HTML, TXT all return HTTP 500 `אין לך הרשאות להעלות קבצים מהסוג הזה`. To allow JSON + HTML, a mu-plugin must be installed at the WordPress filesystem level.

### Path
```
wp-content/mu-plugins/sfagent-allow-json.php
```

### Content
```php
<?php
/**
 * sfagent-allow-json.php — allow JSON + HTML uploads via WP REST API
 * For SFA-S002-P001-WP007 (price index publish pipeline)
 */

function sfagent_allow_extra_mimes($mime_types) {
    $mime_types['json'] = 'application/json';
    $mime_types['html'] = 'text/html';
    $mime_types['htm']  = 'text/html';
    return $mime_types;
}
add_filter('upload_mimes', 'sfagent_allow_extra_mimes');

function sfagent_fix_filetype_check($data, $file, $filename, $mimes) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if ($ext === 'json') {
        $data['ext']  = 'json';
        $data['type'] = 'application/json';
    } elseif (in_array($ext, ['html', 'htm'])) {
        $data['ext']  = $ext;
        $data['type'] = 'text/html';
    }
    return $data;
}
add_filter('wp_check_filetype_and_ext', 'sfagent_fix_filetype_check', 10, 4);
```

### Install procedure (the only working path — 2026-05-07)
**uPress panel → File Manager** (File Manager is the only viable path; FTP-based installation does NOT work because Bezeq blocks port 21 outbound).

1. Log in to uPress panel (`https://panel.upress.co.il` or equivalent).
2. Open File Manager → navigate to the WordPress installation root → `wp-content/`.
3. If `mu-plugins/` does not exist, create the directory.
4. Inside `mu-plugins/`, create a new file `sfagent-allow-json.php`.
5. Paste the PHP content above. Save.

### Smoke test (verify mu-plugin works)
From `waldhomeserver`:

```bash
echo '{"smoke":"test"}' > /tmp/sfa_smoke.json
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST \
  "${UPRESS_WP_REST_BASE}/wp/v2/media" \
  -H "Authorization: Basic $(printf "%s:%s" "$UPRESS_WP_APP_USER" "$UPRESS_WP_APP_PASS" | base64 | tr -d '\n')" \
  -H 'Content-Disposition: attachment; filename="sfa-smoke.json"' \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/sfa_smoke.json
```

Expected: **HTTP 201** (Created). Use the returned `id` for cleanup:
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X DELETE \
  "${UPRESS_WP_REST_BASE}/wp/v2/media/<id>?force=1" \
  -H "Authorization: Basic <token>"
```

### Failure modes
- HTTP 500 `אין לך הרשאות` → mu-plugin missing or not loaded (mu-plugins auto-load; ensure the file is at the exact path above and PHP-syntax-valid).
- HTTP 401 → credentials issue (re-run auth smoke from §3).
- HTTP 200 from `/users/me` but 500 from `/media` POST → mu-plugin specifically not loaded.

---

## 5. WordPress option — manifest URL pointer

Architecture: per-month WP media library URLs change (date-based path), so the shortcode does NOT hard-code asset URLs. Instead:

1. Pipeline uploads a small `sfagent-manifest-of-urls.json` to media library.
2. `wp_shortcode_install.py --set-mou-url <returned-url>` writes the URL into WP option `sfagent_manifest_of_urls_url` via `/wp/v2/settings`.
3. Shortcode `wp_remote_get`s the pointer URL → dereferences to actual artifact URLs.

### Option visibility (must be registered)
The WP option must be registered before `/wp/v2/settings` will accept it. Add to active theme's `functions.php` or as a separate mu-plugin:

```php
add_action('rest_api_init', function () {
    register_setting('options', 'sfagent_manifest_of_urls_url', [
        'show_in_rest' => true,
        'type'         => 'string',
        'default'      => '',
        'sanitize_callback' => 'esc_url_raw',
    ]);
});
```

This is one of the steps in `_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`.

### Update procedure
After every successful publish:
```bash
# url printed by run_publisher --upload
python scripts/wp_shortcode_install.py --set-mou-url "https://www.nimrod.bio/wp-content/uploads/2026/05/sfagent-manifest-of-urls.json"
```

---

## 6. Mac→server credential sync (canonical script)

**Run this from Mac when credentials are rotated.** Uses SSH stdin to avoid command-line exposure of values.

```bash
SRC=/Users/nimrod/Documents/SmallFarmsAgents/.env
WP_REST_BASE=$(grep -E "^UPRESS_WP_REST_BASE=" "$SRC" | head -1 | cut -d= -f2-)
WP_USER=$(grep -E "^UPRESS_WP_APP_USER=" "$SRC" | head -1 | cut -d= -f2-)
WP_PASS=$(grep -E "^UPRESS_WP_APP_PASS=" "$SRC" | head -1 | cut -d= -f2-)

ssh nimrodw@waldhomeserver "WP_REST_BASE='$WP_REST_BASE' WP_USER='$WP_USER' WP_PASS='$WP_PASS' bash -s" <<'REMOTE'
set -e
update_or_append() {
  local file="$1" key="$2" val="$3"
  if grep -qE "^${key}=" "$file" 2>/dev/null; then
    awk -v k="$key" -v v="$val" -F= '$1==k{print k"="v; next} {print}' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
  else
    printf "%s=%s\n" "$key" "$val" >> "$file"
  fi
}
for DST in /data/projects/smallfarmsagents/.env /data/projects/shaked-wg-agent/.env; do
  [ ! -f "$DST" ] && continue
  cp "$DST" "${DST}.bak.$(date +%Y%m%d_%H%M%S)_creds"
  update_or_append "$DST" UPRESS_WP_REST_BASE "$WP_REST_BASE"
  update_or_append "$DST" UPRESS_WP_APP_USER "$WP_USER"
  update_or_append "$DST" UPRESS_WP_APP_PASS "$WP_PASS"
  chmod 600 "$DST"
done
# verify auth
TOKEN=$(printf "%s:%s" "$WP_USER" "$WP_PASS" | base64 | tr -d '\n')
curl -s -o /dev/null -w "auth: HTTP %{http_code}\n" --max-time 10 \
  "${WP_REST_BASE}/wp/v2/users/me" -H "Authorization: Basic $TOKEN"
REMOTE
```

Expected final line: `auth: HTTP 200`.

---

## 7. Network reachability table (waldhomeserver, 2026-05-07)

| Target | Port | Status | Notes |
|--------|------|--------|-------|
| `185.201.148.144` (uPress) | 443 | OPEN ✓ | WP REST primary path |
| `ftp.s887.upress.link` | 21 | **BLOCKED** | Bezeq egress block |
| Same | 22 (SFTP) | BLOCKED | uPress shared hosting blocks SFTP |
| Same | 990 (FTPS implicit) | BLOCKED | Bezeq egress block |
| Same | 2222 (alt FTP) | BLOCKED | Bezeq egress block |
| `1.1.1.1` | 443 | OPEN | clatd IPv4 NAT64 OK |
| `ipv6.google.com` | 443 | OPEN | IPv6 native |

This table is **correct as of 2026-05-07** under Bezeq be IPv6-only fiber WAN. Re-run from `waldhomeserver` after any ISP / network change. team_99 contract IR#15 + ADR048 covers WAN dual-stack verification.

---

## 8. Two FTP accounts (defensive fallback only)

Stored in `.env.upress` on Mac and `.env` on server (FTPS section):

| Account | Scope | When useful |
|---------|-------|-------------|
| `AgentsRoot@nimrod.bio` | WordPress filesystem root | Plugin install, file management — only if running from a non-Bezeq network |
| `HomeServer@nimrod.bio` | Internal directory under WP uploads | Pipeline FTPS upload — only if `UPRESS_FALLBACK_FTPS=1` AND port 21 reachable |

Both are **dormant** in current production. They are NOT used by the daily publish pipeline.

---

## 9. Daily operations checklist

For team_99 / team_60 ops review (weekly):

- [ ] `pipeline_alerts` table on production DB — zero entries with `level=ERROR` and category `upload`.
- [ ] `https://www.nimrod.bio/wp-content/uploads/<YYYY>/<MM>/sfagent-manifest-of-urls.json` HTTP 200.
- [ ] `https://www.nimrod.bio/SmallFarmsAgent` HTTP 200, page renders today's `artifact_version` (within 24h).
- [ ] Per-collector freshness — no source >3 consecutive days failed.
- [ ] uPress WP login still works (verify quarterly minimum).
- [ ] Application password not nearing rotation deadline (WP doesn't expire them — but rotate annually as policy).

---

## 10. Cross-references

| Document | Role |
|----------|------|
| [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md) | Pre-publish review checklist (operator-facing) |
| [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md) | Public publish runbook |
| [`WALD_HOME_SERVER_AGENT_COMMUNICATION.md`](WALD_HOME_SERVER_AGENT_COMMUNICATION.md) | Server connectivity + agent comms |
| [`docs/UPRESS_WORDPRESS_STANDARD_v2.md`](../../docs/UPRESS_WORDPRESS_STANDARD_v2.md) | uPress hosting normative spec (cross-project) |
| [`docs/UPRESS_WORDPRESS_AGENT_PLAYBOOK.md`](../../docs/UPRESS_WORDPRESS_AGENT_PLAYBOOK.md) | Agent playbook for uPress operations |
| [`_aos/work_packages/S002/SFA-S002-P001-WP007/LOD400_spec.md`](../../_aos/work_packages/S002/SFA-S002-P001-WP007/LOD400_spec.md) | LOD400 spec for the migration WP |
| [`_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md`](../../_COMMUNICATION/team_10/SFA-S002-P001-WP007/DEPLOY_HANDOFF.md) | Deploy hand-off (mu-plugin PHP, register_setting PHP, smoke procedure) |
| [`_COMMUNICATION/team_99/SFA-S002-P001-WP007/DEPLOY_LOG_v1.0.0.md`](../../_COMMUNICATION/team_99/SFA-S002-P001-WP007/DEPLOY_LOG_v1.0.0.md) | team_99's first deploy attempt + diagnosis |

---

## 11. For future sessions — what to read first

If you are a new agent session in the SmallFarmsAgents domain and need to touch publish/upload code, env vars, or operations:

1. Read **this document** (`UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md`) end-to-end. Authoritative.
2. Read [`_aos/context/PROJECT_CONTEXT.md`](../../_aos/context/PROJECT_CONTEXT.md) for project-level context.
3. Confirm credentials still valid (§3 auth smoke).
4. Confirm mu-plugin still installed (§4 smoke).
5. Confirm network state matches §7 table (run probes if uncertain).

If any of (3)/(4)/(5) fail — STOP and surface to team_00 before changing code. Do NOT regenerate or rotate credentials without authorization.

---

*Authored 2026-05-07 by team_100 in session SFA-S002-P001 (Public Index Launch Readiness).*
