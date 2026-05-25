---
id: ARCHIVE_MANIFEST_SFA-S003-P002-WP-B1-patch06
wp: SFA-S003-P002-WP-B1-patch06 — JMF_CROP_MAP cleanup (27 entries removed)
status: LOD500_LOCKED
closed_at: "2026-05-26"
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent) + team_110 fix (CM bug)
validator: team_190 (GPT-5.5 — non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 ≠ team_10 Sonnet ≠ team_190 GPT-5.5"
program: SFA-S003-P002-WP-B (COMPLETE — 9/9 WPs LOD500_LOCKED)
execution_mandate_status: ENDED (this is the final WP)
---

# Archive Manifest — patch06 (Cleanup) — FINAL WP

## 1. Gate chain (10 events across 6 team_190 rounds + 2 Sonnet builds + 1 team_110 fix)

| Gate | Round | Result | Commit |
|------|-------|--------|--------|
| L-GATE_E | — | PASS (team_00 via DECISION) | — |
| L-GATE_S | R1 | FAIL (3-engine chain missing) | `a32c9bf` |
| L-GATE_S | R2 | PASS clean (15/15) | `8ef4356` |
| L-GATE_S | R3 | FAIL (file-location: 2 funcs in separate files) | `6cc57a9` |
| L-GATE_S | R4 | PASS_WITH_FINDINGS (advisory addressed inline `ec4b62e`) | `554c88b` |
| L-GATE_BUILD | initial | BUILD_COMPLETE per v1.0.1 (15/15 ACs + 7 consequence-failures STOP) | `113b47d` + report `6801e64` |
| L-GATE_BUILD | incremental | BUILD_COMPLETE per v1.0.3 (7 functions deleted, 1 file removed) | `8920269` + team_110 report stub `038c1ae` |
| L-GATE_V | R1 | FAIL (1 BLOCKER on AC-12/AC-13 — CM misuse) | `0a4a03c` |
| L-GATE_V (fix) | — | team_110 commit `fb3d6aa` (context-manager + mapper registry) | `fb3d6aa` |
| L-GATE_V | R2 | **PASS clean** | `7e467a4` |

6 team_190 rounds total. Most-iterated WP in the EXECUTION_MANDATE extension.

## 2. Deliverables

### 2.1 Code (across 3 build commits)

| Commit | Scope |
|--------|-------|
| `113b47d` initial build | constants.py: 27 keys removed; test_jmf_crop_map.py: 3 LOCKED updates + 3 new appended; test_jmf_crop_map_aliases.py: 2 LOCKED updates + 1 removed; CHANGELOG; scripts/patch06_db_cleanup.py created. 7 consequence-failures reported correctly. |
| `8920269` incremental cleanup | 7 superseded functions deleted across 3 files; `test_jmf_live_workbook_coverage.py` removed (became empty). |
| `fb3d6aa` team_110 fix | `scripts/patch06_db_cleanup.py`: context-manager + SQLAlchemy mapper registry pre-imports. |

Cumulative: 6 modified files + 1 created (script) + 1 file deleted.

### 2.2 Final state of `JMF_CROP_MAP`

| Dimension | Before patch06 (post-patch04) | After patch06 |
|-----------|-------------------------------|---------------|
| Entries | 87 | **60** |
| Baselines (Cat A) | 53 | 53 |
| Synonyms (Cat B) | 6 | 6 |
| Cultivars masquerading (Cat C) | 22 | **0** (moved to crop_varieties by patch04) |
| Workbook typos (Cat D) | 5 | **0** (deleted) |
| Ginger (patch04 add) | 1 | 1 |
| Duplicate-target groups | 24 | **6** (all pure synonym pairs) |
| Sum of group sizes | 55 | **12** |

### 2.3 Specs

| Spec | Final version |
|------|---------------|
| LOD200 | v1.0.0 |
| LOD400 | **v1.0.3 LOCKED** (v1.0.0 → v1.0.1 → v1.0.2 → v1.0.3, 3 R-amendments) |

## 3. ADR042 3-step closure

| Step | Outcome |
|------|---------|
| 1. Archive manifest | ✓ This file |
| 2. Roadmap lifecycle | `status: DONE / lod_status: LOD500_LOCKED / current_lean_gate: L-GATE_V / closed_at: 2026-05-26` |
| 3. validate_aos.sh | 29 PASS / 19 SKIP / 0 FAIL ✓ |

## 4. Findings disposition (final)

| Severity | Finding | Resolution |
|----------|---------|------------|
| L-GATE_S R1 BLOCKER | Frontmatter 3-engine chain | RESOLVED v1.0.1 |
| L-GATE_S R3 BLOCKER | 2 superseded tests in separate files | RESOLVED v1.0.3 |
| L-GATE_S R4 ADVISORY | §3.8/§5 stale prose | Addressed inline |
| L-GATE_BUILD initial | 7 consequence-failures (Sonnet correctly STOPPED) | RESOLVED via R3+R4 amendments + incremental build |
| L-GATE_V R1 BLOCKER | patch06_db_cleanup.py CM misuse + SQLAlchemy mapper registry | RESOLVED in fix commit `fb3d6aa` |

**Final: 0 blockers, 0 majors, 0 minors, 0 unresolved advisories.**

## 5. Iron Rules audit

All applicable IRs preserved. Three-engine separation maintained throughout the 6-round cycle.

## 6. Lessons learned

1. **`get_session` is `@contextmanager`** — script authors must always use `with ... as session:`. The fix commit (`fb3d6aa`) added this to the docstring as a defensive comment. Future scripts should reference this pattern.
2. **SQLAlchemy mapper registry must be complete before query()** — pre-import all models referenced by relationships. Particularly tricky in cleanup scripts that import only `Crop` lazily.
3. **Builder STOP semantics work** — Sonnet's stop at AC-18 in patch03 (test_jmf_crop_map_aliases.py) AND at AC-14 in patch06 (7 consequence-failures) were both correct scope-discipline events. Each forced a spec amendment cycle that produced a cleaner end state.
4. **Sonnet socket errors don't lose work IF the commit succeeded first** — the `8920269` commit was complete before Sonnet's session died. team_110 was able to author the BUILD_REPORT v1.0.1 stub with independently-verified probes. Defensive: always commit BEFORE writing reports.

## 7. Operational follow-ups

| ID | Item | Owner |
|----|------|-------|
| OP-P06-01 | Run `python scripts/patch06_db_cleanup.py --apply` against production Postgres if needed (idempotent — safe to run anytime; no-op if DB already clean) | team_00 |
| OP-P06-02 | M2M sheet 056 (storage/washing) data load — still deferred from patch04. Junction infrastructure ready. | patch07 candidate |
| OP-P06-03 | Add base-falling-cultivar resolution to JMF importer if downstream coverage drops are observed (importer fallback to `crop_varieties` when MAP misses) | future WP |

---

*Archive manifest 2026-05-26 by team_110. Closes the final WP under EXECUTION_MANDATE.*
