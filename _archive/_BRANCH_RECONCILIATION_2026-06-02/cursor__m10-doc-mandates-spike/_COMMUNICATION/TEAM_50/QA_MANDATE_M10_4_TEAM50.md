---
document_type: QA_MANDATE
version: "1.1"
---

# QA Mandate — M10.4 Headless browser and mypips

**Mandate ID:** `QA-MANDATE-M10-4-TEAM50`  
**From:** Team 10 (coordination, per project QA procedure)  
**To:** Team 50 (QA) — **agent-executable**  
**CC:** Team 100 (Architecture), Team 10 (Feature Dev), Team 190 (Preflight, optional)  
**Date:** 2026-04-04  
**Updated:** 2026-04-05 — P1 Alembic head **057** (M10.5 **056** + M10.4 R3 **057**); 2026-03-30 — M10.4 R2; executor role and verbatim SQL clarified

---

## Who executes this document

**Binding rule:** Validation of M10.4 is performed **only** by **Team 50 (QA)** — typically an **autonomous QA agent** following this mandate step by step.

- **Team 10 does not** self-certify AC1–AC8.  
- **Project lead** does not replace Team 50 for gate evidence; human approval uses the **interfaces** after Team 50 files a **PASS** (or **CONDITIONAL PASS**) report.

If any check cannot be run (e.g. no `UPRESS_*`), record **BLOCKED** with reason in the findings report and set gate to **FAIL** or **CONDITIONAL PASS** per template rules.

---

## Authority (read before executing)

1. `_COMMUNICATION/TEAM_10/MANDATE_M10_4_HEADLESS_MYPIPS_TEAM10.md` — **MANDATE-20260404-M10-4-HEADLESS-MYPIPS** (AC1–AC8, D1–D14).  
2. `_COMMUNICATION/TEAM_10/MANDATE_M10_CORRECTIONS_AND_GUIDANCE_TEAM10.md` — **MANDATE-20260404-M10-CORRECTIONS** (per-source ≥90% discipline where applicable to community sources).  
3. Team 10 handoff: `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_4_TEAM10.md`  
4. Implementation evidence: `_COMMUNICATION/TEAM_10/reports/2026-04-04_M10_4_COMPLETION_TEAM10.md`

---

## Preconditions

| ID | Check | Command / action | Pass |
|----|--------|------------------|------|
| P1 | Alembic at head | `python3 -m alembic current` | Revision **057** (or later Team 20 head on target DB) |
| P2 | DB health | `python3 -m organic_market_agent.db.check` | `RESULT: PASS` |
| P3 | Playwright browser | `python3 -m playwright install chromium` | Chromium available when AC1/E2E checks run |
| P4 | Publish env | `UPRESS_*` in `.env` for upload/live checks | Set or document skip |

---

## T01 / AC1 — Playwright installs

**Action:** `pip install -r requirements.txt` then `python3 -m playwright install chromium`.  
**Pass:** No install errors;  

```bash
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()"
```

exits **0**.

---

## T02 / AC2 — Headless collector returns rendered HTML

**Action:** After a mypips ingestion (or equivalent), confirm latest stored HTML for at least one priority source contains product markup (e.g. `pips-card-content`), not only an empty SPA shell.

**Pass:** Evidence from `raw_assets` or pipeline logs — **non-shell** HTML for **≥1** of SRC041, SRC042, SRC053, SRC055, SRC060, SRC061, SRC062, SRC069, SRC070.

---

## T03 / AC3 — ≥7 of 9 priority sources extract products

**Priority codes:** `SRC041`, `SRC042`, `SRC053`, `SRC055`, `SRC060`, `SRC061`, `SRC062`, `SRC069`, `SRC070`.

**Action:** Ensure a coordinated ingestion has been run for the target DB (Team 10 or ops). Then execute **verbatim**:

```sql
SELECT s.code,
  COUNT(rei.id) AS raw_rows
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code;
```

