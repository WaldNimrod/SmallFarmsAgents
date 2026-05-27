---
id: MANDATE_SFA-S003-P002-WP-UI_L-GATE_B_v1.0.0
from: Team 100 (Chief System Architect — smallfarmsagents spoke)
to: Team 10 (sfa_build — Claude Sonnet builder)
date: 2026-05-27
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-UI
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Cross-engine per IR#1. builder=sfa_build (Claude Sonnet — you), L-GATE_V validator=team_190 (non-Claude, GPT-5.5/Cursor — different engine required)."
resubmission_round: 1
---

# L-GATE_B Mandate — SFA-S003-P002-WP-UI

**Standalone web UX shell — adopt team_35 LOD300 onto Slim/PHP/uPress**
**Track:** A | **Profile:** L0 | **Risk:** MEDIUM

---

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | In-session approval of Option B (adapt team_35 LOD300 to Slim/PHP/uPress; preserve design, replace stack assumption only). |
| L-GATE_S | FAIL (R1) | 2026-05-27 | team_190 (GPT-5.5/Cursor) | 2 BLOCKERs + 2 MAJOR + 1 MINOR — addressed in LOD400 v1.0.1. |
| **L-GATE_S** | **PASS_WITH_FINDINGS (R2)** | **2026-05-27** | **team_190 (GPT-5.5/Cursor)** | **All R1 findings resolved. 2 new MINOR findings (LV-S-6/7) addressed inline in LOD400 v1.0.2. Disposition: DISPATCH_BUILD. Verdict: `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md`.** |

This is **Round 1** for L-GATE_B — fresh BUILD dispatch.

---

## 3. Scope

**L-GATE_B — BUILD execution + functional acceptance.** Implement LOD400 v1.0.2 end-to-end and verify all 38 ACs pass before submitting for L-GATE_V (team_190 external validation).

**Specifically you must:**
1. Execute all 9 phases B.0..B.8b per LOD400 §11 (estimated 13h total)
2. Implement the 14 HTML routes + 8 API endpoints per LOD400 §4
3. Adopt all 7 CSS files from `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/design/` verbatim per LOD400 §3.1
4. Translate JSX→PHP includes per LOD400 §3.3 template tree
5. Generate `modules.php` from `MODULES_REGISTRY.yaml` via the generator script (LOD400 §3.5 + R-05)
6. Write the ~21 new phpunit tests per LOD400 §9.1 + §9.5
7. Deploy via FTPS to sfa.nimrod.bio (existing creds in main `.env`)
8. Verify all 38 ACs (visual diff via Claude_in_Chrome at B.8a, Lighthouse at B.8b)
9. Write BUILD_REPORT to `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.0.md`
10. Commit + push for L-GATE_V dispatch

**Constraints (binding):**
- `/crop-book/*` is the canonical URL contract — NOT `/book/*`. The team_35 design's `/book/*` references are decorative; honor `/crop-book/*` in all templates, routes, controller paths, and modules.php.
- Community write surfaces are explicitly OUT of scope (deferred to S004). Do NOT create `community_contributions` table, `CommunityController`, POST `/api/v1/community/contribute`, or GET `/api/v1/community/feed`. The `community.php` template is STATIC (WhatsApp link from `modules.php::contact`).
- Existing live `sfa_delivery/` from WP-S003-P003 (Slim app at `https://sfa.nimrod.bio`) must NOT regress. The 4 regression ACs (AC-29, AC-30, AC-36, AC-37) verify this.
- Existing waldhomeserver `sfa_ingest_push.py` cron at `30 6 * * *` must continue to push successfully (AC-37 verifies via 24h log observation).
- No locked-file changes anywhere (per LOD400 §6).

---

## 4. Validation Criteria (= LOD400 §5 — 38 ACs)

The full AC matrix is in LOD400 v1.0.2 §5. Summary:

| Category | AC range | Count | Tested via |
|----------|----------|-------|------------|
| Foundation (CSS chain, shells, fonts, RTL, viewports) | AC-01..AC-06 | 6 | curl + Claude_in_Chrome |
| Per-route HTML (14 routes × 1 functional + 1 visual) | AC-07..AC-20 | 14 | curl + screenshot vs artboard |
| API endpoints (8 endpoints) | AC-21..AC-28 | 8 | curl + jq |
| HMAC regression | AC-29..AC-30 | 2 | curl with HMAC sig |
| Non-functional (LCP, console, WCAG, JS, RTL) | AC-31..AC-35 | 5 | Lighthouse + axe-core + manual |
| Live regression (health + cron + legacy separation) | AC-36..AC-38 | 3 | curl + tail log + browser |
| **TOTAL** | | **38** | |

**Every AC has a specific pass/fail check defined in §5. Do not skip ACs. If any AC fails, document it in BUILD_REPORT and decide remediation before L-GATE_V dispatch.**

---

## 5. Files to Review

### Spec Documents (binding for BUILD)
- **LOD400 v1.0.2 (primary build target):** `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md`
  - Read §0 (R2 amendment summary), §3 (file mapping), §4 (routes), §5 (ACs), §9 (test plan), §11 (build phases) in that order
- **team_35 design source (verbatim adoption):** `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/design/` — 7 CSS files + JSX components (port to PHP) + `index.html` (artboards for visual diff)
- **team_35 contract docs:** `DESIGN_TOKENS.md`, `COMPONENTS.md`, `TEMPLATES.md`, `MODULES_REGISTRY.yaml`, `IMPLEMENTATION_PLAN.md` (**Note: IMPLEMENTATION_PLAN.md is SUPERSEDED by LOD400 §11 — read for context only, do not follow its Flask instructions**)

