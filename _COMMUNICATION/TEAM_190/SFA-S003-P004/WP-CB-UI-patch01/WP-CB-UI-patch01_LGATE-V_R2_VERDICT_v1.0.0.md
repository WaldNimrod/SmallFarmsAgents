---
id: VERDICT_SFA-S003-P004-WP-CB-UI-patch01_L-GATE_V_R2_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-04
type: validation_verdict
wp: SFA-S003-P004-WP-CB-UI-patch01
gate: L-GATE_V
mandate: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-patch01/VALIDATION_MANDATE_team190_LGATE-V_R2_2026-06-04_v1.0.0.md
branch: claude/ui-polish-hub-cropbook-2026-06-03
branch_head_live: 6703313
validator_engine: Cursor Agent (GPT-5.x — non-Claude)
phase_owner: team_190
correction_cycle: R2
result: PASS_WITH_FINDINGS
---

# WP-CB-UI-patch01 L-GATE_V Verdict (R2)

## Engine constraint (IR#1 / IR#5)

**Validator:** Cursor Agent (GPT-5.x — non-Claude). Builder team_10 (Claude Sonnet); L-GATE_B verifier team_100 (Claude Opus). Cross-engine satisfied for this gate.

## Precondition (R2)

| Requirement | Result | Evidence |
|-------------|--------|----------|
| team_99 DEPLOY_REPORT SUCCESS @ `6703313` | **PASS** | `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md` |
| Live CSS byte-identical to `6703313` @ `?v=1780520599` | **PASS** | `crop-book-v1.css` 58870 B, `classb.css` 49231 B, `crop-book-deep.css` 20618 B — SHA-256 match `sfa_delivery/public_assets/css/*` |
| Cache-bust discipline | **PASS** | All CSS/HTML probes used `?v=1780520599`; WI-5 markers read from `crop-book-v1.css`, WI-6 from `classb.css` (not `hub.css`) |

```yaml
wp: SFA-S003-P004-WP-CB-UI-patch01
gate: L-GATE_V
correction_cycle: R2
validator_engine: Cursor Agent (GPT-5.x — non-Claude)
branch_head_live: 6703313
served_asset_version: 1780520599
result: PASS_WITH_FINDINGS
checks: 9/9
findings:
  - id: F-190-PATCH01-V-R2-01
    severity: INFO
    summary: "/crop-book/table @375 horizontal overflow (WI-8/9) — acknowledged known residual on live 6703313; not in patch01 C1–C9 scope."
    evidence: "Mandate §3 + team_100 CDP (scrollWidth ≈517 > 375). team_190 CDP @375 on 2026-06-04: documentElement/body max scrollWidth=375 (no html overflow flag); table node scrollWidth=339 ≤ viewport — residual may require scroll/interaction to surface. WI-8 `.cb-table-page { overflow-x: clip }` + WI-9 undeployed on 6703313 (land with WP-CB-UI-FIDELITY)."
    disposition: "deferred to FIDELITY deploy / team_50 PRELAUNCH-QA (SFA-S003-P004-WP-PRELAUNCH-QA)"
known_residual_ack: "/crop-book/table @375 overflow — WI-8/9 undeployed; deferred to FIDELITY deploy (acknowledged, not a C1–C9 failure)"
summary: "L-GATE_V R2 PASS_WITH_FINDINGS (9/9). Live https://sfa.nimrod.bio at deployed SHA 6703313 serves patch01 WI-1..WI-7 with asset version 1780520599; the three delivery CSS files are byte-identical to the deploy commit. Hub open-tools row uses auto-fit with four tiles (three live links + non-clickable Field-Log is-dev teaser), crop-book grid is densified (10 tracks @ 1440px), mobile overflow is clean on / and /crop-book/, constitutional delivery-tier checks pass (validate_aos 29/19/0, composer 168/168, ClassBRouteTest patch01 filters 14/14), terminology and hub CTA/copy match mandate, and /about plus crop variety pages have no customer-facing Tend. One INFO records the pre-agreed /crop-book/table WI-8/9 deferral. team_100 may advance patch01 to LOD500_LOCKED."
```

## Per-check matrix (C1–C9) — live `6703313` @ `?v=1780520599`

