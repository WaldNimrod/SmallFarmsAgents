---
id: QA_REPORT_SFA-S003-P002-WP-UI-patch01_v1.0.0
from: team_50 (QA & Functional Acceptance — Claude Haiku)
to: team_100 (Chief System Architect)
date: 2026-05-28
type: QA_REPORT
gate: QA (pre-L-GATE_V)
wp: SFA-S003-P002-WP-UI-patch01
engine: Claude Haiku (QA engine, team_50)
branch: claude/sfa-ui-patch01
---

# QA_REPORT — SFA-S003-P002-WP-UI-patch01

## Verdict

**QA_PASS.** All 19 acceptance criteria independently re-verified and pass. Render harness confirms exactly 3 `<article class="feed-item">` items in desktop shell; hero_url conditional logic verified present/absent as specified. No structural defects; governance validation clean (0 FAIL); composer test suite passes 48/48 tests with 140 assertions.

---

## 19-AC Verification Table

| AC | Item | Check | QA Result | Evidence |
|----|------|-------|-----------|----------|
| AC-01 | B | `php -l app/Lib/CommunityFeed.php` | **PASS** | No syntax errors detected |
| AC-02 | B | `recent(3)` returns ≤3 rows with all 7 keys | **PASS** | Verified: 3 rows returned, all keys present (kind, author_he, region_he, date_he, text_he, tag_he, upvotes) |
| AC-03 | B | Invalid/missing JSON → fallback ≥1 curated row | **PASS** | Fallback returns ≥1 item; all 7 keys present in fallback data |
| AC-04 | B | Render desktop.php → `.dt-side__feed` + exactly 3 `.feed-item` articles | **PASS** | Render harness: `.dt-side__feed` present, 3 `<article class="feed-item">` counted (not BEM substrings) |
| AC-05 | B | `community_feed.json` valid JSON, all items have 7 keys | **PASS** | php json_decode: Valid JSON, 3 items, all keys present |
| AC-06 | B | No POST route / no DB write / no `community_contributions` | **PASS** | git diff: no "POST\|INSERT\|UPDATE\|DELETE\|community_contributions" in committed code |
| AC-07 | C | `bash -n scripts/ftp_deploy_sfa_ui.sh` | **PASS** | Bash syntax check: OK (no errors) |
| AC-08 | C | Script runs `composer install --no-dev` before lftp + verifies `vendor/` | **PASS** | Line 39: `composer install --no-dev --optimize-autoloader --working-dir="$SRC"` present; line 45 verifies `vendor/` |
| AC-09 | C | Script uses all 6 env vars (SFA_FTP_HOST/PORT/USER/PASS/ROOT, SFA_DELIVERY_SRC) | **PASS** | grep: all 6 present (lines 23–29); properly interpolated into lftp open command |
| AC-10 | C | Script is executable | **PASS** | `test -x scripts/ftp_deploy_sfa_ui.sh`: PASS |
| AC-11 | C | `UI_DEPLOY_RUNBOOK.md` documents Option B + smoke + rollback | **PASS** | §1 "Option B", §4 "Post-deploy smoke", §5 "Rollback" sections all present with detailed steps |
| AC-12 | D | `php -l templates/macros/module_card.php` | **PASS** | No syntax errors detected |
| AC-13 | D | `hero_url` set → `<img class="mod-card__hero">` with that src emitted | **PASS** | Render harness with `hero_url='/images/hero.webp'`: img.mod-card__hero present, src matches |
| AC-14 | D | `hero_url` unset → no `.mod-card__hero` (icon-only fallback) | **PASS** | Render harness without hero_url: no img.mod-card__hero present |
| AC-15 | D | `hub.css` has `.mod-card__hero` cover rule + `:has()` icon-revert intact | **PASS** | Line 119: `.mod-card__hero`, line 124: `object-fit: cover`; lines 147, 157, 165–167: `:has(img, picture, .mod-card__hero)` present in icon-revert rules |
| AC-16 | A | og-default prompt artifact (3 variants) + routing MSG exist | **PASS** | Files present: `MEDIA_PROMPT_og-default_v1.0.0.md` + `MSG-team100-to-team_00-MEDIA-og-default-PROMPT-2026-05-28.md` |
| AC-17 | D | module-heroes prompt artifact (8 slug-exact) + routing MSG exist | **PASS** | Files present: `MEDIA_PROMPT_module_heroes_v1.0.0.md` + `MSG-team100-to-team_00-MEDIA-module-heroes-PROMPT-2026-05-28.md` |
| AC-18 | all | `validate_aos.sh .` → 0 FAIL | **PASS** | Result: 29 PASS / 19 SKIP / 0 FAIL; L-GATE_BUILD EXIT CRITERION: SATISFIED |
| AC-19 | all | `composer test` → 0 new failures vs baseline | **PASS** | 48 tests / 140 assertions / 0 failures; +17 new tests from CommunityFeedTest (13 tests) + ModuleCardHeroTest (4 tests) |

