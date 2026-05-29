# WordPress public page (nimrod.bio) — publish runbook

> **⛔ SUPERSEDED — historical record only.** Describes the retired WordPress page on **`www.nimrod.bio`** (S002 / M10 era), **severed 2026-05-28**. The live public site is the Slim/PHP delivery tier on **uPress `sfa.nimrod.bio`** — see [`../02-architecture/sfa-delivery-tier.md`](../02-architecture/sfa-delivery-tier.md) and [`UI_DEPLOY_RUNBOOK.md`](UI_DEPLOY_RUNBOOK.md).

**Goal:** Put the OrganicMarketAgent **public report** on the existing WordPress site as a **new page** (initially **not** in the menu), with a process that is **simple, stable, accurate**, and **fully automatable** after one-time setup.

**Architecture (locked):** Local hub builds **static artifacts** → upload to hosting → WordPress **reads files only** (no live DB to WordPress). See [`PROJECT_VISION_AND_SYSTEM_MAP.md`](../01-overview/PROJECT_VISION_AND_SYSTEM_MAP.md).

### Canonical public page (what users open)

The **primary end-user URL** for the market index on nimrod.bio is the **WordPress page** (Flatsome header/footer + page content area), not the raw static file:

- **Example:** `https://www.nimrod.bio/smallfarmsagent/` (slug may vary; see `UPRESS_PAGE_SLUG` in `.env`).
- **Content:** The page body contains the shortcode `[sfagent_market_report]` (installed via [`scripts/wp_shortcode_install.py`](../../scripts/wp_shortcode_install.py)). PHP reads **`wp-content/uploads/market/public_report_body.html`** and echoes it. Shared layout/CSS comes from **`wp-content/themes/flatsome-child/sfagent-base.css`**, enqueued when that shortcode is present.
- **Implication:** UI/responsive work for “the public page” must target **`public_report_body.html` + `sfagent-base.css`**, then **FTPS-upload** both the uploads bundle **and** the child-theme CSS when it changes. The standalone `public_report.html` in `uploads/market/` is an alternate full-document URL; it is **not** the same shell as `/smallfarmsagent/`.

---

## 1. What the pipeline produces today

After a successful publish (local [`PublishEngine`](../../organic_market_agent/publisher/engine.py)):

| File | Role |
|------|------|
| `output/public/public_report_body.html` | **WordPress embed fragment** — inner markup for `/smallfarmsagent/` (and same shortcode); primary surface for themed public UX |
| `output/public/public_report.html` | Standalone RTL Hebrew full document (optional direct link to `uploads/market/public_report.html`) |
| `output/public/public_report.json` | Machine-readable index + `data_quality` |
| `output/public/manifest.json` | Small summary: dates, staleness, source counts, `data_quality` |

**Note:** The engine currently writes **fixed filenames** (overwrite each run). Versioned `public_report-{timestamp}.json` from the legacy spec is **not** implemented yet; adding it is a small M7 enhancement if you want CDN-friendly immutable URLs.

---

## 2. Recommended hosting layout on WordPress (uPress)

Use a **dedicated directory** under uploads (matches existing plan):

