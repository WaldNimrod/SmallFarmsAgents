---
document_type: PRELAUNCH_QA_REPORT
version: "1.0.0"
from: team_50 (QA & Functional Acceptance)
to: team_100 (Chief System Architect)
cc: team_00, team_99, team_190
date: 2026-06-03
mandate: _COMMUNICATION/TEAM_50/SFA-PRELAUNCH-QA/QA_MANDATE_PRELAUNCH_VISUAL_E2E_2026-06-03_v1.0.0.md
target: https://sfa.nimrod.bio
engine: Cursor Composer (team_50)
branch_cross_check: 7fbcf89 (read-only git show; not deployed live)
---

# Pre-Launch Visual + E2E QA Report — SFA Delivery Tier

## 1. Verdict

**NO-GO** — Live `https://sfa.nimrod.bio` is **not launch-ready**. Mandated patch01 tip **`7fbcf89` (WI-5 compact entry cards + WI-6 app-shell logo)** is **not** present in served CSS; team_00’s render defect (**giant `/crop-book/` entry-path cards**, ~786px tall @1440px) is **reproduced in CDP** and **confirmed visually** on mobile. Functional and Class-B template markers largely pass, but the **primary pre-launch visual blockers** must be fixed and redeployed before market launch. Route remediation to **team_99** (deploy `7fbcf89`) then **team_10** if regressions persist post-deploy.

---

## 2. Environment and preconditions

| Item | Detail |
|------|--------|
| **LIVE** | `https://sfa.nimrod.bio` — PHP 8.5.5, DB ok (`GET /api/v1/health` → `status: ok`) |
| **Deploy report** | [`DEPLOY_REPORT_v1.0.0.md`](../../team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md) records **`08f529d`**, not `7fbcf89` |
| **Live CSS fingerprint** | `crop-book-v1.css`: **no** `.cb-paths { display: grid` / WI-5; live `hub.css` only `.cb-paths { gap: 6px; }`. `classb.css`: **no** `.sh__mark` rules / WI-6 (shell markup uses `.sh__mark` but sizing rules absent from served CSS bundle) |
| **Repo tip `7fbcf89`** | `git show 7fbcf89:...` **contains** WI-5 + WI-6 — **live ≠ branch** |
| **Evidence** | `_COMMUNICATION/TEAM_50/SFA-PRELAUNCH-QA/evidence_2026-06-03/` + [`EVIDENCE_MANIFEST.md`](evidence_2026-06-03/EVIDENCE_MANIFEST.md) |
| **Read-only** | No source/git fixes; report only |

### Class B / template markers (live HTML, 2026-06-03 PM)

| Marker | Route | Live | Notes |
|--------|-------|------|-------|
| `hub-home__inner` | `/` | **PASS** (2) | Class B hub wrapper present |
| `contact.webp` | `/community` | **PASS** (1) | Banner image present |
| `◐` + `.reqinfo` | `/search?q=zzznomatch190` | **PASS** | CTA links `/community` |
| `ptable__th` | `/market/` | **PASS** (4) | Table header class present |
| Footer `aria-current="page"` | `/community` | **PASS** | No self-linking קהילה (CDP + HTML) |

*Morning team_190 L-GATE_V R2 FAIL may reflect pre-deploy state; this audit’s live probes show Class B **template** markers present while **patch01 CSS** (WI-5/6) is still missing.*

---

## 3. Per-surface table

Legend: **Fidelity** = design/layout vs Board-A/B @1440 + mobile375 (CDP + screenshots). **E2E** = interaction matrix §4 (CDP + browser where noted).

