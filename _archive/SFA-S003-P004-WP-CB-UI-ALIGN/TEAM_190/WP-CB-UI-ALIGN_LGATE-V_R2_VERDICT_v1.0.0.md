---
id: VERDICT_SFA-S003-P004-WP-CB-UI-ALIGN_L-GATE_V_R2_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
  - team_99
date: 2026-06-02
type: validation_verdict
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_V
round: 2
live_url: https://sfa.nimrod.bio
deployed_sha: 58c4899bdfa0eebfb6af438a8340c85b4955bca0
deployed_short_sha: 58c4899
deploy_ref: origin/main (team_99 R3 SUCCESS per commit 58c4899; team_50 LIVE_REQA_R2_2026-06-02)
prior_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-ALIGN/WP-CB-UI-ALIGN_LGATE-V_VERDICT_v1.0.0.md
validator_engine: Cursor / Composer (non-Claude)
result: FAIL
---

# WP-CB-UI-ALIGN L-GATE_V Verdict (Round 2)

```yaml
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_V
round: 2
validator_engine: Cursor / Composer (non-Claude)
live_url: https://sfa.nimrod.bio
deployed_sha: 58c4899bdfa0eebfb6af438a8340c85b4955bca0
result: FAIL
checks:
  - id: R2-V01
    result: PASS
    evidence: "fetch /calc/print→200 text/html; /calc/print?crop=lettuce→200; /calc/export.csv→200 text/csv; /calc/export.pdf→404 (retired). calc_dash PDF href=/calc/print data-calc-export=pdf."
  - id: R2-V02
    result: FAIL
    evidence: "document.body.innerText on /crop-book/lettuce/ and /crop-book/watermelon/ contains literal 'family: variety' (span.meta in rotation_hint). team_50 scanned 'family:variety' (no space) — false PASS. Root: sfa_delivery/templates/macros/rotation_hint.php L33 <span class=\"meta\">family: <?= $family_lat ?>."
  - id: R2-V03
    result: PASS_WITH_FINDINGS
    evidence: "#ctx-crop-slug has 71 <option> (70 Hebrew crops + placeholder). SFA_CROP_BOOK script block absent on live — crop_field_enrichment empty on mirror (graceful degrade per HubController). Binding wiring present in code but not exercisable until enrichment rows exist."
  - id: V1
    result: PASS
    evidence: "computed body backgroundColor rgb(248,251,248) on /crop-book/lettuce/ and /calc/."
  - id: V2
    result: PASS
    evidence: ".sh + use[href=\"#sfa-logo\"] on /, /crop-book/, /calc/; no .gj-shell/.dt-shell/.sfa-nav."
  - id: V3
    result: FAIL
    evidence: "Design-vs-live pairs captured evidence_LGATE-V_R2/*.png. Shell/palette/type PASS; crop simple/full/drill CONTENT FAIL — visible 'family: variety' on simple depth (see R2-V02)."
  - id: V4
    result: PASS
    evidence: "typeof SFA_CALC object keys seed,beds,yield,revenue,pop,fert; seed recompute bed_len 30→25→40 changes output 4888.9g→3055.6g→4888.9g; 14 modcards 8 disabled; export routes per R2-V01."
  - id: V5
    result: FAIL
    evidence: "RTL dir=rtl; Hebrew enums visible (חצי-עמיד, זריעה ישירה). BLOCKER-class leak: 'family: variety'. MINOR: disabled modcard still cites (succession_interval_weeks) on /calc/."
  - id: V6
    result: PASS
    evidence: "fetch 200: /, /crop-book/, /crop-book/lettuce/, /market/, /calc/, /calc/export.csv (browser session)."
  - id: V7
    result: PASS
    evidence: "F-QA-04 mobile-nav + F-190-UIALIGN-02 .sh__icon <a> acceptable; Class B follow-up only."
findings:
  - id: F-190-UIALIGN-R2-V02
    severity: MAJOR
    where: "macros/rotation_hint.php · all crop pages with rotation hint (e.g. /crop-book/lettuce/, /crop-book/watermelon/)"
    fix: "Remove or hide <span class=\"meta\">family: …</span> from farmer-facing UI (L33). If Latin family name is needed, use Hebrew-only display or move to data-attribute/admin-only. Re-scan innerText for 'family:' after deploy."
  - id: F-190-UIALIGN-R2-V04
    severity: MINOR
    where: "/calc/ disabled modcard copy"
    fix: "Replace parenthetical succession_interval_weeks with Hebrew field label in disabled-state message (R1 F-V04 carry-over)."
  - id: F-190-UIALIGN-R2-V05
    severity: MINOR
    where: "team_50 LIVE_REQA R2 V02 probe"
    fix: "Expand raw-key scan to include 'family: variety' (space) and rotation_hint .meta — not only family:variety and HTML grep without space."
summary: "R1 fixes V01 (print route) and V03 (crop select) are verified PASS on live @ 58c4899. R1 fix V02 is NOT closed: literal 'family: variety' remains visible on crop pages — same AC-6/AC-3 content-fidelity class as R1. L-GATE_V R2 FAILS; ADR042 blocked. team_100 → one-line rotation_hint fix → team_50 re-QA with expanded grep → L-GATE_V R3."
```

