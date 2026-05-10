# RECONCILIATION NOTES — SFA-S002-P001-WP001

**Date:** 2026-05-07
**Author:** sfa_build (Team 10, Claude Sonnet 4.6)
**WP:** SFA-S002-P001-WP001 — M10 Thaw + Completion
**Strategy:** C — Extract files + reapply (binding per MANDATE_v1.0.0.md)
**Source branch:** `cursor/m10-doc-mandates-spike@bb981ed`
**Target branch:** `offline/2026-05-07-smallfarmsagents-release-prep`

---

## 1. Migration Disposition Table

### Context

Main's migration head at integration time: `031_deactivate_src017_pricez.py` (revision `"031"`, `down_revision = "030"`).

Branch uses simple numeric string revision IDs (e.g., `revision = "031"`, `down_revision = "030"`) — same scheme as main. Branch migration 031 collides with main's 031 by revision ID. Branch migrations 032–073 do not numerically conflict (main tops out at 031).

Decision rationale for SKIP of branch 032–071: The mandate (Step 1) requires per-migration evaluation. These 41 migrations contain M10.2-5, M13-PRE, and CSA source activation content — category **WP002** scope (MyPIPS sources) or explicitly **out of scope** per LOD400 §8. Carrying them would also create a numbering paradox: if branch 032–071 are brought over as-is (numbers don't conflict), then branch 072 and 073 cannot be renumbered to 032 and 033 (those numbers would already be taken). The mandate's binding requirement to place the primary deliverables at 032/033 unambiguously requires skipping the intermediate migrations.

### Branch Migration 031 (mypips_candidate_sources_workbook)

| Migration | Branch ID | Action | Reason |
|-----------|-----------|--------|--------|
| `031_mypips_candidate_sources_workbook` | `revision = "031"` | **SKIP** | Numbering collision — main's `031_deactivate_src017_pricez` holds revision `"031"`. MyPIPS schema belongs in future WP002. Cannot carry without renumbering, and renumbering would shift the entire branch chain. |

### Branch Migrations 032–071 (41 migrations: M10.2-5 + M13-PRE content)

All 41 migrations in this range are **SKIPPED**. Disposition by sub-group:

| Range | Count | Name Pattern | Action | Reason |
|-------|-------|--------------|--------|--------|
| 032–035 | 4 | `m10_2_*` — M10.2 dictionary scope-skip + aliases | SKIP | M10.2 data (catalog quality tuning) — deferred to future WP; no schema dependency for 032/033 primary deliverables |
| 036–039 | 4 | `m10_3_*` — M10.3 static parser sources | SKIP | M10.3 source activation content; sources table edits belong in dedicated WP |
| 040–058 | 19 | `m10_4_*` — M10.4 mypips sources + playwright | SKIP | MyPIPS SPA collector sources (SRC041/042/060/070 etc.) — WP002 scope; no schema deps for 032/033 |
| 059–065 | 7 | `m13_pre_*` — M13-PRE content | SKIP | Explicitly out of scope per LOD400 §8 ("M13 pre-stage — deferred to future WP") |
| 066–071 | 6 | CSA expansion + alias fixes | SKIP | CSA source expansion (SRC075) and alias corrections — deferred; no schema deps for 032/033 |

**Total SKIPPED:** 42 (branch 031 + 032–071)
**Total CARRIED (renumbered):** 2 (branch 072→032, branch 073→033)

### Branch Migrations 072–073 → 032–033 (primary deliverables)

| Branch | Worktree | Revision Change | down_revision Change | Action |
|--------|----------|-----------------|----------------------|--------|
| `072_cq_p01_alias_batch.py` | `032_cq_p01_alias_batch.py` | `"072"` → `"032"` | `"071"` → `"031"` | **CARRY** (renumbered) |
| `073_src_wa_pending_manual.py` | `033_src_wa_pending_manual.py` | `"073"` → `"033"` | `"072"` → `"032"` | **CARRY** (renumbered) |

Chain after integration: `... → 030 → 031 → 032 → 033` (clean linear chain).

---

## 2. rolling_aggregate.py Reconciliation

### Main baseline (commit 75e1fcb "1.2" — 181 lines)

The main version has a flat `build_rolling_publish_products` function that:
- Runs `_LATEST_PER_SOURCE_SQL` (no `display_bucket` join)
- Groups by `(product_id, market_scope, sales_channel)` tuples
- Returns a flat output dict with basic stats (min/max/avg/median/stddev)
- No per-filter-key breakdown, no `stats_by_filter`, no `details` object

### Branch version (bb981ed — 285 lines)

The branch version is a **major functional enhancement** that:
- Adds `JOIN sources s ON s.id = no.source_id` to `_LATEST_PER_SOURCE_SQL` to fetch `s.display_bucket`
- Adds `Counter` import and helper functions: `_collapse_latest_per_source`, `_stats_from_collapsed`, `_dominant_sales_channel`
- Implements per-filter-key stats: `stats_by_filter = {"all": ..., "grower": ..., "store": ..., "chain": ..., "baskets": ...}`
- Adds `build_details_object` integration (new `report_details.py` module)
- Top-level numeric fields mirror the `grower` slice when present (public UI default)
- `source_types` field (sorted display buckets)

### Resolution: **BRANCH VERSION ADOPTED**

The branch version is a superset of main's functionality. Main's 1.2 fix was a rolling window improvement (now subsumed by the branch's full rewrite). The branch version was built after 75e1fcb and incorporates all intent. `report_details.py` was copied alongside (new file, no conflict).

**Risk mitigated:** `rolling_aggregate.py` tests in `tests/test_publisher_local.py` were not modified (branch test count matched main's; no structural incompatibility found).

---

## 3. models/runs.py Reconciliation

### Main baseline (146 lines, 3 additional commits: 07b49bc, 1f83142, 36a0cec)

Main has `RawExtractedItem` CHECK constraint:
```python
"extraction_status IN ('extracted','normalized','unresolvable','ignored')"
```

### Branch version (147 lines)

Branch extends CHECK constraint to add `'pending_manual'`:
```python
"extraction_status IN ("
"'extracted','normalized','unresolvable','ignored','pending_manual')"
```

No other differences found between main and branch in this file.

### Resolution: **MERGE — pending_manual added to constraint**

Single-line change. Main's model preserved entirely; only the `RawExtractedItem` CHECK constraint extended. This matches what migration 033 applies at the DB level (ALTER TABLE ALTER CONSTRAINT). The model must stay in sync with the migration for SQLAlchemy schema reflection to be consistent.

---

## 4. utils/config.py Reconciliation

### Main baseline (66 lines — WP008 version, BINDING)

Main has:
- `ftps_configured()` — classmethod, True when FTPS creds set
- `upress_configured()` — classmethod, OR of `wp_rest_configured()` or `ftps_configured()` (WP008 fix for F-190-01)
- `wp_rest_configured()` — classmethod, True when WP REST creds set
- `load_dotenv(.env.upress)` — loads uPress secrets from separate file
- `UPRESS_WP_REST_BASE` default: `"https://www.nimrod.bio/wp-json"`

### Branch version

Branch version REMOVES `wp_rest_configured()`, `ftps_configured()`, and changes `upress_configured()` back to FTPS-only check. This is **FORBIDDEN** (live production code, WP007/WP008 complete).

The branch also adds:
- `PLAYWRIGHT_HEADLESS: bool` field
- `PLAYWRIGHT_TIMEOUT_MS: int` field

### Resolution: **MAIN IS BASE — only Playwright fields added**

All WP008 methods (`ftps_configured`, `upress_configured`, `wp_rest_configured`) preserved intact from main. Only the two Playwright config fields were added from the branch. Branch's FTPS-only regression was explicitly discarded.

---

## 5. .env.example Reconciliation

### Main baseline

Main has full WP REST API + WP007/WP008 documentation, `.env.upress` reference, and `UPRESS_FALLBACK_FTPS` comment. No Playwright vars.

### Branch baseline

Branch has simpler version: `UPRESS_PURGE_CACHE_AFTER_UPLOAD` key (not in main), missing WP007/WP008 context comments.

### Resolution: **MAIN IS BASE — Playwright vars appended**

Main's .env.example is superior (has WP007/WP008 documentation). Branch's `UPRESS_PURGE_CACHE_AFTER_UPLOAD` key was evaluated: this key does not exist in main's `Config` class (main uses `upress_cache_purge_via_rest_configured()` method which uses the existing REST keys). Excluded. Added only:
```
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=30000
```

No duplicate keys.

---

## 6. Items Deferred / Flagged for team_100

1. **Branch migrations 032–071 (41 migrations):** All SKIPPED. These contain M10.2-5 data (scope-skip rules, aliases, source activations for MyPIPS/CSA sources). When team_100 is ready to thaw M10.2-5, a separate WP should carry these migrations — they are preserved on `cursor/m10-doc-mandates-spike` (tagged `archive/m10-spike-bb981ed`).

2. **db/check.py sources count:** Updated from 20 → 21 to account for SRC_WA seeded by migration 033. If DB smoke is run against a DB that doesn't have migration 033 applied, `check.py` will report FAIL on sources count. This is expected — check.py is a post-migration health probe.

3. **rolling_aggregate.py test coverage:** The enhanced version with `stats_by_filter` and `details` object is not fully covered by existing `test_publisher_local.py`. Recommend team_100 add AC to WP for test coverage of filter-key outputs. Not blocking for WP001 AC-03 (existing tests still pass).

4. **report_details.py:** Copied from branch as a dependency of `rolling_aggregate.py`. Not listed in LOD400 §4 deliverables explicitly but required for import chain. Filed here for team_100 awareness.

---

*Reconciliation filed by sfa_build (Team 10) — 2026-05-07*