**Pass:** **≥7** distinct `code` values with `raw_rows > 0`.  
**Note:** Store “closed” or error pages may yield 0 — document **timestamp** and environment; do not infer PASS without query output.

---

## T04 / AC4 — Per-source resolution ≥90% (mypips priority set)

**Action:** Execute **verbatim** (mypips nine codes only):

```sql
SELECT s.code,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
HAVING COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')) > 0
ORDER BY s.code;
```

**Pass:** For **each** row, `pct >= 90`. If corrections discipline applies, also flag any row with `unres > 0` for Team 100 review (stricter than pct alone).

**Skip row:** If a source has **no** rows in the `HAVING` clause (no normalized/unresolvable mix), state **no extractable catalog in window** — do not count as automatic PASS for that source.

---

## T05 / AC5 — Published product count ≥90

```bash
export $(grep -v '^#' .env | xargs) 2>/dev/null || true
python3 -m organic_market_agent catalog_renormalize
python3 -m organic_market_agent run_publisher
python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))"
```

**Pass:** Printed count **≥ 90**.  
**If fail:** Record rolling-window rules from publisher logs; recommend Team 100 waiver or follow-up milestone.

---

## T06 / AC6 — Full pytest green

```bash
python3 -m pytest tests/ -q
```

**Pass:** **0 failures.**

---

## T07 / AC7 — Mypips parser unit tests

```bash
python3 -m pytest tests/test_mypips_parser.py -q
```

**Pass:** **≥5** tests pass (expected delivery: **6**).

---

## T08 / AC8 — Upload and live page

```bash
export $(grep -v '^#' .env | xargs) 2>/dev/null || true
python3 -m organic_market_agent run_publisher --upload
```

**Pass:** No fatal upload error; logs show successful FTPS (or document `BLOCKED` if credentials absent).

**Live URL (check both redirects):**

```bash
curl -sL -o /dev/null -w "%{http_code}" "https://www.nimrod.bio/smallfarmsagent/"
curl -sL -o /dev/null -w "%{http_code}" "https://nimrod.bio/smallfarmsagent/"
```

**Pass:** Final HTTP code **200** for the canonical site the project uses; brief note that public index reflects current manifest/report (spot-check in browser optional).

---

## Optional — T09 / E2E marker

If Chromium and network are available:

```bash
RUN_MYPIPS_E2E=1 python3 -m pytest tests/test_mypips_integration.py -m integration -q
```

**Pass:** 0 failures. **Weight:** Medium (supplementary to T03).

---

## Deliverable (Team 50 only)

1. Copy `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md` to:

   `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_M10_4_QA_FINDINGS_TEAM50.md`

2. Fill every section; reference this mandate filename in **QA Mandate executed**.  
3. Map **T01–T08** (and T09 if run) to findings tables with **evidence** (command output, SQL result tables, counts).  
4. **Gate decision:** **PASS** / **CONDITIONAL PASS** / **FAIL** per template §5.  
5. After **PASS** or **CONDITIONAL PASS**, Team 10 may file Team 100 completion notice per M10.4 mandate §8.

---

## Outcome summary table (for the findings report)

| Test ID | AC | Description | Pass criterion |
|---------|-----|-------------|----------------|
| T01 | AC1 | Playwright | Launch chromium headless OK |
| T02 | AC2 | Rendered HTML | Non-shell HTML ≥1 source |
| T03 | AC3 | Raw extraction | ≥7/9 codes with `raw_rows > 0` |
| T04 | AC4 | Resolution | Each row `pct >= 90` (see notes) |
| T05 | AC5 | Publish count | products ≥ 90 |
| T06 | AC6 | Pytest full | 0 failures |
| T07 | AC7 | Parser unit | ≥5 tests pass |
| T08 | AC8 | Upload + live | FTPS OK; HTTP 200 |
| T09 | — | E2E optional | 0 failures if executed |
