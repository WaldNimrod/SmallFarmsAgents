---
title: Re-audit Evidence Manifest — SFA Pre-Launch QA (2026-06-04)
version: "1.0"
date: 2026-06-04
auditor: team_50 (Claude Haiku)
target: https://sfa.nimrod.bio (claimed deployed SHA 6703313)
---

# Evidence Manifest — Re-Audit 2026-06-04

## Overview

Re-audit of https://sfa.nimrod.bio following DEPLOY_REPORT_v1.0.0 claim of WI-1..WI-7 deployment. This manifest documents all checks performed and their results.

## 1. CDP Browser QA (qa_probe.mjs)

### Run details
- **Tool:** `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs` (Node 18+ / Chrome DevTools Protocol)
- **Command:** `node qa_probe.mjs --base https://sfa.nimrod.bio --paths "/crop-book/,/crop-book/lettuce/,/crop-book/table,/market/" --absent "WIP,TBD" --shots`
- **Timestamp:** 2026-06-04 ~21:13 UTC
- **Output:** JSON + 8 screenshots

### Results summary
| Page | Viewport | HTTP | scrollWidth | clientWidth | overflow | screenshot | result |
|------|----------|------|---|---|---|---|---|
| `/crop-book/` | mobile (375) | 200 | 375 | 375 | ❌ NO | `_crop_book__mobile.png` | **PASS** |
| `/crop-book/` | desktop (1440) | 200 | 1440 | 1440 | ❌ NO | `_crop_book__desktop.png` | **PASS** |
| `/crop-book/lettuce/` | mobile (375) | 200 | 375 | 375 | ❌ NO | `_crop_book_lettuce__mobile.png` | **PASS** |
| `/crop-book/lettuce/` | desktop (1440) | 200 | 1440 | 1440 | ❌ NO | `_crop_book_lettuce__desktop.png` | **PASS** |
| `/crop-book/table` | mobile (375) | 200 | **517** | 375 | ✅ **YES** | `_crop_book_table_mobile.png` | **FAIL** |
| `/crop-book/table` | desktop (1440) | 200 | 1440 | 1440 | ❌ NO | `_crop_book_table_desktop.png` | **PASS** |
| `/market/` | mobile (375) | 200 | 375 | 375 | ❌ NO | `_market__mobile.png` | **PASS** |
| `/market/` | desktop (1440) | 200 | 1440 | 1440 | ❌ NO | `_market__desktop.png` | **PASS** |

**Key finding:** 1 FAIL (overflow) out of 8 probes → **F-PRE-004 MAJOR unresolved**.

### Screenshots archived
All screenshots saved to: `docs/qa/cdp/screenshots/`
- `_crop_book__mobile.png` — entry cards compact (accidental rendering)
- `_crop_book__desktop.png` — crop grid below entry cards
- `_crop_book_lettuce__mobile.png` — crop detail, no overflow
- `_crop_book_lettuce__desktop.png` — crop detail desktop
- `_crop_book_table_mobile.png` — **TABLE OVERFLOWS** (scrollWidth 517 > 375)
- `_crop_book_table_desktop.png` — table OK at 1440px
- `_market__mobile.png` — mobile market list
- `_market__desktop.png` — market list desktop

## 2. CSS content verification (curl + grep)

### Query: WI-5 entry-path grid rule

**Expected:** `.cb-paths { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }`

**Source (repo):**
```bash
$ grep -r "cb-paths.*grid" /Users/nimrod/Documents/SmallFarmsAgents/sfa_delivery/
# OUTPUT:
/sfa_delivery/public_assets/css/crop-book-v1.css:.cb-paths { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
/sfa_delivery/public_assets/css/crop-book-v1.css:@media (max-width: 600px) { .cb-paths { grid-template-columns: 1fr 1fr; } }
```
✅ **Source HAS the rule.**

**Live (served):**
```bash
$ curl -s "https://sfa.nimrod.bio/public_assets/css/crop-book-v1.css" | grep "cb-paths"
# OUTPUT: (no output — grep found nothing)
```

Also checked in `hub.css`:
```bash
$ curl -s "https://sfa.nimrod.bio/public_assets/css/hub.css" | grep -A 2 "\.cb-paths"
# OUTPUT:
.cb-paths { gap: 6px; }
```
❌ **Served CSS does NOT have the grid rule** (only has `gap: 6px` from an older version).

**Verdict:** **F-PRE-001 NOT DEPLOYED** — source ≠ served.

---

### Query: WI-6 logo rule

**Expected:** `.sh__mark svg { width: 100%; height: 100%; display: block; }`

**Live (served):**
```bash
$ curl -s "https://sfa.nimrod.bio/public_assets/css/classb.css" | grep -B 2 -A 5 "\.sh__mark"
# OUTPUT: (no output)
```
❌ **Served CSS does NOT have `.sh__mark` selector at all.**

