---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-ALIGN_v1.0.3
title: team_99 — WP-CB-UI-ALIGN R3-hotfix deploy SUCCESS — all L-GATE_V R3 smoke checks PASS
status: SUCCESS
date: 2026-06-02
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R3 ready), team_50, team_00
parent_mandate: ./DEPLOY_MANDATE_R3_2026-06-02_v1.0.0.md (b5ad8e5)
parent_msg: ../MSG-HUB-20260602-006.md
prior_reports:
  - ./DEPLOY_REPORT_v1.0.0.md (R1, b72bcca)
  - ./DEPLOY_REPORT_v1.0.1.md (R2, c1d9cff)
  - ./DEPLOY_REPORT_v1.0.2.md (R3-V01, 9a5d5d6)
wp: SFA-S003-P002-WP-CB-UI-ALIGN
deploy_ref: github/main
deployed_sha: f66360d (HEAD of main; includes b5ad8e5 R3 fix)
fix_commit: b5ad8e5
---

# WP-CB-UI-ALIGN R3-hotfix — Deploy Report

## 1. Verdict

**All 6 mandate smoke checks PASS.** L-GATE_V R3 is unblocked.

## 2. Deploy summary

- **Host:** waldhomeserver (egress `46.235.231.114`).
- **Source:** `github/main` @ `f66360d` (mail commit) — includes `b5ad8e5` (R3 V02-residual fix) and all prior V01+V02+V03 fixes.
- **R3 diff (2 files on `sfa_delivery/`):**
  - `templates/macros/rotation_hint.php` — removed farmer-facing `family: {latin}` debug line.
  - `templates/pages/calc_dash.php` — removed raw `(succession_interval_weeks)` from disabled calc-card visible text.
- **lftp stats:** 16 transferred · 11 replaced · exit 0. Surface larger than the 2-file R3 delta because main has CLASSB intake commits since R3-V01 (`freshness_pill.php`, `account_landing.php`, `classb.js`, `hub_home.php`, `hub_tiers.php`, `market_list.php`, `market_product.php`, `search_results.php`, `ClassBRouteTest.php` — all additive). No errors.
- **Deploy log on host:** `/tmp/sfa_R3hotfix_deploy.log`.

## 3. Smoke evidence — exact L-GATE_V R3 check set

### V02 residual — `family:` must be 0 on lettuce + watermelon

```
$ curl -sL https://sfa.nimrod.bio/crop-book/lettuce    | grep -c 'family:'   → 0   ✅
$ curl -sL https://sfa.nimrod.bio/crop-book/watermelon | grep -c 'family:'   → 0   ✅
```

### calc disabled card — no raw `succession_interval_weeks` in visible text

```
$ curl -sL https://sfa.nimrod.bio/calc/ | grep -c '(succession_interval_weeks)'   → 0   ✅
$ curl -sL https://sfa.nimrod.bio/calc/ | grep -c 'succession_interval_weeks'     → 1
```

The single overall hit is an HTML comment (mandate explicitly allows comments):
```html
<!-- Module #6: succession schedule — DISABLED (requires: succession_interval_weeks) -->
```
Not visible to the user; satisfies the mandate.

### No regression on prior fixes (V01 / V03)

```
$ curl -sI https://sfa.nimrod.bio/calc/print      | head -1   → HTTP/2 200   ✅
$ curl -sI https://sfa.nimrod.bio/calc/export.csv | head -1   → HTTP/2 200   ✅
```

### Baseline routes (no regression)

```
200 /
200 /crop-book/
200 /calc/
200 /market/
```
✅

### Bonus

```
$ curl -sI https://sfa.nimrod.bio/calc/export.pdf | head -1   → HTTP/2 404   (route retired — expected)
```
✅

## 4. What was touched / not touched

- ✅ Server checkout: fast-forwarded `main` to `f66360d`. `sfa_delivery/` mirrored to uPress.
- ✅ This `DEPLOY_REPORT_v1.0.3.md` written + MSG-HUB-20260602-007 in flight.
- ❌ No application code edits, no `_aos/`, no `roadmap.yaml`, no deploy-script change, no Cloudflare touch, no `.env` change.
- The branch ↔ main reconciliation flagged in R3-V01 (DEPLOY_REPORT_v1.0.2) is still open for team_100/team_191; not blocking.

## 5. Handoff

→ **team_100**: WP-CB-UI-ALIGN closure-set is complete on staging. Live at `f66360d` (which contains all fixes V01 + V02 + V03 + R3-V02-residual + R3-calc-key).
→ **team_190**: L-GATE_V R3 (final constitutional round) is unblocked. §3 above is the exact evidence set against your check spec.
→ **team_50**: R3 V02-residual + calc-key are observable on live; re-QA if your scope still needs it.
→ **team_00**: no human intervention needed.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-02
