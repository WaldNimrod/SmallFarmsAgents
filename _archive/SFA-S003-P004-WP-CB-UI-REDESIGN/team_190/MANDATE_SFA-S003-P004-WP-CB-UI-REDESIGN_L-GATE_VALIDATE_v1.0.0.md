---
id: MANDATE_SFA-S003-P004-WP-CB-UI-REDESIGN_L-GATE_VALIDATE_v1.0.0
from: Team 100 (Chief System Architect · Claude Code)
to: Team 190 (Constitutional Validator)
date: 2026-06-08
type: GATE_MANDATE
gate: L-GATE_VALIDATE
wp: SFA-S003-P004-WP-CB-UI-REDESIGN
project: SFA-S003-P004
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine (IR#1/#5): builder=claude-code → validator MUST be a non-Claude engine (Cursor / Codex / Desktop). Do NOT validate on Claude Code."
mandate_baseline: 8d03f2e826c2c3bbe9ed73fe7419d44f43e1b23f
build_branch: feat/wp-cb-ui-redesign
build_head: f71dfbc
---

# L-GATE_VALIDATE Mandate — SFA-S003-P004-WP-CB-UI-REDESIGN

**Full redesigned public version of SFA (7 surfaces + calc re-skin + internal tool) → production**
**Track:** L2 (spoke-native) | **Profile:** L0 | **Risk:** MEDIUM (full public-surface redesign; touches a LOD500-locked calc engine via re-skin only)

---

## 1. Header

team_100 (builder, Claude Code) has completed the WORKPLAN build (WI-0 → WI-9) on branch
`feat/wp-cb-ui-redesign` (9 commits, baseline `8d03f2e` → HEAD `f71dfbc`). This mandate routes
the **constitutional L-GATE_VALIDATE** to team_190 on a **non-Claude engine** (cross-engine
independence). Build report: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-REDESIGN/COMPLETION_REPORT_build_2026-06-08_v1.0.0.md`.

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_ELIGIBILITY | PASS | 2026-06-08 | team_100 | WP registered READY; FTP allowlist open; calc locked; validate_aos 0 FAIL (`4b1470f`) |
| L-GATE_BUILD | COMPLETE | 2026-06-08 | team_100 (self, build) | WI-0→WI-9: 226 route/macro tests green; qa_probe 16/16 PASS |
| **L-GATE_VALIDATE** | **PENDING** | — | **team_190 (this mandate)** | constitutional, cross-engine |

## 3. Scope

**L-GATE_VALIDATE — constitutional: full governance compliance + implementation fidelity.**
Independently re-verify that the redesigned delivery tier (`sfa_delivery/`) is correct, honest,
RTL/mobile-safe, does NOT regress the locked WP-CB-CALC engine, and preserves the two-tier
write-isolation canon — WITHOUT reading team_100's conclusions before forming your own.

## 4. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | Route/macro suite (independent run) | `cd sfa_delivery && composer install && APP_ENV_FILE=.env.test php vendor/bin/phpunit --no-coverage` → expect **226 passing**, 0 failures. Cite any failure file:line. |
| VC-2 | Browser-QA, no overflow (CDP, NOT curl) | Run app locally on SQLite (see build report §preview / memory `reference_sfa_local_preview_harness`), then `node _aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs --base http://127.0.0.1:<port> --paths "/,/crop-book/,/crop-book/lettuce/,/crop-book/richcrop/,/market/,/calc/,/assumptions/,/cropdata-entry/"` → expect **16/16 PASS** (mobile 375 + desktop), zero horizontal overflow, non-empty titles, exit 0. |
| VC-3 (External) | WP build code context preserved | (a) `git merge-base --is-ancestor 8d03f2e HEAD` true; (b) working tree clean of builder artifacts (all committed); (c) `git log --name-only 8d03f2e..HEAD -- sfa_delivery/` contains ONLY this WP's commits. `_COMMUNICATION/**` excluded. |
| VC-4 | DSX-1 no-emoji (locked principle #6) | No OS color-emoji in rebuilt templates (`_layout, hub_home, book_entry, book_crop, market_list, assumptions, calc_dash, cropdata_entry`). Monochrome dingbats (✎ ◇ ‹ › ← ⌕ ◔) + the pre-existing WhatsApp `✆` are permitted; flag any 🌱/📅/🪴-class glyph. |
| VC-5 | **Engine-lock fidelity (CRITICAL)** | `git diff 8d03f2e..HEAD -- sfa_delivery/public_assets/js/crop-book-v1.js` MUST be **empty** (engine untouched). `data-calc-goals` JSON shape, `#calc-scope/#qb-*` hooks, goal set (15), result shapes, region picker, basket, parity unchanged. WI-7 is re-skin only. |
| VC-6 | Honest-data / no-fabrication | Missing data renders honest empty-states (crop calendar/care/nursery; market stale "אין מגמה"); no fabricated source pills; `.rng` variety spread only when ≥2 varieties differ. Rich-payload crop renders 200 at every depth (the `$notes`-500 guard). |
| VC-7 | validate_aos.sh | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → **0 FAIL** on the spoke (PASS/SKIP drift acceptable). |
| VC-8 | RTL number integrity + mobile reflow | Numbers/ranges/prices LTR-isolated (`.num`); 375px reflow has no overflow on every surface (covered by VC-2 mobile viewport — spot-check the crop calendar grid + market price cards + assumptions rows). |
| VC-9 | Two-tier write isolation | `/cropdata-entry` stages client-side only (localStorage + contribution funnel); NO canonical write path added to the read-only delivery tier. Confirm no new DB-write code in controllers beyond reads + the existing HMAC ingest. |
| VC-10 | Security — no internal-note leak / no secrets | Crop page renders public-only notes (`is_internal_farm_use_only` filtered); no secrets/creds committed in the deployed asset set; dev-only files (`.env`, `dev_*.php`, `dev_server.sh`, `.env.dev`) are git-ignored and absent from `git ls-files`. |

Total: **10 criteria.**

## 5. Files to Review

### Spec / Design
- LOD300 handoff: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/handoff_ui_redesign/` (mockups + mock.css/mock-v2.css/sfa-icons.js)
- WORKPLAN: `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-REDESIGN/WORKPLAN_full-version_2026-06-08_v1.0.0.md`

### Implementation (build manifest — `git diff 8d03f2e..HEAD`)
- DS/shell: `sfa_delivery/public_assets/css/redesign.css`, `sfa_delivery/public_assets/img/ui-icons.svg`, `sfa_delivery/templates/_layout.php`
- Templates: `templates/pages/{hub_home,book_entry,book_crop,market_list,assumptions,calc_dash,cropdata_entry}.php`
- Controllers: `app/Controllers/{CropBookViewController,MarketViewController,AssumptionsController}.php`, `app/routes.php`
- Tests: `tests/{ClassBRouteTest,CropBookV1RouteTest,CropCardIconTest,RouteSmokeTest}.php`
- `.gitignore`

### Prior Artifacts
- QA Verdict: N/A (this WP's QA was builder-run; re-verify independently per VC-1/VC-2)
- Prior Validation: N/A (first validation round)

## 6. Resolved Findings

N/A — Round #1 (no prior BLOCK).

## 7. Output

Write verdict to: `_COMMUNICATION/team_190/VERDICT_SFA-S003-P004-WP-CB-UI-REDESIGN_L-GATE_VALIDATE_v1.0.0.md`

Use the unified verdict template (7 sections): 1. Verdict Summary · 2. Parameters · 3. Criteria
Table (VC-1..VC-10) · 4. Findings (every FAIL cites file:line) · 5. validate_aos.sh result ·
6. Disposition (PASS / PASS_WITH_FINDINGS / BLOCK) · 7. Next Step.

### Constraints
- **Cross-engine:** builder=claude-code, validator=**{non-Claude — Cursor / Codex / Desktop}** — MUST differ (IR#1/#5).
- **Independence:** do NOT read team_100's COMPLETION_REPORT conclusions or commit messages as truth before forming your own verdict; re-execute VC-1/VC-2 yourself.
- **Evidence:** every FAIL must cite file:line and the failing command output.
- **Disposition routing:** PASS → team_100 executes WP closure (archive → LOD500_LOCK) + the production deploy handoff. BLOCK → resubmission mandate (Phase 3.5 remediation matrix).
