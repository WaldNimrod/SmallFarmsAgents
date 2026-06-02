---
id: VERDICT_SFA-S003-P004-WP-CB-UI-ALIGN_L-GATE_V_v1.0.0
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
round: 1
deployed_sha: b72bcca746838e80cce99013c00af4d501b2fac5
deployed_short_sha: b72bcca
live_url: https://sfa.nimrod.bio
validator_engine: Cursor / Composer (non-Claude)
result: FAIL
---

# WP-CB-UI-ALIGN L-GATE_V Verdict (Round 1)

```yaml
wp: SFA-S003-P004-WP-CB-UI-ALIGN
gate: L-GATE_V
round: 1
validator_engine: Cursor / Composer (non-Claude)
deployed_sha: b72bcca746838e80cce99013c00af4d501b2fac5
result: FAIL
checks:
  - id: V1
    result: PASS
    evidence: "Live /crop-book/ computed body backgroundColor = rgb(248,251,248) (#f8fbf8); --gj-paper computed #f8fbf8. Served tokens.css?v=1780397450 (page-linked cache bust): zero #f5f3ec/Cool Stone/--paper:; body uses var(--gj-paper). Note: bare /public_assets/css/tokens.css (no ?v=) still serves stale pre-deploy cream — pages use ?v= so AC-1 holds on rendered pages."
  - id: V2
    result: PASS
    evidence: "/, /crop-book/, /market/, /calc/ — .sh present, #sfa-logo <use>, no .gj-shell/.dt-shell/.sfa-nav in DOM. crop-book active nav bg rgb(77,106,44) #4d6a2c; calc active rgb(164,113,26) #a4711a; market spot-checked. ≤899px: .sh__nav display none, .sh__nav--mobile flex; mobile calc tab color #a4711a. .sh__icon is <a href=\"/search\">."
  - id: V3
    result: FAIL
    evidence: "Design-vs-live pairs captured under evidence_LGATE-V_R1/ (see per-screen table below). Shell/palette/type (Carmela brand, white-green ground, LOD300 .sh chrome) align on all five screens; crop content surfaces leak raw enum/field keys into visible UI (direct_seed, half_hardy, yield_per_bed_m, price_documented) — not pixel-faithful to LOD300 Hebrew-only copy."
  - id: V4
    result: FAIL
    evidence: "typeof SFA_CALC === 'object'; keys [seed,beds,yield,revenue,pop,fert]. 14 modcards / 8 modcard--disabled / 8 modcard__soon on /calc/. Live recompute: seed 3,666.7→4,888.9 g when bed_len 30→40; beds 3.3→6.7 ערוגות when target_kg 100→200. /calc/export.csv → 200 (UTF-8 BOM, sample crop=חסה). /calc/export.pdf → HTTP 404 (browser + curl, with/without query) despite route in b72bcca routes.php — hosting/Slim path not reachable for .pdf extension."
  - id: V5
    result: FAIL
    evidence: "document.documentElement.dir=rtl; no Array/object Object. Watercolor hero on book-entry + crophero on /crop-book/lettuce/. Raw keys visible in production copy: crop cards show direct_seed, half_hardy, family:variety; finfo/request links append yield_per_bed_m, price_documented; calc disabled cards show rows_per_bed, days_in_nursery, succession_interval_weeks; market filter chips show English taxonomy slugs (alliums, fruiting_vegetables)."
  - id: V6
    result: PASS
    evidence: "HTTP 200: /, /crop-book/, /crop-book/lettuce/, /market/, /calc/, /calc/export.csv. composer test not run (phpunit absent in vendor — pre-existing per mandate; non-blocking)."
  - id: V7
    result: PASS
    evidence: "F-QA-04 remediation acceptable as shipped: mobile nav legible, active calc tab rgb(164,113,26), text-decoration none. F-190-UIALIGN-02 .sh__icon <a> acceptable for /search routing. team_35 Class B follow-up on mobile-nav SSoT gap — not a Class A blocker."
findings:
  - id: F-190-UIALIGN-V01
    severity: BLOCKER
    where: /calc/ export PDF · AC-4
    fix: "Restore /calc/export.pdf on live (uPress: ensure .pdf requests reach Slim index.php, or rename route to non-.pdf path e.g. /calc/export/print). Verify 200 HTML print view opens from dash ⬇ PDF button; re-smoke after deploy."
  - id: F-190-UIALIGN-V02
    severity: MAJOR
    where: /crop-book/{slug}/ simple depth · AC-3 / AC-6
    fix: "Map stored enum values to Hebrew labels before render (e.g. direct_seed→זריעה ישירה, half_hardy→חצי-עמיד). Remove family:variety debug-style strings from visible cards. Hide field_name keys from finfo/request-info visible text (keep in data-attribute or admin-only)."
  - id: F-190-UIALIGN-V03
    severity: MAJOR
    where: /calc/ context strip · AC-4
    fix: "Populate [data-k=crop_slug] <select> from live crop index (server-render or JS fetch) so planners can bind calculations to a real crop; wire selection to book-value chips per catalog. Currently only placeholder option — cannot satisfy 'real crop' AC on dash."
  - id: F-190-UIALIGN-V04
    severity: MINOR
    where: /calc/ disabled modcards · AC-6
    fix: "Replace modcard__needs-field raw schema names (rows_per_bed, days_in_nursery) with Hebrew field labels in disabled-state copy; keep technical names out of farmer-facing UI."
  - id: F-190-UIALIGN-V05
    severity: MINOR
    where: Cloudflare / tokens.css bare URL
    fix: "Purge or 301 stale tokens.css without ?v= (still contains #f5f3ec) so direct asset fetches cannot confuse audits; pages already use ?v=1780397450."
summary: "Deployed @ b72bcca delivers the Class A shell/CSS win: white-green computed ground, site-wide .sh + #sfa-logo, correct surface active colors, 14-card calc layout, CSV export, and SFA_CALC live recompute on input change. L-GATE_V FAILS because AC-4 PDF export 404s on production and AC-3/AC-6 fail on content fidelity — raw DB keys and English enum slugs appear in farmer-facing UI on crop and calc surfaces. Visual fidelity per screen: book-entry PASS (shell/hero/palette); crop-simple MAJOR (shell PASS, content keys FAIL); crop-full/drill not fully exercised in browser but same template → expected same key leak; calc-dash PARTIAL (shell/layout PASS, export PDF FAIL, crop picker empty). team_100 must fix BLOCKER + MAJORs, re-QA live, then L-GATE_V R2. ADR042 closure blocked."
```

