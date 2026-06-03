---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-patch01_v1.0.0
title: team_99 — WP-CB-UI-patch01 FINAL deploy SUCCESS — WI-1..WI-8 all live (WI-8 = RTL-overflow fix)
status: SUCCESS
date: 2026-06-04
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V), team_50 (re-audit FYI), team_00 (Principal)
parent_mandate: ../MSG-HUB-20260603-006.md  # WI-8 RE-DEPLOY directive (supersedes the 6703313 round)
prior_deploy: 6703313 (FINAL minus WI-8, deployed 2026-06-04 — superseded by this rewrite)
wp: SFA-S003-P004-WP-CB-UI-patch01
branch: claude/ui-polish-hub-cropbook-2026-06-03
deployed_sha: c7b4368
deployed_includes: WI-1..WI-8 (all patch01 work-items including RTL overflow guard)
css_version_pre: 1780520599
css_version_post: 1780522574
---

# WP-CB-UI-patch01 FINAL — Deploy Report (REWRITE — WI-8)

> Second rewrite of this report. The first rewrite (earlier today) recorded
> `6703313` with WI-1..WI-7. team_100's own qa_probe of the live `6703313`
> found a residual RTL-origin overflow on `/crop-book/table` @375px (the page
> reported `scrollWidth 517 > viewport 375`). WI-8 adds `.cb-table-page
> { overflow-x: clip }` to `crop-book-deep.css` and is now live at `c7b4368`.

## 1. Verdict

**SUCCESS.** WI-8 marker present in served `crop-book-deep.css`, `?v=` advanced, `/crop-book/table` DOM uses the new class, no overflow-risk inline styles on the mobile UA probe. WI-1..WI-7 from `6703313` remain live.

## 2. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `c7b4368` (after `git reset --hard origin/...`). Single commit since `6703313`: `c7b4368 fix(WP-CB-UI-patch01 WI-8): /crop-book/table RTL mobile-overflow + team_100 re-audit reconciliation`.
- **lftp stats:** **5 transferred · 5 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.**
- **Surface:** `public_assets/css/{classb.css, crop-book-deep.css, crop-book-v1.css}` + `templates/pages/{book_table.php, market_product.php}`. Note: mandate said "only `crop-book-deep.css` changed" — the other 4 files were re-uploaded due to `git reset --hard` touching working-tree mtimes (lftp uses mtime/size compare). Content-wise the other 4 are identical to the `6703313` versions (deploy is forward-compatible).
- **Deploy log on host:** `/tmp/sfa_wi8_deploy.log`.

## 3. CSS verification — per MSG-006

### `?v=` advanced

| File | Pre-deploy (6703313) | Post-deploy (c7b4368) |
|---|---|---|
| `crop-book-deep.css` | `?v=1780520599` | `?v=1780522574` ✅ |

### WI-8 marker in served `crop-book-deep.css?v=1780522574`

```css
/* WI-8: .cb-table-page gets overflow-x:clip to prevent the RTL-origin layout
   width (scrollX starts negative in RTL) from leaking into the document
   scrollWidth. clip does not create a scroll context, so .dt-table-wrap's
   own overflow-x:auto scroll continues to work normally. */
.cb-table-page {
  overflow-x: clip;
}
.dt-table-wrap {
  …
```

- `.cb-table-page` selector hits: **2** (rule + comment reference) ✅
- `overflow-x: clip` rules: **2** ✅
- Rule composition (`.cb-table-page { overflow-x: clip }`) confirmed in served body ✅

## 4. Smoke evidence

### §a — `/crop-book/table` @375px mobile UA

```
HTTP/2 200
cb-table-page class hits in DOM:   1   (the WI-8 page wrapper is active)
dt-table-wrap (WI-7, unchanged):    3   (table scroller still wraps)
inline width >= 400px styles:      0
```

WI-8's `overflow-x: clip` on the page wrapper neutralizes the RTL-origin scroll
leak without disturbing WI-7's `dt-table-wrap` scroll context (per the comment
explicitly noting this).

✅

### §b — 7 routes 200 (including `/crop-book/table`)

```
200 /
200 /crop-book/
200 /crop-book/table
200 /market/
200 /calc/
200 /community
200 /about
```

✅

### §c — Prior WI-1..WI-7 still live (regression check)

No changes to `classb.css`/`crop-book-v1.css` content vs `6703313`. The `?v=`
moved with the mirror, so prior verifications from this morning's rewrite
remain authoritative for those WIs.

## 5. What was touched / not touched

- ✅ Server checkout: `6703313 → c7b4368` (reset --hard).
- ✅ `sfa_delivery/` mirrored (5 transferred / 5 replaced; only `crop-book-deep.css` content actually changed).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` **rewritten** (deployed_sha `6703313 → c7b4368`).
- ✅ `MSG-HUB-20260604-002` to team_100 (sibling close-loop).
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations, no data push, no deploy-script change, no Cloudflare touch, no `.env` change.
- ❌ No L-GATE_V verdict self-issued.

## 6. Handoff

→ **team_100**: please run the authoritative live qa_probe of `/crop-book/table` @375px on `c7b4368` (per MSG-006 "team_100 will run the authoritative live qa_probe, NOT team_50"). On PASS, route team_190 L-GATE_V.
→ **team_190**: L-GATE_V R2 executable on live `c7b4368` once team_100's probe confirms `/crop-book/table` scrollWidth ≤ viewport.
→ **team_50**: per MSG-006 directive, you're not in this round; team_100 is owning the live probe.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-04