### Architectural authority (binding)
- Parent DECISION: `_COMMUNICATION/team_00/DECISION_SFA-S003-P003_DEDICATED_SFA_SUBDOMAIN_2026-05-23_v1.0.0.md`
- Canonical architecture: `documentation/02-architecture/sfa-delivery-tier.md`
- Canonical schema: `documentation/03-data-and-schema/sfa-mysql-mirror.md`

### Existing implementation (read-only — extend, do not regress)
- `sfa_delivery/` — full Slim app from WP-S003-P003-WP-2/3 (Slim 4 + PDO + 4+2 MySQL tables + 4 controllers + 6 templates + .htaccess + 11 phpunit tests + composer.json + .env.example). **All existing files unless explicitly listed in LOD400 §3.3 for replacement remain unchanged.**
- `organic_market_agent/publisher/sfa_ingest_push.py` — waldhomeserver publisher (unchanged in this WP)
- `sfa_delivery/README.md` — deploy procedure (extend with module-regenerate step)

### Prior verdict (your context)
- L-GATE_S R2 verdict: `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md`
- L-GATE_S R1 verdict (historical): `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md`

### Out of scope (do NOT touch)
- `organic_market_agent/admin/` — existing Flask admin app on waldhomeserver
- `organic_market_agent/crop_book/` — existing Flask blueprint on waldhomeserver
- `organic_market_agent/publisher/wp_upload.py`, `ftps_upload.py`, `upload_dispatch.py` — DEPRECATED from WP-5; do not extend
- Anything under `_archive/`
- Other teams' files under `_COMMUNICATION/team_XX/` where XX ≠ 10 or 00

---

## 6. Resolved Findings from Round N-1

N/A — this is Round 1 for L-GATE_B.

(But two MINOR L-GATE_S findings from team_190 R2 (LV-S-6/7) were already addressed inline in LOD400 v1.0.2 by team_100. You will see the cleanup in §0 + §12 + the v1.0.2 footer line.)

---

## 7. Output Format

### BUILD_REPORT
Write to: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.0.md`

Structure (7 sections, mirrors verdict template):

1. **Build Summary** — single line: BUILD_COMPLETE | BUILD_PARTIAL | BUILD_FAIL + 2-sentence rationale
2. **Parameters** — your engine + version (Claude Sonnet 4.x), branch (`claude/sfa-ui-build`), phases executed (B.0..B.8b), wall-clock hours actually spent, vendor/ + bundle sizes
3. **AC Results Table** — all 38 ACs with PASS/FAIL + evidence pointer (curl output snippet / screenshot path / Lighthouse score / log tail)
4. **Findings** — any AC that didn't pass cleanly, severity, root-cause, remediation status
5. **`validate_aos.sh`** — output (expected 0 FAIL)
6. **Artifacts produced** — list of files created + modified, screenshot dir path, Lighthouse JSON path, BUILD bundle path
7. **Next Step** — single imperative sentence for team_100

### Visual evidence
Save to `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/visual_diff/` (B.8a per LOD400 §9.2):
- 28 screenshots: 14 routes × 2 viewports (390×844 mobile, 1280×900 desktop)
- Naming: `{route_slug}_{mobile|desktop}_{YYYYMMDD}.jpg`
- A `diff_notes.md` per LOD400 §9.2 if any visual deltas > 4 px

### Lighthouse evidence
Save to `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/lighthouse/` (B.8b per LOD400 §9.3):
- 3 JSON reports: `/`, `/crop-book/table`, `/market/`
- Naming: `{route_slug}_mobile_{YYYYMMDD}.json`

### Branch + commits
- Branch: `claude/sfa-ui-build` off `claude/gallant-elbakyan-727a60` (current head: 5bfc825 + the v1.0.2 cleanup commit which team_100 just pushed)
- Commit cadence: per phase or per logical chunk; commit messages reference WP id + phase
- Final commit pushes branch + dispatches L-GATE_V via separate mandate (team_100 will issue, you flag readiness in BUILD_REPORT §7)

### Constraints (reminder)

- **Cross-engine (IR#1):** L-GATE_V validator will be team_190 (non-Claude). Your output (visual screenshots + BUILD_REPORT) is their input — make it self-evident and reproducible.
- **IR#4:** team_100 is the single writer to `_aos/roadmap.yaml`. Do NOT modify roadmap. team_100 transitions WP status post-BUILD.
- **Honor binding contracts:** `/crop-book/*` URLs + no community writes + no canonical doc drift. The two BLOCKERs from L-GATE_S R1 are documented exactly so you don't accidentally re-introduce them.
- **Test ownership:** phpunit you run locally; visual + Lighthouse you run at B.8a/B.8b via Claude_in_Chrome + npx.
- **Live regression discipline:** every commit deployed must pass AC-21, AC-29, AC-30, AC-36 immediately via curl. If any regresses, stop and rollback.
- **`composer test` before any phase commit.**
- **Enforcement mode:** STANDARD (PARTIAL or FAIL on BUILD = stop, write report, hand back to team_100; no L-GATE_V dispatch from BUILD_PARTIAL).

---

*Mandate generated 2026-05-27 by team_100 per `/AOS_gate-mandate` canon. Signal B (L-GATE_S PASS → L-GATE_B dispatch). Round 1.*
*Awaiting your BUILD_REPORT.*
