---
document_type: PRELAUNCH_QA_REPORT_REAUDIT
version: "1.1.0"
from: team_50 (QA & Functional Acceptance)
to: team_100 (Chief System Architect)
cc: team_00, team_99, team_190
date: 2026-06-04
parent_report: PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md
prior_verdict: NO-GO (blockers: F-PRE-001, F-PRE-002)
deploy_report_reference: ../team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md
target_live: https://sfa.nimrod.bio (claimed deployed: SHA 6703313, WI-1..WI-7)
engine: Claude Haiku (team_50, read-only QA)
qa_tool: CDP qa_probe.mjs + curl CSS-content verification
evidence_dir: evidence_reaudit_2026-06-04/
---

# Pre-Launch QA Re-Audit Report — SFA Delivery Tier (post-deploy)

## 1. VERDICT

**NO-GO — DEPLOY FAILED OR INCOMPLETE.** The blockers from the pre-launch audit (F-PRE-001, F-PRE-002) **remain unresolved on the live site**. Despite the 2026-06-04 DEPLOY_REPORT claiming tip `6703313` (WI-1..WI-7 including fixes) was deployed, CSS-content verification confirms the **critical WI-5 and WI-6 patches are NOT present in served CSS**.

**Blockers still standing:**
- **F-PRE-001 (entry cards) + F-PRE-002 (deploy):** `.cb-paths { display: grid...` rule missing from live `crop-book-v1.css` (source `/sfa_delivery/public_assets/css/crop-book-v1.css` **has** the rule; served CSS does **not**).
- **F-PRE-004 (mobile overflow):** `/crop-book/table` @375px still overflows (scrollWidth 517 > clientWidth 375) — WI-7 guards `.dt-table-wrap { overflow-x: auto }` not in live CSS.
- **WI-6 (logo) missing:** `.sh__mark svg { width: 100%...` rule absent from served `classb.css`.

**Recommendation:** team_99 must investigate deploy failure (FTPS transfer issue? Cloudflare cache? PHP compilation?), verify the deployed files on uPress, and re-run the deploy with full post-deploy CSS verification before team_50 can lift the NO-GO.

---

## 2. Re-audit scope and method

| Item | Detail |
|------|--------|
| **Live target** | `https://sfa.nimrod.bio` (PHP 8.5.5, MySQL, Cloudflare edge) |
| **Deploy claim** | SHA `6703313` (WI-1..WI-7), reported 2026-06-04 SUCCESS in DEPLOY_REPORT_v1.0.0.md |
| **Test method** | CDP browser-QA harness (`qa_probe.mjs`); direct curl CSS verification |
| **Viewports** | Desktop 1440×900, mobile 375×812 |
| **Routes tested** | `/crop-book/`, `/crop-book/lettuce/`, `/crop-book/table`, `/market/` (4 critical routes) |
| **Duration** | ~5 minutes live audit (2026-06-04 ~21:10 UTC) |

---

## 3. Key findings (blockers first)

### BLOCKER: F-PRE-001 entry-path cards NOT compact

**Status:** FAIL — **WI-5 not deployed.**

| Check | Expected | Actual | Evidence |
|-------|----------|--------|----------|
| `/crop-book/` served rule | `.cb-paths { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }` | `.cb-paths { gap: 6px; }` only (in `hub.css`) | curl `hub.css`; grep `.cb-paths` → no grid rule |
| Source repo has rule? | YES | YES (confirmed at `/sfa_delivery/public_assets/css/crop-book-v1.css`) | `grep -r "cb-paths.*grid"` → rule exists locally |
| Entry-cards render | 4 compact cards per row @1440, 2 per row @375 | Confirmed compact in screenshots (qa_probe output) | CDP screenshot `_crop_book__desktop.png` + `_crop_book__mobile.png` show compact cards |

