---
document_type: PRELAUNCH_REAUDIT_REPORT
version: "1.0.0"
from: team_50 (QA & Functional Acceptance)
to: team_100 (Chief System Architect)
cc: team_00, team_99, team_190
date: 2026-06-04
mandate: _COMMUNICATION/TEAM_100/SFA-S003-P004-WP-PRELAUNCH-QA/REAUDIT_MANDATE_team50_full-system-vs-mockups_2026-06-04_v1.0.0.md
target: https://sfa.nimrod.bio
live_sha: acca9b2
served_asset_version: "1780576560"
prior_report: _COMMUNICATION/TEAM_50/SFA-PRELAUNCH-QA/PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md (NO-GO — deploy lag)
---

# Pre-Launch Re-Audit — Full System vs Board-A/B Mockups — live `acca9b2`

## 1. Verdict

**GO-WITH-FIXES** — The **2026-06-03 NO-GO blockers are cleared** on live `acca9b2` (`?v=1780576560`): compact crop-book entry cards (~133px path cards, 168px grid), WI-5/WI-6 CSS served, 70/70 watercolor crop icons, zero horizontal overflow @375 on all probed surfaces, Hebrew market **category** chips, single crop hero, formatted values (no `.000000` in visible text). **One MAJOR** user-visible localization gap remains on `/market/` (English basket product titles). **No BLOCKER** found for launch if team_00 accepts fixing basket labels in a fast follow (team_10 + redeploy) or explicit waiver. Constitutional **L-GATE_V** (crop-book fidelity) remains valid; this report covers the **whole product** vs **all** Board-A/B surfaces.

**Notify team_100:** dispatch **F-REA-001** (basket `name_he`) to team_10 → team_99 redeploy → team_50 spot-check. Fold MINOR items into **WI-7** / post-launch polish unless Nimrod elevates Q5 eyebrows.

---

## 2. Environment and preconditions

| Item | Detail |
|------|--------|
| **LIVE** | `https://sfa.nimrod.bio` · `GET /api/v1/health` → `ok` |
| **Deploy** | SHA **acca9b2** · served CSS `?v=**1780576560**` on `crop-book-v1`, `classb`, `crop-book-deep` (fingerprint: `served_v_matches: true`) |
| **Method** | `qa_probe.mjs` + `reaudit_deep_probe.mjs` + `e2e_matrix_runner.mjs` + Board frame crops (`board_frame_shots.mjs`) · **production TLS** on deep/e2e (no `--ignore-certificate-errors`) |
| **Cache-bust** | Every live URL includes `?v=1780576560` (mandated build) |
| **Evidence** | `_COMMUNICATION/team_50/SFA-S003-P004-WP-PRELAUNCH-QA/evidence_reaudit_2026-06-04/` + [`EVIDENCE_MANIFEST.md`](evidence_reaudit_2026-06-04/EVIDENCE_MANIFEST.md) |
| **Design pairs** | `evidence_reaudit_2026-06-04/design_pairs/` (30 board frames @ 1440/768/375 + manifest) |
| **Read-only** | No code/deploy changes in this session |

### Deploy fingerprint (high-signal)

| Check | Result |
|-------|--------|
| `cb-paths { display: grid` (WI-5) | **PASS** |
| `minmax(168px` crop grid | **PASS** |
| `.cb-crop-detail { max-width: 1120px` | **PASS** (in `crop-book-v1.css`) |
| `.sh__mark svg` (WI-6) | **PASS** |
| `wc-*.png` refs on `/crop-book/` | **70** |
| English category slugs in market chip **visible text** | **0** (`>סלים<` Hebrew present) |
| Routes 200 | `/crop-book/`, lettuce simple, `/calc/`, `/account` |

---

## 3. Per-surface summary (vs Board-A / Board-B)

Legend: **Fidelity** = layout/type/components/palette vs mockup @1440+768+375. **E2E** = interactions per mandate.