| # | Route | Desktop fidelity | Mobile fidelity | E2E | Key findings |
|---|-------|------------------|-----------------|-----|--------------|
| 1 | `/` | PARTIAL | PASS | PASS | Hub structure OK (`hub-home__inner`); modtiles + CTAs work; Field-Log `is-dev` present in HTML |
| 2 | `/crop-book/` | **FAIL** | **FAIL** | PARTIAL | **BLOCKER:** entry cards ~786px tall; path links work; filters in HTML |
| 3 | `/crop-book/{slug}` depths | PASS | PARTIAL | PARTIAL | `lettuce` simple, `tomatoes` full/drill **200**; overflow mobile on simple |
| 4 | `/crop-book/.../variety/...` | PASS | — | PASS | `anise-hyssop/variety/variety-1/` **200** (test `variety-11` **404**) |
| 5 | `/crop-book/family` | PASS | PASS | PASS | **200** |
| 6 | `/crop-book/table` | PASS | **FAIL** | PASS | Mobile horizontal overflow (qa_probe) |
| 7 | `/crop-book/search` + `/search?q=` | PASS | PASS | PASS | Hit + no-match OK |
| 8 | `/crop-book/questions` | PASS | PASS | PASS | **200** |
| 9 | `/crop-book/cover-crops` | PASS | PASS | PASS | **200** |
| 10 | `/calc/` | PASS | PARTIAL | PASS | 14 modcards (6 live + 8 disabled); `crop-book-v1.js` loaded; export links present |
| 11 | `/calc/print` + `/calc/export.csv` | PASS | — | PASS | Print **200**; CSV link in page |
| 12 | `/market/` | PASS | PASS | PASS | **200**; `ptable__th` present |
| 13 | `/market/prd017` | PASS | **FAIL** | PASS | Detail **200**; 90י/שנה disabled; mobile overflow |
| 14 | `/community` | PASS | PASS | PARTIAL | **200**; contribute API tested separately |
| 15 | `/about` | PASS | PASS | PASS | Tier ladder **200** |
| 16 | `/account` | PASS | PASS | PASS | **200**; בקרוב shell |
| 17 | App-shell | PARTIAL | PARTIAL | PASS | Logo box 30×30px; **WI-6 not in live CSS**; nav/footer consistent across routes (CDP `shHash` width component stable) |

---

## 4. Findings (severity-ordered)

| ID | Sev | Route | What | Evidence | Suggested fix |
|----|-----|-------|------|----------|---------------|
| **F-PRE-001** | **BLOCKER** | `/crop-book/` | Entry-path `.cb-paths .mod-card` render **~1404×786px** (giant cards + oversized leaf art) | CDP: `cdp_deep/cdp_deep_result.json` bbox_offenders; browser screenshot `design_pairs/live_crop-book-entry_mobile375_browser.png`; E2E heights `[786,786,786,786]` | **team_99:** deploy `7fbcf89` (WI-5 in `crop-book-v1.css`). Verify live CSS contains `cb-paths { display: grid` |
| **F-PRE-002** | **BLOCKER** | Ops / CSS | Mandate tip **`7fbcf89` not live** — WI-5/WI-6 absent from served `crop-book-v1.css` / `classb.css` | `deploy_fingerprint.json`; `git show 7fbcf89` has fixes; DEPLOY_REPORT still `08f529d` | **team_99:** FTPS redeploy per MSG-HUB-20260603-004; publish DEPLOY_REPORT with `deployed_sha: 7fbcf89` |
| **F-PRE-003** | **MAJOR** | `/crop-book/` | Design-vs-live **book-entry** — Board shows compact 4-card row; live full-width stacked giants | Pair: `design_pairs/board_book-entry_desktop1440.png` vs `qa_probe/screenshots/crop-book-entry_desktop1440.png` | Same as F-PRE-001 |
| **F-PRE-004** | **MAJOR** | `/crop-book/lettuce/`, `/crop-book/table`, `/market/prd017` | Horizontal overflow @375px / 768px | `qa_probe_result.json` (`overflow: true`) | CSS responsive pass after WI-5; retest table + market detail |
| **F-PRE-005** | **MINOR** | `/crop-book/` | `<option value="direct_seed">` / `half_hardy` in filter markup (Hebrew labels shown; values raw in DOM) | HTML probe in report session | Map to Hebrew-only values or `data-*` if policy requires zero raw keys in HTML |
| **F-PRE-006** | **MINOR** | `/calc/`, crop pages | qa_probe `absent` hits `yield_per_bed_m` in page HTML/JS (not user-visible text) | qa_probe failures on calc/crop routes | Tighten probe to `innerText` only or rename internal keys in JS bundle |
| **F-PRE-007** | **MINOR** | Global | Security headers (HSTS, X-Frame-Options, CSP) not observed on `/` | `link_crawl_and_extras.json` | **team_60/99:** edge/server config if required for launch |
| **F-PRE-008** | **INFO** | — | **F-CALC-002 resolved:** `/calc/` includes `crop-book-v1.js` | `link_crawl_and_extras.json` `calc_assets` | — |
| **F-PRE-009** | **INFO** | — | Prior June-1 deploy drift closed for v1 assets; **patch01 final tip still pending** | Compare to `E2E_QA_FULL_REPORT_2026-06-02` | — |

