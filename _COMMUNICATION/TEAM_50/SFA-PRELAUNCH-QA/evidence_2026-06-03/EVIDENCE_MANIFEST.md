# Evidence manifest — SFA pre-launch QA 2026-06-03

| Field | Value |
|-------|-------|
| **Audit** | PRELAUNCH_QA team_50 |
| **Target** | `https://sfa.nimrod.bio` |
| **Engine** | Cursor Composer (team_50) |
| **Mandate** | `_COMMUNICATION/TEAM_50/SFA-PRELAUNCH-QA/QA_MANDATE_PRELAUNCH_VISUAL_E2E_2026-06-03_v1.0.0.md` |
| **Run UTC** | 2026-06-03T20:33–20:45Z (approx.) |

## Tooling

| Tool | Path / role |
|------|-------------|
| qa_probe.mjs | `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs` |
| Config | `evidence_2026-06-03/prelaunch_qa_probe.json` |
| CDP deep | `evidence_2026-06-03/cdp_deep_probe.mjs` → `cdp_deep/cdp_deep_result.json` |
| E2E CDP | `evidence_2026-06-03/e2e_matrix_runner.mjs` → `e2e_matrix/e2e_matrix_cdp.json` |
| Deploy fingerprint | `deploy_fingerprint.json`, `deploy_fingerprint.py` |
| Link crawl + extras | `link_crawl_and_extras.json` |
| Design boards | Python `http.server` @ `127.0.0.1:8767` |
| Browser MCP | cursor-ide-browser (mobile crop-book visual) |

## Deploy precondition

| Check | Result |
|-------|--------|
| Mandate tip `7fbcf89` WI-5 (`cb-paths { display: grid` in crop-book-v1.css) | **FAIL** on live |
| Mandate tip WI-6 (`.sh__mark svg { width: 100%` in classb.css) | **FAIL** on live |
| team_99 DEPLOY_REPORT SHA | `08f529d` (not `7fbcf89`) |
| Live asset `?v=` on `/` | `1780515224` |

## Screenshot inventory

### qa_probe (80 captures: 20 pages × 4 viewports)

Directory: `qa_probe/screenshots/`

Summary: `qa_probe/qa_probe_result.json` — **22/80** automated substring/overflow failures (see report).

### Design pairs

| File | Description |
|------|-------------|
| `design_pairs/board_book-entry_desktop1440.png` | Board-A `book-entry` frame |
| `design_pairs/board_calc-page_desktop1440.png` | Board-A `calc-page` frame |
| `design_pairs/board_hub-home_desktop1440.png` | Board-B `hub-home` frame |
| `design_pairs/board_market-list_desktop1440.png` | Board-B `market-list` frame |
| `design_pairs/board_community_desktop1440.png` | Board-B `community` frame |
| `design_pairs/live_crop-book-entry_mobile375_browser.png` | Live mobile entry (browser MCP) |
| `design_pairs/design_pairs_manifest.json` | Live ↔ board pair mapping |

Live desktop pairs: `qa_probe/screenshots/{page}_desktop1440.png` per `design_pairs_manifest.json`.

## JSON artifacts

- `deploy_fingerprint.json`
- `qa_probe/qa_probe_result.json`
- `cdp_deep/cdp_deep_result.json`
- `e2e_matrix/e2e_matrix_cdp.json`
- `link_crawl_and_extras.json`
- `design_pairs/design_pairs_manifest.json`
