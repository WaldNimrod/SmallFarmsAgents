# Evidence manifest — Pre-launch re-audit (acca9b2) — 2026-06-04

**Mandate:** `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-PRELAUNCH-QA/REAUDIT_MANDATE_team50_full-system-vs-mockups_2026-06-04_v1.0.0.md`  
**Live:** https://sfa.nimrod.bio · SHA **acca9b2** · cache-bust **`?v=1780576560`**  
**Engine:** team_50 (Cursor Composer) · CDP harness (production TLS, no cert-bypass on deep/e2e probes)

## Design SSoT (Board frames)

| Board | Path |
|-------|------|
| Board-A | `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-A-Book-and-Calculator.html` |
| Board-B | `_archive/SFA-S003-P004-WP-CB-UI-CLASSB/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/Board-B-Hub-Market-Search-Community-About-Account.html` |

Local serve: `python3 -m http.server 8767` in `HANDOFF/design/` (for `board_frame_shots.mjs`).

## Artifacts

| File | Role |
|------|------|
| `deploy_fingerprint.json` | Live CSS/HTML/API fingerprint @ `?v=1780576560` |
| `qa_probe/qa_probe_result.json` | Overflow + forbidden-token scan (36 page×viewport) |
| `qa_probe/screenshots/*.png` | Live full-page captures @ 1440 / 768 / 375 |
| `qa_probe/screenshots/global-search-hit-lettuce_desktop1440.png` | Search hit path (`q=חסה`) — glyph vs watercolor check |
| `cdp_deep/cdp_deep_result.json` | Bbox, leaks, console, calc/market probes |
| `e2e_matrix/e2e_matrix_cdp.json` | Interaction matrix (logo, cards, calc export, ranges, …) |
| `design_pairs/board_*_{desktop1440,tablet768,mobile375}.png` | Board frame crops (30 files) |
| `design_pairs/design_pairs_manifest.json` | Board ↔ live screenshot pairing |

## Harness scripts (this folder)

- `prelaunch_reaudit_probe.json` — qa_probe config  
- `reaudit_deep_probe.mjs` — deep fidelity probe  
- `e2e_matrix_runner.mjs` — E2E matrix  
- `board_frame_shots.mjs` — Board-A/B frame captures  
- `deploy_fingerprint.py` — deploy/CSS fingerprint  

## qa_probe note

`qa_probe.mjs` scans **full `innerHTML`** for forbidden tokens. Failures on `direct_seed`, `half_hardy`, `yield_per_bed_m`, and category slugs in **`<option value>` / JS** are **not** user-visible leaks — see report §4 (INFO). Structural overflow: **0** failures across all 36 probes.
