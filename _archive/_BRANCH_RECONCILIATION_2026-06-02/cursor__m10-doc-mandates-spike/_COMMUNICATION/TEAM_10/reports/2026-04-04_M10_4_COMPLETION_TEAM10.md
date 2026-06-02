# M10.4 — Headless browser and mypips — Team 10 completion report

**Date:** 2026-04-04  
**Mandate:** `MANDATE-20260404-M10-4-HEADLESS-MYPIPS`  
**Status:** Implementation complete — **Team 50 QA required** for formal AC sign-off

---

## Summary

Playwright-based headless collection for mypips.app, `MypipsCollector` / `MypipsParser`, Alembic activation and dictionary passes for nine priority sources (SRC041, SRC042, SRC053, SRC055, SRC060, SRC061, SRC062, SRC069, SRC070). Full pytest suite passes locally after fixing admin test sensitivity to stuck `running` ingestion runs.

---

## Evidence

### Alembic

Revisions **`040_m10_4_mypips_normalizer_activation`** through **`046_m10_4_goji_spelling_scope`** (see `organic_market_agent/db/versions/`).

```bash
python3 -m alembic current   # expect head = 046 or later
```

### Automated tests

```bash
python3 -m pytest tests/test_mypips_parser.py tests/test_mypips_integration.py -q
# 6 passed, 1 skipped (E2E off by default)

python3 -m pytest tests/ -q
# 164 passed, 2 skipped (2026-04-04)
```

Optional E2E (Chromium required):

```bash
RUN_MYPIPS_E2E=1 python3 -m pytest tests/test_mypips_integration.py -m integration
```

### Publish and upload

```bash
python3 -m organic_market_agent run_publisher --upload
```

**Observed:** `PublishEngine: wrote **79** products` (rolling 7d window). Mandate AC5 asks **≥90** vs baseline ~83 — **not met** in this snapshot; Team 50 should confirm whether more live ingestion windows or policy clarification is needed.

**FTPS:** Upload succeeded in dev environment (8 files).  
**Live page:** `curl -sL -o /dev/null -w "%{http_code}" https://nimrod.bio/smallfarmsagent/` → **200**.

### Per-source ingestion (AC3 / AC4)

Mypips storefronts may return a **closed / unavailable** shell for some handles at crawl time; raw row counts are **time-dependent**. Where HTML contained `div.pips-card-content`, collector tab-merge path (migration `042`) restored large catalogs (e.g. SRC053). Team 50 should re-run ingestion against live stores and apply the mandate SQL for per-source resolution.

**Known ops issue:** duplicate raw asset skip for SRC041 if response body is unchanged after cache-bust query — may require deleting recent raw rows for that source or ingestion policy adjustment (documented for QA).

### product_aliases

If `catalog_renormalize` raises `MultipleResultsFound` for aliases, the DB may contain duplicate rows sharing `alias_text_normalized`. Deduplicate (keep lowest `id`) or add a data migration — not shipped in this completion slice.

---

## Acceptance criteria (self-check)

| AC | Result | Notes |
|----|--------|--------|
| AC1 | Pass | `playwright` in requirements; `playwright install chromium` documented in README |
| AC2 | Pass | `HeadlessBrowserCollector` returns rendered HTML after selector wait |
| AC3 | **Conditional** | ≥7/9 when stores serve product DOM; closed pages yield 0 rows |
| AC4 | **Team 50 verify** | Dictionary migrations `043`–`046`; run per-source SQL after fresh ingest |
| AC5 | **Fail / gap** | Published product count **79** in test run; target ≥90 |
| AC6 | Pass | Full `pytest tests/` green after `test_t09` cleanup |
| AC7 | Pass | Six unit tests in `tests/test_mypips_parser.py` |
| AC8 | **Partial** | Upload OK; live URL returns 200; “new products visible” subjective vs baseline |

---

## Next steps

1. **After Team 50 FAIL (2026-04-04):** see remediation handoff **`_COMMUNICATION/TEAM_10/reports/2026-04-05_M10_4_QA_REMEDIATION_COMPLETE_TEAM10.md`** and run **`scripts/verify_m10_4_gate.sh`** before re-QA.  
2. **Team 50 (QA agent):** execute `_COMMUNICATION/TEAM_50/QA_MANDATE_M10_4_TEAM50.md` (v1.1+); file **`_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_M10_4_QA_FINDINGS_TEAM50.md`** using `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md` (PASS / CONDITIONAL PASS / FAIL).  
3. After PASS: Team 100 notice per mandate §8 step 5 (update `_COMMUNICATION/TEAM_100/reports/2026-04-04_M10_4_COMPLETION_NOTICE_TEAM10.md` from pending to signed).  
4. Optional: Team 190 preflight package (not filed for this drop).