## R1 finding re-verification (live @ 58c4899)

| R1 ID | Severity | R2 result | Live evidence |
|-------|----------|-----------|---------------|
| **V01** PDF export 404 | BLOCKER | **PASS** | `/calc/print` 200 HTML; `?crop=lettuce` 200; dash PDF button `href=/calc/print`; `/calc/export.pdf` 404 expected (route retired). |
| **V02** raw enum/keys on crop pages | MAJOR | **FAIL** | `direct_seed`, `half_hardy`, `family:variety` absent; **`family: variety` present** in `innerText` on lettuce + watermelon. |
| **V03** empty crop `<select>` | MAJOR | **PASS** (selector) | 71 options, Hebrew labels. Book-value embed empty on mirror (not a regression of V03 selector fix). |

## Per-screen visual fidelity (AC-3) — design vs live @ 58c4899

Design reference: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` frames `book-entry`, `crop-lettuce` (simple/full/drill), `calc-page`.

| Screen | Live URL | Shell / palette / type | Content / components | Pair evidence |
|--------|----------|------------------------|----------------------|---------------|
| **book-entry** | `/crop-book/` | **PASS** | **PASS** — watercolor hero, filter bar, crop cards | `evidence_LGATE-V_R2/lgate-v-r2-live-book-entry.png` |
| **crop simple** | `/crop-book/lettuce/` depth=פשוט | **PASS** | **FAIL** — `family: variety` visible in rotation hint `.meta` | `evidence_LGATE-V_R2/lgate-v-r2-live-crop-simple-lettuce.png` |
| **crop full** | `/crop-book/lettuce/` depth=מלא | **PASS** | **PASS** (no new raw keys in sampled view; rotation hint may still show on scroll) | `evidence_LGATE-V_R2/lgate-v-r2-live-crop-full-lettuce.png` |
| **crop drill** | `/crop-book/lettuce/` depth=העמקה | **PASS** | **PASS** (variety table; Hebrew labels) | `evidence_LGATE-V_R2/lgate-v-r2-live-crop-drill-lettuce.png` |
| **calc-dash** | `/calc/` | **PASS** — sun-active nav, context strip, 14-card grid | **PASS** — SFA_CALC live recompute; PDF→`/calc/print`; selector populated | `evidence_LGATE-V_R2/lgate-v-r2-live-calc-dash.png` |

## Disposition

**FAIL — no ADR042 closure.** Route team_100 → remove `rotation_hint.php` L33 debug meta → team_50 live re-QA (include `family: variety` in scan) → **L-GATE_V R3**.

**Passes without rework:** R2-V01 print export, V1 cream ground, V2 shell, V4 calc interactivity + exports, V6 routes, V7 design-gap acceptances, V03 crop selector population.

---
*team_190 · L-GATE_V Round 2 · IR#1/#5 satisfied (non-Claude validator).*
