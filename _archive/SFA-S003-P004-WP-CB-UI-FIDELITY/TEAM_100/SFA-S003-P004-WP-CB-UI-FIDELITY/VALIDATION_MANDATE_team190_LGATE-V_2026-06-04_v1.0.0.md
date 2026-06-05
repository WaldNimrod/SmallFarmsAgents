# VALIDATION MANDATE — WP-CB-UI-FIDELITY (L-GATE_V — LAUNCH GATE) — team_100 → team_190 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 (Opus) · **To:** team_190 (**NON-CLAUDE**, IR#1/#5) · **Routed by:** team_00
**Live target:** https://sfa.nimrod.bio · **deployed SHA `acca9b2`** · served **`?v=1780576560`** (team_99 DEPLOY_REPORT_v2.0.0, SUCCESS, 67 watercolors + code; 80 files)
**Gate:** **L-GATE_V** — the launch gate. Live visual + functional validation design-vs-Board-A/B. On PASS → **LOD500_LOCKED**.

## 0. Cross-engine (IR#1/#5 — MANDATORY)
LOD author + builders = Claude (team_100/team_10); L-GATE_B = Claude (team_100). This L-GATE_V **MUST run on a NON-CLAUDE engine** (Cursor/GPT/Codex). State the engine in the verdict header. A Claude verdict is void.

## 1. Context — what shipped, in two deploys
WP-CB-UI-FIDELITY remediated team_00's launch-quality concerns. Two deploys landed it:
- **Deploy 1 (`4c9bab2`)** — FIDELITY blocker fixes (D-1 number-format, D-2 Hebrew units, D-3 Hebrew market chips, D-4 season/leading-question filters, D-5 hero dedup) + patch01 WI-1..9 subsumed.
- **Deploy 2 (`acca9b2`, live now)** — crop-book **visual remediation** + **70 crop icons** + the §4.1 prov fix:
  - card grid restored to the team_35 **168px** template (was over-densified 120px); crop detail page **centered** (`.cb-crop-detail max-width:1120px`); view-toggle aligned;
  - **70/70 crops now render watercolor art** (was 14): 14 recovered via slug-map + 43 new Devora masters (transparent);
  - provenance drill values formatted (no raw 6-decimal in the audit column).

**team_100 independent live verification (PASS, evidence in `live_evidence_acca9b2/`):** 70 crops render art (grid screenshot; 69 distinct `wc-*.png` served), served CSS has `minmax(168px)` + `.cb-crop-detail{max-width:1120px;margin-inline:auto}` + `aud-head…flex-start` (cache-busted at `?v=1780576560`), single `<h1>חסה</h1>`, 0 raw 6-decimals (incl. drill), 0 English unit codes, served image 200, CDP no-overflow.

## 2. Design SSoT
- Board-A (crop book + calculator) / Board-B (hub/market/…): paths in the LOD400 frontmatter `design_ssot`.
- LOD400 (v1.1.0): `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md` — the AC matrix (AC-1..AC-7).

## 3. Checks — run on the LIVE site (cache-bust to `?v=1780576560`) + design-vs-Board-A/B

### 3.1 Acceptance criteria (LOD §5) — live
- **AC-1** No raw multi-decimal numbers anywhere user-facing (crop/variety/calc + drill-depth provenance). CDP text scan: no `\d+\.\d{3,}`.
- **AC-2** No English unit codes; no raw English enum/category keys; market chips + crop filters Hebrew; exactly one unit per value.
- **AC-3** Filters return correct, non-empty sets — market category; crop-book family / **עונה** (season-from-months) / dtm_max / sow / frost; the leading-questions (summer/winter/fast). None erroneously 0.
- **AC-4 / AC-4b** Crop hero renders ONCE, correctly sized, no green blob; `#identity` section-nav anchor resolves.
- **AC-5** Interactions: table⇄cards toggle, audience switch, depth tabs, advanced-filter toggle, market-detail graph range (7י/28י re-fetch), calc (14 calcs + book-chips + AssumptionField + export), search — all function (CDP clicks).
- **AC-6** Per-surface design-vs-live (desktop 1440 + mobile 375) — no open BLOCKER/MAJOR divergence from Board-A/B. **Incl. the new visual round:** crop cards ~168px with watercolor art (not glyph); crop detail a centered column (not full-bleed); `/crop-book/table` @375 no horizontal overflow.
- **AC-7** No regression of the "WORKS" list; palette #f8fbf8 (no cream); no 375 overflow on any route.