## Per-screen visual fidelity (AC-3) — design vs live @ b72bcca

Design reference: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` frames `book-entry`, `crop-lettuce` (simple/full/drill), `calc-page`.

| Screen | Live URL | Shell / palette / type | Content / components | Pair evidence |
|--------|----------|------------------------|----------------------|---------------|
| **book-entry** | `/crop-book/` | **PASS** — `.sh`, leaf-active nav, `#f8fbf8` ground, Carmela SFA, Assistant body | **PASS** — watercolor book hero, mod-cards, filter bar | `evidence_LGATE-V_R1/lgate-v-live-book-entry.png` |
| **crop simple** | `/crop-book/lettuce/` depth=פשוט | **PASS** — crophero watercolor, depth tabs, topic cards | **FAIL** — visible `direct_seed`, `half_hardy`, `family:variety`; finfo links expose `yield_per_bed_m`, `price_documented` | `evidence_LGATE-V_R1/lgate-v-live-crop-simple-lettuce.png` |
| **crop full** | `/crop-book/lettuce/` depth=מלא | **PASS** (same shell) | **FAIL** (same key-leak pattern; tab switch verified in DOM) | — (same page family as simple) |
| **crop drill** | `/crop-book/lettuce/` depth=העמקה | **PASS** (variety table present) | **FAIL** (variety rows OK; finfo/key pattern persists) | — |
| **calc-dash** | `/calc/` | **PASS** — sun-active nav, dark calc-context strip, modcard grid, sticky rail | **PARTIAL** — 14 surfaced + 6 recompute; disabled cards show raw keys; **PDF broken**; crop `<select>` empty | `evidence_LGATE-V_R1/lgate-v-live-calc-dash.png`, `lgate-v-live-calc-mobile-375.png` |

## Disposition

**FAIL — no ADR042 closure.** Route team_100 → build fix (F-190-UIALIGN-V01 hosting/route + V02/V03 content) → team_50 live re-QA → **L-GATE_V R2**.

**Passes without rework:** V1 cream ground (computed), V2 shell site-wide, V6 routes, V7 design-gap acceptances.

---
*team_190 · L-GATE_V Round 1 · IR#1/#5 satisfied (non-Claude validator).*
