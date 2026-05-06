# MANDATE — SFA-S002-P001-WP001 — TEAM_100 → sfa_build

**Date:** 2026-05-07
**From:** team_100 (Opus, orchestrator)
**To:** sfa_build (Sonnet, Team 10 builder)
**WP:** SFA-S002-P001-WP001 — M10 Thaw + Completion
**Type:** GATE_MANDATE
**Gate:** L-GATE_BUILD (entering)
**Status:** QUEUED — mandate published to git this session; builder dispatch deferred to a subsequent session per team_00 directive 2026-05-07 ("לדחוף עכשיו - ליישם אחרי").

---

## 1. Identity

You are **sfa_build (Team 10)**, code builder running on Claude Sonnet under cross-engine governance. team_100 (Opus) orchestrates; you build; external validates. Stay distinct (Iron Rule #1).

---

## 2. Binding artifacts (read first, in this order)

1. **LOD400 spec (work order):**
   `_aos/work_packages/S002/SFA-S002-P001-WP001/LOD400_spec.md`
2. **Audit report (precision input — strategy, conflicts, file inventory):**
   `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md`
3. **Program package:**
   `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`

The 9 Acceptance Criteria (AC-01..AC-09) define DONE.

---

## 3. Strategy (binding from audit)

**Strategy C — Extract files + reapply** (modified cherry-pick). Direct rebase/merge is FORBIDDEN due to migration 031 numbering collision (branch's 031 = `mypips_candidate_sources_workbook` Apr 5; main's 031 = `deactivate_src017_pricez` Apr 21).

You MUST:
1. Renumber branch migrations 072 → 032, 073 → 033 (and their `down_revision` pointers).
2. Evaluate the 41 branch migrations 031–071 per-migration (CARRY / SKIP) against current main. Document each disposition.
3. Manually reconcile 3 CONFLICT-LIKELY files (publisher/rolling_aggregate.py, models/runs.py, utils/config.py).
4. Discard generated outputs and harness configs (output/public/*, .claude/settings.json).

Full file map in audit report §3.

---

## 4. Working environment

| Item | Value |
|------|-------|
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` |
| Repo root | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Source branch | `cursor/m10-doc-mandates-spike@bb981ed` |
| Python | 3.11 |
| DB | offline (use `require_postgres` skip pattern for DB-dependent tests) |

---

## 5. Hard constraints

1. **Coordinate with WP006 (FTPS Remediation):** WP006 modifies `organic_market_agent/publisher/ftps_upload.py` to restore `ReusedSessionFTP_TLS`. If WP006 has landed by the time you start, DO NOT regress that fix. The M10 spike's `ftps_upload.py` changes are CONFLICT-LIKELY against WP006 — preserve WP006's TLS subclass when reconciling.
2. Raw material walled off: do NOT touch `_COMMUNICATION/TEAM_80/{TEND_2018–2022,Team 80 MasterClass,mypips_discovery_package.zip}`.
3. No edits to `_aos/governance/`, `_aos/roadmap.yaml`, or `_aos/PENDING_DB_SYNC.yaml`.
4. **No git push** — commits only. team_100 reviews + pushes.
5. **Cherry-pick branch must NOT be deleted** — tag `archive/m10-spike-bb981ed` after extraction (per AC-08).
6. Cross-engine: orchestrator = Opus, you = Sonnet, validator = external.

---

## 6. Process (high-level — full detail in LOD400)

1. Read MANDATE + LOD400 + audit report end-to-end.
2. Inspect current main + branch state for each file in audit's CONFLICT-LIKELY list.
3. Stage extraction in a working directory; copy clean files (basket_tier_resolver.py, tests, db/check.py).
4. Renumber migrations 072→032, 073→033; adjust down_revision; verify chain.
5. Evaluate per-migration disposition for branch 031–071; build RECONCILIATION_NOTES.md as you go.
6. Reconcile rolling_aggregate.py, models/runs.py, utils/config.py manually — preserve main's changes + branch's intent.
7. Reconcile docs (CLAUDE.md, ROADMAP.md, CHANGELOG.md).
8. Run `alembic upgrade head` against fresh DB (when DB online); if offline, document deferred verification.
9. Run full pytest suite — green (DB-dependent tests may skip).
10. Run `validate_aos.sh` — 0 FAIL.
11. Create tag `archive/m10-spike-bb981ed` pointing to commit `bb981ed` on the source branch.
12. Commit with message starting `build(S002-WP001): M10 thaw — extract+reapply ...`.

---

## 7. Sprint estimate

**MEDIUM (3–5 days)** per audit. Iron Rule §42 sprint discipline ≤3 cap.

---

## 8. Reporting back

Final report per LOD400 §3 AC table format. Include per-migration disposition table from RECONCILIATION_NOTES. team_100 will route to Team 50 QA.

---

## 9. Authority limits

- MAY commit to offline branch.
- MAY NOT push, merge, tag the offline branch, or issue gate verdicts.
- MAY create the `archive/m10-spike-bb981ed` tag (audit trail tag).
- MAY NOT touch raw material (Tend, MasterClass).
- MAY NOT touch shaked-wg-agent code.

---

## 10. References

- LOD400: `_aos/work_packages/S002/SFA-S002-P001-WP001/LOD400_spec.md`
- Audit: `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md`
- Source branch: `cursor/m10-doc-mandates-spike@bb981ed`

---

*Mandate published 2026-05-07. Builder dispatch deferred per team_00 — to be triggered in a subsequent session after WP006 lands.*
