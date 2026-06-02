---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-ALIGN_v1.0.1
title: team_99 — WP-CB-UI-ALIGN R2 re-deploy SUCCESS — V02 + V03 fixed live; V01 = origin 404 (code change required)
status: SUCCESS (V02 + V03); BLOCKED at code-side (V01)
date: 2026-06-02
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R2 evidence), team_50 (re-QA), team_00 (Principal)
parent_mandate: ../MSG-HUB-20260602-002.md (RE-DEPLOY R2 + V01 PDF)
parent_request: ./REQUEST_V01_pdf_export_404_2026-06-02_v1.0.0.md
prior_report: ./DEPLOY_REPORT_v1.0.0.md (R1)
wp: SFA-S003-P002-WP-CB-UI-ALIGN
branch: claude/wp-cb-ui-align-2026-06-02
deployed_sha: c1d9cff
deployed_includes: 78b66df (V02+V03 fix) + later docs-only commits (CLASSB intake + §9 decisions — no sfa_delivery code change)
---

# WP-CB-UI-ALIGN R2 — Deploy Report

## 1. Verdict

| Finding | Status after R2 deploy |
|---|---|
| **V02** crop-page enum/key humanization | ✅ **PASS** — verified live on `/crop-book/watermelon` |
| **V03** calc crop selector populated | ✅ **PASS** — 70 real crops with Hebrew labels |
| **V01** `/calc/export.pdf` 404 | ⚠ **BLOCKED at uPress origin** — code change needed (see §4) |

The R2 build is live at `c1d9cff` (which includes `78b66df`, the V02+V03 fix). team_50 can re-QA V02/V03 immediately. V01 needs a code-side URL scheme switch from team_10/team_100 before team_50 can close it.

## 2. Deploy summary

- **Host:** waldhomeserver (egress `46.235.231.114`, allowlisted on uPress s1240).
- **Branch:** `claude/wp-cb-ui-align-2026-06-02` → HEAD `c1d9cff`.
- **Build target reachable:** `78b66df` ("L-GATE_V R2 — humanize crop-page enums (V02) + populate calc selector (V03)") ✓ in history; the 2 commits after it are docs-only (`88b938d` MSG-002 fallback delivery, `c1d9cff` Class B §9 decisions) and do NOT change `sfa_delivery/`.
- **FTPS cred sync from earlier today held**: no 530 this round — first attempt succeeded.
- **lftp stats**: 5 files transferred · 5 replaced · exit 0. The diff surface matches V02/V03:
  - `app/Controllers/HubController.php`
  - `app/Lib/FieldRegistry.php` (enum humanization)
  - `templates/pages/book_crop.php` (V02 — crop page Hebrew)
  - `templates/pages/calc_dash.php` (V03 — calc selector)
  - `public_assets/js/crop-book-v1.js`
- **Deploy log on host:** `/tmp/sfa_cb_ui_align_R2_deploy.log`.

## 3. Smoke evidence (mandate §3, expanded)

### Baseline 5 surfaces (200 + `.sh` shell, no legacy chrome)

| URL | HTTP | `.sh` hits | legacy chrome refs |
|---|---|---|---|
| `/` | 200 | 1 | 0 |
| `/crop-book/` | 200 | 1 | 0 |
| `/calc/` | 200 | 1 | 0 |
| `/market/` | 200 | 1 | 0 |
| `/crop-book/watermelon` (real per-crop page used for V02) | 200 | (shell present) | 0 |

✅

### V02 — crop page Hebrew, no raw enum text — **PASS**

Probed `/crop-book/watermelon` (real per-crop page). Raw enum string hit-counts in the served HTML:

| token | hits | interpretation |
|---|---|---|
| `direct_seed` | 0 | ✅ |
| `half_hardy` | 0 | ✅ |
| `transplant_only` | 0 | ✅ |
| `hardy` | 0 | ✅ |
| `family:variety` | 0 | ✅ |
| `yield_per_bed_m` | **3** | ✅ — **all inside `data-field="yield_per_bed_m"` attributes** (programmatic field IDs for JS/QA hooks); the visible text in every case is proper Hebrew (`יבול / מ׳` / `יבול ממוצע למ׳` / `יבול/מ׳`). Not a V02 regression. |

Hebrew word count on the page (≥2 chars): **538+** — page renders Hebrew content properly.

### V03 — `/calc/` crop selector populated — **PASS**

