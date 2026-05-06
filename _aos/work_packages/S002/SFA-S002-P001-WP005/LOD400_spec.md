# LOD400 — SFA-S002-P001-WP005 — Public Launch Package

**Date:** 2026-05-07
**Author:** team_100
**WP:** SFA-S002-P001-WP005
**Type:** LOD400_SPEC
**Status:** READY for L-GATE_S
**Builder:** team_100 + Team 50 (this WP is meta-orchestration; deliverable is documentation + dispatch artifact)
**QA:** Team 50
**Validator:** external (the bundle this WP produces IS the external validation request)
**Depends on:** WP001, WP002, WP003, WP004 (all must reach internal L-GATE_V status before this WP starts execution).

---

## 1. Goal

Compose the **external validation package** that team_00 will dispatch to a non-Opus engine (Cursor / Claude Sonnet/Haiku via aos_mail / external session) for **constitutional cross-engine validation** of the entire SFA-S002-P001 release prior to public launch.

This WP **does not** ship code. It produces a coherent, audit-ready bundle plus an `aos_mail` prompt.

---

## 2. Acceptance Criteria

### AC-01 — All upstream WPs internally complete
- WP001, WP002, WP003, WP004 each have:
  - LOD400 spec PASS at L-GATE_S.
  - Builder mandate executed.
  - Team 50 QA verdict = PASS or PASS_WITH_FINDINGS.
  - Internal L-GATE_V draft verdict authored by team_100 (preliminary, pending external).

### AC-02 — Bundle manifest complete
A bundle directory at `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/` containing:
- `MANIFEST.md` — index of all included artifacts with one-line purpose each.
- `PROGRAM_SUMMARY.md` — 1-page executive summary (scope, what was built, what's launching).
- Per-WP folder `WP00X/`:
  - Copy of `LOD400_spec.md`
  - QA verdict
  - Test results summary (pass/fail counts, coverage if measured)
  - Diff summary (`git diff main..offline-branch -- <relevant paths>` shortened)
- `RISK_REGISTER.md` — known issues, deferred items, waivers.
- `ROLLBACK_PLAN.md` — explicit revert procedure (commits to revert, FTPS state to restore, DB state).
- `VALIDATE_AOS_OUTPUT.txt` — latest `validate_aos.sh` run output (must show 0 FAIL).
- `LIGHTHOUSE_REPORT.json` — WP004 mobile audit output.
- `SCRAPING_VERIFICATION.md` — copy of WP003 final verification report.

### AC-03 — Rollback plan precise
- Lists exact commits to `git revert` (in correct order — last-in first-out).
- Lists exact pre-launch FTPS state to restore: artifact_version + manifest hash.
- Lists DB state restore procedure for migrations 032+ (downgrade order).
- Lists external dependencies that may need separate revert (cron schedules, scheduler_config flags).
- Names the on-call human (team_00) and escalation path.

### AC-04 — `aos_mail` external validator prompt drafted
- Path: `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/AOS_MAIL_PROMPT.md`
- Contents (template):
  - Self-contained context (validator has no prior session memory).
  - Bundle location reference.
  - Specific verification asks per WP.
  - Verdict format expected (PASS / PASS_WITH_FINDINGS / FAIL).
  - Where to file the verdict (`_COMMUNICATION/team_190/SFA-S002-P001/EXTERNAL_VERDICT_*.md`).
- Engine constraint: non-Opus (Iron Rule #1 cross-engine).

### AC-05 — Sign-off matrix
- Internal sign-off table in `MANIFEST.md`:

| Team | Role | Status | Date |
|------|------|--------|------|
| team_100 | Architect | <signed/pending> | YYYY-MM-DD |
| team_10 | Builder | <signed/pending> | YYYY-MM-DD |
| team_50 | QA | <signed/pending> | YYYY-MM-DD |
| team_60 | Server (WP003) | <signed/pending> | YYYY-MM-DD |
| team_00 | Principal | <pending external> | YYYY-MM-DD |
| external | Validator | <pending> | YYYY-MM-DD |

### AC-06 — Push state
- Offline branch `offline/2026-05-07-smallfarmsagents-release-prep` pushed to `origin`.
- PR created against `main` (or merge plan documented in `MANIFEST.md` if PR-based workflow not used).
- Branch is **not** merged until external validation returns PASS.

### AC-07 — Hub-side awareness (DB online dependent)
- If DB is back online by the time WP005 executes: run `bash /Users/nimrod/Documents/agents-os/scripts/sync_offline_to_db.sh --force` to clear `_aos/PENDING_DB_SYNC.yaml`.
- If DB still offline: leave PENDING file in place; document state in `MANIFEST.md`.

---

## 3. File-level deliverables

| Path | Action |
|------|--------|
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/MANIFEST.md` | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/PROGRAM_SUMMARY.md` | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/WP001/` (4 files) | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/WP002/` (4 files) | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/WP003/` (4 files) | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/WP004/` (4 files) | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/RISK_REGISTER.md` | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/ROLLBACK_PLAN.md` | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/VALIDATE_AOS_OUTPUT.txt` | CREATE (re-run output) |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/AOS_MAIL_PROMPT.md` | CREATE |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/PUBLISH_CHECKLIST_RUN_2026-05-XX.md` | CREATE — record of running [`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) |

No production code changes under this WP.

---

## 4. External validation feedback handling

After team_00 dispatches `AOS_MAIL_PROMPT.md` and external validator returns its verdict:

- **PASS:** Proceed with merge to `main` per push authority. Run [`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) for launch.
- **PASS_WITH_FINDINGS:** team_100 routes findings as remediation tasks; minor non-blocking findings may be filed as follow-up WP under S003.
- **FAIL:** team_100 opens correction cycle; affected WPs return to L-GATE_B with remediation; new external validation pass required.

---

## 5. Constraints

- **Cross-engine constitutional rule (Iron Rule #1):** External validator engine ≠ Opus. team_00 selects from Cursor / Claude Sonnet/Haiku / manual review.
- **No public launch before PASS verdict** — AC-06 prohibits merge prior.
- **Bundle is self-contained:** validator must be able to act with only the bundle + repo state at the offline branch tip.

---

## 6. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| External validator session lacks context | `AOS_MAIL_PROMPT.md` is fully self-contained; no chat history dependency |
| Validator finds an issue requiring code change | Documented PASS_WITH_FINDINGS path; remediation cycle defined |
| Push to `origin` triggers downstream automation prematurely | Branch is `offline/...`, not `main`; no auto-deploy expected |
| DB still offline when WP005 runs | AC-07 documents both paths |

---

## 7. Sprint estimate

**SMALL–NORMAL (1–2 days)** — bundling existing artifacts, drafting AOS_MAIL prompt, running PUBLISH_CHECKLIST in dry-run mode.

---

## 8. References

- Program package: [`PROGRAM_PACKAGE_LOD200_v1.0.0.md`](../../../../_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md)
- Publish checklist: [`PUBLISH_CHECKLIST.md`](../../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md)
- WordPress publish runbook: [`WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md)
- Iron Rule #1 (cross-engine): hub `methodology/AOS_CONCEPT_AND_PRINCIPLES.md`

---

*LOD400 ready for L-GATE_S verdict.*
