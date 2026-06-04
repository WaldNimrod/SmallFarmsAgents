---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-FIDELITY_v1.0.0
title: team_99 — WP-CB-UI-FIDELITY deploy SUCCESS (1 finding) — Decisions A+B live, prior WI-1..WI-9 subsumed
status: SUCCESS_WITH_1_FINDING
date: 2026-06-04
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V — non-Claude), team_50 (re-audit), team_00 (Principal)
parent_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-UI-FIDELITY/DEPLOY_MANDATE_team99_2026-06-04_v1.0.0.md
parent_lgate_b_verdict: ../../team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/LGATE-B_VERDICT_team100_2026-06-04_v1.0.0.md
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
branch: claude/ui-polish-hub-cropbook-2026-06-03
deployed_sha: 4c9bab2
branch_tip_at_deploy: f305bbd (one doc-only commit on top of 4c9bab2; identical sfa_delivery)
subsumes:
  - SFA-S003-P004-WP-CB-UI-patch01 (WI-1..WI-9, including WI-9 mobile-overflow root-cause that landed after my WI-8 round)
  - TEAM_50/SFA-PRELAUNCH-QA/PRELAUNCH_QA_REPORT_2026-06-03 (NO-GO was deploy-lag, not new defects)
css_version_pre: 1780522574
css_version_post: 1780532267
---

# WP-CB-UI-FIDELITY — Deploy Report

## 1. Verdict

**SUCCESS** with one provenance-display finding (§4.1).

Decisions A (season-from-months) + B (questions restored) are live. WI-1..WI-9 patch01 work-items are all live (the FIDELITY mirror is forward-compatible / superset). 4 of 5 mandate smoke checks fully PASS; the 5th (`/crop-book/lettuce` formatting) PASSes on 4/5 sub-criteria with one `prov__srcval` audit-display showing a raw 6-decimal number — flagged below for team_100 disposition.

## 2. SHA discrepancy in the mandate — resolution

The mandate has two SHAs:
- **Header**: "`deploy commit 4c9bab2` (HEAD; includes Decision A season-from-months + B questions)"
- **§2 + §5**: "Deliver the delivery tier at commit `0cbd5b8`" / "deployed SHA `0cbd5b8`"

`0cbd5b8` is the **earlier** L-GATE_B build commit (before the Decision A patch landed). `4c9bab2` is the **later** commit that adds Decisions A+B, which the mandate header explicitly says is the deploy target. The branch HEAD `f305bbd` is a documentation-only commit on top of `4c9bab2` that records the deploy-target decision (no sfa_delivery delta vs `4c9bab2`).

**Resolution:** deployed `f305bbd` working-tree which is identical to `4c9bab2` for `sfa_delivery/`. Reporting `deployed_sha: 4c9bab2` (the actually-correct code SHA per mandate header + the Decision A+B inclusion criterion). `0cbd5b8` in mandate §2/§5 is treated as stale wording (pre-Decision-A draft).

## 3. Deploy summary