---

## Independent QA Findings

### Static & Syntax
- **PHP lint:** All three modified/new `.php` files clean (CommunityFeed.php, desktop.php, module_card.php).
- **Bash lint:** `ftp_deploy_sfa_ui.sh` syntax valid.
- **JSON:** `community_feed.json` parses cleanly; 3 seed items, all 7 required keys present.

### Render Harness (No DB)
- **Desktop shell:** Renders `.dt-side__feed` wrapper with exactly **3 `<article class="feed-item">` elements** (true article count, not BEM substring matches; builder's report of 30 was correct: 3 articles × ~10 BEM variants each = 30 total substrings, but the AC-04 requirement is 3 articles, verified).
- **Module card hero slot:** Conditional `<img class="mod-card__hero">` correctly emitted when `hero_url` is set; correctly absent when unset.

### Fallback Logic (AC-03)
- Verified via reflection and runtime test: CommunityFeed falls back to curated data when JSON is missing/invalid. Fallback returns ≥1 item with all required keys.

### Scope Integrity (AC-06)
- **No POST routes, no DB writes, no `community_contributions` table introduced.**
- `git diff` confirms: only 10 files changed (7 code + 2 test + 1 BUILD_REPORT), no `vendor/` staged, no roadmap edits.
- Parallel-session working-tree changes (jmf_book/*, .env.example, CHANGELOG.md, external_sources/*) are outside the commit; confirm with `git show --stat` (clean).

### Deferred Items Honesty (AC-16/AC-17)
- **og-default.webp:** Absent (correctly deferred on team_00 media delivery).
- **heroes/*.webp:** Directory absent (correctly deferred).
- **modules.php hero_url wiring:** Not added (correctly deferred; only the template macro accepts the optional `hero_url` parameter).

### Governance (AC-18)
- `validate_aos.sh` returns **0 FAIL** (29 PASS / 19 SKIP).
- Check 32 (_aos/ tree committed) **PASS** — no propagation drift.
- Check 33 (MSG naming advisory): 16 pre-existing advisories (non-blocking, unrelated to this patch).

### Unit Tests (AC-19)
- **Baseline:** 31 tests, 0 failures.
- **Final:** 48 tests, 0 failures.
- **Added:** 17 new tests (+80 assertions) in CommunityFeedTest.php (13 tests) and ModuleCardHeroTest.php (4 tests).
- **Test coverage:** All mandate scenarios covered (recent/limit/fallback/normalize for CommunityFeed; hero_url present/absent for module_card).
- **PHP deprecation note:** 1 pre-existing PHPUnit framework deprecation (unchanged); builder correctly removed reflection `setAccessible()` calls (deprecated in PHP 8.5).

---

## Commit Integrity

- **Branch:** `claude/sfa-ui-patch01` (commit 7551074, authored by team_10 Sonnet, 2026-05-28 15:37:33 +0300)
- **Message quality:** Clear, complete; references build gate (L-GATE_B), both test files, and all 4 items (B/C/D + A prompt artifacts).
- **File count:** 10 changed (7 code + 2 test + 1 BUILD_REPORT) — matches spec exactly.

---

## No Defects

QA found no structural defects, syntax errors, logic failures, or scope violations. All 19 ACs pass independently. The build is functionally correct and reproducible.

---

## Next Step

**Ready for team_190 L-GATE_V** (constitutional validation, non-Claude engine per IR#1). Route to team_190 with this QA_REPORT; no rework required.
