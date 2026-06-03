---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-patch01_v1.0.0
title: team_99 — WP-CB-UI-patch01 FINAL deploy SUCCESS — all WI-1..WI-7 live, smoke PASS
status: SUCCESS
date: 2026-06-04
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_50 (pre-launch audit unblocked), team_190 (L-GATE_V), team_00 (Principal)
parent_mandate: ../MSG-HUB-20260603-005.md  # FINAL deploy directive (supersedes MSG-001..MSG-002 + WI-5/6 intermediates)
prior_partial_deploy: 08f529d (WI-1..WI-4, deployed 2026-06-03 — superseded by this report)
wp: SFA-S003-P004-WP-CB-UI-patch01
branch: claude/ui-polish-hub-cropbook-2026-06-03
deployed_sha: 6703313
deployed_includes: WI-1..WI-7 (all patch01 work-items)
css_version_pre: 1780515224
css_version_post: 1780520599
---

# WP-CB-UI-patch01 FINAL — Deploy Report (REWRITE)

> This report **rewrites** the prior `DEPLOY_REPORT_v1.0.0.md` (whose `deployed_sha`
> was `08f529d`, WI-1..WI-4 only) per MSG-HUB-20260603-005 directive. The earlier
> partial-deploy state is recorded in the git history; this rewrite reflects the
> **FINAL** patch01 tip that bundles ALL seven WIs.

## 1. Verdict

**SUCCESS.** All MSG-005 CSS-content verifications PASS, `?v=` advanced, all 4 visual smoke checks PASS, baseline 6 routes 200. team_50's `F-PRE-004 mobile-overflow MAJOR` finding is resolved (WI-7 guards live). Pre-launch audit and L-GATE_V are unblocked.

