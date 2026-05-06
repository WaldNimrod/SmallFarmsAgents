# MANDATE — SFA-S002-P001-WP002 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (Opus, orchestrator)
**To:** sfa_build (Sonnet, Team 10 builder)
**WP:** SFA-S002-P001-WP002 — MyPIPS Source Integration + Branch Cleanup
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)
**Status:** QUEUED — mandate published to git this session; builder dispatch deferred to a subsequent session per team_00 directive 2026-05-07 ("לדחוף עכשיו - ליישם אחרי").
**Depends on:** WP001 (M10 thaw must land first — provides updated source-handling layer).

---

## 1. Identity

You are **sfa_build (Team 10)**, code builder running on Claude Sonnet under cross-engine governance. team_100 (Opus) orchestrates; you build; external validates. Stay distinct (Iron Rule #1).

---

## 2. Binding artifacts (read first, in this order)

1. **LOD400 spec (work order):**
   `_aos/work_packages/S002/SFA-S002-P001-WP002/LOD400_spec.md`
2. **Audit report (precision input — per-source classification, raw-material guardrails):**
   `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md`
3. **Program package:**
   `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`

The 10 Acceptance Criteria (AC-01..AC-10) define DONE.

---

## 3. THE HARDEST CONSTRAINT — RAW MATERIAL UNTOUCHED

The branch `cursor/mypips-communication-and-handoffs` contains both in-scope MyPIPS work AND **out-of-scope raw material** for the next dev phase. team_00 ruling 2026-05-07: "חומר גלם לא נוגעים."

**FORBIDDEN paths — any commit touching these is rejected:**
- `_COMMUNICATION/TEAM_80/TEND_2018–2022/` (CSV/ZIP archives)
- `_COMMUNICATION/TEAM_80/Team 80 MasterClass/` (PDFs)
- `_COMMUNICATION/TEAM_80/mypips_discovery_package.zip`

You may LOOK at filenames but NOT modify, move, analyze contents, or merge.

---

## 4. Scope summary (full detail in LOD400 + audit)

### Phase 1 — Apply infrastructure (apply stash)
- Add `display_bucket` column to `sources` (new migration after WP001's last)
- Update model `sources.py`, publisher `rolling_aggregate.py` (join + emit `source_types[]`)
- Update template `public_report_body.html` (filter bar UI)
- Land discovery library (`organic_market_agent/discovery/mypips_scan.py`) + 3 CLI scripts
- Land 4 reference reports + canonical `mypips_suspected_links_60.csv`

### Phase 2 — Onboard 4 priority MyPIPS sources via headless Playwright collector
| Handle | Hebrew | Bucket | Priority |
|--------|--------|--------|----------|
| `mashtelatharoe` | משתלת הראה | grower | 1 (307 products) |
| `anatiyot` | הננתיות | store | 2 (organic certified) |
| `fruit4soul` | השחקן שהפך לירקן | store | 3 (217 products) |
| `finerotem` | משק רתם פיין | grower | 4 (irregular cycle) |

Implement `MypipsCollector(handle="...")` parameterized class extending `collectors/base.py`. Playwright/Firestore DOM extraction. Live smoke per source (when source is open).

### Phase 3 — Branch cleanup
- All MYPIPS-WORK files moved to main ✓
- Tend/MasterClass UNCHANGED on branch ✓
- Tag `archive/mypips-handoffs-732121e` at pre-cleanup head
- Rename branch → `archive/raw-material-tend-masterclass-2026-04`

---

## 5. Working environment

| Item | Value |
|------|-------|
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` |
| Source branch | `cursor/mypips-communication-and-handoffs@732121e` (+ `stash@{0}`) |
| Python | 3.11 |
| New dep | `playwright` (chromium) |

---

## 6. Hard constraints

1. **WP001 must land first** — your migration depends on WP001's last migration number.
2. **WP006 (FTPS) takes precedence** if both touch publisher (rolling_aggregate.py overlap).
3. Raw material UNTOUCHED (§3 above).
4. No edits to `_aos/governance/` or `_aos/roadmap.yaml`.
5. **No git push** — commits only.
6. NOT_VIABLE sources (`mypips`, `thelab`) NOT added to `sources` table.
7. PARTIAL sources (L1+L2 ~30 stores, L5 variants) DEFERRED to future WP — document in `RECONCILIATION_NOTES.md`.
8. `playwright install chromium` documented in operations docs (`DEVELOPMENT_WORKSTATION_SCHEDULER_POLICY.md`).
9. Pre-commit guard suggested: reject diffs matching forbidden raw-material paths.

---

## 7. Process (high-level — full detail in LOD400)

1. Read MANDATE + LOD400 + audit end-to-end.
2. Verify WP001 has landed (check for migrations 032/033).
3. Apply stash changes (model + publisher + templates + docs).
4. Add `display_bucket` migration after WP001's last migration.
5. Implement `MypipsCollector` base class with Playwright Firestore DOM extraction.
6. Capture HTML fixtures for the 4 priority stores under `tests/fixtures/mypips/`.
7. Implement per-source overrides (organic flag for `anatiyot`, etc.).
8. Register the 4 sources in `sources` table.
9. Smoke-ingest each source (when open); record run logs in `_COMMUNICATION/team_10/SFA-S002-P001-WP002/SOURCE_ONBOARDING_LOG.md`.
10. Run pytest suite + `validate_aos.sh` — 0 FAIL.
11. Branch cleanup: tag + rename + verify raw material untouched (`git diff <pre>..<post> -- <forbidden paths>` returns empty).
12. Drop `stash@{0}` AFTER its content is fully landed.
13. Commit with message starting `build(S002-WP002): MyPIPS source integration ...`.

---

## 8. Sprint estimate

**LARGE (5–8 days)** per audit. Iron Rule §42 sprint discipline cap ≤3.

---

## 9. Reporting back

Final report per LOD400 §3 AC table format. Include per-source onboarding result table. Document DEFERRED items (PARTIAL sources, L5 variants) explicitly.

---

## 10. Authority limits

- MAY commit to offline branch.
- MAY create archive tag `archive/mypips-handoffs-732121e` and rename source branch (audit-trail moves only).
- MAY NOT push, merge to main, or issue gate verdicts.
- MAY NOT touch raw material (Tend, MasterClass).
- MAY NOT touch shaked-wg-agent code.

---

## 11. References

- LOD400: `_aos/work_packages/S002/SFA-S002-P001-WP002/LOD400_spec.md`
- Audit: `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md`
- Source branch: `cursor/mypips-communication-and-handoffs@732121e` + `stash@{0}`

---

*Mandate published 2026-05-07. Builder dispatch deferred per team_00 — to be triggered in a subsequent session after WP001 + WP006 land.*
