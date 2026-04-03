# Client Hub Standard — v1.1

**Version:** 1.1  
**Date:** 2026-04-09  
**Author:** Team 100 (Architecture) — SmallFarmsAgents project  
**Status:** Canonical — binding for all Agents OS projects  
**Scope:** Client Hub product only (content, structure, view deployment, feedback ingestion). Platform-agnostic — works with any hosting environment. Does NOT cover hosting environment specifics, team model, or gate procedures — those live in separate standards.

---

## 1. Vision and Goals

| Goal | Description |
|------|-------------|
| **Transparency** | The client sees in one place: where the project stands on the roadmap, what was delivered, what tasks are pending, and what decisions await their input. |
| **Decision tracking** | Every item requiring client input gets a stable ID, context, options, implications, and recommendation. Responses are ingested into a structured SSOT store. |
| **Reduced round-trips** | Less "what's happening?" — fewer lost threads across email, WhatsApp, and file shares. |
| **Formal complement** | Hub is a **view and coordination layer**; it does NOT replace formal deliverables (docx/PDF for signature) but links to and mirrors them. |
| **Replication** | Same folder structure, JSON schemas, build scripts, and CSS base apply to every new project with minimal renaming. |
| **Task visibility** | Maintenance, content, and pipeline tasks with priorities are visible alongside milestone progress. |

**Out of scope:** Team numbering, gate procedures, organizational governance, hosting environment configuration — all handled by separate standards per project.

---

## 2. Separation from Hosting / Deployment Environment

The Hub is a **platform-agnostic static product**. It can be deployed to any server or hosting service that can serve static files (managed WordPress hosting, VPS with Nginx/Apache, cloud storage with CDN, GitHub Pages, etc.).

If the project also has a hosting-environment standard (e.g. `UPRESS_WORDPRESS_STANDARD_v2.md` for WordPress projects on uPress), that standard governs the **how** of deployment — not the Hub's content or structure.

| Topic | Belongs to Hub (this standard) | Belongs to hosting / environment standard |
|-------|-------------------------------|------------------------------------------|
| Page structure, JSON schemas, feedback export | Yes | No |
| Stable decision IDs, SSOT ingest | Yes | No |
| Deployment transport (FTP, SCP, rsync, S3, CI/CD) | Only as deployment target | Yes |
| CMS-specific APIs (WordPress REST, `/wp-json`, etc.) | No | Yes (if applicable) |
| Server environment (Docker, WP-CLI, Node, etc.) | Not part of Hub | Yes |

**Rule:** When updating Hub **content** — edit JSON/templates in the repo. When updating **how you deploy** — follow the project's hosting/environment standard or runbook.

---

## 3. Logical Architecture

```
┌─────────────────────── Repo ───────────────────────┐
│                                                      │
│  hub/data/*.json ──► build script ──► hub/dist/      │
│                          ▲                           │
│  hub/ssot/responses/ ────┘                           │
│       ▲                                              │
│  ingest script ◄── exported JSON from browser        │
│                                                      │
└──────────────────────────────────────────────────────┘
         │ deploy (FTP / SCP / rsync / S3 / CI)
         ▼
  ┌── Hosting ──┐
  │  /hub-path/ │  ◄── Client browser (view-only, public)
  └─────────────┘
```

| Layer | Role | Notes |
|-------|------|-------|
| **View** | Static HTML/CSS/JS built from source and deployed to server | What the client opens in the browser; NOT an SSOT by itself. |
| **Data store** (`hub/data/`) | JSON files: decisions, roadmap, updates, tasks | Edited in repo; Git version = build source. |
| **SSOT receiver** (`hub/ssot/`) | Validated responses after ingestion (JSON + manifest) | When view and SSOT conflict — **SSOT wins**. |
| **Ingest** | Script that validates schema and decision IDs, writes to SSOT | Runs locally or in CI per project workflow. |
| **Formal assets** | docx/PDF in project-defined structure | Not replaced by Hub; Hub can link or mirror copies for viewing. |

---

## 4. Feature Catalog

### 4.1 Core — P0 (mandatory for every hub)

