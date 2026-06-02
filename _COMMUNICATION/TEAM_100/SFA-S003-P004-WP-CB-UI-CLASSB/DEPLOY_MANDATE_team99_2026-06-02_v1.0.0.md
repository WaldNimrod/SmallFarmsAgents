# DEPLOY MANDATE — SFA-S003-P004-WP-CB-UI-CLASSB (fix-all → live) — team_100 → team_99 — v1.0.0

**Date:** 2026-06-02
**From:** team_100 (Chief System Architect)
**To:** team_99 (OPS / waldhomeserver)
**Re:** Deploy the Class B QA fix-all build to sfa.nimrod.bio (uPress), then unblock team_190 L-GATE_V.
**Branch:** `claude/sfa-p004-cbdata-classb-2026-06-02` (pushed to origin) · deploy SHA = branch tip (`a8a2260` or later — the Class B fixes; WP-CB-DATA carries only governance docs, no delivery code).
**Host:** waldhomeserver (egress `46.235.231.114`, uPress-allowlisted). The Mac's Bezeq IP is NOT allowlisted — deploy from the host only.

## 1. Preconditions (all met)
- team_10 L-GATE_B build verified by team_100 (Opus): composer 135/135, php -l clean, validate_aos 0 FAIL.
- team_50 re-QA v1.1.0 = PASS (all 10 findings resolved in rendered HTML).
- Only `sfa_delivery/` templates + `classb.css` + tests changed vs the currently-live Class B (forward-only).

## 2. Deploy steps (on waldhomeserver)
```bash
cd <repo-on-waldhomeserver>            # the SmallFarmsAgents checkout
git fetch origin
git checkout claude/sfa-p004-cbdata-classb-2026-06-02
git reset --hard origin/claude/sfa-p004-cbdata-classb-2026-06-02   # match origin exactly
# vendor/ is gitignored + persists in the host working tree; no new composer deps in this build.
bash scripts/ftp_deploy_sfa_ui.sh      # composer install --no-dev if available, else staged vendor/; lftp mirror -R --delete
```
Expected: `lftp mirror` completes with no `Fatal` / `max-retries` / `530`. Note transferred/removed counts + the deployed SHA.

## 3. Smoke checks (must PASS)
1. `curl -sI https://sfa.nimrod.bio/ | head -1` → `HTTP/2 200`.
2. `/community` — NO empty `.comm-banner` beige box: `curl -s https://sfa.nimrod.bio/community | grep -c 'comm-banner'` and confirm an `<img ...contact.webp>` is present inside it (or the box is absent), and `grep -c '#f4ecdc'` on the rendered page region shows the wash is covered.
3. `/` hub — `.hub-home__inner` present: `curl -s https://sfa.nimrod.bio/ | grep -c 'hub-home__inner'` ≥ 1; visually the hero band no longer leaves a blank left half at desktop width.
4. `/market/` — table headers have no inline `style=` (`grep -c 'ptable__th'` ≥ 1).
5. `/search?q=zzzzz` — `◐ בקשו` CTA with class `reqinfo`.
6. `/account`, `/about` → 200.
7. Footer on `/community` shows `<span aria-current="page">קהילה</span>` (no self-`<a href="/community">`).

If a stale-cache anomaly appears (Cloudflare), note it; the prior UI-ALIGN deploy needed no purge for token CSS but flag if `classb.css` serves stale.

## 4. Report
Write `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md` (deployed SHA, lftp stats, all smoke results). On SUCCESS → team_190 L-GATE_V is executable (mandate pre-staged: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-CLASSB/VALIDATION_MANDATE_team190_LGATE-V_2026-06-02_v1.0.0.md`).