### 3.2 Visual fidelity (the heart of this gate — team_00's launch concern)
Per-surface CDP screenshot pairs vs Board-A/B at **1440 + 375**: crop-book entry (cards/art/toggle/density), crop page (hero, headline values, topic cards, sections, varieties), calculator, hub, market, search. List every divergence with severity. The crop-book entry + crop page are the focus (team_00 flagged them); confirm they now read as the sketch.

### 3.3 Regression — prior gates still hold on live
Confirm patch01 **C1–C9** (hub full-width + Field-Log is-dev tile, dense crop grid, גנן, חקלאות מקומית terminology, no Tend on /about, hub-cta) and the FIDELITY blockers (Hebrew units, single hero, Hebrew market chips, working filters) all still hold at `acca9b2`.

## 4. Verdict → `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/WP-CB-UI-FIDELITY_LGATE-V_VERDICT_v1.0.0.md`
```yaml
wp: SFA-S003-P004-WP-CB-UI-FIDELITY
gate: L-GATE_V
validator_engine: <non-Claude — name it>
live_sha: acca9b2
served_asset_version: 1780576560
result: PASS | PASS_WITH_FINDINGS | FAIL
ac_matrix: { AC-1: pass, AC-2: pass, ... AC-7: pass }
visual_divergences:
  - surface: <crop-book entry | crop page | ...>
    severity: BLOCKER | MAJOR | MINOR | INFO
    summary: ...
    evidence: <screenshot / live URL>
findings: [...]
summary: <one paragraph>
```
- **PASS / PASS_WITH_FINDINGS** → team_100 advances WP-CB-UI-FIDELITY to **LOD500_LOCKED** + records the gate; team_35 design completions (WI-7) tracked separately.
- **FAIL** → team_100 dispositions + routes a fix round.

## 5. Cursor prompt (paste into the NON-CLAUDE validator)
> You are **team_190** on a **NON-CLAUDE** engine (Cursor/GPT/Codex — confirm in the verdict header; IR#1/#5). Repo
> `/Users/nimrod/Documents/SmallFarmsAgents`, branch `claude/ui-polish-hub-cropbook-2026-06-03`, deployed LIVE to
> https://sfa.nimrod.bio at SHA `acca9b2`, served `?v=1780576560`. Gate: **L-GATE_V (launch gate)** for
> **WP-CB-UI-FIDELITY**. **Cache-bust every asset to `?v=1780576560`** (force cf-cache MISS). Run §3 against the
> LIVE site + design-vs-Board-A/B (Board-A/B paths in LOD400 frontmatter; LOD `_aos/work_packages/S003/
> SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md`): the AC matrix AC-1..AC-7 (§3.1); per-surface visual fidelity at
> 1440 + 375 (§3.2) — focus on the crop-book entry (cards ~168px with watercolor art, not glyph; toggle aligned) and
> the crop page (single hero no green blob; centered column not full-bleed); and the regression set (§3.3: patch01
> C1–C9 + FIDELITY blockers still hold). Emit the verdict YAML (§4) to the path above. team_100's live verification +
> evidence screenshots: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-UI-FIDELITY/live_evidence_acca9b2/`.

---
*This is the launch gate. team_99 DEPLOY_REPORT_v2.0.0 (SUCCESS, acca9b2). team_50 re-audit runs in parallel; prior NO-GOs subsumed. team_35 design completions (WI-7: Q2 wording / Q3 unit / Q4 question set / Q5 eyebrows) tracked separately and do not block this gate unless a divergence is BLOCKER/MAJOR.*
