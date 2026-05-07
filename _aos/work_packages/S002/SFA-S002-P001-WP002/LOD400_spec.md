# LOD400 — SFA-S002-P001-WP002 — MyPIPS Source Integration + Branch Cleanup

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP002
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_S
**Builder:** sfa_build (Sonnet, Team 10)
**QA:** Team 50 (Haiku)
**Validator:** external
**Depends on:** WP001 (M10 thaw)

**Audit input:** [`AUDIT_WP002_MYPIPS.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md) — read first.

---

## 1. Goal

Integrate the **MyPIPS source-discovery work** parked on `cursor/mypips-communication-and-handoffs` into `main`: apply infrastructure (model + publisher + docs), implement the 4 priority MyPIPS sources as production collectors, and clean up the branch while **preserving Tend exports + MasterClass raw material untouched**.

---

## 2. Hard constraint — RAW MATERIAL UNTOUCHED

The following files exist on the source branch and **MUST NOT be modified, merged, moved, or analyzed** under this WP. They are reserved for the next dev phase per team_00 directive 2026-05-06/07:

- `_COMMUNICATION/TEAM_80/TEND_2018–2022/` (all CSV/ZIP archives)
- `_COMMUNICATION/TEAM_80/Team 80 MasterClass/` (all PDFs)
- `_COMMUNICATION/TEAM_80/mypips_discovery_package.zip`

Any builder commit that touches these paths is rejected.

---

## 3. Acceptance Criteria

### Phase 1 — Infrastructure (apply stash)

#### AC-01 — `display_bucket` column added
- Migration created (next number after WP001's last migration) adds `display_bucket VARCHAR(20)` column to `sources` table with CHECK constraint: `grower | store | chain | discovery | benchmark | verification`.
- Existing rows in `sources` populated with appropriate `display_bucket` values (default `store` if unclear).
- `alembic upgrade head` + `downgrade -1` reversible.

#### AC-02 — Models + publisher updated
- `organic_market_agent/models/sources.py` exposes `display_bucket` field.
- `organic_market_agent/publisher/rolling_aggregate.py` joins `display_bucket` and emits `source_types[]` array in JSON output.
- `organic_market_agent/publisher/templates/public_report_body.html` filter bar UI added (`הכל / 🌱 מגדלים / 🏪 חנויות / 🏬 רשתות`).

#### AC-03 — Discovery library + CLI tools landed
- `organic_market_agent/discovery/mypips_scan.py` — core probe library.
- `scripts/mypips_discover.py` — async httpx CLI.
- `scripts/mypips_verify_suspected_csv.py`.
- `scripts/mypips_build_onboarding_workbook.py`.
- `documentation/06-scripts-and-cli/README.md` updated with MyPIPS CLI section.

#### AC-04 — Reference data + reports filed
- `_COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv` — landed (canonical Phase 1 candidate list).
- `_COMMUNICATION/TEAM_10/reports/2026-04-04_MYPIPS_SPIKE_ASSESSMENT_TEAM10.md` — landed.
- `_COMMUNICATION/TEAM_10/reports/2026-04-04_MyPIPS_DISCOVERY_IMPLEMENTATION_TEAM10.md` — landed.
- `_COMMUNICATION/TEAM_10/reports/2026-04-05_MYPIPS_DISCOVERY_LAYERS_EXPERIMENT_SUMMARY_TEAM10.md` — landed.
- `_COMMUNICATION/TEAM_100/reports/2026-04-04_SOURCE_ONBOARDING_STATUS_AND_PHASE2_PLAN.md` — landed.

### Phase 2 — Per-source onboarding (4 priority stores)

#### AC-05 — `MypipsCollector` base class implemented
- `organic_market_agent/collectors/mypips.py` — parameterized collector class extending [`base.py`](../../../../organic_market_agent/collectors/base.py).
- Uses Playwright headless browser for Firestore DOM extraction (Phase 2C architecture per Team 100 onboarding plan).
- Constructor accepts `handle: str` (e.g., `"mashtelatharoe"`) and shared MyPIPS base URL pattern.
- Resilient to "store closed for orders" state (parses catalog without placing order).
- Unit tests with recorded HTML fixtures in `tests/fixtures/mypips/`.

#### AC-06 — 4 priority sources registered + smoked
For each of the 4 COMPLETED sources:

| Handle | Hebrew name | Priority | Cycle |
|--------|-------------|----------|-------|
| `mashtelatharoe` | משתלת הראה | 1 | weekly Sun–Wed |
| `anatiyot` | הננתיות | 2 | weekly Sun 18:00 – Mon 20:00 |
| `fruit4soul` | השחקן שהפך לירקן | 3 | continuous |
| `finerotem` | משק רתם פיין | 4 | irregular |

- Registered in `sources` table with appropriate `display_bucket` (mashtelatharoe = `grower`; anatiyot = `store`; fruit4soul = `store`; finerotem = `grower`).
- Live smoke ingestion: at least **1 successful raw_extracted_items run per source** (when source is open) recorded in dev DB.
- Each source has a record entry in `_COMMUNICATION/team_10/SFA-S002-P001-WP002/SOURCE_ONBOARDING_LOG.md` with run timestamp, items count, and any quirks.

#### AC-07 — anatiyot organic flag respected
- `anatiyot` collector sets `includeOrganic=true` query parameter (per audit — only store with this flag).
- Smoke test confirms organic-tagged products appear in extracted items.

### Phase 3 — Branch cleanup

#### AC-08 — Branch state after WP002
- `cursor/mypips-communication-and-handoffs` head ≠ `732121e` after cleanup.
- All MYPIPS-WORK files (per audit inventory) have been moved to main and removed from this branch.
- All RAW-PRESERVE files remain on this branch unchanged (`git diff <pre-cleanup>..<post-cleanup>` for raw paths returns empty).
- Tag `archive/mypips-handoffs-732121e` created at the pre-cleanup head.
- Branch renamed to `archive/raw-material-tend-masterclass-2026-04`.

#### AC-09 — Stash drop
- `stash@{0}` (S003-P019 AC-07) — once its MyPIPS-related changes are landed in Phase 1, drop the stash. Document drop in `RECONCILIATION_NOTES.md`.

#### AC-10 — Validation
- `validate_aos.sh` returns 0 FAIL post-WP002.

---

## 4. File-level deliverables (high level — full set per audit)

### CREATE
- `organic_market_agent/db/versions/<NNN>_add_display_bucket_to_sources.py`
- `organic_market_agent/discovery/mypips_scan.py`
- `organic_market_agent/discovery/__init__.py` (if not present)
- `organic_market_agent/collectors/mypips.py`
- `scripts/mypips_discover.py`
- `scripts/mypips_verify_suspected_csv.py`
- `scripts/mypips_build_onboarding_workbook.py`
- `tests/test_mypips_scan.py`
- `tests/test_mypips_collector.py`
- `tests/fixtures/mypips/*.html` (recorded fixtures for the 4 priority stores)
- `_COMMUNICATION/team_10/SFA-S002-P001-WP002/SOURCE_ONBOARDING_LOG.md`
- `_COMMUNICATION/team_10/SFA-S002-P001-WP002/RECONCILIATION_NOTES.md`
- Tag `archive/mypips-handoffs-732121e`
- Renamed branch `archive/raw-material-tend-masterclass-2026-04`

### UPDATE
- `organic_market_agent/models/sources.py` (add `display_bucket`)
- `organic_market_agent/publisher/rolling_aggregate.py` (join + emit)
- `organic_market_agent/publisher/templates/public_report_body.html` (filter UI)
- `documentation/06-scripts-and-cli/README.md`
- `CHANGELOG.md` `[Unreleased]`

### LAND (move from branch to main)
- `_COMMUNICATION/TEAM_80/mypips_suspected_links_60.csv`
- 4 MyPIPS reports (per AC-04)

### DO NOT TOUCH
- Tend exports, MasterClass PDFs, `mypips_discovery_package.zip`

---

## 5. Implementation notes

### Playwright dependency
- Add `playwright` to `requirements.txt` (or pyproject deps).
- Add post-install hook: `playwright install chromium`.
- For CI/dev: document in `documentation/05-admin-and-operations/DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md` how to install playwright on the production server.

### Hebrew handle normalization
- All 4 priority sources use Latin URL handles even though display names are Hebrew. `slugify` for new handles must match the canonical name in MyPIPS URL.

### Failed sources documentation
- For sources tagged NOT_VIABLE in audit (`mypips`, `thelab`): record exclusion rationale in `RECONCILIATION_NOTES.md`. Do NOT add to `sources` table.

### L1+L2 PARTIAL sources
- Out of scope for this WP. Document them in `RECONCILIATION_NOTES.md` as Phase 3 backlog with their slugs.

### L5 variants
- Out of scope. Note in `RECONCILIATION_NOTES.md`.

---

## 6. Test plan

### Unit
- `mypips_scan` async probe behavior (mocked httpx).
- `MypipsCollector` parsing against recorded HTML fixtures.
- `display_bucket` model behavior + migration reversibility.

### Integration
- End-to-end pipeline run: ingest from each of the 4 sources (when open) → normalize → publish → verify `source_types[]` in JSON.
- Filter UI smoke (Playwright headed): clicking each filter button updates visible rows.

### Manual smoke
- Pipeline against production-like dev DB with Playwright.
- Cross-check ingested item counts against MyPIPS UI counts.

---

## 7. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Source HTML structure changes between fixture capture and smoke | Re-capture fixtures at smoke time; record date in fixture filename |
| Playwright instability on production server | Document fallback to httpx for static HTML where possible; per-source override |
| MyPIPS URL pattern changes | Centralize base URL in collector class; version it |
| Anti-scraping measures (rate limit, CAPTCHA) | Honor robots.txt; conservative throttle; document in collector docstring |
| Builder accidentally touches RAW-PRESERVE | Pre-commit guard: reject diffs matching `_COMMUNICATION/TEAM_80/(TEND|MasterClass|mypips_discovery_package)` |

---

## 8. Sprint estimate

**LARGE (5–8 days)** per audit. Iron Rule §42 sprint discipline = single sprint cap, ≤3 sprint allowance.

---

## 9. Out of scope

- L1+L2 PARTIAL sources (~30) — document as Phase 3 backlog.
- L5 variants — document as Phase 3 backlog.
- Google Custom Search API integration — defer to Phase 3.
- Tend exports + MasterClass — raw material, next dev phase.
- Sources beyond the 4 priority handles (mashtelatharoe, anatiyot, fruit4soul, finerotem).

---

## 10. References

- Audit report: [`AUDIT_WP002_MYPIPS.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md)
- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Source branch: `cursor/mypips-communication-and-handoffs@732121e` + `stash@{0}`

---

*LOD400 ready for L-GATE_S verdict.*
