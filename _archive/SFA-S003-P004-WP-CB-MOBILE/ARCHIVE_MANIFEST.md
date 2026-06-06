---
id: ARCHIVE_MANIFEST_SFA-S003-P004-WP-CB-MOBILE
wp: SFA-S003-P004-WP-CB-MOBILE
status: COMPLETE
lod_status: LOD500_LOCKED
closed_at: "2026-06-06"
archived_at: "2026-06-06"
archived_by: team_191
archive_method: "L2 spoke self-archive (ADR034 R9 — git commit is the audit record); team_191 git mv under team_100 mandate"
mandate_ref: "_archive/SFA-S003-P004-WP-CB-MOBILE/team_191/MANDATE_ARCHIVE_SFA-S003-P004-WP-CB-MOBILE_2026-06-06.md"
closing_verdict: "team_50 binding L-GATE_V = GO (2026-06-06) — _archive/SFA-S003-P004-WP-CB-MOBILE/team_50/QA_REPORT_2026-06-06.md"
roadmap_entry: "_aos/roadmap.yaml → id: SFA-S003-P004-WP-CB-MOBILE"
archive_root: "_archive/SFA-S003-P004-WP-CB-MOBILE/"
live_sha: a18816c
served_html_version: 1780576560
served_asset_version: 1780691715
---

# Archive Manifest — SFA-S003-P004-WP-CB-MOBILE

**WP:** Crop-book mobile UI work package — @375 mobile responsiveness remediation for the
public SFA delivery tier (hub, crop-book list, crop detail surfaces simple/full/deep, calculator,
market, about) atop the team_35 v4 mobile design package (`MOBILE_DESIGN_v4.0.0`, `mobile-fixes.css`).

**Final status:** COMPLETE / LOD500_LOCKED · **Live:** https://sfa.nimrod.bio
(HTML `?v=1780576560`, assets `?v=1780691715`) · **Final code commit:** `a18816c`.

## Closing verdict
- **team_50 binding L-GATE_V = GO**, 2026-06-06 (@375 + desktop visual QA).
- Test suite: **217/217** passing.
- Key fix: @375 horizontal overflow collapsed from **9053px → 1366px** (no horizontal scroll).
- Live verification: `https://sfa.nimrod.bio` serving HTML `?v=1780576560` / assets `?v=1780691715`.

## Gate / delivery ladder
| Step | Result | Date | Owner | Notes |
|------|--------|------|-------|-------|
| DESIGN handoff | v4.0.0 | 2026-06-05 | team_35 | mobile design package + `mobile-fixes.css` + surface prototypes |
| LOD400 build spec | issued | 2026-06-05 | team_100 → team_10 | mobile-build work instructions |
| DEPLOY | AUTHORIZED → DEPLOYED | 2026-06-05/06 | team_99 | request → unblock → authorized → deployed-standdown |
| team_100 sweep | findings recorded | 2026-06-06 | team_100 | qa_probe sweep (@375 + desktop) — SWEEP_FINDINGS |
| L-GATE_V | **GO** | 2026-06-06 | team_50 | @375 9053px→1366px; suite 217/217; live `?v=1780576560`/`?v=1780691715` |

## Files moved (source → archive)

### team_100 → `_archive/SFA-S003-P004-WP-CB-MOBILE/team_100/`
- `DESIGN_MANDATE_team35_mobile-ui_2026-06-05_v1.0.0.md`
- `LOD400_team10_mobile-build_2026-06-05_v1.0.0.md`
- `team100_sweep_2026-06-06/SWEEP_FINDINGS_2026-06-06.md`
- `team100_sweep_2026-06-06/qa_config.json`
- `team100_sweep_2026-06-06/qa_probe_result.json`