- **Host:** waldhomeserver (`46.235.231.114`, uPress-allowlisted s1240).
- **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` → HEAD `f305bbd` (after `git reset --hard origin/...`). Last sfa_delivery-touching commit = `4c9bab2`.
- **lftp stats:** **10 transferred · 10 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.**
- **Files in this mirror** (forward-compatible w.r.t. prior c7b4368 deploy):
  - **FIDELITY surface (Decisions A+B + L-GATE_B build):** `app/Controllers/CropBookViewController.php`, `app/Controllers/MarketViewController.php`, `app/Lib/FieldRegistry.php`, `templates/macros/calc_panel.php`, `templates/macros/prov_value.php`, `templates/pages/book_crop.php`, `templates/pages/book_entry.php`, `templates/pages/market_product.php`
  - **WI-9 (post-WI-8 root-cause for `/crop-book/table` overflow):** `public_assets/css/crop-book-deep.css` (responsive table toggle)
  - **classb.js:** new `window.fetchHistory` definition
- **Deploy log on host:** `/tmp/sfa_fidelity_deploy.log`.

## 4. Smoke evidence — per mandate §3 (5 checks)

### §4.1 — `/crop-book/lettuce/` formatting, Hebrew units, single hero — **PASS_WITH_1_FINDING**

```
Hebrew unit hits:       ס״מ=4, ימ׳=5, שבועות=14, ק״ג=2     ✅
raw English units:      cm=0, days=0, weeks=0, kg_per_bed_m=0  ✅
hero <h1>חסה</h1>:      1 (no duplicate, no green-blob marker) ✅
.000000 trailing:       0 occurrences                          ✅
raw 6-decimal numbers:  1 occurrence                           ⚠ FINDING
```

The single remaining raw-decimal occurrence:
```
<span class="prov__srcval">59.043478 ימים</span>
```
This is a **provenance / audit display** (the `prov__srcval` class denotes "provenance source value" — the raw source data shown alongside the formatted/humanized display value as transparency). The user-visible formatted value lives in a sibling span; this is the "evidence" column.

The mandate's exact text ("no `59.043478`, no `.000000`") suggests team_100 wants the audit display also scrubbed/formatted. Routing to team_100 to disposition: either (a) extend the formatter to also wrap `prov__srcval` (small follow-up patch), or (b) accept the raw audit display as intentional provenance. No deploy action from me until you decide.

### §4.2 — `/market/` chips Hebrew — **PASS**

All 11 visible chip labels are Hebrew:
```
fchip is-on >הכל
?category=alliums >בצליים
?category=baskets >סלים
?category=brassicas >כרוביים
?category=cucurbits >דלועיים
?category=eggs >ביצים
?category=fruiting_vegetables >ירקות פרי
?category=fruits >פירות
?category=leafy_greens >ירוקי עלים
?category=legumes_fresh >קטניות טריות
?category=root_vegetables >ירקות שורש
```

The English values (`root_vegetables`, `legumes_fresh`, etc.) only appear in `href="?category=…"` URL parameters — programmatic identifiers, not visible text. ✅

### §4.3 — `/crop-book/` filter "עונה", non-empty result-sets, 3 questions — **PASS**

- `עונה` filter label: 1 hit ✅
- `<select>` options (Hebrew labels with English value codes for the URL):
  ```
  <option value="summer">קיץ
  <option value="winter">חורף
  <option value="spring">אביב
  <option value="autumn">סתיו
  ```
  All 4 seasons present ✅
- `?season=summer` → 42 crop-card anchors (non-empty) ✅
- `?dtm_max=60` → 50 crop-card anchors (non-empty) ✅
- "שאלות מובילות" card reads **"3 שאלות"** (not 12) ✅

### §4.4 — Served CSS markers + `window.fetchHistory` in classb.js — **PASS**

- `?v=` advanced site-wide: `1780522574 → 1780532267` ✅
- `crop-book-v1.css?v=1780532267`: `.cb-paths { display: grid` (WI-5) = 1 hit ✅
- `classb.css?v=1780532267`: `.sh__mark` (WI-6) = 3 hits, includes the rule
  ```css
  .sh__mark { display: inline-flex; … width: 34px; height: 34px; overflow: hidden; flex: none; }
  .sh__mark svg { width: 100%; height: 100%; display: block; }
  ```
- `classb.js?v=1780532267`: `window.fetchHistory` = 5 hits, defined as
  ```js
  window.fetchHistory = function (slug, days, pgraph) { … }
  ```

✅

### §4.5 — This DEPLOY_REPORT is being written and committed alongside the MSG. ✅

## 5. Subsumes prior open items

- **patch01 WI-1..WI-9** — all live in this mirror. The WP-CB-UI-patch01 work is now fully on production for this branch's lineage.
- **TEAM_50 PRELAUNCH-QA NO-GO** (`PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md`) — per mandate, was deploy-lag, not defects. The bytes team_50 wanted are now live.

## 6. What was touched / not touched

- ✅ Server checkout: branch reset to `f305bbd` (sfa_delivery == `4c9bab2`).
- ✅ `sfa_delivery/` mirrored to uPress (10 transferred / 10 replaced).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` written + `MSG-HUB-20260604-003` to team_100.
- ❌ No `_aos/` or `roadmap.yaml` edits (IR#4).
- ❌ No application code edits, no migrations, no data push, no deploy-script change, no Cloudflare touch, no `.env` change.
- ❌ No L-GATE_V verdict self-issued.

## 7. Handoff

→ **team_100**: please disposition the §4.1 `prov__srcval` finding (small patch vs accept-as-provenance). On disposition, route **team_190 (non-Claude) L-GATE_V** design-vs-Board-A/B on live `4c9bab2` (the launch gate) + **team_50 re-audit**.
→ **team_190**: stand by for L-GATE_V routing from team_100. Evidence package = §4 above; assets at `?v=1780532267`.
→ **team_50**: stand by for re-audit routing from team_100. Prior NO-GO is subsumed by this deploy.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-04