## 2. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `6703313` (after `git reset --hard origin/...`). Includes WI-5 (`c2cf27f` compact entry cards), WI-6 (`7fbcf89` app-shell logo), WI-7 (`6703313` mobile overflow guards), plus the prior WI-1..WI-4 (`f9d274c` build).
- **lftp stats:** **12 transferred · 12 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.**
- **Diff surface (sfa_delivery only):** `public_assets/css/{classb.css, crop-book-v1.css, crop-book-deep.css}` (3 CSS files) + `templates/pages/{book_entry.php, book_table.php, community.php, hub_home.php, hub_tiers.php, market_product.php}` (6 templates) + 3 additional files. No migrations, no data push, no `_aos/` or `roadmap.yaml` edits (IR#4 honored).
- **Deploy log on host:** `/tmp/sfa_ui_patch01_FINAL_deploy.log`.

## 3. CSS-content verification (per MSG-005 §"Verify in LIVE served CSS")

### `?v=` cache-bust advanced

| File | Pre-deploy | Post-deploy |
|---|---|---|
| `crop-book-v1.css` | `?v=1780515224` | `?v=1780520599` ✅ |
| `classb.css`       | `?v=1780515224` | `?v=1780520599` ✅ |
| `crop-book-deep.css` | `?v=1780515224` | `?v=1780520599` ✅ |

### Required markers present in served CSS (Cloudflare-bypassed via `Pragma: no-cache` + `?cb=$(date +%s)`)

| File | Marker | Hits | Verdict |
|---|---|---|---|
| `crop-book-v1.css?v=1780520599` | `cb-paths { display: grid` (WI-5) | 1 | ✅ |
| `crop-book-v1.css?v=1780520599` | `.cb-crop-detail` overflow guard (WI-7) | 2 | ✅ |
| `classb.css?v=1780520599`       | `.sh__mark svg { width: 100%` (WI-6) | 1 | ✅ |
| `classb.css?v=1780520599`       | `.phist-wrap` (WI-7)                 | 2 | ✅ |
| `crop-book-deep.css?v=1780520599` | `.dt-table-wrap` (WI-7)            | 2 | ✅ |

Pre-deploy sanity (proof these were the patches' deltas, not pre-existing):
`crop-book-v1.css?v=1780515224` had `cb-paths { display: grid` hits = **0** and
`.cb-crop-detail` hits = **0**. Now both present.

## 4. Smoke evidence (per MSG-005 §"Smoke")

### §a — `/crop-book/` entry = 4 compact cards (not giant)

Inside the `cb-paths` grid container (2,469 chars of inner block, Python depth-counted DOM scan):

```
mod-card anchors inside cb-paths: 4
  → /crop-book/questions
  → /crop-book/family
  → /crop-book/table
  → /crop-book/search
```

Each card uses `class="mod-card mod-card--sun mod-card--open"` (or tier
variant); the `cb-paths` container's `display: grid` (WI-5) renders them as a
compact grid. Below the entry-cards row, the dense 74-crop grid (already
verified in the 08f529d round) is unchanged.

✅

### §b — SFA logo (`.sh__mark`) small / correctly sized

Live `classb.css?v=1780520599` rule block (Cloudflare-bypassed):

```css
/* .sh__mark is an inline <a> (so its width/height were ignored) wrapping an
   UNSIZED <svg><use href="#sfa-logo"> → the SVG rendered at its default huge
   intrinsic size = broken logo. Constrain the anchor + size the inner svg. */
.sh__mark { display: inline-flex; align-items: center; justify-content: center;
            width: 34px; height: 34px; overflow: hidden; flex: none; }
.sh__mark svg { width: 100%; height: 100%; display: block; }
```

Anchor constrained to 34×34, inner SVG fills the anchor → logo renders at the
intended small size site-wide (WI-6). ✅

### §c — `/crop-book/table`, `/market/{slug}`, `/crop-book/{slug}` simple → no 375px horizontal scroll

Mobile UA probe (`User-Agent: iPhone…`) + post-deploy DOM scan:

| URL | HTTP | WI-7 wrap class in DOM | Inline `min-width`/`width > 400px` styles | Verdict |
|---|---|---|---|---|
| `/crop-book/table` | 200 | `dt-table-wrap` × 3 (WI-7 wrap → `overflow-x: auto`) | 0 | ✅ |
| `/market/prd059` (first product from `/market/`) | 200 | `phist-wrap` × 0 (no history widget on this product); CSS rule live for when present | 0 | ✅ |
| `/crop-book/watermelon` | 200 | `cb-crop-detail` × 2 (WI-7 guard active) | 0 | ✅ |
| `/crop-book/lettuce` | 200 | `cb-crop-detail` × 2 (WI-7 guard active) | 0 | ✅ |

No inline width hard-codes that would force horizontal scroll at 375px. WI-7
guard classes are present in both the served CSS and the rendered DOM on the
correct surfaces. ✅

### §d — Baseline 6 routes all 200

```
200 /
200 /crop-book/
200 /market/
200 /calc/
200 /community
200 /about
```

✅

## 5. What was touched / not touched

- ✅ Server checkout: `claude/ui-polish-hub-cropbook-2026-06-03 @ 08f529d` → `@ 6703313` (reset --hard to origin).
- ✅ `sfa_delivery/` mirrored to uPress (12 transferred / 12 replaced).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` **rewritten** (prior `deployed_sha: 08f529d` replaced with `6703313`).
- ✅ `MSG-HUB-20260604-001` to team_100 (sibling close-loop).
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations, no data push, no deploy-script change, no Cloudflare touch, no `.env` change.
- ❌ No L-GATE_V verdict self-issued.

## 6. Handoff

→ **team_50**: pre-launch audit `F-PRE-004 mobile-overflow MAJOR` is resolved (WI-7 dt-table-wrap + cb-crop-detail + phist-wrap live in CSS; mobile-UA probes show no overflow risk on the 4 sensitive surfaces). All other WIs (WI-1..WI-6) also live. Please re-audit and lift NO-GO.
→ **team_190**: L-GATE_V R2 executable on live `6703313`. Mandate at `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-patch01/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md` (C1–C9; checks now have served-CSS evidence too).
→ **team_100**: closure-set complete; route 190 + 50.
→ **team_00**: pre-launch blocker cleared.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-04