| ID | Feature | Description |
|----|---------|-------------|
| F-01 | **Landing page** | Entry point: summary, links to inner pages, recent updates. |
| F-02 | **Roadmap** | Milestones with status, current focus highlight, optional breakdown of active milestone. |
| F-03 | **Tasks** | Categorized task list with priority badges (high/medium/low) and status. Categories are project-defined (e.g. content, maintenance, pipeline). |
| F-04 | **Decisions / Open questions** | Accordion list; each item has stable ID, context, options, recommendation. Interactive form fields (choice + notes) for client input. |
| F-05 | **Updates log** | Timestamped short entries — what was sent, received, changed. |
| F-06 | **JSON feedback export** | Single button exports all decision answers from browser as a JSON file with `schemaVersion`, `exportType`, `exportTimestamp`, `respondent`, `answers[]`. |
| F-07 | **Ingest validation** | Ingest script rejects files with unknown decision IDs or missing required fields. |
| F-08 | **Search engine blocking** | `<meta name="robots" content="noindex, nofollow">` on all pages; `robots.txt` with `Disallow: /`. |
| F-09 | **Branding** | Footer on every page: **"Agents OS @ nimrod.bio"** with permanent WhatsApp link (`https://wa.me/972547776770`). |
| F-10 | **metadata.json** | Generated in `dist/` with `generatedAt`, `schemaVersion`, `project`. |

### 4.2 Recommended — P0.5

| ID | Feature | Description |
|----|---------|-------------|
| F-11 | **File mirroring** | Copy formal docs (docx/pdf/txt) to `dist/files/` so deliverable links work after deploy. Build flag: `--mirror-docs`. |
| F-12 | **Mockup links** | Link from a decision to a static mockup under `dist/mockups/` for client review. |
| F-13 | **Statistics cards** | Landing page cards showing milestone completion ratio, task completion ratio, current focus. |
| F-14 | **Deliverables list** | Dedicated section or page linking to formal documents with descriptions. |

### 4.3 Phase 1 — P1

| ID | Feature | Description |
|----|---------|-------------|
| F-15 | **Server-side feedback save** | Endpoint (e.g. PHP) accepts JSON POST with token auth, saves to `incoming/` on server. Reduces "download → email → ingest" friction. |
| F-16 | **Notifications** | Email or webhook when feedback is submitted. Requires infrastructure and auth. |

### 4.4 Future — P2

| ID | Feature | Description |
|----|---------|-------------|
| F-17 | **Internal dashboard** | Project-owner-only view (not client) — decision SLA, response rates. Separate from this standard. |

### 4.5 Security (cross-cutting)

- **View is always public** — no authentication required to read the hub.
- **Write operations require authentication** — server-side save (F-15) must validate a token. JSON export (F-06) is client-side only (no server auth needed for download).
- **No secrets in Git** — deployment credentials, tokens, passwords only in `.env.*` files (gitignored).
- **GDPR / data minimization** — Hub collects only decision choices and notes. No PII beyond respondent name.

---

## 5. Data Model

### 5.1 Decisions (`decisions.json`)

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Stable project-global ID. Recommended: `D-<PROJECT>-<NN>` or `D-<NN>`. |
| `titleHe` | Yes | Short title for the client. |
| `contextHe` | Recommended | Background and what decision is needed. |
| `optionsHe` | Recommended | Numbered options or free text. |
| `implicationsHe` | Optional | What happens if each option is chosen. |
| `recommendationHe` | Optional | Professional recommendation (non-binding). |
| `mockupHref` | Optional | Relative link to mockup under `dist/`. |
| `status` | Yes | `pending` / `answered` / `deferred`. |

Root object: `{ "schemaVersion": 1, "introHe": "...", "decisions": [...] }`

### 5.2 Roadmap (`roadmap.json`)

| Field | Required | Description |
|-------|----------|-------------|
| `currentFocusId` | Yes | ID of the currently active milestone. |
| `summaryHe` | Recommended | Short intro paragraph for the roadmap page. |
| `milestones[]` | Yes | Array of milestone objects. |
| `milestones[].id` | Yes | Stable ID (e.g. `M1`, `MILESTONE-M2`). |
| `milestones[].code` | Yes | Display code. |
| `milestones[].titleHe` | Yes | Milestone title. |
| `milestones[].status` | Yes | `completed` / `in_progress` / `not_started` / `blocked`. |
| `milestones[].detailHe` | Optional | Summary of what was done or is planned. |
| `currentFocusBreakdown` | Optional | Nested sections with tasks for the active milestone. |