```
<option value="">בחר גידול…</option>           ← placeholder (expected)
<option value="watermelon">אבטיח</option>
<option value="edamame">אדממה</option>
<option value="blackberry">אוסנה</option>
<option value="anise-hyssop">אזוב מצוי</option>
… (70 total real options)
```

✅ 70 non-placeholder crops, Hebrew labels, real slugs.

### Exports

| URL | HTTP |
|---|---|
| `/calc/export.csv` | 200 ✅ |
| `/calc/export.pdf` | 404 ⚠ (origin issue, see §4) |

## 4. V01 — `/calc/export.pdf` 404: **origin is genuinely 404** (no Cloudflare purge will help)

### Probe (Cloudflare-bypass via revalidation)

`waldhomeserver` cannot reach uPress origin directly (sfa.nimrod.bio is served by Cloudflare; the uPress origin IP is not exposed in public DNS). The closest substitute for a direct origin probe is to **force Cloudflare to revalidate** by sending `Pragma: no-cache`. The first probe of this session got:

```
curl -sI -H 'Pragma: no-cache' https://sfa.nimrod.bio/calc/export.pdf

HTTP/2 404
content-type: text/html
cache-control: max-age=14400
cf-cache-status: EXPIRED   ← Cloudflare's cached object had expired
cf-ray: a0563520ce0035c6-TLV
```

`cf-cache-status: EXPIRED` is the smoking gun. EXPIRED means:
1. Cloudflare had a cached entry (a prior 404).
2. The entry's TTL elapsed.
3. Cloudflare **re-fetched from the uPress origin**.
4. The origin's response was still **404**, so CF re-cached and returned it.

Subsequent probes returned `cf-cache-status: HIT` with `age: 0` — re-serving the just-refreshed origin response.

**Conclusion:** uPress is genuinely not routing `.pdf` to Slim. A Cloudflare purge would only force another origin fetch that returns 404 again. **No purge issued.**

### Likely root cause (uPress / Apache)

uPress shared hosting typically uses `mod_negotiation` / `MultiViews` / `mod_mime` / a static-file handler for common extensions. `/calc/export.pdf` is probably being short-circuited to "look for a literal `pdf` file on disk in `/calc/export.*`" rather than dispatched to `index.php` (Slim). Confirmation would require an SSH shell on the uPress account (not currently in scope for team_99) or a `.htaccess` change at the project root that explicitly rewrites `/calc/export.pdf` to Slim's front controller.

### Recommended remediation (per the mandate's branch)

Per `REQUEST_V01_pdf_export_404_2026-06-02_v1.0.0.md` decision-tree:

> **Origin 404** → uPress is not routing `.pdf` to Slim → report what intercepts it; team_100 will then change the export URL scheme in code (e.g. `/calc/export?fmt=pdf`) to sidestep the extension.

→ **team_10 / team_100**: switch the PDF export link from `/calc/export.pdf` to `/calc/export?fmt=pdf` (route accepts `{fmt:csv|pdf}` already; the change is the link in the template + any controller arg parsing). After that change lands on the branch, I'll re-deploy and re-smoke.

### Optional hardening (also per request §"Recommended hardening")

Make `calcExport` always send `Cache-Control: no-store` so HTML / 404 error responses are never edge-cached again. Today's `max-age=14400` (4 hours) is the reason CF kept the stale 404 around long enough to cause this round.

## 5. What was touched / not touched (R2)

- ✅ Branch `claude/wp-cb-ui-align-2026-06-02` pulled to `c1d9cff` on server; `sfa_delivery/` mirrored to uPress.
- ✅ This `DEPLOY_REPORT_v1.0.1.md` written under the WP folder.
- ❌ No application-code edits, no `_aos/`, no `roadmap.yaml`, no deploy-script change, no Cloudflare purge.
- ❌ Server `.env` unchanged this round (the May 29 → today cred sync from R1 still holds).

## 6. Handoff

→ **team_100**: V02 + V03 are live; please push the V01 URL-scheme change (`?fmt=pdf`) when ready and I'll re-deploy in one more round.
→ **team_190**: V02/V03 are observable on `c1d9cff` live. R2 evidence package = §3 above; V01 evidence + remediation path = §4.
→ **team_50**: please re-QA V02 + V03 now. V01 remains BLOCKED-at-code; not your scope this round.
→ **team_00**: no human intervention needed.

— team_99 (OPS / waldhomeserver) 2026-06-02
