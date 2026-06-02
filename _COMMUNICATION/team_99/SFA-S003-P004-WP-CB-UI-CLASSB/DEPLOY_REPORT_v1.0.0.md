---
id: DEPLOY_REPORT_SFA-S003-P004-WP-CB-UI-CLASSB_v1.0.0
title: team_99 — WP-CB-UI-CLASSB deploy SUCCESS — all 7 smoke checks PASS
status: SUCCESS
date: 2026-06-03
from_team: team_99 (OPS / waldhomeserver)
to_team: team_100 (Chief Architect)
cc_team: team_190 (L-GATE_V R3 unblocked for this WP), team_50, team_00
parent_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_MANDATE_team99_2026-06-02_v1.0.0.md
parent_validation_mandate: ../../TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/VALIDATION_MANDATE_team190_LGATE-V_2026-06-02_v1.0.0.md
parent_gate_verdict: ../../team_190/SFA-S003-P004/WP-CB-UI-CLASSB_LGATE-V_VERDICT_R2_v1.0.0.md
wp: SFA-S003-P004-WP-CB-UI-CLASSB
branch: claude/sfa-p004-cbdata-classb-2026-06-02
pre_reset_sha: 815acdc (main HEAD before checkout)
deployed_sha: c51c2e5
coupled_wp: SFA-S003-P004-WP-CB-DATA (separate report once migrate token + push complete)
---

# WP-CB-UI-CLASSB — Deploy Report

## 1. Verdict

**SUCCESS.** All 7 mandate §3 smoke checks PASS. L-GATE_V R3 for this WP is unblocked — team_190's prior FAIL was the expected pre-deploy state (per `c51c2e5 gate(L-GATE_V): both WPs FAIL — DEPLOY PRECONDITION`), and the live HTML now reflects the branch fixes.

## 2. Deploy summary

- **Host:** waldhomeserver (egress `46.235.231.114`, uPress-allowlisted on s1240).
- **Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02` → HEAD `c51c2e5` (post `git reset --hard origin/...`).
- **Pre-reset rollback signal:** server was on `main @ 815acdc` before checkout — captured for traceability.
- **Single FTPS mirror** (coupled with CB-DATA per that mandate's §"Coupling"):
  - **9 files transferred · 7 in-place replacements · exit 0 · no `Fatal`/`530`/`max-retries`.**
  - Class B surface delta: `templates/_layout.php`, `public_assets/css/classb.css`, `templates/pages/{community,hub_home,market_list,search_results}.php`, `app/Controllers/IngestController.php`.
  - CB-DATA additive: `migrations/004_crop_field_enrichment.sql`, `migrations/005_crop_attribute.sql` (also mirrored — applied separately via `/admin/migrate`, see `WP-CB-DATA` report when token unblocks).
- **Deploy log on host:** `/tmp/sfa_classb_data_deploy.log`.
- **Composer:** absent on host as the mandate anticipated; staged production `vendor/` used as-is (no new composer deps in this build).

## 3. Smoke evidence — 7 checks per mandate §3

### §3.1 — `/` returns 200

```
$ curl -sI https://sfa.nimrod.bio/
HTTP/2 200
```
✅

### §3.2 — `/community` has comm-banner with `contact.webp`, no cream wash leak

```
$ curl -sL https://sfa.nimrod.bio/community | grep -c 'comm-banner'           → 1
$ curl -sL https://sfa.nimrod.bio/community | grep -c 'contact.webp'          → 1   (image inside the banner)
$ curl -sL https://sfa.nimrod.bio/community | grep -c '#f4ecdc'                → 0   (cream wash covered/removed)
```
✅

### §3.3 — `/` hub: `hub-home__inner` present (≥1)

```
$ curl -sL https://sfa.nimrod.bio/ | grep -c 'hub-home__inner'                 → 2
```
✅

### §3.4 — `/market/` table headers have no inline `style=`

```
$ curl -sL https://sfa.nimrod.bio/market/ | grep -c 'ptable__th'              → 3
$ curl -sL https://sfa.nimrod.bio/market/ | grep -E 'ptable__th[^>]*style=' | wc -l   → 0
```
✅

### §3.5 — `/search?q=zzzzz` shows `◐ בקשו` CTA with class `reqinfo`

```
$ curl -sL 'https://sfa.nimrod.bio/search?q=zzzzz' | grep -c 'reqinfo'         → 1
$ curl -sL 'https://sfa.nimrod.bio/search?q=zzzzz' | grep -oE '◐[^<]{0,30}'    → ◐ בקשו הוספה
```
✅

### §3.6 — `/account` + `/about` return 200

```
200 /account
200 /about
```
✅

### §3.7 — `/community` footer has `<span aria-current="page">קהילה</span>` (no self-`<a href="/community">`)

```
$ … | grep '<span[^>]+aria-current[^>]*>[^<]+</span>'
<span aria-current="page">קהילה</span>      (count: 1)

$ … | grep 'href="/community"'                                                 → 0
```
✅

## 4. What was touched / not touched

- ✅ Server checkout: switched from `main` to `claude/sfa-p004-cbdata-classb-2026-06-02` + `reset --hard` to `c51c2e5`.
- ✅ `sfa_delivery/` mirrored to uPress (9 transferred / 7 replaced).
- ✅ This `DEPLOY_REPORT_v1.0.0.md` written + `MSG-HUB-20260603-001` to team_100 (sibling).
- ❌ No application code edits; no `_aos/`, no `roadmap.yaml`, no deploy-script change, no Cloudflare touch.
- ❌ Server `.env` unchanged this round (FTPS cred sync from 2026-06-02 R1 still holding).
- ⏸ CB-DATA migrate (`/admin/migrate`) + Mac-side ingest push: **PENDING** — blocked on `ADMIN_MIGRATE_TOKEN`. See sibling MSG-HUB-20260603-001 §"Action required".

## 5. Handoff

→ **team_190**: L-GATE_V R3 for WP-CB-UI-CLASSB is unblocked. Re-run the constitutional round against live `c51c2e5` — §3 above is the evidence package that maps 1-to-1 to the 7 checks in DEPLOY_MANDATE §3.
→ **team_100**: WP-CB-UI-CLASSB live; closure pending team_190 verdict. CB-DATA half is blocked on token — see sibling MSG.
→ **team_50**: optional spot re-QA — your re-QA v1.1.0 was the precondition; surfaces should now match what you validated on branch.
→ **team_00**: no action.

— team_99 (OPS / waldhomeserver `46.235.231.114`) 2026-06-03