Root object: `{ "schemaVersion": 1, "currentFocusId": "...", "milestones": [...] }`

### 5.3 Updates (`updates.json`)

| Field | Required | Description |
|-------|----------|-------------|
| `items[].id` | Yes | Stable ID (e.g. `U-001`). |
| `items[].date` | Yes | ISO date string. |
| `items[].titleHe` | Yes | Short headline. |
| `items[].bodyHe` | Yes | Brief description. |

Root object: `{ "schemaVersion": 1, "items": [...] }`

### 5.4 Tasks (`tasks.json`)

| Field | Required | Description |
|-------|----------|-------------|
| `sections[].id` | Yes | Category ID (e.g. `content-updates`, `maintenance`). |
| `sections[].titleHe` | Yes | Category display name. |
| `sections[].tasks[]` | Yes | Array of task objects. |
| `tasks[].id` | Yes | Stable ID (e.g. `CT-01`, `MT-01`). |
| `tasks[].titleHe` | Yes | Task title. |
| `tasks[].status` | Yes | `completed` / `in_progress` / `not_started` / `blocked`. |
| `tasks[].priorityHe` | Recommended | Display priority in locale language. |
| `tasks[].stateHe` | Optional | Current state description. |

Root object: `{ "schemaVersion": 1, "sections": [...] }`

### 5.5 Feedback Export (browser-generated file)

Required fields in the exported JSON:

| Field | Required | Description |
|-------|----------|-------------|
| `schemaVersion` | Yes | Integer (current: `1`). |
| `exportType` | Yes | Fixed string per project (e.g. `sfa-feedback`, `eyal-feedback`). |
| `exportTimestamp` | Yes | ISO-8601 string. |
| `respondent` | Yes | Name of the person submitting. |
| `answers[]` | Yes | Array of `{ id, choice, notes }`. At least one of `choice`/`notes` must be non-empty. |

Ingestion **fails** if any `answers[].id` is not found in `decisions.json` or a required field is missing.

### 5.6 SSOT Manifest (`hub/ssot/manifest.json`)

```json
{
  "schemaVersion": 1,
  "ingestedExports": [
    {
      "file": "responses/2026-04-09--sfa-feedback--nimrod--a1b2c3d4e5.json",
      "ingestedBy": "nimrod",
      "exportTimestamp": "2026-04-09T14:30:00Z"
    }
  ],
  "lastIngestIso": "2026-04-09T14:30:00Z"
}
```

---

## 6. SSOT Workflow

### 6.1 Definitions

| Term | Meaning |
|------|---------|
| **View** | HTML/CSS/JS files built to `dist/` and deployed to the server — what the client sees in the browser. |
| **SSOT** | JSON files under `hub/ssot/` after **validated ingestion**. |
| **Decision ID** | Every decision must have a stable `id` present in both `decisions.json` and feedback exports. |

**Conflict rule:** If there is a gap between view and SSOT — **SSOT wins**. Rebuild after updating SSOT.

### 6.2 When to Rebuild and Deploy

- Change to any `hub/data/*.json` file.
- After ingesting feedback into `hub/ssot/responses/`.
- Change to `hub/src/` templates or CSS.

### 6.3 Feedback Flow

1. Client opens the hub in browser, navigates to decisions page.
2. Client fills choice/notes for each decision, clicks **"Export all answers to JSON"**.
3. Browser downloads a single JSON file (no server round-trip).
4. File is transferred to the team (email, Drive, or server-side `incoming/` if F-15 is active).
5. Team runs ingest:
   ```
   python3 scripts/ingest_<project>_feedback_json.py path/to/export.json --by "Name"
   ```
6. Ingest validates schema, `exportType`, decision IDs; writes to `hub/ssot/responses/` and updates `manifest.json`.
7. Commit to repo — never overwrite SSOT without Git trace.
8. Optionally rebuild and redeploy to reflect updated statuses in the view.

