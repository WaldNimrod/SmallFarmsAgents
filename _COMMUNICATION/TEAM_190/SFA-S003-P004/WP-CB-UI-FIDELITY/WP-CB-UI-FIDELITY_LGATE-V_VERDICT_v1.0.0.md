---
id: WP-CB-UI-FIDELITY_LGATE-V_VERDICT_v1.0.0
type: VERDICT
gate: L-GATE_V
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-04
project: smallfarmsagents
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
subject: Crop-book + market UI fidelity — LAUNCH GATE (live acca9b2)
mandate: _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/VALIDATION_MANDATE_team190_LGATE-V_2026-06-04_v1.0.0.md
live_sha: acca9b2
served_asset_version: 1780576560
validator_engine: Cursor Agent (GPT-5.x — non-Claude)
phase_owner: team_190
---

# L-GATE_V Verdict — SFA-S003-P004-WP-CB-UI-FIDELITY (LAUNCH GATE)

## Engine attestation (IR#1 / IR#5)

**Validator engine:** Cursor Agent (GPT-5.x — non-Claude).  
LOD author + L-GATE_B = Claude (team_100); builder = Claude (team_10). This launch-gate verdict satisfies cross-engine separation. A Claude-run L-GATE_V verdict would be void.

## Verdict (mandate §4)

```yaml
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
gate: L-GATE_V
validator_engine: Cursor Agent (GPT-5.x — non-Claude)
live_sha: acca9b2
served_asset_version: 1780576560
result: PASS_WITH_FINDINGS
ac_matrix:
  AC-1: pass
  AC-2: pass
  AC-3: pass
  AC-4: pass
  AC-4b: pass
  AC-5: pass
  AC-6: pass
  AC-7: pass
visual_divergences:
  - surface: hub / market (Board-B)
    severity: INFO
    summary: English mono eyebrows (CALC, MARKET, CROP-BOOK, etc.) remain on live tiles/cards — Board-B allows decorative bilingual eyebrows; LOD400 Q5/WI-7 non-blocking.
    evidence: live `/` modtile `<small>` labels; mandate §5 note (team_35 WI-7 tracked separately)
  - surface: crop-book entry (Board-A)
    severity: INFO
    summary: patch01 C3 literal `minmax(120px)` superseded by FIDELITY visual remediation — live grid restored to Board-A ~168px tracks (by design at acca9b2).
    evidence: live `crop-book-v1.css?v=1780576560` `.cards-grid { minmax(168px, 1fr) }`; CDP cardWidth ~190px @1440, ~164px @375; team_100 `live_crop-book-grid_*.png`
findings:
  - id: F-190-FID-V-01
    severity: INFO
    summary: Embedded `window.SFA_CROP_BOOK` JSON on `/calc/` contains English field keys (`spacing_in_row_cm`, etc.) — not user-visible; visible calc UI has no English unit tokens in rendered text scan.
    evidence: curl `/calc/?v=1780576560` script block L782+; CDP innerText engUnits on calc is JSON-key artifact only
    disposition: no action (AC-2 scoped to user-facing render)
  - id: F-190-FID-V-02
    severity: INFO
    summary: Legacy URL `/crop-book/table?category=summer` still returns 0 rows (pre-D-4b path); UI leading-questions now route to `/crop-book/?season=summer` (19 crops).
    evidence: curl counts table_cat=0 vs season_summer=19; `CropBookViewController::questions()` hrefs
    disposition: acceptable — not linked from production UI
  - id: F-190-FID-V-03
    severity: INFO
    summary: patch01 regression C3 (120px dense grid) intentionally superseded by FIDELITY Board-A 168px card template; all other patch01 C1–C2, C4–C9 hold on live acca9b2.
    evidence: CSS byte-identical to `acca9b2`; open-tools 4 tiles; hub-cta; terminology; see §3.3 matrix
    disposition: team_100 acknowledge in LOD500 lock notes
summary: >
  L-GATE_V LAUNCH GATE PASS_WITH_FINDINGS. Live https://sfa.nimrod.bio at SHA acca9b2 with cache-bust
  ?v=1780576560 matches deploy commit (crop-book-v1.css, classb.css, crop-book-deep.css byte-identical).
  AC-1..AC-7 pass on independent CDP/curl probes: no user-facing raw multi-decimals; Hebrew market chips;
  crop/calc filters non-empty; single lettuce hero with wc-lettuce.png watercolor (no duplicate h1/green blob);
  #identity anchor on SECTION; table⇄cards toggle + fetchHistory + depth tabs work; 70/70 crop cards with wc art
  at ~168px; centered `.cb-crop-detail` max-width 1120px; no 375 overflow on probed routes incl. /crop-book/table;
  patch01 hub/terminology/CTA regression holds. INFO-only notes: English eyebrows (WI-7), 168px supersedes patch01
  120px density, calc JSON keys, dead table?category= URL. team_100 may advance to LOD500_LOCKED.
```

## AC matrix evidence (live @ `?v=1780576560`)

