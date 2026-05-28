# BUILD_REPORT — SFA-S003-P002-WP-UI — L-GATE_B

## 1) Build Summary
**BUILD_PARTIAL** — Core implementation for LOD400 v1.0.2 is complete and all local functional checks passed (phpunit + 14 HTML routes + key APIs + HMAC regression). The package is not yet dispatch-ready for L-GATE_V because required visual-diff artifacts were not produced and Lighthouse accessibility thresholds are below AC-31 target.

## 2) Parameters
- Team / role: team_10 / sfa_build
- Engine: Codex 5.3 (builder execution)
- Branch: `claude/sfa-ui-build` (from `origin/claude/gallant-elbakyan-727a60` @ `2aae85a`)
- Build phases executed: B.0..B.8b (functional implementation + local evidence)
- Runtime used for verification: local PHP 8.5.6 + sqlite mirror fixture
- Validation runs:
  - `composer test` => 31 tests, 60 assertions, exit 0
  - `validate_aos.sh .` => 29 PASS / 17 SKIP / 0 FAIL

## 3) AC Results Table (38 AC)

| AC | Status | Evidence |
|---|---|---|
| AC-01 | PASS | 7 CSS files copied from team_35 handoff into `sfa_delivery/public_assets/css/` |
| AC-02 | PASS | `_layout.php` now links: `tokens.css` → `gj.css` → `hub.css` → `community.css` → `crop-book-deep.css` → `desktop.css` → `desktop-extras.css` |
| AC-03 | PASS | `_layout.php` includes `fonts.googleapis.com` + `fonts.gstatic.com` preconnect and combined fonts stylesheet |
| AC-04 | PASS | `_layout.php` renders `<html lang="he" dir="rtl">` |
| AC-05 | PARTIAL | `.gj-shell` rendered in local route smoke; no viewport-specific screenshot proof attached |
| AC-06 | PARTIAL | `.dt-shell` + `<details>` sidebar implemented; no viewport-specific screenshot proof attached |
| AC-07 | PASS | `/` returns 200 in local smoke (`ac_smoke_20260527.txt`) |
| AC-08 | PASS | `/about/` returns 200 in local smoke |
| AC-09 | PASS | `/search/?q=` route implemented and returns 200 |
| AC-10 | PASS | `/calc/` returns 200 with beta messaging + WhatsApp CTA |
| AC-11 | PASS | `/crop-book/` returns 200 with 4 entry links |
| AC-12 | PASS | `/crop-book/questions/` returns 200 |
| AC-13 | PASS | `/crop-book/family/` returns 200 and DB-backed family grouping |
| AC-14 | PASS | `/crop-book/table/` returns 200 |
| AC-15 | PASS | `/crop-book/search/?q=...` returns 200 |
| AC-16 | PASS | `/crop-book/anise-hyssop/` returns 200 |
| AC-17 | PASS | `/crop-book/anise-hyssop/variety/blue-fortune/` returns 200 |
| AC-18 | PASS | `/market/` returns 200 and renders disclaimer macro |
| AC-19 | PASS | `/market/onion-dry/` returns 200 |
| AC-20 | PASS | `/community/` returns 200; static page only (no form, no writes) |
| AC-21 | PASS | `api_health` -> status ok (`ac_smoke_20260527.txt`) |
| AC-22 | PASS | `api_modules 8` (`ac_smoke_20260527.txt`) |
| AC-23 | PASS | `api_search True True` (`ac_smoke_20260527.txt`) |
| AC-24 | PASS | Existing `/api/v1/crops` route preserved; covered by phpunit route suite |
| AC-25 | PASS | Existing `/api/v1/crops/{slug}` preserved; covered in local route/API tests |
| AC-26 | PASS | Existing `/api/v1/products` preserved; covered in local route/API tests |
| AC-27 | PASS | Existing `/api/v1/products/{slug}` preserved; sqlite compatibility fix added |
| AC-28 | PASS | `api_history 1` for `/api/v1/market/onion-dry/history?days=28` |
| AC-29 | PASS | `ingest_valid 200` with computed HMAC signature |
| AC-30 | PASS | `ingest_bad 401` for bad HMAC |
| AC-31 | FAIL | Lighthouse perf/LCP pass, but Accessibility scores are 90/91/92 (<95 target) |
| AC-32 | NOT RUN | Console error scan over all 14 routes not executed with browser automation |
| AC-33 | NOT RUN | WCAG contrast ratios not measured yet |
| AC-34 | PARTIAL | `sfa.js` details-state persistence implemented; not browser-verified with reload evidence |
| AC-35 | PARTIAL | Hebrew content rendered locally; full 14-route manual RTL inspection not recorded |
| AC-36 | NOT RUN | Live `https://sfa.nimrod.bio/api/v1/health` post-deploy check not run (no deploy in this build run) |
| AC-37 | NOT RUN | 24h waldhomeserver cron tail not run in this build run |
| AC-38 | NOT RUN | Live legacy-site 404 verification not run in this build run |

## 4) Findings
1. **F-BUILD-01 (MAJOR)** — AC-31 failed on Accessibility threshold (required >=95; measured 90/91/92).
2. **F-BUILD-02 (MAJOR)** — Visual-diff artifact set (28 screenshots + diff notes) missing; AC-05/06 and visual AC evidence remain partial.
3. **F-BUILD-03 (MAJOR)** — Live-regression AC-36/37/38 not executed because this run did not deploy to sfa.nimrod.bio.

## 5) validate_aos.sh
- Command: `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
- Result: **29 PASS / 17 SKIP / 0 FAIL**

## 6) Artifacts Produced
- Smoke evidence: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/ac_smoke_20260527.txt`
- Lighthouse JSON:
  - `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse/home_mobile_20260527.json`
  - `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse/crop_book_table_mobile_20260527.json`
  - `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse/market_mobile_20260527.json`
- Visual directory placeholder: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/visual_diff/`

## 7) Next Step
Team 100 should route a focused remediation loop for AC-31/32/33 and live AC-36/37/38 completion, then re-run L-GATE_B closure checks before L-GATE_V dispatch.