---

## 7. Replication Checklist (New Project)

When creating a hub for a new project:

1. **Copy structure** — `hub/data/`, `hub/src/` (templates, CSS, JS), `hub/ssot/`.
2. **Rename identifiers** — Decision ID prefix (e.g. `D-SFA-` → `D-NEWPROJECT-`), `exportType` string, project name in `metadata.json`.
3. **SSOT directory** — Initialize `hub/ssot/manifest.json` and empty `responses/`.
4. **Scripts** — Copy and rename `build_*_client_hub.py`, `deploy_*_client_hub.py`, `ingest_*_feedback_json.py`. Update paths and project-specific constants. The deploy script is project-specific — choose the transport appropriate for your hosting (FTP, SCP, rsync, S3, CI/CD pipeline, etc.).
5. **Environment** — Add hub deployment path to the project's `.env` file (e.g. `HUB_DEPLOY_PATH=my-hub`). If the project has a hosting standard, reference it for deployment setup — do NOT duplicate environment config inside the Hub.
6. **Documentation** — Link from project entry point to hub location and SSOT workflow.
7. **Formal/Hub canon** — Document at project level what must be formal (docx/PDF) vs what is Hub-only.
8. **CSS** — Use `hub-base.css` as the foundation. Add project-specific overrides in a separate file or inline.
9. **Branding** — All hubs carry the standard footer (see S10).

---

## 8. Operations (Logical Roles)

This standard does NOT assign team numbers. It defines **actions** required for a healthy hub lifecycle. Who performs each action is defined by the project's own governance.

| Action | Description |
|--------|-------------|
| **Content editing** | Update `hub/data/*.json` (decisions, roadmap, updates, tasks). |
| **Build** | Run build script to generate `dist/`. |
| **Deploy** | Upload `dist/` to server per project's deployment method (FTP, SCP, rsync, S3, CI/CD). |
| **Feedback ingest** | Run ingest script on exported JSON; update `hub/ssot/`. |
| **Pre-delivery check** | Verify pages render, export works, search blocking active. |

**Security reminder:** No secrets (deployment credentials, tokens, passwords) in JSON files committed to Git. Use `.env.*` files per project convention.

---

## 9. Deployment and Environment

### 9.1 Hub is Platform-Agnostic

The Hub is a **static site** (HTML, CSS, JS, JSON). It does NOT require any specific CMS, framework, or hosting platform. Valid deployment targets include:

- **Managed WordPress hosting** (uPress, WP Engine, etc.) — deploy to a subfolder alongside WordPress
- **VPS / dedicated server** — deploy via SCP, rsync, or FTP to any web-accessible directory
- **Cloud storage** (S3 + CloudFront, GCS, Azure Blob) — serve as a static website
- **CI/CD platforms** (GitHub Pages, Netlify, Vercel) — build and deploy from repo
- **Local preview** — `python3 -m http.server` in `dist/` for development

### 9.2 Deploy Script Pattern

Each project provides its own deploy script (`deploy_*_client_hub.py` or equivalent) appropriate for its hosting. The script MUST:

1. Read `dist/` directory (fail if not built)
2. Read deployment target path from environment variable (`.env.*` file)
3. Support `--dry-run` flag
4. Print summary of uploaded files and target URL

### 9.3 Environment Variables

Hub-specific env vars follow the pattern:

| Variable | Purpose | Example |
|----------|---------|---------|
| `<PROJECT>_HUB_PATH` | Remote path for deployment | `sfa-hub`, `ea-eyal-hub` |
| `<PROJECT>_HUB_URL` | Public URL (optional, for logging) | `https://nimrod.bio/sfa-hub/` |

Transport-specific variables (FTP host, SSH key, S3 bucket, etc.) are defined by the project's hosting standard, NOT by this Hub standard.

### 9.4 CMS Integration (Optional)

If the project includes a CMS (WordPress, etc.), automation around the CMS (content import, smoke tests, REST API calls) is governed by the project's hosting/environment standard — NOT by this Hub standard. The Hub and the CMS are independent products that share a server.

---

## 10. Branding

Every hub page footer MUST include:

