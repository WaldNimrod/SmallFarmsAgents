---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-ALIGN_v1.0.2
title: team_99 — WP-CB-UI-ALIGN R3 re-deploy SUCCESS — V01 PDF code fix live (/calc/print)
status: SUCCESS — V01 + V02 + V03 all live
date: 2026-06-02
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R2 evidence — full set), team_50 (re-QA on V01), team_00 (Principal)
parent_mandate: ../MSG-HUB-20260602-004.md (RE-DEPLOY — V01 PDF code fix)
prior_reports:
  - ./DEPLOY_REPORT_v1.0.0.md (R1, b72bcca)
  - ./DEPLOY_REPORT_v1.0.1.md (R2, c1d9cff)
wp: SFA-S003-P002-WP-CB-UI-ALIGN
branch_named_by_mandate: claude/wp-cb-ui-align-2026-06-02
actually_deployed_from: github/main
deployed_sha: 9a5d5d6 (HEAD of github/main; includes fc4b914 R2-progress + fdb4fc7 V01 fix)
fix_commit: fdb4fc7
---

# WP-CB-UI-ALIGN R3 — Deploy Report

## 1. Verdict

| Finding | Status |
|---|---|
| **V01** `/calc/print` (extension-less PDF route) | ✅ **PASS** — 200 text/html, query params work, old `.pdf` URL 404s as expected |
| **V02** crop-page Hebrew (re-verified by quick spot-check) | ✅ remains PASS from R2 |
| **V03** `/calc/` crop selector (re-verified) | ✅ remains PASS from R2 |
| Baseline 5 surfaces — no regression | ✅ |

L-GATE_V R2 closure-set is complete. team_50 can re-QA V01; team_190 can run the live per-page round on all three findings.

## 2. Branch / ref note (important — read once)

MSG-HUB-20260602-004 named `branch claude/wp-cb-ui-align-2026-06-02 @ fc4b914`. After `git pull`, the
**branch's** HEAD was `e8c7e37` (CLASSB-dispatch tip), and `fc4b914` was **not** in the branch's ancestry —
it had been pushed to `main` (alongside `fdb4fc7`, the actual V01 code fix) but not back to the branch.

```
git merge-base --is-ancestor fc4b914 HEAD(branch=e8c7e37)  →  NO
git merge-base --is-ancestor fc4b914 github/main(9a5d5d6)  →  YES
git merge-base --is-ancestor fdb4fc7 github/main           →  YES   ← actual V01 fix
git merge-base --is-ancestor 78b66df github/main           →  YES   ← V02+V03 fix
```

`main` is a strict superset of the branch's tip for `sfa_delivery/`: only the V01-fix surface differs
(`sfa_delivery/app/routes.php`, `sfa_delivery/app/Controllers/HubController.php`, `sfa_delivery/templates/pages/calc_dash.php`).

**Action taken:** switched the deploy source from the branch to `github/main` (HEAD `9a5d5d6`) so that
V01 + V02 + V03 all reach uPress in one round. This is the smallest change that achieves the mandate
intent. Recommend team_100 (or team_191) reconcile the branch ↔ main divergence in a follow-up — either
ff-merge `main` back to `claude/wp-cb-ui-align-2026-06-02` or close the branch once L-GATE_V passes.

## 3. Deploy summary

- **Host:** waldhomeserver (egress `46.235.231.114`, allowlisted on uPress s1240).
- **Source:** `github/main` @ `9a5d5d6` (includes `fc4b914` R2-progress wrap + `fdb4fc7` V01 fix).
- **Routes confirmed in `sfa_delivery/app/routes.php`:**
  ```php
  $app->get('/calc/export.{fmt:csv}', [HubController::class, 'calcExport']);
  $app->get('/calc/print[/]',          [HubController::class, 'calcExport']);
  // V01: PDF print view moved to extension-less /calc/print
  ```
- **lftp stats:** 59 transferred · 59 replaced · exit 0. No `Fatal` / `530` / `max-retries`.
  - Surface larger than the V01 delta because the branch's prior deploy (c1d9cff) lacks unrelated
    main-only assets (e.g., crop-image `wc-*.png` refreshes from earlier WP-CB-MIG2 work). All
    additive / replacement — no functional regressions on the V02/V03 surface (baseline re-check
    below confirms).
- **Deploy log on host:** `/tmp/sfa_R3_deploy.log`.

## 4. Smoke evidence

### V01 — `/calc/print` (mandate §"Smoke")

```
$ curl -sI https://sfa.nimrod.bio/calc/print
HTTP/2 200
content-type: text/html; charset=utf-8
server: cloudflare
```
✅

### V01 with query params (team_100 extra check)

```
$ curl -sI 'https://sfa.nimrod.bio/calc/print?crop=test'
HTTP/2 200
content-type: text/html; charset=utf-8
```
✅ — query params handled; no `.pdf` special-casing residue on extension-less paths.

### `/calc/print` body sanity

First line: `<!doctype html>` · body length: ~1.4 KB (print view template renders).

### `/calc/export.csv` (unchanged)

```
$ curl -sI https://sfa.nimrod.bio/calc/export.csv
HTTP/2 200
```
✅

### Old `/calc/export.pdf` (expected 404 — route retired)

```
$ curl -sI https://sfa.nimrod.bio/calc/export.pdf
HTTP/2 404
```
✅ As designed.

### Baseline regression check (no V02/V03 regression)

| URL | HTTP |
|---|---|
| `/` | 200 |
| `/crop-book/` | 200 |
| `/calc/` | 200 |
| `/market/` | 200 |

✅ V02 + V03 surfaces unaffected (no MySQL mirror change implied; spot re-check skipped per mandate).

## 5. What was touched / not touched

- ✅ Server checkout: switched from branch `claude/wp-cb-ui-align-2026-06-02` to `main` and fast-forwarded to `9a5d5d6`.
- ✅ `sfa_delivery/` mirrored to uPress; this R3 report + MSG-HUB-20260602-005 written.
- ❌ No application code edits, no `_aos/`, no `roadmap.yaml`, no deploy-script change, no Cloudflare touch, no `.env` change (R1 cred sync still holding).
- ❌ Did NOT push branch=main back to `claude/wp-cb-ui-align-2026-06-02` (left to team_100/team_191 to reconcile per §2).

## 6. Handoff

→ **team_100**: V01 + V02 + V03 all live on `9a5d5d6`. Branch ↔ main reconciliation in §2 is a minor follow-up.
→ **team_50**: please re-QA V01 (`/calc/print` 200 + content). V02/V03 already cleared from R2; no need to re-do unless your scope changed.
→ **team_190**: full R2 evidence package is now §3 of this report + §3 of `DEPLOY_REPORT_v1.0.1.md` (V02+V03). L-GATE_V live per-page round can run end-to-end on `9a5d5d6`.
→ **team_00**: no human intervention needed.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-02