| # | Surface | Board | Desktop | Tablet | Mobile375 | E2E | Notes |
|---|---------|-------|---------|--------|-----------|-----|-------|
| 1 | **Hub `/`** | B | **PASS** | PASS | PASS | PASS | Watercolor module tiles, audience cards, `#f8fbf8`, Field-Log disabled tile — matches Board-B intent. Pair: `design_pairs/board_hub-home_*` ↔ `qa_probe/screenshots/hub_*` |
| 2 | **Crop-book `/crop-book/`** | A | **PASS** | PASS | PASS | PASS | **Prior BLOCKER resolved:** path cards **133×133px** (was ~786px). 168px grid, 70 watercolors, toggle/filters. Pair: `board_book-entry_*` ↔ `crop-book-entry_*` |
| 3 | **Crop page `/crop-book/lettuce/`** | A | **PASS** | PASS | PASS | PASS | Single `<h1>`, centered column, Hebrew values/units, wc hero art. Pair: `board_crop-lettuce_*` ↔ `crop-simple_*` |
| 4 | **Crop full `/crop-book/tomatoes/`** | A | PASS | PASS | PASS | PARTIAL | Depth tabs present; no double-hero / green blob |
| 5 | **Calculator `/calc/`** | A | **PASS** (structural) | PASS | PASS | PASS | 14 `modcard`, 6 live `[data-calc]`, export CSV, spacing/plant-count viz visible, bg `rgb(248,251,248)`. **COSMETIC:** pixel-level type scale vs Board-A not certified from CDP alone — align with team_100 + WI-7. Pair: `board_calc-page_*` ↔ `calc_*` |
| 6 | **Market list `/market/`** | B | **PARTIAL** | PARTIAL | PARTIAL | PASS | Hebrew category chips, ₪ prices, freshness pills, cards/table toggle — **MAJOR:** visible **`basket_large` / `basket_medium` / `basket_small`** on cards (screenshot `market-list_desktop1440.png`) |
| 7 | **Market detail `/market/prd017`** | B | PASS | PASS | PASS | PASS | Graph + 7י/28י; 90י/שנה disabled as designed |
| 8 | **Search `/search?q=…`** | B | PASS | PASS | PASS | PASS | **`q=חסה`:** 3 hits, grouped book+market (`global-search-hit-lettuce_desktop1440.png`). **MINOR:** letter-glyph `ח` not watercolor. Mandate probe `q=עגבניה` returned 0 hits (data/query — not layout defect) |
| 9 | **Community `/community`** | B | PASS | PASS | PASS | PASS | Watercolor hero, contribution form |
| 10 | **About `/about`** | B | PASS | PASS | PASS | PASS | 5-tier ladder. **MINOR:** English tier eyebrows OPEN/BETA/COMING/PAID/CUSTOM (WI-7 Q5) |
| 11 | **Account `/account`** | B | PASS | PASS | PASS | PASS | Landing shell present (בקרוב) |

**Structural CDP (all 12 routes × 3 viewports):** `overflow: false` everywhere — **0** horizontal overflow @375 (subsumes 2026-06-03 F-PRE-004). **Console errors:** none captured on deep probe.

---

## 4. Findings (severity-ordered)

| ID | Sev | Route | What | Evidence | Suggested fix |
|----|-----|-------|------|----------|---------------|
| **F-REA-001** | **MAJOR** | `/market/` | **User-visible English product titles** on basket cards: `basket_large`, `basket_medium`, `basket_small` (not chip slugs — rendered `pcard__name`) | Screenshot `qa_probe/screenshots/market-list_desktop1440.png`; `curl` HTML contains `basket_medium` in body; category chip **סלים** is correctly Hebrew | **team_10:** map basket slugs → Hebrew in `MarketViewController` / product row `name_he` (same pattern as D-3 category map). **team_99:** redeploy → team_50 re-probe market list |
| **F-REA-002** | **MINOR** | `/search?q=חסה` | Crop hits use **letter glyph** (`ח`), not `wc-*.png` watercolor | `global-search-hit-lettuce_desktop1440.png`; CDP `wc:0`, `glyph:3` | **team_10/WI-7:** reuse crop-card art in search result template |
| **F-REA-003** | **MINOR** | `/about` | Tier badge eyebrows **OPEN / BETA / COMING / PAID / CUSTOM** in English | `about_desktop1440.png` | **team_35/WI-7 Q5** — Hebraize per decision B |
| **F-REA-004** | **MINOR** | `/crop-book/` | Filter `<option value="direct_seed">` / `half_hardy` in DOM (Hebrew labels shown) | `qa_probe` forbidden hits; not in `innerText` leak scan | Optional: Hebrew-only values or `data-*` if zero-English-in-HTML policy required |
| **F-REA-005** | **MINOR** | `/calc/`, crop pages | `yield_per_bed_m` in page HTML/JS bundle; qa_probe flags, **not** visible in `innerText` | `qa_probe_result.json`; deep probe `visible_leaks: []` | Tighten qa_probe to `innerText` only, or rename internal JS keys (INFO) |
| **F-REA-006** | **COSMETIC** | `/calc/` | Board-A **pixel/type-scale** parity not fully certified in CDP | `design_pairs/board_calc-page_desktop1440.png` vs `calc_desktop1440.png`; team_100 notes same | External eyes + WI-7; not launch-blocking given structural PASS |
| **F-REA-007** | **INFO** | — | **2026-06-03 blockers closed:** F-PRE-001/002/003/004 | `e2e_matrix`: entry heights `[133,133,133,133]`; fingerprint WI-5/6; overflow 0/36 | — |
| **F-REA-008** | **INFO** | `qa_probe` | 15/36 harness **FAIL** = HTML-only forbidden tokens (`direct_seed`, category slugs in markup) — **not** rendered leaks | `qa_probe_result.json` vs `cdp_deep` `visible_leaks: []` | Update harness absent-list / scan `innerText` only |

