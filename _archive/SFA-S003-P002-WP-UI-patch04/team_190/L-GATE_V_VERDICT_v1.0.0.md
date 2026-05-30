---
id: L-GATE_V_VERDICT_SFA-S003-P002-WP-UI-patch04_v1.0.0
from: team_190
to: team_100
cc:
  - team_00
  - team_10
  - team_50
date: 2026-05-30
type: validation_verdict
wp: SFA-S003-P002-WP-UI-patch04
gate: L-GATE_V
build_commit: c7dc779
validated_head: 67b515f7a69ff4ee84b9ee27a9c763a4ca827a3c
verdict: FAIL
validator_engine: Codex / GPT-5 (non-Claude)
builder_engine: Claude Sonnet
qa_engine: Claude Haiku
integrator_engine: Claude Opus
---

# L-GATE_V VERDICT — SFA-S003-P002-WP-UI-patch04 — v1.0.0

## 0. Verdict Box

**Verdict:** FAIL

**Reason:** AC-U4-06 fails on the live crop detail route. `/crop-book/arugula` has the persistent top nav, but the crop-book top-nav active state and the crop-book secondary nav row are absent. This is a live functional regression against the mandate requirement for persistent global navigation and crop-book sub-navigation.

**Engine check:** PASS — validator is Codex / GPT-5, non-Claude. Builder, QA, and integrator were Claude-family engines, so IR#1 cross-engine separation is satisfied.

**Merge / LOD500 recommendation:** DO NOT close ADR042 or set LOD500_LOCKED until AC-U4-06 is repaired and revalidated.

## 1. Blocking Finding

### [BLOCKER] AC-U4-06 fails on live crop detail pages

**Evidence:**

- Live `/crop-book/arugula` fetched from `https://sfa.nimrod.bio/crop-book/arugula` returned 200 and includes `id="sfa-topnav"`.
- The same live HTML does **not** include `sfa-nav__sub`.
- The same live HTML has no `sfa-nav__link is-active` marker for the crop-book top-nav item.
- Live crop-book index/subpages (`/crop-book/`, `/crop-book/table`, `/crop-book/family`, `/crop-book/questions`, `/crop-book/cover-crops`) do include the secondary crop-book nav.

**Root cause visible in local code:**

- `sfa_delivery/templates/pages/book_crop.php:32` sets `$active = 'crop-book'`.
- `sfa_delivery/templates/macros/crop_calendar.php:57` reuses `$active` as a local boolean for active months.
- Because PHP includes share scope, the calendar macro overwrites the page-level `$active` before `book_crop.php:291` calls `_layout.php`.
- `sfa_delivery/templates/partials/nav.php:49` renders the crop-book secondary nav only when `$active === 'crop-book'`.

**Impact:** crop detail pages are missing the mandated global crop-book sub-navigation and active top-nav state. This blocks L-GATE_V.

## 2. Acceptance Criteria Disposition

| AC | Result | Evidence |
|---|---:|---|
| AC-U4-01 | **PASS** | `python3 -m organic_market_agent.publisher.sfa_ingest_push --table crops --limit 70 --dry-run` succeeded: 70 crop rows, 2 dry-run batches. Direct `_fetch_crops` inspection: all 70 rows have `identity`; arugula includes `identity`, `calendar`, `agronomy`, `harvest`, `storage`, `companions`, and `notes` keys. |
| AC-U4-02 | **DEFERRED / NON-BLOCKING PER MANDATE** | `cover_crops` dry-run builds 35 rows, but live `/crop-book/cover-crops` renders the known clean empty-state. The mandate explicitly lists this as deferred/P2 and not a blocking defect. |
| AC-U4-03 | **PASS** | Live arugula section order: `identity` → `calendar` → `agronomy` → `harvest` → `storage` → `companions` → `notes` → `varieties`; `varieties` is last. |
| AC-U4-04 | **PASS** | Live arugula renders species-level calendar, agronomy, harvest, storage, and companion data. |
| AC-U4-05 | **PASS** | Ingest code filters notes with `WHERE is_internal_farm_use_only = FALSE`; direct arugula payload inspection shows `notes: []`; live arugula renders the public-notes empty-state and no internal-note tokens. |
| AC-U4-06 | **FAIL** | Blocking finding above: live detail route lacks crop-book active nav state and secondary nav. |
| AC-U4-07 | **PASS** | Live crawl seeds: `/`, `/crop-book/`, `/crop-book/arugula`, `/crop-book/table`, `/crop-book/family`, `/crop-book/questions`, `/crop-book/cover-crops`, `/market/` all returned 200. 102 internal links discovered from those pages; 0 internal 404s. |
| AC-U4-08 | **PASS** | Live detail includes `.cb-crop-detail`; local CSS defines full-width central panel in `hub.css`. |
| AC-U4-09 | **PASS** | Landing uses `.gj-cropgrid`; planned module cards render disabled/non-navigable; live home has disabled cards and no `/clients/` planned-module link. |
| AC-U4-10 | **PASS** | PHP lint clean across all non-vendor `sfa_delivery/*.php`; `composer test`: 63/63 tests, 202 assertions, 0 failures, 1 PHPUnit deprecation. |
| AC-U4-11 | **PASS** | `validate_aos.sh .`: 29 PASS / 19 SKIP / 0 FAIL. Patch04 diff has no `vendor/`, no migration/db-version/reconciler change; `www.nimrod.bio` appears only in the new LOD400 spec text, not in runtime patch code. MySQL mirror remains payload-based. |
| AC-U4-12 | **PASS** | Live uPress smoke: mandated routes return 200 via `https://sfa.nimrod.bio` / Cloudflare. |

## 3. Command Evidence

- `git merge-base --is-ancestor c7dc779 HEAD` → `0`
- `find sfa_delivery -name '*.php' -not -path '*/vendor/*' -print0 | xargs -0 -n1 php -l` → all clean
- `composer test` in `sfa_delivery` → `Tests: 63, Assertions: 202, PHPUnit Deprecations: 1`
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → `RESULT: 29 PASS / 19 SKIP / 0 FAIL`
- Live crawl → seed routes 200; `INTERNAL_LINKS_CHECKED 102`; `INTERNAL_404S 0`
- Live arugula nav probe → `topnav True`, `subnav False`, `active False`, `www False`

## 4. Final Decision

**FAIL.**

The patch is otherwise materially healthy: rich crop sections render, broken-link crawl is clean, tests pass, AOS passes, and live deployment is on `sfa.nimrod.bio`. However, AC-U4-06 is explicit and user-facing. The crop detail page loses the crop-book navigation state because a macro clobbers `$active`.

Required remediation: rename the month-level `$active` variable in `crop_calendar.php` (for example `$month_active`) or otherwise isolate macro scope, then redeploy and re-run L-GATE_V focused on AC-U4-06 plus the existing smoke crawl.
