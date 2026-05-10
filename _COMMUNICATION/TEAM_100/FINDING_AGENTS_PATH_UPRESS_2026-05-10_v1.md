# FINDING: UPRESS_PUBLIC_BASE — "Agents" Path Analysis

**From:** team_100 (Chief Architect)
**To:** nimrod-bio team_100 (originator of finding)
**Date:** 2026-05-10
**Ref:** nimrod-bio backup scan 2026-05-09 finding — `Agents/` (capital A) path
**Status:** RESOLVED — documented, no corrective action required on production pipeline

---

## 1. Finding Summary (from nimrod-bio)

Files published at:
```
https://nimrod.bio/Agents/wp-content/uploads/market/
```
(capital A — case-sensitive Linux server)

Claim: `Agents/` (capital A) may conflict with intended lowercase `agents/`.

---

## 2. Current Configuration (verified 2026-05-10)

| Variable | Value | Source |
|----------|-------|--------|
| `UPRESS_PUBLIC_BASE` | `https://nimrod.bio` | `.env.upress` line 31 |
| `UPRESS_UPLOAD_PATH` | `wp-content/uploads/market` | `.env.upress` line 35 |
| `UPRESS_WP_REST_BASE` | `https://www.nimrod.bio/wp-json` | `.env.upress` line 60 |
| `upload_base` in manifest | `https://nimrod.bio/wp-content/uploads/market` | `engine.py:167` (computed) |

Note: `.env.upress` comment at line 34 confirms: "FTP root = WordPress root (no public_html/)"

---

## 3. Root Cause Analysis

### Why `Agents/` appears in the actual URL

WordPress is installed in a **subdirectory named `Agents/`** on the uPress server (capital A). The FTP user `mezoohost@nimrod.bio` is chrooted to that directory. Therefore:

- FTP root = `<server>/Agents/`
- Files at FTP path `wp-content/uploads/market/` are publicly accessible at `https://nimrod.bio/Agents/wp-content/uploads/market/`
- `UPRESS_WP_REST_BASE=https://www.nimrod.bio/wp-json` works because WordPress is configured with separate "WordPress Address URL" (under `/Agents/`) and "Site URL" (root), which is a standard WordPress subdirectory-serving-from-root setup

### Is `Agents` (capital A) intentional or a typo?

**It is intentional and structural** — it is the actual filesystem directory where WordPress is installed on the uPress shared hosting server. It was never a user-configurable value in this codebase; it reflects the server-side directory name created during WordPress installation on uPress.

The lowercase `agents/` seen in CHANGELOG 2026-04-11 was a **URL reference** from Team 61 validation (`nimrod.bio/agents/`) — a different path used at that time for a different feature (Famely Newsletter integration). It was never the WordPress installation directory itself.

The CHANGELOG 2026-04-18 entry ("legacy `sfa` / `agents/sfa` removed from active use") refers to old FTPS upload sub-paths within the WordPress uploads directory — not to the WordPress installation directory.

---

## 4. Impact Assessment

### Production pipeline: NO IMPACT

The current primary upload path is **WP REST API** (`wp_upload.py`):
- `upload_artifact()` POSTs to `https://www.nimrod.bio/wp-json/wp/v2/media`
- WordPress returns `source_url` in its response — this is WordPress's own canonical URL, correctly including the `/Agents/` component
- The `manifest-of-urls.json` (AC-04 Option A) is built from these `source_url` values — **correct**
- The WordPress shortcode reads `sfagent_manifest_of_urls_url` option → dereferences the manifest → uses WordPress media URLs — **correct**

### `upload_base` in `manifest.json`: INFORMATIONAL FIELD, INCORRECT

`engine.py:167` computes:
```python
upload_base = config.UPRESS_PUBLIC_BASE.rstrip("/") + "/" + config.UPRESS_UPLOAD_PATH
# → "https://nimrod.bio/wp-content/uploads/market"
```
This is **technically wrong** (missing `/Agents`). However:
- No production consumer resolves artifact URLs from `upload_base`
- The manifest-of-urls (`sfagent-manifest-of-urls.json`) holds the true WordPress URLs
- This field is diagnostic/informational only

### FTPS fallback (disabled, `UPRESS_FALLBACK_FTPS=0`): NO IMPACT

`UPRESS_UPLOAD_PATH=wp-content/uploads/market` is relative to FTP chroot (= WordPress root = `Agents/` on server). FTPS uploads would land correctly at `Agents/wp-content/uploads/market/`. ✓

### `UPRESS_VERIFY_PUBLIC_MANIFEST` (disabled by default): WOULD FAIL IF ENABLED

This feature constructs `https://nimrod.bio/wp-content/uploads/market/manifest.json` for GET verification — missing `/Agents/`. If this feature is ever enabled, `UPRESS_PUBLIC_BASE` must be corrected first.

---

## 5. Decision

| Question | Answer |
|----------|--------|
| Is `Agents` (capital A) intentional? | **Yes** — physical WP install directory on uPress server |
| Is it a typo for `agents` (lowercase)? | **No** — different paths; `agents/` was a legacy upload sub-path, now removed |
| Does this affect production uploads? | **No** — WP REST pipeline uses WordPress `source_url` directly |
| Should `UPRESS_PUBLIC_BASE` be corrected? | **Recommended** (not urgent): add `/Agents` to make `manifest.json`'s `upload_base` accurate and to future-proof `UPRESS_VERIFY_PUBLIC_MANIFEST` |
| What should nimrod-bio do about the gitignore? | See §6 below |

---

## 6. Response to nimrod-bio Team 100

The `Agents/` (capital A) subdirectory on the nimrod.bio server is the **correct and intentional** WordPress installation location. It is not a duplicate of `agents/` (lowercase) — the lowercase variant was a legacy upload sub-path that was removed in April 2026.

For the **nimrod-bio gitignore deduplication**: the active path is `Agents/wp-content/uploads/market/`. The `agents/` (lowercase) directory, if it exists, is an empty legacy artifact and can be removed from the server (via FTP) or ignored.

---

## 7. Optional Corrective Action (non-urgent)

If team_00 approves, apply the following to `.env.upress` and `.env.example` on waldhomeserver:

```diff
- UPRESS_PUBLIC_BASE=https://nimrod.bio
+ UPRESS_PUBLIC_BASE=https://nimrod.bio/Agents
```

This corrects `manifest.json`'s `upload_base` field and enables `UPRESS_VERIFY_PUBLIC_MANIFEST` if ever needed. **No code changes required** — `engine.py:167` already computes `upload_base` correctly once this env var is accurate.

This change is a **documentation/env correction only** — zero production impact regardless of timing.

---

*Authored by team_100 (Chief Architect) — SmallFarmsAgents*
*Finding source: nimrod-bio team_100, 2026-05-10*