---

## 5. E2E interaction matrix (§4)

| Control / area | Result | Note |
|----------------|--------|------|
| Shell logo → `/` | **PASS** | `shell_logo_href` → `/` |
| Shell logo render size | **PARTIAL** | Bbox 30×30; WI-6 CSS not served — visual OK in MCP header but patch not deployed |
| Desktop nav ספר/מחשבון/מחירון | **PASS** | Present in snapshots; routes valid |
| Mobile bottom nav (4 tabs) | **PASS** | Visible on crop-book/calc snapshots |
| Inline search → `/search` | **PASS** | Searchbox + submit link present |
| Footer על הכלים → `/about` | **PASS** | |
| Footer קהילה on `/community` | **PASS** | `aria-current="page"` on קהילה |
| Hub Field-Log non-clickable | **PASS** | `is-dev` + `יומן השדה`; DIV + `aria-disabled` |
| Hub module tiles (3 live + 1 dev) | **PASS** | modtile links to crop-book, market, calc |
| Hub WhatsApp primary CTA | **PASS** | `wa.me` link count ≥ 1 |
| Hub tagline one line @1440 | **NOT VERIFIED** | Deferred — needs desktop browser line-count |
| Crop-book 4 path cards → routes | **PASS** | Links to questions/family/table/search |
| Crop-book cards compact | **FAIL** | Heights 786px — F-PRE-001 |
| Crop-book filters / toggle | **PARTIAL** | Controls present; not all filter combos exercised |
| Crop depth tabs simple/full/drill | **PARTIAL** | All URLs **200**; tab click animation not fully exercised in MCP |
| Calc crop select + book chips | **PARTIAL** | Tomato selected in MCP; chip population not fully asserted |
| Calc AssumptionField recompute | **NOT VERIFIED** | Requires post-select output read |
| Calc 14 modules | **PASS** | 14 total, 8 disabled, 6 `data-calc` live |
| Calc CSV + print | **PASS** | Links present; print route **200** |
| Market Cards⇄Table | **NOT VERIFIED** | |
| Market freshness pills | **NOT VERIFIED** | |
| Market detail range 7/28 active, 90/year disabled | **PASS** | CDP `market_range_disabled` |
| Search no-match → community | **PASS** | `.reqinfo` href `/community` |
| Community contribute POST | **PASS** | `POST /api/v1/contribute` → `{"ok":true}` (test payload) |
| Community request chips | **NOT VERIFIED** | |

---

## 6. Design-vs-mockup notes

| Surface | Board frame | Live capture | Assessment |
|---------|-------------|--------------|------------|
| book-entry | `board_book-entry_desktop1440.png` | `qa_probe/.../crop-book-entry_desktop1440.png` | **MAJOR divergence** — compact grid vs giant stacked cards |
| hub-home | `board_hub-home_desktop1440.png` | `qa_probe/.../hub_desktop1440.png` | **PARTIAL** — structure aligned; pixel diff not scored |
| calc-page | `board_calc-page_desktop1440.png` | `qa_probe/.../calc_desktop1440.png` | **PARTIAL** — 14-module dashboard present |
| market-list | `board_market-list_desktop1440.png` | `qa_probe/.../market-list_desktop1440.png` | **PARTIAL** — `ptable__th` live |
| community | `board_community_desktop1440.png` | `qa_probe/.../community_desktop1440.png` | **PARTIAL** — contact.webp live |

**Intentional (not defects):** 8 calculator modcards `modcard--disabled` until WP-CB-DATA fields enriched; calc “PDF” is print HTML not binary.

---

## 7. Cross-cutting checks (C-A–C-J) + §7 additions