### team_35 → `_archive/SFA-S003-P004-WP-CB-MOBILE/team_35/`
- `design_handoff_mobile_ui/MOBILE_DESIGN_v4.0.0.md`
- `design_handoff_mobile_ui/README.md`
- `design_handoff_mobile_ui/design_files/SFA Mobile Design Board.html`
- `design_handoff_mobile_ui/design_files/classb.css`
- `design_handoff_mobile_ui/design_files/cropbook-v1.css`
- `design_handoff_mobile_ui/design_files/mobile-fixes.css`
- `design_handoff_mobile_ui/design_files/surface-about.html`
- `design_handoff_mobile_ui/design_files/surface-calc.html`
- `design_handoff_mobile_ui/design_files/surface-cards.html`
- `design_handoff_mobile_ui/design_files/surface-crop-deep.html`
- `design_handoff_mobile_ui/design_files/surface-crop-full.html`
- `design_handoff_mobile_ui/design_files/surface-crop.html`
- `design_handoff_mobile_ui/design_files/surface-hub.html`
- `design_handoff_mobile_ui/design_files/surface-market.html`
- `design_handoff_mobile_ui/design_files/tokens.css`

### TEAM_50 → `_archive/SFA-S003-P004-WP-CB-MOBILE/team_50/`
- `ACTIVATION_PROMPT_team50_2026-06-06.md`
- `MSG-team100-to-team50-QA-GO-LIVE-2026-06-06.md`
- `MSG-team50-to-team100-2026-06-06.md`
- `QA_MANDATE_team50_375_2026-06-05_v1.0.0.md`
- `QA_REPORT_2026-06-06.md`
- `qa_run_2026-06-06/cdp_deep_probe.mjs`
- `qa_run_2026-06-06/cdp_deep_result.json`
- `qa_run_2026-06-06/cdp_interaction_probe.mjs`
- `qa_run_2026-06-06/cdp_interaction_result.json`
- `qa_run_2026-06-06/qa_config.json`
- `qa_run_2026-06-06/qa_probe_result.json`
- `qa_run_2026-06-06/screenshots/` (16 PNGs: about/calc/crop-deep/crop-full/crop-simple/cropbook-list/hub/market × desktop1280 + mobile375)

### team_99 → `_archive/SFA-S003-P004-WP-CB-MOBILE/team_99/`
- `DEPLOY_REQUEST_team99_2026-06-05_v1.0.0.md`
- `MSG-team100-to-team99-WP-CB-MOBILE-DEPLOY-AUTHORIZED-2026-06-05.md` (loose, was in shared team_99 dir)
- `MSG-team100-to-team99-WP-CB-MOBILE-DEPLOY-UNBLOCK-2026-06-05.md` (loose)
- `MSG-team100-to-team99-WP-CB-MOBILE-DEPLOYED-STANDDOWN-2026-06-06.md` (loose)

### team_191 → `_archive/SFA-S003-P004-WP-CB-MOBILE/team_191/`
- `MANDATE_ARCHIVE_SFA-S003-P004-WP-CB-MOBILE_2026-06-06.md` (the archival mandate)

## Untracked remnants removed (NOT archived into git)
Per the mandate, untracked duplicate assets and uncommitted sweep evidence were `rm -rf`'d
so the source `_COMMUNICATION/*/SFA-S003-P004-WP-CB-MOBILE/` dirs are fully gone:
- `team_35/.../design_handoff_mobile_ui/design_files/assets/` — duplicate watercolor PNGs / webp heroes / module images / `Carmela.ttf` (originals live in `sfa_delivery/public_assets/img/`).
- `TEAM_100/.../team100_sweep_2026-06-06/screenshots/` — 16 uncommitted sweep PNGs (never git-tracked; sweep findings + qa_probe JSON preserved above).

## Open follow-ups (tracked, non-blocking)
1. **Deep provenance pills** — provenance pills on the crop "deep" surface still pending.
2. **Calculator client math** — only **6 of 14** calculators carry live client-side JS math; the remaining 8 are server-side "בקרוב" stubs (time-anchor captured but unused).

## Left in place
- `_aos/roadmap.yaml` (SSOT — team_100 lane; status flipped `VALIDATE → COMPLETE` this change).
- `CLAUDE.md`, `documentation/`, and the live `sfa_delivery/` source.

*Archived by team_191 (Git/Files) per the team_100 Iron-Rule-#15 mandate, 2026-06-06. git mv only; team_100 owns the commit + push (the git commit is the audit record — ADR034 R9, L2 spoke).*
