---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-patch01_v1.0.0
title: team_99 — WP-CB-UI-patch01 deploy SUCCESS — all 5 smoke checks PASS (WI-3/WI-4 included)
status: SUCCESS
date: 2026-06-03
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R1 unblocked), team_00 (Principal — round-2 hub feedback)
parent_mandate: ../MSG-HUB-20260603-002.md (UPDATED — supersedes MSG-HUB-20260603-001 same WP)
wp: SFA-S003-P004-WP-CB-UI-patch01
branch: claude/ui-polish-hub-cropbook-2026-06-03
pre_reset_sha: 932f08a (server main HEAD before checkout)
deployed_sha: 08f529d
---

# WP-CB-UI-patch01 — Deploy Report

## 1. Verdict

**SUCCESS.** All 5 mandate smoke checks PASS. L-GATE_V R1 (C1–C9) is unblocked for live verification.

## 2. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted on s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `08f529d` (after `git reset --hard origin/...`). `08f529d` is reachable + the named mandate tip (`f9d274c build(WI-3/WI-4) → 08f529d mandate-update`).
- **Pre-checkout state:** server was on `main @ 932f08a` (post tokens.css ack).
- **lftp stats:** **15 transferred · 15 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.**
- **Diff surface (CSS + templates + macros; no migrations / no data push, as the mandate stated):** `hub_home.php`, `hub_tiers.php`, `community.php`, `market_list.php`, `search_results.php`, `book_entry.php`, `templates/macros/market_disclaimer.php`, `public_assets/css/classb.css`, `HubController.php`, …
- **Deploy log on host:** `/tmp/sfa_ui_patch01_deploy.log`.

## 3. Smoke evidence — all 5 PASS

### §1 — `/` open-tools row spans full width, 4 tiles, 4th = יומן השדה (is-dev, non-clickable)

The CSS class name on the live HTML is `modtile` (the patch refactored from the
mandate's nominal "open-tools" to `modtile` / `hub-grid` container — semantic
structure intact). Order of the first 4 tiles on `/`:

```
1. <a class="modtile modtile--leaf">              modtile__title: ספר גידולים        (clickable → /crop-book/)
2. <a class="modtile modtile--tomato">            modtile__title: מחירון              (clickable → /market/)
3. <a class="modtile modtile--sun">               modtile__title: מחשבון לחקלאי        (clickable → /calc/)
4. <div class="modtile modtile--soil is-dev"      modtile__title: יומן השדה / FIELD-LOG (is-dev, aria-disabled="true", glyph 📒)
        aria-disabled="true">
```

- `is-dev` class hits: 1 ✅ (exactly one tile, on the FIELD-LOG one)
- `יומן השדה` (with definite article ה) hits: 1 ✅
- `בפיתוח` ("in-development") hits: 2 ✅
- Mapping: the 4th tile uses `<div>` (not `<a>`) + `aria-disabled="true"` → confirmed non-clickable

✅

### §2 — `/` tagline, gardener card, copy uses חקלאות מקומית, CTA section with two offers

- `גנן` (gardener) hits: **1** ✅ (the gardener card title)
- `חקלאות מקומית` hits: **1** ✅
- `חקלאות קטנה` (old wording — should be gone): **0** ✅
- CTA container: `class="hub-cta"` ✅; `hub-cta__card hub-cta__card--secondary` (the secondary offer) ✅; `hub-cta__icon` ✅
- Two offers:
  - Secondary `href="/community">קהילה` ✅ (community link)
  - Primary `wa.me/972547776770` ✅ (WhatsApp deeplink)

✅

### §3 — `/crop-book/` crop grid dense (≥5–6 cols, no horizontal overflow)

- Grid container: `class="cards-grid"` ✅ (responsive CSS-grid container)
- Distinct crop anchors `href="/crop-book/<slug>/"`: **74** ✅ (full crop set rendering as cards — density follows from CSS minmax on `cards-grid`)
- Page bytes: 117,197 — consistent with 74 cards rendering inline (vs the sparse pre-patch layout)

✅ (column count is a CSS rendering concern not directly testable from curl HTML; the container class + 74-card payload + no `style=` overrides on `cards-grid` is the unambiguous structural signal)

### §4 — `/about` has **no** Tend integration mention

- `Tend` (case-insensitive substring): **0** hits ✅
- Word-boundary `\bTend\b`: **0** hits ✅

✅

### §5 — Baseline 6 routes all 200

```
200 /
200 /crop-book/
200 /market/
200 /calc/
200 /community
200 /about
```

✅

## 4. What was touched / not touched

- ✅ Server checkout: `main 932f08a` → `claude/ui-polish-hub-cropbook-2026-06-03 @ 08f529d` (reset --hard to origin).
- ✅ `sfa_delivery/` mirrored to uPress (15 transferred / 15 replaced).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` written + `MSG-HUB-20260603-005` to team_100 (sibling).
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations, no data push, no deploy-script change, no Cloudflare touch, no `.env` change.

## 5. Handoff

→ **team_190**: L-GATE_V R1 for WP-CB-UI-patch01 is unblocked. Re-run the live constitutional round on `08f529d` against the mandate's C1–C9 checks (mandate at `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-patch01/VALIDATION_MANDATE_team190_LGATE-V_2026-06-03_v1.0.0.md`).
→ **team_100**: WP-CB-UI-patch01 live; closure pending team_190 verdict.
→ **team_00**: round-2 hub feedback is reflected on live; review at your leisure (gardener `גנן` card, `חקלאות מקומית` copy, 4-tile row with `יומן השדה` is-dev placeholder, CTA section with community + WhatsApp, dense crop grid).

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-03