| ID | Requirement | Live | Evidence |
|----|-------------|------|----------|
| C1 | Hub open-tools full width + 4 tiles | **PASS** | Live `classb.css`: `.hub-grid { … repeat(auto-fit, minmax(248px, 1fr)) … }`. Live `/`: open-tools block = 3× `<a class="modtile">` + 1× `<div class="modtile modtile--soil is-dev" aria-disabled="true">` (4 tiles). |
| C2 | Field-Log `is-dev` non-clickable | **PASS** | Live `/`: `יומן השדה` + foot `בפיתוח`; `is-dev` on `<div>` (no `<a … is-dev … href>`). `classb.css` `.modtile.is-dev` dashed/muted rules present. |
| C3 | Crop-book dense grid, no overflow, RTL, 200 | **PASS** | HTTP 200. Live `crop-book-v1.css`: `.cards-grid { … minmax(120px, 1fr); gap: 10px }`. CDP @1440: 10 columns first row (`colsFirstRow: 10`), `dir: rtl`, `htmlSW === clientW`. WI-5 `cb-paths { display: grid }` in `crop-book-v1.css`. |
| C4 | Mobile legible, no overflow on `/` + `/crop-book/` | **PASS** | `qa_probe.mjs` CDP @375: hub + crop-book `scrollWidth=375`, `clientWidth=375`, `overflow: false`. `/crop-book/table` excluded per mandate §3. |
| C5 | Constitutional delivery-tier | **PASS** | Deploy slice `6703313` + build `3c74c87`/`f9d274c`: `sfa_delivery/` only (no Python/migrations). Live `tokens.css`: `--gj-paper: #f8fbf8`. `_layout.php` @6703313: `classb.css` last stylesheet. `validate_aos.sh`: 29 PASS / 19 SKIP / 0 FAIL. `composer test`: 168/168. IR#4: no `_aos/roadmap.yaml` edit in `3c74c87..f9d274c`. |
| C6 | גנן + one-line tagline | **PASS** | Live `/`: `audcard__t` → `גנן` (not `גינאי ביתי`). Live `classb.css` L48–49: `.hub-intro p { white-space: nowrap … }` @ `min-width: 900px`. |
| C7 | חקלאות/חקלאי מקומי terminology | **PASS** | Live `/`: `חקלאות מקומית`, `חקלאי מקומי`; forbidden `חקלאות קטנה` / `חקלאי קטן` count 0 on `/`, `/community`, `/market/`. `market_disclaimer.php` live: `השוק החקלאי המקומי`. |
| C8 | No Tend on /about + crop/variety | **PASS** | Live `/about` + `/crop-book/lettuce/`: no `Tend` substring. *(Hub coming-soon tile still mentions Tend — out of C8 scope per mandate §2.)* |
| C9 | `.hub-cta` dual offers, primary → WhatsApp | **PASS** | Live `/`: `.hub-cta` with secondary → `/community`, primary → `https://wa.me/972547776770`, `hub-cta__card--primary` class; live `classb.css` primary/secondary CTA styles. |

## WI-5/6/7 spot-confirm (non-gating)

| Item | Result | Evidence |
|------|--------|----------|
| WI-5 entry-path cards | **PASS** | Live `crop-book-v1.css`: `.cb-paths { display: grid; … }` |
| WI-6 app-shell logo | **PASS** | Live `classb.css`: `.sh__mark { … width: 34px; height: 34px; overflow: hidden }` + `.sh__mark svg { width: 100% … }` |
| WI-7 detail pages @375 | **PASS** | CDP @375: `/crop-book/lettuce/`, `/market/prd059` — no horizontal overflow |

## Branch verification (supplemental)

| Artifact | Result |
|----------|--------|
| `composer test` | 168/168 OK (2026-06-04) |
| `validate_aos.sh` | 29 PASS / 19 SKIP / 0 FAIL |
| ClassBRouteTest patch01 filters | 14/14 OK |
| Build commits | `3c74c87` (WI-1/2), `f9d274c` (WI-3/4), `6703313` (WI-7 deploy) |

## Live probe log (2026-06-04)

- Base: `https://sfa.nimrod.bio` · asset `?v=1780520599`
- Tools: `/usr/bin/curl` (HTML/CSS), `qa_probe.mjs` + CDP scripts (`/tmp/patch01_lgate_r2_probe.json`, overflow/col probes)
- team_100 re-audit reference: `TEAM100_VERIFICATION_REAUDIT_2026-06-04.md`

## Disposition

**PASS_WITH_FINDINGS** → team_100 may advance **WP-CB-UI-patch01** to **LOD500_LOCKED** and record L-GATE_V R2. INFO finding F-190-PATCH01-V-R2-01 is informational only (mandate §3).
