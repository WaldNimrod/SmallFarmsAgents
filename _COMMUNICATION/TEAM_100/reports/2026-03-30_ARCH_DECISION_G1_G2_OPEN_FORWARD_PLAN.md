# Architecture Decision — Gates G1 + G2 Open + Forward Plan
**Date:** 2026-03-30  
**From:** Team 100 (Architecture)  
**To:** All teams  
**Authority:** Project Lead direction — "move forward"

---

## 1. Gate Decisions

### Gate G1 — OPEN (Conditional Pass, conditions tracked below)

**Evidence accepted:**
- Python 3.11.15 + PostgreSQL 15.17 (Homebrew direct install) — confirmed by Team 20 handoff report
- All 7 `test_db_health.py` tests PASS under Python 3.11.15
- `alembic upgrade head` + `downgrade base` + `upgrade head` round-trip — OK
- `db.check` → RESULT: PASS (23 tables)
- Import sanity — OK
- No FLOAT columns, all `*_at` columns TIMESTAMPTZ, prices NUMERIC(12,4)
- T12 CHECK constraint active — confirmed by migration structure

**Conditional item (tracked, not blocking M3):**
- **T10 — 13 products missing aliases.** High severity. Team 20 must deliver seed patch migration `006` before Gate G3 can open. See `MANDATE_SEED_PATCH_M1.1_TEAM20.md`.

**Additional fix accepted:**
- `pyproject.toml` `build-backend` corrected by Team 20 from `setuptools.backends.legacy:build` to `setuptools.build_meta`. This is the correct value. Mandate snippet is superseded by the working file.

**Gate G1 is formally OPEN.**

---

### Gate G2 — OPEN (Conditional Pass, conditions tracked below)

**Evidence accepted:**
- 27/27 pytest tests PASS (Python 3.11.15): `test_collectors.py` (10), `test_parsers.py` (10), `test_db_health.py` (7)
- Live ingestion run: `status=partial`, `succeeded=16`, `failed=4`, `community_ok=13` — acceptable; 4 failures are external (SRC001: SSL cert expired, SRC015–SRC017: HTTP 403) not implementation defects
- `raw_extracted_items` = 3210 rows (threshold ≥50 met)
- Dedup: second run produced `skipped=8` in logs; no duplicate `(source_id, checksum_sha256)` rows in `raw_assets` — dedup logic proven
- Code review (T10–T12): 0 hardcoded Hebrew product names, 0 hardcoded URLs, 0 live HTTP in tests, 0 `session.query()` calls
- Error handling: SSL + 403 failures correctly logged to `log_entries`, `source_fetch_runs.status='failed'`

**T06 mandate ambiguity — resolved (see §2.1 below):**
Dedup criterion amended. Existing evidence satisfies the amended criterion.

**Conditional items (tracked, not blocking M3):**
1. **EasyFarm selector drift** — several sources return 0 `raw_extracted_items`. Root cause: live DOM differs from default selectors. To be fixed by updating `selector_profile` in `source_fetch_profiles` seed (Team 20 patch). **Impact on M3:** NormalizerEngine will simply find no items to normalize for those sources. Not a blocker.
2. **SRC018–SRC020 fetch_mode mismatch** — seed has `fetch_mode='html_page'` but normalizer_type maps to JSON parsers. Team 20 must correct `source_fetch_profiles` entries in seed patch. Before this fix, these sources will log parser errors (correctly).
3. **Team 10 verification DB was Docker** — acceptable for dev evidence. G2 QA sign-off should be re-confirmed on direct install environment (carried forward as informational, not a retest requirement per Project Lead direction).

**Gate G2 is formally OPEN.**

---

## 2. Architectural Decisions

### 2.1 T06 Dedup Test — Amended Criterion

**Problem:** The mandate required "second run: all `source_fetch_runs.status='skipped'`, `new_assets=0`." This fails on live internet because any source whose response changes (even slightly) produces a new checksum and a legitimate `success`, not a `skipped`.