**Verdict:** **F-PRE-002 / WI-6 NOT DEPLOYED**.

---

### Query: WI-7 mobile overflow guards

**Expected:** `.dt-table-wrap { overflow-x: auto }` + `.cb-crop-detail` rules + `.phist-wrap` rules

**Live (served):**
```bash
$ curl -s "https://sfa.nimrod.bio/public_assets/css/crop-book-deep.css" | grep -i "overflow-x\|dt-table-wrap\|cb-crop-detail\|phist-wrap"
# OUTPUT: (only unrelated flex overflow-x, no guard classes)
```
❌ **Served CSS does NOT have `.dt-table-wrap` overflow-x guard.**

**Verdict:** **F-PRE-004 / WI-7 NOT DEPLOYED**.

---

## 3. HTTP headers and cache analysis

### File timestamp check
```bash
$ curl -s -I "https://sfa.nimrod.bio/public_assets/css/crop-book-v1.css" | grep "^date"
# OUTPUT: date: Wed, 03 Jun 2026 21:14:20 GMT
```
⚠️ **File date: 2026-06-03 21:14 UTC** (BEFORE deploy report date 2026-06-04).

### ETag check
```bash
$ curl -s -I "https://sfa.nimrod.bio/public_assets/css/crop-book-v1.css" | grep "etag"
# OUTPUT: etag: W/"6a1de813-c85b"
```

The ETag hash suggests the file is **old** (pre-deploy). The deploy report's claim of cache-bust version change (`?v=1780515224` → `?v=1780520599`) does not match the actual file modification date.

---

## 4. DOM class verification

### Entry-path card HTML classes
```bash
$ curl -s "https://sfa.nimrod.bio/crop-book/" | grep -A 50 'cb-paths' | head -60
# OUTPUT: 
<div class="cb-paths">
  <a class="mod-card mod-card--sun mod-card--open" href="/crop-book/questions" ...>
  <a class="mod-card mod-card--leaf mod-card--open" href="/crop-book/family" ...>
  <a class="mod-card mod-card--soil mod-card--open" href="/crop-book/table" ...>
  <a class="mod-card mod-card--tomato mod-card--open" href="/crop-book/search" ...>
</div>
```
✅ **HTML structure is correct** (4 entry-path cards, correct links).

### Table wrapper class
```bash
$ curl -s "https://sfa.nimrod.bio/crop-book/table" | grep -o 'class="[^"]*table[^"]*"' | sort | uniq
# OUTPUT:
class="dt-table-wrap"
```
✅ **HTML class `dt-table-wrap` is present in the page**, but the **corresponding CSS rule is missing**.

---

## 5. Baseline route smoke checks

All tested routes returned **HTTP 200** with no errors:
- `/` — 200 ✅
- `/crop-book/` — 200 ✅
- `/crop-book/lettuce/` — 200 ✅
- `/crop-book/table` — 200 ✅
- `/market/` — 200 ✅
- `/calc/` — 200 ✅
- `/community` — 200 ✅
- `/about` — 200 ✅

No new regressions; site is functionally stable.

---

## 6. Summary of failures

| Check | Expected | Actual | Severity |
|-------|----------|--------|----------|
| `.cb-paths { display: grid...` in live CSS | Present | **Absent** | **BLOCKER (F-PRE-001)** |
| `.sh__mark svg { width...` in live CSS | Present | **Absent** | **BLOCKER (F-PRE-002 / WI-6)** |
| `.dt-table-wrap { overflow-x: auto }` in live CSS | Present | **Absent** | **BLOCKER (F-PRE-004 / WI-7)** |
| `/crop-book/table` scrollWidth @375px | ≤ 375 | **517** | **MAJOR (F-PRE-004)** |

**Conclusion:** Deploy failed or was incomplete. CSS files on uPress do not match the source in `/sfa_delivery/`.

---

## 7. Hypothesis

The deploy script (`ftp_deploy_sfa_ui.sh`) may have:
1. **Not transferred the CSS files** — FTPS mirror succeeded per logs, but the target files on uPress were not updated.
2. **Transferred to the wrong path** — files ended up outside the web-served directory.
3. **Cloudflare CDN** — serving stale cache despite version-string cache-bust attempt.
4. **uPress build step failed** — if uPress runs `composer install --no-dev`, build artifacts may not be generated.

---

## Next steps (team_99)

1. Verify FTPS logs on waldhomeserver — confirm 3 CSS files were transferred.
2. SSH to uPress and check `/public_assets/css/crop-book-v1.css` for the grid rule.
3. Clear Cloudflare cache if needed.
4. Re-run deploy with post-deploy CSS verification.
5. Notify team_50 when fixed.

---

**Evidence collection completed: 2026-06-04 ~21:20 UTC**
