# M10.4 — QA remediation round 2 (Team 50 re-review FAIL)

**From:** Team 10  
**To:** Team 50 (QA), Team 100 (Architecture)  
**Date:** 2026-03-30  
**References:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_M10_4_QA_FINDINGS_TEAM50.md`, `QA_MANDATE_M10_4_TEAM50.md` (T03–T05), prior remediation `2026-04-05_M10_4_QA_REMEDIATION_COMPLETE_TEAM10.md`

---

## Summary

Round-2 implements Playwright **context realism** (UA, locale, timezone, extra headers), per-source **wait/timeout** tuning and **tab-click disabled** for four shell-prone stores, **cache-buster `m10_4d`** on entry URLs, **dictionary** work for SRC060/SRC070 (scope-skip + aliases, plus SRC060 Granny Smith typo alias in **055**), **E2E URL cache-bust** when `RUN_MYPIPS_E2E=1`, and documentation (README, integration test module docstring).

**Alembic chain:** `052` → `053` → `054` → `055` (head **055**).

**Out of scope (not in workspace):** `TEAM_100_TO_TEAM_190_S003_P019_FULL_REVALIDATION_CLOSURE_NOTE_v1.0.0.md` — not found under `_COMMUNICATION/`; no code dependency.

---

## T03 / AC3 — Priority sources with `raw_extracted_items`

**Mandate SQL** was run on the development DB **before** a fresh nine-source ingestion after R2 migrations:

| code   | raw_rows (example run) |
|--------|-------------------------|
| SRC041 | 187 |
| SRC053 | 270 |
| SRC060 | 75 |
| SRC061 | 72 |
| SRC070 | 227 |
| SRC042, SRC055, SRC062, SRC069 | 0 (no rows in this snapshot) |

**distinct_with_rows_gt0:** 5/9 in this snapshot.

**Expectation for QA:** Run a **coordinated** mypips ingestion for all nine priority codes after `alembic upgrade head`, then re-run verbatim T03 SQL. R2 collector/profile + `m10_4d` are intended to improve shell stores; residual shell-only HTML may still require headed mode (`PLAYWRIGHT_HEADLESS=false`) per README.

---

## T04 / AC4 — Per-source resolution (verbatim mandate SQL)

After `053` + `055` and `catalog_renormalize --skip-publish`, example output on the same DB:

| code   | norm | unres | pct   |
|--------|------|-------|-------|
| SRC041 | 124  | 0     | 100.0 |
| SRC053 | 113  | 0     | 100.0 |
| SRC060 | 56   | 0     | 100.0 |
| SRC061 | 61   | 2     | 96.8  |
| SRC070 | 116  | 0     | 100.0 |

Sources with **no** rows in the mandate `HAVING` clause (e.g. SRC042 when still 0 extracts) are **skipped rows** per mandate — not automatic PASS for that code.

**Inventory:** Remaining unresolvable set for SRC060/SRC070 was cleared for the catalog slice above; **055** adds alias `תפוח עץ גרני סמיט` → `PRD042` (typo vs `סמית`).

---

## T05 / AC5 — Published product count

After `catalog_renormalize --skip-publish` and `run_publisher`:

- **`len(products)` in `output/public/public_report.json`:** **74** (also **75** in an earlier run on the same rolling window — variance is expected from aggregation state).

**Rolling publisher rule:** ≥2 distinct sources per product in the index window (`rolling_aggregate.py`). With four priority sources still at 0 extracts in the snapshot above, count **remains below 90**.

**Team 100:** Request **waiver or threshold decision** if, after successful nine-source ingestion, the count is still &lt;90 — do **not** change `INDEX_WINDOW_DAYS` without approval.

---

## T09 / E2E — Duplicate checksum

**Mitigation:** `RUN_MYPIPS_E2E=1` triggers a per-run unique query parameter on the Playwright navigation URL so `DuplicateAssetError` does not skip parsing on repeat test runs. Documented in `tests/test_mypips_integration.py` and README.

---

## Forensics (shell stores SRC042 / SRC055 / SRC062 / SRC069)

Stored HTML for these codes previously lacked `pips-card-content` and ₪ anchors (QA T02). R2 adds **realistic browser context**, longer **post_load_delay_ms**, **load** wait, **no tab clicking** for those profiles, and **`m10_4d`** cache-bust. If markup remains empty after QA ingestion, next escalation is JSON/Firestore spike **with Team 100 approval** (per original remediation plan).

---

## Verification commands (Team 10)

```bash
python3 -m alembic upgrade head
python3 -m pytest tests/ -q
python3 -m pytest tests/test_mypips_parser.py -q
./scripts/verify_m10_4_gate.sh   # requires coordinated ingestion for T03 ≥7 if DB is cold
# Optional: RUN_MYPIPS_E2E=1 python3 -m pytest tests/test_mypips_integration.py -m integration -q
```

---

## Files touched (implementation)

- `organic_market_agent/collectors/headless_browser.py` — context kwargs, E2E URL bust  
- `organic_market_agent/collectors/mypips.py` — profile-driven context  
- `organic_market_agent/db/versions/052_m10_4_r2_shell_stores_playwright_context.py`  
- `organic_market_agent/db/versions/053_m10_4_r2_dictionary_src060_src070.py`  
- `organic_market_agent/db/versions/054_m10_4_r2_cache_bust_m10_4d.py`  
- `organic_market_agent/db/versions/055_m10_4_r2_alias_src060_granny_smith_typo.py`  
- `README.md`, `tests/test_mypips_integration.py`, `CHANGELOG.md`  
- `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_4_TEAM10.md`, `QA_MANDATE_M10_4_TEAM50.md` (P1 revision)