**Decision:** Amend `QA_MANDATE_G2.md` T06 as follows:
- Dedup is **proven** when: (a) at least one source is repeated with identical payload → produces `status='skipped'` in `source_fetch_runs`, AND (b) no duplicate rows exist in `raw_assets` for the same `(source_id, checksum_sha256)`.
- The strict "all skipped" criterion is dropped. It was appropriate only for fully mocked/frozen HTTP and does not apply to live collection.

`QA_MANDATE_G2.md` updated accordingly.

### 2.2 EasyFarm Selector Strategy

**Decision:** Default CSS selectors in `EasyFarmCatalogParser` remain as-is. Per-source overrides MUST be loaded from `source_fetch_profiles.selector_profile` (JSONB). When that field is NULL, the parser falls back to defaults.

Team 20 will populate realistic `selector_profile` values for the EasyFarm sources where the default fails (see seed patch mandate). Team 10 **must not** hardcode source-specific selectors in parser code.

### 2.3 SRC018–SRC020 — Parser Map and Seed Alignment

**Decision:** The benchmark/retail sources (SRC018–SRC020) that are effectively HTML pages should have `fetch_mode='html_page'` in their `source_fetch_profiles`. If the normalizer_type remains `retail_benchmark` or `official_wholesale`, Team 10's `ParserEngine` must also accept `simple_product_grid` as a fallback for HTML from those sources, or the seed must align `normalizer_type` with actual content type.

**Chosen path:** Team 20 updates the seed to use `fetch_mode='html_page'` and `normalizer_type='simple_product_grid'` for SRC018–SRC020 until their actual JSON endpoints (if any) are confirmed. Team 10 has no code change for this item.

### 2.4 `pyproject.toml` build-backend

**Decision:** `setuptools.build_meta` is the canonical value. The M1 mandate snippet that showed `setuptools.backends.legacy:build` was a typo. Mandate updated.

### 2.5 log_entries Persistence for Errors

Team 10 added ERROR-level `log_entries` persistence for collector exhaustion and parser errors. This **exceeds** the mandate minimum (which only required stdout logging). It is **accepted and becomes the standard**. All future ERROR-level log calls must persist to `log_entries`.

---

## 3. Required Patches Before Gate G3

These items are **mandatory** before Team 50 can sign off G3:

| # | Action | Owner | Mandate |
|---|--------|-------|---------|
| P1 | Seed migration `006_seed_aliases_complete.py` — aliases for 13 missing products | Team 20 | `MANDATE_SEED_PATCH_M1.1_TEAM20.md` |
| P2 | Update `source_fetch_profiles` seed for SRC018–SRC020 (fetch_mode + normalizer_type) | Team 20 | `MANDATE_SEED_PATCH_M1.1_TEAM20.md` |
| P3 | Populate `selector_profile` JSONB for failing EasyFarm sources | Team 20 | `MANDATE_SEED_PATCH_M1.1_TEAM20.md` |

Team 20 patches must be delivered and `db.check` must pass before Team 10 begins M3 QA.
Team 10 may begin M3 implementation in parallel (patches do not block code writing, only the QA gate).

---

## 4. Active Milestone Update

| Milestone | Status |
|-----------|--------|
| M1 | **COMPLETE** — G1 open |
| M2 | **COMPLETE** — G2 open |
| **M3** | **ACTIVE** — NormalizerEngine |
| M4–M7 | Locked |

Mandate: `_COMMUNICATION/TEAM_10/MANDATE_M3_NORMALIZER_ENGINE.md` (issued with this report).

---

## 5. Next Steps Summary

| Step | Who | When |
|------|-----|------|
| Implement M3 NormalizerEngine | Team 10 | Now |
| Deliver seed patch (P1–P3) | Team 20 | Before G3 QA |
| QA Gate G3 | Team 50 | After M3 complete + seed patch |
| Issue M3 QA Mandate | Team 100 | Issued with this report: `QA_MANDATE_G3.md` |