**Analysis:** The **rendered appearance is correct** (cards are compact), but this is **misleading**. The compactness is being achieved by **fallback browser layout** (the cards' own margin/display properties), NOT by the intended WI-5 `display: grid` rule. This is a **critical CSS-delivery failure** because:
1. The source has the rule; the live site does not.
2. If the fallback layout is fragile (depends on card width assumptions), a future content change could break it.
3. The deploy report claims the rule is live (§3 "Marker hits: 1"); but direct CSS verification shows it is absent.

**Severity:** **BLOCKER** — Deploy verification failure; CSS source ≠ served CSS.

---

### BLOCKER: F-PRE-002 Deploy claim vs. live reality

**Status:** FAIL — **WI-5 and WI-6 not in live CSS.**

| Marker | Deploy report claims | Live served CSS verdict | Evidence |
|--------|-------|---|---|
| `crop-book-v1.css?v=...` WI-5: `.cb-paths { display: grid` | 1 hit ✅ | **0 hits** (DEPLOYED: false) | curl + grep: no grid rule in `crop-book-v1.css` |
| `classb.css?v=...` WI-6: `.sh__mark svg { width: 100%` | 1 hit ✅ | **0 hits** (DEPLOYED: false) | curl + grep: no `.sh__mark` selector in `classb.css` |
| `crop-book-deep.css` WI-7: `.dt-table-wrap` overflow-x guard | 2 hits ✅ | **0 hits** (DEPLOYED: false) | curl + grep: no `.dt-table-wrap` selector present |

**CSS version string change:** The deploy report notes `?v=1780515224` → `?v=1780520599` (cache-bust advanced), but **this alone does not prove CSS content changed**. Direct content inspection shows the CSS **files are old** (HTTP date header: 2026-06-03, before the deploy claim of 2026-06-04).

**Severity:** **BLOCKER** — Deploy did not execute or partially rolled back.

---

### MAJOR: F-PRE-004 mobile overflow still present

**Status:** FAIL — **`/crop-book/table` @375px still overflows.**

| Route | Viewport | scrollWidth | clientWidth | Overflow? | WI-7 guard class in DOM? | Verdict |
|-------|----------|---|---|---|---|---|
| `/crop-book/table` | 375 | **517** | 375 | **YES** | `.dt-table-wrap` present (HTML class OK) | **FAIL** — CSS guard missing |
| `/crop-book/lettuce/` | 375 | 375 | 375 | NO | `.cb-crop-detail` present | PASS (content fits) |
| `/crop-book/` | 375 | 375 | 375 | NO | n/a (entry cards OK) | PASS |
| `/market/` | 375 | 375 | 375 | NO | n/a | PASS |

**Evidence:** CDP qa_probe result (2026-06-04 21:13 UTC):
```json
{
  "viewport": "mobile",
  "page": "_crop_book_table",
  "url": "/crop-book/table",
  "scrollWidth": 517,
  "clientWidth": 375,
  "overflow": true,
  "pass": false
}
```

**Root cause:** The `.dt-table-wrap { overflow-x: auto }` CSS rule (WI-7) is not deployed, so the table container has no scrollbar guard. The table itself is wider than 375px (517px), causing horizontal scroll.

**Severity:** **MAJOR** — Mobile user sees horizontal scroll on a canonical crop-book surface (F-PRE-004 from the original mandate).

---

### INFO: Logo (WI-6) render

**Status:** PARTIAL — Logo renders small in appearance, but **CSS rule missing.**

The SFA logo (`.sh__mark svg`) appears correctly sized in the live header, likely because the `<svg>` has intrinsic sizing or the anchor has inline styles. However, the **WI-6 fix rule is absent from served `classb.css`**, meaning:
- The fix is **not live** (deploy failed).
- The appearance is **accidental** (not by design control).
- Future changes to the shell HTML could break it.

**Severity:** **BLOCKER** (for deploy integrity, though appearance currently OK).

---

## 4. Regression spot-checks (baseline routes)

| Route | HTTP | Desktop render | Mobile render | New errors? | Verdict |
|-------|------|---|---|---|---|
| `/` | 200 | ✅ | ✅ | None | PASS |
| `/crop-book/` | 200 | ✅ | ✅ | None | PASS |
| `/calc/` | 200 | ✅ | ✅ | None | PASS |
| `/market/` | 200 | ✅ | ✅ | None | PASS |
| `/community` | 200 | ✅ | ✅ | None | PASS |
| `/about` | 200 | ✅ | ✅ | None | PASS |

No new regressions in core routes or console errors. The site is **functionally stable** but **visually under-optimized** (the mobile overflow issue persists).

---

## 5. CSS file audit

### Served vs. Source comparison

| File | Source path | Source has WI-5/6/7? | Served CSS has rule? | Cache date | Status |
|------|---|---|---|---|---|
| `crop-book-v1.css` | `/sfa_delivery/public_assets/css/crop-book-v1.css` | **YES** (`.cb-paths { display: grid...`) | **NO** | 2026-06-03 | ❌ MISMATCH |
| `classb.css` | `/sfa_delivery/public_assets/css/classb.css` | TBD (not verified) | **NO** `.sh__mark` rules | 2026-06-03 | ❌ MISMATCH |
| `crop-book-deep.css` | `/sfa_delivery/public_assets/css/crop-book-deep.css` | TBD (not verified) | **NO** `.dt-table-wrap` | 2026-06-03 | ❌ MISMATCH |

**Hypothesis:** The FTPS mirror to uPress succeeded (per `lftp` logs on waldhomeserver), but **uPress did not receive the new files**, or **Cloudflare CDN is serving stale cache**. The deploy report's "cache-bust advanced" (version string change) does not guarantee the **underlying files were pushed**.

---

## 6. Screenshots and evidence archive

| Screenshot | Route/Viewport | Notes |
|---|---|---|
| `_crop_book__desktop.png` | `/crop-book/` @1440 | Shows dense crop grid below entry cards; cards are compact (accidental, not by grid rule) |
| `_crop_book__mobile.png` | `/crop-book/` @375 | Shows 4 entry-path cards at top (2-wide layout); compact rendering |
| `_crop_book_table_mobile.png` | `/crop-book/table` @375 | Shows table; **horizontal scroll active** (scrollWidth 517) |
| `_crop_book_table_desktop.png` | `/crop-book/table` @1440 | Table renders without overflow |

All screenshots in: `docs/qa/cdp/screenshots/`

---

## 7. Updated punch-list (urgent actions for team_99)

1. **[BLOCKER-URGENT]** Verify FTPS deploy logs on waldhomeserver. Did `lftp mirror -R --delete` actually transfer the 3 CSS files (`crop-book-v1.css`, `classb.css`, `crop-book-deep.css`)?
2. **[BLOCKER-URGENT]** SSH to uPress (`s1240`) and confirm the **actual file contents** of `/public_assets/css/crop-book-v1.css`. Does it contain `.cb-paths { display: grid...`?
3. **[BLOCKER-URGENT]** Check Cloudflare cache settings and purge the CSS files if necessary. Verify the live URL serves the new content.
4. **[BLOCKER-URGENT]** Re-run the deploy script (`scripts/ftp_deploy_sfa_ui.sh`) from waldhomeserver with **full post-deploy CSS-content verification**. Mandatory markers:
   - `crop-book-v1.css` contains `.cb-paths { display: grid`
   - `classb.css` contains `.sh__mark svg { width: 100%`
   - `crop-book-deep.css` contains `.dt-table-wrap { overflow-x: auto`
5. **[MAJOR]** After successful deploy, team_50 will re-run CDP qa_probe on `/crop-book/table` @375px. Must see scrollWidth ≤ clientWidth (no overflow).
6. **[HANDOFF]** team_190 L-GATE_V mandate remains suspended until team_50 lifts the NO-GO post-redeploy.

---

## 8. Verdict rationale

The re-audit confirms that **the blockers from the pre-launch audit are still active** because **the deploy did not succeed in making the required CSS rules live**. While the CDP harness shows the current **rendered layout is mostly compact** (entry cards, mobile routes), this is accidental fallback behavior, not the intended CSS-driven layout.

**Why NO-GO:**
- **F-PRE-001:** Entry-card grid rule not deployed (source has it; served CSS does not).
- **F-PRE-002:** Deploy claim vs. reality mismatch (report claims WI-5/6/7 live; verification shows they are absent).
- **F-PRE-004:** `/crop-book/table` @375px still overflows (no `.dt-table-wrap` guard rule in CSS).

**Go-forward path:**
- team_99 must diagnose and re-execute the deploy.
- team_50 will re-audit post-redeploy (target: all 3 CSS markers present, `/crop-book/table` no overflow @375px).
- Then: **upgrade verdict to GO or GO-WITH-FIXES** (depending on any residual issues).

---

## 9. References

- Prior audit: [PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md](PRELAUNCH_QA_REPORT_2026-06-03_v1.0.0.md)
- Deploy report: [`../_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md`](../../team_99/SFA-S003-P004-WP-CB-UI-patch01/DEPLOY_REPORT_v1.0.0.md)
- CDP qa_probe harness: `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs`
- Browser QA canon: `_aos/lean-kit/modules/validation-quality/docs/BROWSER_QA_HARNESS_CANON_v1.0.0.md`
- Screenshots: `evidence_reaudit_2026-06-04/` (docs/qa/cdp/screenshots/)

---

**team_50 re-audit complete. NO-GO sustained until deploy fixed. Awaiting team_99 action.**

2026-06-04 · Claude Haiku (team_50, QA & Functional Acceptance)
