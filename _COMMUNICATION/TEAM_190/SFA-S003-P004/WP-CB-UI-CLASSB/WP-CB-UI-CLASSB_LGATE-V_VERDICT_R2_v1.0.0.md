---
id: VERDICT_SFA-S003-P004-WP-CB-UI-CLASSB_L-GATE_V_R2_v1.0.0
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
branch_head: d0437c61ab6af1feef07021aceda27330dcf035f
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
phase_owner: team_190
correction_cycle: R2
prior_verdict: _COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-CLASSB/WP-CB-UI-CLASSB_LGATE-V_VERDICT_v1.0.0.md
result: FAIL
---

# WP-CB-UI-CLASSB L-GATE_V Verdict (R2)

```yaml
wp: SFA-S003-P004-WP-CB-UI-CLASSB
gate: L-GATE_V
validator_engine: Cursor / Composer 2.5 (GPT — non-Claude)
result: FAIL
surface_checks: 1/7
constitutional_checks: 3/4
findings:
  - id: F-190-CLASSB-V-R2-01
    severity: BLOCKER
    summary: "R2 precondition still unmet — no team_99 DEPLOY_REPORT; live HTML unchanged from R1 FAIL probes."
    evidence: "Expected `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/DEPLOY_REPORT_v1.0.0.md` absent. Live curl 2026-06-03 @ d0437c6 validation: hub-home__inner=0, contact.webp=0, ptable__th=0, /community footer still `<a href=\"/community\">קהילה</a>`."
    disposition: R3
  - id: F-190-CLASSB-V-R2-02
    severity: MAJOR
    summary: "C1 hub — `.hub-home__inner` wrapper not on live `/`."
    evidence: "Branch hub_home.php L71 + classb.css L38. Live home 21 306 B: `hub-home__inner` count=0; legacy `.hub-intro` band without bounded column."
    disposition: R3
  - id: F-190-CLASSB-V-R2-03
    severity: MAJOR
    summary: "C2 community — banner still bare `.comm-banner` without contact.webp image."
    evidence: "Branch community.php L35–40 serves contact.webp when file exists. Live `/community`: `comm-banner` present, `contact.webp`=0, no `<img>`."
    disposition: R3
  - id: F-190-CLASSB-V-R2-04
    severity: MAJOR
    summary: "C3 search no-match — `.reqinfo` missing ◐ glyph (Board-B CTA)."
    evidence: "Branch search_results.php: `◐ בקשו הוספה`. Live `/search?q=zzznomatch190`: `class=\"reqinfo\" href=\"/community\">בקשו הוספה ←`."
    disposition: R3
  - id: F-190-CLASSB-V-R2-05
    severity: MAJOR
    summary: "C5 market list — `.ptable__th` not live; inline table style persists."
    evidence: "Branch market_list.php L172–174. Live `/market/`: `ptable__th`=0; `style=\"width:100%;border-collapse:collapse\"` count=1."
    disposition: R3
  - id: F-190-CLASSB-V-R2-06
    severity: MAJOR
    summary: "C6 footer — `/community` still self-links קהילה instead of aria-current span."
    evidence: "Branch _layout.php L138–142. Live community footer: `<a href=\"/community\">קהילה</a>`; `aria-current=\"page\"`=0."
    disposition: R3
  - id: F-190-CLASSB-V-R2-07
    severity: INFO
    summary: "C4 account logo overlap — NOT VERIFIED visually (deploy blocker); branch account_landing fix present."
    evidence: "Live `/account` 200; shell `sh__mark` + in-page `#sfa-logo` use both present — R2 browser QA deferred until fix-all HTML is live."
    disposition: R3
  - id: F-190-CLASSB-V-R2-08
    severity: INFO
    summary: "Branch fix-all + tests ready; blocked on deploy only (same as R1)."
    evidence: "composer test 141/141 @ d0437c6; ClassBRouteTest asserts hub-home__inner, ptable__th, aria-current; validate_aos 0 FAIL."
    disposition: builder-acknowledge
summary: "L-GATE_V R2 FAIL: despite the session brief that team_99 deploy is live, the repo has no Class B DEPLOY_REPORT and live sfa.nimrod.bio still serves pre-fix-all HTML (six of seven surface checks fail; only C7 /about 5-tier ladder passes). Branch fix-all code and composer 141/141 attest readiness. team_99 must FTPS-deploy branch tip, publish DEPLOY_REPORT SUCCESS with deployed SHA + smoke, then team_190 L-GATE_V R3."
```

## Engine constraint (IR#1 / IR#5)

Validator: **Cursor / Composer 2.5 (GPT — non-Claude)**. Builder team_10 (Claude Sonnet); L-GATE_B + QA = Claude. Cross-engine satisfied.

## Precondition gate (R2)

| Requirement | Result | Evidence |
|-------------|--------|----------|
| team_99 DEPLOY_REPORT = SUCCESS | **FAIL** | `DEPLOY_REPORT_v1.0.0.md` not in `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-CLASSB/` |
| Fix-all live on sfa.nimrod.bio | **FAIL** | Marker probes identical to R1 FAIL (2026-06-03) |

## Per-surface design-vs-live (mandate §3.1)

| Check | Surface | Live result | Notes |
|-------|---------|-------------|-------|
| C1 | Hub `/` | **FAIL** | `hub-home__inner`=0 |
| C2 | Community `/community` | **FAIL** | No `contact.webp` / `<img>` in banner |
| C3 | Search no-match | **FAIL** | `.reqinfo` without ◐ |
| C4 | Account `/account` | **NOT VERIFIED** | Deploy required |
| C5 | Market `/market/` + detail | **FAIL** | `ptable__th`=0 on list; detail not re-probed (list regression sufficient) |
| C6 | Footer on `/community` | **FAIL** | Self-link, not `<span aria-current="page">` |
| C7 | About `/about` | **PASS** | `tier-row` count=25 (5-tier ladder) |

## Constitutional checks (mandate §3.2)

| Check | Result | Evidence |
|-------|--------|----------|
| C8 Tokens/palette | **PASS (branch)** | `tokens.css` `--gj-paper: #f8fbf8`; live CSS order ends with `classb.css` (v=1780407586) — palette drift not observed; hub layout fix not live |
| C9 Scope | **PASS (branch)** | Fix-all confined to `sfa_delivery/` per BUILD_REPORT_FIXALL; no Python/migration |
| C10 Scope-guard (MINOR-2 → SRV-5) | **PASS (branch)** | REGISTER.md SRV-5; hub stats unchanged in fix-all diff |
| C11 Tests | **PASS (branch)** | composer 141/141; validate_aos 0 FAIL — **not attested on deployed SHA** (no deploy) |

## R1 → R2 delta

Live probes on 2026-06-03 show **no change** from R1 FAIL markers. R2 cannot pass until team_99 publishes DEPLOY_REPORT and live HTML includes fix-all markers.

## Verdict

**FAIL** — do not advance to LOD500_LOCKED. team_99 deploy → DEPLOY_REPORT → team_190 L-GATE_V R3.

— team_190