- **Remote base:** `wp-content/uploads/market/` (or the path uPress confirms in [U03](https://support.upress.co.il/dev/how-to-use-ftp/) validation).

**Files to upload each successful publish (minimum):**

1. `manifest.json` — last (or use atomic rename pattern: write `manifest.json.tmp` then rename to `manifest.json` if the host allows).
2. `public_report.json`
3. `public_report.html`

**Optional (spec / M7):** `manifest_last_good.json` — only updated when publish succeeds; WordPress or client reads it if `manifest.json` is missing or corrupt.

---

## 3. WordPress page — integration options (**no iframe**)

**iframe is excluded:** nested scrolling, small viewports, and accessibility issues rule it out for nimrod.bio.

### Option A — Standalone static URL + thin WordPress landing (recommended for first public cut)

1. Upload `public_report.html` to `uploads/market/` as today.
2. Create a new **Page** (not in menu): short Hebrew intro + primary button/link to  
   `https://nimrod.bio/wp-content/uploads/market/public_report.html`  
   (same tab or `target="_blank"` per your UX preference).

The report remains a **full document** with its own responsive CSS; mobile users get native browser scrolling, not a frame.

### Option B — Inline inside WordPress (M7 implementation target)

To show the report **inside** a normal WP page layout (theme header/footer, no separate document):

1. **Publisher change (Team 10):** emit an extra artifact, e.g. `public_report_body.html`, containing only the **inner body markup** (and either embedded `<style>` or a linked stylesheet you also upload).  
2. **WordPress:** a minimal **shortcode** or **custom page template** (child theme or small plugin) that `include`s or reads the file from `wp-content/uploads/market/public_report_body.html` and echoes it inside the page content area (sanitize/allow only trusted static HTML from your own pipeline).

This keeps one automated upload path and avoids iframe.

### Option C — Client-side render from JSON

Custom HTML + JS: fetch `manifest.json` + `public_report.json` and build the table in the DOM. Same-origin only; more code to maintain; duplicates presentation logic unless generated.

**Recommendation:** **Option A** immediately after FTPS works; plan **Option B** as part of **M7 Phase A** alongside FTPS automation.

---

## 4. Automation ladder (manual work vs “beyond obligation”)

| Tier | What runs | Manual steps |
|------|-----------|----------------|
| **0 — Today** | Local `full_data_refresh` / cron + `PublishEngine` → files in `output/public/` | Upload files via FTP client (FileZilla, etc.). |
| **1 — Scripted upload (recommended next)** | Same + `python` script using `ftplib.FTP_TLS` (see [`MANDATE_UPRESS_VALIDATION.md`](../../_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md)) | One-time: store credentials in `.env` (never commit); run U01–U07 from validation plan. |
| **2 — Cron on the Mac / server** | Daily: ingest → aggregate → publish → FTPS upload | None on success; alerts on failure (already have `pipeline_alerts`). |
| **3 — GitHub** | Optional: Action uploads `output/public/*` from a **release artifact** or **scheduled workflow** that does **not** replace the live DB-backed hub — only if you want off-machine backup/publish. | Extra secrets in GitHub; second source of truth risk — use only if clearly owned by ops. |

**Target state for “no unnecessary manual work”:** **Tier 2** — credentials on the machine that runs the pipeline; **one-time** WordPress page creation (Option A landing, then Option B when body-fragment + shortcode exist); **no** daily WP login.

### Production home server (waldhomeserver)

The **staging/production** OrganicMarketAgent host at `/data/projects/smallfarmsagents` runs the **daily scheduler** (`organic_market_agent.scheduler.runner`). For nimrod.bio to receive **automatic** FTPS uploads after each successful publish, set **`scheduler_config.upload_enabled = true`** (Flask admin → **Scheduler** page, or SQL on the single `scheduler_config` row). This is independent of developer laptops (which should not run unattended ingestion).

**Path parity (mandatory):** FTPS must write to the **same directory** WordPress reads for the shortcode: **`UPRESS_UPLOAD_PATH=wp-content/uploads/market`**. **`UPRESS_PUBLIC_BASE`** must include the WordPress subdirectory: `https://www.nimrod.bio/Agents` — uPress physically installs WordPress under `/Agents/` (capital A, case-sensitive Linux server). FTP root = WordPress root = that directory, so public artifacts are reachable at `https://nimrod.bio/Agents/wp-content/uploads/market/`. Do NOT use the bare domain root (`https://www.nimrod.bio`) — that omits `/Agents` and produces wrong `upload_base` values in `manifest.json`. Note: WordPress pages still live at the domain root (`https://www.nimrod.bio/SmallFarmsAgent`) because WordPress is configured with a separate Site URL; only the `UPRESS_PUBLIC_BASE` for upload artifacts must include `/Agents`. A previous misconfiguration used a separate FTP tree (`/sfa`) which caused “good data on FTP / stale JSON over HTTPS” symptoms — `UPRESS_UPLOAD_PATH` and `UPRESS_PUBLIC_BASE` must stay aligned.

**Cache:** uPress **CDN / ezCache** may serve an older `manifest.json` after upload even when FTP `LIST` shows a fresh `manifest.json` (different `Last-Modified` / `content-length` over HTTPS vs FTP). **Always** compare FTP `RETR manifest.json` to `output/public/manifest.json` first; if they match but HTTPS is stale, purge cache. **Options:** (1) uPress panel → ezCache / site cache purge; (2) WordPress REST `POST /wp-json/ezcache/v1/cache` with `{"action":"purge"}` and an Application Password (see [`docs/UPRESS_WORDPRESS_STANDARD_v2.md`](../../docs/UPRESS_WORDPRESS_STANDARD_v2.md)); (3) pipeline host `.env`: `UPRESS_EZCACHE_PURGE_AFTER_UPLOAD=1` plus `UPRESS_WP_REST_BASE`, `UPRESS_WP_APP_USER`, `UPRESS_WP_APP_PASS` — [`ftps_upload.py`](../../organic_market_agent/publisher/ftps_upload.py) calls purge after a successful upload (may return HTTP 403 from some client networks; then use the panel). Optional: `UPRESS_VERIFY_PUBLIC_MANIFEST=1` logs a warning when public JSON still lags after purge.

After a run, verify **`TAG_FTPS_UPLOAD_SUCCESS`** in logs / `pipeline_alerts` and **`last_published_at`** in the public manifest once cache has caught up.

---

## 5. Stability and accuracy checks

1. **Pre-publish:** [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md) (local artifacts + manifest).
2. **Post-upload:** `curl -I` / browser open the three URLs; confirm `Cache-Control` / CDN behaviour (document TTL per [`docs/UPRESS_VALIDATION_PLAN_HE.md`](../../docs/UPRESS_VALIDATION_PLAN_HE.md) U-cache tests when run).
3. **Stale logic:** Already embedded in `public_report.html` from `PublishEngine` (banner thresholds per product context).
4. **Fallback:** When `manifest_last_good` exists, teach the WP page (or script) to prefer it if main manifest fails — **Phase A M7** item in [`ROADMAP.md`](../../_COMMUNICATION/ROADMAP.md).

---

## 6. Roadmap alignment (M7 / G7)

Full **FTPS inside `PublishEngine`**, **U01–U12** tests, and **G7 sign-off** are formally **M7** per roadmap. This runbook does **not** replace the mandate:

- [`_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md`](../../_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md)
- [`docs/UPRESS_VALIDATION_PLAN_HE.md`](../../docs/UPRESS_VALIDATION_PLAN_HE.md)

**Practical path for Nimrod now:** validate **U01–U03 + U07** (login, FTPS, write path, public URL), create the **WP landing page** (Option A — link to static HTML, **no iframe**), then add a **small upload script** called from the same shell that already runs publish — incrementally approaches M7 without blocking a soft launch.

---

## 7. Milestone note — M6 complete, M7 eligible

Per [`_COMMUNICATION/ROADMAP.md`](../../_COMMUNICATION/ROADMAP.md) (v1.8): **M6 — Automation + Resilience** is marked **COMPLETE** with **G6 PASS** (Team 100 arch reference: `ARCH-20260331-G6-PASS-M6-COMPLETE`; Team 50: [`_COMMUNICATION/TEAM_50/reports/2026-03-31_QA_G6_TEAM50.md`](../../_COMMUNICATION/TEAM_50/reports/2026-03-31_QA_G6_TEAM50.md)).

**M7** may proceed under roadmap rules once **Nimrod explicit approval** for go-live work is recorded (G7 still requires QA + Nimrod sign-off at the end).

---

## 8. References

| Document | Path |
|----------|------|
| Publish checklist | [`PUBLISH_CHECKLIST.md`](PUBLISH_CHECKLIST.md) |
| Baseline / metrics (ops) | [`BASELINE_VERSIONING.md`](BASELINE_VERSIONING.md) |
| Roadmap M7 / G7 | [`_COMMUNICATION/ROADMAP.md`](../../_COMMUNICATION/ROADMAP.md) |
| Team 10 uPress mandate | [`_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md`](../../_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md) |

---

*Last updated: 2026-04-17.*