| AC | Result | Key evidence |
|----|--------|----------------|
| **AC-1** | **pass** | CDP text scan all probed pages: `badDecimalCount=0`. Lettuce visible HTML (scripts stripped): no `\d+\.\d{3,}`. `FieldRegistry::fmtNumber` in `book_crop.php`, `prov_value.php`, `prov_table.php`. |
| **AC-2** | **pass** | Crop-book + lettuce + market: no English `cm\|days\|weeks\|count` in visible text. Market chips Hebrew (`ירוקי עלים`, `קטניות טריות`, `ירקות שורש`, …). Lettuce single `<h1>חסה</h1>`. Calc visible UI clean; JSON embed INFO only (F-190-FID-V-01). |
| **AC-3** | **pass** | `/crop-book/` baseline 70 ccards; `?season=summer` 19; `?season=winter` 32; `?dtm_max=60` 23. Leading questions (`/crop-book/questions`): hrefs `?season=summer\|winter`, `?dtm_max=60` — all non-zero. Market category filter Hebrew chips present. |
| **AC-4** | **pass** | Lettuce: 1× `.crophero` with `<img … wc-lettuce.png>`; `heroSections=1`; `hasGreenIconBox=false`; no `cb-crop-hero__icon`. Lede + meta pills preserved under deduped block. |
| **AC-4b** | **pass** | `document.getElementById('identity')` → `SECTION.crophero`, bbox height > 0 (CDP). |
| **AC-5** | **pass** | CDP clicks: crop-book table⇄cards toggle OK; lettuce depth-tab click OK; market `typeof fetchHistory === 'function'` + range button click OK. Routes HTTP 200: `/search`, `/calc/`, `/crop-book/table`. Full 14-calc matrix not exhaustively clicked — spot-check + branch tests 192/192. |
| **AC-6** | **pass** | **Crop-book entry:** `minmax(168px,1fr)`, 70 `wc-*.png` images, 0 glyph-only cards, `.aud-head { justify-content: flex-start }`, 7-col desktop grid per team_100 screenshot. **Crop page:** `max-width:1120px; margin-inline:auto` (margin 142px @1440), single hero watercolor, centered column. **375:** all probed pages `scrollWidth === clientWidth` incl. `/crop-book/table`. Cross-checked team_100 `live_evidence_acca9b2/`. No BLOCKER/MAJOR vs Board-A/B on focus surfaces. |
| **AC-7** | **pass** | `validate_aos.sh` 29 PASS / 20 SKIP / 0 FAIL. `composer test` 192/192. patch01 C1–C2,C4–C9 regression (§3.3). `--gj-paper: #f8fbf8`. Delivery CSS byte-identical to `acca9b2`. |

## §3.3 Regression — patch01 C1–C9 @ `acca9b2`

| ID | Result | Notes |
|----|--------|-------|
| C1 | **pass** | `auto-fit` hub-grid; 4 open-tools tiles |
| C2 | **pass** | `is-dev` Field-Log `<div aria-disabled>` |
| C3 | **pass*** | *FIDELITY supersession:* live `168px` grid (Board-A), not patch01 `120px` — intentional (INFO F-190-FID-V-03) |
| C4 | **pass** | No overflow @375 on `/`, `/crop-book/` |
| C5 | **pass** | Constitutional (delivery-tier, palette, tests) |
| C6 | **pass** | `גנן`; tagline present |
| C7 | **pass** | `חקלאות מקומית` / `חקלאי מקומי`; no `קטנה/קטן` on hub/community/market |
| C8 | **pass** | No Tend on `/about`, `/crop-book/lettuce/` |
| C9 | **pass** | `.hub-cta` dual offers + WhatsApp primary |

**FIDELITY blockers (D-1..D-5):** all remediated on live — confirmed by AC-1..AC-4 probes above.

## Deploy verification

| Check | Result |
|-------|--------|
| Live SHA | `acca9b2` (git object resolves) |
| CSS byte-match | `crop-book-v1.css`, `classb.css`, `crop-book-deep.css` vs `git show acca9b2:sfa_delivery/public_assets/css/*` |
| Markers | `.cards-grid { minmax(168px,1fr) }`; `.cb-crop-detail { max-width:1120px; margin-inline:auto }`; `.aud-head … flex-start` |
| team_100 evidence | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-FIDELITY/live_evidence_acca9b2/` (5 screenshots — corroborated) |

## Probe log (2026-06-04)

- Tools: `/usr/bin/curl`, `qa_probe`-style CDP (`/tmp/fidelity_lgate_v_probe.mjs`, `/tmp/fidelity_ac5_clicks.mjs`)
- Full JSON: `/tmp/fidelity_probe/summary.json` (team_190 session artifact)

## Disposition

**PASS_WITH_FINDINGS** → team_100 may advance **WP-CB-UI-FIDELITY** to **LOD500_LOCKED** and record the launch gate. All findings are **INFO**; no BLOCKER/MAJOR. team_35 WI-7 design completions remain separately tracked per mandate §5 footer.
