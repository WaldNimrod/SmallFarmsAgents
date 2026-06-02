---
id: VERDICT_SFA-S003-P004-WP-CB-UI-CLASSB_L-GATE_V_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-03
type: validation_verdict
wp: SFA-S003-P004-WP-CB-UI-CLASSB
gate: L-GATE_V
mandate: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-CLASSB/VALIDATION_MANDATE_team190_LGATE-V_2026-06-02_v1.0.0.md
branch: claude/sfa-p004-cbdata-classb-2026-06-02
branch_head: 82b1d5b
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
phase_owner: team_190
correction_cycle: R1
result: FAIL
---

# WP-CB-UI-CLASSB L-GATE_V Verdict

```yaml
wp: SFA-S003-P004-WP-CB-UI-CLASSB
gate: L-GATE_V
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
result: FAIL
surface_checks: 1/7
constitutional_checks: 2/4
findings:
  - id: F-190-CLASSB-V-01
    severity: BLOCKER
    summary: "Mandate precondition unmet — no team_99 DEPLOY_REPORT for the fix-all build; live sfa.nimrod.bio still serves the pre-fix Class B HTML."
    evidence: "Expected `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md` absent. Live curl 2026-06-03: `hub-home__inner` count=0; community banner has no contact.webp; market list `ptable__th` count=0; /community footer still `<a href=\"/community\">` not aria-current span."
    disposition: R2
  - id: F-190-CLASSB-V-02
    severity: MAJOR
    summary: "C1 hub hero fix not live — `.hub-home__inner` wrapper absent on `/`."
    evidence: "Branch: sfa_delivery/templates/pages/hub_home.php L71 + classb.css L38. Live: `curl -s https://sfa.nimrod.bio/ | grep -c hub-home__inner` → 0."
    disposition: R2
  - id: F-190-CLASSB-V-03
    severity: MAJOR
    summary: "C2 community banner fix not live — bare `.comm-banner` without contact.webp image."
    evidence: "Branch: community.php serves `/public_assets/img/contact.webp`. Live: `<div class=\"comm-banner\" aria-hidden=\"true\">` with no `<img>`."
    disposition: R2
  - id: F-190-CLASSB-V-04
    severity: MAJOR
    summary: "C3 search no-match CTA not design-aligned — missing ◐ glyph."
    evidence: "Branch search_results.php L83: `◐ בקשו הוספה`. Live: `<a class=\"reqinfo\" href=\"/community\">בקשו הוספה ←</a>`."
    disposition: R2
  - id: F-190-CLASSB-V-05
    severity: MAJOR
    summary: "C5 market table headers still inline-styled — `.ptable__th` not on live `/market/`."
    evidence: "Branch market_list.php L172–174 uses `.ptable__th`. Live: `<table class=\"ptable\" style=\"width:100%;border-collapse:collapse\">` with bare `<th>`."
    disposition: R2
  - id: F-190-CLASSB-V-06
    severity: MAJOR
    summary: "C6 footer scope-guard fix not live — `/community` still self-links קהילה instead of aria-current span."
    evidence: "Branch _layout.php L138–142. Live footer on /community: `<a href=\"/community\">קהילה</a>`."
    disposition: R2
  - id: F-190-CLASSB-V-07
    severity: INFO
    summary: "Branch code + tests attest fix-all build ready; composer 135/135 and validate_aos 0 FAIL on branch — blocked only by missing deploy."
    evidence: "sfa_delivery composer test 135/135 (2026-06-03); validate_aos.sh 29 PASS / 19 SKIP / 0 FAIL; ClassBRouteTest.php asserts hub-home__inner, ptable__th, aria-current."
    disposition: builder-acknowledge
summary: "L-GATE_V cannot pass: team_99 has not deployed the fix-all branch to sfa.nimrod.bio and no DEPLOY_REPORT_v1.0.0.md exists. Live probes confirm six of seven per-surface fix-all checks fail (only C7 /about 5-tier ladder passes — pre-existing Class B). Branch code and re-QA artifacts look ready; team_99 must execute DEPLOY_MANDATE, publish DEPLOY_REPORT SUCCESS, then team_190 re-runs L-GATE_V R2."
```

## Engine constraint (IR#1 / IR#5)

Validator: **Cursor / Composer 2.5 (GPT — non-Claude)**. Builder team_10 (Claude Sonnet); L-GATE_B verifier team_100 (Claude Opus); QA team_50 (Claude Haiku). Cross-engine satisfied.

## Precondition gate

| Requirement | Result | Evidence |
|-------------|--------|----------|
| team_99 DEPLOY_REPORT = SUCCESS | **FAIL** | `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md` not found |
| Fix-all live on sfa.nimrod.bio | **FAIL** | Live HTML lacks fix-all markers (see findings) |

## Per-surface design-vs-live (mandate §3.1)

| Check | Surface | Live result | Notes |
|-------|---------|-------------|-------|
| C1 | Hub `/` | **FAIL** | No `.hub-home__inner` |
| C2 | Community `/community` | **FAIL** | Banner empty — no `contact.webp` |
| C3 | Search no-match | **FAIL** | `.reqinfo` present but wrong copy (no ◐) |
| C4 | Account `/account` | **NOT VERIFIED** | Deploy required for CSS fix; page returns 200 |
| C5 | Market list + detail | **FAIL** | No `.ptable__th` on list; inline table style persists |
| C6 | Footer on `/community` | **FAIL** | Self-link `<a href="/community">` not `<span aria-current="page">` |
| C7 | About `/about` | **PASS** | 25× `.tier-row` — 5-tier ladder intact (original Class B) |

## Constitutional checks (mandate §3.2)

| Check | Result | Evidence |
|-------|--------|----------|
| C8 Tokens/palette | **PASS (branch)** | `tokens.css` `--gj-paper: #f8fbf8`; `classb.css` last in `_layout.php` L73–81. Live not re-probed for computed styles — non-blocking vs deploy blocker. |
| C9 Scope | **PASS (branch)** | Fix-all diff confined to `sfa_delivery/` templates + `classb.css` + tests per BUILD_REPORT_FIXALL_v1.0.0.md. No `_aos/`, Python, or migration edits. |
| C10 Scope-guard honesty | **PASS (branch)** | MINOR-2 (live hub stats) deferred to SRV-5 in REGISTER.md; build report explicitly NOT CHANGED. No server-side creep in fix-all diff. |
| C11 Tests | **PASS (branch)** | `composer test` 135/135; `validate_aos.sh` 0 FAIL. **Not attested on deployed SHA** — no deploy occurred. |

## Branch attestation (not a gate pass)

The fix-all working tree on `claude/sfa-p004-cbdata-classb-2026-06-02` contains all ten team_50 finding fixes (verified by file read + ClassBRouteTest + team_50 re-QA v1.1.0 PASS). This does **not** substitute for live L-GATE_V.

## Verdict

**FAIL** — return to team_99 deploy → team_190 L-GATE_V R2.

**Next steps for team_100:**
1. Route team_99 to execute `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_MANDATE_team99_2026-06-02_v1.0.0.md`
2. Require `DEPLOY_REPORT_v1.0.0.md` with deployed SHA + smoke PASS
3. Re-route team_190 L-GATE_V R2 against live site

— team_190
