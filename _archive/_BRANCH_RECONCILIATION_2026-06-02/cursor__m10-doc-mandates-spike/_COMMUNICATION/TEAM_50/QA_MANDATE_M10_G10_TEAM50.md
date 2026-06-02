---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G10 (M10.2 + M10.3 bundle)

**Mandate ID:** `QA-MANDATE-M10-G10`  
**From:** Team 100 (Architecture) — *issued via Team 10 coordination per project lead*  
**To:** Team 50 (QA) — **agent-executable**  
**CC:** Team 10 (Feature Dev), Team 190 (Preflight, optional)  
**Date:** 2026-04-04  
**Milestones:** M10.2 — Dictionary optimization (phase 13); M10.3 — Static parsers (phase 14)  
**Gate:** G10 (partial until both QA PASS + Team 100 architectural approval recorded)

---

## Authority (read before executing)

1. `_COMMUNICATION/TEAM_10/MANDATE_M10_CORRECTIONS_AND_GUIDANCE_TEAM10.md` — **MANDATE-20260404-M10-CORRECTIONS** (binding order, per-source ≥90%, QA path).  
2. `_COMMUNICATION/TEAM_10/MANDATE_M10_2_DICTIONARY_OPTIMIZATION_TEAM10.md`  
3. `_COMMUNICATION/TEAM_10/MANDATE_M10_3_STATIC_PARSERS_TEAM10.md`  
4. Team 10 requests: `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_2_TEAM10.md`, `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_3_TEAM10.md`

---

## Preconditions

| ID | Check | Command / action | Pass |
|----|--------|------------------|------|
| P0 | Team 190 preflight (optional) | Read `_COMMUNICATION/TEAM_190/reports/2026-04-04_M10_2_PACKAGE_VALIDATION_TEAM190.md` and `2026-04-04_M10_3_PACKAGE_VALIDATION_TEAM190.md` | N/A — informational |
| P1 | Alembic at head | `alembic current` | Shows `039 (head)` or later Team 20 revision |
| P2 | DB health | `python3 -m organic_market_agent.db.check` | `RESULT: PASS` |
| P3 | Env | `DATABASE_URL` set; for live publish QA, `UPRESS_*` configured | As appropriate |

---

## Test suite

### T01 — M10 parser smoke tests

```bash
python3 -m pytest tests/test_m10_3_parsers.py tests/test_ftps_upload.py -q
```

**Pass:** 0 failures.  
**Weight:** Critical (M10.3 regression guard).

---

### T02 — Full pytest (informational for technical debt)

```bash
python3 -m pytest tests/ -q
```

**Pass (G10 M10):** No **new** failures attributable to M10 migrations/parsers (pre-existing admin/Jinja failures may be documented as non-blocking).  
**Weight:** High.

---

### T03 — Per-source resolution (active community)

Execute SQL (verbatim):

```sql
SELECT s.code,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.is_active = true AND s.market_scope = 'community'
GROUP BY s.code
HAVING COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')) > 0
ORDER BY s.code;
```

**Pass (M10.2 corrections §3.2):** For every row, `pct >= 90` **and** `unres = 0` (stricter than 90% when unresolvable exists).  
**Weight:** Critical.

---

### T04 — Pipeline + publish artifacts

```bash
export $(grep -v '^#' .env | xargs)
python3 -m organic_market_agent catalog_renormalize
```

Then:

```bash
python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))"
```

**Pass (M10.2):** product count **≥ 70**.  
**Pass (M10.3):** product count **≥ 80** (corrections §4.4).  
**Weight:** Critical.

---

### T05 — FTPS upload + live page

```bash
python3 -m organic_market_agent run_publisher --upload
```

Then:

```bash
curl -sI https://www.nimrod.bio/smallfarmsagent/ | head -1
```

**Pass:** Upload completes without `SystemExit(2)`; HTTP **200** on live page.  
**Weight:** Critical for go-live acceptance.

---

### T06 — Manifest / version sanity (optional)

Confirm `output/public/manifest.json` references the same `public_report` version as uploaded (manual or `jq`).

**Weight:** Medium.

---

## Deliverable

File a **QA Findings Report** using `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`:

`_COMMUNICATION/TEAM_50/reports/2026-04-04_G10_M10_QA_FINDINGS_TEAM50.md`

**Gate decision:** One of PASS / CONDITIONAL PASS / FAIL per template §5.

---

## Explicit non-scope

- **M10.4** mypips / Playwright — out of scope.  
- **WordPress content** beyond SmallFarmsAgent page availability — out of scope unless project lead expands mandate.