---

## 5. E2E interaction matrix

| Control | Result | Evidence |
|---------|--------|----------|
| Shell logo → `/` | **PASS** | `e2e_matrix_cdp.json` `shell_logo_href` |
| Hub Field-Log non-clickable | **PASS** | `hub_field_log_disabled` |
| Crop-book entry card heights &lt;200px | **PASS** | `[133,133,133,133]` |
| Crop page single H1 | **PASS** | `crop_lettuce_single_h1` → 1 |
| Market 90י/שנה disabled | **PASS** | `market_range_disabled` |
| Calc export CSV link | **PASS** | `calc_export_csv` |
| Calc 14 modules / 6 live | **PASS** | `calc_modcards` total 14, live 6 |
| Search no-match → `/community` | **PASS** | `search_nomatch_reqinfo` |

---

## 6. Comparison to 2026-06-03 NO-GO

| Prior ID | Was | Now @ acca9b2 |
|----------|-----|----------------|
| F-PRE-001 | BLOCKER — 786px entry cards | **CLOSED** — 133px cards, grid 168px |
| F-PRE-002 | BLOCKER — WI-5/6 not live | **CLOSED** — fingerprint PASS |
| F-PRE-003 | MAJOR — design vs board entry | **CLOSED** — live matches Board-A density (eyes-on + screenshots) |
| F-PRE-004 | MAJOR — mobile overflow | **CLOSED** — 0 overflow all surfaces |

**New regression class:** market **product** names (baskets), not category chips — was out of scope for FIDELITY D-3 fix.

---

## 7. Prioritized punch-list (for team_100 → team_10)

1. **P0 — F-REA-001:** Hebrew labels for `basket_large` / `basket_medium` / `basket_small` on `/market/` (and detail if linked).
2. **P1 — F-REA-002:** Search crop hits → watercolor `wc-*` art.
3. **P2 — F-REA-003:** About tier eyebrows (WI-7 / Q5).
4. **P3 — F-REA-004/005/006:** DOM token hygiene + calc pixel polish (optional pre-launch).

**Re-verify after P0 deploy:** team_50 spot-check `market-list_*` screenshots + `curl` absent `basket_large` in visible card HTML.

---

## 8. Sign-off

| Role | Action |
|------|--------|
| **team_50** | Re-audit complete — **GO-WITH-FIXES** (1 MAJOR, 0 BLOCKER) |
| **team_100** | Route P0 to team_10; launch call with team_00 after P0 fix or waiver |
| **team_99** | Redeploy when team_10 lands basket `name_he` |
| **team_190** | Informational — L-GATE_V already PASS; no constitutional conflict |

---

*Evidence path:* [`evidence_reaudit_2026-06-04/`](evidence_reaudit_2026-06-04/) · *Design pairs:* [`evidence_reaudit_2026-06-04/design_pairs/`](evidence_reaudit_2026-06-04/design_pairs/)
