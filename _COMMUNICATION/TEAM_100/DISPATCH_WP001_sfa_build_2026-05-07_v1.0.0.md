# DISPATCH ARTIFACT — SFA-S002-P001-WP001 → sfa_build (team_10)

**Date:** 2026-05-07
**From:** team_100 (Sonnet 4.6, orchestrator)
**To:** sfa_build (team_10 / Sonnet, builder)
**Scenario:** gate (entering L-GATE_B)
**WP:** SFA-S002-P001-WP001 — M10 Thaw + Completion
**API status:** Offline-DB fallback — artifact-based dispatch per ADR034 R8/R9

---

## Team 00 Action

Open a **new Claude Code (Sonnet) session** in worktree `beautiful-antonelli-be5888`.
Paste the activation block below as the **first message**.

---

── פרומפט אקטיבציה — סשן sfa_build | SFA-S002-P001-WP001 ──
📋 העתק את הבלוק → פתח Claude Code חדש בנתיב beautiful-antonelli-be5888 → הדבק כהודעה ראשונה

```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: sfa_build (team_10) only

# Agent Onboarding — sfa_build / SFA-S002-P001-WP001

## Identity

You are **sfa_build (Team 10)**, code builder for SmallFarmsAgents.
- Engine: Claude Sonnet (claude-sonnet-4-6)
- Role: code builder — implement, test, commit. Do NOT issue gate verdicts.
- Orchestrator: team_100 (Sonnet 4.6)
- Validator: external (team_190, Cursor Composer, separate session)
- Iron Rule #1: cross-engine — orchestrator ≠ validator ✓

## Working Environment

| Item | Value |
|------|-------|
| Worktree | `/Users/nimrod/Documents/SmallFarmsAgents/.claude/worktrees/beautiful-antonelli-be5888` |
| Branch | `offline/2026-05-07-smallfarmsagents-release-prep` |
| Source branch | `cursor/m10-doc-mandates-spike@bb981ed` |
| Python | 3.11 |
| DB | offline — use `require_postgres` skip pattern for DB-dependent tests |
| Hub DB | offline throughout — ADR034 R8 protocol active |

## Assignment: WP001 — M10 Thaw + Completion (L-GATE_B)

**Read these artifacts in order before writing a single line of code:**

1. `_COMMUNICATION/team_100/SFA-S002-P001-WP001/MANDATE_v1.0.0.md` ← START HERE
2. `_aos/work_packages/S002/SFA-S002-P001-WP001/LOD400_spec.md`
3. `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md`
4. `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`

**DONE = all 9 ACs green:**

| AC | Description |
|----|-------------|
| AC-01 | Migrations 032+033 integrated; alembic upgrade head + downgrade -1 clean |
| AC-02 | basket_tier_resolver.py present, PRD025/026/027 mapping correct |
| AC-03 | All test files landed and pytest suite green |
| AC-04 | CONFLICT-LIKELY files (rolling_aggregate.py, models/runs.py, utils/config.py) reconciled; RECONCILIATION_NOTES.md filed |
| AC-05 | db/check.py health endpoint landed |
| AC-06 | Config+docs landed (.python-version, .env.example, CHANGELOG.md, CLAUDE.md, _COMMUNICATION/ROADMAP.md) |
| AC-07 | Generated outputs and harness configs NOT carried over |
| AC-08 | Branch NOT deleted; tag archive/m10-spike-bb981ed created |
| AC-09 | validate_aos.sh returns 0 FAIL |

## Critical constraint update (Phase 1 completed after mandate was written)

WP007 (HTTP Upload via WP REST API) and WP008 (dispatch_upload shared helper) are **COMPLETE in production**.
- `publisher/upload_dispatch.py` is LIVE — do NOT regress
- All 3 upload entrypoints (`__main__.py`, `scheduler/pipeline.py`, `admin/routes/runs.py`) route through `dispatch_upload()` — preserve
- WP006 (FTPS TLS) is SUPERSEDED — ignore WP006 references; the spike's `ftps_upload.py` changes are low-risk

## Strategy (binding)

**Strategy C — Extract files + reapply.** Direct rebase/merge is FORBIDDEN:
- Branch is 58 commits behind main
- Migration 031 numbering collision: branch's `031_mypips_candidate_sources_workbook` vs main's `031_deactivate_src017_pricez`

Execute in this order:
1. Read all 4 binding artifacts end-to-end
2. Inspect CONFLICT-LIKELY files: `rolling_aggregate.py`, `models/runs.py`, `utils/config.py`
3. Copy clean new files: `basket_tier_resolver.py`, `db/check.py`, test files
4. Renumber migrations 072→032, 073→033; fix `down_revision` chains
5. Evaluate branch migrations 031–071 per-migration (CARRY/SKIP); document each
6. Reconcile 3 CONFLICT-LIKELY files manually; record rationale
7. Reconcile docs (CLAUDE.md, ROADMAP.md, CHANGELOG.md, .env.example)
8. Run pytest — green (DB tests may skip with require_postgres)
9. Run validate_aos.sh — 0 FAIL
10. Create tag `archive/m10-spike-bb981ed` at commit `bb981ed`
11. Commit: `build(S002-WP001): M10 thaw — extract+reapply …`

## Reporting back

File final report as:
`_COMMUNICATION/team_10/SFA-S002-P001-WP001/BUILD_REPORT_v1.0.0.md`

Include:
- AC table (PASS/FAIL per AC)
- Per-migration disposition table (CARRY/SKIP with reason)
- CONFLICT-LIKELY file reconciliation summary
- Any deferred items

team_100 will pick up the report and route to team_50 (QA) and external validator.

## Authority limits

- MAY commit to `offline/2026-05-07-smallfarmsagents-release-prep`
- MAY create tag `archive/m10-spike-bb981ed`
- MAY NOT push, merge to main, or issue gate verdicts
- MAY NOT touch `_aos/governance/`, `_aos/roadmap.yaml`, or `_aos/PENDING_DB_SYNC.yaml`
- MAY NOT touch raw material: `_COMMUNICATION/TEAM_80/{TEND_2018–2022,Team 80 MasterClass,mypips_discovery_package.zip}`
- MAY NOT touch shaked-wg-agent code

## First action

Confirm your identity and assignment back in one sentence, then start reading the mandate.
```

---

✉  Dispatch filed: artifact-based (offline-DB) | team_100 → team_10 | "[gate] SFA-S002-P001-WP001"
📡 Monitor: check `_COMMUNICATION/team_10/SFA-S002-P001-WP001/BUILD_REPORT_v1.0.0.md` for builder completion