| ID | Result | Evidence |
|----|--------|----------|
| **C-A** Oversized elements | **FAIL** | Giant `.cb-paths .mod-card` @1440 — `cdp_deep_result.json` |
| **C-B** Overflow / RTL | **PARTIAL** | RTL `dir=rtl` on probes; **overflow** on 3 mobile page/viewport combos in qa_probe |
| **C-C** Assets | **PASS** | No CDP `Network.loadingFailed` errors in deep probe session |
| **C-D** Data leakage | **PASS** visible text | No `direct_seed` in `innerText`; option values only in markup |
| **C-E** Console | **PASS** | Zero error-level console entries per route in CDP deep probe |
| **C-F** Links | **PASS** | Crawl 120 paths from hub roots — `broken: []` in `link_crawl_and_extras.json` |
| **C-G** Shell consistency | **PASS** | `.sh__mark` width 30px consistent; shell HTML length varies by page content as expected |
| **C-H** A11y basics | **PARTIAL** | `aria-disabled` on dev tile; full keyboard audit not run |
| **C-I** Responsiveness | **PARTIAL** | 4 viewports shot; mobile nav OK; overflow failures noted |
| **C-J** Performance | **SKIP** | Lighthouse not run (informative only per mandate) |

### team_50 additions (§7)

| Check | Result |
|-------|--------|
| SEO title/OG on `/`, `/crop-book/`, `/calc/` | **PASS** — titles present; generic site `description` |
| `robots.txt` | **PASS** **200** |
| 404 crop slug | **PASS** — `404` with error shell |
| Security headers | **FAIL/MINOR** — none of HSTS/CSP/X-Frame observed |
| Mixed content | **PASS** — no failures in network probe |
| Contribute API | **PASS** — one test POST ok |

---

## 8. Prioritized punch-list (for team_100 → team_10 / team_99)

1. **[BLOCKER] team_99:** Deploy branch tip **`7fbcf89`** to `sfa.nimrod.bio` (`scripts/ftp_deploy_sfa_ui.sh`); update DEPLOY_REPORT; smoke: live `crop-book-v1.css` contains WI-5 grid rule; live `classb.css` contains WI-6 `.sh__mark svg`.
2. **[BLOCKER] team_10:** If cards still giant after deploy — debug `.cb-paths .mod-card` / `mod-card__art` aspect-ratio cascade (delivery CSS specificity).
3. **[MAJOR] team_10:** Fix mobile horizontal overflow on crop simple, book table, market detail (retest qa_probe @375).
4. **[MINOR] team_10:** Replace raw enum `option value=` tokens in crop-book filters if product policy requires.
5. **[MINOR] team_60/99:** Evaluate security headers at uPress/Cloudflare edge.
6. **team_50:** Re-run this mandate **after** deploy; expect verdict upgrade path **NO-GO → GO-WITH-FIXES → GO**.
7. **team_190:** Constitutional **L-GATE_V** (non-Claude) **after** punch-list closed — this report does not substitute.

---

## 9. qa_probe summary

- **80** probes (20 pages × 4 viewports)
- **58 PASS**, **22 FAIL** (mostly `absent` substring in full HTML + 3 mobile overflow cases)
- Full JSON: `evidence_2026-06-03/qa_probe/qa_probe_result.json`

---

## 10. References

- Mandate: [`QA_MANDATE_PRELAUNCH_VISUAL_E2E_2026-06-03_v1.0.0.md`](QA_MANDATE_PRELAUNCH_VISUAL_E2E_2026-06-03_v1.0.0.md)
- Evidence: [`evidence_2026-06-03/EVIDENCE_MANIFEST.md`](evidence_2026-06-03/EVIDENCE_MANIFEST.md)
- Prior E2E: [`../SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md`](../SFA-S003-P004/E2E_QA_FULL_REPORT_2026-06-02_v1.0.0.md)
- Browser QA canon: `_aos/lean-kit/modules/validation-quality/docs/BROWSER_QA_HARNESS_CANON_v1.0.0.md`

---

**team_50 sign-off:** Pre-launch audit complete. **NO-GO** until WI-5/WI-6 live and entry-card render verified on production.
