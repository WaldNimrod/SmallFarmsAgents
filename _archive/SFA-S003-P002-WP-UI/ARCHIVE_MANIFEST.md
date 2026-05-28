# ARCHIVE_MANIFEST — SFA-S003-P002-WP-UI — team_191 — v1.0.0

**Date:** 2026-05-28
**Author:** team_191 (Git/Files / Archive Steward)
**WP:** SFA-S003-P002-WP-UI
**Type:** ARCHIVE_MANIFEST
**archive_date:** 2026-05-28
**archived_by:** team_191 (Git/Files / Archive Steward)
**mandate:** `_archive/SFA-S003-P002-WP-UI/MANDATE_SFA-S003-P002-WP-UI-ARCHIVE_v1.0.0.md` (team_100, 2026-05-28)
**procedure:** `_aos/lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.1.0
**file_count:** 113 (67 doc/code + 46 visual_evidence)
**iron_rule:** IR#15 (Archive)

---

## 1. WP Identity

| Field | Value |
|-------|-------|
| **id** | SFA-S003-P002-WP-UI |
| **label** | UX shell + design adoption (Slim/PHP, uPress) — team_35 LOD300 → live sfa.nimrod.bio |
| **status** | DONE |
| **lod_status** | LOD500_LOCKED |
| **closed_at** | 2026-05-28 |
| **production_url** | https://sfa.nimrod.bio/ |
| **milestone** | S003 |
| **program** | SFA-S003-P002 (Data Enrichment + UX shell) |
| **track** | A |
| **effort** | LARGE |
| **profile** | L0 |
| **original_builder** | sfa_build (team_10, Codex) — BUILD_PARTIAL/v1.0.0 |
| **remediation_builder** | team_100 (Claude Opus 4.7 + 12 sub-agents) — RE-BUILD 2026-05-27→2026-05-28 |
| **validator** | team_190 (external non-Claude, GPT-5.5/Cursor) per IR#1 |

---

## 2. Gate Ledger

| Gate | Round | Result | Commit | Verdict / Report artifact |
|------|-------|--------|--------|--------------------------|
| L-GATE_E | — | PASS | — | team_00 in-session 2026-05-24 |
| L-GATE_S | R1 | PASS_WITH_FINDINGS | — | `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` |
| L-GATE_S | R2 | PASS_WITH_FINDINGS | — | `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md` |
| L-GATE_B | original | PASS | 740ea2c | `team_10/BUILD_REPORT_v1.0.0.md` → `v1.0.1.md` → `v1.0.2.md` |
| L-GATE_V | R1 | PASS_WITH_FINDINGS (STALE) | 1fdd396 | `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` |
| L-GATE_V | R2 | PASS (REVOKED) | 740ea2c | `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.1.md` |
| REVOKE | — | by team_00 | dfb8cf1 (gallant-elbakyan-727a60) | `MANDATE_WP-UI-RE-BUILD_v1.0.0.md` |
| L-GATE_B | RE-BUILD | PASS | ea77818 | `team_100/BUILD_REPORT_v2.0.0.md` (consolidates B1-B7 + REPAIR + DEPLOY + SCREENSHOTS) |
| L-GATE_V | R3 | PASS_WITH_FINDINGS | e7e8bb7 (evidence c898c0a) | `team_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md` |
| L-GATE_V | R4 | PASS (terminal) | f2a761b | `team_190/VERDICT_WP-UI_L-GATE_V_R4_v1.0.0.md` |

---

## 3. Inventory

All paths below are relative to `_archive/SFA-S003-P002-WP-UI/`.

### Archive root

| Archive path | SHA (git object) | Size (bytes) | Origin | Summary |
|-------------|-----------------|-------------|--------|---------|
| `MANDATE_WP-UI-RE-BUILD_v1.0.0.md` | ab48b25a | 18806 | Restored from git dfb8cf1 (unmerged branch gallant-elbakyan-727a60) | team_00 REVOKE mandate that triggered the RE-BUILD |
| `MANDATE_SFA-S003-P002-WP-UI-ARCHIVE_v1.0.0.md` | bf8275f6 | 6974 | `_COMMUNICATION/TEAM_100/` | team_100 archive mandate (this operation) |

### team_10/ — original BUILD artifacts (team_10 / Codex)

| Archive path | SHA | Size | Summary |
|-------------|-----|------|---------|
| `team_10/BUILD_REPORT_v1.0.0.md` | 8b27185c | 5301 | Original BUILD_PARTIAL report v1.0.0 |
| `team_10/BUILD_REPORT_v1.0.1.md` | 4c43ac74 | 6876 | BUILD report v1.0.1 (F-BUILD-04 fix) |
| `team_10/BUILD_REPORT_v1.0.2.md` | d75974b0 | 7568 | BUILD_COMPLETE_CLEAN v1.0.2 (F-BUILD-05 fix) |
| `team_10/ac_smoke_20260527.txt` | 1982d89d | 502 | AC smoke test run output 2026-05-27 |
| `team_10/lighthouse/crop_book_table_mobile_20260527.json` | b6e58a68 | 321459 | Lighthouse JSON — crop book table, mobile |
| `team_10/lighthouse/home_mobile_20260527.json` | a7b703e5 | 316493 | Lighthouse JSON — home, mobile |
| `team_10/lighthouse/market_mobile_20260527.json` | ea9fdec8 | 311104 | Lighthouse JSON — market, mobile |
| `team_10/lighthouse_v2/crop-book_table_mobile_v3.json` | 33594d54 | 409162 | Lighthouse v2 JSON — crop book table |
| `team_10/lighthouse_v2/home_mobile_v3.json` | b0b78c56 | 344043 | Lighthouse v2 JSON — home |
| `team_10/lighthouse_v2/market_mobile_v3.json` | c4a6f32d | 434611 | Lighthouse v2 JSON — market |
| `team_10/visual_diff/diff_notes.md` | 46a1e1b0 | 5272 | Visual diff notes from original BUILD |

### team_100/ — RE-BUILD artifacts (team_100 / Claude Opus 4.7)

| Archive path | SHA | Size | Summary |
|-------------|-----|------|---------|
| `team_100/BUILD_REPORT_B1_shells_v1.0.0.md` | 4f82f3c1 | 13971 | RE-BUILD B1: shell templates |
| `team_100/BUILD_REPORT_B2_macros_v1.0.0.md` | 90b5e7ea | 14168 | RE-BUILD B2: Twig macros |
| `team_100/BUILD_REPORT_B3_hub_v1.0.0.md` | 25883786 | 16351 | RE-BUILD B3: hub controller |
| `team_100/BUILD_REPORT_B4_crop_book_v1.0.0.md` | dfe4018f | 22948 | RE-BUILD B4: crop book pages |
| `team_100/BUILD_REPORT_B5_market_v1.0.0.md` | 787155c5 | 11032 | RE-BUILD B5: market pages |
| `team_100/BUILD_REPORT_B6_community_search_v1.0.0.md` | ca1433c8 | 9811 | RE-BUILD B6: community + search |
| `team_100/BUILD_REPORT_B7_assets_v1.0.0.md` | 9c7357d6 | 7353 | RE-BUILD B7: assets + sfa.js + icons |
| `team_100/BUILD_REPORT_v2.0.0.md` | a2744482 | 19493 | RE-BUILD consolidated report (B1-B7 + REPAIR + DEPLOY + SCREENSHOTS) |
| `team_100/DEPLOY_REPORT_v1.0.0.md` | 9ef7d67b | 10332 | Deployment report — uPress FTPS upload |
| `team_100/REPAIR_REPORT_controllers_v1.0.0.md` | e8d6083c | 19415 | REPAIR: HubController DI fix (F-190-R3-01) |
| `team_100/REPAIR_REPORT_css_v1.0.0.md` | 979b1595 | 12278 | REPAIR: CSS audit and BEM cleanup |
| `team_100/SCREENSHOTS_REPORT_v1.0.0.md` | a767375f | 15337 | Playwright screenshot evidence report |

### team_190/ — Gate verdicts and mandates (team_190 / GPT-5.5, external validator)

Files marked **[misplaced]** were at the `_COMMUNICATION/TEAM_190/` root instead of a WP subdirectory (Iron Rule #12 / POST_GATE_ARCHIVE_PROCEDURE Step 3 misplaced scan).

| Archive path | SHA | Size | Gate | Summary |
|-------------|-----|------|------|---------|
| `team_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` | 2cd4f7fc | 9439 | L-GATE_S R1 | **[misplaced]** L-GATE_S mandate R1 |
| `team_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_RESUBMISSION_v1.0.1.md` | a8a18a80 | 9731 | L-GATE_S R2 | **[misplaced]** L-GATE_S resubmission mandate |
| `team_190/MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md` | 532ba13a | 10526 | L-GATE_V R3 | L-GATE_V R3 mandate (F-190-R3-01/02 remediation) |
| `team_190/MANDATE_WP-UI_L-GATE_V_R4_v1.0.0.md` | 095ab7ae | 5581 | L-GATE_V R4 | L-GATE_V R4 narrow re-check mandate |
| `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` | 8d734afd | 11247 | L-GATE_S R1 | **[misplaced]** L-GATE_S R1 PASS_WITH_FINDINGS verdict |
| `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md` | ea86de19 | 5917 | L-GATE_S R2 | **[misplaced]** L-GATE_S R2 PASS_WITH_FINDINGS verdict |
| `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` | 825efbbb | 8832 | L-GATE_V R1 | R1 PASS_WITH_FINDINGS (STALE — reviewed commit superseded) |
| `team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.1.md` | 0bd0a902 | 5000 | L-GATE_V R2 | R2 PASS (REVOKED by team_00) |
| `team_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md` | 1e96e269 | 8693 | L-GATE_V R3 | R3 PASS_WITH_FINDINGS (F-190-R3-01 MAJOR + F-190-R3-02 MINOR) |
| `team_190/VERDICT_WP-UI_L-GATE_V_R4_v1.0.0.md` | 3e97808f | 4973 | L-GATE_V R4 | R4 PASS (terminal) — LOD500_LOCKED authorized |

### team_35/ — LOD300 design handoff (_handoff/ tree)

| Archive path | SHA | Size | Summary |
|-------------|-----|------|---------|
| `team_35/_handoff/COMPONENTS.md` | 0ee163a6 | 15809 | BEM component registry (SSoT per LOD400 v1.0.3 §0.5) |
| `team_35/_handoff/DESIGN_TOKENS.md` | c124bebf | 6198 | Design token definitions |
| `team_35/_handoff/HANDOFF_LOD300.md` | b39854c0 | 15075 | LOD300 handoff narrative |
| `team_35/_handoff/IMPLEMENTATION_PLAN.md` | c582ed4e | 20826 | Implementation plan |
| `team_35/_handoff/MODULES_REGISTRY.yaml` | c384af75 | 11460 | Module registry YAML |
| `team_35/_handoff/README.md` | a78de058 | 5056 | Handoff README |
| `team_35/_handoff/TEMPLATES.md` | 67777e75 | 14382 | Template specifications |
| `team_35/_handoff/team_100_activation_prompt.md` | ce83df27 | 8750 | team_100 activation prompt |
| `team_35/_handoff/team_110_activation_prompt.md` | 48ad6472 | 8540 | team_110 activation prompt |
| `team_35/_handoff/design/app.jsx` | e735652b | 9500 | App shell JSX design file |
| `team_35/_handoff/design/art-prompts.jsx` | 8461ae6f | 8306 | Art prompts design file |
| `team_35/_handoff/design/community.css` | 05cd82a2 | 9148 | Community CSS |
| `team_35/_handoff/design/community.jsx` | aa3d73d2 | 10282 | Community JSX |
| `team_35/_handoff/design/crop-book-deep.css` | fac2e540 | 13055 | Crop book deep CSS |
| `team_35/_handoff/design/crop-book-deep.jsx` | 2bd9217e | 24967 | Crop book deep JSX |
| `team_35/_handoff/design/design-canvas.jsx` | fa1f93e7 | 49677 | Full design canvas |
| `team_35/_handoff/design/desktop-extras.css` | f5e5246b | 12649 | Desktop extras CSS |
| `team_35/_handoff/design/desktop-extras.jsx` | cf403e7c | 28222 | Desktop extras JSX |
| `team_35/_handoff/design/desktop.css` | 4ac21362 | 13240 | Desktop CSS |
| `team_35/_handoff/design/desktop.jsx` | af012dd8 | 20454 | Desktop JSX |
| `team_35/_handoff/design/garden-journal.jsx` | 648aba4d | 25832 | Garden journal JSX |
| `team_35/_handoff/design/gj.css` | c7011d85 | 22848 | Garden journal CSS |
| `team_35/_handoff/design/hub.css` | 0633f321 | 9326 | Hub CSS |
| `team_35/_handoff/design/hub.jsx` | 2f0bb6b9 | 14498 | Hub JSX |
| `team_35/_handoff/design/illustrations.jsx` | cb126d51 | 14443 | Illustrations JSX |
| `team_35/_handoff/design/image-slot.js` | d1eb01bc | 31288 | Image slot JS |
| `team_35/_handoff/design/index.html` | 3e381c95 | 11922 | Design index HTML |
| `team_35/_handoff/design/mental-model.jsx` | 61c1bdfa | 9024 | Mental model JSX |
| `team_35/_handoff/design/modules-catalog.jsx` | 6e8e042b | 3645 | Modules catalog JSX |
| `team_35/_handoff/design/primitives.jsx` | caf930fe | 6484 | Primitives JSX |
| `team_35/_handoff/design/system.css` | 557fab97 | 7632 | System CSS |
| `team_35/_handoff/design/wireframes.jsx` | 69fc5b6d | 26182 | Wireframes JSX |

### visual_evidence/ — 46 Playwright screenshots + Lighthouse

46 files copied (not moved) from `visual_diff/` at project root. Original `visual_diff/` is preserved in place per mandate §4 ("kept on build branch + archive copy").

| Subset | Count | Notes |
|--------|-------|-------|
| `desktop__*.png` (14) | 14 | Desktop viewport screenshots |
| `mobile__*.png` (14) | 14 | Mobile viewport screenshots |
| `tablet__*.png` (14) | 14 | Tablet viewport screenshots |
| `lighthouse_mobile.html` | 1 | Lighthouse HTML report |
| `lighthouse_mobile.json` | 1 | Lighthouse JSON data |
| `capture.py` | 1 | Playwright capture script |
| `results.json` | 1 | Playwright test results |
| **Total** | **46** | |

---

## 4. Preserved in Place (NOT archived)

| Path | Reason |
|------|--------|
| `sfa_delivery/` | LIVE PRODUCTION — entire stack for https://sfa.nimrod.bio/ |
| `_aos/work_packages/S003/SFA-S003-P002-WP-UI/LOD400_spec.md` | LOD500 reference — immutable per ADR042 |
| `_aos/roadmap.yaml` WP-UI row | Gate history reference — IR#4 single writer (team_100) |
| `visual_diff/` | Original Playwright evidence — preserved on build branch; archive copy in `visual_evidence/` |

---

## 5. Closure Trail

| Event | Commit | Branch | Date | Description |
|-------|--------|--------|------|-------------|
| team_190 R4 PASS verdict | 4517010 | main | 2026-05-28 | Terminal L-GATE_V PASS — LOD500_LOCKED authorized |
| team_100 closure (ADR042 step-2) | a3963fd | main | 2026-05-28 | roadmap LOD500_LOCKED + archive_ref set |
| merge claude/sfa-ui-build-v2 → main | ae9284a | main | 2026-05-28 | RE-BUILD merge commit (--no-ff) |
| team_00 REVOKE mandate | dfb8cf1 | gallant-elbakyan-727a60 (unmerged) | 2026-05-27 | team_00 personal audit found ~91% dead CSS; issued RE-BUILD |
| RE-BUILD BUILD commit | ea77818 | claude/sfa-ui-build-v2 | 2026-05-28 | team_100 RE-BUILD PASS |

---

## 6. Misplaced Artifacts Detected (Step 3 — Iron Rule #12)

The following artifacts were found at `_COMMUNICATION/TEAM_190/` root (should have been in a WP subdirectory):

- `MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` — at team root, should have been `TEAM_190/SFA-S003-P002-WP-UI/`
- `MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_RESUBMISSION_v1.0.1.md` — at team root
- `VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` — at team root
- `VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md` — at team root

All four included in this archive under `team_190/`.

Additionally:
- `MANDATE_WP-UI-RE-BUILD_v1.0.0.md` — created on unmerged branch `gallant-elbakyan-727a60` (commit dfb8cf1); not present in main working tree. Restored into archive directly from git history.

---

## 7. Path Redirects

*(Mandatory — POST_GATE_ARCHIVE_PROCEDURE v1.1.0 M.2)*

| Former path (before archive) | Archived path |
|------------------------------|---------------|
| `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_10/BUILD_REPORT_v1.0.0.md` |
| `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.1.md` | `_archive/SFA-S003-P002-WP-UI/team_10/BUILD_REPORT_v1.0.1.md` |
| `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-UI/BUILD_REPORT_v1.0.2.md` | `_archive/SFA-S003-P002-WP-UI/team_10/BUILD_REPORT_v1.0.2.md` |
| `_COMMUNICATION/TEAM_100/SFA-S003-P002-WP-UI/BUILD_REPORT_v2.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_100/BUILD_REPORT_v2.0.0.md` |
| `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/MANDATE_SFA-S003-P002-WP-UI-ARCHIVE_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/MANDATE_SFA-S003-P002-WP-UI-ARCHIVE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.1.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_V_v1.0.1.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_WP-UI_L-GATE_V_R3_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_WP-UI_L-GATE_V_R4_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_WP-UI_L-GATE_V_R4_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/MANDATE_WP-UI_L-GATE_V_R3_v2.0.0.md` |
| `_COMMUNICATION/TEAM_190/MANDATE_WP-UI_L-GATE_V_R4_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/MANDATE_WP-UI_L-GATE_V_R4_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_RESUBMISSION_v1.0.1.md` | `_archive/SFA-S003-P002-WP-UI/team_190/MANDATE_SFA-S003-P002-WP-UI_L-GATE_S_RESUBMISSION_v1.0.1.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md` | `_archive/SFA-S003-P002-WP-UI/team_190/VERDICT_SFA-S003-P002-WP-UI_L-GATE_S_v1.0.1.md` |
| `_COMMUNICATION/team_35/SFA-S003-P002-WP-UI/_handoff/` (full tree) | `_archive/SFA-S003-P002-WP-UI/team_35/_handoff/` |

**Note for team_100:** `roadmap.yaml` gate_history for L-GATE_V R2 contains `revoke_mandate: _COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` — this path is now stale (file archived; restored from unmerged commit dfb8cf1). Redirect: `_archive/SFA-S003-P002-WP-UI/MANDATE_WP-UI-RE-BUILD_v1.0.0.md`. Per IR#4, roadmap.yaml updates are team_100's responsibility; team_191 flags here per M.4.

---

## 8. Validation

```
validate_aos.sh — post-archive run (2026-05-28)
=================================================
RESULT: 29 PASS / 19 SKIP / 0 FAIL
=================================================
L-GATE_BUILD EXIT CRITERION: SATISFIED

Check 15: No stale artifacts for completed WPs in _COMMUNICATION/ — PASS
Check 4:  All spec_refs resolve to existing files — PASS (LOD400_spec.md preserved in place)
Check 32: _aos/ tree committed (no propagation drift) — PASS
```

---

*Archive manifest generated by team_191 (Git/Files / Archive Steward) | 2026-05-28 | Iron Rule #15 | POST_GATE_ARCHIVE_PROCEDURE v1.1.0*