```html
<footer class="hub-brand">
  <a href="https://wa.me/972547776770" target="_blank" rel="noopener">
    Agents OS @ nimrod.bio
  </a>
</footer>
```

- The WhatsApp link is permanent: `https://wa.me/972547776770`
- The text "Agents OS @ nimrod.bio" is the standard brand mark.
- Additional project-specific footer text (build timestamp, disclaimers) appears ABOVE the brand footer.

---

## 11. CSS Standard

### 11.1 Shared Base (`hub-base.css`)

All hubs MUST use the shared base CSS file. It defines:

- **CSS custom properties** (`:root` variables for colors, spacing, typography)
- **Fonts:** Heebo (UI text, sans-serif) + Frank Ruhl Libre (headings, serif). Loaded from Google Fonts.
- **Direction:** Default is `dir="rtl"` (Hebrew). For LTR projects, set `dir="ltr"` on `<html>` and override relevant CSS rules in the project layer.
- **Core components:** `.wrap`, `nav`, `table.data`, `.badge-*`, `.card`, `.callout`, `.decision-detail`, `.task-row`, `.stat-card`, `.hub-brand`, form fields.
- **Responsive:** Mobile-first with breakpoint at 640px.
- **Print:** Nav hidden, full width, badge borders.

### 11.2 Project Layer

Each project MAY add a thin CSS file that overrides variables or adds project-specific components. The base MUST NOT be modified per-project — fork only if contributing back upstream.

### 11.3 Status Badges

Standard badge classes and their Hebrew labels:

| Class | Label | Use |
|-------|-------|-----|
| `.badge-done` | הושלם | Completed |
| `.badge-run` | בביצוע | In progress |
| `.badge-todo` | לא התחיל | Not started |
| `.badge-blocked` | חסום | Blocked |
| `.badge-qa` | QA | Under QA review |
| `.badge-pending` | ממתין | Awaiting input |
| `.badge-high` | גבוהה | High priority |
| `.badge-medium` | בינונית | Medium priority |
| `.badge-low` | נמוכה | Low priority |

---

## 12. Product Roadmap (Hub Platform)

| Phase | Content |
|-------|---------|
| **P0** (current) | Full static site + JSON export + ingest + SSOT + noindex + branding. Tasks page with priorities. |
| **P1** | Server-side feedback save; notifications; accessibility improvements; i18n hooks. |
| **P2** | Internal dashboard; unified build/publish CLI across projects (single configurable tool). |

---

## 13. Appendix A — Field Naming Convention

- **JSON field names** are always English: `titleHe`, `contextHe`, `optionsHe`, `stateHe`.
- The locale suffix (`He`, `En`, `Ar`, etc.) indicates the content language. This enables i18n by adding `titleEn`, `titleAr`, etc.
- For projects with a single locale, the suffix is still mandatory for forward compatibility.
- **Technical fields** (IDs, statuses, schema versions) have no locale suffix: `id`, `status`, `schemaVersion`, `exportType`.
- **Folder and file names** are English with kebab-case or snake_case: `hub/data/decisions.json`, `hub/ssot/manifest.json`.

---

## 14. Appendix B — Reference Implementations

| Project | Hosting | Hub Location | Build Script | Deploy Script | Ingest Script |
|---------|---------|-------------|-------------|--------------|--------------|
| SmallFarmsAgents | uPress (FTPS) | `hub/` | `scripts/build_sfa_client_hub.py` | `scripts/ftp_publish_sfa_client_hub.py` | `scripts/ingest_sfa_feedback_json.py` |
| Eyal Amit 2026 | uPress (FTPS) | `docs/project/eyal-client-hub/` | `scripts/build_eyal_client_hub.py` | `scripts/ftp_publish_eyal_client_hub.py` | `scripts/ingest_eyal_feedback_json.py` |

> Future projects may use different hosting (VPS, cloud, CI/CD). Deploy scripts will differ — but the build script, data model, feedback export, SSOT workflow, and CSS base remain the same.

---

*End of standard. For WordPress/uPress-specific hosting procedures, see `UPRESS_WORDPRESS_STANDARD_v2.md` (applies only to projects on that platform). For project-specific governance, see each project's `_COMMUNICATION/ROADMAP.md` or equivalent.*
