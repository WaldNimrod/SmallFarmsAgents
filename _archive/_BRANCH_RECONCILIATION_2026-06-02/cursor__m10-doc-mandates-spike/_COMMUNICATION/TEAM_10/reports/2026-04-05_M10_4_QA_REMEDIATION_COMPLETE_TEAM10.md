# M10.4 — QA remediation complete (Team 10 handoff)

**Date:** 2026-04-05  
**Reference QA report:** `_COMMUNICATION/TEAM_50/reports/2026-04-04_M10_4_QA_FINDINGS_TEAM50.md` (FAIL / BLOCKED)  
**Remediation plan:** M10.4 QA remediation (Team 50 feedback)

---

## Summary of code and infra fixes

| Finding | Response |
|---------|----------|
| **T06–T07 / pytest_flask vs Flask 3** | Pinned **`pytest-flask>=1.3.0`** and **`pytest-timeout`** in [`requirements.txt`](requirements.txt). Mandated `python3 -m pytest` must use an environment where `pip install -r requirements.txt` was run on the **same** interpreter. |
| **T03 / ≥7 sources with raw rows** | **`MypipsParser`**: card-first + legacy h6 + **price-anchor** fallback for layouts without `div.pips-card-content`. **`MypipsCollector`**: tab-merge path now runs full **`_prepare_page`** before merging; thin merge → **`page.content()`** fallback; optional **`playwright_timeout_ms`** and **`goto_wait_until`** (`load` / `domcontentloaded` / …) in `selector_profile`. **Migrations `047`–`051`**: cache-bust `m10_4b`, SRC042 longer wait/timeout (**048**), `goto_wait_until` (**049**/**050** fix), SRC042 **`m10_4c`** URL (**051**). |
| **T05 / ≥90 products** | Structural: more distinct community sources with in-window **normalized_observations** unlock publisher buckets. Re-run full ingestion + `catalog_renormalize` + aggregate + `run_publisher` after extraction improves count; if still &lt; 90, use diagnostics in §4 below or **Team 100** waiver. |
| **T09 / E2E hang** | [`tests/test_mypips_integration.py`](tests/test_mypips_integration.py) split into **three** tests with **`@pytest.mark.timeout(180)`**. |
| **Self-check** | [`scripts/verify_m10_4_gate.sh`](scripts/verify_m10_4_gate.sh) — pytest, T03 SQL, `catalog_renormalize --skip-publish`, `run_publisher`, product count (optional `CURL_LIVE=1`). Documented in [`README.md`](README.md). |

**Forensics note:** [`2026-04-05_M10_4_QA_REMEDIATION_FORENSICS_TEAM10.md`](2026-04-05_M10_4_QA_REMEDIATION_FORENSICS_TEAM10.md)

---

## Tests

- **`tests/test_mypips_parser.py`**: 9 unit tests (includes price-anchor fallback).  
- **Full suite:** run `python3 -m pytest tests/ -q` after `pip install -r requirements.txt`.

---

## Environment caveat (headless / mypips)

On the dev machine used for verification, several storefronts still returned **HTML shells without ₪ or `pips-card-content`** under headless Chromium (e.g. SRC042, SRC062), so **T03 may remain data- or environment-dependent** until:

- stores serve full catalog to headless clients, or  
- **`PLAYWRIGHT_HEADLESS=false`** / different runtime is approved for ingestion, or  
- **Firestore** alternative (mandate §5) is implemented with Team 100 security review.

**Duplicate raw asset:** if checksum is unchanged, ingestion skips parse; use a new cache-buster on `entry_url` or operational cleanup of recent `raw_assets` (FK-safe) before re-ingest.

---

## Alembic

Expected head: **`051`** (`051_m10_4_mypips_src042_cache_bust_c`).  
[`QA_MANDATE_M10_4_TEAM50.md`](../TEAM_50/QA_MANDATE_M10_4_TEAM50.md) P1 updated accordingly.

---

## Next steps (process)

1. Run **`./scripts/verify_m10_4_gate.sh`** on the target DB (fix T03 gate before re-QA).  
2. **Team 50:** re-execute [`QA_MANDATE_M10_4_TEAM50.md`](../TEAM_50/QA_MANDATE_M10_4_TEAM50.md); file new `QA_FINDINGS` report.  
3. **Team 100:** after PASS — architectural notice per M10.4 mandate §8; if AC3/AC5 still fail for headless-only environments, decide waiver or Phase B (non-headless / API).

---

*Team 10 — implementation of remediation plan delivered; QA re-run required.*
